"""
Controller za upravljanje stambenim jedinicama u heat loss kalkulatoru.
"""

import streamlit as st
from ..models.stambena_jedinica import StambenaJedinica, TIPOVI_STAMBENIH_JEDINICA


class StambenaJedinicaController:
    """Controller za upravljanje stambenim jedinicama."""
    
    def __init__(self, model):
        """
        Inicijalizira StambenaJedinicaController.
        
        Parameters:
        -----------
        model : MultiRoomModel
            Referenca na glavni model
        """
        self.model = model

    def dodaj_stambenu_jedinicu(self, etaza_id, naziv, tip, opis=""):
        """
        Dodaje novu stambenu jedinicu u model.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže u koju se dodaje stambena jedinica
        naziv : str
            Naziv stambene jedinice
        tip : str
            Tip stambene jedinice (iz TIPOVI_STAMBENIH_JEDINICA)
        opis : str
            Opis stambene jedinice
            
        Returns:
        --------
        StambenaJedinica or None
            Nova stambena jedinica ili None ako etaža ne postoji
        """
        if not naziv or not naziv.strip():
            st.error("Naziv stambene jedinice ne može biti prazan.")
            return None
        
        # Provjeri postoji li već stambena jedinica s istim nazivom na etaži
        postojece_jedinice = self.model.dohvati_stambene_jedinice_za_etazu(etaza_id)
        if any(j.naziv == naziv for j in postojece_jedinice):
            st.error(f"Stambena jedinica s nazivom '{naziv}' već postoji na ovoj etaži.")
            return None
        
        # Validiraj tip stambene jedinice
        if tip not in TIPOVI_STAMBENIH_JEDINICA:
            st.error(f"Neispravni tip stambene jedinice: {tip}")
            return None
        
        # Create and save the new stambena jedinica
        stambena_jedinica = self.model.dodaj_stambenu_jedinicu(etaza_id, naziv, tip, opis)
        
        # Ensure the model is properly saved to session state
        if stambena_jedinica:
            # Explicitly save to session state for reliability
            self.model._spremi_u_session_state()
            
            # Set flag for UI to know that a new unit was added
            st.session_state["nova_stambena_jedinica_dodana"] = True
            st.session_state["zadnja_dodana_id"] = stambena_jedinica.id
            st.session_state["zadnja_etaza_id"] = etaza_id
            
        return stambena_jedinica

    def ukloni_stambenu_jedinicu(self, stambena_jedinica_id):
        """
        Uklanja stambenu jedinicu iz modela.
        
        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice koja se uklanja
        """
        stambena_jedinica = self.model.dohvati_stambenu_jedinicu(stambena_jedinica_id)
        if not stambena_jedinica:
            st.error("Stambena jedinica nije pronađena.")
            return
        
        # Provjeri ima li stambena jedinica prostorije
        prostorije = self.model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica_id)
        if prostorije:
            st.warning(f"Stambena jedinica '{stambena_jedinica.naziv}' sadrži {len(prostorije)} prostorija/e. "
                      f"Sve prostorije će biti uklonjene.")
            
            # Potvrda od korisnika
            if not st.button(f"Potvrdi brisanje stambene jedinice '{stambena_jedinica.naziv}'", 
                           key=f"confirm_delete_stambena_jedinica_{stambena_jedinica_id}"):
                return
        
        self.model.ukloni_stambenu_jedinicu(stambena_jedinica_id)
        st.success(f"Stambena jedinica '{stambena_jedinica.naziv}' je uspješno uklonjena.")

    def uredi_stambenu_jedinicu(self, stambena_jedinica_id, novi_naziv=None, novi_tip=None, novi_opis=None):
        """
        Uređuje postojeću stambenu jedinicu.
        
        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice koja se uređuje
        novi_naziv : str, optional
            Novi naziv stambene jedinice
        novi_tip : str, optional
            Novi tip stambene jedinice
        novi_opis : str, optional
            Novi opis stambene jedinice
        """
        stambena_jedinica = self.model.dohvati_stambenu_jedinicu(stambena_jedinica_id)
        if not stambena_jedinica:
            st.error("Stambena jedinica nije pronađena.")
            return
          # Provjeri valjanost novih vrijednosti
        if novi_naziv and not novi_naziv.strip():
            st.error("Naziv stambene jedinice ne može biti prazan.")
            return
            
        if novi_tip and novi_tip not in TIPOVI_STAMBENIH_JEDINICA:
            st.error(f"Neispravni tip stambene jedinice: {novi_tip}")
            return
        
        # Provjeri jedinstvenost naziva na etaži (samo ako se naziv mijenja)
        if novi_naziv and novi_naziv != stambena_jedinica.naziv:
            postojece_jedinice = self.model.dohvati_stambene_jedinice_za_etazu(stambena_jedinica.etaza_id)
            if any(j.naziv == novi_naziv and j.id != stambena_jedinica_id for j in postojece_jedinice):
                st.error(f"Stambena jedinica s nazivom '{novi_naziv}' već postoji na ovoj etaži.")
                return
        
        # Primijeni promjene
        if novi_naziv:
            stambena_jedinica.naziv = novi_naziv
        if novi_tip:
            stambena_jedinica.tip = novi_tip
        if novi_opis is not None:
            stambena_jedinica.opis = novi_opis
        
        # Preračunaj stambenu jedinicu
        stambena_jedinica.preracunaj()
        
        # Spremi promjene
        self.model._spremi_u_session_state()
        st.success(f"Stambena jedinica '{stambena_jedinica.naziv}' je uspješno ažurirana.")

    def dodaj_prostoriju_u_stambenu_jedinicu(self, stambena_jedinica_id, naziv, tip, povrsina):
        """
        Dodaje novu prostoriju u stambenu jedinicu.
        
        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice u koju se dodaje prostorija
        naziv : str
            Naziv prostorije
        tip : str
            Tip prostorije
        povrsina : float
            Površina prostorije u m²
            
        Returns:
        --------
        Prostorija or None
            Nova prostorija ili None ako je dodavanje neuspješno
        """
        if not naziv or not naziv.strip():
            st.error("Naziv prostorije ne može biti prazan.")
            return None
        
        try:
            povrsina = float(povrsina)
            if povrsina <= 0:
                st.error("Površina prostorije mora biti veća od nule.")
                return None
        except (ValueError, TypeError):
            st.error("Površina prostorije mora biti valjani broj.")
            return None
        
        return self.model.dodaj_prostoriju_u_stambenu_jedinicu(
            stambena_jedinica_id, naziv, tip, povrsina
        )

    def ukloni_prostoriju_iz_stambene_jedinice(self, prostorija_id):
        """
        Uklanja prostoriju iz stambene jedinice.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se uklanja iz stambene jedinice
        """
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        if not prostorija:
            st.error("Prostorija nije pronađena.")
            return
        
        if not prostorija.stambena_jedinica_id:
            st.error("Prostorija nije povezana ni s jednom stambenom jedinicom.")
            return
        
        self.model.ukloni_prostoriju_iz_stambene_jedinice(prostorija_id)
        st.success(f"Prostorija '{prostorija.naziv}' je uklonjena iz stambene jedinice.")

    def premjesti_prostoriju_u_stambenu_jedinicu(self, prostorija_id, nova_stambena_jedinica_id):
        """
        Premješta prostoriju iz jedne stambene jedinice u drugu.
        
        Parameters:
        -----------
        prostorija_id : str
            ID prostorije koja se premješta
        nova_stambena_jedinica_id : str
            ID nove stambene jedinice
        """
        prostorija = self.model.dohvati_prostoriju(prostorija_id)
        nova_stambena_jedinica = self.model.dohvati_stambenu_jedinicu(nova_stambena_jedinica_id)
        
        if not prostorija:
            st.error("Prostorija nije pronađena.")
            return
        
        if not nova_stambena_jedinica:
            st.error("Nova stambena jedinica nije pronađena.")
            return
        
        # Provjeri su li prostorija i stambena jedinica na istoj etaži
        if prostorija.etaza_id != nova_stambena_jedinica.etaza_id:
            st.error("Prostorija i stambena jedinica moraju biti na istoj etaži.")
            return
        
        self.model.premjesti_prostoriju_u_stambenu_jedinicu(prostorija_id, nova_stambena_jedinica_id)
        st.success(f"Prostorija '{prostorija.naziv}' je premještena u stambenu jedinicu '{nova_stambena_jedinica.naziv}'.")

    def dohvati_stambene_jedinice_za_etazu(self, etaza_id):
        """
        Dohvaća sve stambene jedinice za određenu etažu.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže
            
        Returns:
        --------
        list[StambenaJedinica]
            Lista stambenih jedinica na etaži
        """
        return self.model.dohvati_stambene_jedinice_za_etazu(etaza_id)

    def dohvati_stambenu_jedinicu(self, stambena_jedinica_id):
        """
        Dohvaća stambenu jedinicu po ID-u.
        
        Parameters:
        -----------
        stambena_jedinica_id : str
            ID stambene jedinice
            
        Returns:
        --------
        StambenaJedinica or None
            Stambena jedinica ili None ako ne postoji
        """
        return self.model.dohvati_stambenu_jedinicu(stambena_jedinica_id)

    def get_summary_for_etaza(self, etaza_id):
        """
        Vraća sažetak stambenih jedinica za etažu.
        
        Parameters:
        -----------
        etaza_id : str
            ID etaže
            
        Returns:
        --------
        dict
            Sažetak s brojem stambenih jedinica i ukupnim podacima
        """
        stambene_jedinice = self.dohvati_stambene_jedinice_za_etazu(etaza_id)
        
        ukupna_povrsina = sum(s.ukupna_povrsina for s in stambene_jedinice)
        ukupni_gubici = sum(s.ukupni_gubici for s in stambene_jedinice)
        ukupan_broj_prostorija = sum(len(s.prostorije) for s in stambene_jedinice)
        
        return {
            "broj_stambenih_jedinica": len(stambene_jedinice),
            "ukupna_povrsina": ukupna_povrsina,
            "ukupni_gubici": ukupni_gubici,
            "ukupan_broj_prostorija": ukupan_broj_prostorija,
            "tipovi_jedinica": {s.tip for s in stambene_jedinice}
        }
