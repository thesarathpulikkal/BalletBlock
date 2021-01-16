from django.db import models
from election.models import Elector, Candidate

class Voted(models.Model):
    elector = models.OneToOneField(Elector, blank=False, null=False, unique=True, on_delete=models.CASCADE)
    hash_val= models.CharField(max_length=200, null=True, blank=False, default=None)
    system_signature = models.TextField(null=True, blank=True)

class CandidateVote(models.Model):
    candidate = models.OneToOneField(Candidate, blank=False, null=False, unique=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
