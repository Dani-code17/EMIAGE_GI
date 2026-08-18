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
    """Étudiant inscrit sur la plateforme (nom, prénom, niveau)."""

    LEVEL_CHOICES = Document.LEVEL_CHOICES

    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name='Niveau')
    student_id = models.CharField(max_length=20, unique=True, blank=True, verbose_name='Identifiant étudiant')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Étudiant'
        verbose_name_plural = 'Étudiants'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.level})'

    def save(self, *args, **kwargs):
        if not self.student_id:
            year = self.created_at.year if self.created_at else 2026
            count = Student.objects.filter(created_at__year=year).count() + 1
            self.student_id = f'EMG-{year}-{count:04d}'
            # garantit l'unicité en cas de collision (rare)
            while Student.objects.filter(student_id=self.student_id).exclude(pk=self.pk).exists():
                count += 1
                self.student_id = f'EMG-{year}-{count:04d}'
        super().save(*args, **kwargs)
