from django.shortcuts import render
from election.models import Position, Candidate, Elector
from vote.models import Voted, CandidateVote
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.decorators import login_required
import datetime
from election.business import ElectionBusiness
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.core.signing import Signer


# Create your views here.

@login_required
@transaction.atomic
def vote(request, template_name='vote.html'):
    eb = ElectionBusiness()
    context = {}
    signer = Signer()
    if eb.isOccurring():
        # Check if elector already voted.
        if Voted.objects.filter(elector__user=request.user).count() > 0:
            messages.warning(request, 'You have already voted.')   
            return render(request, template_name, context)

        positions = Position.objects.all()
        if request.method == 'POST':
            try:
                for p in positions:
                    pname = 'position{}'.format(p.id)
                    candidate_id = request.POST.get(pname,"")
                    candidate = Candidate.objects.get(id=int(candidate_id))
                    cv, created = CandidateVote.objects.get_or_create(candidate=candidate)
                    cv.quantity = cv.quantity + 1
                    cv.save()
                elector = Elector.objects.get(user=request.user)
                voted = Voted.objects.create(elector=elector)
                voted.system_signature = signer.sign(str(elector.id))
                voted.save()
                messages.success(request, 'Your vote was registred successfully')
            except Exception as e:
                messages.error(request, str(e))
        else:
            context['positions'] = positions
            context['quantity_of_positions'] = positions.count()
    else:
        messages.error(request, 'Election has finished.')
    
    return render(request, template_name, context)


def election_results(request, template_name='election_results.html'):

    data = []
    positions = Position.objects.all()
    for p in positions:
        candidate_vote = CandidateVote.objects.filter(candidate__position=p).values('candidate__name', 'candidate__position__description', 'quantity' )
        candidate_vote_json_str = json.dumps(list(candidate_vote), cls=DjangoJSONEncoder)
        data.append(candidate_vote_json_str)
  
    return render(request, template_name, context={'results_data':json.dumps(data, cls=DjangoJSONEncoder), 'positions':positions})