from election.models import ElectionConfig
from django.contrib import messages
import datetime

class ElectionBusiness():

    def getCurrentElectionConfig(self):
        ecs = ElectionConfig.objects.all()
        if ecs.count() > 0:
            return ecs[0]
        return None

    def canModify(self, request=None):
        if self.isLocked():
            if request:
                msg = 'Election is locked and end time is {}'.format(ec.end_time.isoformat())
                messages.error(request, msg)
            return False
        return True

    def canAdd(self, request=None):
        if ElectionConfig.objects.all().count() > 0:
            if request:
                msg = 'Add more than one election config is forbidden'
                messages.error(request, msg)
            return False
        return True

    def isLocked(self):
        ec = self.getCurrentElectionConfig()
        if ec:
            return ec.locked
        return False

    def isOccurring(self):
        ec = self.getCurrentElectionConfig()
        if ec:
            now = datetime.datetime.now()
            if ec.start_time.isoformat() <= now.isoformat() and \
                    now.isoformat() <= ec.end_time.isoformat() and ec.locked:
                return True
        return False

    def hadFinished(self):
        ec = self.getCurrentElectionConfig()
        if ec:
            now = datetime.datetime.now()
            if ec.end_time.isoformat() < now.isoformat():
                return True
        return False
        