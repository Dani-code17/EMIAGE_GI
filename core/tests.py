import tempfile

from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .models import Document, UE, ECUE
from .views import get_semester_mapping

# Les fichiers uploadés par les tests ne doivent pas polluer media/ :
# on redirige MEDIA_ROOT vers un dossier temporaire.
_TMP_MEDIA = tempfile.mkdtemp(prefix='emiage-test-media-')


class UeEcueModelTests(TestCase):
    """Tests des modèles UE et ECUE."""

    def setUp(self):
        # Code volontairement unique pour ne pas entrer en collision
        # avec les UE seedées par les migrations de données (0004, 0007).
        self.ue = UE.objects.create(
            code='UE TEST-XYZ',
            name='UE TEST-XYZ',
            level='L1',
            semester='S1',
        )

    def test_ue_slug_auto_generated(self):
        self.assertTrue(self.ue.slug)
        self.assertIn('l1', self.ue.slug)
        self.assertIn('s1', self.ue.slug)

    def test_ecue_slug_auto_generated(self):
        ecue = ECUE.objects.create(ue=self.ue, name='ECUE Test')
        self.assertTrue(ecue.slug)
        self.assertIn('l1-s1', ecue.slug)

    def test_ue_unique_per_level_semester_code(self):
        with self.assertRaises(Exception):
            UE.objects.create(
                code='UE TEST-XYZ',
                name='Doublon interdit',
                level='L1',
                semester='S1',
            )


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class DocumentModelTests(TestCase):
    def setUp(self):
        self.ue = UE.objects.create(
            code='UE TEST-XYZ', name='UE TEST-XYZ', level='L1', semester='S1'
        )
        self.ecue = ECUE.objects.create(ue=self.ue, name='ECUE Test')

    def test_document_creation(self):
        before = Document.objects.count()
        f = SimpleUploadedFile('cours.pdf', b'%PDF-1.4 test', content_type='application/pdf')
        doc = Document.objects.create(
            title='Cours de test',
            category='COURS',
            level='L1',
            semester='S1',
            ecue=self.ecue,
            file=f,
        )
        self.assertEqual(Document.objects.filter(title='Cours de test').count(), 1)
        self.assertEqual(Document.objects.count(), before + 1)
        self.assertEqual(str(doc), 'Cours de test (L1 - S1)')
        # L'upload_date est remplie automatiquement
        self.assertIsNotNone(doc.upload_date)


class SemesterMappingTests(TestCase):
    def test_mapping_complet(self):
        self.assertEqual(get_semester_mapping('L1', 's1'), 'S1')
        self.assertEqual(get_semester_mapping('L1', 's2'), 'S2')
        self.assertEqual(get_semester_mapping('L2', 's1'), 'S3')
        self.assertEqual(get_semester_mapping('L2', 's2'), 'S4')
        self.assertEqual(get_semester_mapping('L3', 's1'), 'S5')
        self.assertEqual(get_semester_mapping('L3', 's2'), 'S6')
        self.assertEqual(get_semester_mapping('M1', 's1'), 'S7')
        self.assertEqual(get_semester_mapping('M1', 's2'), 'S8')
        self.assertEqual(get_semester_mapping('M2', 's1'), 'S9')
        self.assertEqual(get_semester_mapping('M2', 's2'), 'S10')


@override_settings(MEDIA_ROOT=_TMP_MEDIA)
class PageTests(TestCase):
    """Smoke tests : toutes les pages principales répondent 200."""

    def setUp(self):
        self.ue = UE.objects.create(
            code='UE TEST', name='UE TEST', level='L1', semester='S1'
        )
        self.ecue = ECUE.objects.create(ue=self.ue, name='ECUE Test')
        f = SimpleUploadedFile('cours.pdf', b'%PDF-1.4 test', content_type='application/pdf')
        Document.objects.create(
            title='Cours de test',
            description='Un document de démonstration',
            category='COURS',
            level='L1',
            semester='S1',
            ecue=self.ecue,
            file=f,
        )

    def test_pages_principales(self):
        urls = [
            reverse('core:home'),
            reverse('core:bibliotheque_index'),
            reverse('core:niveau_l1'),
            reverse('core:niveau_l2'),
            reverse('core:niveau_l3'),
            reverse('core:niveau_m1'),
            reverse('core:niveau_m2'),
            reverse('core:about'),
            reverse('core:coming_soon'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_niveau_avec_filtres(self):
        """La page L1 avec UE + catégorie affiche le document filtré."""
        response = self.client.get(
            reverse('core:niveau_l1'),
            {'semestre': 's1', 'ue': self.ue.slug, 'category': 'cours'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cours de test')
        self.assertEqual(len(response.context['documents']), 1)
        # Contexte UI : libellé du niveau + compteurs de documents par catégorie
        self.assertEqual(response.context['niveau_label'], 'Licence 1')
        self.assertEqual(response.context['category_counts']['cours'], 1)
        self.assertIn('selection_count', response.context)

    def test_niveau_categorie_maquettes(self):
        """La catégorie maquettes affiche les maquettes du niveau même sans UE."""
        response = self.client.get(
            reverse('core:niveau_l1'),
            {'semestre': 's1', 'category': 'maquettes'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('documents', response.context)

    def test_recherche_par_mot_cle(self):
        response = self.client.get(
            reverse('core:niveau_l1'),
            {'semestre': 's1', 'ue': self.ue.slug, 'category': 'cours', 'q': 'démonstration'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['documents']), 1)

    def test_sitemap_xml(self):
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/xml')

    def test_bibliotheque_index_context(self):
        """L'index de la médiathèque fournit les compteurs par niveau."""
        response = self.client.get(reverse('core:bibliotheque_index'))
        self.assertEqual(response.status_code, 200)
        levels = response.context['levels']
        self.assertEqual(len(levels), 5)
        # Chaque niveau a une URL et un libellé
        self.assertTrue(all(l['url'] and l['label'] for l in levels))
        # Le total correspond à la somme des compteurs
        self.assertEqual(
            response.context['total_documents'],
            sum(l['count'] for l in levels),
        )


class StudentFlowTests(TestCase):
    """Parcours étudiant : inscription, connexion, espace, déconnexion."""

    def test_inscription_cree_compte_et_connecte(self):
        response = self.client.post(reverse('core:inscription'), {
            'prenom': 'Daniel',
            'nom': 'YEO',
            'niveau': 'L2',
        })
        self.assertRedirects(response, reverse('core:espace'))
        # Le compte existe avec un identifiant généré
        from .models import Student
        student = Student.objects.get(first_name='Daniel', last_name='YEO')
        self.assertEqual(student.level, 'L2')
        self.assertTrue(student.student_id.startswith('EMG-'))
        # Session connectée
        self.assertEqual(self.client.session['student_id'], student.id)

    def test_inscription_champs_requis(self):
        response = self.client.post(reverse('core:inscription'), {
            'prenom': '',
            'nom': 'YEO',
            'niveau': 'L2',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'nom et ton prénom')
        from .models import Student
        self.assertEqual(Student.objects.count(), 0)

    def test_connexion_retrouve_compte(self):
        from .models import Student
        student = Student.objects.create(first_name='Marie', last_name='Kouassi', level='L1')
        response = self.client.post(reverse('core:connexion'), {
            'prenom': 'marie',
            'nom': 'KOUASSI',
            'niveau': 'L1',
        })
        self.assertRedirects(response, reverse('core:espace'))
        self.assertEqual(self.client.session['student_id'], student.id)

    def test_connexion_inconnue(self):
        response = self.client.post(reverse('core:connexion'), {
            'prenom': 'Inconnu',
            'nom': 'Personne',
            'niveau': 'L1',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aucun compte trouvé')

    def test_espace_redirige_sans_connexion(self):
        response = self.client.get(reverse('core:espace'))
        self.assertRedirects(response, reverse('core:connexion'))

    def test_deconnexion_vide_session(self):
        from .models import Student
        student = Student.objects.create(first_name='Aya', last_name='NGuessan', level='M1')
        self.client.post(reverse('core:connexion'), {
            'prenom': 'Aya',
            'nom': 'NGuessan',
            'niveau': 'M1',
        })
        self.client.get(reverse('core:deconnexion'))
        response = self.client.get(reverse('core:espace'))
        self.assertRedirects(response, reverse('core:connexion'))
