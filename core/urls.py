# core/urls.py
from django.urls import path
from . import views
from django.http import HttpResponse

urlpatterns = [
    path('', views.home,name='dashboard'),
    path('lector/login/', views.lector_login, name='lector-login'),
    path('lector/register/', views.lector_register, name='lector-register'),
    path('student/login/', views.student_login, name='student-login'),
    path('student/register/', views.student_register, name='student-register'),

    path('lector_dashboard/', views.lector_dashboard, name='lector_dashboard'),
    path('student_dashboard/',views.student_dashboard,name='student_dashboard'),
    
    path('lector/manage-students/', views.manage_students, name='manage_students'),
    path('lector/remove-student/<int:student_id>/', views.remove_student, name='remove_student'),
    path('lector/manage-groups/', views.manage_groups, name='manage_groups'),
    path('lector/group/<int:group_id>/add-student/', views.add_student_to_group, name='add_student_to_group'),
    path('lector/group/<int:group_id>/remove-student/<int:student_id>/', views.remove_student_from_group, name='remove_student_from_group'),
    path('lector/group/<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('logout/', views.logout_view, name='logout'),
    
    path('student/group/<int:group_id>/', views.student_group_page, name='student_group_page'),
    path('lector/group/<int:group_id>/', views.lector_group_page, name='lector_group_page'),

    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('groups/<int:group_id>/enter-points/', views.add_point, name='enter_points'),
    path('groups/<int:group_id>/points/', views.view_points, name='view_points'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    path('private/<str:receiver_type>/<int:receiver_id>/', views.private_chat, name='private_chat'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    
    path('ai-chat/', views.chat_page, name='chat'),
    path('ai-chat/api/send/', views.send_message, name='send_message'),


    path('private-message/delete/<int:message_id>/', views.delete_private_message, name='delete_private_message'),
    path('private-message/update/<int:message_id>/', views.update_private_message, name='update_private_message'),
    path('private-messages/bulk-delete/', views.bulk_delete_private_messages, name='bulk_delete_private_messages'),
    
    # Group Chat Message CRUD
    path('group-message/delete/<int:message_id>/', views.delete_group_message, name='delete_group_message'),
    path('group-message/update/<int:message_id>/', views.update_group_message, name='update_group_message'),
    path('group-messages/bulk-delete/', views.bulk_delete_group_messages, name='bulk_delete_group_messages'),

    
]


