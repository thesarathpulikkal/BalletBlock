from django.db import models, connections
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def present_or_future_date_starttime(start_time):
    if start_time < datetime.now():
        raise ValidationError("Check if the start time is set properly.")

def present_or_future_date_endtime(end_time):
    if end_time < datetime.now():
        raise ValidationError("Check if the end time is set properly.")

class ElectionConfig(models.Model):
    description = models.CharField(max_length=100, null=False, blank=False, default='Generic Election')
    start_time = models.DateTimeField(null=False, blank=False)
    end_time = models.DateTimeField(null=False, blank=False)
    block_time_generation = models.IntegerField(default=2)
    guess_rate = models.DecimalField(null=False, blank=False, max_digits=5,decimal_places=4, validators=[MinValueValidator(Decimal('0.0001')), MaxValueValidator(Decimal('0.9999'))], default=Decimal('0.4'))
    min_votes_in_block = models.IntegerField(null=False, blank=False, default=6)
    min_votes_in_last_block = models.IntegerField(null=False, blank=False, default=6)
    attendance_rate = models.DecimalField(null=False, blank=False, max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('0.99'))], default=Decimal('0.5'))
    locked = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class Elector(models.Model):
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name()

class Position(models.Model):
    description = models.CharField(max_length=100, unique=True, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False, default=1)

    def __str__(self):
        return self.description

class Candidate(models.Model):
    name = models.CharField(max_length=300, unique=True, null=False, blank=False)
    position = models.ForeignKey(Position, null=False, blank=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
