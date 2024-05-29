# from django.conf import settings
# from django.db import models
# from django.contrib.auth.models import AbstractUser


# class UserProfile(AbstractUser):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_profile')
#     surname = models.CharField(max_length=30, verbose_name='Отчество', null=True, blank=True, default=None)
#     phone = models.CharField(max_length=15, verbose_name='Телефон', null=True, blank=True, default=None)
#     addres = models.CharField(max_length=255, verbose_name='Адрес', null=True, blank=True, default=None)


#     def __str__(self):
#         return self.user.username
