"""
UI komponente za upravljanje stambenim jedinicama u heat loss kalkulatoru.
"""

import streamlit as st
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
        # Uvijek prvo osvježimo podatke iz session state
        self.model._ucitaj_iz_session_state()
        
        st.header("🏠 Upravljanje stambenim jedinicama")
        if not self.model.etaze:
            st.warning("Prvo dodajte etaže prije dodavanja stambenih jedinica.")
            return
        
        # Provjera i informacija o novim stambenim jedinicama
        if st.session_state.get("nova_stambena_jedinica_dodana", False):
            st.success("Nova stambena jedinica je uspješno dodana.")
        
        # Tabs za različite operacije
        tab1, tab2, tab3 = st.tabs(["📋 Pregled", "➕ Dodaj novu", "📊 Izvještaj"])
        
        with tab1:
            self._prikazi_pregled_stambenih_jedinica()
        
        with tab2:
            self._prikazi_dodaj_stambenu_jedinicu()
        
        with tab3:
            self._prikazi_izvjestaj_stambenih_jedinica()
            
    def _prikazi_pregled_stambenih_jedinica(self):
        """Prikazuje pregled postojećih stambenih jedinica."""
        st.subheader("Postojeće stambene jedinice")
        
        # Uvijek prvo osvježimo podatke iz session state
        self.model._ucitaj_iz_session_state()
        
        # Provjera je li nedavno dodana nova stambena jedinica
        if st.session_state.get("nova_stambena_jedinica_dodana", False):
            # Ako imamo novododanu stambenu jedinicu, dodatno osvježavamo prikaz
            st.info("Osvježavanje prikaza novih stambenih jedinica...")
            # Resetiramo flag da ne ponavlja poruku
            st.session_state["nova_stambena_jedinica_dodana"] = False
        
        # Grupiranje po etažama
        for etaza in sorted(self.model.etaze, key=lambda e: e.redni_broj):
            stambene_jedinice = self.controller.dohvati_stambene_jedinice_za_etazu(etaza.id)
            
            # Using container with border instead of expander to avoid nesting issues
            with st.container(border=True):
                st.markdown(f"### 🏢 {etaza.naziv} ({len(stambene_jedinice)} stambenih jedinica)")
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
                if st.button("✏️", key=f"edit_sj_overview_{etaza.id}_{stambena_jedinica.id}",
                           help="Uredi stambenu jedinicu"):
                    st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = True
                
                if st.button("🗑️", key=f"delete_sj_overview_{etaza.id}_{stambena_jedinica.id}",
                           help="Ukloni stambenu jedinicu"):
                    self.controller.ukloni_stambenu_jedinicu(stambena_jedinica.id)
                    st.rerun()
            
            # Forma za uređivanje (prikazuje se kad se klikne Edit)
            if st.session_state.get(f"edit_stambena_jedinica_{stambena_jedinica.id}", False):
                self._prikazi_formu_za_uredjivanje(stambena_jedinica)
            
            # Prikaz prostorija u stambenoj jedinici
            prostorije = self.model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica.id)
            if prostorije:
                with st.expander(f"📋 Prostorije u {stambena_jedinica.naziv} ({len(prostorije)})", 
                               expanded=False):
                    self._prikazi_prostorije_u_stambenoj_jedinici(stambena_jedinica.id, prostorije)

    def _prikazi_formu_za_uredjivanje(self, stambena_jedinica):
        """Prikazuje formu za uređivanje stambene jedinice."""
        st.markdown("##### Uredi stambenu jedinicu")
        
        with st.form(key=f"edit_form_{stambena_jedinica.id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                novi_naziv = st.text_input("Naziv", value=stambena_jedinica.naziv)
                novi_tip = st.selectbox("Tip", 
                                      options=list(TIPOVI_STAMBENIH_JEDINICA.keys()),
                                      index=list(TIPOVI_STAMBENIH_JEDINICA.keys()).index(stambena_jedinica.tip))
            
            with col2:
                novi_opis = st.text_area("Opis", value=stambena_jedinica.opis, height=100)
            
            submitted = st.form_submit_button("💾 Spremi promjene")
            
            if submitted:
                self.controller.uredi_stambenu_jedinicu(
                    stambena_jedinica.id, novi_naziv, novi_tip, novi_opis
                )
                st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = False
                st.rerun()
        
        if st.button("❌ Odustani", key=f"cancel_edit_{stambena_jedinica.id}"):
            st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = False
            st.rerun()

    def _prikazi_prostorije_u_stambenoj_jedinici(self, stambena_jedinica_id, prostorije):
        """Prikazuje prostorije u stambenoj jedinici."""
        
        # Dugme za dodavanje nove prostorije
        if st.button("➕ Dodaj prostoriju", key=f"add_room_to_{stambena_jedinica_id}"):
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
                if st.button("🔄", key=f"move_room_{prostorija.id}",
                           help="Premjesti u drugu stambenu jedinicu"):
                    st.session_state[f"show_move_room_{prostorija.id}"] = True
                    st.rerun()
        
        # Forma za premještanje prostorije
        self._prikazi_forme_za_premjestanje(prostorije)

    def _prikazi_formu_za_novu_prostoriju(self, stambena_jedinica_id):
        """Prikazuje formu za dodavanje nove prostorije u stambenu jedinicu."""
        with st.form(key=f"new_room_form_{stambena_jedinica_id}"):
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
                submitted = st.form_submit_button("➕ Dodaj prostoriju")
            with col_cancel:
                cancelled = st.form_submit_button("❌ Odustani")
            
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
                with st.form(key=f"move_room_form_{prostorija.id}"):
                    st.markdown(f"##### Premjesti prostoriju '{prostorija.naziv}'")
                    
                    # Dohvati sve stambene jedinice na istoj etaži
                    stambene_jedinice = self.controller.dohvati_stambene_jedinice_za_etazu(prostorija.etaza_id)
                    stambene_jedinice = [s for s in stambene_jedinice if s.id != prostorija.stambena_jedinica_id]
                    
                    if not stambene_jedinice:
                        st.info("Nema drugih stambenih jedinica na ovoj etaži.")
                        if st.form_submit_button("❌ Zatvori"):
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
                        submitted = st.form_submit_button("🔄 Premjesti")
                    with col_cancel:
                        cancelled = st.form_submit_button("❌ Odustani")
                    
                        if submitted:
                            if nova_stambena_jedinica_id == "none":
                                self.controller.ukloni_prostoriju_iz_stambene_jedinice(prostorija.id)
                            else:                            self.controller.premjesti_prostoriju_u_stambenu_jedinicu(
                                    prostorija.id, nova_stambena_jedinica_id
                                )
                            st.session_state[f"show_move_room_{prostorija.id}"] = False
                            st.rerun()
                        
                        if cancelled:
                            st.session_state[f"show_move_room_{prostorija.id}"] = False
                            st.rerun()

    def _prikazi_dodaj_stambenu_jedinicu(self):
        """Prikazuje formu za dodavanje nove stambene jedinice."""
        st.subheader("Dodaj novu stambenu jedinicu")
        
        # Dodajemo provjeru jesu li već dodane stambene jedinice koje nisu vidljive
        if st.session_state.get("nova_stambena_jedinica_dodana", False):
            # Već imamo dodanu stambenu jedinicu koja nije prikazana - osvježimo podatke
            st.info("Detektirano osvježavanje podataka...")
            self.model._ucitaj_iz_session_state()
            # Resetiramo flag da ne ponavlja poruku
            st.session_state["nova_stambena_jedinica_dodana"] = False
        
        # Use a unique form key based on context
        form_key = f"nova_stambena_jedinica_main_tab_{self.context}"
        with st.form(form_key):
            col1, col2 = st.columns(2)
            
            with col1:
                # Izbor etaže
                etaza_options = {e.id: f"{e.naziv} (Etaža {e.redni_broj})" for e in self.model.etaze}
                etaza_id = st.selectbox("Etaža", options=list(etaza_options.keys()), 
                                      format_func=lambda x: etaza_options[x])
                
                naziv = st.text_input("Naziv stambene jedinice", placeholder="npr. Stan A, Apartman 1")
                
            with col2:
                tip = st.selectbox("Tip stambene jedinice", 
                                 options=list(TIPOVI_STAMBENIH_JEDINICA.keys()))
                opis = st.text_area("Opis (neobavezno)", 
                                  placeholder="Kratki opis stambene jedinice...",
                                  height=100)
            
            submitted = st.form_submit_button("➕ Dodaj stambenu jedinicu")
            
            if submitted:
                if not naziv.strip():
                    st.error("Naziv stambene jedinice je obavezan.")
                else:
                    stambena_jedinica = self.controller.dodaj_stambenu_jedinicu(etaza_id, naziv, tip, opis)
                    if stambena_jedinica:                        # Dodajemo informaciju u session_state PRIJE poziva rerun
                        st.session_state["nova_stambena_jedinica_dodana"] = True
                        st.session_state["zadnja_dodana_id"] = stambena_jedinica.id
                        st.session_state["zadnja_etaza_id"] = etaza_id
                        
                        # Ensure model is properly saved to session state
                        self.model._spremi_u_session_state()
                        
                        # Debug info - but not too verbose
                        st.success(f"Stambena jedinica '{naziv}' je uspješno dodana. ID: {stambena_jedinica.id}")
                        
                        # Ponovno pokrenimo aplikaciju da bi se prikazale promjene
                        st.rerun()

    def _prikazi_izvjestaj_stambenih_jedinica(self):
        """Prikazuje izvještaj o stambenim jedinicama."""
        st.subheader("📊 Izvještaj stambenih jedinica")
        
        # Ensure model is synced with session state before displaying units
        self.model._ucitaj_iz_session_state()
        
        # Ukupni sažetak
        ukupno_jedinica = len(self.model.stambene_jedinice)
        ukupna_povrsina = sum(s.ukupna_povrsina for s in self.model.stambene_jedinice)
        ukupni_gubici = sum(s.ukupni_gubici for s in self.model.stambene_jedinice)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ukupno stambenih jedinica", ukupno_jedinica)
        with col2:
            st.metric("Ukupna površina", f"{ukupna_povrsina:.1f} m²")
        with col3:
            st.metric("Ukupni gubici", f"{ukupni_gubici:.0f} W")
        
        if not self.model.stambene_jedinice:
            st.info("Nema stambenih jedinica za prikaz.")
            return
        
        # Izvještaj po etažama
        st.markdown("##### Raspored po etažama")
        for etaza in sorted(self.model.etaze, key=lambda e: e.redni_broj):
            summary = self.controller.get_summary_for_etaza(etaza.id)
            
            if summary["broj_stambenih_jedinica"] == 0:
                continue
            
            with st.expander(f"🏢 {etaza.naziv} - {summary['broj_stambenih_jedinica']} jedinica"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Stambene jedinice", summary["broj_stambenih_jedinica"])
                with col2:
                    st.metric("Prostorije", summary["ukupan_broj_prostorija"])
                with col3:
                    st.metric("Površina", f"{summary['ukupna_povrsina']:.1f} m²")
                with col4:
                    st.metric("Gubici", f"{summary['ukupni_gubici']:.0f} W")
                
                # Tipovi stambenih jedinica na etaži
                if summary["tipovi_jedinica"]:
                    st.write("**Tipovi:** " + ", ".join(summary["tipovi_jedinica"]))

    def prikazi_malu_karticu_stambene_jedinice(self, stambena_jedinica):
        """Prikazuje malu karticu stambene jedinice za korištenje u drugim komponentama."""
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{stambena_jedinica.naziv}**")
                st.caption(f"{stambena_jedinica.tip}")
            
            with col2:
                prostorije = len(self.model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica.id))
                st.metric("Prostorije", prostorije, label_visibility="collapsed")
            
            with col3:
                st.metric("Površina", f"{stambena_jedinica.ukupna_povrsina:.1f} m²", 
                         label_visibility="collapsed")

    def prikazi_selector_stambenih_jedinica(self, etaza_id=None, default_value=None, key_suffix=""):
        """
        Prikazuje selector za izbor stambene jedinice.
        
        Parameters:
        -----------
        etaza_id : str, optional
            ID etaže za filtriranje stambenih jedinica
        default_value : str, optional
            Defaultna vrijednost
        key_suffix : str
            Sufiks za Streamlit key
            
        Returns:
        --------
        str or None
            ID odabrane stambene jedinice
        """
        # Ensure model is synced with session state before retrieving units
        self.model._ucitaj_iz_session_state()
        
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
            key=f"stambena_jedinica_selector_{key_suffix}"
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
        # First ensure we load the latest data from session state
        model._ucitaj_iz_session_state()
        
        etaza = model.dohvati_etazu(etaza_id)
        if not etaza:
            st.error("Etaža nije pronađena.")
            return
        
        # Provjera je li nedavno dodana nova stambena jedinica
        if st.session_state.get("nova_stambena_jedinica_dodana", False) and \
           st.session_state.get("zadnja_etaza_id") == etaza_id:
            # Već imamo dodanu stambenu jedinicu koja nije prikazana - osvježimo podatke
            st.info("Osvježavanje prikaza novih stambenih jedinica...")
            # Resetiramo flag da ne ponavlja poruku
            st.session_state["nova_stambena_jedinica_dodana"] = False
        
        # Dodavanje nove stambene jedinice na etažu
        with st.expander("Dodaj novu stambenu jedinicu", expanded=False):
            self._forma_za_dodavanje_stambene_jedinice(etaza, controller)
        
        # Prikaz postojećih stambenih jedinica na etaži
        stambene_jedinice = model.dohvati_stambene_jedinice_za_etazu(etaza_id)
        
        if not stambene_jedinice:
            st.info(f"Nema definiranih stambenih jedinica na etaži {etaza.naziv}. Dodajte novu stambenu jedinicu.")
            return
        
        st.subheader(f"Stambene jedinice na etaži: {etaza.naziv}")
        
        for stambena_jedinica in stambene_jedinice:
            self._prikazi_kartu_stambene_jedinice(stambena_jedinica, model, controller, show_floor_info=False)

    def _forma_za_dodavanje_stambene_jedinice(self, etaza, controller):
        """Prikazuje formu za dodavanje nove stambene jedinice na odabranu etažu."""
        # Provjeri imamo li dodanu stambenu jedinicu koja još nije vidljiva
        if st.session_state.get("nova_stambena_jedinica_dodana", False) and \
           st.session_state.get("zadnja_etaza_id") == etaza.id:
            # Već imamo dodanu stambenu jedinicu koja nije prikazana - osvježimo podatke
            st.info("Osvježavanje prikaza novih stambenih jedinica...")
            # Explicitly load from session state to get the latest data
            controller.model._ucitaj_iz_session_state()
            # Resetiramo flag da ne ponavlja poruku
            st.session_state["nova_stambena_jedinica_dodana"] = False
        
        # Use unique form key with context
        form_key = f"nova_stambena_jedinica_etaza_{etaza.id}_{self.context}"
        with st.form(key=form_key):
            st.markdown("##### Dodaj novu stambenu jedinicu")
            
            col1, col2 = st.columns(2)
            with col1:
                naziv = st.text_input("Naziv stambene jedinice", placeholder="npr. Stan A, Apartman 1")
                
            with col2:
                tip = st.selectbox("Tip stambene jedinice", 
                                 options=list(TIPOVI_STAMBENIH_JEDINICA.keys()))
                
                opis = st.text_area("Opis (neobavezno)", 
                                  placeholder="Kratki opis stambene jedinice...",
                                  height=100)
            submitted = st.form_submit_button("➕ Dodaj stambenu jedinicu")
            
            if submitted:
                if not naziv.strip():
                    st.error("Naziv stambene jedinice je obavezan.")
                else:
                    stambena_jedinica = controller.dodaj_stambenu_jedinicu(etaza.id, naziv, tip, opis)
                    if stambena_jedinica:
                        # Success message after successfully adding
                        st.success(f"Stambena jedinica '{naziv}' je uspješno dodana.")
                        
                        # Make sure the model is saved to session state before rerunning
                        controller.model._spremi_u_session_state()
                        
                        # Rerun to refresh the UI and show the new unit
                        st.rerun()

    def _prikazi_kartu_stambene_jedinice(self, stambena_jedinica, model, controller, show_floor_info=True):
        """Prikazuje karticu stambene jedinice, sa mogućnošću uređivanja i brisanja."""
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
                # Dugmad za akcije - unique keys for manager context
                if st.button("✏️", key=f"edit_sj_manager_{stambena_jedinica.id}",
                           help="Uredi stambenu jedinicu"):
                    st.session_state[f"edit_stambena_jedinica_{stambena_jedinica.id}"] = True
                
                if st.button("🗑️", key=f"delete_sj_manager_{stambena_jedinica.id}",
                           help="Ukloni stambenu jedinicu"):
                    controller.ukloni_stambenu_jedinicu(stambena_jedinica.id)
                    st.rerun()
            
            # Forma za uređivanje (prikazuje se kad se klikne Edit)
            if st.session_state.get(f"edit_stambena_jedinica_{stambena_jedinica.id}", False):
                self._prikazi_formu_za_uredjivanje(stambena_jedinica)
            
            # Prikaz prostorija u stambenoj jedinici
            prostorije = model.dohvati_prostorije_za_stambenu_jedinicu(stambena_jedinica.id)
            if prostorije:
                with st.expander(f"📋 Prostorije u {stambena_jedinica.naziv} ({len(prostorije)})", 
                               expanded=False):
                    self._prikazi_prostorije_u_stambenoj_jedinici(stambena_jedinica.id, prostorije)
            
            if show_floor_info:
                # Informacije o etaži
                etaza = model.dohvati_etazu(stambena_jedinica.etaza_id)
                if etaza:
                    st.caption(f"Etaža: {etaza.naziv} (Redni broj: {etaza.redni_broj})")
                else:
                    st.caption("Etaža: N/A")

    def _prikazi_etazu(self, etaza):
        """Prikazuje informacije o etaži."""
        with st.container():
            st.markdown("---")
            st.subheader(f"Etaža: {etaza.naziv}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Redni broj etaže", etaza.redni_broj)
            
            with col2:
                st.metric("Broj stambenih jedinica", len(self.model.dohvati_stambene_jedinice_za_etazu(etaza.id)))
            
            # Dugmad za akcije
            if st.button("✏️ Uredi etažu", key=f"edit_etaza_{etaza.id}"):
                st.session_state[f"edit_etaza_{etaza.id}"] = True
            
            if st.button("🗑️ Ukloni etažu", key=f"delete_etaza_{etaza.id}"):
                # Note: Floor removal should be handled by a dedicated floor controller
                # For now, we'll handle it through the model directly
                self.model.ukloni_etazu(etaza.id)
                st.rerun()
            
            # Forma za uređivanje etaže
            if st.session_state.get(f"edit_etaza_{etaza.id}", False):
                self._prikazi_formu_za_uredjivanje_etaze(etaza)
            
            # Prikaz stambenih jedinica na etaži
            stambene_jedinice = self.model.dohvati_stambene_jedinice_za_etazu(etaza.id)
            if stambene_jedinice:
                st.subheader("Stambene jedinice na etaži")
                for stambena_jedinica in stambene_jedinice:
                    self._prikazi_kartu_stambene_jedinice(stambena_jedinica, self.model, self.controller, show_floor_info=False)
            else:
                st.info("Nema stambenih jedinica na ovoj etaži.")

    def _prikazi_formu_za_uredjivanje_etaze(self, etaza):
        """Prikazuje formu za uređivanje etaže."""
        st.markdown("##### Uredi etažu")
        
        with st.form(key=f"edit_form_etaza_{etaza.id}"):
            col1, col2 = st.columns(2)
            
            with col1:
                novi_naziv = st.text_input("Naziv etaže", value=etaza.naziv)
            
            with col2:
                novi_redni_broj = st.number_input("Redni broj etaže", value=etaza.redni_broj, min_value=1)
            
            submitted = st.form_submit_button("💾 Spremi promjene")
            
            if submitted:
                # Note: Floor editing should be handled by a dedicated floor controller
                # For now, we'll handle it through the model directly
                etaza.naziv = novi_naziv
                etaza.redni_broj = novi_redni_broj
                st.session_state[f"edit_etaza_{etaza.id}"] = False
                st.rerun()
        
        if st.button("❌ Odustani", key=f"cancel_edit_etaza_{etaza.id}"):
            st.session_state[f"edit_etaza_{etaza.id}"] = False
            st.rerun()

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
    # Stvori instancu UI klase s jedinstvenim kontekstom
    import time
    context = f"main_{int(time.time()*1000)}"
    ui = StambenaJedinicaUI(model, None, context)  # prostorija_controller nije potreban za osnovni prikaz
    ui.controller = controller  # Koristi prosliješeni controller
    ui.prikazi_upravljanje_stambenim_jedinicama()


def prikazi_manager_stambenih_jedinica_za_etazu(model, etaza_id, controller, show_debug=False):
    """
    Standalone funkcija za upravljanje stambenim jedinicama na specifičnoj etaži.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s etažama i stambenim jedinicama
    etaza_id : str
        ID etaže za koju se upravljaju stambene jedinice
    controller : StambenaJedinicaController
        Kontroler za upravljanje stambenim jedinicama
    show_debug : bool, optional
        Prikazuje debugging informacije ako je True
    """
    # Always load the latest data from session state first
    model._ucitaj_iz_session_state()
    
    # Stvori instancu UI klase s jedinstvenim kontekstom
    import time
    context = f"etaza_{etaza_id}_{int(time.time()*1000)}"
    ui = StambenaJedinicaUI(model, None, context)  # prostorija_controller nije potreban
    ui.controller = controller  # Koristi prosliješeni controller
    
    # Check if we just added a new housing unit
    if st.session_state.get("nova_stambena_jedinica_dodana", False) and st.session_state.get("zadnja_etaza_id") == etaza_id:
        st.info("Osvježavanje prikaza novih stambenih jedinica...")
        # Reset the flag to avoid showing the message again
        st.session_state["nova_stambena_jedinica_dodana"] = False
    
    # Show debug info if requested
    if show_debug:
        debug_session_state()
        
        # Display housing unit count
        stambene_jedinice = model.dohvati_stambene_jedinice_za_etazu(etaza_id)
        st.write(f"Pronađeno {len(stambene_jedinice)} stambenih jedinica na etaži {etaza_id}")
    
    # Pass to the proper instance method
    ui.prikazi_manager_stambenih_jedinica_za_etazu(model, etaza_id, controller)


def prikazi_selector_stambenih_jedinica(model, etaza_id=None, default_value=None, key_suffix=""):
    """
    Standalone funkcija za prikaz selectora stambenih jedinica.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s etažama i stambenim jedinicama
    etaza_id : str, optional
        ID etaže za filtriranje stambenih jedinica
    default_value : str, optional
        Defaultna vrijednost selectora
    key_suffix : str, optional
        Sufiks za jedinstvene ključeve
        
    Returns:
    --------
    str or None
        ID odabrane stambene jedinice
    """
    # Stvori instancu UI klase s jedinstvenim kontekstom
    import time
    context = f"selector_{int(time.time()*1000)}_{key_suffix}"
    ui = StambenaJedinicaUI(model, None, context)
    return ui.prikazi_selector_stambenih_jedinica(etaza_id, default_value, key_suffix)

def debug_session_state(key=None, max_items=10):
    """
    Pomoćna funkcija za debugiranje session state-a.
    
    Parameters:
    -----------
    key : str, optional
        Specifični ključ koji se traži. Ako nije naveden, prikazuje sve ključeve.
    max_items : int, optional
        Maksimalni broj ključeva za prikaz (za preglednost)
    """
    with st.expander("🔍 Debug - Session State", expanded=False):
        if key:
            if key in st.session_state:
                value = st.session_state[key]
                st.write(f"**{key}**: {value}")
            else:
                st.write(f"Ključ '{key}' nije pronađen u session state-u.")
        else:
            st.write("### Ključevi u Session State-u:")
            keys = list(st.session_state.keys())
            displayed_keys = keys[:max_items] if max_items else keys
            
            for k in displayed_keys:
                # Skip streamlit's internal keys and large objects
                if isinstance(k, str) and k.startswith("_st_"):
                    continue
                
                try:
                    v = st.session_state[k]
                    if isinstance(v, (list, dict)) and len(str(v)) > 100:
                        st.write(f"**{k}**: [complex object]")
                    else:
                        st.write(f"**{k}**: {v}")
                except:
                    st.write(f"**{k}**: [error displaying value]")
            
            if len(keys) > max_items:
                st.write(f"... i još {len(keys) - max_items} ključeva")
            
            st.write(f"Ukupno: {len(keys)} ključeva u session state-u.")
    
    return None
