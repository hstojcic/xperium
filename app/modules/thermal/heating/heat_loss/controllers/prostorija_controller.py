"""
Modul koji sadrži kontroler za upravljanje prostorijama.
"""

from ..utils.validators import validate_number

class ProstorijaController:
    """Kontroler za upravljanje prostorijama."""
    
    def __init__(self, model):
        """
        Inicijalizira kontroler.
        
        Parameters:
        -----------
        model : MultiRoomModel
            Model kojim upravlja kontroler
        """
        self.model = model
    
    def dodaj_prostoriju(self, etaza_id, naziv, tip, povrsina, visina=None, koristi_zadanu_visinu=True):
        """
        Dodaje novu prostoriju u model.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže u koju se dodaje prostorija
        naziv : str
            Naziv nove prostorije
        tip : str
            Tip prostorije
        povrsina : float
            Površina prostorije u m²
        visina : float
            Visina prostorije u m (ako se ne koristi zadana visina etaže)
        koristi_zadanu_visinu : bool
            Određuje hoće li se koristiti zadana visina etaže
            
        Returns:
        --------
        Prostorija or None
            Nova prostorija koja je dodana u model ili None ako etaža ne postoji
        """
        # Validacija etaže
        etaza = self.model.dohvati_etazu(etaza_id)
        if not etaza:
            return None
        
        # Validacija površine
        povrsina = validate_number(povrsina, min_value=1.0, default=20.0)
        
        # Dodavanje prostorije
        prostorija = self.model.dodaj_prostoriju(
            etaza_id=etaza_id,
            naziv=naziv,
            tip=tip,
            povrsina=povrsina
        )
        
        if prostorija:
            prostorija.koristi_zadanu_visinu = koristi_zadanu_visinu
            if not koristi_zadanu_visinu and visina is not None:
                prostorija.visina = validate_number(visina, min_value=2.0, max_value=6.0, default=etaza.visina_etaze)
            
            # Spremanje promjena u model
            self.model._spremi_u_session_state()
        
        return prostorija
    
    def uredi_prostoriju(self, prostorija_id, naziv=None, tip=None, povrsina=None, 
                         visina=None, koristi_zadanu_visinu=None, temp_unutarnja=None, 
                         izmjene_zraka=None, temperatura_susjednog_negrijanog=None,
                         pod_tip=None, strop_tip=None):
        """
        Uređuje postojeću prostoriju.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se uređuje
        naziv : str
            Novi naziv prostorije (ako se mijenja)
        tip : str
            Novi tip prostorije (ako se mijenja)
        povrsina : float
            Nova površina prostorije u m² (ako se mijenja)
        visina : float
            Nova visina prostorije u m (ako se mijenja)
        koristi_zadanu_visinu : bool
            Određuje hoće li se koristiti zadana visina etaže (ako se mijenja)
        temp_unutarnja : float
            Nova unutarnja temperatura prostorije u °C (ako se mijenja)
        izmjene_zraka : float
            Novi broj izmjena zraka u h⁻¹ (ako se mijenja)
        temperatura_susjednog_negrijanog : float
            Nova temperatura susjednog negrijanog prostora u °C (ako se mijenja)
        pod_tip : str
            Novi tip poda (ako se mijenja)
        strop_tip : str
            Novi tip stropa (ako se mijenja)
            
        Returns:
        --------
        bool
            True ako je prostorija uspješno uređena, False inače
        """
        # Dohvaćanje prostorije
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return False
        
        # Dohvaćanje etaže
        etaza = self.model.dohvati_etazu(prostorija.etaza_id)
        
        # Ažuriranje podataka prostorije
        if naziv is not None:
            prostorija.naziv = naziv
        
        if tip is not None:
            prostorija.azuriraj_tip_prostorije(tip)
        
        if povrsina is not None:
            prostorija.povrsina = validate_number(povrsina, min_value=1.0, default=20.0)
        
        if koristi_zadanu_visinu is not None:
            prostorija.koristi_zadanu_visinu = koristi_zadanu_visinu
            
            # Ako smo prebacili na korištenje zadane visine, postavimo visinu na None
            if koristi_zadanu_visinu:
                prostorija.visina = None
                
                # Ažuriranje visine zidova
                if etaza:
                    for zid in prostorija.zidovi:
                        zid["visina"] = etaza.visina_etaze
        
        if not prostorija.koristi_zadanu_visinu and visina is not None:
            prostorija.visina = validate_number(visina, min_value=2.0, max_value=6.0, default=etaza.visina_etaze if etaza else 2.8)
            
            # Ažuriranje visine zidova
            for zid in prostorija.zidovi:
                zid["visina"] = prostorija.visina
        
        if temp_unutarnja is not None:
            prostorija.temp_unutarnja = validate_number(temp_unutarnja, min_value=5.0, max_value=30.0, default=20.0)
        
        if izmjene_zraka is not None:
            prostorija.izmjene_zraka = validate_number(izmjene_zraka, min_value=0.1, max_value=5.0, default=0.5)
        
        if temperatura_susjednog_negrijanog is not None:
            prostorija.temperatura_susjednog_negrijanog = validate_number(temperatura_susjednog_negrijanog, min_value=-20.0, max_value=20.0, default=10.0)
        
        if pod_tip is not None:
            prostorija.pod_tip = pod_tip
        
        if strop_tip is not None:
            prostorija.strop_tip = strop_tip
        
        # Spremanje promjena u model
        self.model._spremi_u_session_state()
        
        return True
    
    def ukloni_prostoriju(self, prostorija_id):
        """
        Uklanja prostoriju iz modela.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se uklanja
            
        Returns:
        --------
        bool
            True ako je prostorija uspješno uklonjena, False inače
        """
        # Dohvaćanje prostorije
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return False
        
        # Uklanjanje prostorije
        self.model.ukloni_prostoriju(prostorija_id)
        
        return True
