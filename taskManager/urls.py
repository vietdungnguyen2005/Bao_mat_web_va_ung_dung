#     _  _                        __   __
#  __| |(_)__ _ _ _  __ _ ___   _ \ \ / /
# / _` || / _` | ' \/ _` / _ \_| ' \ V /
# \__,_|/ \__,_|_||_\__, \___(_)_||_\_/
#     |__/          |___/
#
#			INSECURE APPLICATION WARNING
#
# django.nV is a PURPOSELY INSECURE web-application
# meant to demonstrate Django security problems
# UNDER NO CIRCUMSTANCES should you take any code
# from django.nV for use in another web application!
#

# from django.conf.urls import patterns, include, url
# from django.contrib import admin

# urlpatterns = patterns('',
#                        url(r'^$',
#                            'taskManager.views.index',
#                            name='index'),
#                        url(r'^taskManager/',
#                            include('taskManager.taskManager_urls',
#                                    namespace="taskManager")),
#                        url(r'^admin/',
#                            include(admin.site.urls)),
#                       )

from django.contrib import admin
from django.urls import path, include, re_path
from taskManager import views

urlpatterns = [
    # Trang chủ
    re_path(r'^$', views.index, name='index'),
    
    # Include URLs của app taskManager với namespace để template không bị lỗi
    # Cú pháp: include((module, app_name), namespace)
    path('taskManager/', include(('taskManager.taskManager_urls', 'taskManager'), namespace='taskManager')),
    
    # Trang admin
    path('admin/', admin.site.urls),
]