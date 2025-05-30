"""
Kontroler za upravljanje građevinskim elementima.
"""

import uuid
import streamlit as st
from ..models.elementi.building_elements_model import WallType, FloorType, CeilingType, WindowType, DoorType
from ..models.elementi.constants import TIPOVI_ELEMENATA # Koristit će se za mapiranje tipova ako je potrebno

class ElementiController:
    """
    Kontroler za upravljanje građevinskim elementima 
    (podovi, stropovi, zidovi, vrata, prozori).
    Radi s instancom BuildingElementsModel.
    """
    
    def __init__(self, building_elements_model):
        """
        Inicijalizira kontroler za građevinske elemente.
        
        Parameters:
        -----------
        building_elements_model : BuildingElementsModel
            Model koji sadrži liste građevinskih elemenata (zidovi, podovi, itd.)
        """
        self.building_elements_model = building_elements_model
    
    def dohvati_sve_elemente(self):
        """
        Dohvaća sve građevinske elemente iz BuildingElementsModel.
        
        Returns:
        --------
        list
            Lista svih građevinskih elemenata (objekti tipa WallType, FloorType, itd.)
        """
        sve = []
        if hasattr(self.building_elements_model, 'podovi'):
            sve.extend(self.building_elements_model.podovi)
        if hasattr(self.building_elements_model, 'stropovi'):
            sve.extend(self.building_elements_model.stropovi)
        if hasattr(self.building_elements_model, 'zidovi'):
            sve.extend(self.building_elements_model.zidovi)
        if hasattr(self.building_elements_model, 'prozori'):
            sve.extend(self.building_elements_model.prozori)
        if hasattr(self.building_elements_model, 'vrata'):
            sve.extend(self.building_elements_model.vrata)
        return sve
    
    def dohvati_element(self, element_id):
        """
        Dohvaća građevinski element prema ID-u pretraživanjem svih lista u BuildingElementsModel.
        
        Parameters:
        -----------
        element_id : str
            ID elementa koji se dohvaća
            
        Returns:
        --------
        WallType, FloorType, itd. ili None
            Pronađeni element ili None ako element nije pronađen
        """
        for elem_list in [
            self.building_elements_model.podovi,
            self.building_elements_model.stropovi,
            self.building_elements_model.zidovi,
            self.building_elements_model.prozori,
            self.building_elements_model.vrata,
        ]:
            for element in elem_list:
                if element.id == element_id:
                    return element
        return None
    
    def dohvati_elemente_po_tipu(self, tip_elementa_kljuc):
        """
        Dohvaća sve građevinske elemente određenog tipa.
        'tip_elementa_kljuc' je string kao "POD", "VANJSKI_ZID" itd.,
        koji dolazi iz konfiguracije korisničkog sučelja.
        
        Parameters:
        -----------
        tip_elementa_kljuc : str
            Ključ za tip elementa (npr. "POD", "VANJSKI_ZID")
            
        Returns:
        --------
        list
            Lista građevinskih elemenata određenog tipa
        """
        # Pretpostavljamo da su ključevi direkti stringovi kako se koriste u UI
        if tip_elementa_kljuc == "POD":
            return self.building_elements_model.podovi
        elif tip_elementa_kljuc == "STROP":
            return self.building_elements_model.stropovi
        elif tip_elementa_kljuc == "VANJSKI_ZID":
            return [z for z in self.building_elements_model.zidovi if z.tip == 'vanjski']
        elif tip_elementa_kljuc == "UNUTARNJI_ZID":
            # Uključuje različite tipove unutarnjih zidova definirane u building_elements_model.py
            return [z for z in self.building_elements_model.zidovi if z.tip in ['unutarnji', 'prema_prostoriji']]
        elif tip_elementa_kljuc == "PROZOR":
            return self.building_elements_model.prozori
        elif tip_elementa_kljuc == "VANJSKA_VRATA":
            return [v for v in self.building_elements_model.vrata if v.tip == 'vanjska']
        elif tip_elementa_kljuc == "UNUTARNJA_VRATA":
            return [v for v in self.building_elements_model.vrata if v.tip == 'unutarnja']
        # Uklonjen fallback za općenito "VRATA"
        # Potencijalno dodati mapiranje preko TIPOVI_ELEMENATA ako su ključevi drugačiji
        # elif tip_elementa_kljuc == TIPOVI_ELEMENATA.get("NAZIV_TIPA_ZA_POD"): ...
        st.warning(f"Nepoznat ili neobrađen tip elementa za dohvaćanje: {tip_elementa_kljuc}")
        return []
    
    def dodaj_element(self, tip_elementa_kljuc, **kwargs):
        """
        Dodaje novi građevinski element koristeći metode iz BuildingElementsModel.
        
        Parameters:
        -----------
        tip_elementa_kljuc : str
            Ključ za tip elementa (npr. "POD", "VANJSKI_ZID")
        **kwargs : dict
            Argumenti specifični za element (naziv, u_vrijednost, debljina, sirina, visina, etc.)
            
        Returns:
        --------
        bool
            True ako je dodavanje uspješno, False inače
        """
        try:
            naziv = kwargs.get("naziv")
            u_vrijednost = float(kwargs.get("u_vrijednost")) # UI treba osigurati da je ovo float

            if not naziv or not naziv.strip():
                st.error("Naziv elementa ne može biti prazan.")
                return False
            if u_vrijednost is None: # Provjera za None, jer 0.0 je validna U-vrijednost
                st.error("U-vrijednost elementa mora biti definirana.")
                return False

            opis = kwargs.get("opis", "") # Zajednički parametar

            if tip_elementa_kljuc == "POD":
                debljina_konstrukcije = float(kwargs.get("debljina_konstrukcije", 20.0))
                debljina_dodatnih_slojeva = float(kwargs.get("debljina_dodatnih_slojeva", 5.0))
                tip_specific = kwargs.get("tip", "na tlu") # 'tip' iz forme za podove
                self.building_elements_model.dodaj_pod(naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis, tip_specific)
            elif tip_elementa_kljuc == "STROP":
                debljina_konstrukcije = float(kwargs.get("debljina_konstrukcije", 25.0))
                debljina_dodatnih_slojeva = float(kwargs.get("debljina_dodatnih_slojeva", 5.0))
                tip_specific = kwargs.get("tip", "prema negrijanom") # 'tip' iz forme za stropove
                self.building_elements_model.dodaj_strop(naziv, u_vrijednost, debljina_konstrukcije, debljina_dodatnih_slojeva, opis, tip_specific)
            elif tip_elementa_kljuc == "VANJSKI_ZID":
                debljina = float(kwargs.get("debljina", 0.25)) # Default iz building_elements_model
                debljina_izolacije = float(kwargs.get("debljina_izolacije", 0.10))
                self.building_elements_model.dodaj_vanjski_zid(naziv, u_vrijednost, debljina, debljina_izolacije, opis)
            elif tip_elementa_kljuc == "UNUTARNJI_ZID":
                debljina = float(kwargs.get("debljina", 0.10)) # Default iz building_elements_model
                self.building_elements_model.dodaj_unutarnji_zid(naziv, u_vrijednost, debljina, opis)
            elif tip_elementa_kljuc == "PROZOR":
                sirina = float(kwargs.get("sirina", 1.2))
                visina = float(kwargs.get("visina", 1.2))
                self.building_elements_model.dodaj_prozor(naziv, u_vrijednost, sirina, visina, opis)
            elif tip_elementa_kljuc == "VANJSKA_VRATA":
                sirina = float(kwargs.get("sirina", 0.9))
                visina = float(kwargs.get("visina", 2.05))
                self.building_elements_model.dodaj_vrata(naziv, u_vrijednost, sirina, visina, opis, tip="vanjska")
            elif tip_elementa_kljuc == "UNUTARNJA_VRATA":
                sirina = float(kwargs.get("sirina", 0.8))
                visina = float(kwargs.get("visina", 2.0))
                self.building_elements_model.dodaj_vrata(naziv, u_vrijednost, sirina, visina, opis, tip="unutarnja")
            # Uklonjen fallback za općenito "VRATA"
            else:
                st.error(f"Nepoznat tip elementa za dodavanje: {tip_elementa_kljuc}")
                return False
            
            # BuildingElementsModel.dodaj_* metode već zovu spremi_elemente()
            st.success(f"Element '{naziv}' ({tip_elementa_kljuc}) uspješno dodan.")
            return True
        except ValueError as ve:
            st.error(f"Greška u podacima za element ({tip_elementa_kljuc}): {str(ve)}. Provjerite jesu li brojevne vrijednosti ispravne.")
            return False
        except Exception as e:
            st.error(f"Neočekivana greška prilikom dodavanja elementa ({tip_elementa_kljuc}): {str(e)}")
            return False
    
    def azuriraj_element(self, element_id, **kwargs):
        """
        Ažurira postojeći građevinski element.
        NAPOMENA: Ova metoda trenutno nije pozvana iz standardnog UI-ja za dodavanje/brisanje.
                  Ako je potrebna, UI za ažuriranje treba implementirati.
        
        Parameters:
        -----------
        element_id : str
            ID elementa koji se ažurira
        **kwargs : dict
            Nove vrijednosti za atribute elementa
            
        Returns:
        --------
        bool
            True ako je ažuriranje uspješno, False inače
        """
        try:
            element = self.dohvati_element(element_id)
            if not element:
                st.error(f"Element s ID-om {element_id} nije pronađen za ažuriranje.")
                return False

            # Ažuriranje zajedničkih atributa
            if "naziv" in kwargs and kwargs["naziv"].strip():
                element.naziv = kwargs["naziv"].strip()
            if "u_vrijednost" in kwargs:
                element.u_vrijednost = float(kwargs["u_vrijednost"])
            if "opis" in kwargs:
                element.opis = kwargs["opis"]

            # Ažuriranje specifičnih atributa
            if isinstance(element, WallType):
                if "debljina" in kwargs:
                    element.debljina = float(kwargs["debljina"])
            
            if isinstance(element, FloorType):
                if "debljina_konstrukcije" in kwargs:
                    element.debljina_konstrukcije = float(kwargs["debljina_konstrukcije"])
                if "debljina_dodatnih_slojeva" in kwargs:
                    element.debljina_dodatnih_slojeva = float(kwargs["debljina_dodatnih_slojeva"])
            
            if isinstance(element, CeilingType):
                if "debljina_konstrukcije" in kwargs:
                    element.debljina_konstrukcije = float(kwargs["debljina_konstrukcije"])
                if "debljina_dodatnih_slojeva" in kwargs:
                    element.debljina_dodatnih_slojeva = float(kwargs["debljina_dodatnih_slojeva"])
            
            if isinstance(element, (FloorType, CeilingType, WallType)): # Za zidove, podove, stropove koji imaju 'tip'
                 if "tip" in kwargs: # Ako UI šalje 'tip' kao npr. "na tlu", "krov", "vanjski"
                    element.tip = kwargs["tip"]

            if isinstance(element, (WindowType, DoorType)):
                recalculate_area = False
                if "sirina" in kwargs:
                    element.sirina = float(kwargs["sirina"])
                    recalculate_area = True
                if "visina" in kwargs:
                    element.visina = float(kwargs["visina"])
                    recalculate_area = True
                if recalculate_area:
                    element.povrsina = element.sirina * element.visina
                # Dodajemo ažuriranje tipa za vrata ako je poslano
                if isinstance(element, DoorType) and "tip" in kwargs:
                    element.tip = kwargs["tip"]
            
            self.building_elements_model.spremi_elemente()
            st.success(f"Element '{element.naziv}' (ID: {element_id}) uspješno ažuriran.")
            return True
        except ValueError as ve:
            st.error(f"Greška u podacima za ažuriranje elementa {element_id}: {str(ve)}. Provjerite jesu li brojevne vrijednosti ispravne.")
            return False
        except Exception as e:
            st.error(f"Neočekivana greška prilikom ažuriranja elementa {element_id}: {str(e)}")
            return False
    
    def ukloni_element(self, element_id):
        """
        Uklanja građevinski element iz BuildingElementsModel.
        
        Parameters:
        -----------
        element_id : str
            ID elementa koji se uklanja
            
        Returns:
        --------
        bool
            True ako je uklanjanje uspješno, False inače
        """
        try:
            element_za_uklanjanje = self.dohvati_element(element_id)
            if not element_za_uklanjanje:
                st.error(f"Element s ID-om {element_id} nije pronađen za uklanjanje.")
                return False

            # Placeholder za provjeru korištenja elementa
            # if self._provjeri_koristenje_elementa(element_id):
            #     st.warning(f"Element '{element_za_uklanjanje.naziv}' se koristi i ne može se ukloniti.")
            #     return False
            
            naziv_elementa = element_za_uklanjanje.naziv
            tip_instance = type(element_za_uklanjanje)

            if tip_instance == FloorType:
                self.building_elements_model.ukloni_pod(element_id)
            elif tip_instance == CeilingType:
                self.building_elements_model.ukloni_strop(element_id)
            elif tip_instance == WallType:
                self.building_elements_model.ukloni_zid(element_id)
            elif tip_instance == WindowType:
                self.building_elements_model.ukloni_prozor(element_id)
            elif tip_instance == DoorType:
                self.building_elements_model.ukloni_vrata(element_id)
            else:
                st.error(f"Nepoznat tip instance za element ID {element_id} prilikom uklanjanja.")
                return False
            
            # BuildingElementsModel.ukloni_* metode već zovu spremi_elemente()
            st.success(f"Element '{naziv_elementa}' (ID: {element_id}) uspješno uklonjen.")
            return True
        except Exception as e:
            st.error(f"Greška prilikom uklanjanja elementa {element_id}: {str(e)}")
            return False
    
    def _provjeri_koristenje_elementa(self, element_id):
        """
        Provjerava koristi li se element negdje u modelu (npr. u prostorijama).
        OVO JE PLACEHOLDER - Potrebna implementacija stvarne provjere.
        
        Parameters:
        -----------
        element_id : str
            ID elementa koji se provjerava
            
        Returns:
        --------
        bool
            True ako se element koristi, False inače
        """
        # Primjer: Provjeriti je li element_id referenciran u self.multi_room_model (ako je dostupan)
        # ili u drugim dijelovima aplikacije koji koriste ove tipove elemenata.
        # Za sada, uvijek vraća False da omogući brisanje.
        return False
