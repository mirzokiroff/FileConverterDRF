from django.contrib.auth.models import AbstractUser
from django.db.models import CharField


class UserProfile(AbstractUser):
    password = CharField(max_length=111)
    confirm_password = CharField(max_length=111)

    def __str__(self):
        return self.username
