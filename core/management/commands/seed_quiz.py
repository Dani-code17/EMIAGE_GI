"""Seed de questions de quiz d'exemple (idempotent) — à compléter via l'admin.

Usage : python manage.py seed_quiz
"""
from django.core.management.base import BaseCommand
from core.models import UE, QuizQuestion, QuizAnswer


def q(ue, question, good, others, difficulty, explanation=''):
    """Crée une question avec une bonne réponse et des mauvaises."""
    question_obj = QuizQuestion.objects.create(
        ue=ue, question=question, difficulty=difficulty, explanation=explanation,
    )
    QuizAnswer.objects.create(question=question_obj, text=good, is_correct=True)
    for text in others:
        QuizAnswer.objects.create(question=question_obj, text=text, is_correct=False)
    return question_obj


class Command(BaseCommand):
    help = 'Seed de questions de quiz d\'exemple (idempotent).'

    def handle(self, *args, **options):
        created = 0

        def seed(ue_code, level, semester, questions):
            nonlocal created
            ue = UE.objects.filter(code=ue_code, level=level, semester=semester).first()
            if not ue:
                self.stdout.write(f'[SKIP] UE introuvable : {ue_code} {level} {semester}')
                return
            if ue.questions.exists():
                self.stdout.write(f'[SKIP] Questions déjà présentes : {ue_code}')
                return
            for args_q in questions:
                q(ue, *args_q)
                created += 1
            self.stdout.write(f'[OK] {len(questions)} questions pour {ue_code}')

        seed('UE MATHEMATIQUES 1', 'L1', 'S1', [
            ("Quelle est la limite de la suite u_n = 1/n quand n tend vers l'infini ?",
             '0', ['1', '+∞', '-∞'], 'facile',
             "1/n devient de plus en plus petit : sa limite est 0."),
            ("La somme des n premiers entiers 1+2+...+n est égale à :",
             'n(n+1)/2', ['n²', 'n(n-1)/2', '2n'], 'normal',
             "C'est la formule classique de Gauss : n(n+1)/2."),
        ])

        seed('UE ALGORITHMIQUE ET PROGRAMMATION', 'L1', 'S2', [
            ("En programmation, une variable est :",
             'un emplacement mémoire nommé', ['un fichier', 'une fonction', 'un algorithme'], 'facile',
             "Une variable désigne un emplacement mémoire auquel on donne un nom."),
            ("Quelle est la complexité temporelle d'une recherche dichotomique dans un tableau trié ?",
             'O(log n)', ['O(n)', 'O(n²)', 'O(1)'], 'difficile',
             "À chaque étape on divise la zone de recherche par deux : O(log n)."),
        ])

        seed('Mathématiques 4', 'L2', 'S3', [
            ("Dans une base, un vecteur v = (2, -1) a pour coordonnées...",
             '2 et -1', ['-2 et 1', '1 et 2', '-1 et 2'], 'facile',
             "Les coordonnées du vecteur sont simplement ses composantes dans la base."),
            ("La transposée d'une matrice 2×3 est une matrice :",
             '3×2', ['2×3', '2×2', '3×3'], 'normal',
             "La transposée inverse les dimensions : une matrice m×n devient n×m."),
        ])

        seed('Données semi-structurées et bases de données', 'L2', 'S4', [
            ("Quel langage permet d'interroger une base de données relationnelle ?",
             'SQL', ['HTML', 'Python seul', 'JSON'], 'facile',
             "SQL (Structured Query Language) est le langage standard des bases relationnelles."),
            ("Une clé primaire doit être :",
             'unique et non nulle', ['nullable', 'multiple', 'optionnelle'], 'normal',
             "La clé primaire identifie chaque ligne de façon unique ; elle ne peut pas être NULL."),
        ])

        seed('Programmation orientée objet', 'L2', 'S3', [
            ("En POO, l'héritage permet de :",
             "réutiliser et étendre le comportement d'une classe", ['dupliquer du code sans lien', 'supprimer des classes', 'cacher tous les attributs'], 'normal',
             "L'héritage permet à une classe d'hériter des attributs et méthodes d'une autre."),
            ("Le polymorphisme signifie :",
             'qu\'un même message peut être traité différemment selon l\'objet',
             ['qu\'une classe ne peut avoir qu\'une méthode', 'que les objets sont immuables', 'qu\'il n\'y a qu\'un type'], 'difficile',
             "Le polymorphisme permet à des objets de classes différentes de répondre à la même interface."),
        ])

        self.stdout.write(self.style.SUCCESS(f'[SUMMARY] {created} questions créées'))
