# Documentation des Tests Django

*Dernière mise à jour : 13/05/2025*

Ce document fournit une vue d'ensemble de la manière dont les tests sont structurés et utilisés dans ce projet Django. Il explique le but des tests, comment ils sont organisés, et comment les exécuter.

## Table des Matières

1. [Objectifs des Tests](#objectifs-des-tests)
2. [Organisation des Tests](#organisation-des-tests)
3. [Types de Tests](#types-de-tests)
4. [Exemples de Code et Explications](#exemples-de-code-et-explications)
5. [Comment Exécuter les Tests](#comment-exécuter-les-tests)
6. [Nouveaux Tests](#nouveaux-tests)

## Objectifs des Tests

Les tests automatisés sont cruciaux pour assurer la qualité et la fiabilité de l'application. Ils permettent de :

* **Vérifier le bon fonctionnement des fonctionnalités :** S'assurer que chaque partie du code se comporte comme prévu.
* **Prévenir les régressions :** Détecter si de nouvelles modifications cassent des fonctionnalités existantes.
* **Faciliter la refactorisation :** Permettre de modifier le code en toute confiance, sachant que les tests valideront les changements.
* **Documenter le code :** Les tests servent aussi de documentation, montrant comment le code est censé être utilisé.

## Organisation des Tests

Les tests sont organisés en modules Python, généralement situés dans des fichiers `tests.py` au sein de chaque application Django.  

**Structure Générale :**

* `tests.py` (ou fichiers de tests multiples)
    * `TestCase` classes
        * `test_...` methods (chaque méthode teste une fonctionnalité spécifique)

**Principales Classes de Test :**

* `django.test.TestCase` :  La classe de base pour les tests Django. Elle s'occupe de la création et de la suppression de la base de données de test. Elle est utilisée pour tester les modèles, les vues, les formulaires, etc.
* `django.test.Client` :  Un client HTTP simulé qui permet de faire des requêtes aux vues Django (GET, POST, etc.) sans démarrer de serveur web.
* `django.test.override_settings` : Un décorateur ou un gestionnaire de contexte pour modifier temporairement les paramètres de Django (par exemple, `MEDIA_ROOT` pour les tests de fichiers).
* `django.contrib.auth.get_user_model` :  Une fonction pour récupérer le modèle d'utilisateur personnalisé de Django.
* `django.urls.reverse` :  Une fonction pour construire les URLs à partir des noms de vues.

## Types de Tests

* **Tests de Vues :**
    *     Vérifient que les vues renvoient les bons codes de statut HTTP (200, 302, etc.).
    *     Vérifient que les vues utilisent les bons templates.
    *     Vérifient que les données correctes sont passées au contexte des templates.
    *     Testent les redirections après les soumissions de formulaires.
* **Tests de Modèles :**
    *     Vérifient que les modèles peuvent être créés et récupérés correctement.
    *     Vérifient les contraintes de champs (par exemple, `unique=True`, `null=False`, `blank=False`).
    *     Testent les méthodes personnalisées des modèles.
* **Tests de Formulaires :**
    *     Vérifient que les formulaires valident correctement les données.
    *     Vérifient que les formulaires affichent les erreurs appropriées pour les données invalides.
* **Tests de Fichiers Uploadés :**
    *     Utilisent `django.core.files.uploadedfile.SimpleUploadedFile` pour simuler les fichiers uploadés.
    *     Testent que les fichiers sont correctement enregistrés et traités.
    *     Utilisent `override_settings(MEDIA_ROOT='test_media...')` pour isoler les fichiers de test.
    *     Gèrent la création et la suppression des répertoires de médias de test.
* **Tests d'Authentification :**
    *     Utilisent `django.contrib.auth.get_user_model` pour créer et manipuler les utilisateurs.
    *     Testent la connexion et la déconnexion des utilisateurs.
    *     Testent les vues protégées par les décorateurs `@login_required` et `@user_passes_test`.

## Exemples de Code et Explications

**1. Test d'une Vue (Semestriel):**

```python
from django.test import TestCase, Client
from django.urls import reverse
from .models import SemestrielPage

User = get_user_model()
MEDIA_ROOT = 'test_media_semestriel'


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SemestrielPageViewTestCase(TestCase):
    # Méthode de configuration exécutée avant chaque test
    def setUp(self):
        self.client = Client()  # Client de test pour simuler des requêtes HTTP
        self.semestriel_url = reverse('semestriels:semestriel')  # URL de la vue semestriel
        self.today = timezone.now().date()

    # Méthode de nettoyage exécutée après chaque test
    def tearDown(self):
        SemestrielPage.objects.all().delete()
        Event.objects.all().delete()
        if os.path.exists(MEDIA_ROOT):
            shutil.rmtree(MEDIA_ROOT)

    # Test de la vue semestriel (GET request)
    def test_semestriel_view_get_view(self):
        """
        Test l'affichage de la page semestriel (GET request).

        Méthode de test pour vérifier l'affichage de la vue semestrielle via une requête GET.

        Cette méthode effectue les vérifications suivantes :
        - Vérifie que la réponse HTTP a un code de statut 200 (succès).
        - Vérifie que le template utilisé pour la réponse est 'semestriel/semestriel.html'.
        - Vérifie que le contexte de la réponse contient les clés suivantes :
            - 'content' : Contenu principal de la page.
            - 'incoming_events' : Événements à venir affichés sur la page.
            - 'passed_events' : Événements passés affichés sur la page.
        """
        response = self.client.get(self.semestriel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'semestriel/semestriel.html')
        self.assertIn('content', response.context)
        self.assertIn('incoming_events', response.context)
        self.assertIn('passed_events', response.context)

    # Test de la vue semestriel (POST request)
    def test_semestriel_view_no_content(self):
        """
        Test l'affichage de la page semestriel sans contenu.

        Ce test vérifie que la vue semestriel s'affiche correctement même lorsqu'il n'y a pas de contenu dans la base de données.
        Il s'assure que :
        - Le code de statut HTTP de la réponse est 200 (succès).
        - Le bon template est utilisé pour rendre la page.
        - Les clés attendues ('content', 'incoming_events', 'passed_events') sont présentes dans le contexte de la réponse.
        """
        # Effectue une requête GET sur l'URL de la vue semestriel
        response = self.client.get(self.semestriel_url)
        
        # Vérifie que le code de statut HTTP est 200 (succès)
        self.assertEqual(response.status_code, 200)
        
        # Vérifie que le template utilisé est 'semestriel/semestriel.html'
        self.assertTemplateUsed(response, 'semestriel/semestriel.html')
        
        # Vérifie que les clés 'content', 'incoming_events', et 'passed_events' sont présentes dans le contexte de la réponse
        self.assertIn('content', response.context)
        self.assertIn('incoming_events', response.context)
        self.assertIn('passed_events', response.context)

## Comment Exécuter les Tests

Pour exécuter les tests Django, utilisez la commande `python manage.py test`. Cette commande découvrira et exécutera tous les tests définis dans les fichiers `tests.py` de vos applications Django.

**Commandes utiles :**

* `python manage.py test` : Exécute tous les tests de toutes les applications du projet.  C'est la commande la plus générale.
* `python manage.py test <app_label>` : Exécute les tests d'une application spécifique. Par exemple, pour exécuter uniquement les tests de l'application `journal`, utilisez : `python manage.py test journal`
* `python manage.py test <app_label>.<TestCaseClass>` : Exécute les tests d'une classe de test spécifique au sein d'une application.  Par exemple : `python manage.py test journal.JournalModelTest`
* `python manage.py test <app_label>.<TestCaseClass>.test_method` : Exécute une méthode de test spécifique. Par exemple : `python manage.py test journal.JournalModelTest.test_journal_creation`
* `python manage.py test --verbosity=2` : Affiche un niveau de détail plus élevé dans les résultats des tests.  Cela peut être utile pour déboguer les échecs de tests.  Les valeurs de `verbosity` peuvent être 0 (silencieux), 1 (par défaut), ou 2 (verbeux).
* `python manage.py test --failfast` : Arrête l'exécution des tests dès qu'un test échoue.  Cela peut vous faire gagner du temps si vous avez beaucoup de tests et que vous voulez corriger la première erreur rapidement.
* `python manage.py test --settings=myproject.test_settings` :  Utilise un fichier de paramètres Django spécifique pour l'exécution des tests.  C'est utile si vous avez des paramètres différents pour le développement, la production et les tests.

**Interprétation des Résultats des Tests :**

Lorsque vous exécutez les tests, Django affiche des informations sur la progression et les résultats.  Voici les éléments clés à comprendre :

* **`OK` :** Indique qu'un test a réussi.
* **`FAIL` :** Indique qu'un test a échoué.  Django fournira généralement une trace d'erreur (traceback) qui indique la ligne de code où l'assertion a échoué et la raison de l'échec.
* **`ERROR` :** Indique qu'une erreur inattendue s'est produite lors de l'exécution du test (par exemple, une exception non gérée).  Là encore, Django fournira une trace d'erreur.
* **`SKIPPED` ou `s` :** Indique qu'un test a été intentionnellement ignoré.  Vous pouvez utiliser le décorateur `@unittest.skip('raison')` pour sauter un test.
* **Nombre de tests exécutés :** Django affiche le nombre total de tests exécutés.
* **Temps d'exécution :** Django indique le temps total nécessaire pour exécuter les tests.

**Exemple de Sortie sans erreur:**

```plaintext	
PS C:\Users\ethan\Documents\CCSA\CCSA> python .\manage.py test

......................................................
----------------------------------------------------------------------
Ran 54 tests in 21.740s

OK
Destroying test database for alias 'default'...
```

**Exemple de Sortie avec erreur:**

```plaintext	
PS C:\Users\ethan\Documents\CCSA\CCSA> python manage.py test --failfast .\conseil_communautaire\

..F
======================================================================
FAIL: test_delete_cancel_conseil_membre_view (conseil_communautaire.tests.ConseilMembreViewsTestCase.test_delete_cancel_conseil_membre_view)
Teste la vue de suppression de Conseil Membre avec annulation
----------------------------------------------------------------------
Traceback (most recent call last):
  File "C:\Users\ethan\Documents\CCSA\CCSA\conseil_communautaire\tests.py", line 472, in test_delete_cancel_conseil_membre_view
    self.assertTrue(ConseilMembre.objects.filter(first_name="Jane").exists())
AssertionError: False is not true

----------------------------------------------------------------------
Ran 3 tests in 1.306s

FAILED (failures=1)
Destroying test database for alias 'default'...
```

## Nouveaux Tests

### Tests Ajoutés le 13/05/2025

- Tests de validation des formulaires d'administration
- Tests de compatibilité avec le mode sombre
- Tests de performance des requêtes de base de données
- Tests de sécurité des routes protégées
- Tests d'accessibilité RGAA 4.1

### Exemple de Nouveau Test

```python
def test_dark_mode_compatibility(self):
    """
    Test la compatibilité avec le mode sombre.
    
    Vérifie que :
    - Les classes CSS dark sont correctement appliquées
    - Le contraste des couleurs est suffisant
    - Les images ont des alternatives en mode sombre
    """
    response = self.client.get(self.url)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'dark-mode')
    self.assertContains(response, 'data-theme="dark"')
```