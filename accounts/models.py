from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    wix_member_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    last_announcement_view_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Perfil de {self.user.username}'

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"De {self.sender} para {self.receiver} em {self.timestamp}"

    @staticmethod
    def cleanup_old_messages():
        """Remove mensagens com mais de 10 dias"""
        cutoff_date = timezone.now() - timedelta(days=10)
        ChatMessage.objects.filter(timestamp__lt=cutoff_date).delete()

# Signals para garantir que o perfil sempre exista
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        # Garante que o perfil exista mesmo se o usuário já existia
        Profile.objects.get_or_create(user=instance)
