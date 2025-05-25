"""
Model za aplikaciju proračuna toplinskih gubitaka s podrškom za više prostorija i etaža.
"""

import streamlit as st
import uuid
import math
from .constants import TIPOVI_PROSTORIJA, ORIJENTACIJE
from .building_elements import WallElements

class SegmentZida:
    """Klasa koja predstavlja segment unutarnjeg zida."""
    def __init__(self, id=None, duljina=1.0, tip_segmenta="prema_prostoriji", povezana_prostorija_id=None, orijentacija=None):
        self.id = id if id else str(uuid.uuid4())
        self.duljina = duljina
        self.tip_segmenta = tip_segmenta  # Moguće vrijednosti: "prema_negrijanom", "prema_prostoriji"
        self.povezana_prostorija_id = povezana_prostorija_id
        self.orijentacija = orijentacija

    def to_dict(self):
        """Pretvara segment zida u rječnik za spremanje."""
        return {
            "id": self.id,
            "duljina": self.duljina,
            "tip_segmenta": self.tip_segmenta,
            "povezana_prostorija_id": self.povezana_prostorija_id,
            "orijentacija": self.orijentacija
        }

    @classmethod
    def from_dict(cls, data):
        """Stvara objekt SegmentZida iz rječnika."""
        return cls(
            id=data.get("id"),
            duljina=data.get("duljina", 1.0),
            tip_segmenta=data.get("tip_segmenta", "prema_prostoriji"),
            povezana_prostorija_id=data.get("povezana_prostorija_id"),
            orijentacija=data.get("orijentacija")
        )

class Etaza:
    """Klasa koja predstavlja jednu etažu u proračunu."""
    def __init__(self, id=None, naziv="Nova etaža", redni_broj=1, visina_etaze=2.8):
        self.id = id if id is not None else uuid.uuid4().hex
        self.naziv = naziv
        self.redni_broj = int(redni_broj)
        self.visina_etaze = float(visina_etaze)

    def to_dict(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "redni_broj": self.redni_broj,
            "visina_etaze": self.visina_etaze,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            naziv=data.get("naziv", "Nova etaža"),
            redni_broj=int(data.get("redni_broj", 1)),
            visina_etaze=float(data.get("visina_etaze", 2.8))
        )

class Prostorija:
    """Klasa koja predstavlja jednu prostoriju u proračunu."""
    def __init__(self, id=None, naziv="Nova prostorija", tip="Dnevni boravak", etaza_id=None, povrsina=20.0, model_ref=None):
        self.id = id if id is not None else uuid.uuid4().hex
        self.naziv = naziv
        self.tip = tip
        self.etaza_id = etaza_id
        self.povrsina = float(povrsina)
        self.visina = None  # Može se postaviti kasnije, ili preuzeti s etaže
        self.koristi_zadanu_visinu = True # Ako je False, koristi visinu etaže
        self.temp_unutarnja = TIPOVI_PROSTORIJA.get(tip, {}).get("temp", 20)
        self.izmjene_zraka = TIPOVI_PROSTORIJA.get(tip, {}).get("izmjene", 0.5)
        self.temperatura_susjednog_negrijanog = 10.0
        self.pod_tip = "Prema tlu"
        self.strop_tip = "Prema negrijanom prostoru"
        self.zidovi = []  # Lista rječnika koji predstavljaju zidove
        self.model_ref = model_ref

    def azuriraj_tip_prostorije(self, novi_tip):
        """
        Ažurira tip prostorije i povezane atribute (temperatura, izmjene zraka).
        """
        self.tip = novi_tip
        if novi_tip in TIPOVI_PROSTORIJA:
            self.temp_unutarnja = TIPOVI_PROSTORIJA[novi_tip].get("temp", self.temp_unutarnja)
            self.izmjene_zraka = TIPOVI_PROSTORIJA[novi_tip].get("izmjene", self.izmjene_zraka)

    def dodaj_zid(self, tip="vanjski", orijentacija="Sjever", duzina=5.0, visina_zida=None, 
                  povezana_prostorija_obj: 'Prostorija' = None, model_ref: 'MultiRoomModel' = None,
                  postojeci_id_zida_A=None, 
                  je_segmentiran_val=False, 
                  segmenti_val=None, # Expects a list of SegmentZida objects or None
                  elementi_obj=None): # Expects a WallElements object or None
        """
        Dodaje novi zid u prostoriju. 
        Ako je tip 'prema_prostoriji' i povezana_prostorija_obj je zadan,
        automatski kreira odgovarajući zid u povezanoj prostoriji.
        Može prihvatiti postojeći ID, informacije o segmentaciji i postojeće elemente.
        """
        try:
            processed_duzina = float(duzina)
            if processed_duzina <= 0:
                # Invalid length, cannot create wall
                return None 
        except (ValueError, TypeError):
            # duzina is not a valid number
            return None

        novi_id_zida_A = postojeci_id_zida_A if postojeci_id_zida_A is not None else uuid.uuid4().hex
        dijeljeni_elementi = elementi_obj if elementi_obj is not None else WallElements()

        stvarna_visina_zida_A = None
        if visina_zida is not None:
            try:
                candidate_visina = float(visina_zida)
                if candidate_visina > 0:
                    stvarna_visina_zida_A = candidate_visina
                # If candidate_visina is not positive, stvarna_visina_zida_A remains None, fallback will occur
            except (ValueError, TypeError):
                pass # stvarna_visina_zida_A remains None, fallback will occur
        
        if stvarna_visina_zida_A is None: # Covers visina_zida being None, invalid, or non-positive
            if model_ref: 
                etaza_A = model_ref.dohvati_etazu(self.etaza_id)
                if etaza_A:
                    stvarna_visina_zida_A = self.get_actual_height(etaza_A)
                else: 
                    stvarna_visina_zida_A = 2.8 # Default if etaza_A not found
            else: 
                 stvarna_visina_zida_A = 2.8 # Default if model_ref not available

        zid_A = {
            "id": novi_id_zida_A,
            "tip": tip,
            "orijentacija": orijentacija if tip == "vanjski" else None,
            "duzina": processed_duzina, # Use processed_duzina
            "visina": stvarna_visina_zida_A,
            "povezana_prostorija_id": None,
            "povezani_zid_id": None,
            "elementi": dijeljeni_elementi,
            "je_segmentiran": je_segmentiran_val,
            "segmenti": segmenti_val if segmenti_val is not None else []
        }

        if tip == "prema_prostoriji" and povezana_prostorija_obj and self.id != povezana_prostorija_obj.id:
            novi_id_zida_B = uuid.uuid4().hex
            
            zid_B = {
                "id": novi_id_zida_B,
                "tip": "prema_prostoriji", 
                "orijentacija": None, 
                "duzina": processed_duzina, # Use processed_duzina
                "visina": stvarna_visina_zida_A, 
                "povezana_prostorija_id": self.id, 
                "povezani_zid_id": novi_id_zida_A, 
                "elementi": dijeljeni_elementi, # Dijeljeni elementi
                "je_segmentiran": je_segmentiran_val, # Preslikavamo segmentaciju
                "segmenti": segmenti_val if segmenti_val is not None else [] # Preslikavamo segmente
            }
            povezana_prostorija_obj.zidovi.append(zid_B)

            zid_A["povezana_prostorija_id"] = povezana_prostorija_obj.id
            zid_A["povezani_zid_id"] = novi_id_zida_B
            zid_A["tip"] = "prema_prostoriji" 
            zid_A["orijentacija"] = None
        
        self.zidovi.append(zid_A)
        return zid_A

    def ukloni_zid(self, zid_id_za_uklanjanje, model_ref: 'MultiRoomModel' = None):
        """
        Uklanja zid iz prostorije. Ako je zid povezan s drugim zidom 
        u drugoj prostoriji, uklanja i taj povezani zid.
        """
        zid_za_uklanjanje = self.dohvati_zid(zid_id_za_uklanjanje)
        if not zid_za_uklanjanje:
            return False 

        povezana_prostorija_id = zid_za_uklanjanje.get("povezana_prostorija_id")
        povezani_zid_id_u_drugoj_prostoriji = zid_za_uklanjanje.get("povezani_zid_id")

        self.zidovi = [z for z in self.zidovi if z.get("id") != zid_id_za_uklanjanje]

        if povezana_prostorija_id and povezani_zid_id_u_drugoj_prostoriji and model_ref:
            povezana_prostorija_obj = model_ref.dohvati_prostoriju(povezana_prostorija_id)
            if povezana_prostorija_obj:
                povezana_prostorija_obj.zidovi = [
                    z for z in povezana_prostorija_obj.zidovi 
                    if z.get("id") != povezani_zid_id_u_drugoj_prostoriji
                ]
        return True

    def dohvati_zid(self, zid_id):
        """Dohvaća zid iz prostorije na temelju njegovog 'id' atributa."""
        for zid in self.zidovi:
            if zid.get("id") == zid_id:
                return zid
        return None

    def get_actual_height(self, parent_etaza: 'Etaza') -> float:
        """
        Calculates the actual height of the room.
        """
        default_height_fallback = 2.8

        if not self.koristi_zadanu_visinu:
            if self.visina is not None:
                return float(self.visina)
            elif parent_etaza:
                return float(parent_etaza.visina_etaze)
            else:
                return default_height_fallback
        else:
            if parent_etaza:
                return float(parent_etaza.visina_etaze)
            else:
                return default_height_fallback

    def to_dict(self):
        zidovi_data = []
        for zid_dict in self.zidovi:
            # Convert WallElements to dict if present
            elementi_dict = zid_dict.get("elementi")
            if isinstance(elementi_dict, WallElements):
                elementi_copy = elementi_dict.to_dict()
            else:
                elementi_copy = WallElements().to_dict()
                
            # Create a copy of the wall dictionary
            zid_copy = zid_dict.copy()
            zid_copy["elementi"] = elementi_copy
            zidovi_data.append(zid_copy)

        return {
            "id": self.id,
            "naziv": self.naziv,
            "tip": self.tip,
            "etaza_id": self.etaza_id,
            "povrsina": self.povrsina,
            "visina": self.visina,
            "koristi_zadanu_visinu": self.koristi_zadanu_visinu,
            "temp_unutarnja": self.temp_unutarnja,
            "izmjene_zraka": self.izmjene_zraka,
            "temperatura_susjednog_negrijanog": self.temperatura_susjednog_negrijanog,
            "pod_tip": self.pod_tip,
            "strop_tip": self.strop_tip,
            "zidovi": zidovi_data,
        }

    @classmethod
    def from_dict(cls, data, model_ref=None):
        instance = cls(
            id=data.get("id"),
            naziv=data.get("naziv", "Nova prostorija"),
            tip=data.get("tip", "Dnevni boravak"),
            etaza_id=data.get("etaza_id"),
            povrsina=float(data.get("povrsina", 20.0)),
            model_ref=model_ref
        )
        
        instance.visina = data.get("visina")
        instance.koristi_zadanu_visinu = data.get("koristi_zadanu_visinu", True)
        instance.temp_unutarnja = data.get("temp_unutarnja", TIPOVI_PROSTORIJA.get(instance.tip, {}).get("temp", 20))
        instance.izmjene_zraka = data.get("izmjene_zraka", TIPOVI_PROSTORIJA.get(instance.tip, {}).get("izmjene", 0.5))
        instance.temperatura_susjednog_negrijanog = data.get("temperatura_susjednog_negrijanog", 10.0)
        instance.pod_tip = data.get("pod_tip", "Prema tlu")
        instance.strop_tip = data.get("strop_tip", "Prema negrijanom prostoru")
        
        # Add walls
        zidovi = []
        for zid_dict in data.get("zidovi", []):
            zid_dict_for_instance = zid_dict.copy()
            
            # Deserialize 'elementi' into WallElements object
            elementi_as_dict = zid_dict_for_instance.get("elementi")
            if isinstance(elementi_as_dict, dict):
                zid_dict_for_instance["elementi"] = WallElements.from_dict(elementi_as_dict)
            elif not isinstance(elementi_as_dict, WallElements): 
                zid_dict_for_instance["elementi"] = WallElements()
                
            # Deserialize 'segmenti' list of dicts into list of SegmentZida objects
            segmenti_as_dicts = zid_dict_for_instance.get("segmenti", [])
            segmenti_as_objects = []
            if isinstance(segmenti_as_dicts, list):
                for segment_dict in segmenti_as_dicts:
                    if isinstance(segment_dict, dict):
                        segmenti_as_objects.append(SegmentZida.from_dict(segment_dict))
                    else:
                        segmenti_as_objects.append(segment_dict)
            zid_dict_for_instance["segmenti"] = segmenti_as_objects
            
            zidovi.append(zid_dict_for_instance)
            
        instance.zidovi = zidovi
        return instance

class MultiRoomModel:
    """Model koji upravlja s više prostorija, etaža i njihovim vezama."""
    def __init__(self, session_key):
        self.session_key = session_key
        self.etaze = []
        self.prostorije = []
        self._ucitaj_iz_session_state()

    def _ucitaj_iz_session_state(self):
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
            # Load etaze
            self.etaze = [Etaza.from_dict(e_data) for e_data in saved_state.get("etaze", [])]
            # Load prostorije
            self.prostorije = [Prostorija.from_dict(p_data, self) for p_data in saved_state.get("prostorije", [])]
        else:
            self._inicijaliziraj_zadano_stanje()
        
        if not self.etaze:
            self.dodaj_etazu(naziv="Prizemlje", redni_broj=1, visina_etaze=2.8, spremi=False)
        
        self.restore_shared_elements_references()
        self._spremi_u_session_state()

    def _inicijaliziraj_zadano_stanje(self):
        self.etaze = []
        self.prostorije = []

    def _spremi_u_session_state(self):
        stanje = {
            "etaze": [e.to_dict() for e in self.etaze],
            "prostorije": [p.to_dict() for p in self.prostorije],
        }
        st.session_state[self.session_key] = stanje

    def restore_shared_elements_references(self):
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

    def dodaj_etazu(self, naziv="Nova etaža", redni_broj=None, visina_etaze=2.8, spremi=True):
        if redni_broj is None:
            redni_broj = (max(e.redni_broj for e in self.etaze) + 1) if self.etaze else 1
        
        if any(e.redni_broj == redni_broj for e in self.etaze):
            redni_broj = (max(e.redni_broj for e in self.etaze) + 1) if self.etaze else 1
        
        etaza = Etaza(naziv=naziv, redni_broj=redni_broj, visina_etaze=visina_etaze)
        self.etaze.append(etaza)
        self.etaze.sort(key=lambda e: e.redni_broj)
        
        if spremi:
            self._spremi_u_session_state()
        return etaza

    def ukloni_etazu(self, etaza_id, spremi=True):
        etaza_za_uklanjanje = self.dohvati_etazu(etaza_id)
        if not etaza_za_uklanjanje:
            return
        
        prostorije_na_uklonjenoj_etazi_ids = {p.id for p in self.dohvati_prostorije_za_etazu(etaza_id)}
        self.prostorije = [p for p in self.prostorije if p.etaza_id != etaza_id]
        self.etaze = [e for e in self.etaze if e.id != etaza_id]
        
        if spremi:
            self._spremi_u_session_state()

    def dohvati_etazu(self, etaza_id):
        for e in self.etaze:
            if e.id == etaza_id:
                return e
        return None

    def dohvati_etazu_po_nazivu(self, naziv_etaze):
        for e in self.etaze:
            if e.naziv == naziv_etaze:
                return e
        return None

    def dodaj_prostoriju(self, etaza_id, naziv="Nova prostorija", tip="Dnevni boravak", povrsina=20.0, spremi=True):
        etaza = self.dohvati_etazu(etaza_id)
        if not etaza:
            return None
        
        prostorija = Prostorija(naziv=naziv, tip=tip, etaza_id=etaza_id, povrsina=povrsina, model_ref=self)
        if prostorija.visina is None and not prostorija.koristi_zadanu_visinu:
            prostorija.visina = etaza.visina_etaze
        self.prostorije.append(prostorija)
        if spremi:
            self._spremi_u_session_state()
        return prostorija

    def ukloni_prostoriju(self, prostorija_id, spremi=True):
        prostorija_za_uklanjanje = self.dohvati_prostoriju(prostorija_id)
        if not prostorija_za_uklanjanje:
            return
        self.prostorije = [p for p in self.prostorije if p.id != prostorija_id]
        if spremi:
            self._spremi_u_session_state()

    def dohvati_prostoriju(self, prostorija_id):
        for p in self.prostorije:
            if p.id == prostorija_id:
                return p
        return None

    def dohvati_prostorije_za_etazu(self, etaza_id):
        return [p for p in self.prostorije if p.etaza_id == etaza_id]
    
    def add_wall_to_room(self, prostorija_id, tip_zida, duzina, visina_zida=None, 
                          orijentacija=None, povezana_ciljna_prostorija_id=None,
                          je_segmentiran=False, tip_zida_id=None):
        """
        Dodaje zid u prostoriju. Delegira poziv odgovarajućoj metodi 'dodaj_zid' u klasi Prostorija.
        
        Args:
            prostorija_id: ID prostorije u koju se dodaje zid
            tip_zida: Tip zida ("vanjski", "prema_prostoriji", itd.)
            duzina: Duljina zida
            visina_zida: Visina zida (ako je None, koristi se visina etaže)
            orijentacija: Orijentacija zida (relevantno samo za vanjski zid)
            povezana_ciljna_prostorija_id: ID povezane prostorije (za zidove tipa "prema_prostoriji")
            je_segmentiran: Označava je li zid segmentiran
            tip_zida_id: ID tipa zida (za određivanje karakteristika zida)
            
        Returns:
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
            
        # Elementi zida na temelju tip_zida_id - koristimo defaultni WallElements ako nije specificirano
        elementi_obj = WallElements()
        # Ako je potrebno, ovdje možete dodati logiku za postavljanje elemenata zida na temelju tip_zida_id
        
        # Dodajemo zid u prostoriju koristeći metodu dodaj_zid
        novi_zid = prostorija.dodaj_zid(
            tip=tip_zida,
            orijentacija=orijentacija,
            duzina=duzina,
            visina_zida=visina_zida,
            povezana_prostorija_obj=povezana_prostorija_obj,
            model_ref=self,
            je_segmentiran_val=je_segmentiran,
            elementi_obj=elementi_obj
        )
        
        # Spremamo promjene u session state
        self._spremi_u_session_state()
        
        # Vraćamo ID novog zida
        return novi_zid["id"] if novi_zid else None

    def obrisi_zid_iz_prostorije(self, prostorija_id, zid_id):
        """
        Briše zid iz prostorije. Delegira poziv metodi 'ukloni_zid' u klasi Prostorija.
        
        Args:
            prostorija_id: ID prostorije iz koje se briše zid
            zid_id: ID zida koji se briše
            
        Returns:
            True ako je zid uspješno obrisan, False inače
        """
        prostorija = self.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            return False
        
        # Delegiramo brisanje zida metodi ukloni_zid u klasi Prostorija
        result = prostorija.ukloni_zid(zid_id, model_ref=self)
        
        # Spremamo promjene u session state
        self._spremi_u_session_state()
        
        return result

def inicijaliziraj_model(session_key: str) -> MultiRoomModel:
    """
    Inicijalizira MultiRoomModel. Pri svakom pokretanju skripte,
    nova instanca modela se stvara. Klasa MultiRoomModel sama
    upravlja učitavanjem svog stanja iz Streamlit session state-a
    (gdje je spremljeno kao rječnik) ili inicijalizacijom novog stanja.
    """
    # MultiRoomModel konstruktor sada interno rješava učitavanje/inicijalizaciju
    # i osigurava da je st.session_state[session_key] ispravnog (rječničkog) tipa.
    model_instance = MultiRoomModel(session_key)
    return model_instance
