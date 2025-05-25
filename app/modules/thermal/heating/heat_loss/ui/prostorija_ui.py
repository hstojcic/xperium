"""
Modul koji sadrži funkcije za prikaz i upravljanje prostorijama u UI-u.
"""

import streamlit as st
from ..models.elementi.constants import TIPOVI_PROSTORIJA
from ..utils.validators import validate_number
# Direktni uvoz zamijenjen odgođenim - koristit ćemo ga unutar funkcije gdje je potreban

def prikaz_prostorija_izbornika(model, etaza, on_prostorija_selected=None):
    """
    Prikazuje izbornik za odabir prostorije u odabranoj etaži.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model u kojem se nalaze prostorije
    etaza : Etaza
        Etaža za koju se prikazuju prostorije
    on_prostorija_selected : function
        Funkcija koja se poziva kad se odabere prostorija
    """
    prostorije = model.dohvati_prostorije_za_etazu(etaza.id)
    
    if not prostorije:
        st.info(f"Nema definiranih prostorija u etaži '{etaza.naziv}'.")
        return None
    
    st.subheader("Odabir prostorije")    # Sort rooms by room number, then by name for consistent display
    sortirane_prostorije = sorted(prostorije, key=lambda p: (p.broj_prostorije or 0, p.naziv))
    opcije = [f"{p.get_formatted_broj_prostorije()}. {p.naziv} ({p.tip})" if p.broj_prostorije else f"{p.naziv} ({p.tip})" for p in sortirane_prostorije]
    
    # Dodaj prostoriju u session state ako ne postoji
    key = f"odabrana_prostorija_index_{etaza.id}"
    if key not in st.session_state:
        st.session_state[key] = 0
    
    if len(opcije) <= st.session_state[key]:
        st.session_state[key] = 0
    
    selected_index = st.selectbox(
        "Prostorija:",
        range(len(opcije)), 
        format_func=lambda i: opcije[i],
        key=key
    )
    
    odabrana_prostorija = prostorije[selected_index]
    
    if on_prostorija_selected:
        on_prostorija_selected(odabrana_prostorija)
        
    return odabrana_prostorija

def forma_za_dodavanje_prostorije(model, etaza, callback_nakon_dodavanja=None):
    """
    Prikazuje formu za dodavanje nove prostorije.
    Omogućuje prvo odabir tipa prostorije, a zatim uređivanje detalja.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model u koji se dodaje prostorija
    etaza : Etaza
        Etaža u koju se dodaje prostorija
    callback_nakon_dodavanja : function
        Funkcija koja se poziva nakon dodavanja prostorije
    """
    # Koristimo container umjesto expandera za izbjegavanje problema s ugniježđenim expanderima
    with st.container():
        st.subheader("Dodaj novu prostoriju")
        
        # Inicijaliziraj session state
        if "odabrani_tip_prostorije" not in st.session_state:
            st.session_state.odabrani_tip_prostorije = None
        
        # Korak 1: Odabir tipa prostorije ako tip nije odabran
        if st.session_state.odabrani_tip_prostorije is None:
            tipovi_prostorija = list(TIPOVI_PROSTORIJA.keys())
            st.write("**1. korak:** Odaberite tip prostorije koji želite dodati")
            
            # Prikazujemo tipove prostorija u mreži
            cols = st.columns(3)
            for i, tip in enumerate(tipovi_prostorija):
                col_idx = i % 3
                with cols[col_idx]:
                    if st.button(f"{tip}", key=f"btn_tip_{tip}", 
                               help=f"Temp: {TIPOVI_PROSTORIJA[tip].get('temp')}°C, Izmjene: {TIPOVI_PROSTORIJA[tip].get('izmjene')} 1/h"):
                        st.session_state.odabrani_tip_prostorije = tip
                        st.rerun()
            
            return None
        
        # Korak 2: Unos detalja prostorije
        else:
            odabrani_tip = st.session_state.odabrani_tip_prostorije
              # Dohvati standardne postavke za odabrani tip
            default_temp = float(TIPOVI_PROSTORIJA[odabrani_tip].get("temp", 20))
            default_izmjene = float(TIPOVI_PROSTORIJA[odabrani_tip].get("izmjene", 0.5))
            default_grijana = TIPOVI_PROSTORIJA[odabrani_tip].get("grijana", True)
            
            st.write(f"**2. korak:** Uređivanje podataka o prostoriji tipa **{odabrani_tip}**")
            
            with st.form("forma_nova_prostorija"):
                col1, col2 = st.columns(2)
                with col1:
                    naziv = st.text_input("Naziv prostorije", odabrani_tip)  # Defaultno koristimo ime tipa
                    oznaka = st.text_input("Oznaka prostorije", "")  # Polje za oznaku prostorije
                    povrsina = st.number_input("Površina [m²]", min_value=1.0, value=20.0, step=1.0)
                    koristi_zadanu_visinu = st.checkbox("Koristi visinu etaže", value=True)
                    if not koristi_zadanu_visinu:
                        visina = st.number_input("Visina prostorije [m]", min_value=2.0, max_value=6.0, value=etaza.visina_etaze, step=0.1)
                    else:
                        visina = None
                
                with col2:
                    # Stambena jedinica sekcija
                    st.markdown("**Stambena jedinica**")
                    # Dohvati stambene jedinice za trenutnu etažu
                    stambene_jedinice = model.dohvati_stambene_jedinice_za_etazu(etaza.id)
                    
                    if stambene_jedinice:
                        opcije_stambenih_jedinica = {
                            "": "Bez stambene jedinice"
                        }
                        opcije_stambenih_jedinica.update({
                            s.id: f"{s.naziv} ({s.tip})" for s in stambene_jedinice
                        })
                        
                        odabrana_stambena_jedinica = st.selectbox(
                            "Dodjeli stambenu jedinicu",
                            options=list(opcije_stambenih_jedinica.keys()),
                            format_func=lambda x: opcije_stambenih_jedinica[x],
                            help="Odaberite stambenu jedinicu kojoj pripada ova prostorija"
                        )
                    else:
                        st.info("Nema definiranih stambenih jedinica na ovoj etaži.")
                        odabrana_stambena_jedinica = ""
                
                # Opcija za negrijanu prostoriju
                grijana = st.checkbox("Negrijana prostorija", value=(not default_grijana), key="negrijana_nova_prostorija")  # Obrnuta logika - kvačicom označavamo negrijane
                
                # Parametri za temperaturu i izmjene zraka
                if grijana:  # Ako je označeno kao negrijana
                    st.info("Za negrijane prostorije, temperatura će biti izračunata na temelju ovojnice i susjednih prostora.")
                    
                    # Za negrijane prostorije, koristimo defaultnu temperaturu bez prikaza polja
                    temp_unutarnja = default_temp
                    
                    # Iako je prostorija negrijana, i dalje ima izmjene zraka
                    izmjene_zraka = st.number_input(
                        "Izmjene zraka [1/h]", 
                        min_value=0.0, 
                        max_value=5.0, 
                        value=default_izmjene, 
                        step=0.1,
                        key="izmjene_zraka_negrijana_nova"
                    )
                else:  # Za grijane prostorije
                    # Za grijane prostorije prikazujemo polja za temperaturu i izmjene zraka
                    with col2:
                        temp_unutarnja = st.number_input(
                            "Projektna temperatura [°C]", 
                            min_value=5.0, 
                            max_value=30.0, 
                            value=default_temp, 
                            step=1.0,
                            key="temp_unutarnja_grijana_nova"
                        )
                        izmjene_zraka = st.number_input(
                            "Izmjene zraka [1/h]", 
                            min_value=0.1, 
                            max_value=5.0, 
                            value=default_izmjene, 
                            step=0.1,
                            key="izmjene_zraka_grijana_nova"
                        )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submitted = st.form_submit_button("Dodaj prostoriju")
                with col_btn2:
                    cancel_button = st.form_submit_button("Odustani")
                
                if cancel_button:
                    st.session_state.odabrani_tip_prostorije = None
                    st.rerun()
                
                if submitted:
                    nova_prostorija = model.dodaj_prostoriju(
                        etaza_id=etaza.id, 
                        naziv=naziv, 
                        tip=odabrani_tip, 
                        povrsina=povrsina
                    )
                    if nova_prostorija:
                        nova_prostorija.koristi_zadanu_visinu = koristi_zadanu_visinu
                        if not koristi_zadanu_visinu and visina:
                            nova_prostorija.visina = visina
                        
                        # Postavljamo dodatne atribute
                        nova_prostorija.oznaka = oznaka  # Dodaj oznaku prostorije
                        nova_prostorija.temp_unutarnja = temp_unutarnja
                        nova_prostorija.izmjene_zraka = izmjene_zraka
                        nova_prostorija.grijana = not grijana  # Negacija jer u UI označavamo negrijanu, a atribut je "grijana"
                        
                        # Postavi stambenu jedinicu ako je odabrana
                        if odabrana_stambena_jedinica:
                            nova_prostorija.stambena_jedinica_id = odabrana_stambena_jedinica
                            # Dodaj prostoriju u stambenu jedinicu
                            stambena_jedinica = model.dohvati_stambenu_jedinicu(odabrana_stambena_jedinica)
                            if stambena_jedinica:
                                stambena_jedinica.dodaj_prostoriju(nova_prostorija.id)
                        
                        # Spremanje promjena u model
                        model._spremi_u_session_state()
                        st.success(f"Prostorija '{naziv}' je uspješno dodana!")
                        st.session_state.odabrani_tip_prostorije = None  # Resetiramo odabir tipa
                        
                        if callback_nakon_dodavanja:
                            callback_nakon_dodavanja(nova_prostorija)
                        
                        # Rerun the page to close the form
                        st.rerun()
                        
                        return nova_prostorija
                    else:
                        st.error("Greška prilikom dodavanja prostorije!")
    return None

def forma_za_uredivanje_prostorije(prostorija, model, callback_nakon_uredivanja=None):
    """
    Prikazuje formu za uređivanje postojeće prostorije.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija koja se uređuje
    model : MultiRoomModel
        Model u kojem se nalazi prostorija
    callback_nakon_uredivanja : function
        Funkcija koja se poziva nakon uređivanja prostorije
    """
    etaza = model.dohvati_etazu(prostorija.etaza_id)
    
    # Dohvaćamo informaciju je li prostorija grijana (podržava starije modele gdje atribut možda ne postoji)
    grijana = getattr(prostorija, 'grijana', True)
    
    # Koristimo container umjesto expander kako bi izbjegli probleme s ugniježđenim expanderima
    with st.container():
        with st.form("forma_uredi_prostoriju"):
            st.subheader("Uredi prostoriju")
            naziv = st.text_input("Naziv prostorije", prostorija.naziv)
            
            tipovi_prostorija = list(TIPOVI_PROSTORIJA.keys())
            try:
                tip_index = tipovi_prostorija.index(prostorija.tip)
            except ValueError:
                tip_index = 0
            
            tip = st.selectbox("Tip prostorije", tipovi_prostorija, index=tip_index)
            povrsina = st.number_input("Površina [m²]", min_value=1.0, value=prostorija.povrsina, step=1.0)
            
            col1, col2 = st.columns(2)
            with col1:
                koristi_zadanu_visinu = st.checkbox("Koristi visinu etaže", value=prostorija.koristi_zadanu_visinu, key=f"koristi_visinu_etaze_edit_{prostorija.id}")
            
            with col2:
                # Stambena jedinica sekcija
                st.markdown("**Stambena jedinica**")
                # Dohvati stambene jedinice za trenutnu etažu
                stambene_jedinice = model.dohvati_stambene_jedinice_za_etazu(etaza.id)
                
                if stambene_jedinice:
                    opcije_stambenih_jedinica = {
                        "": "Bez stambene jedinice"
                    }
                    opcije_stambenih_jedinica.update({
                        s.id: f"{s.naziv} ({s.tip})" for s in stambene_jedinice
                    })
                    
                    trenutna_stambena_jedinica = getattr(prostorija, 'stambena_jedinica_id', "") or ""
                    default_index = 0
                    if trenutna_stambena_jedinica in opcije_stambenih_jedinica:
                        default_index = list(opcije_stambenih_jedinica.keys()).index(trenutna_stambena_jedinica)
                    
                    odabrana_stambena_jedinica = st.selectbox(
                        "Stambena jedinica",
                        options=list(opcije_stambenih_jedinica.keys()),
                        format_func=lambda x: opcije_stambenih_jedinica[x],
                        index=default_index,
                        key=f"stambena_jedinica_edit_{prostorija.id}",
                        help="Promjeni stambenu jedinicu kojoj pripada ova prostorija"
                    )
                else:
                    st.info("Nema definiranih stambenih jedinica na ovoj etaži.")
                    odabrana_stambena_jedinica = ""
            
            visina_input_widget_val = None # Varijabla za vrijednost iz number_input za visinu
            if not koristi_zadanu_visinu:
                visina_value = prostorija.visina if prostorija.visina is not None else etaza.visina_etaze if etaza else 2.5
                # 'visina' varijabla će držati vrijednost iz ovog inputa
                visina_input_widget_val = st.number_input("Visina prostorije [m]", min_value=2.0, max_value=6.0, value=visina_value, step=0.1, key=f"visina_prostorije_edit_{prostorija.id}")
            # Ako koristi_zadanu_visinu ostane True, visina_input_widget_val ostaje None
            
            # Dodana opcija za negrijanu prostoriju
            init_grijana = getattr(prostorija, 'grijana', True)
            negrijana_checkbox_val = st.checkbox("Negrijana prostorija", value=not init_grijana, key=f"negrijana_edit_chbx_{prostorija.id}")

            temp_unutarnja_input_val = None  # Vrijednost iz number_input ako je prostorija grijana
            izmjene_zraka_input_val = None # Vrijednost iz number_input za izmjene zraka
            
            if negrijana_checkbox_val:
                st.info("Za negrijane prostorije, projektna temperatura se ne unosi. Izračunat će se na temelju ovojnice i susjednih prostora.")
                izracunata_temp = getattr(prostorija, 'izracunata_temp_negrijane', None)
                if izracunata_temp is not None:
                    st.write(f"Trenutna procijenjena temperatura: **{izracunata_temp:.1f}°C** (konačna vrijednost ovisi o definiranoj ovojnici).")
                else:
                    st.write("Temperatura će biti izračunata nakon što se definiraju svi elementi ovojnice prostorije (zidovi, pod, strop) i svojstva susjednih prostora.")
                
                default_izmjene_negrijana = float(prostorija.izmjene_zraka) if hasattr(prostorija, 'izmjene_zraka') and prostorija.izmjene_zraka is not None else 0.5
                izmjene_zraka_input_val = st.number_input(
                    "Izmjene zraka [1/h]", 
                    min_value=0.0, 
                    max_value=5.0, 
                    value=default_izmjene_negrijana, 
                    step=0.1,
                    key=f"izmjene_zraka_negrijana_edit_{prostorija.id}"
                )
            else: # Za grijane prostorije
                col1_temp_air, col2_temp_air = st.columns(2)
                with col1_temp_air:
                    default_temp_grijana = float(prostorija.temp_unutarnja) if hasattr(prostorija, 'temp_unutarnja') and prostorija.temp_unutarnja is not None else 20.0
                    temp_unutarnja_input_val = st.number_input(
                        "Unutarnja temperatura [°C]", 
                        min_value=5.0, 
                        max_value=30.0, 
                        value=default_temp_grijana, 
                        step=1.0,
                        key=f"temp_unutarnja_grijana_edit_{prostorija.id}"
                    )
                with col2_temp_air:
                    default_izmjene_grijana = float(prostorija.izmjene_zraka) if hasattr(prostorija, 'izmjene_zra') and prostorija.izmjene_zraka is not None else 0.5
                    izmjene_zraka_input_val = st.number_input(
                        "Izmjene zraka [1/h]", 
                        min_value=0.1, 
                        max_value=5.0, 
                        value=default_izmjene_grijana, 
                        step=0.1,
                        key=f"izmjene_zraka_grijana_edit_{prostorija.id}"
                    )            # Gumbi za form
            col_form_btn1, col_form_btn2 = st.columns(2) # Preimenovane varijable da se izbjegne sukob s col1, col2 gore
            with col_form_btn1:
                submitted = st.form_submit_button("Spremi promjene")
            with col_form_btn2:
                delete_button = st.form_submit_button("Obriši prostoriju", type="secondary")
        
        if submitted:
                # Ažuriranje podataka prostorije
                prostorija.naziv = naziv
                prostorija.azuriraj_tip_prostorije(tip) # Ovo može postaviti defaultne vrijednosti za grijana i temp_unutarnja
                prostorija.povrsina = validate_number(povrsina, min_value=1.0, default=20.0)
                prostorija.koristi_zadanu_visinu = koristi_zadanu_visinu
                
                if not koristi_zadanu_visinu and visina_input_widget_val is not None:
                    prostorija.visina = validate_number(visina_input_widget_val, min_value=2.0, max_value=6.0, default=etaza.visina_etaze if etaza else 2.5)
                else:
                    prostorija.visina = None # Koristit će se visina etaže
                
                # Eksplicitno postavljanje 'grijana' statusa NAKON azuriraj_tip_prostorije, da bi checkbox imao prednost
                prostorija.grijana = not negrijana_checkbox_val

                if prostorija.grijana:
                    # Ako je prostorija grijana, postavi temperaturu iz input polja (ako je bilo vidljivo)
                    if temp_unutarnja_input_val is not None:
                        prostorija.temp_unutarnja = validate_number(temp_unutarnja_input_val, min_value=5.0, max_value=30.0, default=20.0)
                    # Ako temp_unutarnja_input_val is None, znači da polje nije bilo prikazano;
                    # u tom slučaju, temp_unutarnja zadržava vrijednost koju je postavio azuriraj_tip_prostorije
                    # ili prethodnu vrijednost ako tip nije mijenjan.
                else:
                    # Ako je prostorija negrijana, temp_unutarnja se NE postavlja iz forme.
                    # Njena vrijednost je određena izračunom (izracunata_temp_negrijane) ili
                    # defaultnom vrijednošću za negrijane prostore (koju je možda postavio azuriraj_tip_prostorije).
                    # Osiguravamo da se ne prepiše vrijednošću iz skrivenog inputa za grijane prostorije.
                    pass # Namjerno ne diramo prostorija.temp_unutarnja; oslanjamo se na logiku modela ili tipa prostorije.
                
                # Izmjene zraka se uvijek postavljaju iz odgovarajućeg vidljivog input polja
                if izmjene_zraka_input_val is not None:
                    prostorija.izmjene_zraka = validate_number(izmjene_zraka_input_val, min_value=0.0, max_value=5.0, default=0.5)
                
                # Upravljanje stambenom jedinicom
                trenutna_stambena_jedinica_id = getattr(prostorija, 'stambena_jedinica_id', None)
                
                if trenutna_stambena_jedinica_id != odabrana_stambena_jedinica:
                    # Ukloni iz trenutne stambene jedinice
                    if trenutna_stambena_jedinica_id:
                        trenutna_stambena_jedinica = model.dohvati_stambenu_jedinicu(trenutna_stambena_jedinica_id)
                        if trenutna_stambena_jedinica:
                            trenutna_stambena_jedinica.ukloni_prostoriju(prostorija.id)
                      # Dodaj u novu stambenu jedinicu
                    if odabrana_stambena_jedinica:
                        nova_stambena_jedinica = model.dohvati_stambenu_jedinicu(odabrana_stambena_jedinica)
                        if nova_stambena_jedinica:
                            nova_stambena_jedinica.dodaj_prostoriju(prostorija.id)
                            prostorija.stambena_jedinica_id = odabrana_stambena_jedinica
                    else:
                        prostorija.stambena_jedinica_id = None
                
                # Spremanje promjena u model
                model._spremi_u_session_state()
                
                st.success(f"Prostorija '{naziv}' je uspješno ažurirana!")
                
                if callback_nakon_uredivanja:
                    callback_nakon_uredivanja(prostorija)
                
                return prostorija
        
        if delete_button:
                # Brisanje prostorije
                model.ukloni_prostoriju(prostorija.id)
                st.success(f"Prostorija '{prostorija.naziv}' je uspješno obrisana!")
                
                if callback_nakon_uredivanja:
                    callback_nakon_uredivanja(None)
                
                return None
    
    return None

def prikaz_detalja_prostorije(prostorija, model):
    """
    Prikazuje detalje o prostoriji.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija koja se prikazuje    model : MultiRoomModel
        Model u kojem se nalazi prostorija
    """
    etaza = model.dohvati_etazu(prostorija.etaza_id)
    grijana = getattr(prostorija, 'grijana', True)  # Dohvaćamo atribut sa zadanom vrijednosti
    
    room_title = f"{prostorija.get_formatted_broj_prostorije()}. {prostorija.naziv}" if prostorija.broj_prostorije else prostorija.naziv
    st.subheader(f"Detalji prostorije: {room_title}")
    
    # Reorganized layout: 2 rows, 4 columns
    # First row: Room number, Name, Type, Area
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if prostorija.broj_prostorije:
            st.metric("Broj prostorije", prostorija.get_formatted_broj_prostorije())
        else:
            st.metric("Broj prostorije", "Nije dodjeljen")
    with col2:
        st.metric("Naziv", prostorija.naziv)
    with col3:
        st.metric("Tip", prostorija.tip)
    with col4:
        st.metric("Površina", f"{prostorija.povrsina:.1f} m²")
      # Second row: Status, Temperature, Air changes, Height  
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        status = "Grijana" if grijana else "Negrijana"
        st.metric("Status grijanja", status)
    with col2:
        # Ovisno o tome je li prostorija grijana, prikazujemo unutarnju temperaturu na različit način
        if grijana:
            st.metric("Unutarnja temperatura", f"{prostorija.temp_unutarnja:.1f} °C")
        else:
            izracunata_temp = getattr(prostorija, 'izracunata_temp_negrijane', None)
            if izracunata_temp is not None:
                st.metric("Izračunata temperatura", f"{izracunata_temp:.1f} °C")
            else:
                st.metric("Temperatura", "Čeka izračun", delta="?")
    with col3:
        st.metric("Izmjene zraka", f"{prostorija.izmjene_zraka:.1f} h⁻¹")
    with col4:
        visina = prostorija.get_actual_height(etaza)
        st.metric("Visina", f"{visina:.2f} m")
    
    # Third row: Residential unit assignment
    stambena_jedinica_id = getattr(prostorija, 'stambena_jedinica_id', None)
    if stambena_jedinica_id:
        stambena_jedinica = model.dohvati_stambenu_jedinicu(stambena_jedinica_id)
        if stambena_jedinica:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stambena jedinica", stambena_jedinica.naziv)
            with col2:
                st.metric("Tip jedinice", stambena_jedinica.tip)
            with col3:
                st.metric("Ukupna površina jedinice", f"{stambena_jedinica.ukupna_povrsina:.1f} m²")
            with col4:
                broj_prostorija = len(stambena_jedinica.prostorije_ids)
                st.metric("Broj prostorija u jedinici", broj_prostorija)
    else:
        st.info("Prostorija nije dodijeljena nijednoj stambenoj jedinici.")
        # Ako je prostorija negrijana, dodajemo još informaciju o izračunu temperature
    if not grijana:
        izracunata_temp = getattr(prostorija, 'izracunata_temp_negrijane', None)
        if izracunata_temp is not None:
            st.info(f"Izračunata temperatura negrijane prostorije: {izracunata_temp:.1f}°C (na osnovi ovojnice i susjednih prostora)")
        else:
            st.info("Temperatura negrijane prostorije bit će izračunata nakon što se definiraju svi elementi ovojnice prostorije (zidovi, pod, strop) i svojstva susjednih prostora.")

def prikazi_manager_prostorija(model, etaza_id, prostorija_controller, zid_controller):
    """
    Prikazuje sučelje za upravljanje prostorijama na etaži (dodavanje, uređivanje, brisanje).
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s prostorijama
    etaza_id : str
        ID etaže za koju se prikazuju prostorije
    prostorija_controller : ProstorijaController
        Kontroler za upravljanje prostorijama
    zid_controller : ZidController
        Kontroler za upravljanje zidovima
    """
    etaza = model.dohvati_etazu(etaza_id)
    if not etaza:
        st.error("Etaža nije pronađena.")
        return
    
    # Dodavanje nove prostorije
    with st.expander("Dodaj novu prostoriju", expanded=False):
        forma_za_dodavanje_prostorije(model, etaza)
    
    # Prikaz postojećih prostorija
    prostorije = model.dohvati_prostorije_za_etazu(etaza_id)
    
    if not prostorije:
        st.info(f"Nema definiranih prostorija na etaži {etaza.naziv}. Dodajte novu prostoriju.")
        return
    
    st.subheader(f"Prostorije na etaži: {etaza.naziv}")
      # Sort rooms by room number, then by name for consistent display
    prostorije = sorted(prostorije, key=lambda p: (p.broj_prostorije or 0, p.naziv))
      # Add some styling for the room cards
    st.markdown("""
    <style>
    .room-card {
        border: 1px solid #f0f2f6;
        border-radius: 5px;
        padding: 10px;
        margin-bottom: 10px;
        background-color: #f8f9fa;
    }
    .room-title {
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Display each room in a clean, card-like format
    for i, prostorija in enumerate(prostorije):
        with st.container():
            st.markdown(f"<div class='room-card'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                room_title = f"{prostorija.get_formatted_broj_prostorije()}. {prostorija.naziv}" if prostorija.broj_prostorije else prostorija.naziv
                st.markdown(f"<div class='room-title'>{room_title}</div>", unsafe_allow_html=True)
                
                # Basic room info
                room_info = f"Tip: **{prostorija.tip}** | Površina: **{prostorija.povrsina:.1f} m²**"
                
                # Add residential unit info if assigned
                stambena_jedinica_id = getattr(prostorija, 'stambena_jedinica_id', None)
                if stambena_jedinica_id:
                    stambena_jedinica = model.dohvati_stambenu_jedinicu(stambena_jedinica_id)
                    if stambena_jedinica:
                        room_info += f" | SJ: **{stambena_jedinica.naziv}**"
                    else:
                        room_info += " | SJ: **Nepoznata**"
                else:
                    room_info += " | SJ: **Nedodijeljena**"
                
                st.markdown(room_info)
            
            with col2:
                # Toggle details
                show_details_key = f"show_details_prostorija_{prostorija.id}"
                if st.button("Detalji", key=f"details_btn_{prostorija.id}", 
                            help="Prikaži detaljne informacije o prostoriji"):
                    st.session_state[show_details_key] = not st.session_state.get(show_details_key, False)
                    st.rerun()
            
            with col3:
                # Toggle edit form
                edit_key = f"edit_prostorija_open_{prostorija.id}"
                if st.button("Uredi", key=f"edit_btn_{prostorija.id}", 
                            help="Uredi podatke prostorije"):
                    st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                    st.rerun()
            
            # Management buttons in a nicer layout
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Upravljaj zidovima", key=f"walls_btn_{prostorija.id}", 
                           help="Definiraj zidove, prozore i vrata"):
                    st.session_state["selected_room_for_walls"] = prostorija.id
                    st.rerun()
            
            with col2:
                # Empty column for spacing
                pass
            
            with col3:
                delete_btn = st.button("Obriši prostoriju", key=f"delete_btn_{prostorija.id}", 
                                     help="Trajno ukloni prostoriju")
                if delete_btn:
                    # Confirmation dialog with better styling
                    st.warning(f"⚠️ Jeste li sigurni da želite obrisati prostoriju '{prostorija.naziv}'?")
                    confirm_col1, confirm_col2 = st.columns(2)
                    with confirm_col1:
                        confirm_delete = st.button("Da, obriši", key=f"confirm_delete_{prostorija.id}")
                        if confirm_delete:
                            if prostorija_controller.ukloni_prostoriju(prostorija.id):
                                st.success(f"Prostorija '{prostorija.naziv}' uspješno uklonjena!")
                                st.rerun()
                            else:
                                st.error("Greška prilikom brisanja prostorije.")
                    with confirm_col2:
                        if st.button("Odustani", key=f"cancel_delete_{prostorija.id}"):
                            st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)  # Close the room-card div

        # Prikaži detalje ako je otvoreno
        if st.session_state.get(f"show_details_prostorija_{prostorija.id}", False):
            with st.container():
                st.markdown("---")
                prikaz_detalja_prostorije(prostorija, model)
                if st.button("Sakrij detalje", key=f"hide_details_{prostorija.id}"):
                    st.session_state[f"show_details_prostorija_{prostorija.id}"] = False
                    st.rerun()
                st.markdown("---")
        
        # Prikaži formu za uređivanje ako je otvorena
        if st.session_state.get(f"edit_prostorija_open_{prostorija.id}", False):
            with st.container():
                st.markdown("---")
                if forma_za_uredivanje_prostorije(prostorija, model):
                    st.session_state[f"edit_prostorija_open_{prostorija.id}"] = False
                    st.rerun()
                if st.button("Odustani", key=f"cancel_edit_prostorija_{prostorija.id}"):
                    st.session_state[f"edit_prostorija_open_{prostorija.id}"] = False
                    st.rerun()
                st.markdown("---")
        
        # Display wall UI if selected
        if st.session_state.get("selected_room_for_walls") == prostorija.id:
            with st.container():
                st.markdown("---")
                # Odgođeno učitavanje zid_ui modula kako bismo izbjegli cirkularni uvoz
                import importlib
                zid_ui_module = importlib.import_module("..ui.zid_ui", package="modules.thermal.heating.heat_loss.ui")
                prikazi_zidove_prostorije = zid_ui_module.prikazi_zidove_prostorije
                prikazi_zidove_prostorije(prostorija, model, zid_controller)
                if st.button("Zatvori upravljanje zidovima", key=f"close_walls_{prostorija.id}"):
                    del st.session_state["selected_room_for_walls"]
                    st.rerun()
                st.markdown("---")
        
        # Separator između prostorija
        st.markdown("---")

# Helper functions for displaying different aspects of a room
def prikazi_osnovne_podatke_prostorije(prostorija, model):
    """Prikazuje osnovne podatke o prostoriji."""
    st.subheader("Osnovni podaci")
    
    # Dohvaćamo informaciju je li prostorija grijana (podržava starije modele gdje atribut možda ne postoji)
    grijana = getattr(prostorija, 'grijana', True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Tip prostorije:** {prostorija.tip}")
        
        # Ovisno o tome je li prostorija grijana, prikazujemo temperaturu na različit način
        if grijana:
            st.markdown(f"**Projektna temperatura:** {prostorija.unutarnja_temp} °C")
        else:
            izracunata_temp = getattr(prostorija, 'izracunata_temp_negrijane', None)
            if izracunata_temp is not None:
                st.markdown(f"**Izračunata temperatura:** {izracunata_temp:.1f} °C")
            else:
                st.markdown(f"**Status temperature:** Čeka izračun")
                
    with col2:
        st.markdown(f"**Površina:** {prostorija.povrsina:.2f} m²")
        st.markdown(f"**Broj izmjena zraka:** {prostorija.izmjene_zraka:.1f} 1/h")
        # Dodajemo informaciju o statusu grijanja
        status = "Grijana" if grijana else "Negrijana"
        st.markdown(f"**Status grijanja:** {status}")
    
    # Ako je prostorija negrijana, dodajemo još informaciju o izračunu temperature
    if not grijana:
        izracunata_temp = getattr(prostorija, 'izracunata_temp_negrijane', None)
        if izracunata_temp is not None:
            st.info(f"Izračunata temperatura negrijane prostorije: {izracunata_temp:.1f}°C (na osnovi ovojnice i susjednih prostora)")
        else:
            st.info("Temperatura negrijane prostorije bit će izračunata nakon što se definiraju svi elementi ovojnice prostorije (zidovi, pod, strop) i svojstva susjednih prostora.")

def prikazi_dimenzije_prostorije(prostorija, model):
    """Prikazuje dimenzije prostorije."""
    st.subheader("Dimenzije")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**Duljina:** {prostorija.duljina:.2f} m")
    with col2:
        st.markdown(f"**Širina:** {prostorija.sirina:.2f} m")
    with col3:
        st.markdown(f"**Visina:** {prostorija.visina:.2f} m")
    st.markdown(f"**Volumen:** {prostorija.volumen:.2f} m³")

def prikazi_pod_i_strop_prostorije(prostorija, model):
    """Prikazuje podatke o podu i stropu prostorije."""
    st.subheader("Pod i strop")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Tip poda:** {prostorija.pod.get('tip', 'Nije definirano')}")
        st.markdown(f"**U-vrijednost poda:** {prostorija.pod.get('u_vrijednost', 0.0):.3f} W/m²K")
    with col2:
        st.markdown(f"**Tip stropa:** {prostorija.strop.get('tip', 'Nije definirano')}")
        st.markdown(f"**U-vrijednost stropa:** {prostorija.strop.get('u_vrijednost', 0.0):.3f} W/m²K")

def prikazi_prostorije_po_stambenim_jedinicama(model, etaza_id):
    """
    Prikazuje prostorije grupirane po stambenim jedinicama.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s prostorijama
    etaza_id : str
        ID etaže za koju se prikazuju prostorije
    """
    etaza = model.dohvati_etazu(etaza_id)
    if not etaza:
        st.error("Etaža nije pronađena.")
        return

    prostorije = model.dohvati_prostorije_za_etazu(etaza_id)
    if not prostorije:
        st.info(f"Nema definiranih prostorija na etaži {etaza.naziv}.")
        return

    # Grupiraj prostorije po stambenim jedinicama
    prostorije_po_jedinicama = {}
    prostorije_bez_jedinice = []
    
    for prostorija in prostorije:
        stambena_jedinica_id = getattr(prostorija, 'stambena_jedinica_id', None)
        if stambena_jedinica_id:
            if stambena_jedinica_id not in prostorije_po_jedinicama:
                prostorije_po_jedinicama[stambena_jedinica_id] = []
            prostorije_po_jedinicama[stambena_jedinica_id].append(prostorija)
        else:
            prostorije_bez_jedinice.append(prostorija)
    
    st.subheader(f"Prostorije na etaži: {etaza.naziv} (po stambenim jedinicama)")
    
    # Prikaži prostorije grupirane po stambenim jedinicama
    for stambena_jedinica_id, prostorije_u_jedinici in prostorije_po_jedinicama.items():
        stambena_jedinica = model.dohvati_stambenu_jedinicu(stambena_jedinica_id)
        if stambena_jedinica:
            with st.expander(f"🏠 {stambena_jedinica.naziv} ({stambena_jedinica.tip}) - {len(prostorije_u_jedinici)} prostorija/e", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Ukupna površina", f"{stambena_jedinica.ukupna_povrsina:.1f} m²")
                with col2:
                    broj_grijanih = sum(1 for p in prostorije_u_jedinici if getattr(p, 'grijana', True))
                    st.metric("Grijane prostorije", f"{broj_grijanih}/{len(prostorije_u_jedinici)}")
                with col3:
                    ukupna_povrsina_prostorija = sum(p.povrsina for p in prostorije_u_jedinici)
                    st.metric("Površina prostorija", f"{ukupna_povrsina_prostorija:.1f} m²")
                
                # Prikaži prostorije u ovoj stambenoj jedinici
                for prostorija in sorted(prostorije_u_jedinici, key=lambda p: (p.broj_prostorije or 0, p.naziv)):
                    room_title = f"{prostorija.get_formatted_broj_prostorije()}. {prostorija.naziv}" if prostorija.broj_prostorije else prostorija.naziv
                    grijana = getattr(prostorija, 'grijana', True)
                    status_icon = "🔥" if grijana else "❄️"
                    st.markdown(f"• {status_icon} **{room_title}** ({prostorija.tip}) - {prostorija.povrsina:.1f} m²")
    
    # Prikaži prostorije koje nisu dodijeljene nijednoj stambenoj jedinici
    if prostorije_bez_jedinice:
        with st.expander(f"📦 Nedodijeljene prostorije - {len(prostorije_bez_jedinice)} prostorija/e", expanded=True):
            st.warning("Ove prostorije nisu dodijeljene nijednoj stambenoj jedinici:")
            for prostorija in sorted(prostorije_bez_jedinice, key=lambda p: (p.broj_prostorije or 0, p.naziv)):
                room_title = f"{prostorija.get_formatted_broj_prostorije()}. {prostorija.naziv}" if prostorija.broj_prostorije else prostorija.naziv
                grijana = getattr(prostorija, 'grijana', True)
                status_icon = "🔥" if grijana else "❄️"
                st.markdown(f"• {status_icon} **{room_title}** ({prostorija.tip}) - {prostorija.povrsina:.1f} m²")
