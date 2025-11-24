# api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer, CreateMessageSerializer
from .crypto_service import message_service

User = get_user_model()

class ConversationsListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        # Do NOT use union()  ----> SQLite breaks
        qs1 = list(Conversation.objects.filter(user1=user))
        qs2 = list(Conversation.objects.filter(user2=user))

        conversations = qs1 + qs2   # merge lists

        # Python-side sorting (SQLite safe)
        conversations = sorted(conversations, key=lambda c: c.created_at, reverse=True)

        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create conversation with 'other_email' in body"""
        other_email = request.data.get("other_email")
        if not other_email:
            return Response({"error": "other_email required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            other = User.objects.get(email=other_email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        conv, created = Conversation.get_or_create_between(request.user, other)
        return Response({
            "id": conv.id,
            "created": created
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class MessageListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_conversation(self, pk):
        return get_object_or_404(Conversation, pk=pk)

    def get(self, request, pk):
        conv = self.get_conversation(pk)

        # check if user is a participant
        if request.user not in (conv.user1, conv.user2):
            return Response({"error": "Not permitted"}, status=status.HTTP_403_FORBIDDEN)

        qs = conv.messages.all().order_by("created_at")
        serializer = MessageSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        conv = self.get_conversation(pk)

        # permission check
        if request.user not in (conv.user1, conv.user2):
            return Response({"error": "Not permitted"}, status=status.HTTP_403_FORBIDDEN)

        serializer_in = CreateMessageSerializer(data=request.data)
        if not serializer_in.is_valid():
            return Response(serializer_in.errors, status=status.HTTP_400_BAD_REQUEST)

        plaintext = serializer_in.validated_data["message"]

        # encrypt message
        encrypted = message_service.encrypt(plaintext)

        msg = Message.objects.create(
            conversation=conv,
            sender=request.user,
            encrypted_content=encrypted
        )

        serializer_out = MessageSerializer(msg)
        return Response(serializer_out.data, status=status.HTTP_201_CREATED)
