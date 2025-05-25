"""
Konstante koje se koriste za definiranje građevinskih elemenata i njihovih toplinskih svojstava.
Ova datoteka sadži sve konstante specifične za građevinske elemente.
"""

# Tipovi prostorija s pripadajućim temperaturama, ventilacijom i statusom grijanja
TIPOVI_PROSTORIJA = {
    "Dnevni boravak": {"temp": 20, "izmjene": 0.5, "grijana": True},
    "Spavaća soba": {"temp": 20, "izmjene": 0.5, "grijana": True},
    "Kuhinja": {"temp": 20, "izmjene": 1.5, "grijana": True},
    "Kupaonica": {"temp": 24, "izmjene": 1.5, "grijana": True},
    "WC": {"temp": 20, "izmjene": 1.5, "grijana": True},
    "Hodnik": {"temp": 18, "izmjene": 0.5, "grijana": True},
    "Predsoblje": {"temp": 18, "izmjene": 0.5, "grijana": True},
    "Stubište": {"temp": 18, "izmjene": 0.5, "grijana": False},
    "Garderoba": {"temp": 18, "izmjene": 0.5, "grijana": True},
    "Ostava": {"temp": 18, "izmjene": 0.5, "grijana": False},
    "Radna soba": {"temp": 20, "izmjene": 0.5, "grijana": True},
    "Blagovaonica": {"temp": 20, "izmjene": 0.5, "grijana": True},
    "Ured": {"temp": 20, "izmjene": 0.5, "grijana": True},
    "Garaža": {"temp": 5, "izmjene": 0.5, "grijana": False},
    "Podrum": {"temp": 10, "izmjene": 0.5, "grijana": False},
    "Tavan": {"temp": 10, "izmjene": 0.5, "grijana": False},
    "Vešeraj": {"temp": 18, "izmjene": 1.0, "grijana": True},
    "Terasa": {"temp": 10, "izmjene": 0.0, "grijana": False},
    "Lođa": {"temp": 10, "izmjene": 0.0, "grijana": False},
    "Balkon": {"temp": 10, "izmjene": 0.0, "grijana": False},
    "Tlocrtno složena prostorija": {"temp": 20, "izmjene": 0.5, "grijana": True},
}

# Importiramo direktno iz parent modula, bez kružne reference
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from constants import GRADOVI_TEMP

# Alias za pristup temperaturama gradova
VANJSKE_TEMP_PO_GRADOVIMA = GRADOVI_TEMP

# Default vrijednosti za U-vrijednosti građevinskih elemenata
DEFAULT_U_VALUES = {
    "vanjski_zid": 0.3,      # W/m²K
    "unutarnji_zid": 1.0,     # W/m²K
    "pod_na_tlu": 0.35,      # W/m²K
    "pod_izmedu_etaza": 0.6,  # W/m²K
    "strop_prema_tavanu": 0.25, # W/m²K
    "ravni_krov": 0.25,      # W/m²K
    "kosi_krov": 0.25,       # W/m²K
    "prozor": 1.4,           # W/m²K
    "vanjska_vrata": 1.8,    # W/m²K
    "unutarnja_vrata": 2.0    # W/m²K
}

# Temperaturni faktori za različite vrste prostora
TEMP_FAKTORI = {
    "vanjski": 1.0,              # Faktor za vanjske zidove
    "negrijani": 0.5,            # Faktor za negrijane prostore
    "podrum": 0.6,               # Faktor za podrum
    "tavan": 0.9,                # Faktor za tavan
    "tlo": 0.3                   # Faktor za tlo
}

# Detaljniji temperaturni faktori prema EN ISO 13370
TEMP_FAKTORI_DETALJNI = {
    # Vanjski elementi
    "vanjski_zid": 1.0,          # Faktor za vanjske zidove
    "prozor": 1.0,               # Faktor za prozore
    "vanjska_vrata": 1.0,        # Faktor za vanjska vrata
    
    # Elementi prema negrijanim prostorima
    "prema_negrijanom": 0.5,     # Faktor za negrijane prostore (općenito)
    "prema_stubištu": 0.4,       # Faktor za negrijanao stubište
    "prema_tavanu": 0.9,         # Faktor za tavan
    "prema_podrumu": 0.6,        # Faktor za podrum
    "prema_garaži": 0.5,         # Faktor za garažu
    
    # Elementi prema tlu
    "pod_na_tlu": 0.3,           # Faktor za pod na tlu
    "zid_prema_tlu": 0.6,        # Faktor za zid prema tlu
    "pod_podruma": 0.5,          # Faktor za pod podruma
    
    # Specifični faktori
    "topli_most": 1.0            # Faktor za toplinske mostove
}

# Otpori prijelaza topline prema EN ISO 6946
TOPLINSKI_OTPORI_PRIJELAZA = {
    "unutarnji_zid": 0.13,       # Unutarnja površina zida (m²K/W)
    "unutarnji_strop": 0.10,     # Unutarnja površina stropa ili krova (m²K/W)
    "unutarnji_pod": 0.17,       # Unutarnja površina poda (m²K/W)
    "vanjski": 0.04,             # Vanjska površina (m²K/W)
    "ventilirani_sloj": 0.13,    # Ventilirani zračni sloj (m²K/W)
    "neventilirani_sloj_10mm": 0.15,  # Neventilirani zračni sloj 10mm (m²K/W)
    "neventilirani_sloj_25mm": 0.18,  # Neventilirani zračni sloj 25mm (m²K/W)
    "neventilirani_sloj_50mm": 0.18,  # Neventilirani zračni sloj 50mm (m²K/W)
    "neventilirani_sloj_100mm": 0.17,  # Neventilirani zračni sloj 100mm (m²K/W)
    "neventilirani_sloj_300mm": 0.16,  # Neventilirani zračni sloj 300mm (m²K/W)
}

# Prosječne temperature tla po dubinama u Hrvatskoj
PROSJECNE_TEMPERATURE_TLA = {
    "0.5m": 12.0,
    "1.0m": 12.5,
    "2.0m": 13.0,
    "3.0m": 13.5,
    "5.0m": 14.0,
    "10.0m": 14.5
}

# Različiti tipovi zidova
TIPOVI_ZIDOVA = {
    "vanjski": {
        "naziv": "Vanjski zid",
        "default_u": 0.30,
        "temperaturni_faktor": 1.0
    },
    "pregradni": {
        "naziv": "Pregradni zid",
        "default_u": 1.0,
        "temperaturni_faktor": 0.0
    },
    "prema_negrijanom": {
        "naziv": "Zid prema negrijanom prostoru",
        "default_u": 0.50,
        "temperaturni_faktor": 0.5
    },
    "prema_prostoriji": {
        "naziv": "Zid prema drugoj prostoriji",
        "default_u": 1.0,
        "temperaturni_faktor": 0.0
    }
}

# Nazivi tipova elemenata za UI prikaz
TIPOVI_ELEMENATA = {
    "zid": "Zid",
    "prozor": "Prozor",
    "vrata": "Vrata",
    "pod": "Pod",
    "strop": "Strop"
}
