"""
Komponente korisničkog sučelja za aplikaciju proračuna toplinskih gubitaka
s podrškom za više prostorija
"""

import streamlit as st
from .constants import TIPOVI_PROSTORIJA, DEFAULT_U_VALUES, ORIJENTACIJE, TEMP_FAKTORI
from .utils import prikazuje_upozorenje_o_povrsinama
from .multi_room import inicijaliziraj_model, Prostorija, SegmentZida
from .building_elements import inicijaliziraj_elemente
from .building_elements_ui import prikazi_vanjski_zid_s_elementima, prikazi_unutarnji_zid_s_elementima

# Definicija ključa za session state za ovaj modul, ako već nije definirano globalno
SESSION_KEY_MULTI_ROOM = "heat_loss_model"  # Može se centralizirati

def prikazi_postavke_etaze(model):
    """
    Prikazuje postavke za etažu (zadana visina)
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s više prostorija
    """
    st.markdown("<h3 class='subsection-header'>Postavke etaže</h3>", unsafe_allow_html=True)
    
    # Use a truly unique key by combining multiple elements and session state
    # This ensures the key is unique even if the same model is accessed multiple times
    if "etaza_key_counter" not in st.session_state:
        st.session_state.etaza_key_counter = 0
    
    # Increment counter to ensure uniqueness across re-renders
    key = f"etaza_visina_{st.session_state.etaza_key_counter}"
    st.session_state.etaza_key_counter += 1

    # Determine the current default height to display
    # If there are etaze, use the height of the first one as a reference
    # Otherwise, use a fallback default (e.g., 2.8)
    current_default_height = model.etaze[0].visina_etaze if model.etaze else 2.8
    
    zadana_visina = st.number_input(
        "Zadana visina etaže [m]:", 
        min_value=2.0, 
        max_value=6.0, 
        value=current_default_height, # Use the determined current default height
        step=0.1,
        key=key,
        help="Ova visina će se koristiti za sve prostorije koje nemaju posebno definiranu visinu"
    )
    
    # This part of the logic might need refinement.
    # If the intention is to change the height of a *specific* etaza,
    # then that etaza needs to be identified and updated.
    # If it's to change a global default for *new* etaze, the model needs to store this.
    # For now, if there's at least one etaza, we'll update the first one as an example.
    if model.etaze and zadana_visina != model.etaze[0].visina_etaze:
        # This is a placeholder for the actual logic to update the intended etaza(s)
        # For example, update the first etaza:
        model.etaze[0].visina_etaze = zadana_visina
        model._spremi_u_session_state() # Assuming this method exists and saves the model
        st.success(f"Zadana visina prve etaže postavljena na {zadana_visina} m")
    elif not model.etaze:
        st.info("Dodajte etažu kako biste postavili njenu visinu.")

def prikazi_manager_etaza(model):
    """
    Prikazuje sučelje za upravljanje etažama
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s više prostorija
    """
    st.markdown("<h3 class='subsection-header'>Upravljanje etažama</h3>", unsafe_allow_html=True)
    
    # Prikaz postojećih etaža
    if not model.etaze:
        st.info("Nema definiranih etaža. Dodajte prvu etažu.")
    else:
        # Sortiramo etaže prema rednom broju
        etaze_sortirano = sorted(model.etaze, key=lambda e: e.redni_broj)
        
        for etaza in etaze_sortirano:
            # Dohvat broja prostorija na etaži
            prostorije_na_etazi = model.dohvati_prostorije_za_etazu(etaza.id)
            broj_prostorija = len(prostorije_na_etazi)
            
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"**{etaza.naziv}** ({broj_prostorija} prostorija)")
                
                with col2:
                    st.markdown(f"Visina: {etaza.visina_etaze} m")
                
                with col3:
                    # Omogućujemo brisanje samo ako nema prostorija na etaži
                    if broj_prostorija == 0:
                        if st.button("Obriši", key=f"delete_etaza_{etaza.id}"):
                            pass # Placeholder to prevent syntax error
                    else:
                        st.write("Ima prostorije")
                
                # Detaljne postavke etaže kao expander
                with st.expander("Postavke etaže", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        novi_naziv = st.text_input(
                            "Naziv etaže:", 
                            value=etaza.naziv,
                            key=f"etaza_naziv_{etaza.id}"
                        )
                        if novi_naziv != etaza.naziv:
                            etaza.naziv = novi_naziv
                            model._spremi_u_session_state()
                    
                    with col2:
                        nova_visina = st.number_input(
                            "Zadana visina etaže [m]:", 
                            min_value=2.0, 
                            max_value=6.0, 
                            value=etaza.visina_etaze,
                            step=0.1,
                            key=f"etaza_visina_{etaza.id}"
                        )
                        if nova_visina != etaza.visina_etaze:
                            etaza.visina_etaze = nova_visina
                            model._spremi_u_session_state()
                    
                    # Popis prostorija na etaži
                    if broj_prostorija > 0:
                        st.markdown("##### Prostorije na etaži")
                        
                        prostorije_na_etazi = model.dohvati_prostorije_za_etazu(etaza.id)
                        for p in prostorije_na_etazi:
                            st.markdown(f"- {p.naziv} ({p.tip}, {p.povrsina:.1f} m²)")
    
    # Gumb za dodavanje nove etaže
    if st.button("+ Dodaj novu etažu", key="dodaj_etazu"):
        model.dodaj_etazu()
        st.success("Dodana nova etaža")
        st.rerun()

def prikazi_etaze_i_prostorije(model, elements_model):
    """
    Prikazuje hijerarhijski prikaz etaža i prostorija s mogućnošću odabira
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s više prostorija
    elements_model : BuildingElementsModel
        Model s definiranim tipovima elemenata
        
    Returns:
    --------
    dict
        Kontekst s odabranom prostorijom
    """
    st.markdown("<h3 class='subsection-header'>Odabir prostorije</h3>", unsafe_allow_html=True)
    
    # Inicijalizacija varijabli u session state ako ne postoje
    if 'aktivna_etaza_id' not in st.session_state and model.etaze:
        st.session_state['aktivna_etaza_id'] = model.etaze[0].id
    
    aktivna_prostorija = None
    
    # Izbor etaže preko padajućeg izbornika
    if model.etaze:
        opcije_etaza = [f"{e.id}: {e.naziv}" for e in sorted(model.etaze, key=lambda e: e.redni_broj)]
        
        # Pronalazimo trenutni indeks etaže
        trenutni_index = 0
        if 'aktivna_etaza_id' in st.session_state:
            for i, opcija in enumerate(opcije_etaza):
                if opcija.startswith(f"{st.session_state['aktivna_etaza_id']}:"):
                    trenutni_index = i
                    break
        
        odabrana_etaza_opcija = st.selectbox(
            "Odaberite etažu:",
            opcije_etaza,
            index=trenutni_index
        )
        
        # Izvlačimo ID etaže iz odabrane opcije
        odabrana_etaza_id = odabrana_etaza_opcija.split(":")[0]
        st.session_state['aktivna_etaza_id'] = odabrana_etaza_id
        
        # Dohvaćamo prostorije za odabranu etažu
        prostorije_na_etazi = model.dohvati_prostorije_za_etazu(odabrana_etaza_id)
        
        if prostorije_na_etazi:
            st.markdown("##### Prostorije na etaži")
            
            # Gumbi za odabir prostorije
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write("**Naziv prostorije**")
            with col2:
                st.write("**Površina**")
            with col3:
                st.write("**Akcije**")
            
            for prostorija in prostorije_na_etazi:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"{prostorija.naziv} ({prostorija.tip})")
                with col2:
                    st.write(f"{prostorija.povrsina:.1f} m²")
                with col3:
                    if st.button("Odaberi", key=f"odaberi_prostoriju_{prostorija.id}"):
                        st.session_state['aktivna_prostorija_id'] = prostorija.id
            
            # Gumb za dodavanje nove prostorije na etažu
            if st.button("+ Dodaj novu prostoriju", key=f"dodaj_prostoriju_etaza_{odabrana_etaza_id}"):
                nova_prostorija = model.dodaj_prostoriju(odabrana_etaza_id)
                st.session_state['aktivna_prostorija_id'] = nova_prostorija.id
                st.rerun()
        else:
            st.info(f"Nema prostorija na etaži {model.dohvati_etazu(odabrana_etaza_id).naziv}. Dodajte prvu prostoriju.")
            
            # Gumb za dodavanje nove prostorije na etažu
            if st.button("+ Dodaj novu prostoriju", key=f"dodaj_prvu_prostoriju_etaza_{odabrana_etaza_id}"):
                nova_prostorija = model.dodaj_prostoriju(odabrana_etaza_id)
                st.session_state['aktivna_prostorija_id'] = nova_prostorija.id
                st.rerun()
    else:
        st.warning("Nema definiranih etaža. Dodajte etaže na kartici 'Postavke zgrade'.")
    
    # Dohvaćamo aktivnu prostoriju
    if 'aktivna_prostorija_id' in st.session_state:
        aktivna_prostorija = model.dohvati_prostoriju(st.session_state['aktivna_prostorija_id'])
    
    return {
        "model": model,
        "aktivna_prostorija": aktivna_prostorija,
        "elements_model": elements_model
    }

def prikazi_manager_prostorija(session_key: str, show_ui: bool = True):
    """
    Prikazuje sučelje za upravljanje prostorijama ili samo inicijalizira model.
    
    Parameters:
    -----------
    session_key : str
        Ključ za session state koji koristi model.
    show_ui : bool, optional
        Ako je True, prikazuje korisničko sučelje za upravljanje prostorijama.
        Ako je False, samo inicijalizira model bez prikazivanja sučelja.
    
    Returns:
    --------
    dict
        Rječnik s informacijama o aktivnoj prostoriji
    """
    # Inicijaliziramo model
    model = inicijaliziraj_model(session_key)
    
    # Inicijaliziramo model elemenata
    elements_model = inicijaliziraj_elemente()

    # Čišćenje potencijalno zaostalih UI state ključeva od prethodnih sesija
    # kako bi se izbjeglo neželjeno ponašanje pri učitavanju spremljenih projekata.
    # Pretpostavljamo da je osnovni key_prefix za zidove "zidovi_tab3__" ako je
    # prikazi_specificne_podatke_prostorije pozvan s praznim key_prefixom.
    # Ovo treba prilagoditi ako je struktura ključeva drugačija.
    if hasattr(model, 'prostorije') and isinstance(model.prostorije, list):
        # Dohvaćamo sve ID-jeve prostorija iz modela
        # Potrebno je osigurati da model.prostorije sadrži objekte Prostorija koji imaju .id atribut
        all_room_ids = []
        for p_obj in model.prostorije:
            if hasattr(p_obj, 'id') and p_obj.id:
                 all_room_ids.append(p_obj.id)
            elif isinstance(p_obj, dict) and p_obj.get('id'): # Ako su prostorije rječnici u nekom trenu
                 all_room_ids.append(p_obj['id'])


        for room_id in all_room_ids:
            # Konstruiramo ključeve na temelju pretpostavljene strukture.
            # Originalni key_prefix za prikazi_specificne_podatke_prostorije je često ""
            # unutar prikazi_specificne_podatke_prostorije, unique_key_prefix = f"tab3_{key_prefix}"
            # unutar prikazi_zidove_prostorije, unique_key_prefix = f"zidovi_{key_prefix_iz_spec_podataka}_{room_id}"
            # Dakle, ako je početni key_prefix="", onda je key_prefix_iz_spec_podataka="tab3_"
            # pa je konačni prefiks za ključeve unutar prikazi_zidove_prostorije: "zidovi_tab3__<room_id>"
            
            # Ako je prikazi_specificne_podatke_prostorije pozvan s npr. key_prefix="nešto",
            # onda bi bilo "zidovi_tab3_nešto_<room_id>"
            # Za sada, koristimo najčešći slučaj s praznim početnim key_prefixom.
            base_prefix_for_room_walls = f"zidovi_tab3__{room_id}" # Pretpostavka

            stale_key_defining = f"{base_prefix_for_room_walls}_defining_new_segmented_wall"
            stale_key_data = f"{base_prefix_for_room_walls}_new_segmented_wall_data"

            if stale_key_defining in st.session_state:
                del st.session_state[stale_key_defining]
            if stale_key_data in st.session_state:
                del st.session_state[stale_key_data]

    # Ako ne pokazujemo UI, samo vraćamo model i prazne podatke
    if not show_ui:
        return {
            "model": model,
            "aktivna_prostorija": None,
            "elements_model": elements_model
        }
    
    # Dohvaćamo aktivnu prostoriju ako je definirana
    aktivna_prostorija = None
    if 'aktivna_prostorija_id' in st.session_state:
        aktivna_prostorija = model.dohvati_prostoriju(st.session_state['aktivna_prostorija_id'])
    
    return {
        "model": model,
        "aktivna_prostorija": aktivna_prostorija, 
        "elements_model": elements_model
    }

def prikazi_osnovne_podatke_prostorije(prostorija, key_prefix=""):
    """
    Prikazuje osnovne podatke o prostoriji s mogućnošću uređivanja
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za prikaz
    key_prefix : str, optional
        Prefiks za Streamlit ključeve
        
    Returns:
    --------
    dict
        Ažurirani podaci o prostoriji
    """
    st.markdown("<h3 class='subsection-header'>Osnovni podaci</h3>", unsafe_allow_html=True)
    
    room_id = prostorija.id
    
    # Naziv prostorije (može se uređivati neovisno o tipu)
    # Add 'tab3_' to make sure keys are unique between tabs
    unique_key_prefix = f"tab3_{key_prefix}"
    
    naziv = st.text_input(
        "Naziv prostorije:", 
        value=prostorija.naziv, 
        key=f"{unique_key_prefix}naziv_{room_id}"
    )
    
    # Držimo stari tip za usporedbu
    stari_tip = prostorija.tip
    
    tip_prostorije = st.selectbox(
        "Tip prostorije:", 
        list(TIPOVI_PROSTORIJA.keys()), 
        index=list(TIPOVI_PROSTORIJA.keys()).index(prostorija.tip) if prostorija.tip in TIPOVI_PROSTORIJA else 0,
        key=f"{unique_key_prefix}tip_{room_id}"
    )
    
    # Provjera je li se tip prostorije promijenio
    tip_promijenjen = stari_tip != tip_prostorije
    
    # Ako je tip promijenjen, ažuriramo temperaturu i izmjene zraka iz konstanti
    if tip_promijenjen:
        prostorija.azuriraj_tip_prostorije(tip_prostorije)
    
    # Vrijednosti temperature i izmjena zraka se prikazuju iz prostorije
    # ali mogu se i ručno mijenjati
    temp_unutarnja = st.slider(
        "Unutarnja projektna temperatura [°C]:",
        min_value=10,
        max_value=26,
        value=int(prostorija.temp_unutarnja),  # Uzimamo trenutnu vrijednost iz prostorije
        step=1,
        key=f"{unique_key_prefix}temp_{room_id}",
        help="Početna vrijednost je postavljena prema tipu prostorije, ali može se prilagoditi"
    )
    
    izmjene_zraka = st.number_input(
        "Broj izmjena zraka [1/h]:",
        min_value=0.1,
        max_value=5.0,
        value=float(prostorija.izmjene_zraka),  # Uzimamo trenutnu vrijednost iz prostorije
        step=0.1,
        key=f"{unique_key_prefix}izmjene_{room_id}",
        help="Početna vrijednost je postavljena prema tipu prostorije, ali može se prilagoditi"
    )

    temp_susjednog_negrijanog = st.slider(
        "Temperatura susjednog negrijanog prostora [°C]:",
        min_value=-20,
        max_value=18, # Negrijani prostor ne bi trebao biti topliji od minimalne grijane
        value=int(prostorija.temperatura_susjednog_negrijanog),
        step=1,
        key=f"{unique_key_prefix}temp_negrijanog_{room_id}",
        help="Temperatura negrijanih prostora uz ovu prostoriju."
    )

    # Spremamo izmjene
    prostorija.naziv = naziv
    prostorija.tip = tip_prostorije
    prostorija.temp_unutarnja = temp_unutarnja
    prostorija.izmjene_zraka = izmjene_zraka
    prostorija.temperatura_susjednog_negrijanog = temp_susjednog_negrijanog

    return {
        "naziv": naziv,
        "tip_prostorije": tip_prostorije,
        "temp_unutarnja": temp_unutarnja,
        "izmjene_zraka": izmjene_zraka,
        "temperatura_susjednog_negrijanog": temp_susjednog_negrijanog
    }

def prikazi_dimenzije_prostorije(prostorija, model, key_prefix=""):
    """
    Prikazuje polja za unos dimenzija prostorije s mogućnošću uređivanja
    Omogućuje unos površine umjesto duljine i širine
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za prikaz
    model : MultiRoomModel
        Model s više prostorija (za dohvat zadane visine etaže)
    key_prefix : str, optional
        Prefiks za Streamlit ključeve
        
    Returns:
    --------
    dict
        Ažurirani podaci o dimenzijama prostorije
    """
    st.markdown("<h3 class='subsection-header'>Dimenzije prostorije</h3>", unsafe_allow_html=True)
    
    room_id = prostorija.id
    
    # Add 'tab3_' to make sure keys are unique
    unique_key_prefix = f"tab3_{key_prefix}"

    # Get the height of the etaza this prostorija belongs to
    etaza_obj = model.dohvati_etazu(prostorija.etaza_id)
    # Provide a fallback if etaza_obj is None, though it shouldn't happen in normal flow
    aktualna_visina_etaze = etaza_obj.visina_etaze if etaza_obj else 2.8 
    
    # Unos površine
    povrsina = st.number_input(
        "Površina prostorije [m²]:", 
        min_value=1.0, 
        max_value=100.0, 
        value=prostorija.povrsina, 
        step=0.5,
        key=f"{unique_key_prefix}povrsina_{room_id}",
        help="Unesite ukupnu površinu prostorije"
    )
    
    # Ako se površina promijenila, ažuriramo dimenzije
    if povrsina != prostorija.povrsina:
        prostorija.povrsina = povrsina
    
    # Checkbox for using default height
    koristi_zadanu_visinu = st.checkbox(
        "Koristi zadanu visinu etaže", 
        value=prostorija.koristi_zadanu_visinu,
        key=f"{unique_key_prefix}koristi_zadanu_visinu_{room_id}",
        help=f"Ako je označeno, koristit će se zadana visina etaže ({aktualna_visina_etaze} m)"
    )
    
    # Ako ne koristi zadanu visinu, prikazujemo polje za unos visine
    if not koristi_zadanu_visinu:
        # Ako prije nije imao vlastitu visinu, inicijaliziramo je na zadanu visinu etaže
        if prostorija.visina is None:
            prostorija.visina = aktualna_visina_etaze
            
        visina = st.number_input(
            "Visina prostorije [m]:", 
            min_value=2.0, 
            max_value=6.0, 
            value=prostorija.visina, 
            step=0.1,
            key=f"{unique_key_prefix}visina_{room_id}"
        )
        prostorija.visina = visina
    else:
        # Informativni prikaz zadane visine
        st.write(f"Visina prostorije: {aktualna_visina_etaze} m (zadana visina etaže)")
    
    # Spremamo izmjene
    prostorija.koristi_zadanu_visinu = koristi_zadanu_visinu
    
    return {
        "povrsina": povrsina,
        "koristi_zadanu_visinu": koristi_zadanu_visinu,
        "visina": prostorija.visina if not koristi_zadanu_visinu else None
    }

def prikazi_pod_i_strop_prostorije(prostorija, u_values, key_prefix=""):
    """
    Prikazuje polja za unos podataka o podu i stropu s mogućnošću uređivanja
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za prikaz
    u_values : dict
        U-vrijednosti građevinskih elemenata
    key_prefix : str, optional
        Prefiks za Streamlit ključeve
        
    Returns:
    --------
    dict
        Ažurirani podaci o podu i stropu
    """
    st.markdown("<h3 class='subsection-header'>Pod i strop</h3>", unsafe_allow_html=True)
    
    room_id = prostorija.id
    
    # Add 'tab3_' to make sure keys are unique
    unique_key_prefix = f"tab3_{key_prefix}"
    
    pod_tip = st.selectbox(
        "Tip poda (prema):", 
        list(TEMP_FAKTORI.keys()),
        index=list(TEMP_FAKTORI.keys()).index(prostorija.pod_tip) if prostorija.pod_tip in TEMP_FAKTORI else 0,
        key=f"{unique_key_prefix}pod_tip_{room_id}"
    )
    
    if pod_tip == "Prema tlu":
        u_pod = u_values["Pod prema tlu"]
    elif pod_tip == "Prema negrijanom prostoru":
        u_pod = u_values["Pod prema negrijanom prostoru"]
    elif pod_tip == "Prema vanjskom prostoru":
        u_pod = u_values["Pod prema vanjskom prostoru"]
    else:
        u_pod = u_values["Pod prema tlu"]
    
    strop_tip = st.selectbox(
        "Tip stropa (prema):", 
        list(TEMP_FAKTORI.keys()),
        index=list(TEMP_FAKTORI.keys()).index(prostorija.strop_tip) if prostorija.strop_tip in TEMP_FAKTORI else 0,
        key=f"{unique_key_prefix}strop_tip_{room_id}"
    )
    
    if strop_tip == "Prema vanjskom prostoru":
        strop_podtip = st.radio(
            "Tip krova:", 
            ["Ravan krov", "Kosi krov"],
            key=f"{unique_key_prefix}strop_podtip_{room_id}"
        )
        if strop_podtip == "Ravan krov":
            u_strop = u_values["Ravan krov"]
        else:
            u_strop = u_values["Kosi krov"]
    elif strop_tip == "Prema negrijanom prostoru":
        u_strop = u_values["Strop prema negrijanom prostoru"]
    elif strop_tip == "Prema tlu":
        u_strop = u_values["Strop prema tavanu"]
    else:
        u_strop = u_values["Strop prema negrijanom prostoru"]
    
    # Spremamo izmjene
    prostorija.pod_tip = pod_tip
    prostorija.strop_tip = strop_tip
    
    return {
        "pod_tip": pod_tip,
        "u_pod": u_pod,
        "strop_tip": strop_tip,
        "u_strop": u_strop
    }

def prikazi_zidove_prostorije(prostorija, model, elements_model, key_prefix=""):
    st.markdown("<h3 class='subsection-header'>Zidovi prostorije</h3>", unsafe_allow_html=True)
    room_id = prostorija.id
    unique_key_prefix = f"zidovi_{key_prefix}_{room_id}"

    etaza = model.dohvati_etazu(prostorija.etaza_id)
    visina_prostorije_actual = prostorija.get_actual_height(etaza) if etaza else 2.8

    # Prikaz postojećih zidova
    st.markdown("##### Postojeći zidovi")
    if not prostorija.zidovi:
        st.info("Nema definiranih zidova za ovu prostoriju.")
    else:
        for i, zid in enumerate(prostorija.zidovi):
            # Defensive access assuming zid might be a dict
            zid_tip = zid.get('tip_zida', 'Nepoznat')
            zid_duzina = zid.get('duzina', 0.0)
            zid_orijentacija = zid.get('orijentacija')
            zid_povezana_id = zid.get('povezana_ciljna_prostorija_id')
            zid_id = zid.get('id', f'fallback_id_{i}') # Fallback ID for key
            zid_tip_zida_id = zid.get('tip_zida_id')
            zid_visina = zid.get('visina_zida')
            zid_je_segmentiran = zid.get('je_segmentiran', False)
            zid_segmenti = zid.get('segmenti', [])

            zid_details = f"Zid {i+1}: Tip: {zid_tip}, Duljina: {zid_duzina}m"
            if zid_orijentacija:
                zid_details += f", Orijentacija: {zid_orijentacija}"
            if zid_povezana_id:
                try:
                    povezana_prostorija = model.dohvati_prostoriju(zid_povezana_id)
                    zid_details += f", Povezan s: {povezana_prostorija.naziv if povezana_prostorija else 'Nepoznata prostorija'}"
                except Exception:
                    zid_details += f", Povezan s ID: {zid_povezana_id[:4]}..."

            # Dohvaćanje naziva tipa zida ako postoji ID
            zid_tip_naziv = "" # Corrected indentation
            element_zida = None  # Initialize element_zida
            if zid_tip_zida_id and elements_model:
                element_zida = elements_model.dohvati_element(zid_tip_zida_id)
                if element_zida:
                    zid_tip_naziv = f" ({element_zida.naziv})"
                    
            zid_display_name = f"Zid {i+1}: {zid_tip.replace('_', ' ').capitalize()}{zid_tip_naziv} - {zid_duzina}m"
            if zid_orijentacija:
                zid_display_name += f", {zid_orijentacija}"

            with st.expander(zid_display_name):
                st.write(f"ID zida: {zid_id}")
                st.write(f"Tip zida: {zid_tip}")
                st.write(f"Duljina: {zid_duzina} m")
                st.write(f"Visina: {zid_visina if zid_visina is not None else visina_prostorije_actual} m (Automatska visina: {visina_prostorije_actual} m)")
                
                if zid_tip_zida_id:
                    st.write(f"ID tipa elementa zida: {zid_tip_zida_id}")
                    if element_zida:  # Check if element_zida was found
                         st.write(f"Naziv elementa: {element_zida.naziv}, U-vrijednost: {element_zida.u_vrijednost}")

                if zid_orijentacija:
                    st.write(f"Orijentacija: {zid_orijentacija}")
                if zid_povezana_id:
                    try:
                        povezana_prostorija = model.dohvati_prostoriju(zid_povezana_id)
                        st.write(f"Povezana prostorija: {povezana_prostorija.naziv if povezana_prostorija else 'Nepoznata prostorija'} (ID: {zid_povezana_id[:4]}...)")
                    except Exception as e:
                        st.write(f"Povezana prostorija ID: {zid_povezana_id[:4]}... (Greška pri dohvaćanju: {e})")

                st.write(f"Segmentiran: {'Da' if zid_je_segmentiran else 'Ne'}")
                if zid_je_segmentiran and zid_segmenti:
                    st.write("Segmenti:")
                    for seg_idx, segment in enumerate(zid_segmenti):
                        # Assuming segment is also a dict
                        seg_tip = segment.get('tip_segmenta', 'Nepoznat')
                        seg_duzina = segment.get('duzina_segmenta', 0.0)
                        seg_visina = segment.get('visina_segmenta', 0.0)
                        st.write(f"  - Segment {seg_idx + 1}: Tip: {seg_tip}, Duljina: {seg_duzina}m, Visina: {seg_visina}m")
                
                # Dodajemo prikaz prozora i vrata koristeći postojeće funkcije
                st.markdown("---")
                st.markdown("##### Prozori i vrata na zidu")
                
                if zid_tip == "vanjski":
                    prikazi_vanjski_zid_s_elementima(zid, visina_prostorije_actual, elements_model, key_prefix=f"{unique_key_prefix}_elem_{zid_id}")
                elif zid_tip == "prema_prostoriji" and zid_povezana_id:
                    povezana_prostorija = model.dohvati_prostoriju(zid_povezana_id)
                    if povezana_prostorija:
                        prikazi_unutarnji_zid_s_elementima(zid, visina_prostorije_actual, elements_model, povezana_prostorija, key_prefix=f"{unique_key_prefix}_elem_{zid_id}")
                else: # Corrected alignment and new line for the else statement
                    # Za ostale tipove zidova (npr. prema_negrijanom) možemo koristiti prikaz vanjskog zida bez orijentacije
                    prikazi_vanjski_zid_s_elementima(zid, visina_prostorije_actual, elements_model, key_prefix=f"{unique_key_prefix}_elem_{zid_id}")
                
                # Gumb za brisanje zida
                if st.button(f"Obriši zid {i+1}", key=f"{unique_key_prefix}_delete_wall_{zid_id}"):
                    model.obrisi_zid_iz_prostorije(prostorija.id, zid_id)
                    st.success(f"Zid {zid_id} obrisan.")
                    st.rerun()

    # POJEDNOSTAVLJENI PRISTUP - JEDAN ZAJEDNIČKI FORM ZA DEFINIRANJE ZIDA
    with st.form(key=f"{unique_key_prefix}_form_dodaj_zid"):
        st.markdown("##### Dodaj novi zid")
        
        # Definiranje tipa zida
        form_tip_zida_val = st.selectbox(
            "Tip zida:", 
            ["vanjski", "prema_prostoriji", "prema_negrijanom"], 
            key=f"{unique_key_prefix}_form_tip_zida",
            help="Odaberite tip zida prema njegovoj poziciji"
        )
        
        # Odmah prikazujemo odgovarajuća polja na osnovu odabranog tipa zida
        col_form_duzina, col_form_dodatno = st.columns(2)
        
        with col_form_duzina:
            form_duzina_val = st.number_input(
                "Duljina zida [m]:", 
                min_value=0.1, value=3.0, step=0.1, 
                key=f"{unique_key_prefix}_form_duzina"
            )
            
            # Checkbox za segmentaciju
            je_segmentiran = st.checkbox(
                "Ovaj zid je segmentiran", 
                key=f"{unique_key_prefix}_je_segmentiran",
                help="Ako je označeno, zid će se podijeliti na više segmenata različitih tipova"
            )
        
        # Dodatni parametri ovisno o tipu zida
        with col_form_dodatno:
            form_orijentacija_val = None
            form_povezana_prostorija_id_val = None
            form_tip_zida_id_val = None
            
            if form_tip_zida_val == "vanjski":
                # Dodatno omogućavamo odabir tipa vanjskog zida
                vanjski_zidovi = [z for z in elements_model.zidovi if z.tip == "vanjski"]
                if vanjski_zidovi:
                    opcije_vanjskih_zidova = {z.id: f"{z.naziv} (d={z.debljina}cm, U={z.u_vrijednost})" for z in vanjski_zidovi}
                    
                    form_tip_zida_id_val = st.selectbox(
                        "Odaberi tip vanjskog zida:",
                        options=list(opcije_vanjskih_zidova.keys()),
                        format_func=lambda x: opcije_vanjskih_zidova.get(x, ""),
                        key=f"{unique_key_prefix}_form_tip_vanjski_zid"
                    )
                
                form_orijentacija_val = st.selectbox(
                    "Orijentacija:", 
                    list(ORIJENTACIJE.keys()), 
                    key=f"{unique_key_prefix}_form_orijentacija"
                )
            
            elif form_tip_zida_val == "prema_prostoriji":
                # Dodatno omogućavamo odabir tipa unutarnjeg zida
                unutarnji_zidovi = [z for z in elements_model.zidovi if z.tip == "unutarnji"]
                if unutarnji_zidovi:
                    opcije_unutarnjih_zidova = {z.id: f"{z.naziv} (d={z.debljina}cm, U={z.u_vrijednost})" for z in unutarnji_zidovi}
                    
                    form_tip_zida_id_val = st.selectbox(
                        "Odaberi tip unutarnjeg zida:",
                        options=list(opcije_unutarnjih_zidova.keys()),
                        format_func=lambda x: opcije_unutarnjih_zidova.get(x, ""),
                        key=f"{unique_key_prefix}_form_tip_unutarnji_zid"
                    )
                
                # Odmah prikazujemo polje za odabir povezane prostorije
                sve_prostorije_form = model.prostorije
                ostale_prostorije_form = [p for p in sve_prostorije_form if p.id != prostorija.id]
                
                opcije_povezanih_prostorija_form = {"": "Odaberi prostoriju..."}
                opcije_povezanih_prostorija_form.update({p.id: f"{p.naziv} (ID: {p.id[:4]}...)" for p in ostale_prostorije_form})
                
                form_povezana_prostorija_id_val = st.selectbox(
                    "Povezana prostorija:",
                    options=list(opcije_povezanih_prostorija_form.keys()),
                    format_func=lambda x: opcije_povezanih_prostorija_form.get(x, "Nije odabrano"),
                    key=f"{unique_key_prefix}_form_povezana_prostorija"
                )
            
            elif form_tip_zida_val == "prema_negrijanom":
                # Dodatno omogućavamo odabir tipa zida prema negrijanom
                negrijani_zidovi = [z for z in elements_model.zidovi if z.tip == "negrijani"]
                if negrijani_zidovi:
                    opcije_negrijanih_zidova = {z.id: f"{z.naziv} (d={z.debljina}cm, U={z.u_vrijednost})" for z in negrijani_zidovi}
                    
                    form_tip_zida_id_val = st.selectbox(
                        "Odaberi tip zida prema negrijanom:",
                        options=list(opcije_negrijanih_zidova.keys()),
                        format_func=lambda x: opcije_negrijanih_zidova.get(x, ""),
                        key=f"{unique_key_prefix}_form_tip_negrijani_zid"
                    )
                
                st.info("Zid prema negrijanom prostoru. Koristit će se temp. negrijanog prostora definirana za prostoriju.")
        
        # Prikaz definicije segmenata ako je zid segmentiran
        if je_segmentiran:
            st.markdown("##### Segmenti zida")
            st.info("Nakon dodavanja zida, moći ćete definirati segmente kroz posebno sučelje.")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button_label = "Dodaj zid i definiraj segmente" if je_segmentiran else "Dodaj zid"
            submitted_dodaj_zid = st.form_submit_button(submit_button_label, type="primary")
        
        with col2:
            # Opcija za poništavanje/čišćenje forme
            submitted_cancel = st.form_submit_button("Poništi unos")
        
        if submitted_dodaj_zid:
            # Validacija ulaznih podataka
            valid_input = True
            
            if form_tip_zida_val == "prema_prostoriji" and not form_povezana_prostorija_id_val:
                st.warning("Za zid tipa 'prema prostoriji' morate odabrati povezanu prostoriju.")
                valid_input = False
            
            if form_tip_zida_val == "vanjski" and not form_orijentacija_val:
                st.warning("Za vanjski zid morate odabrati orijentaciju.")
                valid_input = False
            
            if valid_input:
                try:
                    # Dodajemo zid u model
                    new_wall_id = model.add_wall_to_room(
                        prostorija_id=prostorija.id,
                        tip_zida=form_tip_zida_val,
                        duzina=form_duzina_val,
                        visina_zida=None, 
                        orijentacija=form_orijentacija_val,
                        povezana_ciljna_prostorija_id=form_povezana_prostorija_id_val,
                        je_segmentiran=je_segmentiran,
                        tip_zida_id=form_tip_zida_id_val  # Dodajemo ID odabranog tipa zida
                    )
                    
                    # Ako je zid segmentiran, postavljamo stanje za definiranje segmenata
                    if je_segmentiran:
                        st.session_state[f"{unique_key_prefix}_editing_segments_for_wall"] = new_wall_id
                        st.success(f"Zid je dodan. Nastavite s definiranjem segmenata.")
                    else:
                        st.success(f"Zid tipa '{form_tip_zida_val}' duljine {form_duzina_val}m je dodan.")
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Greška pri dodavanju zida: {str(e)}")

def prikazi_specificne_podatke_prostorije(prostorija, model, elements_model, key_prefix=""):
    """
    Prikazuje specifične podatke o prostoriji (pod, strop, zidovi)
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za prikaz
    model : MultiRoomModel
        Model s više prostorija
    elements_model : BuildingElementsModel
        Model s definiranim tipovima elemenata
    key_prefix : str, optional
        Prefiks za Streamlit ključeve
    """
    st.markdown("<h3 class='subsection-header'>Specifični podaci prostorije</h3>", unsafe_allow_html=True)
    
    room_id = prostorija.id
    unique_key_prefix = f"tab3_{key_prefix}"
    
    # Podaci o podu
    st.markdown("##### Pod")
    pod_tip = st.selectbox(
        "Tip poda:", 
        ["Prema tlu", "Prema negrijanom prostoru", "Iznad grijanog prostora"],
        index=["Prema tlu", "Prema negrijanom prostoru", "Iznad grijanog prostora"].index(prostorija.pod_tip) if prostorija.pod_tip in ["Prema tlu", "Prema negrijanom prostoru", "Iznad grijanog prostora"] else 0,
        key=f"{unique_key_prefix}pod_tip_{room_id}"
    )
    prostorija.pod_tip = pod_tip
    
    # Podaci o stropu
    st.markdown("##### Strop")
    strop_tip = st.selectbox(
        "Tip stropa:", 
        ["Prema negrijanom prostoru", "Ispod grijanog prostora", "Ravni krov"],
        index=["Prema negrijanom prostoru", "Ispod grijanog prostora", "Ravni krov"].index(prostorija.strop_tip) if prostorija.strop_tip in ["Prema negrijanom prostoru", "Ispod grijanog prostora", "Ravni krov"] else 0,
        key=f"{unique_key_prefix}strop_tip_{room_id}"
    )
    prostorija.strop_tip = strop_tip
    
    # Prikaz zidova
    prikazi_zidove_prostorije(prostorija, model, elements_model, key_prefix=unique_key_prefix)