"""
Modul koji sadrži kontroler za upravljanje zidovima.
"""

from ..utils.validators import validate_number

class ZidController:
    """Kontroler za upravljanje zidovima."""
    
    def __init__(self, model):
        """
        Inicijalizira kontroler.
        
        Parameters:
        -----------
        model : MultiRoomModel
            Model kojim upravlja kontroler
        """
        self.model = model
    
    def dodaj_zid(self, prostorija_id, tip_zida, duzina, visina_zida=None, 
                 orijentacija=None, povezana_prostorija_id=None, 
                 je_segmentiran=False, tip_zida_id=None):
        """
        Dodaje novi zid u prostoriju.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije u koju se dodaje zid
        tip_zida : str
            Tip zida ("vanjski", "prema_prostoriji", "prema_negrijanom")
        duzina : float
            Duljina zida u m
        visina_zida : float
            Visina zida u m (ako se ne koristi zadana visina etaže)
        orijentacija : str
            Orijentacija zida (za vanjske zidove)
        povezana_prostorija_id : str
            ID povezane prostorije (za zidove tipa "prema_prostoriji")
        je_segmentiran : bool
            Određuje je li zid segmentiran
        tip_zida_id : str
            ID tipa zida iz kataloga
            
        Returns:
        --------
        str or None
            ID novog zida ili None ako dodavanje nije uspjelo
        """
        # Validacija duljine
        duzina = validate_number(duzina, min_value=0.1, default=5.0)
        
        # Dodavanje zida
        return self.model.add_wall_to_room(
            prostorija_id=prostorija_id,
            tip_zida=tip_zida,
            duzina=duzina,
            visina_zida=visina_zida,
            orijentacija=orijentacija,
            povezana_ciljna_prostorija_id=povezana_prostorija_id,
            je_segmentiran=je_segmentiran,
            tip_zida_id=tip_zida_id
        )
    
    def uredi_zid(self, prostorija_id, zid_id, duzina=None, visina=None, 
                 orijentacija=None, je_segmentiran=None):
        """
        Uređuje postojeći zid.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije u kojoj se nalazi zid
        zid_id : str
            ID zida koji se uređuje
        duzina : float
            Nova duljina zida u m (ako se mijenja)
        visina : float
            Nova visina zida u m (ako se mijenja)
        orijentacija : str
            Nova orijentacija zida (za vanjske zidove, ako se mijenja)
        je_segmentiran : bool
            Određuje je li zid segmentiran (ako se mijenja)
            
        Returns:
        --------
        bool
            True ako je zid uspješno uređen, False inače
        """
        # Dohvaćanje prostorije
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return False
        
        # Dohvaćanje zida
        zid = prostorija.dohvati_zid(zid_id)
        if not zid:
            return False
        
        # Ažuriranje podataka zida
        if duzina is not None:
            zid["duzina"] = validate_number(duzina, min_value=0.1, default=5.0)
        
        if visina is not None:
            zid["visina"] = validate_number(visina, min_value=0.1, default=2.8)
        
        if zid.get("tip") == "vanjski" and orijentacija is not None:
            zid["orijentacija"] = orijentacija
        
        if je_segmentiran is not None:
            zid["je_segmentiran"] = je_segmentiran
        
        # Spremanje promjena u model
        self.model._spremi_u_session_state()
        
        return True
    
    def ukloni_zid(self, prostorija_id, zid_id):
        """
        Uklanja zid iz prostorije.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije iz koje se uklanja zid
        zid_id : str
            ID zida koji se uklanja
            
        Returns:
        --------
        bool
            True ako je zid uspješno uklonjen, False inače
        """
        return self.model.obrisi_zid_iz_prostorije(prostorija_id, zid_id)
    
    def dodaj_prozor_na_zid(self, prostorija_id, zid_id, tip_prozora_id, tip_prozora_naziv, dodatni_podaci=None):
        """
        Dodaje prozor na zid.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije u kojoj se nalazi zid
        zid_id : str
            ID zida na koji se dodaje prozor
        tip_prozora_id : str
            ID tipa prozora iz kataloga
        tip_prozora_naziv : str
            Naziv tipa prozora
        dodatni_podaci : dict, optional
            Dodatni podaci o prozoru (sirina, visina, u_vrijednost, itd.)
            
        Returns:
        --------
        dict or None
            Dodani prozor ili None ako dodavanje nije uspjelo
        """
        # Dohvaćanje prostorije
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return None
        
        # Dohvaćanje zida
        zid = prostorija.dohvati_zid(zid_id)
        if not zid:
            return None
        
        # Dohvaćanje elemenata zida
        elementi = zid.get("elementi")
        if not elementi:
            return None
        
        # Postavljanje dimenzija iz dodatnih podataka
        sirina = None
        visina = None
        if dodatni_podaci:
            sirina = dodatni_podaci.get("sirina")
            visina = dodatni_podaci.get("visina")
        
        # Dodavanje prozora
        prozor = elementi.dodaj_prozor(tip_prozora_id, tip_prozora_naziv, sirina, visina)
        
        # Dodaj dodatne podatke ako postoje
        if dodatni_podaci and prozor:
            for key, value in dodatni_podaci.items():
                if key not in ["sirina", "visina"]:  # Ove podatke već obrađujemo kroz dodaj_prozor
                    prozor[key] = value
        # Spremanje promjena u model
        self.model._spremi_u_session_state()
        
        return prozor
    
    def dodaj_vrata_na_zid(self, prostorija_id, zid_id, tip_vrata_id, tip_vrata_naziv, dodatni_podaci=None):
        """
        Dodaje vrata na zid.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije u kojoj se nalazi zid
        zid_id : str
            ID zida na koji se dodaju vrata
        tip_vrata_id : str
            ID tipa vrata iz kataloga
        tip_vrata_naziv : str
            Naziv tipa vrata
        dodatni_podaci : dict, optional
            Dodatni podaci o vratima (sirina, visina, u_vrijednost, itd.)
            
        Returns:
        --------
        dict or None
            Dodana vrata ili None ako dodavanje nije uspjelo
        """
        # Dohvaćanje prostorije
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return None
        
        # Dohvaćanje zida
        zid = prostorija.dohvati_zid(zid_id)
        if not zid:
            return None
        
        # Dohvaćanje elemenata zida
        elementi = zid.get("elementi")
        if not elementi:
            return None
        
        # Postavljanje dimenzija iz dodatnih podataka
        sirina = None
        visina = None
        if dodatni_podaci:
            sirina = dodatni_podaci.get("sirina")
            visina = dodatni_podaci.get("visina")
        
        # Dodavanje vrata
        vrata = elementi.dodaj_vrata(tip_vrata_id, tip_vrata_naziv, sirina, visina)
        
        # Dodaj dodatne podatke ako postoje
        if dodatni_podaci and vrata:
            for key, value in dodatni_podaci.items():
                if key not in ["sirina", "visina"]:  # Ove podatke već obrađujemo kroz dodaj_vrata
                    vrata[key] = value
        
        # Spremanje promjena u model
        self.model._spremi_u_session_state()
        
        return vrata
    
    def ukloni_prozor(self, prostorija_id, zid_id, prozor_id):
        """
        Uklanja prozor sa zida.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije u kojoj se nalazi zid
        zid_id : str
            ID zida s kojeg se uklanja prozor
        prozor_id : int
            ID prozora koji se uklanja
            
        Returns:
        --------
        bool
            True ako je prozor uspješno uklonjen, False inače
        """
        # Dohvaćanje prostorije
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return False
        
        # Dohvaćanje zida
        zid = prostorija.dohvati_zid(zid_id)
        if not zid:
            return False
        
        # Dohvaćanje elemenata zida
        elementi = zid.get("elementi")
        if not elementi:
            return False
        
        # Uklanjanje prozora
        elementi.ukloni_prozor(prozor_id)
        
        # Spremanje promjena u model
        self.model._spremi_u_session_state()
        
        return True
    
    def ukloni_vrata(self, prostorija_id, zid_id, vrata_id):
        """
        Uklanja vrata sa zida.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije u kojoj se nalazi zid
        zid_id : str
            ID zida s kojeg se uklanjaju vrata
        vrata_id : int
            ID vrata koja se uklanjaju
            
        Returns:
        --------
        bool
            True ako su vrata uspješno uklonjena, False inače
        """
        # Dohvaćanje prostorije
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return False
        
        # Dohvaćanje zida
        zid = prostorija.dohvati_zid(zid_id)
        if not zid:
            return False
        
        # Dohvaćanje elemenata zida
        elementi = zid.get("elementi")
        if not elementi:
            return False
        
        # Uklanjanje vrata
        elementi.ukloni_vrata(vrata_id)
        
        # Spremanje promjena u model
        self.model._spremi_u_session_state()
        
        return True
