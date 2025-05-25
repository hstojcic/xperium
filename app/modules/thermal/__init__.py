"""
Modul koji sadrži termodinamičke kalkulatore
"""

# Inicijalizacijska datoteka za 'thermal' modul

# Napomena: Prethodna implementacija ručne registracije zamijenjena 
# automatskim otkrivanjem kalkulatora kroz ModuleManager klasu.
# Pogledajte core/module_manager.py za implementaciju.

# Import from heating submodule
from .heating import HeatLossCalc, ExpansionVesselCalc, FloorHeatingCalc, ChimneySizingCalc

# Export all calculators
__all__ = ['HeatLossCalc', 'ExpansionVesselCalc', 'FloorHeatingCalc', 'ChimneySizingCalc']