

from django.urls import path
from . import views

urlpatterns = [
    path('NGO_signup/',  views.registerUser, name="NGO_signup"),
    path('home/', views.home2, name="home"),
    path('edit/',  views.editAccountForNGO, name="edit"),
    path('login/',  views.loginUser, name="login"),
    path('create-skill/', views.createSkill, name="add_skill"),
    path('post-project/', views.post_project, name="post_project"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('browse_jobs/', views.browse_jobs, name='browse_jobs'),
    path('task_description/<int:task_id>/', views.taskdesc, name='task_description'),










    
]

