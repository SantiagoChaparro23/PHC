from django.db import models
from django.contrib.auth.models import User

# Create your models here.
STATE = {
    (1, 'Activo'),
    (2, 'Retirado')
}


class Collaborator(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, blank = False, null = False)
    entry_at = models.DateField()
    id_card = models.BigIntegerField(blank=True, null=True)
    salary = models.IntegerField(default=0, blank=True, null=True)
    state = models.IntegerField(choices=STATE, default=1, blank=False, null=False)

    class Meta:
        verbose_name = 'Collaborator'
        ordering = ['entry_at']

    def __str__(self):
        return str(f'{self.user.first_name} {self.user.last_name}')


class Settings(models.Model):
    days_max = models.IntegerField(blank=True, null=True)
    notify_days_max = models.IntegerField(blank=True, null=True)
    group_notify_days_max = models.CharField(default='[]', max_length=500, blank=True, null=True)
    group_notify_request = models.CharField(default='[]', max_length=500, blank=True, null=True)
    notify_request_pending = models.IntegerField(blank=True, null=True)
    group_notify_request_pending = models.CharField(default='[]', max_length=500, blank=True, null=True)
    group_notify_request_accepted = models.CharField(default='[]', max_length=500, blank=True, null=True)
    group_notify_request_deny_final_acceptor = models.CharField(default='[]', max_length=500, blank=True, null=True)
    group_notify_liquidation_deny = models.CharField(default='[]', max_length=500, blank=True, null=True)
    final_acceptor = models.ForeignKey(User, on_delete = models.CASCADE, blank = False, null = False)

    class Meta:
        verbose_name = 'Settings'
        ordering = ['id']

    def __str__(self):
        return str(self.id)


class Bonus(models.Model):
    collaborator = models.ForeignKey(Collaborator, on_delete = models.CASCADE, blank=False, null=False)
    extra_days = models.IntegerField(blank=False, null=False)
    expiration_at = models.DateField(blank=False, null=False)
    bonus_state = models.BooleanField(default=True)
    description = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'Bonus'
        ordering = ['-id']

    def __str__(self):
        return str(self.collaborator)


class DaysCaused(models.Model):
    collaborator = models.ForeignKey(Collaborator, on_delete = models.CASCADE, blank=False, null=False)
    days_caused = models.IntegerField(blank=False, null=False)
    description = models.TextField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name = 'Days Caused'
        ordering = ['-id']

    def __str__(self):
        return str(self.collaborator)


class Requests(models.Model):
    collaborator = models.ForeignKey(Collaborator, on_delete = models.CASCADE, blank = False, null = False)
    leader = models.ForeignKey(User, on_delete = models.CASCADE, blank = False, null = False, related_name = 'leader')
    final_acceptor = models.ForeignKey(User, on_delete = models.CASCADE, blank = True, null = True, related_name = 'final_acceptor')
    accepted_leader = models.BooleanField(default=None, blank=True, null=True)
    date_leader = models.DateTimeField(default=None, blank=True, null=True)
    accepted_final_acceptor = models.BooleanField(default=None, blank=True, null=True)
    date_final_acceptor = models.DateTimeField(default=None, blank=True, null = True)
    request_completed = models.BooleanField(default=None, blank=True, null=True)
    start_date_vacations = models.DateField(blank=True, null=True)
    end_date_vacations = models.DateField(blank=True, null=True)
    calendar_days_taken = models.IntegerField(blank=True, null=True)
    business_days_taken = models.IntegerField(blank=True, null=True)
    accepted_liquidation = models.BooleanField(default=None, blank=True, null=True)
    path_liquidation = models.CharField(max_length=255, blank=True, null=True)
    comments = models.TextField(max_length=1000, blank=True, null=True)

    class Meta:
        verbose_name = 'Requests'
        ordering = ['-id']

    def __str__(self):
        return str(self.collaborator)
