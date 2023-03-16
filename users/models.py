from django.db import models
from django.contrib.auth.models import User


class Roles(models.Model):
    role = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Roles'
        ordering = ['role']

    def __str__(self):
        return str(self.role)


class RolesUsers(models.Model):
    role = models.ForeignKey(Roles, on_delete=models.CASCADE, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)

    class Meta:
        verbose_name_plural = 'Roles users'
        ordering = ['role']

    def __str__(self):
        return str(self.role)
