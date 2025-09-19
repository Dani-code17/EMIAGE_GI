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
    file = models.FileField(upload_to='documents/', verbose_name='Fichier')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Date d\'ajout')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='Dernière modification')

    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

    def __str__(self):
        return f"{self.title} ({self.level} - {self.semester})"

    def delete(self, *args, **kwargs):
        self.file.delete()
        super().delete(*args, **kwargs)


class UE(models.Model):
    code = models.CharField(max_length=50, verbose_name='Code UE')
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
