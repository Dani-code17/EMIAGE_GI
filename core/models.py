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
    birth_date = models.DateField(null=True, blank=True, verbose_name='Date de naissance')
    student_id = models.CharField(max_length=60, unique=True, verbose_name='Identifiant permanent (IP)')
    # default='' uniquement pour la migration ; les comptes créés passent par set_password()
    password = models.CharField(max_length=128, default='', verbose_name='Mot de passe')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.level})'

    @classmethod
    def _normalize_name(cls, name):
        """Nom sans accents, en majuscules (ex: 'Éloi' -> 'ELOI')."""
        import unicodedata
        norm = unicodedata.normalize('NFKD', name or '')
        norm = ''.join(c for c in norm if not unicodedata.combining(c))
        return norm.upper()

    @classmethod
    def _date_jjmmAA(cls, birth_date):
        """Date au format JJMMAA (ex: 20/02/2007 -> '200207')."""
        return f'{birth_date:%d%m%y}'

    @classmethod
    def build_student_id(cls, last_name, first_name, birth_date):
        """Construit l'IP unique : 3 lettres du nom + 1ère lettre du prénom
        + date JJMMAA + suffixe 0001 (incrémenté si collision).

        Ex : YEO Daniel né le 26/08/2004 -> 'YEOD2608040001'
        """
        base = (
            cls._normalize_name(last_name)[:3]
            + cls._normalize_name(first_name)[:1]
            + cls._date_jjmmAA(birth_date)
        )
        suffix = 1
        while cls.objects.filter(student_id=f'{base}{suffix:04d}').exists():
            suffix += 1
        return f'{base}{suffix:04d}'

    def set_password(self, raw_password):
        """Hache et enregistre le mot de passe."""
        from django.contrib.auth.hashers import make_password
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Vérifie le mot de passe haché.

        Gère aussi les comptes créés via l'admin avec un mot de passe en clair :
        si la valeur stockée n'est pas un hash valide, on compare en clair et on
        re-hache immédiatement (migration en douceur).
        """
        from django.contrib.auth.hashers import check_password, identify_hasher
        try:
            identify_hasher(self.password)
            is_hashed = True
        except ValueError:
            is_hashed = False

        if not is_hashed:
            if self.password == raw_password:
                self.set_password(raw_password)
                self.save(update_fields=['password'])
                return True
            return False
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
    ecue = models.ForeignKey(ECUE, related_name='questions', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='ECUE')
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


class JIEdition(models.Model):
    """Une édition de la Journée d'Intégration (JI-MIAGE).

    Le contenu est modifiable depuis l'admin : l'utilisateur peut mettre à jour
    les infos (date, lieu, prix…), les moyens de paiement et les photos.
    """

    STATUS_CHOICES = [
        ('avenir', 'À venir'),
        ('inscriptions', 'Inscriptions ouvertes'),
        ('passee', 'Passée'),
    ]

    year = models.CharField(max_length=20, verbose_name='Édition / année')  # ex: "2026"
    title = models.CharField(max_length=200, verbose_name='Titre')
    subtitle = models.CharField(max_length=250, blank=True, verbose_name='Sous-titre')
    event_date = models.DateField(null=True, blank=True, verbose_name='Date')
    event_time = models.CharField(max_length=50, blank=True, verbose_name='Heure')  # ex: "09h00"
    location = models.CharField(max_length=200, blank=True, verbose_name='Lieu')
    description = models.TextField(blank=True, verbose_name='Description / programme')
    price = models.CharField(max_length=100, blank=True, verbose_name='Prix (ex: 5 000 FCFA)')
    poster_url = models.URLField(blank=True, verbose_name='Affiche (URL)')
    poster = models.ImageField(upload_to='ji/', blank=True, null=True, verbose_name='Affiche (fichier)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='avenir', verbose_name='Statut')
    is_featured = models.BooleanField(default=False, verbose_name="Édition mise en avant")
    order = models.IntegerField(default=0, verbose_name='Ordre')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order', '-year']
        verbose_name = "Édition de la JI"
        verbose_name_plural = "Éditions de la JI"

    def __str__(self):
        return f'JI {self.year} — {self.title}'

    @property
    def poster_image(self):
        """Affiche : l'URL si fournie, sinon le fichier uploadé."""
        if self.poster_url:
            return self.poster_url
        if self.poster:
            return self.poster.url
        return ''

    @property
    def status_label(self):
        return dict(self.STATUS_CHOICES).get(self.status, '')


class JIPayment(models.Model):
    """Moyen de paiement / inscription à la JI (numéro, lien…)."""

    edition = models.ForeignKey(JIEdition, related_name='payments', on_delete=models.CASCADE,
                                null=True, blank=True, verbose_name='Édition')
    label = models.CharField(max_length=100, verbose_name='Moyen (ex: Orange Money)')
    number = models.CharField(max_length=60, blank=True, verbose_name='Numéro')
    holder = models.CharField(max_length=120, blank=True, verbose_name='Titulaire')
    instructions = models.CharField(max_length=250, blank=True, verbose_name='Instructions')
    link = models.URLField(blank=True, verbose_name='Lien de paiement')
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    order = models.IntegerField(default=0, verbose_name='Ordre')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Moyen de paiement JI'
        verbose_name_plural = 'Moyens de paiement JI'

    def __str__(self):
        return f'{self.label} — {self.number or self.link}'


class JIPhoto(models.Model):
    """Photo d'une édition de la JI (pour les archives)."""

    edition = models.ForeignKey(JIEdition, related_name='photos', on_delete=models.CASCADE,
                               verbose_name='Édition')
    image_url = models.URLField(blank=True, verbose_name='Photo (URL)')
    image = models.ImageField(upload_to='ji/', blank=True, null=True, verbose_name='Photo (fichier)')
    caption = models.CharField(max_length=200, blank=True, verbose_name='Légende')
    order = models.IntegerField(default=0, verbose_name='Ordre')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Photo JI'
        verbose_name_plural = 'Photos JI'

    def __str__(self):
        return self.caption or f'Photo {self.pk}'

    @property
    def src(self):
        """Source : l'URL si fournie, sinon le fichier uploadé."""
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return ''
