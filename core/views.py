from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Document

def home(request):
    # Récupérer quelques statistiques pour la page d'accueil
    total_documents = Document.objects.count()
    latest_documents = Document.objects.order_by('-upload_date')[:5]
    
    context = {
        'total_documents': total_documents,
        'latest_documents': latest_documents,
    }
    return render(request, 'core/home.html', context)

def library(request):
    # Récupérer les paramètres de filtrage
    level = request.GET.get('level')
    semester = request.GET.get('semester')
    category = request.GET.get('category')
    
    # Commencer avec tous les documents
    documents = Document.objects.all()
    
    # Appliquer les filtres
    if level:
        documents = documents.filter(level=level)
    if semester:
        documents = documents.filter(semester=semester)
    if category:
        documents = documents.filter(category=category)
    
    context = {
        'documents': documents,
        'levels': Document.LEVEL_CHOICES,
        'semesters': Document.SEMESTER_CHOICES,
        'categories': Document.CATEGORY_CHOICES,
        'selected_level': level,
        'selected_semester': semester,
        'selected_category': category,
    }
    
    # Si la requête est AJAX, renvoyer seulement les résultats filtrés
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'core/includes/document_list.html', context)
    
    return render(request, 'core/library.html', context)

def library_category(request, category):
    documents = Document.objects.filter(category=category.upper())
    context = {
        'documents': documents,
        'category': dict(Document.CATEGORY_CHOICES)[category.upper()],
    }
    return render(request, 'core/library_category.html', context)
