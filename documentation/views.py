from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Create your views here.

@login_required
def doc_index(request):
	return render(request, 'doc_index.html')