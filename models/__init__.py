# models/__init__.py
# Point d’entrée unique pour tous les modèles
# + alias pour compatibilité avec l’ancien code

from .patient import Patient
from .medecin import Medecin
from .rendezvous import Rendezvous
from .admin import Admin
from .notification import Notification

# Alias de compatibilité (ancien code utilisait RendezVous)
RendezVous = Rendezvous

__all__ = [
    "Patient",
    "Medecin",
    "Rendezvous",
    "RendezVous",
    "Admin",
    "Notification",
]
