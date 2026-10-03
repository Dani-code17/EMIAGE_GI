# Contribuer à E-MIAGE-GI

Merci de vouloir améliorer la plateforme ! Ce guide explique **comment travailler**
sur le projet sans risquer de casser le site en ligne.

## Règle d'or

Le site en production (https://emiage-gi.onrender.com) est **déployé manuellement**.
Aucune modification n'est mise en ligne automatiquement : vos changements sont donc
examinés avant publication. **Ne travaillez jamais directement sur `main`.**

## Périmètre de la Journée d'Intégration (JI)

Vous êtes responsable de la **page Journée d'Intégration**. Les fichiers concernés :

| Fichier | Contenu |
|---|---|
| `core/templates/core/journee_integration.html` | La page publique de la JI |
| `core/models.py` → classes `JIEdition`, `JIPayment`, `JIPhoto` | Champs de données de la JI |
| `core/admin.py` → `JIEditionAdmin`, `JIPaymentAdmin`, `JIPhotoAdmin` | Interface d'administration |

> ⚠️ Merci de **ne pas modifier** les autres parties (documents, UE/ECUE, quiz,
> étudiants, comptes, `settings.py`, `requirements.txt`) sans en parler d'abord :
> elles sont utilisées par tout le site.

## Mise en place (une seule fois)

```bash
git clone https://github.com/Dani-code17/EMIAGE_GI.git
cd EMIAGE_GI
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Le site est alors visible sur http://127.0.0.1:8000/ (avec la base SQLite locale).

## Travailler sur une modification

```bash
# 1. Se placer sur main à jour, puis créer une branche dédiée
git checkout main
git pull
git checkout -b ji/ma-modification      # nommez clairement votre branche

# 2. Modifier les fichiers, puis tester en local
python manage.py check
python manage.py test core

# 3. Enregistrer et envoyer votre branche
git add -A
git commit -m "JI: description claire de ma modification"
git push origin ji/ma-modification
```

## Ouvrir une Pull Request

1. Sur GitHub, ouvrez une **Pull Request** de votre branche vers `main`.
2. Décrivez en quelques lignes **ce que vous avez changé et pourquoi**.
3. Ajoutez une **capture d'écran** si c'est visuel (avant / après).
4. La Pull Request est relue avant fusion, puis le déploiement est déclenché.

Une fois fusionnée, votre modification apparaît sur le site après publication.

## Bonnes pratiques

- **Testez avant d'envoyer** : `python manage.py check` puis `python manage.py test core`
  doivent passer sans erreur.
- **Petites Pull Requests** : une modification = une PR, c'est plus facile à relire.
- **Nommez clairement** vos branches (`ji/affiche-2026`, `ji/fix-paiement`…).
- **N'ajoutez jamais de secret** (mot de passe, clé API, fichier `.env`) dans le
  dépôt : utilisez les variables d'environnement.
- Les photos : préférez une **URL** (lien permanent) à un fichier téléversé, car
  l'hébergement gratuit ne conserve pas les fichiers envoyés.

## Contenu de la JI (sans toucher au code)

Pour simplement **mettre à jour les informations** (date, lieu, prix, programme,
numéros de paiement, photos), pas besoin de code : connectez-vous à
`/admin/` avec le compte du comité — vous n'y voyez que la section JI.

## Besoin d'aide ?

Écrivez à **metydatech@gmail.com**.
