"""
Modul koji sadrži model za upravljanje građevinskim elementima
(zidovi, podovi, stropovi, prozori, vrata).
"""

import streamlit as st
import uuid

class WindowType:
    """
    Klasa koja predstavlja jedan tip prozora
    """
    def __init__(self, id, naziv, u_vrijednost, sirina=1.2, visina=1.2, opis=""):
        self.id = id
        self.naziv = naziv
        self.sirina = float(sirina)
        self.visina = float(visina)
        self.povrsina = self.sirina * self.visina
        self.u_vrijednost = float(u_vrijednost)
        self.opis = opis

    def to_dict(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "u_vrijednost": self.u_vrijednost,
            "sirina": self.sirina,
            "visina": self.visina,
            "opis": self.opis
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            naziv=data.get("naziv", ""),
            u_vrijednost=data.get("u_vrijednost", 0),
            sirina=data.get("sirina", 0),
            visina=data.get("visina", 0),
            opis=data.get("opis", "")
        )


class DoorType:
    """
    Klasa koja predstavlja jedan tip vrata
    """
    def __init__(self, id, naziv, u_vrijednost, sirina=0.9, visina=2.05, opis="", tip="vanjska"): # Added tip, default "vanjska"
        self.id = id
        self.naziv = naziv
        self.sirina = float(sirina)
        self.visina = float(visina)
        self.povrsina = self.sirina * self.visina
        self.u_vrijednost = float(u_vrijednost)
        self.opis = opis
        self.tip = tip # Added tip attribute

    def to_dict(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "u_vrijednost": self.u_vrijednost,
            "sirina": self.sirina,
            "visina": self.visina,
            "opis": self.opis,
            "tip": self.tip # Added tip to dict
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            naziv=data.get("naziv", ""),
            u_vrijednost=data.get("u_vrijednost", 0),
            sirina=data.get("sirina", 0),
            visina=data.get("visina", 0),
            opis=data.get("opis", ""),
            tip=data.get("tip", "vanjska") # Added tip from dict
        )


class WallType:
    """
    Klasa koja predstavlja jedan tip zida
    """
    def __init__(self, id, naziv, u_vrijednost, debljina=0.3, debljina_izolacije=0.1, opis="", tip="vanjski"):
        self.id = id
        self.naziv = naziv
        self.u_vrijednost = float(u_vrijednost)
        self.debljina = float(debljina)          # Osnovna debljina konstrukcije zida
        self.debljina_izolacije = float(debljina_izolacije)  # Debljina izolacije
        self.ukupna_debljina = self.debljina + self.debljina_izolacije  # Ukupna debljina
        self.opis = opis
        self.tip = tip  # Tip zida (npr. vanjski, unutarnji)

    def to_dict(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "u_vrijednost": self.u_vrijednost,
            "debljina": self.debljina,
            "debljina_izolacije": self.debljina_izolacije,
            "ukupna_debljina": self.ukupna_debljina,
            "opis": self.opis,
            "tip": self.tip
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            naziv=data.get("naziv", ""),
            u_vrijednost=data.get("u_vrijednost", 0),
            debljina=data.get("debljina", 0),
            debljina_izolacije=data.get("debljina_izolacije", 0),
            opis=data.get("opis", ""),
            tip=data.get("tip", "vanjski")
        )


class FloorType:
    """
    Klasa koja predstavlja jedan tip poda
    """
    def __init__(self, id, naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis="", tip="na tlu"):
        self.id = id
        self.naziv = naziv
        self.u_vrijednost = float(u_vrijednost)
        self.debljina_konstrukcije = float(debljina_konstrukcije)  # Dodana debljina konstrukcije
        self.debljina_dodatnih_slojeva = float(debljina_dodatnih_slojeva)  # Dodana debljina dodatnih slojeva
        self.opis = opis
        self.tip = tip # npr. "na tlu", "iznad negrijanog", "iznad grijanog", "međukatna"
        self.povrsina = 0 # Površina se računa kasnije

    def to_dict(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "u_vrijednost": self.u_vrijednost,
            "debljina_konstrukcije": self.debljina_konstrukcije,
            "debljina_dodatnih_slojeva": self.debljina_dodatnih_slojeva,
            "opis": self.opis,
            "tip": self.tip,
            "povrsina": self.povrsina,
            "tip_elementa": "POD" 
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            naziv=data.get("naziv", ""),
            u_vrijednost=data.get("u_vrijednost", 0),
            debljina_konstrukcije=data.get("debljina_konstrukcije", 0.0), # Osigurati default ako nedostaje
            debljina_dodatnih_slojeva=data.get("debljina_dodatnih_slojeva", 0.0), # Osigurati default
            opis=data.get("opis", ""),
            tip=data.get("tip", "na tlu")
        )


class CeilingType:
    """
    Klasa koja predstavlja jedan tip stropa
    """
    def __init__(self, id, naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis="", tip="prema negrijanom"):
        self.id = id
        self.naziv = naziv
        self.u_vrijednost = float(u_vrijednost)
        self.debljina_konstrukcije = float(debljina_konstrukcije)  # Dodana debljina konstrukcije
        self.debljina_dodatnih_slojeva = float(debljina_dodatnih_slojeva)  # Dodana debljina dodatnih slojeva
        self.opis = opis
        self.tip = tip # npr. "prema negrijanom", "ravni krov", "kosi krov", "međukatna"
        self.povrsina = 0 # Površina se računa kasnije

    def to_dict(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "u_vrijednost": self.u_vrijednost,
            "debljina_konstrukcije": self.debljina_konstrukcije,
            "debljina_dodatnih_slojeva": self.debljina_dodatnih_slojeva,
            "opis": self.opis,
            "tip": self.tip,
            "povrsina": self.povrsina,
            "tip_elementa": "STROP"
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            naziv=data.get("naziv", ""),
            u_vrijednost=data.get("u_vrijednost", 0),
            debljina_konstrukcije=data.get("debljina_konstrukcije", 0.0), # Osigurati default
            debljina_dodatnih_slojeva=data.get("debljina_dodatnih_slojeva", 0.0), # Osigurati default
            opis=data.get("opis", ""),
            tip=data.get("tip", "prema negrijanom")
        )


class BuildingElementsModel:
    """
    Model koji sadrži sve građevinske elemente
    """
    SESSION_KEY = "building_elements_data"
    
    def __init__(self):
        self.zidovi = []     # Lista WallType elemenata
        self.podovi = []     # Lista FloorType elemenata
        self.stropovi = []   # Lista CeilingType elemenata
        self.prozori = []    # Lista WindowType elemenata
        self.vrata = []      # Lista DoorType elemenata
        
        self._ucitaj_elemente()
    
    def _ucitaj_elemente(self):
        """Učitava elemente iz session state ako postoje"""
        if self.SESSION_KEY in st.session_state:
            data = st.session_state[self.SESSION_KEY]
            
            # Učitaj zidove
            if "zidovi" in data and isinstance(data["zidovi"], list):
                self.zidovi = [WallType.from_dict(z) for z in data["zidovi"]]
            
            # Učitaj podove
            if "podovi" in data and isinstance(data["podovi"], list):
                self.podovi = [FloorType.from_dict(p) for p in data["podovi"]]
            
            # Učitaj stropove
            if "stropovi" in data and isinstance(data["stropovi"], list):
                self.stropovi = [CeilingType.from_dict(s) for s in data["stropovi"]]
            
            # Učitaj prozore
            if "prozori" in data and isinstance(data["prozori"], list):
                self.prozori = [WindowType.from_dict(p) for p in data["prozori"]]
              # Učitaj vrata
            if "vrata" in data and isinstance(data["vrata"], list):
                self.vrata = [DoorType.from_dict(v) for v in data["vrata"]]
    
    def spremi_elemente(self):
        """Sprema elemente u session state"""
        st.session_state[self.SESSION_KEY] = {
            "zidovi": [z.to_dict() for z in self.zidovi],
            "podovi": [p.to_dict() for p in self.podovi],
            "stropovi": [s.to_dict() for s in self.stropovi],
            "prozori": [p.to_dict() for p in self.prozori],
            "vrata": [v.to_dict() for v in self.vrata]        }
    
    def dodaj_zid(self, naziv, u_vrijednost, debljina=0.3, debljina_izolacije=0.1, opis="", tip="vanjski"):
        """Dodaje novi tip zida"""
        id = str(uuid.uuid4())
        novi_zid = WallType(id, naziv, u_vrijednost, debljina, debljina_izolacije, opis, tip)
        self.zidovi.append(novi_zid)
        self.spremi_elemente()
        return novi_zid
    def dodaj_pod(self, naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis="", tip="na tlu"):
        """Dodaje novi pod u listu podova."""
        id = str(uuid.uuid4())
        novi_pod = FloorType(id, naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis, tip)
        self.podovi.append(novi_pod)
        self.spremi_elemente()
        return novi_pod.id
    
    def dodaj_strop(self, naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis="", tip="prema negrijanom"):
        """Dodaje novi strop u listu stropova."""
        id = str(uuid.uuid4())
        novi_strop = CeilingType(id, naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis, tip)
        self.stropovi.append(novi_strop)
        self.spremi_elemente()
        return novi_strop.id
    
    def dodaj_prozor(self, naziv, u_vrijednost, sirina=1.2, visina=1.2, opis=""):
        """Dodaje novi tip prozora"""
        id = str(uuid.uuid4())
        novi_prozor = WindowType(id, naziv, u_vrijednost, sirina, visina, opis)
        self.prozori.append(novi_prozor)
        self.spremi_elemente()
        return novi_prozor
    
    def dodaj_vrata(self, naziv, u_vrijednost, sirina=0.9, visina=2.05, opis="", tip="vanjska"): # Added tip parameter
        """Dodaje novi tip vrata"""
        id = str(uuid.uuid4())
        nova_vrata = DoorType(id, naziv, u_vrijednost, sirina, visina, opis, tip) # Pass tip to constructor
        self.vrata.append(nova_vrata)
        self.spremi_elemente()
        return nova_vrata
    
    def dodaj_vanjski_zid(self, naziv, u_vrijednost, debljina=0.3, debljina_izolacije=0.1, opis=""):
        """Dodaje novi tip vanjskog zida"""
        return self.dodaj_zid(naziv, u_vrijednost, debljina, debljina_izolacije, opis, "vanjski")
    
    def dodaj_unutarnji_zid(self, naziv, u_vrijednost, debljina=0.2, opis=""):
        """Dodaje novi tip unutarnjeg zida"""
        # Unutarnji zidovi nemaju izolaciju, pa koristimo defaultnu vrijednost 0
        return self.dodaj_zid(naziv, u_vrijednost, debljina, 0, opis, "unutarnji")
    
    def dohvati_zid(self, id):
        """Vraća zid s traženim ID-om"""
        for z in self.zidovi:
            if z.id == id:
                return z
        return None
    
    def dohvati_pod(self, id):
        """Vraća pod s traženim ID-om"""
        for p in self.podovi:
            if p.id == id:
                return p
        return None
    
    def dohvati_strop(self, id):
        """Vraća strop s traženim ID-om"""
        for s in self.stropovi:
            if s.id == id:
                return s
        return None
    
    def dohvati_prozor(self, id):
        """Vraća prozor s traženim ID-om"""
        for p in self.prozori:
            if p.id == id:
                return p
        return None
    
    def dohvati_vrata(self, id):
        """Vraća vrata s traženim ID-om"""
        for v in self.vrata:
            if v.id == id:
                return v
        return None
    
    def ukloni_zid(self, id):
        """Uklanja zid s traženim ID-om"""
        self.zidovi = [z for z in self.zidovi if z.id != id]
        self.spremi_elemente()
    
    def ukloni_pod(self, id):
        """Uklanja pod s traženim ID-om"""
        self.podovi = [p for p in self.podovi if p.id != id]
        self.spremi_elemente()
    
    def ukloni_strop(self, id):
        """Uklanja strop s traženim ID-om"""
        self.stropovi = [s for s in self.stropovi if s.id != id]
        self.spremi_elemente()
    
    def ukloni_prozor(self, id):
        """Uklanja prozor s traženim ID-om"""
        self.prozori = [p for p in self.prozori if p.id != id]
        self.spremi_elemente()
    
    def ukloni_vrata(self, id):
        """Uklanja vrata s traženim ID-om"""
        self.vrata = [v for v in self.vrata if v.id != id]
        self.spremi_elemente()
    
    # Alias methods for compatibility
    def obrisi_zid(self, id):
        """Alias za ukloni_zid, za kompatibilnost"""
        return self.ukloni_zid(id)
    
    def obrisi_pod(self, id):
        """Alias za ukloni_pod, za kompatibilnost"""
        return self.ukloni_pod(id)
    
    def obrisi_strop(self, id):
        """Alias za ukloni_strop, za kompatibilnost"""
        return self.ukloni_strop(id)
    
    def obrisi_prozor(self, id):
        """Alias za ukloni_prozor, za kompatibilnost"""
        return self.ukloni_prozor(id)
    
    def obrisi_vrata(self, id):
        """Alias za ukloni_vrata, za kompatibilnost"""
        return self.ukloni_vrata(id)


def inicijaliziraj_elemente():
    """
    Inicijalizira model građevinskih elemenata.
    Ako podaci postoje u session_state, učitava ih.
    Ako ne postoje ili su prazni, dodaje defaultne elemente.
    Sprema konačno stanje modela u session_state.
    """
    model = BuildingElementsModel()  # Automatski poziva _ucitaj_elemente()

    # Provjeri jesu li liste elemenata prazne nakon pokušaja učitavanja.
    if not model.zidovi and \
       not model.podovi and \
       not model.stropovi and \
       not model.prozori and \
       not model.vrata:
        _dodaj_default_elemente(model)
    
    model.spremi_elemente()  # Spremi trenutno stanje
    return model


def _dodaj_default_elemente(model):
    """
    Dodaje defaultne elemente u model.
    """    # Dodaj zidove - s pojednostavljenim nazivima
    model.dodaj_zid("Vanjski zid", 0.3, 0.25, 0.1, "Vanjski zid s toplinskom izolacijom", "vanjski")
    model.dodaj_zid("Vanjski zid izoliran", 0.3, 0.30, 0.15, "Vanjski zid s pojačanom toplinskom izolacijom", "vanjski")
    model.dodaj_zid("Unutarnji pregradni zid", 1.0, 0.10, 0.0, "Lagani pregradni zid", "prema_prostoriji")
    model.dodaj_zid("Unutarnji nosivi zid", 1.0, 0.20, 0.0, "Nosivi unutarnji zid", "prema_prostoriji")
      # Dodaj podove - s pojednostavljenim nazivima
    model.dodaj_pod("Pod prema tlu", 0.35, 0.15, 0.05, "Pod u prizemlju prema tlu", "na tlu")
    model.dodaj_pod("Pod prema negrijanom prostoru", 0.35, 0.20, 0.05, "Pod prema podrumu ili garaži", "prema negrijanom")
    model.dodaj_pod("Pod između stanova", 0.6, 0.25, 0.05, "Pod između stanova (etaža)", "prema stanu")
    model.dodaj_pod("Međukatna konstrukcija - Pod", 0.6, 0.20, 0.05, "Međukatna konstrukcija (pod)", "međukatna")
    model.dodaj_pod("Pod iznad negrijanog", 0.28, 0.15, 0.10, "Pod iznad negrijanog prostora", "iznad negrijanog")
    
    # Dodaj stropove - s pojednostavljenim nazivima
    model.dodaj_strop("Ravni krov", 0.25, 0.20, 0.05, "Ravni krov s toplinskom izolacijom", "krov")
    model.dodaj_strop("Kosi krov", 0.25, 0.25, 0.10, "Kosi krov s toplinskom izolacijom", "krov")
    model.dodaj_strop("Strop prema tavanu", 0.25, 0.20, 0.05, "Strop prema negrijanom tavanu", "prema negrijanom")
    model.dodaj_strop("Međukatna konstrukcija - Strop", 0.6, 0.20, 0.05, "Međukatna konstrukcija (strop)", "međukatna")
    
    # Dodaj prozore
    model.dodaj_prozor("Dvostruko staklo", 1.4, 1.2, 1.2, "Standardni PVC prozor s dvostrukim staklom")
    model.dodaj_prozor("Trostruko staklo", 1.0, 1.2, 1.2, "PVC prozor s trostrukim staklom")
    model.dodaj_prozor("Aluminijska stolarija", 1.6, 1.2, 1.2, "Prozor s aluminijskim okvirom")
    
    # Dodaj vrata
    model.dodaj_vrata("Ulazna vrata", 1.8, 1.0, 2.1, "Vanjska ulazna vrata", tip="vanjska") # Specify tip
    model.dodaj_vrata("Sobna vrata", 2.0, 0.8, 2.0, "Unutarnja sobna vrata", tip="unutarnja") # Specify tip
    model.dodaj_vrata("Balkonska vrata", 1.5, 0.9, 2.1, "Balkonska klizna vrata", tip="vanjska") # Specify tip
