# Guide des Bonnes Pratiques Git

## Table des matières
- [Configuration initiale](#configuration-initiale)
- [Messages de commit](#messages-de-commit)
- [Stratégies de branching](#stratégies-de-branching)
- [Workflow et collaboration](#workflow-et-collaboration)
- [Rebase vs Merge](#rebase-vs-merge)
- [Gestion des fichiers](#gestion-des-fichiers)
- [Hooks et automatisation](#hooks-et-automatisation)
- [Sécurité et bonnes pratiques](#sécurité-et-bonnes-pratiques)
- [Résolution de problèmes](#résolution-de-problèmes)
- [Outils et intégrations](#outils-et-intégrations)

## Configuration initiale

### Configuration globale
```bash
# Informations utilisateur
git config --global user.name "Votre Nom"
git config --global user.email "votre.email@exemple.com"

# Éditeur par défaut
git config --global core.editor "code --wait"  # VS Code
git config --global core.editor "vim"          # Vim

# Configuration des fins de ligne
git config --global core.autocrlf input    # Linux/Mac
git config --global core.autocrlf true     # Windows

# Configuration des couleurs
git config --global color.ui auto

# Configuration du pager
git config --global core.pager "less -FRX"

# Configuration du push par défaut
git config --global push.default simple

# Configuration du pull par défaut (évite les messages d'avertissement)
git config --global pull.rebase false  # merge (par défaut)
# ou
git config --global pull.rebase true   # rebase
```

### Configuration locale du projet
```bash
# Pour un projet spécifique
git config user.email "email.professionnel@entreprise.com"
git config user.name "Nom Professionnel"

# Configuration des hooks locaux
git config core.hooksPath .githooks
```

### Alias utiles
```bash
# Aliases pour les commandes fréquentes
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.st status
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual '!gitk'

# Aliases avancés
git config --global alias.lg "log --color --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit"
git config --global alias.cleanup "!git branch --merged | grep -v '\\*\\|main\\|develop' | xargs -n 1 git branch -d"
git config --global alias.contributors "shortlog --summary --numbered"
```

## Messages de commit

### Format de message conventionnel
```
<type>[scope optionnel]: <description>

[corps optionnel]

[footer(s) optionnel(s)]
```

### Types de commit
- **feat**: Nouvelle fonctionnalité
- **fix**: Correction de bug
- **docs**: Documentation seulement
- **style**: Changements qui n'affectent pas le code (espaces, formatage, etc.)
- **refactor**: Refactorisation du code sans changement de fonctionnalité
- **perf**: Amélioration des performances
- **test**: Ajout ou modification de tests
- **chore**: Maintenance, configuration, outils de build
- **ci**: Changements dans la configuration CI/CD
- **build**: Changements dans le système de build ou dépendances externes
- **revert**: Annulation d'un commit précédent

### Exemples de bons messages
```bash
# Exemples corrects
git commit -m "feat(auth): add password reset functionality"
git commit -m "fix(api): handle null response in user endpoint"
git commit -m "docs: update README with installation instructions"
git commit -m "refactor(utils): extract validation logic to separate module"
git commit -m "perf(db): optimize user query with proper indexing"
git commit -m "test(auth): add unit tests for login validation"

# Message avec corps et footer
git commit -m "feat(payment): integrate Stripe payment gateway

- Add Stripe SDK integration
- Implement payment processing logic
- Add error handling for failed payments
- Update user model with payment status

Closes #123
Breaking change: Payment API now requires authentication"
```

### Règles pour les messages
1. **Utilisez l'impératif** : "Add feature" au lieu de "Added feature"
2. **Première ligne max 50 caractères**
3. **Corps du message max 72 caractères par ligne**
4. **Séparez le titre du corps par une ligne vide**
5. **Expliquez le "pourquoi", pas le "quoi"**
6. **Référencez les issues/tickets** : "Fixes #123", "Closes #456"

### Anti-patterns à éviter
```bash
# ❌ Messages à éviter
git commit -m "fix"
git commit -m "various changes"
git commit -m "WIP"
git commit -m "fixed bug"
git commit -m "update"
git commit -m "refactoring stuff"
```

## Stratégies de branching

### Git Flow
```bash
# Branches principales
main/master    # Code de production
develop        # Branche de développement

# Branches de support
feature/*      # Nouvelles fonctionnalités
release/*      # Préparation des releases
hotfix/*       # Corrections urgentes en production

# Exemple de flux
git checkout develop
git checkout -b feature/user-authentication
# ... développement ...
git checkout develop
git merge feature/user-authentication
git branch -d feature/user-authentication
```

### GitHub Flow (plus simple)
```bash
# Une seule branche principale
main           # Code de production

# Branches temporaires
feature/*      # Toutes les modifications

# Exemple de flux
git checkout main
git pull origin main
git checkout -b feature/add-search-functionality
# ... développement ...
git push origin feature/add-search-functionality
# Pull Request → Review → Merge → Deploy
```

### Nomenclature des branches
```bash
# Bonnes pratiques de nommage
feature/user-authentication
feature/payment-integration
feature/JIRA-123-user-profile

bugfix/login-error
bugfix/memory-leak-fix
bugfix/TICKET-456-cart-calculation

hotfix/security-vulnerability
hotfix/critical-payment-bug

release/v1.2.0
release/2023-Q4-release

# Évitez
feature/stuff
fix/bug
my-branch
test123
```

## Workflow et collaboration

### Workflow de base
```bash
# 1. Synchroniser avec la branche principale
git checkout main
git pull origin main

# 2. Créer une nouvelle branche
git checkout -b feature/nouvelle-fonctionnalite

# 3. Développer et commiter
git add .
git commit -m "feat: add new functionality"

# 4. Pousser la branche
git push origin feature/nouvelle-fonctionnalite

# 5. Créer une Pull Request

# 6. Après merge, nettoyer
git checkout main
git pull origin main
git branch -d feature/nouvelle-fonctionnalite
```

### Commits atomiques
```bash
# ✅ Un commit = une modification logique
git add src/auth/login.py
git commit -m "feat(auth): add login validation"

git add src/auth/logout.py
git commit -m "feat(auth): add logout functionality"

git add tests/test_auth.py
git commit -m "test(auth): add authentication tests"

# ❌ Évitez les gros commits
git add .
git commit -m "add authentication system"
```

### Amend et fixup
```bash
# Modifier le dernier commit
git add fichier-oublie.py
git commit --amend --no-edit

# Corriger un ancien commit
git add correction.py
git commit --fixup=abc1234  # SHA du commit à corriger
git rebase -i --autosquash HEAD~5
```

### Staging sélectif
```bash
# Ajouter seulement certaines parties d'un fichier
git add -p fichier.py

# Ajouter interactivement
git add -i

# Voir les changements stagés
git diff --staged
```

## Rebase vs Merge

### Quand utiliser rebase
```bash
# Rebase pour un historique linéaire propre
git checkout feature/ma-branche
git rebase main

# Rebase interactif pour nettoyer l'historique
git rebase -i HEAD~3

# Options du rebase interactif:
# pick   = utiliser le commit
# reword = utiliser le commit, mais modifier le message
# edit   = utiliser le commit, mais s'arrêter pour modification
# squash = utiliser le commit, mais le fusionner avec le précédent
# fixup  = comme squash, mais ignorer le message de commit
# drop   = supprimer le commit
```

### Quand utiliser merge
```bash
# Merge pour préserver l'historique des branches
git checkout main
git merge feature/ma-branche

# Merge sans fast-forward pour garder l'historique de branche
git merge --no-ff feature/ma-branche

# Squash merge pour un seul commit propre
git merge --squash feature/ma-branche
git commit -m "feat: complete user authentication system"
```

### Règles de rebase
1. **Ne jamais rebase des commits partagés/pushés**
2. **Rebase seulement ses propres branches locales**
3. **Utiliser rebase pour nettoyer avant de pusher**
4. **Utiliser merge pour intégrer les features terminées**

## Gestion des fichiers

### .gitignore stratégique
```gitignore
# Dépendances
node_modules/
venv/
env/
__pycache__/
*.pyc

# Fichiers de build
dist/
build/
*.egg-info/

# Fichiers d'environnement
.env
.env.local
.env.production
secrets.yaml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log
npm-debug.log*

# OS
.DS_Store
Thumbs.db

# Bases de données locales
*.sqlite3
*.db

# Certificats et clés
*.pem
*.key
*.crt

# Fichiers temporaires
temp/
tmp/
*.tmp
```

### .gitattributes pour la cohérence
```gitattributes
# Traitement des fins de ligne
* text=auto
*.sh text eol=lf
*.bat text eol=crlf

# Fichiers binaires
*.png binary
*.jpg binary
*.gif binary
*.ico binary
*.pdf binary

# Fichiers de code
*.js text
*.css text
*.html text
*.py text
*.json text
*.yaml text
*.yml text

# Exclusions des diffs/merges
package-lock.json merge=ours
```

### Gestion des fichiers sensibles
```bash
# Pour les secrets déjà commités
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch secret-file.txt' \
--prune-empty --tag-name-filter cat -- --all

# Alternative moderne avec git-filter-repo
git filter-repo --path secret-file.txt --invert-paths

# Prévention avec git-secrets
git secrets --register-aws
git secrets --install
git secrets --scan
```

## Hooks et automatisation

### Pre-commit hooks
```bash
#!/bin/sh
# .git/hooks/pre-commit

# Vérification du style de code
echo "Running code style checks..."
if ! command -v black &> /dev/null; then
    echo "Black not found. Please install: pip install black"
    exit 1
fi

black --check .
if [ $? -ne 0 ]; then
    echo "Code style issues found. Run 'black .' to fix."
    exit 1
fi

# Tests unitaires
echo "Running tests..."
python -m pytest
if [ $? -ne 0 ]; then
    echo "Tests failed. Please fix before committing."
    exit 1
fi

echo "All checks passed!"
```

### Commit-msg hook
```bash
#!/bin/sh
# .git/hooks/commit-msg

# Vérification du format du message de commit
commit_regex='^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .{1,50}'

if ! grep -qE "$commit_regex" "$1"; then
    echo "Invalid commit message format!"
    echo "Format: type(scope): description"
    echo "Example: feat(auth): add login functionality"
    exit 1
fi
```

### Pre-push hook
```bash
#!/bin/sh
# .git/hooks/pre-push

protected_branch='main'
current_branch=$(git symbolic-ref HEAD | sed -e 's,.*/\(.*\),\1,')

if [ $protected_branch = $current_branch ]; then
    echo "Direct push to main branch is not allowed"
    exit 1
fi
```

### Utilisation de pre-commit (outil Python)
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-case-conflict

  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
```

## Sécurité et bonnes pratiques

### Signature des commits
```bash
# Configuration GPG
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git config --global tag.gpgsign true

# Commit signé
git commit -S -m "feat: add secure authentication"

# Vérification des signatures
git log --show-signature
```

### Vérification de l'intégrité
```bash
# Vérifier l'intégrité du repository
git fsck

# Vérifier les objets corrompus
git fsck --full

# Nettoyer le repository
git gc --prune=now
```

### Sécurité des credentials
```bash
# Utiliser credential helper
git config --global credential.helper store    # Attention: stockage en clair
git config --global credential.helper cache    # Cache temporaire
git config --global credential.helper 'cache --timeout=3600'

# Meilleure option: gestionnaire de credentials OS
git config --global credential.helper manager-core  # Windows
git config --global credential.helper osxkeychain   # macOS
```

### URLs sécurisées
```bash
# Forcer HTTPS au lieu de HTTP
git config --global url."https://".insteadOf "git://"

# Vérifier les remotes
git remote -v

# Changer l'URL d'un remote
git remote set-url origin https://github.com/user/repo.git
```

## Résolution de problèmes

### Annuler des modifications
```bash
# Annuler les modifications non stagées
git checkout -- fichier.py
git restore fichier.py

# Annuler les modifications stagées
git reset HEAD fichier.py
git restore --staged fichier.py

# Annuler le dernier commit (garde les modifications)
git reset --soft HEAD~1

# Annuler le dernier commit (supprime les modifications)
git reset --hard HEAD~1

# Réinitialiser complètement à un commit
git reset --hard abc1234
```

### Récupération de données
```bash
# Récupérer un fichier supprimé
git checkout HEAD~1 -- fichier-supprime.py

# Voir l'historique d'un fichier supprimé
git log --all --full-history -- fichier-supprime.py

# Récupérer des commits perdus
git reflog
git checkout 1a2b3c4  # SHA du commit perdu

# Récupérer une branche supprimée
git reflog
git checkout -b branche-recuperee 1a2b3c4
```

### Résolution de conflits
```bash
# Voir les conflits
git status
git diff

# Outils de merge
git config --global merge.tool vimdiff
git mergetool

# Résolution manuelle
# Éditer le fichier, résoudre les conflits
git add fichier-resolu.py
git commit

# Abandonner un merge
git merge --abort

# Abandonner un rebase
git rebase --abort
```

### Nettoyage et maintenance
```bash
# Nettoyer les branches locales supprimées sur remote
git remote prune origin

# Supprimer les branches mergées
git branch --merged | grep -v "\*\|main\|develop" | xargs -n 1 git branch -d

# Nettoyer les fichiers non trackés
git clean -fd

# Voir l'espace utilisé
git count-objects -vH

# Optimiser le repository
git gc --aggressive --prune=now
```

## Outils et intégrations

### Outils en ligne de commande
```bash
# Installation d'outils utiles
npm install -g commitizen cz-conventional-changelog
echo '{ "path": "cz-conventional-changelog" }' > ~/.czrc

# Utilisation
git cz  # Au lieu de git commit

# Tig - interface Git en terminal
sudo apt-get install tig  # Ubuntu
brew install tig          # macOS

# Lazygit - interface Git simplifiée
brew install lazygit

# GitKraken, SourceTree, Fork - GUIs populaires
```

### Intégration CI/CD
```yaml
# .github/workflows/git-checks.yml
name: Git Checks
on: [push, pull_request]

jobs:
  git-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Check commit messages
        run: |
          for commit in $(git rev-list ${{ github.event.before }}..${{ github.sha }}); do
            message=$(git log --format=%B -n 1 $commit)
            if ! echo "$message" | grep -qE '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'; then
              echo "Invalid commit message: $message"
              exit 1
            fi
          done

      - name: Check for large files
        run: |
          git ls-files | xargs ls -la | awk '{if ($5 > 1048576) print $9 " is " $5 " bytes"}'
```

### Configuration d'équipe
```bash
# .gitmessage template d'équipe
# Titre: type(scope): description courte

# Corps: Expliquer POURQUOI, pas QUOI
# - Première raison
# - Deuxième raison

# Footer:
# Fixes #123
# Breaking change: describe the breaking change

# Configurer le template
git config commit.template .gitmessage
```

## Checklist des bonnes pratiques

### Configuration
- [ ] Nom et email configurés
- [ ] Éditeur configuré
- [ ] Alias utiles définis
- [ ] Configuration des fins de ligne
- [ ] Credential helper configuré

### Commits
- [ ] Messages suivent la convention
- [ ] Commits atomiques
- [ ] Pas de commits de merge/debug
- [ ] Signature des commits (optionnel)
- [ ] Tests passent avant commit

### Branches
- [ ] Nomenclature cohérente des branches
- [ ] Branches feature courtes
- [ ] Pas de développement direct sur main
- [ ] Nettoyage des branches mergées
- [ ] Protection des branches principales

### Collaboration
- [ ] Pull Requests pour tous les changements
- [ ] Code review systématique
- [ ] Tests automatisés
- [ ] Documentation à jour
- [ ] Pas de fichiers sensibles commités

### Maintenance
- [ ] .gitignore approprié
- [ ] Repository optimisé régulièrement
- [ ] Hooks configurés
- [ ] Monitoring de la taille du repo
- [ ] Sauvegarde régulière