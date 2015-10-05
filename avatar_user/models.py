from django.db import models


class Account(models.Model):
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=128)
    ticket = models.CharField(max_length=36, null=True)
    last_login = models.DateTimeField(null=True)
    last_update = models.DateTimeField(null=True)
    register_time = models.DateTimeField(null=True)

    def __str__(self):
        return self.id
