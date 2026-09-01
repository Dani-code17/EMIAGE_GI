from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse, StreamingHttpResponse
from django.urls import reverse
from .models import Document, UE, ECUE, Student, StudentStat, Prize, QuizQuestion, QuizAnswer, QuizAttempt
from django.db.models import Q
from collections import Counter
import os
import re
import urllib.request


def _niveau_extra_context(niveau_label, level, documents):
    """Contexte UI supplémentaire pour les pages niveau :
    libellé du niveau + compteurs de documents par catégorie pour la
    sélection courante (le bouton « Maquettes » compte niveau entier)."""
    counts = Counter(documents.values_list('category', flat=True))
    counts['MAQUETTES'] = Document.objects.filter(level=level, category='MAQUETTES').count()
    return {
        'niveau_label': niveau_label,
        'niveau_url': reverse(f'core:niveau_{level.lower()}'),
        'category_counts': {c.lower(): n for c, n in counts.items()},
        'selection_count': documents.count(),
    }

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
    ue_slug = request.GET.get('ue')
    ecue_slug = request.GET.get('ecue')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    # Build base queryset for this level + semester
    real_semestre = get_semester_mapping('L1', semestre)
    documents = Document.objects.filter(level='L1', semester=real_semestre)

    # Charger les UE du semestre
    ues = UE.objects.filter(level='L1', semester=real_semestre).order_by('code', 'name')
    context['ues'] = ues

    selected_ue = None
    selected_ecue = None
    ecues = None

    # Filtrage par UE/ECUE via slugs
    if ue_slug:
        try:
            selected_ue = UE.objects.get(slug=ue_slug, level='L1', semester=real_semestre)
            context['selected_ue'] = selected_ue
            ecues = selected_ue.ecues.all().order_by('name')
            context['ecues'] = ecues
            
            # Si l'UE n'a qu'une seule ECUE, la sélectionner automatiquement
            if ecues.count() == 1:
                selected_ecue = ecues.first()
                context['selected_ecue'] = selected_ecue
                documents = documents.filter(ecue=selected_ecue)
        except UE.DoesNotExist:
            selected_ue = None

    if ecue_slug:
        try:
            selected_ecue = ECUE.objects.select_related('ue').get(slug=ecue_slug, ue__level='L1', ue__semester=real_semestre)
            context['selected_ecue'] = selected_ecue
            # Restreindre les documents à cette ECUE
            documents = documents.filter(ecue=selected_ecue)
        except ECUE.DoesNotExist:
            selected_ecue = None

    # Contexte UI : libellé du niveau + compteurs de documents par catégorie
    context.update(_niveau_extra_context('Licence 1', 'L1', documents))

    # Cas spécial: afficher toutes les maquettes du niveau (L1) quel que soit le semestre/UE/ECUE
    if category == 'maquettes':
        documents = Document.objects.filter(level='L1', category='MAQUETTES')
        # Appliquer la recherche éventuelle
        if query:
            tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
            if tokens:
                q_obj = Q()
                for token in tokens:
                    q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
                documents = documents.filter(q_obj)
        context['documents'] = documents
    else:
        # Narrow by category if provided (autres catégories)
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

        # Afficher les documents si :
        # 1. Une ECUE est choisie ET qu'une catégorie est fournie
        # 2. OU si une UE avec une seule ECUE est sélectionnée ET qu'une catégorie est fournie
        if (selected_ecue and category) or (selected_ue and ecues and ecues.count() == 1 and category):
            context['documents'] = documents
    
    return render(request, 'core/niveau/l1.html', context)

def niveau_l2(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    ue_slug = request.GET.get('ue')
    ecue_slug = request.GET.get('ecue')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    real_semestre = get_semester_mapping('L2', semestre)
    documents = Document.objects.filter(level='L2', semester=real_semestre)

    # Charger les UE du semestre
    ues = UE.objects.filter(level='L2', semester=real_semestre).order_by('code', 'name')
    context['ues'] = ues

    selected_ue = None
    selected_ecue = None
    ecues = None

    # Filtrage par UE/ECUE via slugs
    if ue_slug:
        try:
            selected_ue = UE.objects.get(slug=ue_slug, level='L2', semester=real_semestre)
            context['selected_ue'] = selected_ue
            ecues = selected_ue.ecues.all().order_by('name')
            context['ecues'] = ecues
            
            # Si l'UE n'a qu'une seule ECUE, la sélectionner automatiquement
            if ecues.count() == 1:
                selected_ecue = ecues.first()
                context['selected_ecue'] = selected_ecue
                documents = documents.filter(ecue=selected_ecue)
        except UE.DoesNotExist:
            selected_ue = None

    if ecue_slug:
        try:
            selected_ecue = ECUE.objects.select_related('ue').get(slug=ecue_slug, ue__level='L2', ue__semester=real_semestre)
            context['selected_ecue'] = selected_ecue
            # Restreindre les documents à cette ECUE
            documents = documents.filter(ecue=selected_ecue)
        except ECUE.DoesNotExist:
            selected_ecue = None

    # Contexte UI : libellé du niveau + compteurs de documents par catégorie
    context.update(_niveau_extra_context('Licence 2', 'L2', documents))

    # Cas spécial: afficher toutes les maquettes du niveau (L2) quel que soit le semestre/UE/ECUE
    if category == 'maquettes':
        documents = Document.objects.filter(level='L2', category='MAQUETTES')
        if query:
            tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
            if tokens:
                q_obj = Q()
                for token in tokens:
                    q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
                documents = documents.filter(q_obj)
        context['documents'] = documents
    else:
        if category:
            documents = documents.filter(category=category.upper())
        if query:
            tokens = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
            if tokens:
                q_obj = Q()
                for token in tokens:
                    q_obj |= Q(title__icontains=token) | Q(description__icontains=token)
                documents = documents.filter(q_obj)
        
        # Afficher les documents si :
        # 1. Une ECUE est choisie ET qu'une catégorie est fournie
        # 2. OU si une UE avec une seule ECUE est sélectionnée ET qu'une catégorie est fournie
        if (selected_ecue and category) or (selected_ue and ecues and ecues.count() == 1 and category):
            context['documents'] = documents
    
    return render(request, 'core/niveau/l2.html', context)

def niveau_l3(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    ue_slug = request.GET.get('ue')
    ecue_slug = request.GET.get('ecue')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    # Build base queryset for this level + semester
    real_semestre = get_semester_mapping('L3', semestre)
    documents = Document.objects.filter(level='L3', semester=real_semestre)

    # Charger les UE du semestre
    ues = UE.objects.filter(level='L3', semester=real_semestre).order_by('code', 'name')
    context['ues'] = ues

    selected_ue = None
    selected_ecue = None
    ecues = None

    # Filtrage par UE/ECUE via slugs
    if ue_slug:
        try:
            selected_ue = UE.objects.get(slug=ue_slug, level='L3', semester=real_semestre)
            context['selected_ue'] = selected_ue
            ecues = selected_ue.ecues.all().order_by('name')
            context['ecues'] = ecues
            
            # Si l'UE n'a qu'une seule ECUE, la sélectionner automatiquement
            if ecues.count() == 1:
                selected_ecue = ecues.first()
                context['selected_ecue'] = selected_ecue
                documents = documents.filter(ecue=selected_ecue)
        except UE.DoesNotExist:
            selected_ue = None

    if ecue_slug:
        try:
            selected_ecue = ECUE.objects.select_related('ue').get(slug=ecue_slug, ue__level='L3', ue__semester=real_semestre)
            context['selected_ecue'] = selected_ecue
            # Restreindre les documents à cette ECUE
            documents = documents.filter(ecue=selected_ecue)
        except ECUE.DoesNotExist:
            selected_ecue = None

    # Contexte UI : libellé du niveau + compteurs de documents par catégorie
    context.update(_niveau_extra_context('Licence 3', 'L3', documents))

    # Narrow by category if provided
    # Cas spécial: afficher toutes les maquettes du niveau quel que soit le
    # semestre/UE/ECUE (comportement identique à L1/L2)
    if category == 'maquettes':
        documents = Document.objects.filter(level='L3', category='MAQUETTES')
        context['documents'] = documents
    else:
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

        # Afficher les documents si :
        # 1. Une ECUE est choisie ET qu'une catégorie est fournie
        # 2. OU si une UE avec une seule ECUE est sélectionnée ET qu'une catégorie est fournie
        if (selected_ecue and category) or (selected_ue and ecues and ecues.count() == 1 and category):
            context['documents'] = documents
    
    return render(request, 'core/niveau/l3.html', context)

def niveau_m1(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    ue_slug = request.GET.get('ue')
    ecue_slug = request.GET.get('ecue')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    # Build base queryset for this level + semester
    real_semestre = get_semester_mapping('M1', semestre)
    documents = Document.objects.filter(level='M1', semester=real_semestre)

    # Charger les UE du semestre
    ues = UE.objects.filter(level='M1', semester=real_semestre).order_by('code', 'name')
    context['ues'] = ues

    selected_ue = None
    selected_ecue = None
    ecues = None

    # Filtrage par UE/ECUE via slugs
    if ue_slug:
        try:
            selected_ue = UE.objects.get(slug=ue_slug, level='M1', semester=real_semestre)
            context['selected_ue'] = selected_ue
            ecues = selected_ue.ecues.all().order_by('name')
            context['ecues'] = ecues
            
            # Si l'UE n'a qu'une seule ECUE, la sélectionner automatiquement
            if ecues.count() == 1:
                selected_ecue = ecues.first()
                context['selected_ecue'] = selected_ecue
                documents = documents.filter(ecue=selected_ecue)
        except UE.DoesNotExist:
            selected_ue = None

    if ecue_slug:
        try:
            selected_ecue = ECUE.objects.select_related('ue').get(slug=ecue_slug, ue__level='M1', ue__semester=real_semestre)
            context['selected_ecue'] = selected_ecue
            # Restreindre les documents à cette ECUE
            documents = documents.filter(ecue=selected_ecue)
        except ECUE.DoesNotExist:
            selected_ecue = None

    # Contexte UI : libellé du niveau + compteurs de documents par catégorie
    context.update(_niveau_extra_context('Master 1', 'M1', documents))

    # Narrow by category if provided
    # Cas spécial: afficher toutes les maquettes du niveau quel que soit le
    # semestre/UE/ECUE (comportement identique à L1/L2)
    if category == 'maquettes':
        documents = Document.objects.filter(level='M1', category='MAQUETTES')
        context['documents'] = documents
    else:
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

        # Afficher les documents si :
        # 1. Une ECUE est choisie ET qu'une catégorie est fournie
        # 2. OU si une UE avec une seule ECUE est sélectionnée ET qu'une catégorie est fournie
        if (selected_ecue and category) or (selected_ue and ecues and ecues.count() == 1 and category):
            context['documents'] = documents
    
    return render(request, 'core/niveau/m1.html', context)

def niveau_m2(request):
    semestre = request.GET.get('semestre', 's1')
    category = request.GET.get('category')
    query = request.GET.get('q')
    ue_slug = request.GET.get('ue')
    ecue_slug = request.GET.get('ecue')
    
    context = {
        'semestre': semestre,
        'category': category
    }
    # Build base queryset for this level + semester
    real_semestre = get_semester_mapping('M2', semestre)
    documents = Document.objects.filter(level='M2', semester=real_semestre)

    # Charger les UE du semestre
    ues = UE.objects.filter(level='M2', semester=real_semestre).order_by('code', 'name')
    context['ues'] = ues

    selected_ue = None
    selected_ecue = None
    ecues = None

    # Filtrage par UE/ECUE via slugs
    if ue_slug:
        try:
            selected_ue = UE.objects.get(slug=ue_slug, level='M2', semester=real_semestre)
            context['selected_ue'] = selected_ue
            ecues = selected_ue.ecues.all().order_by('name')
            context['ecues'] = ecues
            
            # Si l'UE n'a qu'une seule ECUE, la sélectionner automatiquement
            if ecues.count() == 1:
                selected_ecue = ecues.first()
                context['selected_ecue'] = selected_ecue
                documents = documents.filter(ecue=selected_ecue)
        except UE.DoesNotExist:
            selected_ue = None

    if ecue_slug:
        try:
            selected_ecue = ECUE.objects.select_related('ue').get(slug=ecue_slug, ue__level='M2', ue__semester=real_semestre)
            context['selected_ecue'] = selected_ecue
            # Restreindre les documents à cette ECUE
            documents = documents.filter(ecue=selected_ecue)
        except ECUE.DoesNotExist:
            selected_ecue = None

    # Contexte UI : libellé du niveau + compteurs de documents par catégorie
    context.update(_niveau_extra_context('Master 2', 'M2', documents))

    # Narrow by category if provided
    # Cas spécial: afficher toutes les maquettes du niveau quel que soit le
    # semestre/UE/ECUE (comportement identique à L1/L2)
    if category == 'maquettes':
        documents = Document.objects.filter(level='M2', category='MAQUETTES')
        context['documents'] = documents
    else:
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

        # Afficher les documents si :
        # 1. Une ECUE est choisie ET qu'une catégorie est fournie
        # 2. OU si une UE avec une seule ECUE est sélectionnée ET qu'une catégorie est fournie
        if (selected_ecue and category) or (selected_ue and ecues and ecues.count() == 1 and category):
            context['documents'] = documents
    
    return render(request, 'core/niveau/m2.html', context)

def coming_soon(request):
    """Simple page indicating the feature is in development."""
    return render(request, 'core/coming_soon.html')


def about(request):
    """Render the 'Qui sommes nous ?' page."""
    return render(request, 'core/about.html')


def bibliotheque_index(request):
    """Index de la médiathèque : liste des niveaux avec leur nombre de documents."""
    from django.urls import reverse
    levels = [
        ('L1', 'Licence 1', 'fa-graduation-cap'),
        ('L2', 'Licence 2', 'fa-graduation-cap'),
        ('L3', 'Licence 3', 'fa-graduation-cap'),
        ('M1', 'Master 1', 'fa-user-graduate'),
        ('M2', 'Master 2', 'fa-user-graduate'),
    ]
    context = {
        'levels': [
            {
                'code': code,
                'label': label,
                'icon': icon,
                'count': Document.objects.filter(level=code).count(),
                'url': reverse(f'core:niveau_{code.lower()}'),
            }
            for code, label, icon in levels
        ],
        'total_documents': Document.objects.count(),
    }
    return render(request, 'core/bibliotheque_index.html', context)


def meta_test(request):
    """Return a minimal HTML page containing the google-site-verification meta tag for deployment verification."""
    html = '''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="google-site-verification" content="TS4KVTjig14AFA58XmJOZuasZ-HgvjrIqso9pt1cEeo" /><title>Meta Test</title></head><body>Meta test page</body></html>'''
    return HttpResponse(html)


# ============================================================
# Espace étudiants (inscription / connexion / espace)
# ============================================================

def _current_student(request):
    """Renvoie l'étudiant connecté (session) ou None.

    La session est gérée côté serveur et signée par Django : son contenu ne peut
    pas être falsifié par le client. On purge un identifiant résiduel qui ne
    correspond plus à un compte existant.
    """
    student_id = request.session.get('student_id')
    if not student_id:
        return None
    student = Student.objects.filter(id=student_id).first()
    if student is None:
        # Compte supprimé ou identifiant orphelin : on nettoie la session
        try:
            del request.session['student_id']
        except KeyError:
            pass
        return None
    return student


def inscription(request):
    """Création de compte : nom, prénom, niveau, identifiant et mot de passe."""
    if _current_student(request):
        return redirect('core:espace')

    error = None
    if request.method == 'POST':
        first_name = request.POST.get('prenom', '').strip()
        last_name = request.POST.get('nom', '').strip()
        level = request.POST.get('niveau', '')
        student_id = request.POST.get('identifiant', '').strip()
        password = request.POST.get('mdp', '')
        password2 = request.POST.get('mdp2', '')
        valid_levels = dict(Student.LEVEL_CHOICES)

        if not first_name or not last_name:
            error = 'Merci de renseigner ton nom et ton prénom.'
        elif level not in valid_levels:
            error = 'Merci de choisir un niveau valide.'
        elif len(student_id) < 3:
            error = 'Choisis un identifiant permanent (IP) d\'au moins 3 caractères.'
        elif Student.objects.filter(student_id__iexact=student_id).exists():
            error = 'Cet identifiant est déjà utilisé. Choisis-en un autre.'
        elif len(password) < 6:
            error = 'Le mot de passe doit contenir au moins 6 caractères.'
        elif password != password2:
            error = 'Les deux mots de passe ne correspondent pas.'
        else:
            student = Student(first_name=first_name, last_name=last_name, level=level, student_id=student_id)
            student.set_password(password)
            student.save()
            request.session['student_id'] = student.id
            return redirect('core:espace')

    return render(request, 'core/inscription.html', {
        'error': error,
        'levels': dict(Student.LEVEL_CHOICES),
    })


def connexion(request):
    """Connexion : identifiant (ou nom + prénom) + mot de passe."""
    if _current_student(request):
        return redirect('core:espace')

    error = None
    if request.method == 'POST':
        identifier = request.POST.get('identifiant', '').strip()
        password = request.POST.get('mdp', '')

        # L'identifiant peut être l'IP OU « prénom nom »
        parts = identifier.split()
        student = Student.objects.filter(student_id__iexact=identifier).first()
        if not student and len(parts) >= 2:
            student = Student.objects.filter(
                first_name__iexact=parts[0],
                last_name__iexact=' '.join(parts[1:]),
            ).first()

        if student and student.check_password(password):
            request.session['student_id'] = student.id
            return redirect('core:espace')
        error = 'Identifiant ou mot de passe incorrect.'

    return render(request, 'core/connexion.html', {
        'error': error,
    })


def _ranking(month):
    """Classement du mois : score = visites × 10 + minutes × 2."""
    stats = list(StudentStat.objects.filter(month=month).select_related('student'))
    stats.sort(key=lambda s: s.score, reverse=True)
    return stats


def espace(request):
    """Espace étudiant : bienvenue, classement mensuel, accès rapide à son niveau."""
    student = _current_student(request)
    if not student:
        return redirect('core:connexion')

    from django.utils import timezone
    month = timezone.now().strftime('%Y-%m')

    level_counts = Counter(
        Document.objects.filter(level=student.level).values_list('category', flat=True)
    )
    ues = UE.objects.filter(level=student.level).exclude(code='UE MAQUETTES').order_by('semester', 'code')

    # Stats perso du mois
    my_stat = StudentStat.objects.filter(student=student, month=month).first()
    # Classement du mois
    ranking = _ranking(month)
    my_rank = None
    for i, stat in enumerate(ranking, start=1):
        if stat.student_id == student.id:
            my_rank = i
            break
    # Prix du mois
    prizes = Prize.objects.filter(month=month).select_related('student').order_by('-id')

    # Historique des quiz (progression)
    attempts = student.quiz_attempts.select_related('ue')[:10]
    attempts_count = student.quiz_attempts.count()
    best = student.quiz_attempts.order_by('-note').first()
    avg = None
    if attempts_count:
        from django.db.models import Avg
        avg = student.quiz_attempts.aggregate(a=Avg('note'))['a']

    return render(request, 'core/espace.html', {
        'student': student,
        'my_stat': my_stat,
        'my_rank': my_rank,
        'ranking': ranking[:10],
        'prizes': prizes,
        'month': month,
        'attempts': attempts,
        'attempts_count': attempts_count,
        'best': best,
        'avg': avg,
        'level_counts': {c.lower(): n for c, n in level_counts.items()},
        'ues': ues,
        'niveau_url': reverse(f'core:niveau_{student.level.lower()}'),
    })


def heartbeat(request):
    """Point de contrôle activité : met à jour activity_last via le middleware."""
    return HttpResponse(status=204)


def deconnexion(request):
    """Déconnexion : vide la session."""
    request.session.flush()
    return redirect('core:home')


# ============================================================
# Quiz (exercices)
# ============================================================

def quiz_choose(request):
    """Choix : UE (de SON niveau) → ECUE → difficulté → nombre de questions."""
    student = _current_student(request)
    if not student:
        return redirect('core:connexion')

    error = None
    # L'étudiant ne peut faire que les quiz de SON niveau
    ues = UE.objects.filter(level=student.level).exclude(code='UE MAQUETTES').order_by('semester', 'code')
    if request.method == 'POST':
        ue_id = request.POST.get('ue')
        ecue_id = request.POST.get('ecue', '')
        difficulty = request.POST.get('difficulte', '')
        number = int(request.POST.get('nombre', 5) or 5)
        ue = UE.objects.filter(id=ue_id, level=student.level).first()
        if not ue:
            error = 'Merci de choisir une UE de ton niveau.'
        else:
            qs = QuizQuestion.objects.filter(ue=ue)
            if ecue_id:
                qs = qs.filter(ecue_id=ecue_id)
            if difficulty in ('facile', 'normal', 'difficile'):
                qs = qs.filter(difficulty=difficulty)
            qs = list(qs.order_by('?')[:number])
            if not qs:
                error = 'Aucune question disponible pour cette sélection pour le moment. Reviens plus tard !'
            else:
                request.session['quiz_questions'] = [q.id for q in qs]
                request.session['quiz_ue'] = ue.name
                request.session['quiz_difficulty'] = difficulty
                return redirect('core:quiz_play')

    return render(request, 'core/quiz_choose.html', {
        'student': student,
        'ues': ues,
        'ecues': ECUE.objects.filter(ue__level=student.level).select_related('ue').order_by('ue__code', 'name'),
        'error': error,
    })


def quiz_play(request):
    """Affiche le quiz généré."""
    student = _current_student(request)
    if not student:
        return redirect('core:connexion')

    qids = request.session.get('quiz_questions')
    if not qids:
        return redirect('core:quiz')
    questions = QuizQuestion.objects.filter(id__in=qids).prefetch_related('answers')
    # préserve l'ordre choisi
    by_id = {q.id: q for q in questions}
    ordered = [by_id[i] for i in qids if i in by_id]

    return render(request, 'core/quiz_play.html', {
        'student': student,
        'questions': ordered,
        'ue_name': request.session.get('quiz_ue', ''),
        'total': len(ordered),
    })


def quiz_result(request):
    """Corrige le quiz : note sur 20 + correction expliquée."""
    student = _current_student(request)
    if not student:
        return redirect('core:connexion')

    qids = request.session.get('quiz_questions')
    if not qids:
        return redirect('core:quiz')

    questions = QuizQuestion.objects.filter(id__in=qids).prefetch_related('answers')
    by_id = {q.id: q for q in questions}
    ordered = [by_id[i] for i in qids if i in by_id]

    correct = 0
    corrections = []
    for q in ordered:
        chosen_id = int(request.POST.get(f'q{q.id}', 0) or 0)
        good = q.answers.filter(is_correct=True).first()
        chosen = q.answers.filter(id=chosen_id).first()
        is_ok = bool(chosen and chosen.is_correct)
        if is_ok:
            correct += 1
        corrections.append({
            'question': q,
            'chosen': chosen.text if chosen else '—',
            'good': good.text if good else '—',
            'is_ok': is_ok,
        })

    total = len(ordered)
    note = round((correct / total) * 20, 1) if total else 0

    # Enregistre la tentative (historique de progression)
    ue = UE.objects.filter(name=request.session.get('quiz_ue', '')).first()
    QuizAttempt.objects.create(
        student=student,
        ue=ue,
        difficulty=request.session.get('quiz_difficulty', ''),
        correct=correct,
        total=total,
        note=note,
    )

    return render(request, 'core/quiz_result.html', {
        'student': student,
        'corrections': corrections,
        'correct': correct,
        'total': total,
        'note': note,
        'ue_name': request.session.get('quiz_ue', ''),
    })


# ============================================================
# Espace admin personnalisé (Daniki)
# ============================================================

def _is_admin(request):
    return request.session.get('admin_logged') is True


def admin_login(request):
    """Connexion admin : identifiant + mot de passe (settings)."""
    from django.conf import settings
    if _is_admin(request):
        return redirect('core:admin_dashboard')

    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if (username == settings.ADMIN_LOGIN and password == settings.ADMIN_PASSWORD):
            request.session['admin_logged'] = True
            return redirect('core:admin_dashboard')
        error = 'Identifiant ou mot de passe admin incorrect.'

    return render(request, 'core/admin_login.html', {'error': error})


def admin_dashboard(request):
    """Tableau de bord admin : stats, classement, prix, questions."""
    from django.utils import timezone
    if not _is_admin(request):
        return redirect('core:admin_login')

    month = timezone.now().strftime('%Y-%m')

    if request.method == 'POST' and request.POST.get('action') == 'prize':
        student_id = request.POST.get('student_id')
        label = request.POST.get('label', '').strip()
        amount = request.POST.get('amount', '').strip()
        student = Student.objects.filter(id=student_id).first()
        if student and label:
            Prize.objects.create(student=student, month=month, label=label, amount=amount)

    ranking = _ranking(month)
    total_students = Student.objects.count()
    month_stats = StudentStat.objects.filter(month=month)
    total_visits = sum(s.visits for s in month_stats)
    total_minutes = sum(s.minutes for s in month_stats)
    prizes = Prize.objects.filter(month=month).select_related('student').order_by('-id')
    recent_students = Student.objects.order_by('-created_at')[:10]

    return render(request, 'core/admin_dashboard.html', {
        'month': month,
        'ranking': ranking,
        'total_students': total_students,
        'total_visits': total_visits,
        'total_minutes': total_minutes,
        'prizes': prizes,
        'recent_students': recent_students,
    })


def admin_logout(request):
    request.session['admin_logged'] = False
    return redirect('core:admin_login')


def sitemap_xml(request):
    """Serve the repository sitemap.xml file from project root so /sitemap.xml works in production.

    This keeps deployment resilient when the hosting static root isn't configured to serve the repo root file.
    """
    from django.conf import settings
    import os
    # Use BASE_DIR defined in settings for a robust path to project root
    sitemap_path = os.path.join(settings.BASE_DIR, 'sitemap.xml')
    try:
        with open(sitemap_path, 'rb') as f:
            data = f.read()
        return HttpResponse(data, content_type='application/xml')
    except Exception:
        # Return 404 if the file can't be read for any reason
        return HttpResponse(status=404)


def telecharger_document(request, doc_id):
    """Force le téléchargement d'un document avec Content-Disposition: attachment.

    Utile pour iPhone/Safari qui, sinon, affiche les PDF en aperçu dans le
    navigateur au lieu de les télécharger. Le fichier est streamé depuis sa
    source (GitHub emiage-media, R2, ou le disque local en dev).
    """
    from django.conf import settings
    doc = get_object_or_404(Document, id=doc_id)

    # Titre de fichier propre pour le téléchargement
    ext = doc.extension.lower() or 'bin'
    filename = f'{doc.title}.{ext}'
    ascii_name = filename.encode('ascii', 'replace').decode('ascii').replace('?', '_').replace(' ', '_')
    try:
        enc_name = urllib.request.quote(filename).replace(' ', '%20')
    except Exception:
        enc_name = ascii_name
    disposition = f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{enc_name}"

    url = doc.file.url
    try:
        if url.startswith('/'):
            # Dev local : stream depuis le disque
            local = os.path.join(settings.MEDIA_ROOT, doc.file.name)
            if not os.path.exists(local):
                return HttpResponse('Fichier introuvable', status=404)
            response = HttpResponse(
                (chunk for chunk in iter(lambda: open(local, 'rb').read(65536), b'')),
                content_type='application/octet-stream',
            )
            response['Content-Length'] = os.path.getsize(local)
        else:
            # Source distante (GitHub/R2) : streamer
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            upstream = urllib.request.urlopen(req, timeout=60)
            content_type = upstream.headers.get('Content-Type', 'application/octet-stream')
            response = HttpResponse(
                (chunk for chunk in iter(lambda: upstream.read(65536), b'')),
                content_type=content_type,
            )
        response['Content-Disposition'] = disposition
        response['Cache-Control'] = 'no-cache'
        response['X-Content-Type-Options'] = 'nosniff'
        return response
    except Exception as exc:  # noqa: BLE001
        return HttpResponse(f'Erreur lors du téléchargement : {exc}', status=500)


def robots_txt(request):
    """Sert le fichier robots.txt pour les moteurs de recherche."""
    from django.conf import settings
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml\n"
    )
    return HttpResponse(content, content_type='text/plain')


def service_worker(request):
    """Sert le service worker PWA avec le bon MIME (les navigateurs le refusent
    s'il n'est pas servie en text/javascript)."""
    from django.conf import settings
    sw_path = settings.BASE_DIR / 'core' / 'static' / 'core' / 'sw.js'
    try:
        data = sw_path.read_bytes()
    except OSError:
        return HttpResponse(status=404)
    return HttpResponse(data, content_type='text/javascript; charset=utf-8')


def manifest_json(request):
    """Sert le manifest PWA avec le bon MIME application/manifest+json."""
    from django.conf import settings
    path = settings.BASE_DIR / 'core' / 'static' / 'core' / 'manifest.webmanifest'
    try:
        data = path.read_bytes()
    except OSError:
        return HttpResponse(status=404)
    return HttpResponse(data, content_type='application/manifest+json; charset=utf-8')
