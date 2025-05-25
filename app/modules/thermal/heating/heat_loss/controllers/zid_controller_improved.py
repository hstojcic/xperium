"""
Modul koji sadrži klasu za kontroliranje zidova u modelu toplinskih gubitaka.
"""

class ZidController:
    """Klasa koja upravlja zidovima u modelu."""
    
    def __init__(self, model):
        """
        Inicijalizira kontroler za rad sa zidovima.
        
        Parameters:
        -----------
        model : MultiRoomModel
            Model s prostorijama i zidovima
        """
        self.model = model
    
    def dodaj_zid(self, prostorija_id, tip_zida, duzina, visina_zida=None, 
                 orijentacija=None, povezana_prostorija_id=None,
                 je_segmentiran=False):
        """
        Dodaje zid u prostoriju.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije u koju se dodaje zid
        tip_zida : str
            Tip zida ("vanjski", "prema_prostoriji", itd.)
        duzina : float
            Duljina zida u metrima
        visina_zida : float
            Visina zida u metrima (ako je None, koristi se visina etaže)
        orijentacija : str
            Orijentacija zida (relevantno samo za vanjski zid)
        povezana_prostorija_id : str
            ID povezane prostorije (za zidove tipa "prema_prostoriji")
        je_segmentiran : bool
            Označava je li zid segmentiran
        
        Returns:
        --------
        str or None
            ID novog zida ili None ako prostorija nije pronađena
        """
        try:
            zid_id = self.model.add_wall_to_room(
                prostorija_id=prostorija_id,
                tip_zida=tip_zida,
                duzina=duzina,
                visina_zida=visina_zida,
                orijentacija=orijentacija,
                povezana_ciljna_prostorija_id=povezana_prostorija_id,
                je_segmentiran=je_segmentiran
            )
            
            return zid_id
        except Exception as e:
            import traceback
            traceback.print_exc()
            return None
    
    def obrisi_zid(self, prostorija_id, zid_id):
        """
        Briše zid iz prostorije.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije iz koje se briše zid
        zid_id : str
            ID zida koji se briše
        
        Returns:
        --------
        bool
            True ako je zid uspješno obrisan, False inače
        """
        try:
            return self.model.obrisi_zid_iz_prostorije(prostorija_id, zid_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    def dohvati_zid(self, prostorija_id, zid_id):
        """
        Dohvaća zid iz prostorije.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije
        zid_id : str
            ID zida
        
        Returns:
        --------
        dict or None
            Zid ili None ako ne postoji
        """
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return None
        
        return prostorija.dohvati_zid(zid_id)
    
    def analiziraj_povezanost_zidova(self):
        """
        Analizira prostorije i identificira potencijalno povezane zidove.
        
        Returns:
        --------
        list
            Lista potencijalnih povezivanja zidova
        """
        try:
            return self.model.analiziraj_povezanost_zidova()
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
    
    def povezi_zidove(self, prostorija1_id, zid1_id, prostorija2_id, zid2_id):
        """
        Povezuje dva zida u različitim prostorijama kao isti fizički zid.
        
        Parameters:
        -----------
        prostorija1_id, prostorija2_id : str
            ID prostorija čiji se zidovi povezuju
        zid1_id, zid2_id : str
            ID zidova koji se povezuju
            
        Returns:
        --------
        bool
            True ako je povezivanje uspjelo, False inače
        """
        try:
            return self.model.povezi_zidove(prostorija1_id, zid1_id, prostorija2_id, zid2_id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
