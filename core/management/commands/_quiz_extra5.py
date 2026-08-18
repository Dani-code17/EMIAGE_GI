"""Cinquième question pour les ECUEs qui n'en avaient que 4."""
EXTRA_QUESTIONS_5 = {
    ('L1', 'S2', 'UE Atelier de maintenance'): {
        'Atelier de maintenance': [
            ("Le remplacement préventif d'une pièce usée relève de :", "la maintenance préventive",
             ["la maintenance corrective", "la maintenance prédictive", "aucune maintenance"], "normal",
             "Remplacer avant la panne est de la maintenance préventive."),
        ],
    },
    ('L1', 'S1', 'UE ECONOMIE'): {
        'Économie 2': [
            ("Le taux de chômage se calcule :", "chômeurs / population active",
             ["chômeurs / population totale", "population active / chômeurs", "chômeurs × population"], "normal",
             "Taux de chômage = chômeurs ÷ actifs."),
        ],
    },
    ('L1', 'S2', 'UE Gestion des ressources humaines'): {
        'Gestion des ressources humaines': [
            ("La paie comprend notamment :", "le salaire brut et les cotisations",
             ["les achats", "les ventes", "les impôts de l'entreprise"], "normal",
             "La paie détaille salaires, cotisations et net à payer."),
        ],
    },
    ('L1', 'S2', 'UE Infographie(Montage vidéo,etc..)'): {
        'Infographie(Montage vidéo,etc..)': [
            ("Le format vectoriel (SVG) est idéal pour :", "les logos et icônes redimensionnables",
             ["les photos", "les vidéos", "le son"], "normal",
             "Le vectoriel s'agrandit sans perte de qualité."),
        ],
    },
    ('L1', 'S2', 'UE Intelligence économique'): {
        'Intelligence économique': [
            ("L'espionnage industriel est :", "illicite et sanctionné",
             ["autorisé", "recommandé", "bénin"], "normal",
             "L'espionnage industriel est une pratique illégale."),
        ],
    },
    ('L1', 'S2', 'UE MATHEMATIQUES 3'): {
        'Géometrie': [
            ("Le périmètre d'un cercle de rayon r est :", "2πr",
             ["πr²", "πr", "4πr"], "facile", "Périmètre = 2πr."),
        ],
        'Espaces vectoriels': [
            ("Le vecteur nul appartient à :", "tout sous-espace vectoriel",
             ["aucun sous-espace", "un seul sous-espace", "uniquement à R"], "difficile",
             "Tout sous-espace contient le vecteur nul."),
        ],
    },
    ('L1', 'S2', 'UE Outils Bureautiques 2'): {
        'Outils Bureautiques 2': [
            ("Une formule Excel « =SOMME(B2:B10) » additionne :", "les cellules B2 à B10",
             ["les colonnes A à C", "les feuilles", "les lignes 2 à 10 de A"], "facile",
             "La plage B2:B10 est additionnée."),
        ],
    },
    ('L1', 'S2', 'UE PROBABILITES ET STATISTIQUE 1'): {
        'Langage R': [
            ("La commande « plot(x, y) » dans R :", "crée un graphique de points",
             ["calcule la moyenne", "importe un fichier", "supprime des données"], "facile",
             "plot() trace un nuage de points."),
        ],
    },
    ('L1', 'S2', 'UE TECHNIQUE D\'EXPRESSION ET METHODOLOGIE DU TRAVAIL'): {
        'Methodologie de travail': [
            ("Réviser de façon espacée (jours différents) :", "améliore la mémorisation",
             ["n'a aucun effet", "diminue la mémoire", "est interdit"], "normal",
             "L'espacement des révisions renforce la mémoire."),
        ],
        "Technique d'expression": [
            ("Une argumentation efficace s'appuie sur :", "des arguments et des exemples",
             ["des opinions sans preuve", "la répétition", "le silence"], "normal",
             "Argumenter = justifier avec des preuves et exemples."),
        ],
    },
    ('L2', 'S4', 'Données semi-structurées et bases de données'): {
        'base de données et applications': [
            ("Une clé étrangère établit :", "un lien entre deux tables",
             ["un index", "une vue", "un trigger"], "facile",
             "La clé étrangère référence une clé primaire d'une autre table."),
        ],
    },
    ('L2', 'S4', 'Génie logiciel'): {
        'Initiation au Langage SCALA': [
            ("En Scala, « map » applique :", "une fonction à chaque élément d'une collection",
             ["une condition", "un tri", "une jointure"], "normal",
             "map transforme chaque élément de la collection."),
        ],
    },
    ('L2', 'S3', 'Probabilités et statistique 2'): {
        'Probabilités 2': [
            ("La loi binomiale modélise :", "le nombre de succès dans n essais indépendants",
             ["la durée de vie", "la taille", "la moyenne"], "normal",
             "B(n, p) compte les succès sur n essais."),
        ],
        'Statistique 2': [
            ("Le test d'hypothèse permet de :", "valider ou rejeter une hypothèse statistiquement",
             ["calculer une moyenne", "trier", "afficher"], "normal",
             "Le test décide avec un risque d'erreur contrôlé."),
        ],
        'Analyse de données': [
            ("Le clustering (classification non supervisée) regroupe :", "des observations similaires",
             ["des variables identiques", "des erreurs", "des fichiers"], "normal",
             "Le clustering trouve des groupes dans les données."),
        ],
    },
    ('L2', 'S3', 'Programmation orientée objet'): {
        'Fondements de la POO': [
            ("Le polymorphisme permet :", "une même interface, des comportements différents",
             ["une seule classe", "aucune méthode", "du code identique"], "normal",
             "Le polymorphisme adapte le comportement selon l'objet."),
        ],
        'outils formels pour l\'informatique': [
            ("Une preuve par récurrence comporte :", "une initialisation et une hérédité",
             ["une conclusion seule", "un contre-exemple", "un graphique"], "normal",
             "La récurrence prouve pour tout n par initialisation + hérédité."),
        ],
    },
    ('L2', 'S4', 'Programmation sous windows'): {
        'Programmation VBA': [
            ("En VBA, « Range(\"A1\").Value » accède à :", "la valeur de la cellule A1",
             ["la formule de B2", "la feuille", "le classeur"], "facile",
             "Range(\"A1\") cible la cellule A1."),
        ],
        'Programmation C#': [
            ("En C#, « foreach » sert à :", "parcourir une collection",
             ["déclarer une variable", "compiler", "définir une classe"], "facile",
             "foreach itère sur les éléments d'une collection."),
        ],
    },
    ('L3', 'S6', 'ANALYSE DE DONNEES'): {
        'ANALYSE DE DONNEES': [
            ("Le sur-apprentissage (overfitting) :", "le modèle colle trop aux données d'entraînement",
             ["le modèle généralise bien", "le modèle est trop simple", "aucun risque"], "difficile",
             "L'overfitting nuit à la généralisation."),
        ],
    },
    ('L3', 'S6', 'ANGLAIS'): {
        'ANGLAIS': [
            ("« Thereby » signifie :", "ainsi / de ce fait",
             ["cependant", "bien que", "par ailleurs"], "difficile",
             "Thereby introduit une conséquence logique."),
        ],
    },
    ('L3', 'S5', 'COMPTABILITE ANALYTIQUE'): {
        'COMPTABILITE ANALYTIQUE': [
            ("Les charges indirectes sont :", "réparties entre plusieurs produits",
             ["directement affectées à un produit", "nulles", "toujours variables"], "normal",
             "Les charges indirectes nécessitent une répartition (clés)."),
        ],
    },
    ('L3', 'S6', 'ENVIRONNEMENT JURIDIQUE'): {
        'ENVIRONNEMENT JURIDIQUE': [
            ("Une licence logicielle open source permet :", "d'utiliser et souvent modifier le code",
             ["de voler le code", "d'interdire toute utilisation", "de breveter"], "normal",
             "Les licences open source (GPL, MIT…) autorisent l'usage et la modification."),
        ],
    },
    ('L3', 'S6', 'GENIE LOGICIEL JAVA'): {
        'GENIE LOGICIEL JAVA': [
            ("L'annotation @Test (JUnit) marque :", "une méthode de test",
             ["une classe de production", "un bug", "une variable"], "normal",
             "@Test identifie les méthodes exécutées par JUnit."),
        ],
    },
    ('L3', 'S6', 'GESTION FINANCIERE'): {
        'GESTION FINANCIERE': [
            ("L'actualisation consiste à :", "ramener des flux futurs à leur valeur actuelle",
             ["augmenter les prix", "supprimer des flux", "calculer les salaires"], "difficile",
             "L'actualisation applique un taux pour comparer les flux dans le temps."),
        ],
    },
    ('L3', 'S6', 'PROGRAMMATION D\'APPLICATION'): {
        "PROGRAMMATION D'APPLICATION": [
            ("Le pattern MVC sépare :", "le modèle, la vue et le contrôleur",
             ["le client et le serveur", "le code et la base", "le HTML et le CSS"], "normal",
             "MVC organise l'application en trois couches."),
        ],
    },
}
