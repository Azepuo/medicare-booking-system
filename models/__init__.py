# models/__init__.py
# Expose les modèles de façon stable et fournit un alias pour compatibilité
from .rendezvous import Rendezvous
from .patient import Patient
from .medecin import Medecin

# Compatibilité avec du code ancien qui importait "RendezVous" (avec V majuscule interne)
# Ceci évite les ImportError si certains fichiers utilisent RendezVous au lieu de Rendezvous.
RendezVous = Rendezvous

__all__ = ['Rendezvous', 'RendezVous', 'Patient', 'Medecin']
