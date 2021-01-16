from django.urls import path
from vote import views

urlpatterns = [
    path('vote', views.vote, name='vote'),
    path('election_results', views.election_results, name='election_results'),
]

