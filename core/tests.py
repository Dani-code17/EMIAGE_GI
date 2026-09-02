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

    def _create(self, prenom='Daniel', nom='YEO', niveau='L2', identifiant='24-1234', mdp='secret12'):
        from .models import Student
        s = Student(first_name=prenom, last_name=nom, level=niveau, student_id=identifiant)
        s.set_password(mdp)
        s.save()
        return s

    def test_inscription_cree_compte_et_connecte(self):
        # YEO Daniel né le 26/08/2004 -> IP attendue YEOD2608040001
        response = self.client.post(reverse('core:inscription'), {
            'prenom': 'Daniel', 'nom': 'YEO', 'niveau': 'L2',
            'date_naissance': '2004-08-26',
            'mdp': 'secret12', 'mdp2': 'secret12',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], reverse('core:espace'))
        from .models import Student
        student = Student.objects.filter(first_name='Daniel', last_name='YEO').first()
        self.assertIsNotNone(student)
        # IP générée automatiquement au bon format
        self.assertEqual(student.student_id, 'YEOD2608040001')
        self.assertEqual(student.level, 'L2')
        self.assertTrue(student.check_password('secret12'))
        self.assertFalse(student.check_password('mauvais'))
        # Session connectée + bandeau IP prévu (avant la redirection suivie)
        self.assertEqual(self.client.session['student_id'], student.id)
        self.assertEqual(self.client.session['nouvel_inscrit'], student.id)

    def test_inscription_ip_leve_collision(self):
        """Deux mêmes nom+prénom+naissance -> suffixe incrémente (0002)."""
        from .models import Student
        ids = []
        for _ in range(2):
            self.client.post(reverse('core:inscription'), {
                'prenom': 'Jean', 'nom': 'KOUASSI', 'niveau': 'L1',
                'date_naissance': '2002-01-15', 'mdp': 'secret12', 'mdp2': 'secret12',
            })
            # se déconnecter pour pouvoir s'inscrire à nouveau (inscription
            # redirige si déjà connecté)
            self.client.get(reverse('core:deconnexion'))
        for s in Student.objects.filter(first_name='Jean'):
            ids.append(s.student_id)
        self.assertIn('KOUJ1501020001', ids)
        self.assertIn('KOUJ1501020002', ids)

    def test_inscription_champs_requis(self):
        response = self.client.post(reverse('core:inscription'), {
            'prenom': '', 'nom': 'YEO', 'niveau': 'L2',
            'date_naissance': '2004-08-26', 'mdp': 'secret12', 'mdp2': 'secret12',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'nom et ton prénom')
        from .models import Student
        self.assertEqual(Student.objects.count(), 0)

    def test_inscription_date_manquante(self):
        response = self.client.post(reverse('core:inscription'), {
            'prenom': 'Daniel', 'nom': 'YEO', 'niveau': 'L2',
            'mdp': 'secret12', 'mdp2': 'secret12',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'date de naissance')
        from .models import Student
        self.assertEqual(Student.objects.count(), 0)

    def test_inscription_mdp_courts_ou_differents(self):
        from .models import Student
        def post(**extra):
            data = {'prenom': 'A', 'nom': 'B', 'niveau': 'L1',
                    'date_naissance': '2004-08-26', 'mdp': 'secret12', 'mdp2': 'secret12'}
            data.update(extra)
            return self.client.post(reverse('core:inscription'), data)
        # mot de passe trop court
        post(mdp='123', mdp2='123')
        self.assertEqual(Student.objects.count(), 0)
        # mots de passe différents
        post(mdp2='autre12')
        self.assertEqual(Student.objects.count(), 0)

    def test_connexion_par_identifiant_et_mdp(self):
        student = self._create()
        response = self.client.post(reverse('core:connexion'), {
            'identifiant': '24-1234', 'mdp': 'secret12',
        })
        self.assertRedirects(response, reverse('core:espace'))
        self.assertEqual(self.client.session['student_id'], student.id)

    def test_connexion_par_prenom_nom_DOIT_echouer(self):
        """La connexion par prénom+nom (sans l'IP) est refusée (sécurité)."""
        self._create(prenom='Daniel', nom='YEO', identifiant='24-1234')
        response = self.client.post(reverse('core:connexion'), {
            'identifiant': 'Daniel YEO', 'mdp': 'secret12',
        })
        self.assertEqual(response.status_code, 200)  # pas de redirection
        self.assertNotIn('student_id', self.client.session)

    def test_connexion_rate_limit(self):
        """5 échecs successifs bloquent temporairement."""
        self._create()
        for _ in range(5):
            self.client.post(reverse('core:connexion'), {
                'identifiant': '24-1234', 'mdp': 'mauvais',
            })
        # 6e tentative : bloquée
        response = self.client.post(reverse('core:connexion'), {
            'identifiant': '24-1234', 'mdp': 'secret12',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Trop de tentatives')
        self.assertNotIn('student_id', self.client.session)

    def test_connexion_mauvais_mdp(self):
        self._create()
        response = self.client.post(reverse('core:connexion'), {
            'identifiant': '24-1234', 'mdp': 'mauvais',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Identifiant ou mot de passe incorrect')

    def test_mdp_en_clair_ancien_admin_rehache(self):
        """Un compte créé via l'admin avec un mdp en clair doit pouvoir se
        connecter, et son mot de passe est re-haché automatiquement."""
        from .models import Student
        from django.contrib.auth.hashers import identify_hasher
        # Simule un compte créé via l'admin (mot de passe stocké en clair)
        s = Student(first_name='Ancien', last_name='Compte', level='L1', student_id='ancien-1', password='clair123')
        s.save()
        # connexion avec le mot de passe en clair
        response = self.client.post(reverse('core:connexion'), {
            'identifiant': 'ancien-1', 'mdp': 'clair123',
        })
        self.assertRedirects(response, reverse('core:espace'))
        # le mot de passe est maintenant haché
        s.refresh_from_db()
        identify_hasher(s.password)  # ne doit pas lever d'exception
        self.assertTrue(s.check_password('clair123'))

    def test_espace_redirige_sans_connexion(self):
        response = self.client.get(reverse('core:espace'))
        self.assertRedirects(response, reverse('core:connexion'))

    def test_deconnexion_vide_session(self):
        self._create(prenom='Aya', nom='NGuessan', niveau='M1', identifiant='m1-99')
        self.client.post(reverse('core:connexion'), {'identifiant': 'm1-99', 'mdp': 'secret12'})
        self.client.get(reverse('core:deconnexion'))
        response = self.client.get(reverse('core:espace'))
        self.assertRedirects(response, reverse('core:connexion'))

    def test_securite_espace_protege_sans_session(self):
        """Un visiteur non connecté ne voit pas 'Mon espace' et ne peut pas accéder à /espace/."""
        # Page d'accueil : pas de lien 'Mon espace', présence de Connexion
        html = self.client.get(reverse('core:home')).content.decode('utf-8')
        self.assertNotIn('> Mon espace', html)
        self.assertIn('Connexion', html)
        # /espace/ redirige vers la connexion
        response = self.client.get(reverse('core:espace'))
        self.assertRedirects(response, reverse('core:connexion'))

    def test_securite_espace_protege_avec_session_forgee(self):
        """Une session avec un étudiant_id inconnu est purgée -> pas d'accès."""
        self.client.session['student_id'] = 999999
        self.client.session.save()
        response = self.client.get(reverse('core:espace'))
        self.assertRedirects(response, reverse('core:connexion'))
        # la session a été purgée
        self.assertIsNone(self.client.session.get('student_id'))

    def test_activite_enregistree(self):
        """Le middleware compte les visites et le temps."""
        from django.utils import timezone
        from .models import StudentStat
        self._create()
        self.client.post(reverse('core:connexion'), {'identifiant': '24-1234', 'mdp': 'secret12'})
        student_id = self.client.session['student_id']
        self.client.get(reverse('core:espace'))
        month = timezone.now().strftime('%Y-%m')
        stat = StudentStat.objects.filter(student_id=student_id, month=month).first()
        # La visite du jour est enregistrée (mois courant)
        self.assertIsNotNone(stat)
        self.assertGreaterEqual(stat.visits, 1)


class AdminEspaceTests(TestCase):
    def test_admin_login_ok(self):
        response = self.client.post(reverse('core:admin_login'), {
            'username': 'Daniki', 'password': 'Daniel87606819',
        })
        self.assertRedirects(response, reverse('core:admin_dashboard'))
        self.assertEqual(self.client.session.get('admin_logged'), True)

    def test_admin_login_ko(self):
        response = self.client.post(reverse('core:admin_login'), {
            'username': 'Daniki', 'password': 'mauvais',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Identifiant ou mot de passe admin incorrect')

    def test_dashboard_requiert_connexion(self):
        response = self.client.get(reverse('core:admin_dashboard'))
        self.assertRedirects(response, reverse('core:admin_login'))


class QuizFlowTests(TestCase):
    def setUp(self):
        from .models import Student
        s = Student(first_name='Quiz', last_name='Test', level='L2', student_id='quiz-1')
        s.set_password('secret12')
        s.save()
        self.client.post(reverse('core:connexion'), {'identifiant': 'quiz-1', 'mdp': 'secret12'})

    def test_quiz_sans_questions_renvoie_erreur(self):
        # Une UE sans questions
        ue = UE.objects.create(code='UE VIDE', name='UE VIDE', level='L2', semester='S3')
        response = self.client.post(reverse('core:quiz'), {'ue': ue.id, 'difficulte': '', 'nombre': 5})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aucune question disponible')

    def test_quiz_complet(self):
        from .models import UE, QuizQuestion, QuizAnswer
        # Les UE L2 ne sont pas seedées par les migrations : on crée la nôtre
        ue = UE.objects.create(code='Mathématiques 4', name='Mathématiques 4', level='L2', semester='S3')
        # Crée des questions dans la BD de test
        q1 = QuizQuestion.objects.create(ue=ue, question='2+2 = ?', difficulty='facile', explanation='Arithmétique')
        QuizAnswer.objects.create(question=q1, text='4', is_correct=True)
        QuizAnswer.objects.create(question=q1, text='5', is_correct=False)
        q2 = QuizQuestion.objects.create(ue=ue, question='3+3 = ?', difficulty='facile', explanation='Arithmétique')
        QuizAnswer.objects.create(question=q2, text='6', is_correct=True)
        QuizAnswer.objects.create(question=q2, text='7', is_correct=False)
        questions = [q1, q2]

        # génère le quiz
        response = self.client.post(reverse('core:quiz'), {'ue': ue.id, 'difficulte': '', 'nombre': 5})
        self.assertRedirects(response, reverse('core:quiz_play'))
        qids = self.client.session['quiz_questions']
        self.assertEqual(len(qids), 2)

        # répond : toutes les bonnes réponses
        post = {}
        for q in questions:
            good = q.answers.filter(is_correct=True).first()
            post[f'q{q.id}'] = good.id
        response = self.client.post(reverse('core:quiz_result'), post)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/20')
        self.assertEqual(response.context['note'], 20.0)
        self.assertEqual(response.context['correct'], 2)
        # La tentative est enregistrée (historique)
        from .models import QuizAttempt
        attempt = QuizAttempt.objects.get(student__student_id='quiz-1')
        self.assertEqual(attempt.note, 20.0)
        self.assertEqual(attempt.correct, 2)
