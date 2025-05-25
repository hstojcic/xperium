"""
UI komponente za proračun plinskog priključka.
"""
import streamlit as st
from .constants import *
from .data_tables import *
from .calculation_utils import validate_pipe_selection, validate_velocity, validate_pressure_drop, get_pipe_recommendations

def render_connection_type_selection(data):
    """
    Prikaz izbora vrste plinskog priključka.
    
    Args:
        data: Dictionary s podacima iz session_state
    """
    st.subheader("Vrsta plinskog priključka")
    
    options = ["Niskotlačni priključak (do 100 mbar)", "Srednjetlačni priključak (0,1-5,0 bar)"]
    
    selected_option = st.radio(
        "Odaberite vrstu plinskog priključka:",
        options=options,
        index=data["tip_prikljucka"] - 1,
        horizontal=True
    )
    
    # Postavljanje vrijednosti 1 ili 2 ovisno o odabiru
    data["tip_prikljucka"] = options.index(selected_option) + 1
    
    # Prikaži dodatne informacije o odabranom tipu
    if data["tip_prikljucka"] == 1:
        st.info("Kod niskotlačnog priključka maksimalni dozvoljeni pad tlaka je 1 mbar.")
    else:
        st.info("Kod srednjetlačnog priključka maksimalni dozvoljeni pad tlaka je 100 mbar.")

def render_boiler_selection(data):
    """
    Prikaz izbora kotla.
    
    Args:
        data: Dictionary s podacima o kotlu
    """
    st.subheader("Plinski kotao")
    
    # Odabir ima li kotao ili ne
    kotao_options = ["Kondenzacijski kotao", "Klasični kotao", "Nema kotla"]
    kotao_selection = st.radio(
        "Odaberite vrstu plinskog kotla:",
        options=kotao_options,
        index=0 if data["tip"] == 1 and data["ima_kotao"] else 
              1 if data["tip"] == 2 and data["ima_kotao"] else 2,
        horizontal=True
    )
    
    # Ažuriranje podataka o kotlu
    data["ima_kotao"] = kotao_selection != "Nema kotla"
    
    if data["ima_kotao"]:
        data["tip"] = 1 if kotao_selection == "Kondenzacijski kotao" else 2
        
        # Postavi odgovarajući eta
        data["eta"] = ETA_KONDENZACIJSKI if data["tip"] == 1 else ETA_KLASICNI
        
        # Kontejner za detalje kotla
        with st.container():
            # Odabir proizvođača
            proizvodjaci = list(KOTLOVI.keys())
            if not data["proizvodjac"] or data["proizvodjac"] not in proizvodjaci:
                data["proizvodjac"] = proizvodjaci[0]
                
            proizvodjac = st.selectbox(
                "Proizvođač kotla:",
                proizvodjaci,
                index=proizvodjaci.index(data["proizvodjac"])
            )
            data["proizvodjac"] = proizvodjac
            
            # Odabir modela kotla
            tip_kotla = "Kondenzacijski" if data["tip"] == 1 else "Klasični"
            
            if proizvodjac in KOTLOVI and tip_kotla in KOTLOVI[proizvodjac]:
                modeli = KOTLOVI[proizvodjac][tip_kotla]
                model_names = [m["model"] for m in modeli]
                
                if model_names:
                    if not data["model"] or data["model"] not in model_names:
                        data["model"] = model_names[0]
                        
                    model_index = model_names.index(data["model"]) if data["model"] in model_names else 0
                    model = st.selectbox(
                        "Model kotla:", 
                        model_names,
                        index=model_index
                    )
                    
                    # Ažuriranje podataka o odabranom modelu
                    data["model"] = model
                    selected_model = next((m for m in modeli if m["model"] == model), None)
                    
                    if selected_model:
                        data["snaga_grijanja"] = selected_model["Pgr"]
                        data["snaga_ptv"] = selected_model["Pptv"]
                        
                        # Prikaz detalja odabranog kotla
                        st.info(f"Snaga grijanja: {data['snaga_grijanja']} kW | "
                                f"Snaga PTV: {data['snaga_ptv']} kW")
                else:
                    st.warning(f"Nema dostupnih modela za odabrani tip kotla i proizvođača.")
            else:
                st.warning(f"Nema dostupnih modela za odabrani tip kotla i proizvođača.")
            
            # Odabir broja kotlova
            col1, col2 = st.columns([1, 2])
            
            with col1:
                data["broj_kotlova"] = st.number_input(
                    "Broj kotlova:", 
                    min_value=1, 
                    max_value=10, 
                    value=data["broj_kotlova"]
                )
            
            # Automatski izračun faktora istovremenosti
            data["faktor"] = F_KOTAO[data["broj_kotlova"]]
            
            with col2:
                st.info(f"Faktor istovremenosti: {data['faktor']:.3f}")

def render_stove_selection(data):
    """
    Prikaz izbora plinskog štednjaka/ploče.
    
    Args:
        data: Dictionary s podacima o plinskom uređaju
    """
    st.subheader("Plinska ploča/štednjak")
    
    # Odabir ima li ploču/štednjak ili ne
    uredjaj_options = ["Plinska ploča", "Plinski štednjak", "Nema ga"]
    uredjaj_selection = st.radio(
        "Odaberite vrstu plinskog uređaja:",
        options=uredjaj_options,
        index=0 if data["tip"] == 1 and data["ima_uredjaj"] else 
              1 if data["tip"] == 2 and data["ima_uredjaj"] else 2,
        horizontal=True
    )
    
    # Ažuriranje podataka o uređaju
    data["ima_uredjaj"] = uredjaj_selection != "Nema ga"
    
    if data["ima_uredjaj"]:
        data["tip"] = 1 if uredjaj_selection == "Plinska ploča" else 2
        data["naziv"] = uredjaj_selection
        data["eta"] = ETA_PLOCA
        
        # Kontejner za detalje uređaja
        with st.container():
            # Odabir broja plamenika
            if data["tip"] == 1:  # Plinska ploča
                plamenici_options = ["2 plamenika", "3 plamenika", "4 plamenika"]
                default_index = min(data["broj_plamenika"] - 2, 2)
            else:  # Štednjak
                plamenici_options = ["3 plamenika", "4 plamenika"]
                default_index = min(data["broj_plamenika"] - 3, 1)
                
            plamenici_selection = st.radio(
                "Odaberite broj plamenika:",
                options=plamenici_options,
                index=default_index,
                horizontal=True
            )
            
            # Ažuriranje broja plamenika
            if data["tip"] == 1:  # Plinska ploča
                data["broj_plamenika"] = plamenici_options.index(plamenici_selection) + 2
            else:  # Štednjak
                data["broj_plamenika"] = plamenici_options.index(plamenici_selection) + 3
            
            # Opcija za pećnicu (samo za štednjak s 4 plamenika)
            if data["tip"] == 2 and data["broj_plamenika"] == 4:
                data["ima_pecnicu"] = st.checkbox(
                    "Štednjak ima pećnicu", 
                    value=data["ima_pecnicu"]
                )
            else:
                data["ima_pecnicu"] = False
            
            # Odabir broja uređaja
            col1, col2 = st.columns([1, 2])
            
            with col1:
                data["broj_uredjaja"] = st.number_input(
                    f"Broj {data['naziv'].lower()}a:", 
                    min_value=1, 
                    max_value=10, 
                    value=data["broj_uredjaja"]
                )
            
            # Izračun snage i faktora
            broj_plamenika = data["broj_plamenika"]
            broj_uredjaja = data["broj_uredjaja"]
            
            # Snaga jednog uređaja
            if data["tip"] == 2 and data["broj_plamenika"] == 4 and data["ima_pecnicu"]:
                data["snaga_jedinicna"] = (broj_plamenika * 2) + 2  # Dodajemo 2 kW za pećnicu
                data["faktor"] = F_STEDNJAK_PECNICA[broj_uredjaja]
            else:
                data["snaga_jedinicna"] = broj_plamenika * 2
                if broj_plamenika == 2:
                    data["faktor"] = F_PLOCA_2[broj_uredjaja]
                else:  # 3 ili 4 plamenika
                    data["faktor"] = F_PLOCA_3_4[broj_uredjaja]
            
            # Ukupna snaga
            data["snaga_ukupna"] = data["snaga_jedinicna"] * broj_uredjaja
            
            with col2:
                st.info(f"Snaga po uređaju: {data['snaga_jedinicna']} kW | "
                        f"Ukupna snaga: {data['snaga_ukupna']} kW | "
                        f"Faktor istovremenosti: {data['faktor']:.3f}")

def render_pipe_length_input(data):
    """
    Prikaz unosa duljine cijevi.
    
    Args:
        data: Dictionary s podacima iz session_state
    """
    st.subheader("Duljina cjevovoda")
    
    data["cijev"]["duljina"] = st.number_input(
        "Duljina cjevovoda [m]:", 
        min_value=1.0, 
        max_value=1000.0, 
        value=data["cijev"]["duljina"],
        step=0.1,
        format="%.1f"
    )

def render_pipe_selection(data):
    """
    Prikaz odabira cijevi.
    
    Args:
        data: Dictionary s podacima iz session_state
    """
    st.subheader("Odabir cijevi")
    
    # Odabir vrste cijevi
    pipe_options = ["Polietilenske cijevi visoke gustoće (PE-HD)", "Čelične bešavne cijevi (SMLS)"]
    
    col1, col2 = st.columns([1, 1])
    with col1:
        selected_pipe = st.radio(
            "Odaberite vrstu cijevi:",
            options=pipe_options,
            index=data["cijev"]["tip"] - 1,
            horizontal=True
        )
        # Postavljanje vrijednosti 1 ili 2 ovisno o odabiru
        data["cijev"]["tip"] = pipe_options.index(selected_pipe) + 1
    
    # Dohvati preporuke cijevi
    preporuke = get_pipe_recommendations(data["rezultati"]["potreban_promjer"], data["cijev"]["tip"])
    
    # Dohvati odgovarajuću tablicu cijevi
    cijevi = PEHD_CIJEVI if data["cijev"]["tip"] == 1 else SMLS_CIJEVI
    materijal_cijevi = "PE-HD" if data["cijev"]["tip"] == 1 else "SMLS"
    
    # Prikaz preporuke za cijev
    with col2:
        if preporuke["preporucena"] is not None:
            st.info(
                f"{materijal_cijevi} Ø{cijevi[preporuke['preporucena']]['vanjski']}×{cijevi[preporuke['preporucena']]['debljina']}"
            )
        else:
            st.warning("Ne postoji odgovarajuća cijev za izračunati promjer.")
    
    # Prikaz dostupnih dimenzija cijevi
    st.write("Dostupne dimenzije cijevi:")
    
    # Prikazati cijevi za odabir uz preporuku na temelju potrebnog promjera
    potreban_promjer = data["rezultati"]["potreban_promjer"]
    odabrana_oznaka = data["cijev"]["oznaka"]
    
    # Postavi oznaku ako nije postavljena ili ne postoji u trenutnim cijevima
    if not odabrana_oznaka or not any(c["oznaka"] == odabrana_oznaka for c in cijevi.values()):
        if preporuke["preporucena"] is not None:
            data["cijev"]["oznaka"] = cijevi[preporuke["preporucena"]]["oznaka"]
        elif len(cijevi) > 0:
            data["cijev"]["oznaka"] = cijevi[max(cijevi.keys())]["oznaka"]
    
    # Kreiraj opcije za padajući izbornik s formatiranim tekstom
    pipe_options = []
    for i, dims in cijevi.items():
        option_text = f"{materijal_cijevi} Ø{dims['vanjski']}×{dims['debljina']}"
        
        if dims["unutarnji"] < potreban_promjer:
            option_text += " - Premali promjer!"
            
        pipe_options.append(option_text)
    
    # Pronađi trenutni indeks odabrane cijevi
    selected_index = 0
    for i, option in enumerate(pipe_options):
        if cijevi[i+1]["oznaka"] == data["cijev"]["oznaka"]:
            selected_index = i
            break
    
    # Prikaži padajući izbornik s cijevima
    selected_option = st.selectbox(
        "Odaberite dimenziju cijevi:",
        options=pipe_options,
        index=selected_index,
        help="Odaberite odgovarajuću dimenziju cijevi. Crveno označene cijevi imaju premali promjer."
    )
    
    # Ažuriraj podatke o odabranoj cijevi
    selected_index = pipe_options.index(selected_option) + 1
    data["cijev"]["oznaka"] = cijevi[selected_index]["oznaka"]
    data["cijev"]["dimenzije"] = {
        "vanjski": cijevi[selected_index]["vanjski"],
        "debljina": cijevi[selected_index]["debljina"],
        "unutarnji": cijevi[selected_index]["unutarnji"]
    }
    
    # Validacija odabrane cijevi
    validacija = validate_pipe_selection(potreban_promjer, data["cijev"]["dimenzije"]["unutarnji"])
    
    # Prikaži upozorenje ili informaciju ovisno o validaciji
    if not validacija[0]:
        st.error(validacija[1])
    elif "predimenzionirana" in validacija[1]:
        st.warning(validacija[1])
    else:
        st.success(validacija[1])
    
    # Prikaži informacije o odabranoj cijevi
    st.info(f"{materijal_cijevi} Ø{data['cijev']['dimenzije']['vanjski']}×{data['cijev']['dimenzije']['debljina']}")

def render_validation_results(data):
    """
    Prikaz rezultata validacije i savjeta.
    
    Args:
        data: Dictionary s podacima iz session_state
    """
    if not data["rezultati"]["vrsni_protok"] > 0 or not data["cijev"]["oznaka"]:
        return
    
    # Provjeri jesu li izračunati svi potrebni podaci
    if data["rezultati"]["stvarna_brzina"] <= 0 or data["rezultati"]["pad_tlaka"] <= 0:
        return
    
    with st.expander("Provjera i savjeti", expanded=False):
        # Validacija brzine
        validacija_brzine = validate_velocity(data["rezultati"]["stvarna_brzina"], data["tip_prikljucka"])
        
        if not validacija_brzine[0]:
            st.error(f"Brzina: {validacija_brzine[1]}")
        elif "predimenzionirana" in validacija_brzine[1]:
            st.warning(f"Brzina: {validacija_brzine[1]}")
        else:
            st.success(f"Brzina: {validacija_brzine[1]}")
        
        # Validacija pada tlaka
        validacija_pada_tlaka = validate_pressure_drop(data["rezultati"]["pad_tlaka"], data["tip_prikljucka"])
        
        if not validacija_pada_tlaka[0]:
            st.error(f"Pad tlaka: {validacija_pada_tlaka[1]}")
        elif "predimenzionirana" in validacija_pada_tlaka[1]:
            st.warning(f"Pad tlaka: {validacija_pada_tlaka[1]}")
        else:
            st.success(f"Pad tlaka: {validacija_pada_tlaka[1]}")
        
        # Savjeti za optimizaciju
        st.markdown("### Savjeti za optimizaciju")
        
        # Provjeri je li cijev možda predimenzionirana
        if "predimenzionirana" in validacija_brzine[1] or "predimenzionirana" in validacija_pada_tlaka[1]:
            st.info("""
            **Optimizacija dimenzije cijevi:**
            - Odabrana cijev je možda predimenzionirana što može povećati troškove instalacije.
            - Razmotrite korištenje cijevi manjeg promjera ako je to moguće.
            - Optimalna brzina plina u cijevima je između 3 i 6 m/s.
            """)
        
        # Ako je pad tlaka premašen
        if not validacija_pada_tlaka[0]:
            st.info("""
            **Smanjenje pada tlaka:**
            - Odaberite cijev većeg promjera da smanjite pad tlaka.
            - Razmotrite kraću dionicu cjevovoda ako je moguće.
            """)
        
        # Savjeti ovisno o tipu priključka
        if data["tip_prikljucka"] == 1:  # Niskotlačni
            st.info("""
            **Niskotlačni priključak - dodatni savjeti:**
            - Kod niskotlačnih priključaka važno je paziti na pad tlaka koji ne smije prelaziti 1 mbar.
            - Izbjegavajte nepotrebne zavoje i redukcije promjera koje dodatno povećavaju pad tlaka.
            """)
        else:  # Srednjetlačni
            st.info("""
            **Srednjetlačni priključak - dodatni savjeti:**
            - Srednjetlačni priključci dopuštaju veći pad tlaka (do 100 mbar).
            - Pazite na brzinu plina u cijevima koja ne bi trebala prelaziti 8 m/s.
            - Obavezno provjerite je li odabrani plinomjer primjeren za srednjetlačni priključak.
            """)