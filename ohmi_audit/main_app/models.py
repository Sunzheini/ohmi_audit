from django.db import models


class Audit(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Auditor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name
