"""
UI komponente za upravljanje stambenim jedinicama u heat loss kalkulatoru.
Pojednostavljena verzija koja funkcioniše.
"""

import streamlit as st
import time
from ..models.stambena_jedinica import StambenaJedinica, TIPOVI_STAMBENIH_JEDINICA
from ..controllers.stambena_jedinica_controller import StambenaJedinicaController


class StambenaJedinicaUI:
    """UI klasa za upravljanje stambenim jedinicama."""
    
    def __init__(self, model, prostorija_controller, context="default"):
        """
        Inicijalizira StambenaJedinicaUI.
        
        Parameters:
        -----------
        model : MultiRoomModel
            Referenca na glavni model
        prostorija_controller : ProstorijaController
            Controller za upravljanje prostorijama
        context : str
            Kontekst za kreiranje jedinstvenih ključeva
        """
        self.model = model
        self.controller = StambenaJedinicaController(model)
        self.prostorija_controller = prostorija_controller
        self.context = context
        
        # Ensure session state variables exist
        if "nova_stambena_jedinica_dodana" not in st.session_state:
            st.session_state["nova_stambena_jedinica_dodana"] = False
        if "zadnja_dodana_id" not in st.session_state:
            st.session_state["zadnja_dodana_id"] = None
        if "zadnja_etaza_id" not in st.session_state:
            st.session_state["zadnja_etaza_id"] = None
        if "potrebno_osvjeziti_stambene_jedinice" not in st.session_state:
            st.session_state["potrebno_osvjeziti_stambene_jedinice"] = False
    
    def prikazi_upravljanje_stambenim_jedinicama(self):
        """Prikazuje glavni interface za upravljanje stambenim jedinicama."""
        
        st.header("Upravljanje stambenim jedinicama")
        if not self.model.etaze:
            st.warning("Prvo dodajte etaže prije dodavanja stambenih jedinica.")
            return
        
        # Provjera i informacija o novim stambenim jedinicama
        if st.session_state.get("nova_stambena_jedinica_dodana", False):
            st.success("Nova stambena jedinica je uspješno dodana.")        # Jednostavna forma za dodavanje (bez tabova)
        forma_za_dodavanje_stambene_jedinice(self.model)
        
        # Prikaz postojećih stambenih jedinica
        st.markdown("---")
        self._prikazi_pregled_stambenih_jedinica()
            
    def _prikazi_pregled_stambenih_jedinica(self):
        """Prikazuje pregled postojećih stambenih jedinica."""
        st.subheader("Postojeće stambene jedinice")
        
        # Grupiranje po etažama
        for etaza in sorted(self.model.etaze, key=lambda e: e.redni_broj):
            stambene_jedinice = self.controller.dohvati_stambene_jedinice_za_etazu(etaza.id)
            
            # Using container with border instead of expander to avoid nesting issues
            with st.container(border=True):
                st.markdown(f"### {etaza.naziv} ({len(stambene_jedinice)} stambenih jedinica)")
                if not stambene_jedinice:
                    st.info("Nema stambenih jedinica na ovoj etaži.")
                    continue
                
                # Prikaz stambenih jedinica
                for stambena_jedinica in stambene_jedinice:
                    self._prikazi_stambenu_jedinicu_card(stambena_jedinica, etaza)

    def _prikazi_stambenu_jedinicu_card(self, stambena_jedinica, etaza):
        """Prikazuje karticu za jednu stambenu jedinicu."""
        with st.container():
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{stambena_jedinica.naziv}**")
                st.caption(f"Tip: {stambena_jedinica.tip}")
                if stambena_jedinica.opis:
                    st.caption(f"Opis: {stambena_jedinica.opis}")
            
            with col2:
                prostorije = self.model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica.id)
                st.metric("Prostorije", len(prostorije))                
                if prostorije:
                    prostorije_nazivi = ", ".join([p.naziv for p in prostorije[:3]])
                    if len(prostorije) > 3:
                        prostorije_nazivi += f"... (+{len(prostorije)-3})"
                    st.caption(prostorije_nazivi)
            
            with col3:
                st.metric("Površina", f"{stambena_jedinica.ukupna_povrsina:.1f} m²")
                if stambena_jedinica.ukupni_gubici > 0:
                    st.metric("Gubici", f"{stambena_jedinica.ukupni_gubici:.0f} W")
            
            with col4:
                # Dugmad za akcije - unique keys for overview context with etaza ID
                if st.button("Uredi", key=f"edit_sj_overview_{etaza.id}_{stambena_jedinica.id}_{self.context}",
                           help="Uredi stambenu jedinicu"):
                    st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = True
                
                if st.button("Ukloni", key=f"delete_sj_overview_{etaza.id}_{stambena_jedinica.id}_{self.context}",
                           help="Ukloni stambenu jedinicu"):
                    self.controller.ukloni_stambenu_jedinicu(stambena_jedinica.id)
                    st.rerun()
            
            # Forma za uređivanje (prikazuje se kad se klikne Edit)
            if st.session_state.get(f"edit_stambena_jedinica_{stambena_jedinica.id}", False):
                self._prikazi_formu_za_uredjivanje(stambena_jedinica)
            
            # Prikaz prostorija u stambenoj jedinici
            prostorije = self.model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica.id)
            if prostorije:
                with st.expander(f"Prostorije u {stambena_jedinica.naziv} ({len(prostorije)})", 
                               expanded=False):
                    self._prikazi_prostorije_u_stambenoj_jedinici(stambena_jedinica.id, prostorije)

    def _prikazi_formu_za_uredjivanje(self, stambena_jedinica):
        """Prikazuje formu za uređivanje stambene jedinice."""
        st.markdown("##### Uredi stambenu jedinicu")
        
        with st.form(key=f"edit_form_{stambena_jedinica.id}_{self.context}"):
            col1, col2 = st.columns(2)
            
            with col1:
                novi_naziv = st.text_input("Naziv", value=stambena_jedinica.naziv)
                novi_tip = st.selectbox("Tip", 
                                      options=list(TIPOVI_STAMBENIH_JEDINICA.keys()),
                                      index=list(TIPOVI_STAMBENIH_JEDINICA.keys()).index(stambena_jedinica.tip))
            
            with col2:
                novi_opis = st.text_area("Opis", value=stambena_jedinica.opis, height=100)
                submitted = st.form_submit_button("Spremi promjene")
            
            if submitted:
                self.controller.uredi_stambenu_jedinicu(
                    stambena_jedinica.id, novi_naziv, novi_tip, novi_opis
                )
                st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = False
                st.rerun()
        
        if st.button("Odustani", key=f"cancel_edit_{stambena_jedinica.id}_{self.context}"):
            st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = False
            st.rerun()

    def _prikazi_prostorije_u_stambenoj_jedinici(self, stambena_jedinica_id, prostorije):
        """Prikazuje prostorije u stambenoj jedinici."""
        # Dugme za dodavanje nove prostorije
        if st.button("Dodaj prostoriju", key=f"add_room_to_{stambena_jedinica_id}_{self.context}"):
            st.session_state[f"show_add_room_form_{stambena_jedinica_id}"] = True
            st.rerun()
        
        # Forma za dodavanje nove prostorije
        if st.session_state.get(f"show_add_room_form_{stambena_jedinica_id}", False):
            self._prikazi_formu_za_novu_prostoriju(stambena_jedinica_id)
        
        # Prikaz postojećih prostorija
        for prostorija in prostorije:
            col1, col2, col3, col4 = st.columns([3, 1.5, 1.5, 1])
            
            with col1:
                st.write(f"**{prostorija.naziv}** ({prostorija.tip})")
            
            with col2:
                st.write(f"{prostorija.povrsina} m²")
            
            with col3:
                if hasattr(prostorija, 'ukupni_gubici') and prostorija.ukupni_gubici:
                    st.write(f"{prostorija.ukupni_gubici:.0f} W")
                else:
                    st.write("-")
            
            with col4:
                if st.button("Premjesti", key=f"move_room_{prostorija.id}_{self.context}",
                           help="Premjesti u drugu stambenu jedinicu"):
                    st.session_state[f"show_move_room_{prostorija.id}"] = True
                    st.rerun()
        
        # Forma za premještanje prostorije
        self._prikazi_forme_za_premjestanje(prostorije)

    def _prikazi_formu_za_novu_prostoriju(self, stambena_jedinica_id):
        """Prikazuje formu za dodavanje nove prostorije u stambenu jedinicu."""
        with st.form(key=f"new_room_form_{stambena_jedinica_id}_{self.context}"):
            st.markdown("##### Dodaj novu prostoriju")
            
            col1, col2 = st.columns(2)
            with col1:
                naziv = st.text_input("Naziv prostorije")
                povrsina = st.number_input("Površina (m²)", min_value=0.1, value=20.0, step=0.1)
            
            with col2:
                # Import tipova prostorija
                from ..models.prostorija import TIPOVI_PROSTORIJA
                tip_options = list(TIPOVI_PROSTORIJA.keys())
                tip = st.selectbox("Tip prostorije", options=tip_options)
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submitted = st.form_submit_button("Dodaj prostoriju")
            with col_cancel:
                cancelled = st.form_submit_button("Odustani")
            
            if submitted:
                prostorija = self.controller.dodaj_prostoriju_u_stambenu_jedinicu(
                    stambena_jedinica_id, naziv, tip, povrsina
                )
                if prostorija:
                    st.success(f"Prostorija '{naziv}' je dodana.")
                    st.session_state[f"show_add_room_form_{stambena_jedinica_id}"] = False
                    st.rerun()
            
            if cancelled:
                st.session_state[f"show_add_room_form_{stambena_jedinica_id}"] = False
                st.rerun()

    def _prikazi_forme_za_premjestanje(self, prostorije):
        """Prikazuje forme za premještanje prostorija."""
        for prostorija in prostorije:
            if st.session_state.get(f"show_move_room_{prostorija.id}", False):
                with st.form(key=f"move_room_form_{prostorija.id}_{self.context}"):
                    st.markdown(f"##### Premjesti prostoriju '{prostorija.naziv}'")
                    
                    # Dohvati sve stambene jedinice na istoj etaži
                    stambene_jedinice = self.controller.dohvati_stambene_jedinice_za_etazu(prostorija.etaza_id)
                    stambene_jedinice = [s for s in stambene_jedinice if s.id != prostorija.stambena_jedinica_id]
                    
                    if not stambene_jedinice:
                        st.info("Nema drugih stambenih jedinica na ovoj etaži.")
                        if st.form_submit_button("Zatvori"):
                            st.session_state[f"show_move_room_{prostorija.id}"] = False
                            st.rerun()
                        continue
                    
                    opcije = {s.id: f"{s.naziv} ({s.tip})" for s in stambene_jedinice}
                    opcije["none"] = "Ukloni iz stambene jedinice"
                    
                    nova_stambena_jedinica_id = st.selectbox(
                        "Nova stambena jedinica",
                        options=list(opcije.keys()),
                        format_func=lambda x: opcije[x]
                    )
                    
                    col_submit, col_cancel = st.columns(2)
                    with col_submit:
                        submitted = st.form_submit_button("Premjesti")
                    with col_cancel:
                        cancelled = st.form_submit_button("Odustani")
                    
                    if submitted:
                        if nova_stambena_jedinica_id == "none":
                            self.controller.ukloni_prostoriju_iz_stambene_jedinice(prostorija.id)
                        else:
                            self.controller.premjesti_prostoriju_u_stambenu_jedinicu(prostorija.id, nova_stambena_jedinica_id)
                        st.session_state[f"show_move_room_{prostorija.id}"] = False
                        st.rerun()
                    
                    if cancelled:
                        st.session_state[f"show_move_room_{prostorija.id}"] = False
                        st.rerun()

    def prikazi_selector_stambene_jedinice(self, etaza_id=None, default_value=None, key_suffix="default"):
        """
        Prikazuje selector za odabir stambene jedinice.
        
        Parameters:
        -----------
        etaza_id : str, optional
            ID etaže za filtriranje. Ako nije naveden, prikazuju se sve stambene jedinice.
        default_value : str, optional
            Zadana vrijednost za selector
        key_suffix : str
            Sufiks za ključ komponente
        
        Returns:
        --------
        str or None
            ID odabrane stambene jedinice
        """
        if etaza_id:
            stambene_jedinice = self.controller.dohvati_stambene_jedinice_za_etazu(etaza_id)
        else:
            stambene_jedinice = self.model.stambene_jedinice
        
        if not stambene_jedinice:
            st.info("Nema dostupnih stambenih jedinica.")
            return None
        
        opcije = {s.id: f"{s.naziv} ({s.tip})" for s in stambene_jedinice}
        opcije["none"] = "Bez stambene jedinice"
        
        default_index = 0
        if default_value and default_value in opcije:
            default_index = list(opcije.keys()).index(default_value)
        
        izbor = st.selectbox(
            "Stambena jedinica",
            options=list(opcije.keys()),
            format_func=lambda x: opcije[x],
            index=default_index,
            key=f"stambena_jedinica_selector_{key_suffix}_{self.context}"
        )
        
        return izbor if izbor != "none" else None

    def prikazi_manager_stambenih_jedinica_za_etazu(self, model, etaza_id, controller):
        """
        Prikazuje upravljanje stambenim jedinicama za specifičnu etažu.
        
        Parameters:
        -----------
        model : MultiRoomModel
            Model s etažama i stambenim jedinicama
        etaza_id : str
            ID etaže za koju se prikazuju stambene jedinice
        controller : StambenaJedinicaController
            Kontroler za upravljanje stambenim jedinicama
        """
        etaza = model.dohvati_etazu(etaza_id)
        if not etaza:
            st.error("Etaža nije pronađena.")
            return
        
        # Provjera je li nedavno dodana nova stambena jedinica
        if st.session_state.get("nova_stambena_jedinica_dodana", False) and \
           st.session_state.get("zadnja_etaza_id") == etaza_id:
            st.info("Osvježavanje prikaza novih stambenih jedinica...")
            st.session_state["nova_stambena_jedinica_dodana"] = False
        
        # Dodavanje nove stambene jedinice na etažu - jednostavna forma
        st.subheader("Dodaj novu stambenu jedinicu")
        with st.form(key=f"nova_stambena_jedinica_etaza_{etaza.id}_{self.context}"):
            col1, col2 = st.columns(2)
            with col1:
                naziv = st.text_input("Naziv stambene jedinice", placeholder="npr. Stan A, Apartman 1")
                
            with col2:
                tip = st.selectbox("Tip stambene jedinice", 
                                 options=list(TIPOVI_STAMBENIH_JEDINICA.keys()))
                
            opis = st.text_area("Opis (neobavezno)", 
                              placeholder="Kratki opis stambene jedinice...",
                              height=100)
            
            submitted = st.form_submit_button("Dodaj stambenu jedinicu")
            
            if submitted:
                if not naziv.strip():
                    st.error("Naziv stambene jedinice je obavezan.")
                else:
                    stambena_jedinica = controller.dodaj_stambenu_jedinicu(etaza.id, naziv, tip, opis)
                    if stambena_jedinica:
                        st.success(f"Stambena jedinica '{naziv}' je uspješno dodana.")
                        controller.model._spremi_u_session_state()
                        st.rerun()
        
        # Prikaz postojećih stambenih jedinica na etaži
        stambene_jedinice = model.dohvati_stambene_jedinice_za_etazu(etaza_id)
        
        if not stambene_jedinice:
            st.info(f"Nema definiranih stambenih jedinica na etaži {etaza.naziv}. Dodajte novu stambenu jedinicu.")
            return
        
        st.subheader(f"Stambene jedinice na etaži: {etaza.naziv}")
        
        for stambena_jedinica in stambene_jedinice:
            self._prikazi_kartu_stambene_jedinice_za_etazu(stambena_jedinica, model, controller)

    def _prikazi_kartu_stambene_jedinice_za_etazu(self, stambena_jedinica, model, controller):
        """Prikazuje karticu stambene jedinice za specifičnu etažu."""
        with st.container():
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{stambena_jedinica.naziv}**")
                st.caption(f"Tip: {stambena_jedinica.tip}")
                if stambena_jedinica.opis:
                    st.caption(f"Opis: {stambena_jedinica.opis}")
            
            with col2:
                prostorije = model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica.id)
                st.metric("Prostorije", len(prostorije))
                if prostorije:
                    prostorije_nazivi = ", ".join([p.naziv for p in prostorije[:3]])
                    if len(prostorije) > 3:
                        prostorije_nazivi += f"... (+{len(prostorije)-3})"
                    st.caption(prostorije_nazivi)
            
            with col3:
                st.metric("Površina", f"{stambena_jedinica.ukupna_povrsina:.1f} m²")
                if stambena_jedinica.ukupni_gubici > 0:
                    st.metric("Gubici", f"{stambena_jedinica.ukupni_gubici:.0f} W")
            
            with col4:
                if st.button("Uredi", key=f"edit_sj_manager_{stambena_jedinica.id}_{self.context}",
                           help="Uredi stambenu jedinicu"):
                    st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = True
                
                if st.button("Ukloni", key=f"delete_sj_manager_{stambena_jedinica.id}_{self.context}",
                           help="Ukloni stambenu jedinicu"):
                    controller.ukloni_stambenu_jedinicu(stambena_jedinica.id)
                    st.rerun()
            
            # Forma za uređivanje
            if st.session_state.get(f"edit_stambena_jedinica_{stambena_jedinica.id}", False):
                self._prikazi_formu_za_uredjivanje(stambena_jedinica)
            
            # Prikaz prostorija u stambenoj jedinici
            prostorije = model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica.id)
            if prostorije:
                with st.expander(f"Prostorije u {stambena_jedinica.naziv} ({len(prostorije)})", 
                               expanded=False):
                    self._prikazi_prostorije_u_stambenoj_jedinici(stambena_jedinica.id, prostorije)


def forma_za_dodavanje_stambene_jedinice(model, callback_nakon_dodavanja=None):
    """
    Prikazuje jednostavnu formu za dodavanje nove stambene jedinice (po uzoru na etažu).
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model u koji se dodaje stambena jedinica
    callback_nakon_dodavanja : function
        Funkcija koja se poziva nakon dodavanja stambene jedinice
    """
    if not model.etaze:
        st.warning("Prvo dodajte etaže prije dodavanja stambenih jedinica.")
        return None
    
    st.subheader("Dodaj novu stambenu jedinicu")
    
    # Generiraj jedinstveni ključ
    unique_key = f"dodaj_stambenu_jedinicu_form_{int(time.time()*1000)}"
    
    with st.form(key=unique_key):
        # Odabir etaže
        sortirane_etaze = sorted(model.etaze, key=lambda e: e.redni_broj)
        etaza_opcije = [f"{e.naziv} (#{e.redni_broj})" for e in sortirane_etaze]
        
        selected_etaza_index = st.selectbox(
            "Etaža:",
            range(len(etaza_opcije)), 
            format_func=lambda i: etaza_opcije[i]
        )
        
        naziv = st.text_input("Naziv stambene jedinice:", value="Nova stambena jedinica")
        tip = st.selectbox("Tip stambene jedinice:", options=list(TIPOVI_STAMBENIH_JEDINICA.keys()))
        opis = st.text_area("Opis (opcionalno):", value="", height=100)
        
        submitted = st.form_submit_button("Dodaj stambenu jedinicu")
        
        if submitted:
            selected_etaza = sortirane_etaze[selected_etaza_index]
            nova_stambena_jedinica = model.dodaj_stambenu_jedinicu(
                etaza_id=selected_etaza.id,
                naziv=naziv,
                tip=tip,
                opis=opis
            )
            if nova_stambena_jedinica:
                st.success(f"Dodana nova stambena jedinica: {naziv}")
                if callback_nakon_dodavanja:
                    callback_nakon_dodavanja(nova_stambena_jedinica)
                return nova_stambena_jedinica
    return None


# Standalone funkcije za korištenje u drugim modulima
def prikazi_manager_stambenih_jedinica(model, controller):
    """
    Standalone funkcija za upravljanje stambenim jedinicama.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s etažama i stambenim jedinicama
    controller : StambenaJedinicaController
        Kontroler za upravljanje stambenim jedinicama
    """
    context = f"main_{int(time.time()*1000)}"
    ui = StambenaJedinicaUI(model, None, context)
    ui.controller = controller
    ui.prikazi_upravljanje_stambenim_jedinicama()


def prikazi_manager_stambenih_jedinica_za_etazu(model, etaza_id, controller, show_debug=False):
    """
    Standalone funkcija za upravljanje stambenim jedinicama na specifičnoj etaži.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s etažama i stambenim jedinicama
    etaza_id : str
        ID etaže za koju se prikazuju stambene jedinice
    controller : StambenaJedinicaController
        Kontroler za upravljanje stambenim jedinicama
    show_debug : bool
        Pokazuje debug informacije
    """
    context = f"etaza_{etaza_id}_{int(time.time()*1000)}"
    ui = StambenaJedinicaUI(model, None, context)
    ui.controller = controller
    ui.prikazi_manager_stambenih_jedinica_za_etazu(model, etaza_id, controller)


def prikazi_selector_stambene_jedinice(model, etaza_id=None, default_value=None, key_suffix="default"):
    """
    Standalone funkcija za prikaz selectora stambene jedinice.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s etažama i stambenim jedinicama
    etaza_id : str, optional
        ID etaže za filtriranje
    default_value : str, optional
        Zadana vrijednost
    key_suffix : str
        Sufiks za ključ komponente
        
    Returns:
    --------
    str or None
        ID odabrane stambene jedinice
    """
    context = f"selector_{int(time.time()*1000)}"
    ui = StambenaJedinicaUI(model, None, context)
    return ui.prikazi_selector_stambene_jedinice(etaza_id, default_value, key_suffix)
