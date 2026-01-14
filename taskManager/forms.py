""" forms.py contains various Django forms for the application """

from taskManager.models import Project, Task
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import re

def get_my_choices_users(user):
    accessible_projects = Project.objects.filter(users=user)
    
    user_list = User.objects.filter(taskmanager_project__in=accessible_projects).distinct()
    
    user_tuple = []
    counter = 1
    for u in user_list:
        user_tuple.append((counter, u))
        counter += 1
    return user_tuple


def get_my_choices_tasks(current_proj):
    """ Retrieves all tasks in the system for the task management page
    """
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


def get_my_choices_projects(user):
    proj_list = Project.objects.filter(users=user)
    
    proj_tuple = []
    counter = 1
    for proj in proj_list:
        proj_tuple.append((counter, proj))
        counter += 1
    return proj_tuple

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_password(self):
        data = self.cleaned_data.get('password')
        if data:
            if len(data) < 8:
                raise ValidationError("Mật khẩu quá ngắn (tối thiểu 8 ký tự).")
            
            # Kiểm tra độ khó: Phải có chữ thường, hoa, số, ký tự đặc biệt
            if not re.match(r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).+$', data):
                raise ValidationError("Mật khẩu yếu! Cần có: chữ hoa, thường, số và ký tự đặc biệt.")
        return data

class ProjectFileForm(forms.Form):
    """ Used for uploading files attached to projects """
    name = forms.CharField(max_length=300)
    file = forms.FileField()

class ProfileForm(forms.Form):

    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=300, required=False) 
    
    picture = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])]
    )
    
    def clean_first_name(self):
        data = self.cleaned_data['first_name']
        if data:
            if not re.match(r'^[a-zA-Z\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]*$', data):
                raise ValidationError("Tên không được chứa ký tự đặc biệt (Script, thẻ HTML...).")
        return data

    def clean_last_name(self):
        data = self.cleaned_data['last_name']
        if data:
            if not re.match(r'^[a-zA-Z\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]*$', data):
                raise ValidationError("Họ không được chứa ký tự đặc biệt.")
        return data

    def clean_picture(self):
        picture = self.cleaned_data.get('picture')
        
        if picture:
            if picture.size > 2 * 1024 * 1024:
                raise ValidationError("File ảnh quá lớn (tối đa 2MB).")

            if hasattr(picture, 'content_type'):
                main_type = picture.content_type.split('/')[0]
                if main_type != 'image':
                    raise ValidationError("File tải lên không phải là ảnh hợp lệ.")
                
        return picture