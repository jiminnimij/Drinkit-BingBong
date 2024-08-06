from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Mypage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nickname = models.CharField(max_length=20, blank=True, default="익명")
    image = models.ImageField(upload_to='mypage/', default='default.png')
    friends = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='friends_with')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Mypage.objects.create(user=instance)

# Create your models here.

class Timer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    time_left = models.IntegerField(default=7200)
    is_running = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user}'s Timer"