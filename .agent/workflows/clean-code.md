---
description: Agent spécialisé Clean Code avec correction automatique pylint/flake8 sans casser le code
---

# Agent Clean Code & Linting

Cet agent analyse, corrige et applique les bonnes pratiques Clean Code tout en garantissant la conformité pylint/flake8.

## ⚠️ DÉCLENCHEMENT AUTOMATIQUE

**Cet agent DOIT être appliqué automatiquement lors de :**
- Création/modification de fichiers Python (`.py`)
- Avant chaque commit
- Sur demande d'analyse de code

---

## Procédure de correction sécurisée

### Règle d'or : NE JAMAIS CASSER LE CODE

Avant toute correction :
1. Vérifier que les tests passent
2. Appliquer les corrections une par une
3. Vérifier après chaque modification
4. Rollback si erreur

---

## Étape 1 : Analyse du fichier

// turbo
```bash
# Lancer flake8 sur le fichier
flake8 <fichier.py> --max-line-length=88

# Lancer pylint sur le fichier  
pylint <fichier.py> --max-line-length=88

# Vérifier les imports
isort <fichier.py> --check-only --diff
```

---

## Étape 2 : Corrections automatiques sûres

### 2.1 Formatage avec Black (automatique)

// turbo
```bash
# Formater avec Black (sans risque)
black <fichier.py> --line-length=88
```

### 2.2 Tri des imports avec isort

// turbo
```bash
# Trier les imports
isort <fichier.py> --profile=black
```

---

## Étape 3 : Corrections manuelles par catégorie

### A. Longueur de ligne (E501)

```python
# ❌ AVANT - Ligne trop longue
message = "Ceci est un message très très très très très très très très long qui dépasse 88 caractères"

# ✅ APRÈS - Plusieurs options

# Option 1 : Parenthèses implicites
message = (
    "Ceci est un message très très très très "
    "très très très très long qui dépasse 88 caractères"
)

# Option 2 : Variables intermédiaires
prefix = "Ceci est un message très très très très"
suffix = "très très très très long"
message = f"{prefix} {suffix}"

# Option 3 : Backslash (moins recommandé)
message = "Ceci est un message très " \
          "très long"
```

### B. Imports inutilisés (F401)

```python
# ❌ AVANT
from django.shortcuts import render, redirect, get_object_or_404  # redirect non utilisé

# ✅ APRÈS
from django.shortcuts import render, get_object_or_404
```

### C. Variables non utilisées (F841)

```python
# ❌ AVANT
def process():
    unused_var = compute()  # Variable jamais utilisée
    return True

# ✅ APRÈS - Option 1 : Supprimer
def process():
    compute()  # Appel conservé si effet de bord
    return True

# ✅ APRÈS - Option 2 : Underscore si intentionnel
def process():
    _ = compute()  # Explicitement ignoré
    return True
```

### D. Espaces (E203, E225, E231, W291, W293)

```python
# ❌ AVANT
x=1+2
list = [1,2,3]
dict = {"a":1,"b":2}
def func( arg ):  # Espaces inutiles
    pass   # Espaces en fin de ligne

# ✅ APRÈS
x = 1 + 2
list = [1, 2, 3]
dict = {"a": 1, "b": 2}
def func(arg):
    pass
```

### E. Lignes vides (E302, E303, W391)

```python
# ❌ AVANT
def func1():
    pass
def func2():  # Manque lignes vides
    pass



def func3():  # Trop de lignes vides
    pass

# ✅ APRÈS
def func1():
    pass


def func2():
    pass


def func3():
    pass
```

### F. Comparaisons (E711, E712)

```python
# ❌ AVANT
if x == None:
    pass
if x == True:
    pass
if x == False:
    pass

# ✅ APRÈS
if x is None:
    pass
if x:
    pass
if not x:
    pass
```

### G. Docstrings (D100, D101, D102, D103)

```python
# ❌ AVANT
def calculate_total(items):
    return sum(item.price for item in items)

# ✅ APRÈS
def calculate_total(items):
    """Calculer le total des prix des articles.
    
    Args:
        items: Liste d'objets avec attribut price.
        
    Returns:
        float: Somme des prix.
    """
    return sum(item.price for item in items)
```

### H. Logging avec f-string (W1203)

**Ne pas utiliser de f-string dans les appels logger** - utiliser le formatage % lazy.

```python
# ❌ AVANT - f-string dans logging (W1203)
logger.info(f"Utilisateur {user.name} connecté depuis {ip}")
logger.error(f"Erreur pour {user_id}: {error}")

# ✅ APRÈS - Formatage % lazy (plus performant)
logger.info("Utilisateur %s connecté depuis %s", user.name, ip)
logger.error("Erreur pour %s: %s", user_id, error)
```

**Pourquoi ?**
- Le formatage % est "lazy" : la chaîne n'est formatée que si le niveau de log est actif
- Avec f-string, le formatage est toujours effectué, même si le log est désactivé
- Gain de performance significatif en production

### I. Exception trop générale (W0718)

**Ne pas attraper `Exception` directement** - spécifier les exceptions attendues.

```python
# ❌ AVANT - Exception trop générale (W0718)
try:
    send_email(user)
except Exception as e:
    logger.error("Erreur: %s", e)

# ✅ APRÈS - Exceptions spécifiques
try:
    send_email(user)
except (OSError, ValueError, RuntimeError) as e:
    logger.error("Erreur d'envoi email: %s", e)

# ✅ OU - Si vraiment nécessaire, avec commentaire
try:
    external_api_call()
except Exception as e:  # pylint: disable=broad-exception-caught
    # Justification : API externe peut lever n'importe quelle exception
    logger.error("Erreur API: %s", e)
```

**Exceptions courantes à attraper :**
| Contexte | Exceptions |
|----------|------------|
| Fichiers | `OSError`, `IOError`, `FileNotFoundError` |
| Réseau | `OSError`, `ConnectionError`, `TimeoutError` |
| JSON | `json.JSONDecodeError`, `ValueError` |
| Email | `OSError`, `smtplib.SMTPException` |
| Base de données | `DatabaseError`, `IntegrityError` |

---

## Étape 4 : Principes Clean Code

### 4.1 Nommage

```python
# ❌ MAUVAIS
def calc(x, y):
    return x * y

lst = [1, 2, 3]
d = {"a": 1}

# ✅ BON
def calculate_area(width, height):
    return width * height

numbers = [1, 2, 3]
config = {"api_key": "xxx"}
```

**Règles de nommage :**
| Type | Convention | Exemple |
|------|------------|---------|
| Variable | snake_case | `user_name` |
| Fonction | snake_case | `get_user_by_id` |
| Classe | PascalCase | `UserProfile` |
| Constante | UPPER_SNAKE | `MAX_RETRIES` |
| Privé | _prefix | `_internal_method` |

### 4.2 Fonctions courtes

```python
# ❌ MAUVAIS - Fonction trop longue
def process_order(order):
    # Validation (10 lignes)
    # Calcul prix (15 lignes)
    # Envoi email (10 lignes)
    # Mise à jour stock (10 lignes)
    pass

# ✅ BON - Fonctions séparées
def process_order(order):
    """Traiter une commande."""
    validate_order(order)
    total = calculate_total(order)
    send_confirmation_email(order, total)
    update_stock(order)


def validate_order(order):
    """Valider les données de la commande."""
    ...


def calculate_total(order):
    """Calculer le total de la commande."""
    ...
```

### 4.3 Single Responsibility

```python
# ❌ MAUVAIS - Classe qui fait trop de choses
class User:
    def save(self): ...
    def send_email(self): ...
    def generate_pdf(self): ...
    def calculate_taxes(self): ...

# ✅ BON - Responsabilités séparées
class User:
    def save(self): ...

class EmailService:
    def send_to_user(self, user): ...

class TaxCalculator:
    def calculate(self, user): ...
```

### 4.4 DRY (Don't Repeat Yourself)

```python
# ❌ MAUVAIS - Code dupliqué
def get_active_users():
    return User.objects.filter(is_active=True).order_by("-created_at")

def get_active_admins():
    return User.objects.filter(is_active=True, is_admin=True).order_by("-created_at")

# ✅ BON - Réutilisation
def get_active_users(admin_only=False):
    queryset = User.objects.filter(is_active=True)
    if admin_only:
        queryset = queryset.filter(is_admin=True)
    return queryset.order_by("-created_at")
```

### 4.5 Éviter les magic numbers

```python
# ❌ MAUVAIS
if user.age >= 18:
    pass

if len(password) < 8:
    raise ValueError("...")

# ✅ BON
LEGAL_AGE = 18
MIN_PASSWORD_LENGTH = 8

if user.age >= LEGAL_AGE:
    pass

if len(password) < MIN_PASSWORD_LENGTH:
    raise ValueError("...")
```

---

## Étape 5 : Vérification finale

// turbo
```bash
# Vérification complète après corrections
flake8 <fichier.py> --max-line-length=88 --count

# Si 0 erreur, vérifier que le code fonctionne
python manage.py check

# Lancer les tests si disponibles
python manage.py test <app> --verbosity=2
```

---

## Étape 6 : Rapport de correction

```
## Rapport Clean Code - [fichier.py]

### 📊 Analyse initiale
- Erreurs flake8 : X
- Erreurs pylint : X
- Score pylint : X/10

### 🔧 Corrections appliquées
| Code | Description | Lignes |
|------|-------------|--------|
| E501 | Ligne trop longue | 45, 78 |
| F401 | Import non utilisé | 3 |
| ... | ... | ... |

### ✅ Résultat final
- Erreurs flake8 : 0
- Score pylint : 10/10
- Tests : ✅ Passent

### Statut : CORRIGÉ / PARTIELLEMENT CORRIGÉ
```

---

## Configuration recommandée

### `.flake8` ou `setup.cfg`

```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = 
    .git,
    __pycache__,
    migrations,
    .venv
per-file-ignores =
    __init__.py: F401
```

### `pyproject.toml` (Black + isort)

```toml
[tool.black]
line-length = 88
target-version = ['py312']

[tool.isort]
profile = "black"
line_length = 88
```

---

## Utilisation manuelle

```
/clean-code [fichier.py]       # Analyser et corriger un fichier
/clean-code --check            # Analyse sans correction
/clean-code --all              # Tous les fichiers Python
/clean-code --fix-imports      # Corriger uniquement les imports
/clean-code --format           # Formater avec Black
```

---

## Codes d'erreur fréquents

### Flake8

| Code | Description | Auto-fix |
|------|-------------|----------|
| E501 | Ligne > 88 caractères | Manuel |
| E302 | 2 lignes vides attendues | Black |
| E303 | Trop de lignes vides | Black |
| F401 | Import non utilisé | Manuel |
| F841 | Variable non utilisée | Manuel |
| W291 | Espace en fin de ligne | Black |
| W293 | Ligne vide avec espaces | Black |

### Pylint

| Code | Description | Auto-fix |
|------|-------------|----------|
| C0114 | Docstring module manquant | Manuel |
| C0115 | Docstring classe manquant | Manuel |
| C0116 | Docstring fonction manquant | Manuel |
| C0301 | Ligne trop longue | Manuel |
| W0611 | Import non utilisé | Manuel |
| W0612 | Variable non utilisée | Manuel |
| **W0718** | **Exception trop générale (broad-exception-caught)** | **Manuel** |
| **W1203** | **f-string dans logging (logging-fstring-interpolation)** | **Manuel** |


---

## Références

- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstrings](https://peps.python.org/pep-0257/)
- [Clean Code - Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [Black - Code Formatter](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
