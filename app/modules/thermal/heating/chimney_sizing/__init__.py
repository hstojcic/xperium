"""
Chimney sizing calculation module initialization.
Proračun dimnjaka prema EN 13384-2 normi.
"""

from .chimney_sizing_calc import ChimneySizingCalc

__version__ = "2.0.0"
__author__ = "Inženjerski tim"
__description__ = "Proračun dimnjaka prema EN 13384-2 normi s poboljšanjima"

# Export glavne klase
__all__ = ["ChimneySizingCalc"]

# Metadata o modulu
MODULE_INFO = {
    "name": "Chimney Sizing Calculator",
    "version": __version__,
    "standard": "EN 13384-2:2015+A1:2019",
    "description": "Kompletni kalkulator za proračun dimnjaka s poboljšanim formulama",
    "features": [
        "Poboljšana formula za točku rosišta",
        "Pravilno izračunan potrebni tlak PZ",
        "Iterativni izračun temperature stijenke",
        "Validacija prema EN 13384-2",
        "Poboljšana gustoća dimnih plinova",
        "Reynolds broj u izračunu trenja"
    ],
    "improvements": [
        "Uklonjen matplotlib kod",
        "Dodane validacije unosa",
        "Ispravke svih temperatura na 0°C",
        "Dodana BaseCalculation klasa",
        "Proširene konstante i tablice",
        "Dodani novi modeli kotlova i dimnjaka"
    ]
}