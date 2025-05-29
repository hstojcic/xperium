"""
Modul koji sadrži glavnu klasu modela za proračun toplinskih gubitaka.
"""

import streamlit as st
import uuid
from .etaza import Etaza
from .prostorija import Prostorija

from .elementi.wall_elements import WallElements
from .elementi.fizicki_zid import FizickiZid

class MultiRoomModel:
    """
    Model koji upravlja s više prostorija, etaža i njihovim vezama.
    
    Ova verzija koristi centralizirani sustav upravljanja fizičkim zidovima, što omogućuje
    da više prostorija dijeli isti fizički zid, eliminirajući probleme nedosljednosti.
    """
    
    def __init__(self, session_key):
        self.session_key = session_key
        self.etaze = []
        self.prostorije = []
        self.fizicki_zidovi = {}  # Rječnik fizičkih zidova {id: FizickiZid}
        self._fizicki_elementi = {}  # Rječnik s fizičkim elementima za proračun
        self._ucitaj_iz_session_state()
        
    def _ucitaj_iz_session_state(self):
        """Učitava model iz Streamlit session state-a."""
        current_data_in_state = st.session_state.get(self.session_key)

        # Provjera i oporavak od neispravno spremljene instance modela u session state
        if isinstance(current_data_in_state, MultiRoomModel):
            try:
                # Pokušaj konverzije instance u rječnik
                converted_dict = {
                    "etaze": [e.to_dict() for e in current_data_in_state.etaze],
                    "prostorije": [p.to_dict() for p in current_data_in_state.prostorije],
                    "fizicki_zidovi": {zid_id: zid.to_dict() for zid_id, zid in current_data_in_state.fizicki_zidovi.items()}
                }
                st.session_state[self.session_key] = converted_dict
                current_data_in_state = st.session_state[self.session_key]  # Sada bi trebao biti rječnik
            except (AttributeError, TypeError):
                # Ako konverzija ne uspije, obriši neispravno stanje
                del st.session_state[self.session_key]
                current_data_in_state = None
        elif current_data_in_state is not None and not isinstance(current_data_in_state, dict):
            # Ako je u session state nešto što nije ni rječnik, ni None, ni MultiRoomModel instanca
            del st.session_state[self.session_key]
            current_data_in_state = None
        
        if current_data_in_state:  # Ovdje bi current_data_in_state trebao biti rječnik ili None
            saved_state = current_data_in_state
            
            # Load fizicki zidovi
            fizicki_zidovi_data = saved_state.get("fizicki_zidovi", {})
            for zid_id, zid_data in fizicki_zidovi_data.items():
                try:
                    fizicki_zid_obj = FizickiZid.from_dict(zid_data)
                    self.fizicki_zidovi[zid_id] = fizicki_zid_obj
                except Exception:
                    # st.warning(f"Greška pri učitavanju fizičkog zida: {e}")
                    pass  # Preskoči zid koji se ne može učitati
            
            # Load etaze
            etaze_data = saved_state.get("etaze", [])
            loaded_etaze_temp = []
            for e_data in etaze_data:
                try:
                    # Pretpostavljamo da Etaza.from_dict() vraća Etaza objekt ili None/iznimku za neispravne podatke
                    etaza_obj = Etaza.from_dict(e_data)
                    if isinstance(etaza_obj, Etaza):  # Provjeravamo je li objekt instanca klase Etaza
                        loaded_etaze_temp.append(etaza_obj)
                except Exception:
                    # Možete dodati st.warning za neuspjelo učitavanje etaže, za debugiranje
                    # npr. st.warning(f"Greška pri učitavanju etaže: {e}")
                    pass  # Preskoči etažu koja se ne može učitati            self.etaze = loaded_etaze_temp
            
            # Load prostorije
            prostorije_data = saved_state.get("prostorije", [])
            loaded_prostorije_temp = []
            for p_data in prostorije_data:
                try:
                    prostorija_obj = Prostorija.from_dict(p_data, self)
                    if isinstance(prostorija_obj, Prostorija): # Provjeravamo je li objekt instanca klase Prostorija
                        loaded_prostorije_temp.append(prostorija_obj)
                except Exception:
                    # st.warning(f"Greška pri učitavanju prostorije: {e}")
                    pass  # Preskoči prostoriju koja se ne može učitati
              # Assign loaded prostorije to the model
            self.prostorije = loaded_prostorije_temp
        else:
            self._inicijaliziraj_zadano_stanje()
            
        if not self.etaze:
            self.dodaj_etazu(naziv="Prizemlje", redni_broj=1, visina_etaze=2.5, spremi=False)
        
        self.restore_shared_elements_references()
        self._spremi_u_session_state()
    
    def _inicijaliziraj_zadano_stanje(self):
        """Inicijalizira model s praznim listama etaža i prostorija."""
        self.etaze = []
        self.prostorije = []
    
    # === METODE ZA UPRAVLJANJE ETAŽAMA ===
    
    def _spremi_u_session_state(self):
        """Sprema model u Streamlit session state."""
        stanje = {
            "etaze": [e.to_dict() for e in self.etaze],
            "prostorije": [p.to_dict() for p in self.prostorije],
            "fizicki_zidovi": {zid_id: zid.to_dict() for zid_id, zid in self.fizicki_zidovi.items()}
        }
        st.session_state[self.session_key] = stanje

    def restore_shared_elements_references(self):
        """
        Obnavlja reference između povezanih zidova.
        Ova metoda osigurava da zidovi koji su međusobno povezani dijele isti
        objekt za elemente (prozore, vrata).
        """
        processed_zid_ids_for_elements_sharing = set()

        for prostorija in self.prostorije:
            for zid in prostorija.zidovi:
                zid_id = zid.get("id")
                if zid_id in processed_zid_ids_for_elements_sharing:
                    continue  # Skip walls we've already processed
                processed_zid_ids_for_elements_sharing.add(zid_id)

                povezani_zid_id = zid.get("povezani_zid_id")
                povezana_prostorija_id = zid.get("povezana_prostorija_id")

                if povezani_zid_id and povezana_prostorija_id:
                    povezana_prostorija = self.dohvati_prostoriju(povezana_prostorija_id)
                    if povezana_prostorija:
                        for povezani_zid in povezana_prostorija.zidovi:
                            if povezani_zid.get("id") == povezani_zid_id:
                                # Ensure both walls share the same WallElements object
                                if not isinstance(zid.get("elementi"), WallElements):
                                    zid["elementi"] = WallElements()
                                if not isinstance(povezani_zid.get("elementi"), WallElements):
                                    povezani_zid["elementi"] = WallElements()
                                
                                # Set both walls to use the same elements object
                                povezani_zid["elementi"] = zid["elementi"]
                                break
                elif not isinstance(zid.get("elementi"), WallElements):
                    zid["elementi"] = WallElements()
    
    def dodaj_etazu(self, naziv="Nova etaža", redni_broj=None, visina_etaze=2.5, broj_etaze=None, spremi=True):
        """
        Dodaje novu etažu u model.
        
        Parameters:
        -----------
        naziv : str
            Naziv nove etaže
        redni_broj : int
            Redni broj etaže (ako nije naveden, automatski se generira)
        visina_etaze : float
            Visina etaže u metrima
        broj_etaze : int
            Broj etaže za numeraciju prostorija (ako nije naveden, koristi se redni_broj)
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
            
        Returns:
        --------
        Etaza
            Nova etaža koja je dodana u model
        """
        if redni_broj is None:
            redni_broj = (max(e.redni_broj for e in self.etaze) + 1) if self.etaze else 1
        
        if any(e.redni_broj == redni_broj for e in self.etaze):
            redni_broj = (max(e.redni_broj for e in self.etaze) + 1) if self.etaze else 1
        
        etaza = Etaza(naziv=naziv, redni_broj=redni_broj, visina_etaze=visina_etaze, broj_etaze=broj_etaze)
        self.etaze.append(etaza)
        self.etaze.sort(key=lambda e: e.redni_broj)
        
        if spremi:
            self._spremi_u_session_state()
        return etaza

    def ukloni_etazu(self, etaza_id, spremi=True):
        """
        Uklanja etažu iz modela.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže koja se uklanja
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
        """
        etaza_za_uklanjanje = self.dohvati_etazu(etaza_id)
        if not etaza_za_uklanjanje:
            return
        
        prostorije_na_uklonjenoj_etazi_ids = {p.id for p in self.dohvati_prostorije_za_etazu(etaza_id)}
        self.prostorije = [p for p in self.prostorije if p.etaza_id != etaza_id]
        self.etaze = [e for e in self.etaze if e.id != etaza_id]
        
        if spremi:
            self._spremi_u_session_state()

    def dohvati_etazu(self, etaza_id):
        """
        Dohvaća etažu po ID-u.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže koja se dohvaća
            
        Returns:
        --------
        Etaza or None
            Etaža s navedenim ID-om ili None ako ne postoji
        """
        for e in self.etaze:
            if e.id == etaza_id:
                return e
        return None

    def dohvati_prostorije_za_etazu(self, etaza_id):
        """
        Dohvaća sve prostorije koje pripadaju određenoj etaži.

        Parameters:
        -----------
        etaza_id : str
            ID etaže za koju se dohvaćaju prostorije.

        Returns:
        --------
        list[Prostorija]
            Lista prostorija koje pripadaju navedenoj etaži.
        """
        return [p for p in self.prostorije if p.etaza_id == etaza_id]

    def dodaj_prostoriju(self, etaza_id, naziv="Nova prostorija", tip="Dnevni boravak", povrsina=20.0, spremi=True):
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
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
            
        Returns:
        --------
        Prostorija
            Nova prostorija koja je dodana u model
        """
        etaza = self.dohvati_etazu(etaza_id)
        if not etaza:
            return None        
        prostorija = Prostorija(
            naziv=naziv,
            tip=tip,
            povrsina=povrsina,
            etaza_id=etaza_id,
            model_ref=self
        )
        
        self.prostorije.append(prostorija)
        
        if spremi:
            self._spremi_u_session_state()
        return prostorija

    def ukloni_prostoriju(self, prostorija_id, spremi=True):
        """
        Uklanja prostoriju iz modela.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se uklanja
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
        """
        prostorija_za_uklanjanje = self.dohvati_prostoriju(prostorija_id)
        if not prostorija_za_uklanjanje:
            return        # Ukloni prostoriju iz modela
        self.prostorije = [p for p in self.prostorije if p.id != prostorija_id]
        
        if spremi:
            self._spremi_u_session_state()

    def dohvati_prostoriju(self, prostorija_id):
        """
        Dohvaća prostoriju po ID-u.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se dohvaća
            
        Returns:
        --------
        Prostorija or None
            Prostorija s navedenim ID-om ili None ako ne postoji
        """
        for p in self.prostorije:
            if p.id == prostorija_id:
                return p
        return None

    def uredi_prostoriju(self, prostorija_id, naziv=None, tip=None, povrsina=None, spremi=True):
        """
        Uređuje postojeću prostoriju.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se uređuje
        naziv : str, optional
            Novi naziv prostorije
        tip : str, optional
            Novi tip prostorije
        povrsina : float, optional
            Nova površina prostorije
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
            
        Returns:
        --------
        Prostorija or None
            Uređena prostorija ili None ako prostorija ne postoji
        """
        prostorija = self.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return None
        
        if naziv is not None:
            prostorija.naziv = naziv
        if tip is not None:
            prostorija.tip = tip
        if povrsina is not None:
            prostorija.povrsina = povrsina
        
        if spremi:
            self._spremi_u_session_state()
        return prostorija

    def dupliciraj_prostoriju(self, prostorija_id, novi_naziv=None, spremi=True):
        """
        Duplicira postojeću prostoriju.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se duplicira
        novi_naziv : str, optional
            Naziv nove prostorije (ako nije naveden, koristi se "Kopija od {originalni_naziv}")
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
            
        Returns:
        --------
        Prostorija or None
            Nova prostorija ili None ako originalna ne postoji
        """
        originalna = self.dohvati_prostoriju(prostorija_id)
        if not originalna:
            return None
        
        if novi_naziv is None:
            novi_naziv = f"Kopija od {originalna.naziv}"        
        nova_prostorija = Prostorija(
            naziv=novi_naziv,
            tip=originalna.tip,
            povrsina=originalna.povrsina,
            etaza_id=originalna.etaza_id,            model_ref=self
        )
        
        # Kopiraj zidove
        nova_prostorija.zidovi = [zid.copy() for zid in originalna.zidovi]
        
        self.prostorije.append(nova_prostorija)
        
        if spremi:
            self._spremi_u_session_state()
        return nova_prostorija

    def izracunaj_ukupne_gubitke(self):
        """
        Izračunava ukupne gubitke topline za sve prostorije u modelu.
        
        Returns:
        --------
        float
            Ukupni gubici topline u W
        """
        ukupni_gubici = 0
        for prostorija in self.prostorije:
            if hasattr(prostorija, 'ukupni_gubici'):
                ukupni_gubici += prostorija.ukupni_gubici
        return ukupni_gubici

    def izracunaj_ukupnu_povrsinu(self):
        """
        Izračunava ukupnu površinu svih prostorija u modelu.
        
        Returns:
        --------
        float
            Ukupna površina u m²
        """
        return sum(p.povrsina for p in self.prostorije)

    def dohvati_katalog_elemenata(self):
        """
        Dohvaća katalog građevinskih elemenata.
        
        Returns:
        --------        
        object or None
            Katalog građevinskih elemenata ili None
        """
        return None
    
    @property
    def fizicki_elementi(self):
        """
        Property for accessing physical elements dictionary.
        
        Returns:
        --------
        dict
            Dictionary of physical elements
        """
        return self._fizicki_elementi
    
    @property
    def katalog_elemenata(self):
        """
        Property for accessing building elements catalog.
        
        Returns:
        --------
        object or None
            Building elements catalog or None
        """
        return self.dohvati_katalog_elemenata()
    
    def create_physical_elements_from_rooms(self):
        """
        Creates physical elements from room definitions.
        This method processes all rooms and creates corresponding physical wall elements.
        """
        # Clear existing physical elements
        self._fizicki_elementi = {}
        
        # Process each room and create physical elements
        for prostorija in self.prostorije:
            for zid in prostorija.zidovi:
                # Create physical wall element if it doesn't exist
                if hasattr(zid, 'id') and zid.id not in self._fizicki_elementi:
                    try:
                        # Create a physical wall element
                        fizicki_element = {
                            'id': zid.id,
                            'tip': getattr(zid, 'tip', 'vanjski'),
                            'duzina': getattr(zid, 'duzina', 0.0),
                            'visina': getattr(zid, 'visina', 2.5),
                            'povrsina': getattr(zid, 'duzina', 0.0) * getattr(zid, 'visina', 2.5),
                            'orijentacija': getattr(zid, 'orijentacija', None),
                            'prostorija_id': prostorija.id,
                            'prostorija_naziv': prostorija.naziv
                        }
                        self._fizicki_elementi[zid.id] = fizicki_element
                    except Exception as e:
                            st.write(f"Warning: Could not create physical element for wall {zid.id}: {e}")
        
        def to_dict(self):
            """
            Konvertira MultiRoomModel instancu u rječnik.
            
            Returns:
            --------
            dict
                Rječnik koji predstavlja model s etažama, prostorijama i fizičkim zidovima
            """
            return {
                "etaze": [e.to_dict() for e in self.etaze],
                "prostorije": [p.to_dict() for p in self.prostorije],
                "fizicki_zidovi": {zid_id: zid.to_dict() for zid_id, zid in self.fizicki_zidovi.items()}
            }
