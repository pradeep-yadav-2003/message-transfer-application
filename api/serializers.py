# api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .crypto_service import message_service

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email')

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    decrypted = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id','conversation','sender','encrypted_content','decrypted','created_at')
        read_only_fields = ('id','sender','decrypted','created_at')

    def get_decrypted(self, obj):
        try:
            return message_service.decrypt(obj.encrypted_content)
        except Exception:
            return None

class CreateMessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class ConversationSerializer(serializers.ModelSerializer):
    user1 = UserSerializer()
    user2 = UserSerializer()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ('id','user1','user2','created_at','last_message')

    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        if not last:
            return None
        try:
            snippet = message_service.decrypt(last.encrypted_content)
        except Exception:
            snippet = None
        return {
            "id": last.id,
            "sender_id": last.sender.id,
            "snippet": snippet[:80] if snippet else None,
            "created_at": last.created_at
        }
