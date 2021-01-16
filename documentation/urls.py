from django.urls import path, include
from documentation import views

urlpatterns = [
    path('index', views.doc_index, name='doc_index'),
]