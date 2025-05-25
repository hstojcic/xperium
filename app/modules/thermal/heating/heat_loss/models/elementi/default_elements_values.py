"""
Modul koji sadrži defaultne vrijednosti za građevinske elemente,
organizirane kao nested dictionary za lakše korištenje.
"""

# Default vrijednosti za U-vrijednosti građevinskih elemenata
# Ovo je nested dictionary verzija originalnog DEFAULT_U_VALUES iz constants modula,
# strukturirana na način da omogućuje lakši pristup po tipovima elemenata
DEFAULT_U_VALUES = {
    "zid": {
        "vanjski": 0.3,       # W/m²K
        "unutarnji": 1.0,     # W/m²K
    },
    "pod": {
        "tlo": 0.35,          # W/m²K
        "negrijani": 0.35,    # W/m²K
        "etaza": 0.6,         # W/m²K
    },
    "strop": {
        "tavan": 0.25,        # W/m²K
        "ravni_krov": 0.25,   # W/m²K
        "kosi_krov": 0.25,    # W/m²K
    },    "prozor": {
        "dvostruko": 1.4,     # W/m²K
        "trostruko": 1.0,     # W/m²K
        "aluminij": 1.6       # W/m²K
    },
    "vrata": {
        "ulazna": 1.8,        # W/m²K
        "sobna": 2.0,         # W/m²K
        "balkonska": 1.5      # W/m²K
    }
}
