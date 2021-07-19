from django.urls import path

from . import views

app_name = 'app'
urlpatterns = [
    path('', views.index, name='index'),
    path('results/', views.results, name = 'results'),
    path('results', views.results, name = 'results'),
]