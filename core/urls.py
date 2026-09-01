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
    path('telecharger/<int:doc_id>/', views.telecharger_document, name='telecharger_document'),
    path('bibliotheque/', views.bibliotheque_index, name='bibliotheque_index'),
    path('meta-test/', views.meta_test, name='meta_test'),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('espace/', views.espace, name='espace'),
    path('espace/heartbeat/', views.heartbeat, name='heartbeat'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('quiz/', views.quiz_choose, name='quiz'),
    path('quiz/play/', views.quiz_play, name='quiz_play'),
    path('quiz/result/', views.quiz_result, name='quiz_result'),
    path('admin-espace/login/', views.admin_login, name='admin_login'),
    path('admin-espace/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-espace/deconnexion/', views.admin_logout, name='admin_logout'),
]
