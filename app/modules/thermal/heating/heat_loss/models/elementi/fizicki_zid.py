"""
Modul koji sadrži klasu FizickiZid za centralizirano upravljanje fizičkim zidovima u proračunu toplinskih gubitaka.
"""

import uuid
from .wall_elements import WallElements
from .segment_zida import SegmentZida

class FizickiZid:
    """
    Klasa koja predstavlja fizički zid između prostorija.
    
    Ova klasa omogućuje centralizirano upravljanje zidovima, gdje više prostorija
    može dijeliti referencu na isti fizički zid, eliminirajući probleme
    nedosljednosti koji su postojali u prethodnoj implementaciji.
    """
    def __init__(self, id=None, tip="vanjski", orijentacija=None, duzina=5.0, visina=None,
                 je_segmentiran=False, segmenti=None, elementi=None):
        """
        Inicijalizacija novog fizičkog zida.
        
        Parameters:
        -----------
        id : str
            Jedinstveni identifikator zida (ako nije naveden, automatski se generira)
        tip : str
            Tip zida ("vanjski", "prema_prostoriji", "prema_negrijanom")
        orijentacija : str
            Orijentacija zida (relevantno samo za vanjske zidove)
        duzina : float
            Duljina zida u metrima
        visina : float
            Visina zida u metrima
        je_segmentiran : bool
            Označava je li zid segmentiran
        segmenti : list
            Lista segmenata zida
        elementi : WallElements
            Elementi na zidu (prozori, vrata)
        """
        self.id = id if id is not None else uuid.uuid4().hex
        self.tip = tip
        self.orijentacija = orijentacija if tip == "vanjski" else None
        self.duzina = float(duzina)
        self.visina = float(visina) if visina is not None else None
        self.je_segmentiran = je_segmentiran
        self.segmenti = segmenti if segmenti is not None else []
        self.elementi = elementi if elementi is not None else WallElements()
        
        # Reference na prostorije koje dijele ovaj zid
        self.povezane_prostorije = []  # [{"prostorija_id": str, "zid_referenca_id": str}, ...]

    def dodaj_povezanu_prostoriju(self, prostorija_id, zid_referenca_id):
        """
        Dodaje povezanu prostoriju na ovaj fizički zid.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se povezuje s ovim zidom
        zid_referenca_id : str
            ID reference na zid u prostoriji (ID rječnika koji predstavlja zid u prostoriji)
        """
        # Provjeri postoji li već ta povezana prostorija
        for povezana in self.povezane_prostorije:
            if povezana["prostorija_id"] == prostorija_id:
                povezana["zid_referenca_id"] = zid_referenca_id
                return
                
        # Ako ne postoji, dodaj je
        self.povezane_prostorije.append({
            "prostorija_id": prostorija_id,
            "zid_referenca_id": zid_referenca_id
        })

    def ukloni_povezanu_prostoriju(self, prostorija_id):
        """
        Uklanja poveznicu s prostorijom.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se odvaja od ovog zida
            
        Returns:
        --------
        bool
            True ako je prostorija uspješno uklonjena, False inače
        """
        prije_len = len(self.povezane_prostorije)
        self.povezane_prostorije = [p for p in self.povezane_prostorije 
                                   if p["prostorija_id"] != prostorija_id]
        return prije_len > len(self.povezane_prostorije)

    def dohvati_povezanu_referencu(self, prostorija_id):
        """
        Dohvaća ID reference na zid u prostoriji.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije za koju se traži referenca
            
        Returns:
        --------
        str or None
            ID reference na zid u prostoriji ili None ako ne postoji
        """
        for povezana in self.povezane_prostorije:
            if povezana["prostorija_id"] == prostorija_id:
                return povezana["zid_referenca_id"]
        return None

    def azuriraj_tip(self, novi_tip):
        """
        Ažurira tip zida.
        
        Parameters:
        -----------
        novi_tip : str
            Novi tip zida
        """
        self.tip = novi_tip
        if novi_tip != "vanjski":
            self.orijentacija = None

    def ima_suprotnu_stranu(self):
        """
        Provjerava ima li zid suprotnu stranu (tj. dijele li ga barem dvije prostorije).
        
        Returns:
        --------
        bool
            True ako zid dijele barem dvije prostorije, False inače
        """
        return len(self.povezane_prostorije) >= 2
    
    def treba_biti_prema_prostoriji(self):
        """
        Određuje treba li zid biti tipa "prema_prostoriji" na temelju broja povezanih prostorija.
        
        Returns:
        --------
        bool
            True ako zid treba biti tipa "prema_prostoriji", False inače
        """
        return self.ima_suprotnu_stranu()

    def osvjezi_tip_na_temelju_povezanosti(self):
        """
        Osvježava tip zida na temelju povezanosti s prostorijama.
        Ako je zid povezan s više prostorija, postaje "prema_prostoriji".
        """
        if self.treba_biti_prema_prostoriji():
            self.azuriraj_tip("prema_prostoriji")

    def to_dict(self):
        """
        Pretvara instancu u rječnik za spremanje.
        
        Returns:
        --------
        dict
            Rječnička reprezentacija fizičkog zida
        """
        return {
            "id": self.id,
            "tip": self.tip,
            "orijentacija": self.orijentacija,
            "duzina": self.duzina,
            "visina": self.visina,
            "je_segmentiran": self.je_segmentiran,
            "segmenti": [segment.to_dict() if hasattr(segment, 'to_dict') else segment for segment in self.segmenti],
            "elementi": self.elementi.to_dict() if hasattr(self.elementi, 'to_dict') else self.elementi,
            "povezane_prostorije": self.povezane_prostorije
        }

    @classmethod
    def from_dict(cls, data):
        """
        Stvara instancu iz rječnika.
        
        Parameters:
        -----------
        data : dict
            Rječnik s podacima
            
        Returns:
        --------
        FizickiZid
            Nova instanca
        """
        elementi = data.get("elementi")
        if isinstance(elementi, dict):
            elementi = WallElements.from_dict(elementi)
            
        segmenti = data.get("segmenti", [])
        processed_segmenti = []
        for segment in segmenti:
            if isinstance(segment, dict):
                processed_segmenti.append(SegmentZida.from_dict(segment))
            else:
                processed_segmenti.append(segment)
        
        instance = cls(
            id=data.get("id"),
            tip=data.get("tip", "vanjski"),
            orijentacija=data.get("orijentacija"),
            duzina=data.get("duzina", 5.0),
            visina=data.get("visina"),
            je_segmentiran=data.get("je_segmentiran", False),
            segmenti=processed_segmenti,
            elementi=elementi
        )
        
        instance.povezane_prostorije = data.get("povezane_prostorije", [])
        
        return instance
