"""
Modul koji sadrži funkcije za prikaz i upravljanje etažama u UI-u.
"""

import streamlit as st
# Umjesto direktnog uvoza bolje je koristiti odgođeni uvoz (lazy import)
# funkciju prikazi_manager_prostorija ćemo uvesti unutar funkcije

def prikaz_etaza_izbornika(model, on_etaza_selected=None):
    """
    Prikazuje izbornik za odabir etaže.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model u kojem se nalaze etaže
    on_etaza_selected : function
        Funkcija koja se poziva kad se odabere etaža
    """
    if not model.etaze:
        st.warning("Nema definiranih etaža.")
        return None
    
    st.subheader("Odabir etaže")
    
    # Sortiranje etaža po rednom broju za konzistentan prikaz
    sortirane_etaze = sorted(model.etaze, key=lambda e: e.redni_broj)
    opcije = [f"{e.naziv} (#{e.redni_broj})" for e in sortirane_etaze]
    
    # Dodaj etažu u session state ako ne postoji
    key = "odabrana_etaza_index"
    if key not in st.session_state:
        st.session_state[key] = 0
    
    selected_index = st.selectbox(
        "Etaža:",
        range(len(opcije)), 
        format_func=lambda i: opcije[i],
        key="odabrana_etaza_index"
    )
    
    odabrana_etaza = model.etaze[selected_index]
    
    if on_etaza_selected:
        on_etaza_selected(odabrana_etaza)
        
    return odabrana_etaza

def forma_za_dodavanje_etaze(model, callback_nakon_dodavanja=None):
    """
    Prikazuje formu za dodavanje nove etaže.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model u koji se dodaje etaža
    callback_nakon_dodavanja : function
        Funkcija koja se poziva nakon dodavanja etaže
    """
    st.subheader("Dodaj novu etažu")
    with st.form(key="dodaj_etazu_form"):
        # Inicijaliziramo defaultni redni broj kao maksimalni postojeći + 1
        default_redni_broj = 1
        if model.etaze:
            default_redni_broj = max([e.redni_broj for e in model.etaze]) + 1
        naziv = st.text_input("Naziv etaže:", value=f"Etaža {default_redni_broj}")
        redni_broj = st.number_input("Redni broj:", min_value=1, value=default_redni_broj, step=1)
        broj_etaze = st.number_input("Broj etaže (za numeraciju prostorija):", min_value=1, value=default_redni_broj, step=1, help="Broj koji će se koristiti za numeraciju prostorija (npr. 1.1, 1.2)")
        visina_etaze = st.number_input("Visina etaže [m]:", min_value=1.0, value=2.5, step=0.1)
        submitted = st.form_submit_button("Dodaj etažu")
        if submitted:
            nova_etaza = model.dodaj_etazu(naziv=naziv, redni_broj=redni_broj, visina_etaze=visina_etaze, broj_etaze=broj_etaze)
            if nova_etaza:
                st.success(f"Dodana nova etaža: {naziv}")
                if callback_nakon_dodavanja:
                    callback_nakon_dodavanja(nova_etaza)
                return nova_etaza
    return None

def forma_za_uredivanje_etaze(etaza, model, callback_nakon_uredivanja=None):
    """
    Prikazuje formu za uređivanje postojeće etaže.
    
    Parameters:
    -----------
    etaza : Etaza
        Etaža koja se uređuje
    model : MultiRoomModel
        Model u kojem se nalazi etaža
    callback_nakon_uredivanja : function
        Funkcija koja se poziva nakon uređivanja etaže
        
    Returns:
    --------
    bool
        True ako su promjene uspješno spremljene, False inače
    """
    st.subheader(f"Uredi etažu: {etaza.naziv}")
    with st.form(key=f"uredi_etazu_form_{etaza.id}"):
        naziv = st.text_input("Naziv etaže:", value=etaza.naziv)
        redni_broj = st.number_input("Redni broj:", min_value=1, value=etaza.redni_broj, step=1)
        broj_etaze = st.number_input("Broj etaže (za numeraciju prostorija):", min_value=1, value=getattr(etaza, 'broj_etaze', etaza.redni_broj), step=1, help="Broj koji će se koristiti za numeraciju prostorija (npr. 1.1, 1.2)")
        visina_etaze = st.number_input("Visina etaže [m]:", min_value=1.0, value=etaza.visina_etaze, step=0.1)
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Spremi promjene")
            cancel = st.form_submit_button("Odustani", type="secondary")
        
        if submitted:
            # Direktno ažuriramo objekt etaže
            etaza.naziv = naziv
            etaza.naziv = naziv
            etaza.redni_broj = redni_broj
            etaza.broj_etaze = broj_etaze
            etaza.visina_etaze = visina_etaze
            model._spremi_u_session_state()
            
            st.success(f"Etaža '{naziv}' je uspješno ažurirana!")
            
            if callback_nakon_uredivanja:
                callback_nakon_uredivanja(etaza)
            
            return True
        
        if cancel:
            return False
    
    return None

# Additional functions for the refactored heat_loss module

def prikazi_manager_etaza(model, controller, prostorija_controller, zid_controller, stambena_jedinica_controller=None): # Add stambena_jedinica_controller
    """
    Prikazuje sučelje za upravljanje etažama (dodavanje, uređivanje, brisanje).
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s etažama
    controller : EtazaController
        Kontroler za upravljanje etažama
    prostorija_controller : ProstorijaController
        Kontroler za upravljanje prostorijama
    zid_controller : ZidController
        Kontroler za upravljanje zidovima
    stambena_jedinica_controller : StambenaJedinicaController, optional
        Kontroler za upravljanje stambenim jedinicama
    """
    st.header("Upravljanje etažama")
    
    # Dodavanje nove etaže
    with st.expander("Dodaj novu etažu", expanded=False):
        nova_etaza = forma_za_dodavanje_etaze(model)
      # Dodajemo upravljanje stambenim jedinicama ako je kontroler proslijeđen
    if stambena_jedinica_controller:
        st.markdown("### Upravljanje stambenim jedinicama")
        # Adding a container with border for visual separation
        with st.container(border=True):
            # Import stambena jedinica UI
            try:
                from .stambena_jedinica_ui import prikazi_manager_stambenih_jedinica
                prikazi_manager_stambenih_jedinica(model, stambena_jedinica_controller)
            except ImportError:
                st.warning("Modul za upravljanje stambenim jedinicama nije dostupan.")
      # Prikaz postojećih etaža
    if not model.etaze:
        st.info("Nema definiranih etaža. Dodajte novu etažu.")
        return
    
    # Provjeravamo imaju li etaže definirane prostorije
    prostorije_postoje = False
    for etaza in model.etaze:
        if model.dohvati_prostorije_za_etazu(etaza.id):
            prostorije_postoje = True
            break
    
    if not prostorije_postoje:
        st.warning("Nema definiranih prostorija ni na jednoj etaži. Koristite gumb 'Upravljaj prostorijama' pored etaže za dodavanje prostorija.")
    
    st.subheader("Postojeće etaže")
    
    # Sort floors by floor number for consistent display
    sorted_etaze = sorted(model.etaze, key=lambda e: e.redni_broj)
    
    # Create a clean visual layout for each floor
    for i, etaza in enumerate(sorted_etaze):
        with st.container():
            col1, col2, col3, col4 = st.columns([4, 1, 1, 2]) # Added a column for room management
            
            with col1:
                st.markdown(f"### Etaža {etaza.redni_broj}: {etaza.naziv}")
                st.markdown(f"Visina etaže: **{etaza.visina_etaze:.2f} m**")
                
                # Prikaz informacije o stambenim jedinicama kroz model                # Debug: Check for housing units
                stambene_jedinice = model.dohvati_stambene_jedinice_za_etazu(etaza.id)
                
                # Debug information - temporarily visible
                st.caption(f"DEBUG: Etaza ID: {etaza.id}")
                st.caption(f"DEBUG: Broj stambenih jedinica pronađen: {len(stambene_jedinice) if stambene_jedinice else 0}")
                if stambene_jedinice:
                    st.caption(f"DEBUG: Nazivi: {[sj.naziv for sj in stambene_jedinice]}")
                
                if stambene_jedinice:
                    broj_stambenih_jedinica = len(stambene_jedinice)
                    st.markdown(f"Stambene jedinice: **{broj_stambenih_jedinica}**")
                else:
                    st.markdown("Stambene jedinice: **Nema definiranih**")
            
            with col2:
                if st.button("Uredi", key=f"edit_etaza_{etaza.id}", 
                             help="Uredi podatke o etaži"):
                    st.session_state[f"edit_etaza_open_{etaza.id}"] = True
                    st.rerun()
            
            with col3:
                if st.button("Obriši", key=f"delete_etaza_{etaza.id}", 
                           help="Obriši etažu i sve prostorije u njoj"):
                    # Show confirmation dialog
                    st.warning(f"Jeste li sigurni da želite obrisati etažu '{etaza.naziv}'? Sve prostorije u njoj će biti izgubljene.")
                    confirm_col1, confirm_col2 = st.columns(2)
                    with confirm_col1:
                        if st.button("Da, obriši", key=f"confirm_delete_etaza_{etaza.id}"):
                            if controller.ukloni_etazu(etaza.id):
                                st.success(f"Etaža {etaza.naziv} uspješno uklonjena!")
                                st.rerun()
                            else:
                                st.error("Greška prilikom brisanja etaže.")
                    with confirm_col2:
                        if st.button("Odustani", key=f"cancel_delete_etaza_{etaza.id}"):
                            st.rerun()
            
            with col4: # New column for "Upravljaj prostorijama" button                
                # Check if already managing rooms for this etaza
                is_managing_rooms = st.session_state.get('selected_etaza_for_rooms') == etaza.id
                button_label = "Zatvori upravljanje" if is_managing_rooms else "Upravljaj prostorijama"
                
                if st.button(button_label, key=f"manage_rooms_etaza_{etaza.id}"):
                    if is_managing_rooms:
                        # Close room management
                        if 'selected_etaza_for_rooms' in st.session_state:
                            del st.session_state['selected_etaza_for_rooms']
                    else:
                        # Explicitly refresh model data before opening room management
                        model._ucitaj_iz_session_state()
                        # Open room management
                        st.session_state['selected_etaza_for_rooms'] = etaza.id
                        # Clear other potentially conflicting states
                        if 'selected_room_for_walls' in st.session_state:
                            del st.session_state['selected_room_for_walls']
                    st.rerun()
                
                # Add a button for managing stambene jedinice within this floor
                if stambena_jedinica_controller:
                    is_managing_units = st.session_state.get('selected_etaza_for_units') == etaza.id
                    units_button_label = "Zatvori stambene" if is_managing_units else "Upravljaj stambenim jedinicama"
                    
                    if st.button(units_button_label, key=f"manage_units_etaza_{etaza.id}"):
                        if is_managing_units:
                            # Close residential units management
                            if 'selected_etaza_for_units' in st.session_state:
                                del st.session_state['selected_etaza_for_units']
                        else:
                            # Explicitly refresh model data before opening units management
                            model._ucitaj_iz_session_state()
                            # Open units management
                            st.session_state['selected_etaza_for_units'] = etaza.id
                        st.rerun()
                
                # Dodatna informacija za korisnika
                if not is_managing_rooms:
                    st.info("Kliknite na 'Upravljaj prostorijama' za prikaz i uređivanje prostorija na ovoj etaži.")# Prikaži formu za uređivanje ako je otvorena
            if st.session_state.get(f"edit_etaza_open_{etaza.id}", False):
                with st.container():
                    st.markdown("---")
                    # Koristimo postojeću funkciju za uređivanje etaže
                    editing_result = forma_za_uredivanje_etaze(etaza, model, None)
                    
                    # Ako je promjena spremljena ili odbačena, zatvaramo formu
                    if editing_result is not None:  # True (spremi) ili False (odustani)
                        st.session_state[f"edit_etaza_open_{etaza.id}"] = False
                        st.rerun()
                        
                    st.markdown("---")
              # Display room manager if this etaza is selected for room management
            if st.session_state.get('selected_etaza_for_rooms') == etaza.id:
                with st.container():
                    st.markdown("---")
                    st.markdown("### Upravljanje prostorijama na etaži: " + etaza.naziv)
                      # Import the room management UI directly
                    from ..ui.prostorija_ui import prikazi_manager_prostorija
                    
                    # Call the function that displays room management UI
                    prikazi_manager_prostorija(model, etaza.id, prostorija_controller, zid_controller)
                    
                    st.markdown("---")
            
            # Display residential units manager if this etaza is selected for units management
            if stambena_jedinica_controller and st.session_state.get('selected_etaza_for_units') == etaza.id:
                with st.container():
                    st.markdown("---")
                    st.markdown("### Upravljanje stambenim jedinicama na etaži: " + etaza.naziv)
                    
                    # Import the residential units management UI
                    try:
                        from .stambena_jedinica_ui import prikazi_manager_stambenih_jedinica_za_etazu
                        prikazi_manager_stambenih_jedinica_za_etazu(model, etaza.id, stambena_jedinica_controller)
                    except ImportError:
                        st.error("Modul za upravljanje stambenim jedinicama nije dostupan.")
                    
                    st.markdown("---")

            # Separator između etaža
            if i < len(model.etaze) - 1:
                st.markdown("---")

def prikazi_postavke_etaze(etaza, controller):
    """
    Prikazuje postavke odabrane etaže.
    
    Parameters:
    -----------
    etaza : Etaza
        Etaža čije postavke se prikazuju
    controller : EtazaController
        Kontroler za upravljanje etažama
    """
    st.header(f"Postavke etaže: {etaza.naziv}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Redni broj", etaza.redni_broj)
    
    with col2:
        st.metric("Visina etaže", f"{etaza.visina_etaze} m")
    
    # Omogućujemo promjenu visine etaže
    nova_visina = st.slider(
        "Promijeni visinu etaže [m]:", 
        min_value=2.0, 
        max_value=5.0, 
        value=float(etaza.visina_etaze), 
        step=0.1,
        key=f"visina_etaze_slider_{etaza.id}"
    )
    
    if nova_visina != etaza.visina_etaze:
        if st.button("Primijeni novu visinu etaže"):
            if controller.uredi_etazu(etaza.id, visina_etaze=nova_visina):
                st.success(f"Visina etaže promijenjena na {nova_visina} m.")
                st.rerun()
            else:
                st.error("Greška prilikom promjene visine etaže.")
