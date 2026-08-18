"""Seed de questions de quiz pour L1, L2 et L3 (par UE et ECUE).

Idempotent : ne recrée pas les questions d'une ECUE déjà seedée.
Usage : python manage.py seed_quiz [--force]
"""
from django.core.management.base import BaseCommand
from core.models import UE, ECUE, QuizQuestion, QuizAnswer


def q(ue, ecue, question, good, others, difficulty, explanation=''):
    """Crée une question (attachée à l'ECUE, ou à l'UE si ecue est None)."""
    question_obj = QuizQuestion.objects.create(
        ue=ue, ecue=ecue, question=question, difficulty=difficulty, explanation=explanation,
    )
    QuizAnswer.objects.create(question=question_obj, text=good, is_correct=True)
    for text in others:
        QuizAnswer.objects.create(question=question_obj, text=text, is_correct=False)
    return question_obj


# Structure : (niveau, semestre, code UE) -> {nom ECUE (ou None) : [questions]}
# Chaque question : (énoncé, bonne réponse, [mauvaises réponses], difficulté, explication)
BANK = {
    # ============================ L1 S1 ============================
    ('L1', 'S1', 'UE MATHEMATIQUES 1'): {
        'suites et fonctions': [
            ("La limite de la suite u_n = 1/n quand n tend vers l'infini est :", "0",
             ["1", "+∞", "-∞"], "facile",
             "1/n devient de plus en plus petit : sa limite est 0."),
            ("Une suite est dite croissante si :", "u_{n+1} ≥ u_n pour tout n",
             ["u_{n+1} ≤ u_n", "u_{n+1} = 0", "elle n'a pas de limite"], "normal",
             "Une suite croissante vérifie u_{n+1} ≥ u_n pour tout rang n."),
        ],
        'Calcul intégral': [
            ("L'intégrale de f(x) = 1 entre a et b vaut :", "b − a",
             ["a + b", "a × b", "1"], "normal",
             "L'aire sous la courbe constante 1 entre a et b est b − a."),
            ("Une primitive de f(x) = 2x est :", "x² + C",
             ["2x + C", "x + C", "x³ + C"], "normal",
             "La dérivée de x² est 2x, donc x² (à une constante près) est une primitive."),
        ],
    },
    ('L1', 'S1', 'UE MATHEMATIQUES 2'): {
        'Elements de Logique': [
            ("La proposition « A ET B » est vraie :", "si A et B sont toutes les deux vraies",
             ["si A est vraie", "si B est vraie", "toujours"], "facile",
             "La conjonction ET n'est vraie que si les deux propositions le sont."),
            ("La négation de « A ⇒ B » est :", "A et non B",
             ["non A et B", "non A ou B", "A ou B"], "difficile",
             "A ⇒ B est faux uniquement quand A est vraie et B fausse."),
        ],
        'Structure Algébrique': [
            ("L'élément neutre de l'addition est :", "0",
             ["1", "-1", "∞"], "facile",
             "a + 0 = a pour tout nombre a."),
            ("Dans un groupe, chaque élément possède :", "un inverse",
             ["un double", "un neutre identique", "une puissance"], "normal",
             "Par définition d'un groupe, tout élément a un inverse."),
        ],
    },
    ('L1', 'S1', 'UE ECONOMIE'): {
        'Economie générale': [
            ("La loi de l'offre et de la demande : quand le prix augmente, la demande :",
             "diminue", ["augmente", "reste stable", "disparaît"], "facile",
             "Toutes choses égales par ailleurs, une hausse du prix réduit la demande."),
            ("Le PIB mesure :", "la richesse produite dans un pays sur une période",
             ["la population", "le taux de chômage", "la dette publique"], "normal",
             "Le PIB (produit intérieur brut) mesure la production de biens et services."),
        ],
        'Économie 2': [
            ("L'inflation est :", "la hausse générale et durable des prix",
             ["la baisse des prix", "la hausse du chômage", "la hausse du PIB"], "normal",
             "L'inflation correspond à une hausse générale et durable des prix."),
        ],
    },
    ('L1', 'S1', 'UE Organisations des Entreprises'): {
        'Organisations des Entreprises': [
            ("Une organisation se distingue d'un groupe informel par :",
             "des objectifs et une structure formels",
             ["le nombre de membres", "sa localisation", "sa taille"], "normal",
             "L'organisation possède des objectifs précis et une structure de répartition des tâches."),
            ("La fonction « commerciale » d'une entreprise concerne :",
             "la vente et le marketing", ["la comptabilité", "la production", "les RH"], "facile",
             "Le commercial s'occupe de la vente, du marketing et de la relation client."),
        ],
    },
    ('L1', 'S1', 'UE Initiation à l\'informatique'): {
        'Initiation à l\'informatique': [
            ("Qu'est-ce qu'un octet ?", "8 bits",
             ["16 bits", "4 bits", "1 bit"], "facile",
             "Un octet regroupe 8 bits."),
            ("La RAM est une mémoire :", "volatile (effacée à l'extinction)",
             ["permanente", "de stockage de masse", "en lecture seule"], "normal",
             "La RAM perd son contenu quand on coupe l'alimentation."),
        ],
    },
    ('L1', 'S1', 'UE Initiation à l\'algorithmique'): {
        'Initiation à l\'algorithmique': [
            ("Un algorithme est :", "une suite finie d'étapes pour résoudre un problème",
             ["un programme compilé", "un langage", "une donnée"], "facile",
             "Un algorithme décrit la démarche, indépendamment du langage."),
            ("Un algorithme doit toujours :", "se terminer",
             ["être le plus long possible", "utiliser beaucoup de mémoire", "être itératif"], "normal",
             "L'algorithmique garantit la terminaison pour être exploitable."),
        ],
    },
    ('L1', 'S1', 'UE Outils Bureautiques 1'): {
        'Outils Bureautiques 1': [
            ("Dans Excel, une formule commence par :", "=",
             ["+", "#", "&"], "facile",
             "Toute formule Excel commence par le signe =."),
            ("Dans Word, « Ctrl+S » permet de :", "enregistrer le document",
             ["copier", "imprimer", "annuler"], "facile",
             "Ctrl+S enregistre le document en cours."),
        ],
    },
    ('L1', 'S1', 'UE Electronique Numérique'): {
        'Electronique Numérique': [
            ("Un signal numérique prend :", "des valeurs discrètes (0 ou 1)",
             ["des valeurs continues", "des valeurs analogiques", "aucune valeur"], "facile",
             "Le numérique code l'information en valeurs discrètes binaires."),
            ("La loi d'Ohm s'écrit :", "U = R × I",
             ["U = R / I", "U = I / R", "U = R + I"], "normal",
             "La tension U est le produit de la résistance R par l'intensité I."),
        ],
    },

    # ============================ L1 S2 ============================
    ('L1', 'S2', 'UE MATHEMATIQUES 3'): {
        'Calcul matriciel': [
            ("La matrice identité 2×2 a pour diagonale :", "1, 1",
             ["0, 0", "1, 0", "0, 1"], "facile",
             "La matrice identité a des 1 sur la diagonale et des 0 ailleurs."),
            ("Le produit d'une matrice 2×3 par une matrice 3×4 donne :", "une matrice 2×4",
             ["une matrice 3×3", "une matrice 4×2", "impossible"], "normal",
             "Le nombre de colonnes de A doit égaler le nombre de lignes de B ; le résultat est 2×4."),
        ],
        'Espaces vectoriels': [
            ("Le vecteur nul est :", "l'élément neutre de l'addition vectorielle",
             ["l'inverse de tout vecteur", "un vecteur unitaire", "une base"], "normal",
             "v + 0 = v pour tout vecteur v."),
        ],
        'Géometrie': [
            ("La distance entre deux points dans le plan se calcule avec :", "le théorème de Pythagore",
             ["le théorème de Thalès", "la loi d'Ohm", "le binôme de Newton"], "normal",
             "La distance euclidienne découle du théorème de Pythagore."),
        ],
    },
    ('L1', 'S2', 'UE PROBABILITES ET STATISTIQUE 1'): {
        'Probabilité': [
            ("La probabilité d'un événement certain est :", "1",
             ["0", "0,5", "+∞"], "facile",
             "Un événement certain a une probabilité de 1."),
            ("Si P(A) = 0,3, alors P(contraire de A) = :", "0,7",
             ["0,3", "1,3", "-0,3"], "normal",
             "P(non A) = 1 − P(A) = 0,7."),
        ],
        'Statistique': [
            ("La moyenne de 2, 4, 6 est :", "4",
             ["3", "5", "12"], "facile",
             "(2 + 4 + 6) / 3 = 4."),
            ("La médiane d'une série ordonnée partage la série :", "en deux moitiés égales",
             ["en trois tiers", "autour de la moyenne", "en quartiles"], "normal",
             "La médiane est la valeur centrale qui partage la série en deux."),
        ],
        'Langage R': [
            ("Dans R, le symbole d'affectation courant est :", "<-",
             ["=>", "::", "=="], "normal",
             "R utilise <- (ou =) pour affecter une valeur à une variable."),
        ],
    },
    ('L1', 'S2', 'UE ALGORITHMIQUE ET PROGRAMMATION'): {
        'Algorithmique': [
            ("Une recherche dichotomique exige un tableau :", "trié",
             ["aléatoire", "inversé", "de petite taille uniquement"], "normal",
             "La dichotomie repose sur la comparaison au milieu d'un tableau trié."),
            ("La complexité de la recherche dichotomique est :", "O(log n)",
             ["O(n)", "O(n²)", "O(1)"], "difficile",
             "Chaque étape divise l'espace de recherche par deux : O(log n)."),
        ],
        'Programmation Java': [
            ("En Java, le point d'entrée d'un programme est :", "la méthode main",
             ["la méthode start", "le constructeur", "la classe Main uniquement"], "normal",
             "L'exécution démarre dans la méthode public static void main."),
            ("Java est un langage :", "compilé en bytecode puis exécuté par la JVM",
             ["interprété directement", "uniquement compilé en natif", "de script"], "normal",
             "Java compile vers du bytecode exécuté par la machine virtuelle Java."),
        ],
    },
    ('L1', 'S2', 'UE Anglais'): {
        'Anglais': [
            ("« Thank you » se traduit par :", "merci",
             ["bonjour", "au revoir", "s'il vous plaît"], "facile",
             "Thank you signifie merci."),
            ("Le prétérit de « go » est :", "went",
             ["goed", "gone", "going"], "normal",
             "Go est un verbe irrégulier : go, went, gone."),
        ],
    },
    ('L1', 'S2', 'UE Intelligence économique'): {
        'Intelligence économique': [
            ("L'intelligence économique consiste à :",
             "collecter et exploiter l'information pour décider",
             ["espionner", "faire de la publicité", "vendre des données"], "normal",
             "Elle vise à maîtriser l'information stratégique (veille, protection, influence)."),
        ],
    },
    ('L1', 'S2', 'UE Gestion des ressources humaines'): {
        'Gestion des ressources humaines': [
            ("La GRH s'occupe principalement :", "des salariés de l'entreprise",
             ["des clients", "des fournisseurs", "des machines"], "facile",
             "La GRH gère le personnel : recrutement, formation, paie, motivation."),
        ],
    },
    ('L1', 'S2', 'UE Atelier de maintenance'): {
        'Atelier de maintenance': [
            ("Une maintenance préventive est réalisée :", "avant la panne",
             ["après la panne", "uniquement en fin de garantie", "jamais"], "normal",
             "La maintenance préventive anticipe les pannes par des contrôles réguliers."),
        ],
    },
    ('L1', 'S2', 'UE Infographie(Montage vidéo,etc..)'): {
        'Infographie(Montage vidéo,etc..)': [
            ("En infographie, la résolution d'une image se mesure en :", "pixels",
             ["octets", "hertz", "watts"], "facile",
             "La résolution décrit le nombre de pixels d'une image."),
        ],
    },
    ('L1', 'S2', 'UE Outils Bureautiques 2'): {
        'Outils Bureautiques 2': [
            ("Dans PowerPoint, un « masque » permet de :",
             "définir la mise en page commune des diapositives",
             ["créer une animation", "insérer un tableau", "compter les mots"], "normal",
             "Le masque fixe le style de fond appliqué à toutes les diapositives."),
        ],
    },
    ('L1', 'S2', 'UE TECHNIQUE D\'EXPRESSION ET METHODOLOGIE DU TRAVAIL'): {
        "Technique d'expression": [
            ("Une introduction de dissertation doit contenir :",
             "l'annonce du sujet et du plan",
             ["la conclusion", "les références", "les exemples détaillés"], "normal",
             "L'introduction présente le sujet, la problématique et le plan."),
        ],
        'Methodologie de travail': [
            ("Une fiche de lecture sert à :", "résumer et analyser un document",
             ["recopier le document", "remplacer le cours", "remplir du temps"], "normal",
             "La fiche de lecture synthétise l'essentiel et structure l'analyse."),
        ],
    },

    # ============================ L2 S3 ============================
    ('L2', 'S3', 'Mathématiques 4'): {
        'Algèbre': [
            ("La transposée d'une matrice 2×3 est une matrice :", "3×2",
             ["2×3", "2×2", "3×3"], "facile",
             "La transposée inverse les dimensions."),
            ("Une matrice inversible est :", "de déterminant non nul",
             ["de déterminant nul", "carrée uniquement", "symétrique"], "normal",
             "Une matrice est inversible si et seulement si son déterminant est non nul."),
        ],
        'Analyse 3': [
            ("La limite de sin(x)/x quand x → 0 est :", "1",
             ["0", "+∞", "n'existe pas"], "difficile",
             "C'est une limite classique : sin(x)/x tend vers 1 en 0."),
            ("Une fonction dérivable en un point est :", "continue en ce point",
             ["forcément constante", "forcément positive", "discontinue"], "normal",
             "La dérivabilité implique la continuité."),
        ],
    },
    ('L2', 'S3', 'Probabilités et statistique 2'): {
        'Probabilités 2': [
            ("Deux événements sont indépendants si :",
             "P(A ∩ B) = P(A) × P(B)",
             ["P(A ∪ B) = 0", "A = B", "P(A) = P(B)"], "normal",
             "L'indépendance se traduit par le produit des probabilités."),
        ],
        'Statistique 2': [
            ("La variance mesure :", "la dispersion autour de la moyenne",
             ["la valeur centrale", "le nombre de données", "la médiane"], "normal",
             "La variance quantifie l'écart des données par rapport à la moyenne."),
        ],
        'Analyse de données': [
            ("L'analyse en composantes principales (ACP) sert à :",
             "réduire la dimension des données",
             ["augmenter les données", "trier les données", "supprimer la moyenne"], "normal",
             "L'ACP synthétise un grand nombre de variables en quelques composantes."),
        ],
    },
    ('L2', 'S3', 'Comptabilité generale'): {
        'Modèle comptable': [
            ("Le bilan comptable présente :", "l'actif et le passif de l'entreprise",
             ["les recettes et dépenses", "les salaires", "le chiffre d'affaires"], "normal",
             "Le bilan décrit le patrimoine : ce que l'on possède (actif) et ce que l'on doit (passif)."),
            ("L'équilibre du bilan impose :", "actif = passif",
             ["actif > passif", "actif < passif", "recettes = dépenses"], "facile",
             "Le bilan est toujours équilibré : actif = passif."),
        ],
        'Opérations comptables': [
            ("Une facture d'achat se comptabilise au :", "débit du compte fournisseurs concerné",
             ["crédit du compte banque uniquement", "débit du compte client", "crédit du compte capital"], "difficile",
             "L'achat augmente une charge (débit) et la dette fournisseur (crédit)."),
            ("Le journal comptable enregistre les opérations :", "chronologiquement",
             ["par ordre alphabétique", "par montant", "aléatoirement"], "normal",
             "Les écritures sont saisies dans l'ordre chronologique."),
        ],
        'Opérations d\'inventaires': [
            ("Les amortissements concernent :", "les immobilisations",
             ["les stocks de marchandises", "les créances clients", "la trésorerie"], "normal",
             "On amortit les immobilisations (matériel, bâtiments…) sur leur durée de vie."),
            ("Une provision pour dépréciation se constitue :",
             "quand la valeur d'un élément diminue",
             ["quand les ventes augmentent", "chaque mois", "à la clôture uniquement"], "difficile",
             "La provision constate la perte de valeur probable d'un élément d'actif."),
        ],
    },
    ('L2', 'S3', 'Programmation orientée objet'): {
        'Fondements de la POO': [
            ("L'encapsulation consiste à :",
             "protéger les attributs et exposer des méthodes",
             ["hériter des classes", "dupliquer le code", "supprimer les méthodes"], "normal",
             "L'encapsulation cache les données et contrôle l'accès via des méthodes."),
        ],
        'POO en Java': [
            ("En Java, « extends » permet de :", "réaliser l'héritage",
             ["implémenter une interface", "créer un objet", "surcharger une méthode"], "normal",
             "extends établit une relation d'héritage entre classes."),
            ("Le mot-clé « this » fait référence à :", "l'objet courant",
             ["la classe mère", "un objet alloué", "une variable locale"], "difficile",
             "this désigne l'instance sur laquelle la méthode est appelée."),
        ],
        'outils formels pour l\'informatique': [
            ("Un graphe orienté possède :", "des arêtes avec un sens",
             ["des arêtes sans sens", "aucun sommet", "uniquement des boucles"], "facile",
             "Dans un graphe orienté, chaque arête a une direction."),
        ],
    },
    ('L2', 'S3', 'Anglais'): {
        'Anglais': [
            ("« I have been studying » est au :", "present perfect continuous",
             ["simple past", "future", "past perfect"], "difficile",
             "Have been + -ing marque le present perfect continuous."),
            ("« Could you help me ? » est une demande :", "polie",
             ["impérative", "au conditionnel passé", "négative"], "normal",
             "Could exprime une demande polie."),
        ],
    },

    # ============================ L2 S4 ============================
    ('L2', 'S4', 'Mathématiques 5'): {
        'Arithmétique': [
            ("Un nombre premier possède exactement :", "deux diviseurs (1 et lui-même)",
             ["un diviseur", "trois diviseurs", "aucun diviseur"], "facile",
             "Un nombre premier n'a que 1 et lui-même comme diviseurs."),
            ("Le PGCD de 12 et 18 est :", "6",
             ["3", "12", "2"], "normal",
             "Les diviseurs communs de 12 et 18 : 6 est le plus grand."),
        ],
    },
    ('L2', 'S4', 'Données semi-structurées et bases de données'): {
        'Base de données relationnelles': [
            ("Quel langage interroge une base relationnelle ?", "SQL",
             ["HTML", "CSS", "XML seul"], "facile",
             "SQL est le langage standard des bases relationnelles."),
            ("Une clé primaire doit être :", "unique et non nulle",
             ["nullable", "multiple", "optionnelle"], "normal",
             "La clé primaire identifie chaque ligne de façon unique."),
            ("L'opération qui joint deux tables sur une condition est :", "JOIN",
             ["SELECT", "INSERT", "DELETE"], "normal",
             "JOIN combine les lignes de deux tables selon une condition."),
        ],
        'Données semi-structurées': [
            ("Un document JSON est structuré en :", "paires clé-valeur",
             ["tableaux uniquement", "feuilles de calcul", "balises XML uniquement"], "normal",
             "JSON organise les données en paires clé-valeur imbriquées."),
            ("XML sert principalement à :", "échanger des données structurées avec des balises",
             ["stocker des images", "afficher du texte", "compiler du code"], "normal",
             "XML est un format de données à balises pour l'échange."),
        ],
        'base de données et applications': [
            ("Une requête qui modifie des données s'appelle :", "une requête de mise à jour (UPDATE)",
             ["une requête de lecture", "une jointure", "un index"], "normal",
             "UPDATE modifie des enregistrements existants."),
        ],
    },
    ('L2', 'S4', 'Génie logiciel'): {
        'Atelier de Génie Logiciel': [
            ("La méthode Merise est une méthode de :", "conception de systèmes d'information",
             ["compilation", "réseau", "marketing"], "normal",
             "Merise guide la conception des SI (MCD, MLD…)."),
            ("Un MCD (modèle conceptuel de données) représente :",
             "les entités et leurs associations",
             ["les écrans", "le réseau", "les coûts"], "normal",
             "Le MCD décrit les entités et les associations entre elles."),
        ],
        'Initiation au Langage SCALA': [
            ("Scala est un langage qui combine :", "la programmation objet et fonctionnelle",
             ["le web et le réseau", "SQL et XML", "le matériel et le logiciel"], "normal",
             "Scala fusionne les paradigmes objet et fonctionnel."),
        ],
    },
    ('L2', 'S4', 'Initiation Python'): {
        'Application à la cryptographie': [
            ("Le chiffrement de César décale :", "chaque lettre d'un certain rang",
             ["les chiffres", "les mots de passe", "les adresses"], "normal",
             "Le chiffre de César décale chaque lettre de l'alphabet."),
            ("La cryptographie sert à :", "protéger la confidentialité des données",
             ["accélérer le réseau", "réduire la taille", "afficher des images"], "facile",
             "Elle chiffre l'information pour qu'elle soit illisible sans clé."),
        ],
    },
    ('L2', 'S4', 'Programmation sous windows'): {
        'Programmation C#': [
            ("C# est un langage développé par :", "Microsoft",
             ["Oracle", "Apple", "Google"], "facile",
             "C# a été créé par Microsoft pour la plateforme .NET."),
        ],
        'Programmation VBA': [
            ("VBA s'exécute principalement dans :", "les applications Microsoft Office",
             ["le navigateur", "Linux", "le BIOS"], "normal",
             "VBA automatise Excel, Word, Access…"),
        ],
    },
    ('L2', 'S4', 'Programmation web'): {
        'Programmation web': [
            ("HTML sert à :", "structurer le contenu d'une page web",
             ["styliser", "interagir", "stocker en base"], "facile",
             "HTML définit la structure et le contenu de la page."),
            ("CSS permet de :", "mettre en forme la page",
             ["créer la base de données", "compiler le serveur", "écrire les requêtes"], "facile",
             "CSS gère l'apparence (couleurs, marges, polices…)."),
            ("JavaScript s'exécute :", "côté navigateur (et serveur avec Node.js)",
             ["uniquement sur le serveur", "dans la base de données", "dans le BIOS"], "normal",
             "JavaScript s'exécute dans le navigateur, et aussi côté serveur."),
        ],
    },
    ('L2', 'S4', 'Contrôle budgétaire'): {
        'Contrôle budgétaire': [
            ("Un budget prévisionnel compare :", "le prévu et le réalisé",
             ["les clients et les fournisseurs", "l'actif et le passif", "les salaires et les impôts"], "normal",
             "Le contrôle budgétaire suit les écarts entre prévisions et réalisations."),
            ("Un écart défavorable signifie :", "un résultat moins bon que prévu",
             ["un résultat meilleur", "aucune différence", "une erreur de saisie"], "normal",
             "L'écart défavorable dégrade le résultat attendu."),
        ],
    },
    ('L2', 'S4', 'Projet'): {
        'Projet': [
            ("La méthode agile privilégie :", "des itérations courtes avec le client",
             ["un plan figé", "aucun contact client", "une documentation exhaustive"], "difficile",
             "L'agilité découpe le projet en itérations avec retours fréquents."),
        ],
    },

    # ============================ L3 S5 ============================
    ('L3', 'S5', 'ALGORITHMIQUE DES GRAPHES'): {
        'ALGORITHMIQUE DES GRAPHES': [
            ("L'algorithme de Dijkstra calcule :", "les plus courts chemins depuis une source",
             ["l'arbre couvrant maximal", "le tri d'un tableau", "la factorisation"], "difficile",
             "Dijkstra trouve les plus courts chemins dans un graphe pondéré positif."),
            ("Un parcours en largeur (BFS) utilise :", "une file",
             ["une pile", "un tas", "un dictionnaire"], "normal",
             "BFS explore les sommets niveau par niveau avec une file."),
        ],
    },
    ('L3', 'S5', 'BASE DE DONNEES AVANCEES'): {
        'BASE DE DONNEES AVANCEES': [
            ("Une transaction doit respecter les propriétés :", "ACID",
             ["SQL", "JSON", "HTTP"], "difficile",
             "Atomicité, Cohérence, Isolation, Durabilité."),
            ("Un index en base de données sert à :", "accélérer les recherches",
             ["réduire le stockage", "chiffrer les données", "supprimer les doublons"], "normal",
             "L'index accélère l'accès aux lignes."),
        ],
    },
    ('L3', 'S5', 'COMPTABILITE ANALYTIQUE'): {
        'COMPTABILITE ANALYTIQUE': [
            ("La comptabilité analytique calcule :", "les coûts par produit ou activité",
             ["le résultat fiscal", "les impôts", "la trésorerie"], "normal",
             "Elle répartit les charges pour calculer des coûts de revient."),
        ],
    },
    ('L3', 'S5', 'COURS DE PROGRAMMATION'): {
        'COURS DE PROGRAMMATION': [
            ("La récursivité est :", "une fonction qui s'appelle elle-même",
             ["une boucle infinie", "un type de variable", "un fichier"], "facile",
             "Une fonction récursive s'appelle elle-même sur un cas plus simple."),
            ("Un pointeur contient :", "l'adresse mémoire d'une variable",
             ["la valeur de la variable", "un fichier", "une classe"], "difficile",
             "Le pointeur stocke l'adresse d'une zone mémoire."),
        ],
    },
    ('L3', 'S5', 'PROGRAMMATION LINEAIRE'): {
        'PROGRAMMATION LINEAIRE': [
            ("La programmation linéaire optimise :", "une fonction objectif sous contraintes linéaires",
             ["une base de données", "un réseau", "une interface"], "normal",
             "Elle maximise/minimise une fonction linéaire sous des contraintes linéaires."),
            ("La méthode du simplexe est utilisée pour :", "résoudre des problèmes de programmation linéaire",
             ["trier des données", "chiffrer", "compiler"], "difficile",
             "Le simplexe est l'algorithme classique de la PL."),
        ],
    },
    ('L3', 'S5', 'PROGRAMMATION WEB CLIENT'): {
        'PROGRAMMATION WEB CLIENT': [
            ("Le DOM est :", "la représentation en mémoire de la page web",
             ["un langage", "un serveur", "une base de données"], "difficile",
             "Le DOM (Document Object Model) est l'arbre de la page manipulable en JS."),
            ("AJAX permet de :", "échanger des données sans recharger la page",
             ["créer des styles", "compiler le serveur", "stocker en base"], "normal",
             "AJAX fait des requêtes asynchrones vers le serveur."),
        ],
    },
    ('L3', 'S5', 'SYSTEME D\'EXPLOITATION'): {
        "SYSTEME D'EXPLOITATION": [
            ("Le rôle principal d'un système d'exploitation est :",
             "gérer les ressources matérielles et les processus",
             ["compiler le code", "créer des sites web", "stocker des documents"], "normal",
             "L'OS orchestre le matériel, la mémoire et les processus."),
            ("Un processus est :", "un programme en cours d'exécution",
             ["un fichier", "une adresse mémoire", "un périphérique"], "facile",
             "Le processus est l'exécution active d'un programme."),
        ],
    },
    ('L3', 'S5', 'UNIX_C'): {
        'UNIX_C': [
            ("Le shell UNIX est :", "l'interpréteur de commandes",
             ["le noyau", "un compilateur", "un éditeur"], "facile",
             "Le shell exécute les commandes de l'utilisateur."),
            ("La commande qui liste les fichiers est :", "ls",
             ["cd", "mkdir", "pwd"], "facile",
             "ls affiche le contenu du répertoire."),
        ],
    },

    # ============================ L3 S6 ============================
    ('L3', 'S6', 'ANALYSE DE DONNEES'): {
        'ANALYSE DE DONNEES': [
            ("La régression linéaire modélise :", "la relation entre une variable et une autre",
             ["la variance", "un réseau", "un graphe"], "normal",
             "Elle ajuste une droite aux données pour prédire une variable."),
        ],
    },
    ('L3', 'S6', 'ANGLAIS'): {
        'ANGLAIS': [
            ("« Nevertheless » signifie :", "néanmoins",
             ["cependant pas", "de plus", "enfin"], "normal",
             "Nevertheless marque l'opposition : néanmoins."),
        ],
    },
    ('L3', 'S6', 'ENVIRONNEMENT JURIDIQUE'): {
        'ENVIRONNEMENT JURIDIQUE': [
            ("Le droit de l'informatique couvre :", "la protection des données et les contrats informatiques",
             ["les impôts uniquement", "le droit pénal", "la fiscalité"], "normal",
             "Il régit les données personnelles, les logiciels, les contrats."),
        ],
    },
    ('L3', 'S6', 'FILE D\'ATTENTE ET GESTION DE STOCKS'): {
        "FILE D'ATTENTE ET GESTION DE STOCKS": [
            ("La loi de Little relie :", "le nombre de clients, le débit et le temps d'attente",
             ["les stocks et les ventes", "les salaires et les coûts", "l'actif et le passif"], "difficile",
             "L = λ × W : nombre moyen de clients = débit × temps moyen."),
            ("Le point de commande déclenche :", "une réapprovisionnement quand le stock baisse",
             ["la clôture des comptes", "le paiement des salaires", "la fin de l'exercice"], "normal",
             "Le point de commande est le niveau de stock qui déclenche la commande."),
        ],
    },
    ('L3', 'S6', 'GENIE LOGICIEL JAVA'): {
        'GENIE LOGICIEL JAVA': [
            ("JUnit sert à :", "écrire et exécuter des tests unitaires",
             ["déployer des serveurs", "styliser", "gérer les transactions"], "normal",
             "JUnit teste des unités de code (méthodes, classes)."),
        ],
    },
    ('L3', 'S6', 'GESTION FINANCIERE'): {
        'GESTION FINANCIERE': [
            ("La VAN (valeur actuelle nette) mesure :", "la rentabilité d'un investissement",
             ["le chiffre d'affaires", "le nombre de salariés", "la trésorerie"], "difficile",
             "La VAN actualise les flux futurs pour juger un projet."),
        ],
    },
    ('L3', 'S6', 'INTERNET-INTRANET'): {
        'INTERNET-INTRANET': [
            ("Un intranet est :", "un réseau interne à l'entreprise utilisant les technologies web",
             ["un réseau public", "un fournisseur d'accès", "un navigateur"], "normal",
             "L'intranet reprend les outils web en accès restreint à l'entreprise."),
            ("Un pare-feu (firewall) :", "filtre le trafic réseau",
             ["accélère la connexion", "stocke les pages", "compresse les fichiers"], "facile",
             "Le pare-feu contrôle les flux entrants et sortants."),
        ],
    },
    ('L3', 'S6', 'PROGRAMMATION D\'APPLICATION'): {
        "PROGRAMMATION D'APPLICATION": [
            ("Une API REST utilise les méthodes :", "GET, POST, PUT, DELETE",
             ["SELECT, INSERT, UPDATE", "OPEN, CLOSE", "READ, WRITE"], "normal",
             "REST manipule des ressources via ces verbes HTTP."),
        ],
    },
    ('L3', 'S6', 'RESEAU'): {
        'RESEAU': [
            ("L'adresse IP identifie :", "un équipement sur le réseau",
             ["un fichier", "un utilisateur", "une page web"], "facile",
             "L'IP localise chaque machine sur le réseau."),
            ("Le protocole TCP garantit :", "la fiabilité de la transmission",
             ["la vitesse maximale", "le chiffrement", "l'anonymat"], "normal",
             "TCP assure la livraison fiable des paquets."),
        ],
    },
    ('L3', 'S6', 'THEORIE DU LANGUAGE'): {
        'THEORIE DU LANGUAGE': [
            ("Une grammaire formelle sert à :", "définir un langage",
             ["compiler des images", "créer des bases", "gérer la mémoire"], "normal",
             "La grammaire décrit la syntaxe d'un langage."),
            ("Un automate à états finis reconnaît :", "les langages réguliers",
             ["les langages contextuels", "tous les langages", "les langages naturels"], "difficile",
             "Les automates finis caractérisent les langages réguliers."),
        ],
    },
    ('L3', 'S6', 'UML'): {
        'UML': [
            ("Le diagramme de classes représente :", "la structure statique du système",
             ["les échanges de messages", "les cas d'utilisation", "le déploiement"], "normal",
             "Le diagramme de classes montre les classes et leurs relations."),
            ("Un cas d'utilisation décrit :", "une interaction entre l'acteur et le système",
             ["une table", "un serveur", "un algorithme"], "normal",
             "Le cas d'utilisation capture un besoin fonctionnel vu par l'acteur."),
        ],
    },
}


class Command(BaseCommand):
    help = 'Seed de questions de quiz pour L1/L2/L3 (par UE et ECUE, idempotent).'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Recrée les questions même si déjà présentes.')

    def handle(self, *args, **options):
        force = options['force']
        created = 0
        skipped = 0

        for (level, semester, ue_code), ecues in BANK.items():
            ue = UE.objects.filter(code=ue_code, level=level, semester=semester).first()
            if not ue:
                self.stdout.write(f'[SKIP] UE introuvable : {ue_code} {level} {semester}')
                continue
            for ecue_name, questions in ecues.items():
                ecue = ECUE.objects.filter(ue=ue, name=ecue_name).first()
                if not ecue:
                    self.stdout.write(f'[SKIP] ECUE introuvable : {ue_code} / {ecue_name}')
                    continue
                if not force and ecue.questions.exists():
                    skipped += 1
                    continue
                if force:
                    ecue.questions.all().delete()
                for args_q in questions:
                    q(ue, ecue, *args_q)
                    created += 1
                self.stdout.write(f'[OK] {len(questions)} questions — {ue_code} / {ecue_name}')

        self.stdout.write(self.style.SUCCESS(
            f'[SUMMARY] {created} questions créées, {skipped} ECUEs déjà seedées (ignorées)'
        ))
