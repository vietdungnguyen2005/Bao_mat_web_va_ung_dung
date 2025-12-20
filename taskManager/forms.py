""" forms.py contains various Django forms for the application """

import os
from django import forms
from django.contrib.auth.models import User
from taskManager.models import Project, Task
from django.core.exceptions import ValidationError

# --- FIX A03: Thêm hàm kiểm tra đuôi file (Input Validation) ---
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # Lấy đuôi file
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls', '.txt', '.jpeg']
    if not ext.lower() in valid_extensions:
        raise ValidationError('File không hợp lệ! Chỉ chấp nhận: pdf, doc, xls, jpg, png, txt.')

# --- Helper Functions (Giữ nguyên logic cũ để tránh lỗi View) ---
def get_my_choices_users():
    user_list = User.objects.order_by('date_joined')
    user_tuple = []
    counter = 1
    for user in user_list:
        user_tuple.append((counter, user))
        counter = counter + 1
    return user_tuple

def get_my_choices_tasks(current_proj):
    task_list = []
    tasks = Task.objects.all()
    for task in tasks:
        if task.project == current_proj:
            task_list.append(task)
    task_tuple = []
    counter = 1
    for task in task_list:
        task_tuple.append((counter, task))
        counter = counter + 1
    return task_tuple

def get_my_choices_projects():
    proj_list = Project.objects.all()
    proj_tuple = []
    counter = 1
    for proj in proj_list:
        proj_tuple.append((counter, proj))
        counter = counter + 1
    return proj_tuple


# --- FIX A01: MASS ASSIGNMENT ---
class UserForm(forms.ModelForm):
    """ User registration form """
    password = forms.CharField(widget=forms.PasswordInput()) # Ẩn password khi nhập

    class Meta:
        model = User
        # FIX: Thay vì dùng exclude (loại trừ), ta dùng fields (whitelist).
        # Chỉ cho phép người dùng nhập đúng 5 trường này.
        # Các trường nguy hiểm như is_superuser, is_staff sẽ bị chặn.
        fields = ['username', 'first_name', 'last_name', 'email', 'password']


# --- FIX A03: INPUT VALIDATION (FILE UPLOAD) ---
class ProjectFileForm(forms.Form):
    """ Used for uploading files attached to projects """
    name = forms.CharField(max_length=300)
    # FIX: Thêm validators để chặn file mã độc (.exe, .sh, .py...)
    file = forms.FileField(validators=[validate_file_extension])


class ProfileForm(forms.Form):
    """ Provides a form for editing your own profile """
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.CharField(max_length=300, required=False)
    # FIX: Thêm validators cho ảnh đại diện
    picture = forms.FileField(required=False, validators=[validate_file_extension])