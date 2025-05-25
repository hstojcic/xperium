"""
Modul koji sadrži klasu WallElements za upravljanje elementima na zidu.
Prilagođena verzija koja omogućuje jednostavno korištenje u heat_loss kalkulatoru.
"""

class WallElements:
    """
    Klasa koja predstavlja elemente na zidu (prozore i vrata).
    Pojednostavljena implementacija za heat_loss kalkulator.
    """
    def __init__(self):
        self.prozori = []  # Lista instanci prozora na zidu
        self.vrata = []    # Lista instanci vrata na zidu
        self._next_prozor_id = 1
        self._next_vrata_id = 1
    
    def dodaj_prozor(self, tip_id, tip_naziv, sirina=None, visina=None):
        """
        Dodaje novi prozor na zid.
        
        Parameters:
        -----------
        tip_id : str
            ID tipa prozora iz kataloga
        tip_naziv : str
            Naziv tipa prozora (za informativni prikaz)
        sirina : float
            Opcionalna širina u metrima - ako nije navedena, koristi se standardna iz kataloga
        visina : float
            Opcionalna visina u metrima - ako nije navedena, koristi se standardna iz kataloga
        """
        koristiti_standardne_dimenzije = sirina is None or visina is None
        
        prozor = {
            "id": self._next_prozor_id,
            "tip_id": tip_id,
            "tip_naziv": tip_naziv,
            "sirina": sirina,  # Može biti None - tada se koriste standardne dimenzije
            "visina": visina,  # Može biti None - tada se koriste standardne dimenzije
            "koristiti_standardne_dimenzije": koristiti_standardne_dimenzije
        }
        self.prozori.append(prozor)
        self._next_prozor_id += 1
        return prozor
    
    def dodaj_vrata(self, tip_id, tip_naziv, sirina=None, visina=None):
        """
        Dodaje nova vrata na zid.
        
        Parameters:
        -----------
        tip_id : str
            ID tipa vrata iz kataloga
        tip_naziv : str
            Naziv tipa vrata (za informativni prikaz)
        sirina : float
            Opcionalna širina u metrima - ako nije navedena, koristi se standardna iz kataloga
        visina : float
            Opcionalna visina u metrima - ako nije navedena, koristi se standardna iz kataloga
        """
        koristiti_standardne_dimenzije = sirina is None or visina is None
        
        vrata = {
            "id": self._next_vrata_id,
            "tip_id": tip_id,
            "tip_naziv": tip_naziv,
            "sirina": sirina,  # Može biti None - tada se koriste standardne dimenzije
            "visina": visina,  # Može biti None - tada se koriste standardne dimenzije
            "koristiti_standardne_dimenzije": koristiti_standardne_dimenzije
        }
        self.vrata.append(vrata)
        self._next_vrata_id += 1
        return vrata
    
    def ukloni_prozor(self, prozor_id):
        """Uklanja prozor sa zida prema ID-u"""
        self.prozori = [p for p in self.prozori if p["id"] != prozor_id]
    
    def ukloni_vrata(self, vrata_id):
        """Uklanja vrata sa zida prema ID-u"""
        self.vrata = [v for v in self.vrata if v["id"] != vrata_id]
    
    def izracunaj_ukupnu_povrsinu_prozora(self, prozori_katalog=None):
        """
        Izračunava ukupnu površinu svih prozora na zidu.
        
        Parameters:
        -----------
        prozori_katalog : dict
            Katalog s definiranim tipovima prozora, gdje su ključevi ID-ovi
            
        Returns:
        --------
        float
            Ukupna površina prozora u m²
        """
        ukupna_povrsina = 0.0
        
        if not prozori_katalog or not self.prozori:
            return ukupna_povrsina
            
        for prozor in self.prozori:
            tip_id = prozor.get("tip_id")
            
            # Ako su definirane vlastite dimenzije, koristi njih
            if not prozor.get("koristiti_standardne_dimenzije", True):
                sirina = prozor.get("sirina", 0)
                visina = prozor.get("visina", 0)
                if sirina and visina:
                    ukupna_povrsina += sirina * visina
                continue
                
            # Inače koristi dimenzije iz kataloga
            if tip_id in prozori_katalog:
                tip_prozora = prozori_katalog[tip_id]
                if hasattr(tip_prozora, 'povrsina'):
                    ukupna_povrsina += tip_prozora.povrsina
                elif hasattr(tip_prozora, 'sirina') and hasattr(tip_prozora, 'visina'):
                    ukupna_povrsina += tip_prozora.sirina * tip_prozora.visina
                    
        return ukupna_povrsina
    
    def izracunaj_ukupnu_povrsinu_vrata(self, vrata_katalog=None):
        """
        Izračunava ukupnu površinu svih vrata na zidu.
        
        Parameters:
        -----------
        vrata_katalog : dict
            Katalog s definiranim tipovima vrata, gdje su ključevi ID-ovi
            
        Returns:
        --------
        float
            Ukupna površina vrata u m²
        """
        ukupna_povrsina = 0.0
        
        if not vrata_katalog or not self.vrata:
            return ukupna_povrsina
            
        for vrata_item in self.vrata:
            tip_id = vrata_item.get("tip_id")
            
            # Ako su definirane vlastite dimenzije, koristi njih
            if not vrata_item.get("koristiti_standardne_dimenzije", True):
                sirina = vrata_item.get("sirina", 0)
                visina = vrata_item.get("visina", 0)
                if sirina and visina:
                    ukupna_povrsina += sirina * visina
                continue
                
            # Inače koristi dimenzije iz kataloga
            if tip_id in vrata_katalog:
                tip_vrata = vrata_katalog[tip_id]
                if hasattr(tip_vrata, 'povrsina'):
                    ukupna_povrsina += tip_vrata.povrsina
                elif hasattr(tip_vrata, 'sirina') and hasattr(tip_vrata, 'visina'):
                    ukupna_povrsina += tip_vrata.sirina * tip_vrata.visina
                    
        return ukupna_povrsina
        
    def to_dict(self):
        """Pretvara objekt u rječnik za spremanje"""
        return {
            "prozori": self.prozori,
            "vrata": self.vrata,
            "_next_prozor_id": self._next_prozor_id,
            "_next_vrata_id": self._next_vrata_id,
        }
        
    @classmethod
    def from_dict(cls, data):
        """Stvara objekt iz rječnika"""
        instance = cls()
        instance.prozori = data.get("prozori", [])
        instance.vrata = data.get("vrata", [])
        instance._next_prozor_id = data.get("_next_prozor_id", 1)
        instance._next_vrata_id = data.get("_next_vrata_id", 1)
        return instance
        
    def get(self, key, default=None):
        """
        Implementacija metode get kao kod rječnika.
        Omogućuje da se objekt koristi kao rječnik s metodom get.
        
        Parameters:
        -----------
        key : str
            Ključ za pristup
        default : Any
            Zadana vrijednost ako ključ ne postoji
            
        Returns:
        --------
        Any
            Vrijednost za ključ ili default ako ključ ne postoji
        """
        if key == "prozori":
            return self.prozori
        elif key == "vrata":
            return self.vrata
        return default
