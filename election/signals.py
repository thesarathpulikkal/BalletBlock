from django.dispatch import receiver
from django.db.models.signals import pre_save
from election.models import ElectionConfig
from election.business import ElectionBusiness
import datetime
from django.core.exceptions import ValidationError

@receiver(pre_save, sender=ElectionConfig)
def canModify(sender, instance, **kwargs):
    if ElectionConfig.objects.count() > 0 and instance.id is None:
        # We can not have more than one election config
        raise ValidationError('Add more than one election config is forbidden')

    eb = ElectionBusiness()
    if eb.isLocked() and not eb.hadFinished():
        raise ValidationError('Election is locked and can not be changed.')


