from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse
from .models import Document
from django.db.models import Q
import re

def home(request):
    total_documents = Document.objects.count()
    latest_documents = Document.objects.order_by('-upload_date')[:5]
    
    context = {
        'total_documents': total_documents,
        'latest_documents': latest_documents,
    }
    return render(request, 'core/home.html', context)

def get_semester_mapping(niveau, affiche_semestre):
    """
    Convertit le semestre affiché (1 ou 2) en semestre réel selon le niveau
    """
    mapping = {
        'L1': {'s1': 'S1', 's2': 'S2'},
        'L2': {'s1': 'S3', 's2': 'S4'},
        'L3': {'s1': 'S5', 's2': 'S6'},
        'M1': {'s1': 'S7', 's2': 'S8'},
        'M2': {'s1': 'S9', 's2': 'S10'},
    }
    return mapping[niveau][affiche_semestre]

def niveau_l1(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    # Build base queryset for this level + semester
    real_semestre = get_semester_mapping('L1', semestre)
    documents = Document.objects.filter(level='L1', semester=real_semestre)

    # Narrow by category if provided
    if category:
        documents = documents.filter(category=category.upper())

    # If a search query is present, tokenize and apply OR across tokens
    if query:
        # Split on whitespace, ignore empty tokens
        tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
        if tokens:
            q_obj = Q()
            for token in tokens:
                q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
            documents = documents.filter(q_obj)

    # Only expose documents in context when there's either a category selected or a search query
    if category or query:
        context['documents'] = documents
    
    return render(request, 'core/niveau/l1.html', context)

def niveau_l2(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    real_semestre = get_semester_mapping('L2', semestre)
    documents = Document.objects.filter(level='L2', semester=real_semestre)
    if category:
        documents = documents.filter(category=category.upper())
    if query:
        tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
        if tokens:
            q_obj = Q()
            for token in tokens:
                q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
            documents = documents.filter(q_obj)
    if category or query:
        context['documents'] = documents
    
    return render(request, 'core/niveau/l2.html', context)

def niveau_l3(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    real_semestre = get_semester_mapping('L3', semestre)
    documents = Document.objects.filter(level='L3', semester=real_semestre)
    if category:
        documents = documents.filter(category=category.upper())
    if query:
        tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
        if tokens:
            q_obj = Q()
            for token in tokens:
                q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
            documents = documents.filter(q_obj)
    if category or query:
        context['documents'] = documents
    
    return render(request, 'core/niveau/l3.html', context)

def niveau_m1(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    real_semestre = get_semester_mapping('M1', semestre)
    documents = Document.objects.filter(level='M1', semester=real_semestre)
    if category:
        documents = documents.filter(category=category.upper())
    if query:
        tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
        if tokens:
            q_obj = Q()
            for token in tokens:
                q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
            documents = documents.filter(q_obj)
    if category or query:
        context['documents'] = documents
    
    return render(request, 'core/niveau/m1.html', context)

def niveau_m2(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    real_semestre = get_semester_mapping('M2', semestre)
    documents = Document.objects.filter(level='M2', semester=real_semestre)
    if category:
        documents = documents.filter(category=category.upper())
    if query:
        tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
        if tokens:
            q_obj = Q()
            for token in tokens:
                q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
            documents = documents.filter(q_obj)
    if category or query:
        context['documents'] = documents
    
    return render(request, 'core/niveau/m2.html', context)

def coming_soon(request):
    """Simple page indicating the feature is in development."""
    return render(request, 'core/coming_soon.html')


def about(request):
    """Render the 'Qui sommes nous ?' page."""
    return render(request, 'core/about.html')


def bibliotheque_index(request):
    """Simple index page for the médiathèques listing all niveaux."""
    return render(request, 'core/bibliotheque_index.html')


def meta_test(request):
    """Return a minimal HTML page containing the google-site-verification meta tag for deployment verification."""
    html = '''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="google-site-verification" content="TS4KVTjig14AFA58XmJOZuasZ-HgvjrIqso9pt1cEeo" /><title>Meta Test</title></head><body>Meta test page</body></html>'''
    return HttpResponse(html)
