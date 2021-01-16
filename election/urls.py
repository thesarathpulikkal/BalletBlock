from django.urls import path
from election import views

urlpatterns = [
    path('config_mock_election/', views.config_mock_election, name='config_mock_election'),
    path('electionconfig/',views.electionConfiguration, name='electionconfig'),
    path('start_election/',views.start_election, name='start_election'),
    path('clean_election/',views.clean_election, name='clean_election'),
    path('candidate/',views.candidate, name='candidate'),
    path('candidate/<int:id>/change', views.candidate_change, name='candidate_change'),
    path('candidate/<int:id>/delete', views.candidate_delete, name='candidate_delete'),
    path('candidate/add', views.candidate_add, name='candidate_add'),
    path('elector/',views.elector, name='elector'),
    path('elector/<int:id>/delete', views.elector_delete, name='elector_delete'),
    path('elector/<int:id>/change', views.elector_change, name='elector_change'),
    path('elector/add', views.elector_add, name='elector_add'),
    path('position/',views.position, name='position'),
    path('position/<int:id>/delete', views.position_delete, name='position_delete'),
    path('position/<int:id>/change', views.position_change, name='position_change'),
    path('position/add', views.position_add, name='position_add'),
    
]
