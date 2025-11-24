# api/urls.py
from django.urls import path
from .views import ConversationsListCreate, MessageListCreate

urlpatterns = [
    path('conversations/', ConversationsListCreate.as_view(), name='conversations'),
    path('conversations/<int:pk>/messages/', MessageListCreate.as_view(), name='conversation-messages'),
]
