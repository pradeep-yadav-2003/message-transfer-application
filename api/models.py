# api/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Conversation(models.Model):
    # Normalize order: always store (user1.id < user2.id) to make uniqueness easy
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # ensure one conversation per unordered pair
        unique_together = (('user1','user2'),)
        ordering = ['-created_at']

    def __str__(self):
        return f"Conversation {self.id}: {self.user1.email} <-> {self.user2.email}"

    @classmethod
    def get_or_create_between(cls, a, b):
        """Return conversation for users a and b; normalize order internally."""
        if a.id == b.id:
            raise ValueError("Cannot create conversation with same user")
        u1, u2 = (a, b) if a.id < b.id else (b, a)
        conv, created = cls.objects.get_or_create(user1=u1, user2=u2)
        return conv, created

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_content = models.TextField()   # store encrypted string (Fernet token)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message {self.id} in Conv {self.conversation.id} by {self.sender.email}"
