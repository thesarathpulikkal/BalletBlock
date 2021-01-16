from django.shortcuts import render, redirect
from election.models import Elector, Candidate, ElectionConfig, Position
from vote.models import Voted, CandidateVote
from chain.models import BBlock
from chain.business import BBlockHandler
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from datetime import datetime
from election.business import ElectionBusiness
from django.contrib import messages
from election.forms import VoteForm,ElectionConfigForm, CandidateForm, PositionForm, ElectorForm
from election.signals import canModify
from election.middleware import ElectionMiddleware
from election.tables import CandidateTable, PositionTable, ElectorTable
from django_tables2.config import RequestConfig
from django.contrib.auth.hashers import make_password

@transaction.atomic
@staff_member_required
def config_mock_election(request, elector_quantity=501, template_name='mock_election.html'):

    if request.election_is_locked:
        messages.error(request, 'Election is locked')
        return render(request, template_name)

    # Delete tables of resutls
    Voted.objects.all().delete()
    CandidateVote.objects.all().delete()

    # Delete tables of election
    Elector.objects.all().delete()
    Candidate.objects.all().delete()
    Position.objects.all().delete()
    ElectionConfig.objects.all().delete()

    # Delete users which are not superuser
    User.objects.filter(is_superuser=False).delete()

    BBlock.objects.all().delete()

    # Create 1st position
    position = Position.objects.create(description="Best soccer player of all time")
    position.save()

    names = ['Pele', 'Messi', 'Cristiano Ronaldo', 'Zidane', 'Ronaldo', 'Romario']
    for name in names:
        c = Candidate.objects.create(position=position, name=name)
        c.save()

    # Create 2nd position
    position = Position.objects.create(description="Best city to live in Canada")
    position.save()

    names = ['Toronto', 'Vancouver', 'Windsor', 'Montreal', 'Quebec', 'Ottawa']
    for name in names:
        c = Candidate.objects.create(position=position, name=name)
        c.save()

     # Create 3rd position
    position = Position.objects.create(description="Best programming language")
    position.save()

    names = ['Python', 'Javascript', 'Java', 'C#', 'PHP', 'Prolog']
    for name in names:
        c = Candidate.objects.create(position=position, name=name)
        c.save()


    # Create "elector_quantity" of electors
    # username: userXXX
    # pass: BallotBlockXXX
    # where XXX is ther user number from 001 to elector_quantity

    i = 1
    s = len(str(elector_quantity))
    user_list = []
    while i < elector_quantity:
        username = ''.join(('user', str(i).zfill(s)))
        email = ''.join((username, '@ballotblock.com'))
        password = make_password(''.join(('BallotBlock', str(i).zfill(s) )), None, 'md5')
        user_list.append(User(username=username,
                                 email=email,
                                 password=password,
                                 first_name='user',
                                 last_name=str(i).zfill(s)))
        i = i + 1
    
    User.objects.bulk_create(user_list)
    users = User.objects.filter(is_superuser=False)

    elector_list = []
    for u in users:
        e = Elector(user=u)
        elector_list.append(e)
    Elector.objects.bulk_create(elector_list)

    messages.success(request, 'Mock election generated')
    return render(request, template_name)

# Only staff members can access the election configuration
@staff_member_required
def electionConfiguration(request, template_name='electionconfig.html'):

    ec = None
    # If exists at least one row in the table
    if ElectionConfig.objects.all().count() > 0:
        # Select all rows and get the first one.
        ec = ElectionConfig.objects.filter()[0]

    if request.election_is_locked:
        form = ElectionConfigForm(instance=ec, readonly=request.election_is_locked)
        return render(request, template_name, {'form':form})

    if request.POST:
        form = ElectionConfigForm(request.POST, instance=ec, readonly=request.election_is_locked)
        if form.is_valid():
            form.save()
            msg = 'Election configuration saved'
            messages.success(request, msg)
            return redirect('electionconfig')
        return render(request, template_name, {'form':form})
    else:
        form = ElectionConfigForm(instance=ec)

    return render(request, template_name, {'form':form})

@staff_member_required
def candidate(request, template_name='candidate/candidate_list.html'):
    candidate_table = CandidateTable(Candidate.objects.all())
    # Exclude delete column if election is locked
    if request.election_is_locked:
        candidate_table.exclude = ('delete')
    return render(request, template_name, {'candidate_table':candidate_table })

@staff_member_required
def candidate_delete(request, id):
    if request.election_is_locked:
        msg = 'Election is locked. Delete candidates is not allowed.'
        messages.error(request, msg)
        return redirect('candidate')

    try:
        Candidate.objects.get(id=int(id)).delete()
    except Exception as e:
        s = str(e)
        messages.error(request, e)

    return redirect('candidate')

@staff_member_required
def candidate_add(request, template_name='candidate/candidate_form.html'):
    if request.election_is_locked:
        msg = 'Election is locked. Candidate modifications are not allowed.'
        messages.warning(request, msg)
        return redirect('candidate')

    if request.POST:
        form = CandidateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('candidate')
        else:
            return render(request, template_name, {'form':form})
    else:
        form = CandidateForm()
    return render(request, template_name, {'form':form})

@staff_member_required
def candidate_change(request, id, template_name='candidate/candidate_form.html'):
    candidate = Candidate.objects.get(id=int(id))
    if request.POST:
        if request.election_is_locked:
            msg = 'Election is locked. Candidate modifications are not allowed.'
            messages.error(request, msg)
            return redirect('candidate')

        form = CandidateForm(request.POST, instance=candidate, readonly=request.election_is_locked)
        if form.is_valid():
            form.save()
            return redirect('candidate')
        else:
            return render(request, template_name, {'form':form})
    else:
        # If election is locked, the form will be readonly
        form = CandidateForm(instance=candidate, readonly=request.election_is_locked)
    return render(request, template_name, {'form':form})

@staff_member_required
def position(request, template_name='position/position_list.html'):
    position_table = PositionTable(Position.objects.all())
    # Exclude delete column if election is locked
    if request.election_is_locked:
        position_table.exclude = ('delete')
    return render(request, template_name, {'position_table':position_table })

@staff_member_required
def position_delete(request, id):
    if request.election_is_locked:
        msg = 'Election is locked. Delete position is not allowed.'
        messages.error(request, msg)
        return redirect('position')

    try:
        Position.objects.get(id=int(id)).delete()
    except Exception as e:
        s = str(e)
        messages.error(request, e)

    return redirect('position')

@staff_member_required
def position_add(request, template_name='position/position_form.html'):
    if request.election_is_locked:
        msg = 'Election is locked. Position modifications are not allowed.'
        messages.warning(request, msg)
        return redirect('position')

    if request.POST:
        form = PositionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('position')
        else:
            return render(request, template_name, {'form':form})
    else:
        form = PositionForm()
    return render(request, template_name, {'form':form})

@staff_member_required
def position_change(request, id, template_name='position/position_form.html'):
    position = Position.objects.get(id=int(id))
    if request.POST:
        if request.election_is_locked:
            msg = 'Election is locked. Position modifications are not allowed.'
            messages.error(request, msg)
            return redirect('position')

        form = PositionForm(request.POST, instance=position, readonly=request.election_is_locked)
        if form.is_valid():
            form.save()
            return redirect('position')
        else:
            return render(request, template_name, {'form':form})
    else:
        # If election is locked, the form will be readonly
        form = PositionForm(instance=position, readonly=request.election_is_locked)
    return render(request, template_name, {'form':form})




@staff_member_required
def elector(request, template_name='elector/elector_list.html'):
    elector_table = ElectorTable(Elector.objects.all())
    # Exclude delete column if election is locked
    if request.election_is_locked:
        elector_table.exclude = ('delete')
    return render(request, template_name, {'elector_table':elector_table })

@staff_member_required
def elector_delete(request, id):
    if request.election_is_locked:
        msg = 'Election is locked. Delete electors is not allowed.'
        messages.error(request, msg)
        return redirect('elector')

    try:
        Elector.objects.get(id=int(id)).delete()
    except Exception as e:
        s = str(e)
        messages.error(request, e)

    return redirect('elector')

@staff_member_required
def elector_add(request, template_name='elector/elector_form.html'):
    if request.election_is_locked:
        msg = 'Election is locked. Elector modifications are not allowed.'
        messages.warning(request, msg)
        return redirect('elector')

    if request.POST:
        form = ElectorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('elector')
        else:
            return render(request, template_name, {'form':form})
    else:
        form = ElectorForm()
    return render(request, template_name, {'form':form})

@staff_member_required
def elector_change(request, id, template_name='elector/elector_form.html'):
    elector = Elector.objects.get(id=int(id))
    if request.POST:
        if request.election_is_locked:
            msg = 'Election is locked. Elector modifications are not allowed.'
            messages.error(request, msg)
            return redirect('elector')

        form = ElectorForm(request.POST, instance=elector, readonly=request.election_is_locked)
        if form.is_valid():
            form.save()
            return redirect('elector')
        else:
            return render(request, template_name, {'form':form})
    else:
        # If election is locked, the form will be readonly
        form = ElectorForm(instance=elector, readonly=request.election_is_locked)
    return render(request, template_name, {'form':form})


@transaction.atomic
@staff_member_required
def start_election(request, template_name='election/start_election.html'):

    has_error = False

    # If election is locked, the tests will not be executed.
    if request.election_is_locked:
        msg = 'Election has already started'
        messages.warning(request, msg)
        return render(request, template_name)

    if ElectionConfig.objects.all().count() != 1:
        has_error = True
        msg = 'Election Configuration is not configured properly.'
        messages.error(request, msg)

    ec = ElectionBusiness().getCurrentElectionConfig()
    if ec:
        if ec.start_time >= ec.end_time:
            has_error = True
            msg = 'Election Configuration start time is greater than end time.'
            messages.error(request, msg)

        if ec.end_time < datetime.now():
            has_error = True
            msg = 'End time of Election Configuration is a past date'
            messages.error(request, msg)

    if Position.objects.all().count() == 0:
        has_error = True
        msg = 'There are not poisitions configurated for the election'
        messages.error(request, msg)

    for position in Position.objects.all():
        if position.candidate_set.count() == 0:
            has_error = True
            msg = 'Position "{}" does not have candidates'.format(position.description)
            messages.error(request, msg)

    #Check positions without candidates
    #Check electors
    if Elector.objects.all().count() == 0:
        messages.error(request, 'There are not electors configurated for the election')
        has_error = True

    # Delete votes, results, blocks, etc...
    if not has_error:
        Voted.objects.all().delete()
        CandidateVote.objects.all().delete()
        for candidate in Candidate.objects.all():
            cv = CandidateVote.objects.create(candidate=candidate, quantity=0)
            cv.save()
        BBlock.objects.all().delete()

        ec = ElectionConfig.objects.all()[0]
        ec.locked = True
        ec.save()
        
        # Add genesis block
        BBlockHandler().add_genesis()
            
    return redirect('home')

@transaction.atomic
@staff_member_required
def clean_election(request, template_name='election/clean_election.html'):
    if request.election_is_locked:
        messages.error(request, 'Election is locked')
        return render(request, template_name)

    # Delete tables of resutls
    Voted.objects.all().delete()
    CandidateVote.objects.all().delete()

    # Delete tables of election
    Elector.objects.all().delete()
    Candidate.objects.all().delete()
    Position.objects.all().delete()
    ElectionConfig.objects.all().delete()

    # Delete users which are not superuser
    User.objects.filter(is_superuser=False).delete()

    BBlock.objects.all().delete()

    messages.success(request, 'Election is clean')
    return render(request, template_name)
