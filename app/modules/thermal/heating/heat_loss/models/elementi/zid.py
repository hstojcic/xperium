"""
Modul koji sadrži funkcije za rad sa zidovima u proračunu toplinskih gubitaka.
"""

import uuid
from .wall_elements import WallElements

def create_wall(tip="vanjski", orijentacija="Sjever", duzina=5.0, visina=None,
               povezana_prostorija_id=None, povezani_zid_id=None,
               je_segmentiran=False, segmenti=None, elementi=None):
    """
    Stvara novi zid s određenim karakteristikama.
    
    Parameters:
    -----------
    tip : str
        Tip zida ("vanjski", "prema_prostoriji", "prema_negrijanom")
    orijentacija : str
        Orijentacija zida (relevantno samo za vanjske zidove)
    duzina : float
        Duljina zida u metrima
    visina : float
        Visina zida u metrima (ako nije navedena, koristit će se visina etaže)
    povezana_prostorija_id : str
        ID povezane prostorije (za zidove tipa "prema_prostoriji")
    povezani_zid_id : str
        ID povezanog zida (za zidove tipa "prema_prostoriji")
    je_segmentiran : bool
        Označava je li zid segmentiran
    segmenti : list
        Lista segmenata zida
    elementi : WallElements
        Elementi na zidu (prozori, vrata)
        
    Returns:
    --------
    dict
        Rječnik koji predstavlja zid
    """
    try:
        processed_duzina = float(duzina)
        if processed_duzina <= 0:
            return None  # Neispravna duljina
    except (ValueError, TypeError):
        return None  # Duljina nije broj
    
    elementi_obj = elementi if elementi is not None else WallElements()
    
    zid = {
        "id": str(uuid.uuid4().hex),
        "tip": tip,
        "orijentacija": orijentacija if tip == "vanjski" else None,
        "duzina": processed_duzina,
        "visina": float(visina) if visina is not None else None,
        "povezana_prostorija_id": povezana_prostorija_id,
        "povezani_zid_id": povezani_zid_id,
        "elementi": elementi_obj,
        "je_segmentiran": je_segmentiran,
        "segmenti": segmenti if segmenti is not None else []
    }
    
    return zid

def povezivanje_zidova(zid_A, zid_B, prostorija_A_id, prostorija_B_id):
    """
    Povezuje dva zida između prostorija tako da dijele elemente.
    
    Parameters:
    -----------
    zid_A : dict
        Prvi zid koji se povezuje
    zid_B : dict
        Drugi zid koji se povezuje
    prostorija_A_id : str
        ID prostorije u kojoj se nalazi prvi zid
    prostorija_B_id : str
        ID prostorije u kojoj se nalazi drugi zid
        
    Returns:
    --------
    tuple
        (zid_A, zid_B) - ažurirani zidovi
    """
    zid_A["povezana_prostorija_id"] = prostorija_B_id
    zid_A["povezani_zid_id"] = zid_B["id"]
    zid_A["tip"] = "prema_prostoriji"
    zid_A["orijentacija"] = None
    
    zid_B["povezana_prostorija_id"] = prostorija_A_id
    zid_B["povezani_zid_id"] = zid_A["id"]
    zid_B["tip"] = "prema_prostoriji"
    zid_B["orijentacija"] = None
    
    # Dijelimo isti objekt elemenata između zidova
    if not isinstance(zid_A.get("elementi"), WallElements):
        zid_A["elementi"] = WallElements()
    if not isinstance(zid_B.get("elementi"), WallElements):
        zid_B["elementi"] = WallElements()
        
    zid_B["elementi"] = zid_A["elementi"]
    
    return (zid_A, zid_B)

def izracunaj_povrsinu_zida(zid, default_height=2.5):
    """
    Izračunava površinu zida.
    
    Parameters:
    -----------
    zid : dict
        Zid za koji se računa površina
    default_height : float
        Zadana visina ako visina zida nije definirana
        
    Returns:
    --------
    float
        Površina zida u m²
    """
    visina = zid.get("visina") if zid.get("visina") is not None else default_height
    duzina = zid.get("duzina", 0.0)
    
    return visina * duzina
