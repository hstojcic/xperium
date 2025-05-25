"""
Modul koji sadrži kontroler za upravljanje etažama.
"""

class EtazaController:
    """Kontroler za upravljanje etažama."""
    
    def __init__(self, model):
        """
        Inicijalizira kontroler.
        
        Parameters:
        -----------
        model : MultiRoomModel
            Model kojim upravlja kontroler
        """
        self.model = model
    
    def dodaj_etazu(self, naziv, redni_broj, visina_etaze):
        """
        Dodaje novu etažu u model.
        
        Parameters:
        -----------
        naziv : str
            Naziv nove etaže
        redni_broj : int
            Redni broj etaže
        visina_etaze : float
            Visina etaže u metrima
            
        Returns:
        --------
        Etaza
            Nova etaža koja je dodana u model
        """
        return self.model.dodaj_etazu(
            naziv=naziv, 
            redni_broj=redni_broj, 
            visina_etaze=visina_etaze
        )
    
    def uredi_etazu(self, etaza_id, naziv=None, redni_broj=None, visina_etaze=None):
        """
        Uređuje postojeću etažu.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže koja se uređuje
        naziv : str
            Novi naziv etaže (ako se mijenja)
        redni_broj : int
            Novi redni broj etaže (ako se mijenja)
        visina_etaze : float
            Nova visina etaže u metrima (ako se mijenja)
            
        Returns:
        --------
        bool
            True ako je etaža uspješno uređena, False inače
        """
        etaza = self.model.dohvati_etazu(etaza_id)
        if not etaza:
            return False
        
        if naziv is not None:
            etaza.naziv = naziv
        
        if redni_broj is not None:
            etaza.redni_broj = redni_broj
        
        if visina_etaze is not None:
            etaza.visina_etaze = float(visina_etaze)
        
        # Ako je promijenjena visina etaže, ažuriramo i zidove u prostorijama
        if visina_etaze is not None:
            prostorije = self.model.dohvati_prostorije_za_etazu(etaza_id)
            for prostorija in prostorije:
                if prostorija.koristi_zadanu_visinu:
                    for zid in prostorija.zidovi:
                        zid["visina"] = float(visina_etaze)
        
        # Spremanje promjena u model
        self.model._spremi_u_session_state()
        
        return True
    
    def ukloni_etazu(self, etaza_id):
        """
        Uklanja etažu iz modela.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže koja se uklanja
            
        Returns:
        --------
        bool
            True ako je etaža uspješno uklonjena, False inače
        """
        etaza = self.model.dohvati_etazu(etaza_id)
        if not etaza:
            return False
        
        # Provjerimo ima li prostorija na etaži
        prostorije = self.model.dohvati_prostorije_za_etazu(etaza_id)
        if prostorije:
            return False  # Ne dopuštamo brisanje etaže s prostorijama
        
        # Uklanjamo etažu
        self.model.ukloni_etazu(etaza_id)
        
        return True
