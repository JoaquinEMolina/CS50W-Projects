from django.utils.timezone import localtime
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)
    def serialize(self):
        return {
            "username": self.username
        }

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="posts")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    
    def serialize(self, user=None):
        return {
            "id": self.id,
            "user": self.user.username,
            "body": self.body,
            "timestamp": localtime(self.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "likes": {
                "count": self.likes.count(),
                "liked": bool(user and self.likes.filter(id=user.id).exists())
            }
        }
