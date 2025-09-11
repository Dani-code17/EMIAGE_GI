from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('bibliotheque/', views.library, name='library'),
    path('bibliotheque/categorie/<str:category>/', views.library_category, name='library_category'),
]
