"""
Modul koji sadrži glavnu klasu modela za proračun toplinskih gubitaka.
"""

import streamlit as st
import uuid
from .etaza import Etaza
from .prostorija import Prostorija
from .stambena_jedinica import StambenaJedinica  # Dodano
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
        self.stambene_jedinice = []  # Dodana lista stambenih jedinica
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
                st.session_state[self.session_key] = current_data_in_state.to_dict()
                current_data_in_state = st.session_state[self.session_key]  # Sada bi trebao biti rječnik
            except AttributeError:
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
                    if isinstance(fizicki_zid_obj, FizickiZid):
                        self.fizicki_zidovi[zid_id] = fizicki_zid_obj
                except Exception as e:
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
                    # Možete dodati st.warning ako etaza_obj nije Etaza, za debugiranje
                except Exception as e:
                    # Možete dodati st.warning za neuspjelo učitavanje etaže, za debugiranje
                    # npr. st.warning(f"Greška pri učitavanju etaže: {e}")
                    pass  # Preskoči etažu koja se ne može učitati
            self.etaze = loaded_etaze_temp
            
            # Load stambene jedinice - IMPORTANT: load this BEFORE prostorije since prostorije reference stambene jedinice
            stambene_jedinice_data = saved_state.get("stambene_jedinice", [])
            loaded_stambene_jedinice_temp = []
            for s_data in stambene_jedinice_data:
                try:
                    stambena_jedinica_obj = StambenaJedinica.from_dict(s_data)
                    if isinstance(stambena_jedinica_obj, StambenaJedinica):
                        loaded_stambene_jedinice_temp.append(stambena_jedinica_obj)
                except Exception as e:
                    # st.warning(f"Greška pri učitavanju stambene jedinice: {e}")
                    pass  # Preskoči stambenu jedinicu koja se ne može učitati
            
            # Assign loaded stambene jedinice to the model
            self.stambene_jedinice = loaded_stambene_jedinice_temp
            
            # Load prostorije
            prostorije_data = saved_state.get("prostorije", [])
            loaded_prostorije_temp = []
            for p_data in prostorije_data:
                try:
                    prostorija_obj = Prostorija.from_dict(p_data, self)
                    if isinstance(prostorija_obj, Prostorija): # Provjeravamo je li objekt instanca klase Prostorija
                        loaded_prostorije_temp.append(prostorija_obj)
                except Exception as e:
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
        self.stambene_jedinice = []  # Dodano

    # === METODE ZA UPRAVLJANJE STAMBENIM JEDINICAMA ===
    
    def dodaj_stambenu_jedinicu(self, etaza_id, naziv="Nova stambena jedinica", tip="Stan", opis="", spremi=True):
        """
        Dodaje novu stambenu jedinicu u model.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže u koju se dodaje stambena jedinica
        naziv : str
            Naziv nove stambene jedinice
        tip : str
            Tip stambene jedinice (iz TIPOVI_STAMBENIH_JEDINICA)
        opis : str
            Opis stambene jedinice
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
            
        Returns:
        --------
        StambenaJedinica or None
            Nova stambena jedinica ili None ako etaža ne postoji
        """
        etaza = self.dohvati_etazu(etaza_id)
        if not etaza:
            return None
        
        stambena_jedinica = StambenaJedinica(naziv=naziv, tip=tip, opis=opis, etaza_id=etaza_id)
        self.stambene_jedinice.append(stambena_jedinica)
        
        # Dodaj stambenu jedinicu i u etažu
        etaza.dodaj_stambenu_jedinicu(stambena_jedinica)
        
        if spremi:
            self._spremi_u_session_state()
        return stambena_jedinica

    def ukloni_stambenu_jedinicu(self, stambena_jedinica_id, spremi=True):
        """
        Uklanja stambenu jedinicu iz modela.
        
        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice koja se uklanja
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
        """
        stambena_jedinica = self.dohvati_stambenu_jedinicu(stambena_jedinica_id)
        if not stambena_jedinica:
            return
        
        # Ukloni iz etaže
        etaza = self.dohvati_etazu(stambena_jedinica.etaza_id)
        if etaza:
            etaza.ukloni_stambenu_jedinicu(stambena_jedinica_id)
        
        # Ukloni prostorije koje pripadaju ovoj stambenoj jedinici
        prostorije_za_uklanjanje = [p for p in self.prostorije if p.stambena_jedinica_id == stambena_jedinica_id]
        for prostorija in prostorije_za_uklanjanje:
            self.ukloni_prostoriju(prostorija.id, spremi=False)
        
        # Ukloni stambenu jedinicu iz modela
        self.stambene_jedinice = [s for s in self.stambene_jedinice if s.id != stambena_jedinica_id]
        
        if spremi:
            self._spremi_u_session_state()

    def dohvati_stambenu_jedinicu(self, stambena_jedinica_id):
        """
        Dohvaća stambenu jedinicu po ID-u.
        
        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice koja se dohvaća
            
        Returns:
        --------
        StambenaJedinica or None
            Stambena jedinica s navedenim ID-om ili None ako ne postoji
        """
        for s in self.stambene_jedinice:
            if s.id == stambena_jedinica_id:
                return s
        return None

    def dohvati_stambene_jedinice_za_etazu(self, etaza_id):
        """
        Dohvaća sve stambene jedinice koje pripadaju određenoj etaži.

        Parameters:
        -----------
        etaza_id : str
            ID etaže za koju se dohvaćaju stambene jedinice.

        Returns:
        --------
        list[StambenaJedinica]
            Lista stambenih jedinica koje pripadaju navedenoj etaži.
        """
        return [s for s in self.stambene_jedinice if s.etaza_id == etaza_id]

    def dohvati_prostorije_za_stambenu_jedinicu(self, stambena_jedinica_id):
        """
        Dohvaća sve prostorije koje pripadaju određenoj stambenoj jedinici.

        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice za koju se dohvaćaju prostorije.

        Returns:
        --------
        list[Prostorija]
            Lista prostorija koje pripadaju navedenoj stambenoj jedinici.
        """
        return [p for p in self.prostorije if p.stambena_jedinica_id == stambena_jedinica_id]

    def dodaj_prostoriju_u_stambenu_jedinicu(self, stambena_jedinica_id, naziv="Nova prostorija", tip="Dnevni boravak", povrsina=20.0, spremi=True):
        """
        Dodaje novu prostoriju u stambenu jedinicu.
        
        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice u koju se dodaje prostorija
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
        Prostorija or None
            Nova prostorija ili None ako stambena jedinica ne postoji
        """
        stambena_jedinica = self.dohvati_stambenu_jedinicu(stambena_jedinica_id)
        if not stambena_jedinica:
            return None
        
        # Dodaj prostoriju u model
        prostorija = self.dodaj_prostoriju(
            etaza_id=stambena_jedinica.etaza_id,
            naziv=naziv,
            tip=tip,
            povrsina=povrsina,
            spremi=False
        )
        
        if prostorija:
            # Postavi stambenu jedinicu u prostoriju
            prostorija.stambena_jedinica_id = stambena_jedinica_id
            
            # Dodaj prostoriju u stambenu jedinicu
            stambena_jedinica.dodaj_prostoriju(prostorija)
            
            if spremi:
                self._spremi_u_session_state()
        
        return prostorija

    def ukloni_prostoriju_iz_stambene_jedinice(self, prostorija_id, spremi=True):
        """
        Uklanja prostoriju iz stambene jedinice (ali ne briše prostoriju).
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se uklanja iz stambene jedinice
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
        """
        prostorija = self.dohvati_prostoriju(prostorija_id)
        if not prostorija or not prostorija.stambena_jedinica_id:
            return
        
        stambena_jedinica = self.dohvati_stambenu_jedinicu(prostorija.stambena_jedinica_id)
        if stambena_jedinica:
            stambena_jedinica.ukloni_prostoriju(prostorija_id)
        
        prostorija.stambena_jedinica_id = None
        
        if spremi:
            self._spremi_u_session_state()

    def premjesti_prostoriju_u_stambenu_jedinicu(self, prostorija_id, nova_stambena_jedinica_id, spremi=True):
        """
        Premješta prostoriju iz jedne stambene jedinice u drugu.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se premješta
        nova_stambena_jedinica_id : str
            ID nove stambene jedinice
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
        """
        prostorija = self.dohvati_prostoriju(prostorija_id)
        nova_stambena_jedinica = self.dohvati_stambenu_jedinicu(nova_stambena_jedinica_id)
        
        if not prostorija or not nova_stambena_jedinica:
            return
        
        # Ukloni iz stare stambene jedinice
        if prostorija.stambena_jedinica_id:
            self.ukloni_prostoriju_iz_stambene_jedinice(prostorija_id, spremi=False)
        
        # Dodaj u novu stambenu jedinicu        prostorija.stambena_jedinica_id = nova_stambena_jedinica_id
        nova_stambena_jedinica.dodaj_prostoriju(prostorija)
        
        if spremi:
            self._spremi_u_session_state()

    # === KRAJ METODA ZA STAMBENE JEDINICE ===
        
    def _spremi_u_session_state(self):
        """Sprema model u Streamlit session state."""
        stanje = {
            "etaze": [e.to_dict() for e in self.etaze],
            "prostorije": [p.to_dict() for p in self.prostorije],
            "stambene_jedinice": [s.to_dict() for s in self.stambene_jedinice],
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
                                    povezani_zid["elementi"] = WallElements()                                    # Set both walls to use the same elements object
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

    def dohvati_etazu_po_nazivu(self, naziv_etaze):
        """
        Dohvaća etažu po nazivu.
        
        Parameters:
        -----------
        naziv_etaze : str
            Naziv etaže koja se dohvaća
              Returns:
        --------
        Etaza or None
            Etaža s navedenim nazivom ili None ako ne postoji
        """
        for e in self.etaze:
            if e.naziv == naziv_etaze:
                return e
        return None
    
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
            Tip prostorije (npr. "Dnevni boravak", "Kupaonica", itd.)
        povrsina : float
            Površina prostorije u m²
        spremi : bool
            Određuje hoće li se promjene spremiti u session state
            
        Returns:
        --------
        Prostorija or None
            Nova prostorija koja je dodana u model ili None ako etaža ne postoji
        """
        etaza = self.dohvati_etazu(etaza_id)
        if not etaza:
            return None
        
        # Automatska numeracija prostorija po etaži
        prostorije_na_etazi = [p for p in self.prostorije if p.etaza_id == etaza_id]
        if prostorije_na_etazi:
            # Pronađi najveći broj prostorije na etaži
            brojevi = [p.broj_prostorije for p in prostorije_na_etazi if p.broj_prostorije is not None]
            novi_broj = max(brojevi) + 1 if brojevi else 1
        else:
            novi_broj = 1
        
        prostorija = Prostorija(naziv=naziv, tip=tip, etaza_id=etaza_id, povrsina=povrsina, 
                               model_ref=self, broj_prostorije=novi_broj)
        if prostorija.visina is None and not prostorija.koristi_zadanu_visinu:
            prostorija.visina = etaza.visina_etaze
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
            return
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
        
    def create_physical_wall_from_wall(self, wall_dict):
        """
        Stvara novi fizički zid na temelju rječnika zida iz prostorije.
        
        Parameters:
        -----------
        wall_dict : dict
            Rječnik s podacima o zidu
            
        Returns:
        --------
        FizickiZid
            Novostvoreni fizički zid
        """
        # Izvlačimo elemente zida
        elementi = wall_dict.get("elementi")
        if not isinstance(elementi, WallElements):
            elementi = WallElements()
            
        # Izvlačimo segmente zida
        segmenti = wall_dict.get("segmenti", [])
            
        # Stvaramo novi fizički zid
        fizicki_zid = FizickiZid(
            tip=wall_dict.get("tip", "vanjski"),
            orijentacija=wall_dict.get("orijentacija"),
            duzina=float(wall_dict.get("duzina", 5.0)),
            visina=float(wall_dict.get("visina")) if wall_dict.get("visina") is not None else None,
            je_segmentiran=wall_dict.get("je_segmentiran", False),
            segmenti=segmenti,
            elementi=elementi
        )
            
        return fizicki_zid

    def analiziraj_povezanost_zidova(self):
        """
        Analizira prostorije i identificira potencijalno povezane zidove.
        
        Returns:
        --------
        list
            Lista potencijalnih povezivanja zidova
        """
        # Importiramo funkciju iz modula zid_povezivanje
        from .zid_povezivanje import analiziraj_povezanost_zidova
        return analiziraj_povezanost_zidova(self)
        
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
        # Importiramo funkciju iz modula zid_povezivanje
        from .zid_povezivanje import povezi_zidove
        return povezi_zidove(self, prostorija1_id, zid1_id, prostorija2_id, zid2_id)
        
    def add_wall_to_room(self, prostorija_id, tip_zida, duzina, visina_zida=None, 
                      orijentacija=None, povezana_ciljna_prostorija_id=None,
                      je_segmentiran=False, tip_zida_id=None, postojeci_fizicki_zid_id=None):
        """
        Dodaje zid u prostoriju i stvara ili povezuje s fizičkim zidom.
        
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
        povezana_ciljna_prostorija_id : str
            ID povezane prostorije (za zidove tipa "prema_prostoriji")
        je_segmentiran : bool
            Označava je li zid segmentiran
        tip_zida_id : str
            ID tipa zida (za određivanje karakteristika zida)
        postojeci_fizicki_zid_id : str
            ID postojećeg fizičkog zida ako se dodaje referenca na postojeći fizički zid
            
        Returns:
        --------
        str or None
            ID novog zida ili None ako prostorija nije pronađena
        """
        # Dohvaćamo prostoriju
        prostorija = self.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return None
            
        # Dohvaćamo povezanu prostoriju ako postoji
        povezana_prostorija_obj = None
        if povezana_ciljna_prostorija_id and tip_zida == "prema_prostoriji":
            povezana_prostorija_obj = self.dohvati_prostoriju(povezana_ciljna_prostorija_id)
        
        # Stvaramo ili koristimo postojeći fizički zid
        if postojeci_fizicki_zid_id and postojeci_fizicki_zid_id in self.fizicki_zidovi:
            # Koristimo postojeći fizički zid
            fizicki_zid = self.fizicki_zidovi[postojeci_fizicki_zid_id]
        else:
            # Stvaramo novi fizički zid
            fizicki_zid = FizickiZid(
                tip=tip_zida,
                orijentacija=orijentacija if tip_zida == "vanjski" else None,
                duzina=float(duzina),
                visina=float(visina_zida) if visina_zida is not None else None,
                je_segmentiran=je_segmentiran
            )
            self.fizicki_zidovi[fizicki_zid.id] = fizicki_zid
          # Dodajemo zid u prostoriju koristeći metodu dodaj_zid
        novi_zid = prostorija.dodaj_zid(
            tip=tip_zida,
            orijentacija=orijentacija,
            duzina=duzina,
            visina_zida=visina_zida,
            povezana_prostorija_obj=povezana_prostorija_obj,
            model_ref=self,
            je_segmentiran_val=je_segmentiran,
            elementi_obj=fizicki_zid.elementi,
            fizicki_zid_ref=fizicki_zid,
            tip_zida_id=tip_zida_id
        )
        
        if novi_zid:
            # Dodajemo referencu na prostoriju u fizički zid
            fizicki_zid.dodaj_povezanu_prostoriju(prostorija.id, novi_zid["id"])
            
            # Ako imamo povezanu prostoriju, ažuriramo tip zida
            if povezana_prostorija_obj:
                povezani_zid_id = novi_zid.get("povezani_zid_id")
                if povezani_zid_id:
                    fizicki_zid.dodaj_povezanu_prostoriju(povezana_prostorija_obj.id, povezani_zid_id)
                    fizicki_zid.osvjezi_tip_na_temelju_povezanosti()
        
        # Spremamo promjene u session state
        self._spremi_u_session_state()
        
        # Vraćamo ID novog zida
        return novi_zid["id"] if novi_zid else None
        
    def obrisi_zid_iz_prostorije(self, prostorija_id, zid_id):
        """
        Briše zid iz prostorije i ažurira fizički zid.
        
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
        prostorija = self.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return False
        
        # Dohvaćamo zid prije brisanja da bismo mogli ažurirati fizički zid
        zid_prije_brisanja = prostorija.dohvati_zid(zid_id)
        if not zid_prije_brisanja:
            return False
            
        # Dohvaćamo fizički zid ako postoji
        fizicki_zid_id = zid_prije_brisanja.get("fizicki_zid_id")
        if fizicki_zid_id and fizicki_zid_id in self.fizicki_zidovi:
            # Uklanjamo poveznicu s prostorijom
            fizicki_zid = self.fizicki_zidovi[fizicki_zid_id]
            fizicki_zid.ukloni_povezanu_prostoriju(prostorija_id)
            
            # Provjeravamo je li fizički zid i dalje povezan s nekim prostorijama
            if not fizicki_zid.povezane_prostorije:
                # Ako nema više povezanih prostorija, uklanjamo fizički zid
                del self.fizicki_zidovi[fizicki_zid_id]
            else:
                # Inače, ažuriramo tip zida
                fizicki_zid.osvjezi_tip_na_temelju_povezanosti()
        
        # Delegiramo brisanje zida metodi ukloni_zid u klasi Prostorija
        result = prostorija.ukloni_zid(zid_id, model_ref=self)
        # Spremamo promjene u session state
        self._spremi_u_session_state()
        return result
        
    @property
    def fizicki_elementi(self):
        """
        Vraća rječnik fizičkih elemenata za proračun.
        
        Returns:
        --------
        dict
            Rječnik s fizičkim elementima {id: element}
        """
        return self._fizicki_elementi
        
    def create_physical_elements_from_rooms(self):
        """
        Stvara fizičke elemente iz prostorija za potrebe proračuna.
        Ova metoda osigurava da se fizički zidovi pravilno mapiraju u fizičke elemente.
        """
        # Resetiramo postojeće fizičke elemente
        self._fizicki_elementi = {}
        
        # Prvotno dodajemo sve fizičke zidove u mapu fizičkih elemenata
        for zid_id, zid in self.fizicki_zidovi.items():
            self._fizicki_elementi[zid_id] = zid
            # Inicijaliziramo listu parova
            if not hasattr(zid, 'originalni_zid_soba_parovi'):
                zid.originalni_zid_soba_parovi = []
        
        # Za svaku prostoriju i svaki zid,
        # pobrinemo se da su svi zidovi s fizicki_zid_id pravilno mapirani
        for prostorija in self.prostorije:
            for zid in prostorija.zidovi:
                fizicki_zid_id = zid.get("fizicki_zid_id")
                if fizicki_zid_id and fizicki_zid_id in self.fizicki_zidovi:
                    # Ako zid ima fizički zid ID i taj fizički zid postoji,
                    # dodajemo dodatne informacije za proračun
                    fizicki_zid = self.fizicki_zidovi[fizicki_zid_id]
                    
                    # Čuvamo par originalnog zida i prostorije
                    par = {
                        "originalni_zid_id": zid.get("id"),
                        "prostorija_id": prostorija.id
                    }
                    
                    # Provjera postoji li već ovaj par
                    postoji = False
                    for postojeci_par in fizicki_zid.originalni_zid_soba_parovi:
                        if (postojeci_par["originalni_zid_id"] == par["originalni_zid_id"] and
                            postojeci_par["prostorija_id"] == par["prostorija_id"]):
                            postoji = True
                            break
                    
                    # Dodajemo par u listu parova samo ako već ne postoji
                    if not postoji:
                        fizicki_zid.originalni_zid_soba_parovi.append(par)
                    
                    # Čuvamo i osnovne atribute za kompatibilnost s postojećim kodom
                    fizicki_zid.originalni_zid_id = zid.get("id")
                    fizicki_zid.prostorija_id = prostorija.id
                    
                    # Ako je zid prema prostoriji, dodajemo informaciju o povezanoj prostoriji
                    if zid.get("tip") == "prema_prostoriji" and zid.get("povezana_prostorija_id"):
                        fizicki_zid.povezana_prostorija_id = zid.get("povezana_prostorija_id")
                        
    @property
    def katalog_elemenata(self):
        """
        Vraća katalog građevinskih elemenata potreban za proračun.
        U trenutnoj implementaciji, ova metoda vraća None, jer se katalog 
        dohvaća iz session_state u heat_loss_calc.py pod ključem 'elements_model'.
        
        Returns:
        --------        object or None
            Katalog građevinskih elemenata ili None
        """
        return None
    
    def to_dict(self):
        """
        Konvertira MultiRoomModel instancu u rječnik.
        
        Returns:
        --------
        dict
            Rječnik koji predstavlja model s etažama, prostorijama, stambenim jedinicama i fizičkim zidovima
        """
        return {
            "etaze": [e.to_dict() for e in self.etaze],
            "prostorije": [p.to_dict() for p in self.prostorije],
            "stambene_jedinice": [s.to_dict() for s in self.stambene_jedinice],
            "fizicki_zidovi": {zid_id: zid.to_dict() for zid_id, zid in self.fizicki_zidovi.items()}
        }
