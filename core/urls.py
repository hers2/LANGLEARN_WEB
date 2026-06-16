from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('grammar/', views.grammar_view, name='grammar'),
    path(
    'grammar/history/<path:mistake_type>/',
    views.grammar_history_by_type_view,
    name='grammar_history_by_type'
    ),

    path('chat/', views.chat_start_view, name='chat'),
    path('chat/<int:session_id>/', views.chat_session_view, name='chat_session'),
    path('chat/<int:session_id>/finish/', views.finish_chat_view, name='finish_chat'),
    path('chat/<int:session_id>/clear/', views.clear_chat_view, name='clear_chat'),
    path('chat/<int:session_id>/delete/', views.delete_chat_view, name='delete_chat'),

    path('quiz/', views.quiz_view, name='quiz'),
    path('progress/', views.progress_view, name='progress'),
    path('progress/reset/', views.reset_progress_view, name='reset_progress'),

    path('operator/questions/', views.operator_questions_view, name='operator_questions'),
    path('operator/questions/add/', views.operator_question_create_view, name='operator_question_add'),
    path('operator/questions/<int:pk>/edit/', views.operator_question_update_view, name='operator_question_edit'),
    path('operator/questions/<int:pk>/delete/', views.operator_question_delete_view, name='operator_question_delete'),
]