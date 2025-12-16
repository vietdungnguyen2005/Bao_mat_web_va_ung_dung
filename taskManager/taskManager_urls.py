#     _  _                        __   __
#  __| |(_)__ _ _ _  __ _ ___   _ \ \ / /
# / _` || / _` | ' \/ _` / _ \_| ' \ V /
# \__,_|/ \__,_|_||_\__, \___(_)_||_\_/
#     |__/          |___/
#
#                       INSECURE APPLICATION WARNING
#
# django.nV is a PURPOSELY INSECURE web-application
# meant to demonstrate Django security problems
# UNDER NO CIRCUMSTANCES should you take any code
# from django.nV for use in another web application!
#

# from django.conf.urls import patterns, url

# from taskManager import views

# urlpatterns = patterns('',
#                        url(r'^$', views.index, name='index'),

#                        # File
#                        url(r'^download/(?P<file_id>\d+)/$',
#                            views.download, name='download'),
#                        url(r'^(?P<project_id>\d+)/upload/$',
#                            views.upload, name='upload'),
#                        url(r'^downloadprofilepic/(?P<user_id>\d+)/$',
#                            views.download_profile_pic, name='download_profile_pic'),

#                        # Authentication & Authorization
#                        url(r'^register/$', views.register, name='register'),
#                        url(r'^login/$', views.login, name='login'),
#                        url(r'^logout/$', views.logout_view, name='logout'),
#                        url(r'^manage_groups/$', views.manage_groups,
#                            name='manage_groups'),
#                        url(r'^profile/$', views.profile, name='profile'),
#                        url(r'^change_password/$', views.change_password,
#                            name='change_password'),
#                       url(r'^forgot_password/$', views.forgot_password,
#                            name='forgot_password'),
#                       url(r'^reset_password/$', views.reset_password,
#                            name='reset_password'),
#                        url(r'^profile/(?P<user_id>\d+)$',
#                            views.profile_by_id, name='profile_by_id'),
#                        url(r'^profile_view/(?P<user_id>\d+)$',
#                            views.profile_view, name='profile_view'),

#                        # Projects
#                        url(r'^project_create/$', views.project_create,
#                            name='project_create'),
#                        url(r'^(?P<project_id>\d+)/edit_project/$',
#                            views.project_edit, name='project_edit'),
#                        url(r'^manage_projects/$', views.manage_projects,
#                            name='manage_projects'),
#                        url(r'^(?P<project_id>\d+)/project_delete/$',
#                            views.project_delete, name='project_delete'),
#                        url(r'^(?P<project_id>\d+)/$',
#                            views.project_details, name='project_details'),
#                        url(r'^project_list/$', views.project_list,
#                            name='project_list'),

#                        # Tasks
#                        url(r'^(?P<project_id>\d+)/task_create/$',
#                            views.task_create, name='task_create'),
#                        url(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/$',
#                            views.task_details, name='task_details'),
#                        url(r'^(?P<project_id>\d+)/task_edit/(?P<task_id>\d+)$',
#                            views.task_edit, name='task_edit'),
#                        url(r'^(?P<project_id>\d+)/task_delete/(?P<task_id>\d+)$',
#                            views.task_delete, name='task_delete'),
#                        url(r'^(?P<project_id>\d+)/task_complete/(?P<task_id>\d+)$',
#                            views.task_complete, name='task_complete'),
#                        url(r'^task_list/$', views.task_list, name='task_list'),
#                        url(r'^(?P<project_id>\d+)/manage_tasks/$',
#                            views.manage_tasks, name='manage_tasks'),


#                        # Notes
#                        url(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/note_create/$',
#                            views.note_create, name='note_create'),
#                        url(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/note_edit/(?P<note_id>\d+)$',
#                            views.note_edit, name='note_edit'),
#                        url(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/note_delete/(?P<note_id>\d+)$',
#                            views.note_delete, name='note_delete'),

#                        url(r'^dashboard/$', views.dashboard, name='dashboard'),
#                        url(r'^search/$', views.search, name='search'),


#                        # Tutorials
#                        url(r'^tutorials/$', views.tutorials, name='tutorials'),
#                        url(r'^tutorials/(?P<vuln_id>[a-z\-]+)/$',
#                            views.show_tutorial, name='show_tutorial'),

#                        # Settings - DEBUG
#                        url(r'^settings/$', views.tm_settings, name='settings'),
#                       )



from django.urls import re_path
from taskManager import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),

    # File
    re_path(r'^download/(?P<file_id>\d+)/$', views.download, name='download'),
    re_path(r'^(?P<project_id>\d+)/upload/$', views.upload, name='upload'),
    re_path(r'^downloadprofilepic/(?P<user_id>\d+)/$', views.download_profile_pic, name='download_profile_pic'),

    # Authentication & Authorization
    re_path(r'^register/$', views.register, name='register'),
    re_path(r'^login/$', views.login, name='login'),
    re_path(r'^logout/$', views.logout_view, name='logout'),
    re_path(r'^manage_groups/$', views.manage_groups, name='manage_groups'),
    re_path(r'^profile/$', views.profile, name='profile'),
    re_path(r'^change_password/$', views.change_password, name='change_password'),
    re_path(r'^forgot_password/$', views.forgot_password, name='forgot_password'),
    re_path(r'^reset_password/$', views.reset_password, name='reset_password'),
    re_path(r'^profile/(?P<user_id>\d+)$', views.profile_by_id, name='profile_by_id'),
    re_path(r'^profile_view/(?P<user_id>\d+)$', views.profile_view, name='profile_view'),

    # Projects
    re_path(r'^project_create/$', views.project_create, name='project_create'),
    re_path(r'^(?P<project_id>\d+)/edit_project/$', views.project_edit, name='project_edit'),
    re_path(r'^manage_projects/$', views.manage_projects, name='manage_projects'),
    re_path(r'^(?P<project_id>\d+)/project_delete/$', views.project_delete, name='project_delete'),
    re_path(r'^(?P<project_id>\d+)/$', views.project_details, name='project_details'),
    re_path(r'^project_list/$', views.project_list, name='project_list'),

    # Tasks
    re_path(r'^(?P<project_id>\d+)/task_create/$', views.task_create, name='task_create'),
    re_path(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/$', views.task_details, name='task_details'),
    re_path(r'^(?P<project_id>\d+)/task_edit/(?P<task_id>\d+)$', views.task_edit, name='task_edit'),
    re_path(r'^(?P<project_id>\d+)/task_delete/(?P<task_id>\d+)$', views.task_delete, name='task_delete'),
    re_path(r'^(?P<project_id>\d+)/task_complete/(?P<task_id>\d+)$', views.task_complete, name='task_complete'),
    re_path(r'^task_list/$', views.task_list, name='task_list'),
    re_path(r'^(?P<project_id>\d+)/manage_tasks/$', views.manage_tasks, name='manage_tasks'),

    # Notes
    re_path(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/note_create/$', views.note_create, name='note_create'),
    re_path(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/note_edit/(?P<note_id>\d+)$', views.note_edit, name='note_edit'),
    re_path(r'^(?P<project_id>\d+)/(?P<task_id>\d+)/note_delete/(?P<note_id>\d+)$', views.note_delete, name='note_delete'),

    re_path(r'^dashboard/$', views.dashboard, name='dashboard'),
    re_path(r'^search/$', views.search, name='search'),

    # Tutorials
    re_path(r'^tutorials/$', views.tutorials, name='tutorials'),
    re_path(r'^tutorials/(?P<vuln_id>[a-z\-]+)/$', views.show_tutorial, name='show_tutorial'),

    # Settings - DEBUG
    re_path(r'^settings/$', views.tm_settings, name='settings'),
]