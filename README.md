Plateforme de planification des études (IFT2255, automne 2026). Elle aide une personne étudiante à planifier sa session avant de s'inscrire : catalogue d'activités, vérification des règles (préalables, conflits d'horaire, crédits, temps plein, dates limites) et suivi des demandes aux personnes qui encadrent.

## Installation

Python 3.10 ou plus récent.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Ouvrir http://localhost:8000.

## Comptes de démonstration

Créés par `seed`. Mot de passe : `demo`.

| Compte | Rôle |
|---|---|
| `alice`, `bob` | Étudiants |
| `tremblay`, `gagnon` | Encadrants |

`seed` remplace les données existantes.

## Structure

```
config/   réglages Django
planif/   application (modèles, règles, vues, gabarits, commande seed)
docs/     conception, diagrammes et rapport
```
