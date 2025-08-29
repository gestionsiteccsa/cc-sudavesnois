# Documentation des routes (URLs) du projet CCSA

*Dernière mise à jour : 13/05/2025*

Cette documentation liste toutes les routes principales du projet, leur chemin, la vue associée, et une courte description.

## Nouvelles Routes (13/05/2025)

### Routes d'Accessibilité
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/accessibility/` | `accessibility_view` | Page de configuration de l'accessibilité |
| `/accessibility/settings/` | `accessibility_settings` | Paramètres d'accessibilité |
| `/accessibility/contrast/` | `contrast_settings` | Configuration du contraste |

### Routes de Mode Sombre
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/dark-mode/` | `dark_mode_view` | Configuration du mode sombre |
| `/dark-mode/settings/` | `dark_mode_settings` | Paramètres du mode sombre |

---

## Racine et structure principale (`app/urls.py`)

| Chemin | Vue/Namespace | Description |
|--------|---------------|-------------|
| `/admin/` | Django Admin | Interface d'administration Django |
| `/` | `home.urls` | Pages d'accueil et institutionnelles |
| `/accounts/` | `accounts.urls` | Gestion des comptes utilisateurs |
| `/sitemap.xml` | Django sitemap | Sitemap XML pour SEO |
| `/conseil/` | `conseil_communautaire.urls` | Conseil communautaire |
| `/journal/` | `journal.urls` | Gestion des journaux |
| `/elus/` | `bureau_communautaire.urls` | Gestion des élus et documents |
| `/commune/` | `communes_membres.urls` | Communes membres et actes locaux |
| `/commissions/` | `commissions.urls` | Commissions et documents |
| `/competences/` | `competences.urls` | Compétences administratives |
| `/semestriels/` | `semestriels.urls` | Semestriels et événements |
| `/comptes-rendus-conseils-communautaires/` | `comptes_rendus.urls` | Comptes-rendus des conseils |
| `/services/` | `services.urls` | Gestion des services |

---

## Exemples détaillés par app

### home
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/` | `home` | Accueil |
| `/presentation/` | `presentation` | Présentation institutionnelle |
| `/marches-publics/` | `marches_publics` | Marchés publics |
| `/mobilite/` | `mobilite` | Mobilité |
| `/habitat/` | `habitat` | Habitat |
| `/collecte-dechets/` | `collecte_dechets` | Collecte des déchets |
| `/encombrants/` | `encombrants` | Encombrants |
| `/dechetteries/` | `dechetteries` | Déchetteries |
| `/maisons-sante-pluridisciplinaires/` | `maisons_sante` | Maisons de santé |
| `/mutuelle-intercommunautaire/` | `mutuelle` | Mutuelle intercommunautaire |
| `/plui/` | `plui` | PLUI |
| `/projet-plui/` | `projet_plui` | Projet PLUI |
| `/equipe/` | `equipe` | Équipe administrative |
| `/rapports-activite/` | `rapports_activite` | Rapports d'activité |
| `/mentions-legales/` | `mentions_legales` | Mentions légales |
| `/politique-confidentialite/` | `politique_confidentialite` | Politique de confidentialité |

### bureau_communautaire
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/elus/` | `elus` | Liste publique des élus |
| `/elus/ajouter-elu/` | `add_elu` | Ajouter un élu (admin) |
| `/elus/liste-elus/` | `list_elus` | Liste des élus (admin) |
| `/elus/modifier-elu/<id>/` | `update_elu` | Modifier un élu (admin) |
| `/elus/supprimer-elu/<id>/` | `delete_elu` | Supprimer un élu (admin) |
| `/elus/ajouter-document/` | `add_document` | Ajouter un document (admin) |
| `/elus/liste-documents/` | `list_documents` | Liste des documents (admin) |
| `/elus/modifier-document/<id>/` | `update_document` | Modifier un document (admin) |
| `/elus/supprimer-document/<id>/` | `delete_document` | Supprimer un document (admin) |

### commissions
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/commissions/` | `commissions` | Liste publique des commissions |
| `/commissions/ajouter/` | `add_commission` | Ajouter une commission (admin) |
| `/commissions/liste/` | `list_commission` | Liste des commissions (admin) |
| `/commissions/modifier/<commission_id>/` | `edit_commission` | Modifier une commission (admin) |
| `/commissions/supprimer/<commission_id>/` | `delete_commission` | Supprimer une commission (admin) |
| `/commissions/upload/` | `add_document` | Ajouter un document (admin) |
| `/commissions/modifier_doc/<document_id>/` | `edit_document` | Modifier un document (admin) |
| `/commissions/supprimer_doc/<document_id>/` | `delete_document` | Supprimer un document (admin) |
| `/commissions/modifier_mandat/<mandat_id>/` | `edit_mandat` | Modifier un mandat (admin) |

### communes_membres
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/commune/<id>` | `commune` | Page publique d'une commune |
| `/commune/ajouter-acte/` | `add_acte_local` | Ajouter un acte local (admin) |
| `/commune/liste-actes/` | `list_acte_local` | Liste des actes (admin) |
| `/commune/modifier-acte/<id>` | `update_acte_local` | Modifier un acte (admin) |
| `/commune/supprimer-acte/<id>` | `delete_acte_local` | Supprimer un acte (admin) |

### competences
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/competences/` | `competences` | Page publique des compétences |
| `/competences/liste/` | `competences_list` | Liste des compétences (admin) |
| `/competences/ajouter/` | `add_competence` | Ajouter une compétence (admin) |
| `/competences/modifier/<id>/` | `edit_competence` | Modifier une compétence (admin) |
| `/competences/supprimer/<id>/` | `delete_competence` | Supprimer une compétence (admin) |

### comptes_rendus
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/comptes-rendus-conseils-communautaires/` | `comptes_rendus` | Page publique des comptes-rendus |
| `/comptes-rendus-conseils-communautaires/cr-admin/` | `admin_page` | Admin des comptes-rendus |
| `/comptes-rendus-conseils-communautaires/ajouter-conseil/` | `add_conseil` | Ajouter un conseil (admin) |
| `/comptes-rendus-conseils-communautaires/modifier-conseil/<id>/` | `edit_conseil` | Modifier un conseil (admin) |
| `/comptes-rendus-conseils-communautaires/supprimer-conseil/<id>/` | `delete_conseil` | Supprimer un conseil (admin) |
| `/comptes-rendus-conseils-communautaires/ajouter-cr-link/` | `add_cr_link` | Ajouter un lien CR (admin) |
| `/comptes-rendus-conseils-communautaires/modifier-cr-link/<id>/` | `edit_cr_link` | Modifier un lien CR (admin) |
| `/comptes-rendus-conseils-communautaires/supprimer-cr-link/<id>/` | `delete_cr_link` | Supprimer un lien CR (admin) |

### conseil_communautaire
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/conseil/` | `conseil` | Page publique du conseil |
| `/conseil/ajouter-ville/` | `add_city` | Ajouter une ville (admin) |
| `/conseil/liste-ville/` | `list_cities` | Liste des villes (admin) |
| `/conseil/supprimer-ville/<id>/` | `delete_city` | Supprimer une ville (admin) |
| `/conseil/modifier-ville/<id>/` | `edit_city` | Modifier une ville (admin) |
| `/conseil/ajouter-membre/` | `add_member` | Ajouter un membre (admin) |
| `/conseil/liste-membres/` | `admin_list_members` | Liste des membres (admin) |
| `/conseil/modifier-membre/<id>/` | `edit_member` | Modifier un membre (admin) |
| `/conseil/supprimer-membre/<id>/` | `delete_member` | Supprimer un membre (admin) |

### journal
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/journal/` | `journal` | Page publique des journaux |
| `/journal/ajouter-journal/` | `add_journal` | Ajouter un journal (admin) |
| `/journal/liste-journaux/` | `list_journals` | Liste des journaux (admin) |
| `/journal/supprimer-journal/<id>/` | `delete_journal` | Supprimer un journal (admin) |
| `/journal/modifier-journal/<id>/` | `edit_journal` | Modifier un journal (admin) |

### semestriels
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/semestriels/` | `semestriel` | Page publique des semestriels |
| `/semestriels/ajouter/` | `add_content` | Ajouter du contenu (admin) |
| `/semestriels/modifier/<id>/` | `edit_content` | Modifier du contenu (admin) |
| `/semestriels/ajouter-evenement/` | `add_event` | Ajouter un événement (admin) |
| `/semestriels/modifier-evenement/<id>/` | `edit_event` | Modifier un événement (admin) |
| `/semestriels/supprimer-evenement/<id>/` | `delete_event` | Supprimer un événement (admin) |
| `/semestriels/liste-evenements/` | `list_event` | Liste des événements (admin) |

### services
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/services/ajout-service/` | `add_service` | Ajouter un service (admin) |
| `/services/modifier-service/<id>` | `update_service` | Modifier un service (admin) |
| `/services/supprimer-service/<id>` | `delete_service` | Supprimer un service (admin) |
| `/services/liste-services/` | `service_list` | Liste des services (admin) |

### accounts
| Chemin | Vue | Description |
|--------|-----|-------------|
| `/accounts/register/` | `register_view` | Inscription utilisateur |
| `/accounts/login/` | `login_view` | Connexion utilisateur |
| `/accounts/logout/` | `LogoutView` | Déconnexion utilisateur |
| `/accounts/profile/` | `profile_view` | Profil utilisateur |
| `/accounts/password-reset/` | `password_reset_view` | Demande de réinitialisation de mot de passe |
| `/accounts/password-reset/done/` | `password_reset_done_view` | Confirmation de demande de réinitialisation |
| `/accounts/password-reset-confirm/<uidb64>/<token>/` | `password_reset_confirm_view` | Confirmation du reset |
| `/accounts/password-reset-complete/` | `password_reset_complete_view` | Fin du reset |
| `/accounts/users/` | `admin_user_list` | Liste des utilisateurs (admin) |
| `/accounts/users/create/` | `admin_create_user` | Créer un utilisateur (admin) |

---

**Remarque :**
- Les routes marquées `(admin)` sont protégées par des permissions (superuser ou staff).
- Les routes publiques sont accessibles à tous.
- Les variables `<id>`, `<pk>`, `<commission_id>`, etc. sont des identifiants numériques d'objets.

Pour chaque app, tu peux retrouver la logique détaillée dans le fichier `urls.py` correspondant.
