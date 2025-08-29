Dernière mise à jour : 12/05/2025
# Utilisation des Scripts d'Initialisation des Données

Ce document explique comment utiliser les scripts Python fournis pour initialiser la base de données de votre projet Django avec des données de test. Ces scripts sont conçus pour peupler la base de données avec des informations essentielles pour le développement et les tests.

## Scripts Disponibles

Les scripts suivants sont disponibles pour initialiser différentes parties de l'application :

* `init_all_data.py` : Ce script exécute tous les autres scripts d'initialisation pour peupler la base de données entière. C'est le moyen le plus simple de tout initialiser.
* `init_journal_data.py` : Initialise les données des journaux (MSA) pour l'application `journal`.
* `init_services_data.py` : Initialise les données des services pour l'application `services`.
* `init_competences_data.py` : Initialise les données des compétences pour l'application `competences`.
* `init_commune_data.py` : Initialise les données de communes pour l'application `conseil_communautaire`.
* `init_membre_data.py` : Initialise les données de membres pour l'application `conseil_communautaire`.
* `init_elus_data.py` : Initialise les données pour les élus de l'application `bureau_communautaire`.
* `init_commission_data.py` : Initialise les données pour les commissions de l'application `bureau_communautaire`.
* `init_cr_data.py` : Initialise les données pour les comptes rendus de l'application `comptes_rendus`.

## Prérequis

Avant d'exécuter les scripts, assurez-vous que :

1.  **Votre environnement Django est configuré :** Vous devez avoir Python installé, ainsi que les dépendances de votre projet Django installées (vous pouvez les installer avec `pip install -r requirements.txt`).
2.  **La base de données est configurée :** Votre fichier `settings.py` doit être correctement configuré pour se connecter à une base de données.  Vous pouvez avoir besoin de créer la base de données avant d'exécuter les scripts.
3.  **Les migrations sont appliquées :** Exécutez `python manage.py migrate` pour créer les tables de la base de données en fonction de vos modèles Django.

## Comment Exécuter les Scripts

Les scripts d'initialisation sont des "management commands" Django.  Vous pouvez les exécuter à partir de la ligne de commande en utilisant `python manage.py <nom_du_script>`.

**Exemples :**

* Pour exécuter le script qui initialise les données des journaux :

    ```bash
    python manage.py init_journal_data
    ```

* Pour exécuter le script qui initialise les données des communes :

    ```bash
    python manage.py init_commune_data
    ```

* Pour exécuter le script qui initialise **toutes** les données :

    ```bash
    python manage.py init_all_data
    ```

## Comprendre ce que font les Scripts

Chaque script effectue généralement les opérations suivantes :

1.  **Importe les modèles nécessaires :** Le script importe les classes de modèle Django pour l'application qu'il doit peupler.
2.  **Définit les données à créer :** Le script définit une liste de dictionnaires ou une autre structure de données qui représente les objets que vous souhaitez créer dans la base de données.  Cela inclut les valeurs des champs pour chaque objet.
3.  **Crée les objets dans la base de données :** Le script itère sur les données définies et utilise la méthode `objects.create()` ou `objects.get_or_create()` des modèles Django pour ajouter les objets à la base de données.
4.  **Gère les fichiers (si nécessaire) :** Si le modèle inclut des champs de fichiers (comme des images ou des documents), le script ouvrira les fichiers et les enregistrera dans le champ de fichier du modèle.

**Points Importants :**

* **`get_or_create()` :** Beaucoup de scripts utilisent `objects.get_or_create()`.  Cela signifie que si un objet avec les mêmes valeurs pour certains champs existe déjà dans la base de données, le script ne créera pas un nouvel objet.  Au lieu de cela, il récupérera l'objet existant.  C'est utile pour éviter de créer des doublons si vous exécutez le script plusieurs fois.
* **Chemins de fichiers :** Les scripts qui gèrent les fichiers (comme `init_commune_data.py`, `init_journal_data.py` et `init_elus_data.py`) utilisent désormais des chemins relatifs, car les fichiers nécessaires sont situés dans le même dossier que les scripts. Vous n'avez donc plus besoin de modifier les chemins de fichiers.
* **Dépendances entre les scripts :** Le script `init_all_data.py` appelle d'autres scripts.  Cela signifie que l'ordre d'exécution est important pour garantir que les données dépendantes sont créées en premier. Par exemple, les communes doivent être créées avant les membres du conseil.

## Personnalisation

Vous pouvez modifier les scripts pour :

* **Ajouter plus de données :** Simplement ajouter plus d'éléments aux listes de données.
* **Modifier les données existantes :** Changer les valeurs dans les dictionnaires de données.
* **Ajouter de nouvelles fonctionnalités :** Par exemple, vous pourriez modifier les scripts pour créer des utilisateurs ou des groupes.

**Attention :** Soyez prudent lorsque vous modifiez les scripts, surtout si vous travaillez sur une base de données existante. Vous pourriez accidentellement modifier ou supprimer des données importantes.  Il est recommandé de travailler sur une base de données de développement ou de test.

Ce document devrait vous aider à démarrer avec l'utilisation des scripts d'initialisation des données. Si vous avez des questions, n'hésitez pas à consulter le code des scripts ou à demander de l'aide.