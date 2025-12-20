#     _  _                        __   __
#  __| |(_)__ _ _ _  __ _ ___   _ \ \ / /
# / _` || / _` | ' \/ _` / _ \_| ' \ V /
# \__,_|/ \__,_|_||_\__, \___(_)_||_\_/
#     |__/          |___/
#
#           SECURE APPLICATION VERSION (PATCHED)
#

import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

# Hàm helper để tránh lỗi migration trong Django 5.0
def get_default_due_date():
    return timezone.now() + datetime.timedelta(weeks=1)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.CharField(max_length=3000, default="")
    
    # --- FIX A07: Identification and Authentication Failures ---
    # Tăng độ dài từ 7 lên 100 để chứa được token mã hóa mạnh (SHA, UUID...)
    reset_token = models.CharField(max_length=100, default="")
    
    reset_token_expiration = models.DateTimeField(default=timezone.now)

class Project(models.Model):
    title = models.CharField(max_length=50, default='Default')
    text = models.CharField(max_length=500)
    start_date = models.DateTimeField('date started')
    
    # Sử dụng hàm helper cho default value
    due_date = models.DateTimeField(
        'date due',
        default=get_default_due_date
    )
    users_assigned = models.ManyToManyField(User)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.title

    def was_created_recently(self):
        return self.start_date >= timezone.now() - datetime.timedelta(days=1)

    def is_overdue(self):
        return self.due_date <= timezone.now()

    def percent_complete(self):
        counter = 0
        # Dùng .all() thay vì truy cập trực tiếp set
        for task in self.task_set.all():
            counter = counter + (1 if task.completed else 0)
        try:
            return round(float(counter) / self.task_set.count() * 100)
        except ZeroDivisionError:
            return 0


class Task(models.Model):
    project = models.ForeignKey(Project, default=1, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    title = models.CharField(max_length=200, default="N/A")
    start_date = models.DateTimeField('date created')
    
    due_date = models.DateTimeField(
        'date due',
        default=get_default_due_date
    )
    
    # --- FIX Compatibility Django 5.0 ---
    # NullBooleanField đã bị xóa. Thay bằng BooleanField(null=True)
    # Thêm default=False để tránh lỗi logic khi tính % hoàn thành
    completed = models.BooleanField(null=True, default=False)
    
    users_assigned = models.ManyToManyField(User)

    def __str__(self):
        return self.text

    def was_created_recently(self):
        return self.start_date >= timezone.now() - datetime.timedelta(days=1)

    def is_overdue(self):
        return self.due_date <= timezone.now()

    def percent_complete(self):
        return 100 if self.completed else 0


class Notes(models.Model):
    task = models.ForeignKey(Task, default=1, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default="N/A")
    text = models.CharField(max_length=200)
    image = models.CharField(max_length=200)
    
    # Lưu ý: Vẫn giữ CharField cho user để tương thích với dữ liệu cũ (fixtures)
    # Nếu đổi sang ForeignKey sẽ phải sửa lại toàn bộ file json data.
    user = models.CharField(max_length=200, default='ancestor')

    def __str__(self):
        return self.text


class File(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=300, default="")
    path = models.CharField(max_length=3000, default="")

    def __str__(self):
        return self.name