from django.db import models
from django.utils.text import slugify

class Document(models.Model):
    CATEGORY_CHOICES = [
        ('COURS', 'Cours'),
        ('TD_TP', 'TD/TP'),
        ('EXAMS', 'Anciens Sujets'),
        ('MAQUETTES', 'Maquettes'),
    ]
    
    LEVEL_CHOICES = [
        ('L1', 'Licence 1'),
        ('L2', 'Licence 2'),
        ('L3', 'Licence 3'),
        ('M1', 'Master 1'),
        ('M2', 'Master 2'),
    ]
    
    SEMESTER_CHOICES = [
        ('S1', 'Semestre 1'),
        ('S2', 'Semestre 2'),
        ('S3', 'Semestre 3'),
        ('S4', 'Semestre 4'),
        ('S5', 'Semestre 5'),
        ('S6', 'Semestre 6'),
        ('S7', 'Semestre 7'),
        ('S8', 'Semestre 8'),
        ('S9', 'Semestre 9'),
        ('S10', 'Semestre 10'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(blank=True, verbose_name='Description')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Catégorie')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name='Niveau')
    semester = models.CharField(max_length=3, choices=SEMESTER_CHOICES, verbose_name='Semestre')
    ecue = models.ForeignKey('ECUE', null=True, blank=True, on_delete=models.SET_NULL, related_name='documents', verbose_name='ECUE')
    file = models.FileField(upload_to='documents/', max_length=255, verbose_name='Fichier')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')

    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return f"{self.title} ({self.level} - {self.semester})"

    @property
    def extension(self):
        """Extension du fichier en majuscules (ex: PDF, DOCX) pour l'affichage."""
        name = self.file.name or ''
        return name.rsplit('.', 1)[-1].upper() if '.' in name else ''

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)


class UE(models.Model):
    code = models.CharField(max_length=200, verbose_name='Code UE')
    name = models.CharField(max_length=200, verbose_name='Nom UE')
    slug = models.SlugField(max_length=220, unique=True, verbose_name='Slug UE')
    level = models.CharField(max_length=2, choices=Document.LEVEL_CHOICES, verbose_name='Niveau')
    semester = models.CharField(max_length=3, choices=Document.SEMESTER_CHOICES, verbose_name='Semestre')

    class Meta:
        unique_together = ('level', 'semester', 'code')
        ordering = ['level', 'semester', 'code']
        verbose_name = 'UE'
        verbose_name_plural = 'UEs'

    def __str__(self):
        return f"{self.code} - {self.name} ({self.level} {self.semester})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.level}-{self.semester}-{self.code}-{self.name}")
        super().save(*args, **kwargs)


class ECUE(models.Model):
    code = models.CharField(max_length=50, verbose_name='Code ECUE', blank=True)
    name = models.CharField(max_length=200, verbose_name='Nom ECUE')
    slug = models.SlugField(max_length=220, unique=True, verbose_name='Slug ECUE')
    ue = models.ForeignKey(UE, related_name='ecues', on_delete=models.CASCADE, verbose_name='UE')

    class Meta:
        unique_together = ('ue', 'code', 'name')
        ordering = ['ue__code', 'name']
        verbose_name = 'ECUE'
        verbose_name_plural = 'ECUEs'

    def __str__(self):
        return f"{self.ue.code} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.ue.level}-{self.ue.semester}-{self.ue.code}-{self.name}"
            self.slug = slugify(base)
        super().save(*args, **kwargs)


class Student(models.Model):
    """Étudiant inscrit sur la plateforme (nom, prénom, niveau, identifiant, mot de passe)."""

    LEVEL_CHOICES = Document.LEVEL_CHOICES

    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name='Niveau')
    student_id = models.CharField(max_length=50, unique=True, verbose_name='Identifiant / matricule')
    # default='' uniquement pour la migration ; les comptes créés passent par set_password()
    password = models.CharField(max_length=128, default='', verbose_name='Mot de passe')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.level})'

    def set_password(self, raw_password):
        """Hache et enregistre le mot de passe."""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Vérifie le mot de passe haché."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password)


class StudentStat(models.Model):
    """Statistiques mensuelles d'activité d'un étudiant (visites + temps)."""

    student = models.ForeignKey(Student, related_name='stats', on_delete=models.CASCADE)
    month = models.CharField(max_length=7, verbose_name='Mois (AAAA-MM)')  # ex: 2026-08
    visits = models.PositiveIntegerField(default=0, verbose_name='Visites')
    seconds = models.PositiveIntegerField(default=0, verbose_name='Temps (secondes)')

    class Meta:
        unique_together = ('student', 'month')
        verbose_name = 'Statistique'
        verbose_name_plural = 'Statistiques'

    def __str__(self):
        return f'{self.student} — {self.month}'

    @property
    def minutes(self):
        return self.seconds // 60

    @property
    def score(self):
        """Score mensuel : visites × 10 + minutes × 2."""
        return self.visits * 10 + (self.seconds // 60) * 2


class Prize(models.Model):
    """Prix attribué par l'admin à un étudiant pour un mois donné."""

    student = models.ForeignKey(Student, related_name='prizes', on_delete=models.CASCADE)
    month = models.CharField(max_length=7, verbose_name='Mois (AAAA-MM)')
    label = models.CharField(max_length=200, verbose_name='Prix / place')
    amount = models.CharField(max_length=100, blank=True, verbose_name='Montant / cadeau')
    awarded_at = models.DateTimeField(auto_now_add=True, verbose_name='Attribué le')

    class Meta:
        ordering = ['-month', '-id']
        verbose_name = 'Prix'
        verbose_name_plural = 'Prix'

    def __str__(self):
        return f'{self.student} — {self.month} : {self.label}'


class QuizQuestion(models.Model):
    """Question de quiz rattachée à une UE, avec difficulté et explication."""

    DIFFICULTY_CHOICES = [
        ('facile', 'Facile'),
        ('normal', 'Normal'),
        ('difficile', 'Difficile'),
    ]

    ue = models.ForeignKey(UE, related_name='questions', on_delete=models.CASCADE, verbose_name='UE')
    question = models.TextField(verbose_name='Question')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='normal', verbose_name='Difficulté')
    explanation = models.TextField(blank=True, verbose_name='Explication / correction')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ue__code', 'difficulty', 'id']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f'{self.ue.code} [{self.difficulty}] {self.question[:60]}'


class QuizAnswer(models.Model):
    """Réponse possible d'une question de quiz."""

    question = models.ForeignKey(QuizQuestion, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=300, verbose_name='Réponse')
    is_correct = models.BooleanField(default=False, verbose_name='Bonne réponse')

    def __str__(self):
        return self.text


class QuizAttempt(models.Model):
    """Tentative de quiz d'un étudiant (pour suivre la progression)."""

    student = models.ForeignKey(Student, related_name='quiz_attempts', on_delete=models.CASCADE)
    ue = models.ForeignKey(UE, related_name='quiz_attempts', on_delete=models.SET_NULL, null=True, verbose_name='UE')
    difficulty = models.CharField(max_length=10, blank=True, verbose_name='Difficulté')
    correct = models.PositiveIntegerField(default=0, verbose_name='Bonnes réponses')
    total = models.PositiveIntegerField(default=0, verbose_name='Questions')
    note = models.DecimalField(max_digits=4, decimal_places=1, default=0, verbose_name='Note /20')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Date')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tentative de quiz'
        verbose_name_plural = 'Tentatives de quiz'

    def __str__(self):
        return f'{self.student} — {self.ue} : {self.note}/20'

    @property
    def percentage(self):
        return round((self.correct / self.total) * 100) if self.total else 0
