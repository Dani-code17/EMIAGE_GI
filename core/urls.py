from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('bibliotheque/l1/', views.niveau_l1, name='niveau_l1'),
    path('bibliotheque/l2/', views.niveau_l2, name='niveau_l2'),
    path('bibliotheque/l3/', views.niveau_l3, name='niveau_l3'),
    path('bibliotheque/m1/', views.niveau_m1, name='niveau_m1'),
    path('bibliotheque/m2/', views.niveau_m2, name='niveau_m2'),
    path('coming-soon/', views.coming_soon, name='coming_soon'),
    path('about/', views.about, name='about'),
    path('bibliotheque/', views.bibliotheque_index, name='bibliotheque_index'),
    path('meta-test/', views.meta_test, name='meta_test'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
