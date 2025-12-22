#     _  _                        __   __
#  __| |(_)__ _ _ _  __ _ ___   _ \ \ / /
# / _` || / _` | ' \/ _` / _ \_| ' \ V /
# \__,_|/ \__,_|_||_\__, \___(_)_||_\_/
#     |__/          |___/
#
#           SECURE APPLICATION VERSION (PATCHED)
#

import datetime
import mimetypes
import os
import logging
import secrets

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.utils import timezone
from django.db import connection
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout
from django.contrib.auth.models import Group, User
from django.contrib.auth.decorators import login_required, user_passes_test

from taskManager.models import Task, Project, Notes, File, UserProfile
from taskManager.misc import store_uploaded_file
from taskManager.forms import UserForm, ProjectFileForm, ProfileForm

# Logger
security_logger = logging.getLogger('security')

# --- HELPER FUNCTION: FIX A01 (Kiểm tra quyền truy cập Project) ---
def check_project_access(user, project):
    """
    Kiểm tra xem user có quyền truy cập vào project này không.
    Ngăn chặn lỗi IDOR (A01).
    """
    if user.is_superuser:
        return True
    # Kiểm tra user có nằm trong danh sách được gán cho project không
    return project.users_assigned.filter(pk=user.pk).exists()

@login_required
def manage_tasks(request, project_id):
    user = request.user
    # FIX A01: Dùng get_object_or_404 để tránh lỗi 500 nếu ID sai
    proj = get_object_or_404(Project, pk=project_id)

    # FIX A01: Kiểm tra quyền truy cập
    if not check_project_access(user, proj):
        return HttpResponseForbidden("Bạn không có quyền quản lý task của dự án này.")

    if user.has_perm('taskManager.change_task'):
        if request.method == 'POST':
            userid = request.POST.get("userid")
            taskid = request.POST.get("taskid")
            
            target_user = get_object_or_404(User, pk=userid)
            task = get_object_or_404(Task, pk=taskid)

            # Đảm bảo task thuộc về project này
            if task.project == proj:
                task.users_assigned.add(target_user)

            return redirect('/taskManager/')
        else:
            return render(request, 'taskManager/manage_tasks.html', {
                'tasks': Task.objects.filter(project=proj).order_by('title'),
                'users': User.objects.order_by('date_joined')
            })
    else:
        return redirect('/taskManager/', {'permission': False})

@login_required
def manage_projects(request):
    user = request.user
    # Django 5.0: is_authenticated là property, không phải hàm
    logged_in = user.is_authenticated

    if user.has_perm('taskManager.change_project'):
        if request.method == 'POST':
            userid = request.POST.get("userid")
            projectid = request.POST.get("projectid")

            target_user = get_object_or_404(User, pk=userid)
            project = get_object_or_404(Project, pk=projectid)

            # FIX A01: Chỉ quản lý nếu mình có quyền trong project đó
            if check_project_access(user, project):
                project.users_assigned.add(target_user)

            return redirect('/taskManager/')
        else:
            return render(request, 'taskManager/manage_projects.html', {
                'projects': Project.objects.order_by('title'),
                'users': User.objects.order_by('date_joined'),
                'logged_in': logged_in
            })
    else:
        return redirect('/taskManager/', {'permission': False})

@login_required
def manage_groups(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/taskManager/login/')

    user_list = User.objects.order_by('date_joined')

    # Chỉ cho phép Admin hoặc người có quyền thay đổi nhóm
    if user.has_perm('auth.change_group'):
        if request.method == 'POST':
            accesslevel = request.POST.get("accesslevel", "").strip()

            if accesslevel in ['admin_g', 'project_managers', 'team_member']:
                grp, created = Group.objects.get_or_create(name=accesslevel)
                
                userid = request.POST.get("userid")
                specified_user = get_object_or_404(User, pk=userid)
                
                specified_user.groups.add(grp)
                
                security_logger.info(
                    f"User group changed | Target: {specified_user.username} | Group: {accesslevel} | By: {user.username}"
                )
                
                return render(request, 'taskManager/manage_groups.html', {
                    'users': user_list, 'groups_changed': True, 'logged_in': True
                })
        
        return render(request, 'taskManager/manage_groups.html', {
            'users': user_list, 'logged_in': True
        })
    else:
        return redirect('/taskManager/', {'permission': False})


# --- FIX A03: SQL INJECTION & A01: IDOR ---
@login_required
def upload(request, project_id):
    # FIX A01: Kiểm tra quyền truy cập project trước khi cho upload
    proj = get_object_or_404(Project, pk=project_id)
    if not check_project_access(request.user, proj):
        security_logger.warning(f"Unauthorized upload attempt | User: {request.user.username} | Project: {project_id}")
        return HttpResponseForbidden("Không có quyền upload vào dự án này.")

    if request.method == 'POST':
        # Sử dụng form đã validate ở forms.py (chặn file .exe, .php)
        form = ProjectFileForm(request.POST, request.FILES)

        if form.is_valid():
            # Lấy dữ liệu sạch từ form
            name = form.cleaned_data['name']
            
            # Hàm store_uploaded_file đã fix A03 (OS Injection) bên misc.py
            upload_path = store_uploaded_file(name, request.FILES['file'])
            
            security_logger.info(f"File uploaded | File: {name} | Project: {project_id} | User: {request.user.username}")

            # FIX A03: Sử dụng Parameterized Query để chặn SQL Injection
            # Thay vì nối chuỗi '%s' % (var), ta truyền tham số vào list []
            with connection.cursor() as curs:
                curs.execute(
                    "INSERT INTO taskManager_file ('name','path','project_id') VALUES (%s,%s,%s)",
                    [name, upload_path, project_id]
                )

            return redirect('/taskManager/' + project_id + '/', {'new_file_added': True})
        else:
            # Form lỗi (ví dụ sai đuôi file)
            return render(request, 'taskManager/upload.html', {'form': form})
    else:
        form = ProjectFileForm()
    
    return render(request, 'taskManager/upload.html', {'form': form})


# --- FIX A03: Path Traversal & A01: IDOR ---
@login_required
def download(request, file_id):
    file_obj = get_object_or_404(File, pk=file_id)

    # FIX A01: IDOR - Kiểm tra xem user có thuộc project chứa file này không
    if not check_project_access(request.user, file_obj.project):
        return HttpResponseForbidden("Bạn không được phép tải file này.")

    security_logger.info(f"File download | File: {file_obj.name} | User: {request.user.username}")

    # FIX A03: Path Traversal - Xử lý đường dẫn an toàn
    base_dir = os.path.dirname(os.path.realpath(__file__))
    # os.path.normpath giúp loại bỏ các ký tự ../ dư thừa
    safe_path = os.path.normpath(os.path.join(base_dir, '..', file_obj.path.lstrip('/')))
    
    # Kiểm tra xem file có thực sự tồn tại không
    if not os.path.exists(safe_path):
        raise Http404("File không tìm thấy trên hệ thống.")

    try:
        with open(safe_path, 'rb') as f:
            response = HttpResponse(f.read())
            response['Content-Type'] = mimetypes.guess_type(safe_path)[0] or 'application/octet-stream'
            response['Content-Disposition'] = 'attachment; filename=%s' % file_obj.name
            return response
    except IOError:
        raise Http404("Lỗi đọc file.")

@login_required
def download_profile_pic(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    try:
        filepath = target_user.userprofile.image
        if filepath and len(filepath) > 1:
            return redirect(filepath)
    except UserProfile.DoesNotExist:
        pass
    return redirect('/static/taskManager/uploads/default.png')

@login_required
def task_create(request, project_id):
    # FIX A01: Check quyền
    proj = get_object_or_404(Project, pk=project_id)
    if not check_project_access(request.user, proj):
        return HttpResponseForbidden()

    if request.method == 'POST':
        text = request.POST.get('text', '')
        task_title = request.POST.get('task_title', 'No Title')
        
        now = timezone.now()
        # Xử lý input date an toàn
        try:
            timestamp = int(request.POST.get('task_duedate', 0))
            task_duedate = datetime.datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            task_duedate = now + datetime.timedelta(weeks=1)

        task = Task(
            text=text,
            title=task_title,
            start_date=now,
            due_date=task_duedate,
            project=proj
        )
        task.save()
        # Django 5.0: ManyToMany dùng .add()
        task.users_assigned.add(request.user)

        return redirect('/taskManager/' + project_id + '/', {'new_task_added': True})
    else:
        return render(request, 'taskManager/task_create.html', {'proj_id': project_id})

@login_required
def task_edit(request, project_id, task_id):
    proj = get_object_or_404(Project, pk=project_id)
    task = get_object_or_404(Task, pk=task_id)

    # FIX A01: IDOR Check
    if not check_project_access(request.user, proj) or task.project != proj:
        return HttpResponseForbidden()

    if request.method == 'POST':
        task.title = request.POST.get('task_title', task.title)
        task.text = request.POST.get('text', task.text)
        task_completed = request.POST.get('task_completed', '0')
        task.completed = True if task_completed == "1" else False
        task.save()

        return redirect('/taskManager/' + project_id + '/' + task_id)
    else:
        return render(request, 'taskManager/task_edit.html', {'task': task})

@login_required
def task_delete(request, project_id, task_id):
    proj = get_object_or_404(Project, pk=project_id)
    task = get_object_or_404(Task, pk=task_id)

    # FIX A01: IDOR Check - Chỉ cho phép xóa nếu user thuộc project và task thuộc project
    if check_project_access(request.user, proj) and task.project == proj:
        task.delete()
        return redirect('/taskManager/' + project_id + '/')
    
    return HttpResponseForbidden("Không có quyền xóa task này.")

@login_required
def task_complete(request, project_id, task_id):
    proj = get_object_or_404(Project, pk=project_id)
    task = get_object_or_404(Task, pk=task_id)

    # FIX A01: IDOR Check
    if check_project_access(request.user, proj) and task.project == proj:
        task.completed = not task.completed
        task.save()
        return redirect('/taskManager/' + project_id)
    
    return HttpResponseForbidden()

@login_required
def project_create(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'No Title')
        text = request.POST.get('text', '')
        try:
            priority = int(request.POST.get('project_priority', 1))
        except ValueError:
            priority = 1
            
        now = timezone.now()
        project = Project(
            title=title,
            text=text,
            priority=priority,
            start_date=now,
            due_date=now + datetime.timedelta(weeks=4)
        )
        project.save()
        project.users_assigned.add(request.user)

        return redirect('/taskManager/', {'new_project_added': True})
    else:
        return render(request, 'taskManager/project_create.html', {})

@login_required
def project_edit(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    
    # FIX A01: IDOR Check
    if not check_project_access(request.user, proj):
        return HttpResponseForbidden()

    if request.method == 'POST':
        proj.title = request.POST.get('title', proj.title)
        proj.text = request.POST.get('text', proj.text)
        try:
            proj.priority = int(request.POST.get('project_priority', proj.priority))
        except ValueError:
            pass
        proj.save()

        return redirect('/taskManager/' + project_id + '/')
    else:
        return render(request, 'taskManager/project_edit.html', {'proj': proj})

@login_required
def project_delete(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    
    # FIX A01: IDOR Check - Nghiêm trọng nhất
    if check_project_access(request.user, proj):
        proj.delete()
        return redirect('/taskManager/dashboard')
    
    return HttpResponseForbidden("Bạn không có quyền xóa dự án này.")

# --- FIX A10: OPEN REDIRECT ---
def logout_view(request):
    username = request.user.username if request.user.is_authenticated else 'anonymous'
    security_logger.info(f"User logout | User: {username}")
    
    logout(request)
    # FIX A10: Luôn redirect về trang chủ, bỏ qua tham số 'redirect' từ URL
    return redirect('/taskManager/')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth_login(request, user)
                security_logger.info(f"Successful login | User: {username} | IP: {request.META.get('REMOTE_ADDR')}")
                return redirect('/taskManager/')
            else:
                return redirect('/taskManager/', {'disabled_user': True})
        else:
            security_logger.warning(f"Failed login | User: {username}")
            return render(request, 'taskManager/login.html', {'failed_login': True})
    else:
        return render(request, 'taskManager/login.html', {})

def register(request):
    registered = False
    if request.method == 'POST':
        # Sử dụng UserForm đã fix A01 (Mass Assignment) ở forms.py
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password) # Hash password an toàn
            user.save()

            UserProfile.objects.create(user=user)
            
            security_logger.info(f"New user registered | User: {user.username}")
            registered = True
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    return render(request, 'taskManager/register.html', {'user_form': user_form, 'registered': registered})

def index(request):
    sorted_projects = Project.objects.order_by('-start_date')
    admin_level = False

    if request.user.is_authenticated:
        if request.user.groups.filter(name='admin_g').exists():
            admin_level = True
        return redirect("/taskManager/dashboard")
    else:
        return render(request, 'taskManager/index.html', {
            'project_list': sorted_projects,
            'user': request.user,
            'admin_level': admin_level
        })

@login_required
def profile_view(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    
    if request.user.groups.filter(name='admin_g').exists():
        role = "Admin"
    elif request.user.groups.filter(name='project_managers').exists():
        role = "Project Manager"
    else:
        role = "Team Member"

    sorted_projects = Project.objects.filter(users_assigned=target_user.id).order_by('title')
    return render(request, 'taskManager/profile_view.html',
                  {'user': target_user, 'role': role, 'project_list': sorted_projects})

@login_required
def project_details(request, project_id):
    proj = get_object_or_404(Project, pk=project_id)
    
    # FIX A01: Check Access
    if not check_project_access(request.user, proj):
        messages.warning(request, 'You are not authorized to view this project')
        return redirect('/taskManager/dashboard')

    user_can_edit = request.user.has_perm('taskManager.change_project')
    security_logger.info(f"Project access | Project: {proj.title} | User: {request.user.username}")
    
    return render(request, 'taskManager/project_details.html',
                  {'proj': proj, 'user_can_edit': user_can_edit})

@login_required
def note_create(request, project_id, task_id):
    proj = get_object_or_404(Project, pk=project_id)
    if not check_project_access(request.user, proj):
        return HttpResponseForbidden()

    if request.method == 'POST':
        parent_task = get_object_or_404(Task, pk=task_id)
        note = Notes(
            title=request.POST.get('note_title', ''),
            text=request.POST.get('text', ''),
            user=request.user.username, # Lưu ý: Model Notes đang lưu username dạng string (xấu nhưng giữ nguyên để tránh lỗi DB)
            task=parent_task
        )
        note.save()
        return redirect('/taskManager/' + project_id + '/' + task_id, {'new_note_added': True})
    else:
        return render(request, 'taskManager/note_create.html', {'task_id': task_id})

@login_required
def note_edit(request, project_id, task_id, note_id):
    proj = get_object_or_404(Project, pk=project_id)
    task = get_object_or_404(Task, pk=task_id)
    note = get_object_or_404(Notes, pk=note_id)

    # FIX A01: IDOR
    if not check_project_access(request.user, proj):
        return HttpResponseForbidden()

    if request.method == 'POST':
        if task.project == proj and note.task == task:
            note.title = request.POST.get('note_title', '')
            note.text = request.POST.get('text', '')
            note.save()
        return redirect('/taskManager/' + project_id + '/' + task_id)
    else:
        return render(request, 'taskManager/note_edit.html', {'note': note})

@login_required
def note_delete(request, project_id, task_id, note_id):
    proj = get_object_or_404(Project, pk=project_id)
    task = get_object_or_404(Task, pk=task_id)
    note = get_object_or_404(Notes, pk=note_id)

    # FIX A01: IDOR
    if check_project_access(request.user, proj) and task.project == proj and note.task == task:
        note.delete()
        return redirect('/taskManager/' + project_id + '/' + task_id)
    
    return HttpResponseForbidden()

@login_required
def task_details(request, project_id, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    # Basic permission checks
    assigned_to = False
    if task.users_assigned.filter(username=request.user.username).exists():
        assigned_to = True
    elif request.user.groups.filter(name='admin_g').exists():
        assigned_to = True

    return render(request, 'taskManager/task_details.html', {
        'task': task,
        'assigned_to': assigned_to,
        'logged_in': request.user.is_authenticated,
        'completed_task': "Yes" if task.completed else "No"
    })

@login_required
def dashboard(request):
    sorted_projects = Project.objects.filter(users_assigned=request.user.id).order_by('title')
    sorted_tasks = Task.objects.filter(users_assigned=request.user.id).order_by('title')
    return render(request, 'taskManager/dashboard.html', {
        'project_list': sorted_projects,
        'user': request.user,
        'task_list': sorted_tasks
    })

@login_required
def project_list(request):
    sorted_projects = Project.objects.filter(users_assigned=request.user.id).order_by('title')
    return render(request, 'taskManager/project_list.html', {
        'project_list': sorted_projects,
        'user': request.user,
        'user_can_edit': request.user.has_perm('taskManager.change_project'),
        'user_can_delete': request.user.has_perm('taskManager.delete_project'),
        'user_can_add': request.user.has_perm('taskManager.add_project')
    })

@login_required
def task_list(request):
    my_task_list = Task.objects.filter(users_assigned=request.user.id)
    return render(request, 'taskManager/task_list.html', {'task_list': my_task_list, 'user': request.user})

@login_required
def search(request):
    query = request.GET.get('q', '')
    # FIX: Chỉ search trong project của mình
    my_project_list = Project.objects.filter(users_assigned=request.user.id, title__icontains=query)
    my_task_list = Task.objects.filter(users_assigned=request.user.id, title__icontains=query)
    
    return render(request, 'taskManager/search.html', {
        'q': query,
        'task_list': my_task_list,
        'project_list': my_project_list,
        'user': request.user
    })

def tutorials(request):
    return render(request, 'taskManager/tutorials.html', {'user': request.user})

def show_tutorial(request, vuln_id):
    valid_ids = ["injection", "brokenauth", "xss", "idor", "misconfig", 
                 "exposure", "access", "csrf", "components", "redirects"]
    if vuln_id in valid_ids:
        return render(request, 'taskManager/tutorials/' + vuln_id + '.html')
    else:
        return render(request, 'taskManager/tutorials.html', {'user': request.user})

@login_required
def profile(request):
    return render(request, 'taskManager/profile.html', {'user': request.user})


# --- FIX A01/A05: CSRF VULNERABILITIES ---
# Đã XÓA @csrf_exempt khỏi tất cả các hàm dưới đây
# Django sẽ tự động bật bảo vệ CSRF

@login_required
def profile_by_id(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    
    # FIX A01: Chỉ được sửa profile của chính mình (trừ khi là superuser)
    if request.user != target_user and not request.user.is_superuser:
        return HttpResponseForbidden("Bạn không thể sửa hồ sơ của người khác.")

    if request.method == 'POST':
        # Dùng Form để validate dữ liệu đầu vào (bao gồm cả file ảnh)
        # Lưu ý: ProfileForm trong forms.py đã được thêm validator chặn file độc
        form = ProfileForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Cập nhật thông tin text
            if request.POST.get('first_name'):
                target_user.first_name = request.POST.get('first_name')
            if request.POST.get('last_name'):
                target_user.last_name = request.POST.get('last_name')
            if request.POST.get('email'):
                target_user.email = request.POST.get('email')
            
            # Xử lý đổi mật khẩu (nếu có nhập)
            new_pass = request.POST.get('password')
            if new_pass:
                target_user.set_password(new_pass)

            # --- KHÔI PHỤC LOGIC UPLOAD ẢNH (Đã vá lỗi A03) ---
            if request.FILES.get('picture'):
                # Lấy file từ request
                uploaded_pic = request.FILES['picture']
                
                # Tạo tên file an toàn: username_filename
                # store_uploaded_file (trong misc.py) đã có cơ chế làm sạch tên file
                safe_filename = f"{target_user.username}_{uploaded_pic.name}"
                
                # Lưu file và lấy đường dẫn
                file_path = store_uploaded_file(safe_filename, uploaded_pic)
                
                # Lưu đường dẫn vào UserProfile
                # Dùng get_or_create để tránh lỗi nếu user cũ chưa có profile
                profile, created = UserProfile.objects.get_or_create(user=target_user)
                profile.image = file_path
                profile.save()

            target_user.save()
            messages.info(request, "Cập nhật hồ sơ thành công!")
        else:
            # Nếu form không hợp lệ (ví dụ upload file .exe)
            messages.warning(request, "Dữ liệu không hợp lệ hoặc file không đúng định dạng.")

    return render(request, 'taskManager/profile.html', {'user': target_user})

def reset_password(request):
    if request.method == 'POST':
        reset_token = request.POST.get('reset_token')
        try:
            userprofile = UserProfile.objects.get(reset_token=reset_token)
            if timezone.now() > userprofile.reset_token_expiration:
                messages.warning(request, 'Token hết hạn')
                return render(request, 'taskManager/reset_password.html')
        except UserProfile.DoesNotExist:
            messages.warning(request, 'Token không hợp lệ')
            return render(request, 'taskManager/reset_password.html')

        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password == confirm_password:
            userprofile.user.set_password(new_password) # Hash password
            userprofile.reset_token = ''
            userprofile.user.save()
            userprofile.save()
            messages.success(request, 'Password reset success')
            return redirect('/taskManager/login')
        else:
            messages.warning(request, 'Passwords do not match')

    return render(request, 'taskManager/reset_password.html')

def forgot_password(request):
    if request.method == 'POST':
        t_email = request.POST.get('email')

        try:
            reset_user = User.objects.get(email=t_email)

            # --- FIX A07: Weak Password Reset Token ---
            # Thay vì dùng os.urandom(6) chỉ ra 6 số (dễ brute-force)
            # Ta dùng secrets.token_urlsafe(32) -> Ra chuỗi ngẫu nhiên dài, cực khó đoán.
            # (Làm được điều này là nhờ bạn đã sửa max_length=100 trong models.py)
            reset_token = secrets.token_urlsafe(32)

            # Xử lý an toàn: Nếu chưa có profile thì tạo mới, có rồi thì lấy ra
            profile, created = UserProfile.objects.get_or_create(user=reset_user)
            
            profile.reset_token = reset_token
            profile.reset_token_expiration = timezone.now() + datetime.timedelta(minutes=10)
            profile.save()

            # Gửi email (Logic cũ)
            reset_user.email_user(
                "Reset your password",
                f"You can reset your password at /taskManager/reset_password/. Use \"{reset_token}\" as your token. This link will only work for 10 minutes."
            )

            security_logger.info(
                f"Password reset requested | User: {reset_user.username} | Email: {t_email} | IP: {request.META.get('REMOTE_ADDR', 'unknown')}"
            )
            messages.success(request, 'Check your email for a reset token')
            return redirect('/taskManager/reset_password')

        except User.DoesNotExist:
            # FIX: Username Enumeration protection
            # Dù email không tồn tại, vẫn báo thành công giả để hacker không biết email này có trong hệ thống không.
            security_logger.warning(f"Password reset attempted for non-existent email: {t_email}")
            messages.warning(request, 'Check your email for a reset token')

    return render(request, 'taskManager/forgot_password.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if user.check_password(old_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                auth_login(request, user) # Giữ đăng nhập sau khi đổi pass
                messages.success(request, 'Password Updated')
                return redirect('/taskManager/')
            else:
                messages.warning(request, 'Passwords do not match')
        else:
            messages.warning(request, 'Invalid Password')

    return render(request, 'taskManager/change_password.html', {'user': request.user})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def tm_settings(request):
    # Chỉ superuser mới được xem settings server
    settings_list = request.META
    return render(request, 'taskManager/settings.html', {'settings': settings_list})