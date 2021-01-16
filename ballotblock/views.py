from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from django.db.models import Count, F
from django.utils import timezone
from django.http import JsonResponse
from django.forms import formset_factory, inlineformset_factory
import datetime
from django.db import transaction
from django_tables2 import RequestConfig
from election.business import ElectionBusiness
from django.contrib import messages

@login_required
def home(request):
	if request.user.is_superuser:
		#eb = ElectionBusiness()
		#election_is_occurring = eb.isOccurring()
		#context = {'election_is_occurring':election_is_occurring}
		#return render(request, 'home.html', context)
		return render(request, 'home.html')
	else:
		# return redirect('vote')
		return render(request, 'home.html')
		#return render(request, 'vote.html', context)

@login_required
def about_us(request):
	return render(request, 'about_us.html')

@login_required
def help(request):
	return render(request, 'help.html')
