from django.db import models

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
    ]
    
    title = models.CharField(max_length=200, verbose_name='Titre')
    description = models.TextField(blank=True, verbose_name='Description')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name='Catégorie')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, verbose_name='Niveau')
    semester = models.CharField(max_length=2, choices=SEMESTER_CHOICES, verbose_name='Semestre')
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
