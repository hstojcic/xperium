# modules/thermal/ventilation/ventilation_recovery/ui/basic_info_ui.py

"""
UI components for the basic info tab of the ventilation recovery calculator.
"""

import streamlit as st
from modules.thermal.heating.heat_loss.constants import REGIJE_GRADOVI_TEMP

def render_basic_info_tab(calculator):
    """Prikazuje tab za unos osnovnih podataka."""
    st.header("Osnovni podaci o projektu")
    
    data = st.session_state.ventilation_recovery_data["basic_info"]

    # Podaci o lokaciji i temperaturi - prikazani prvi
    st.subheader("Lokacija i projektne temperature")
    
    # Odabir regije i grada - implementacija iz heat_loss kalkulatora
    regija = st.selectbox(
        "Odaberite regiju:",
        list(REGIJE_GRADOVI_TEMP.keys()),
        help="Odaberite klimatsku regiju za vašu lokaciju"
    )
    
    # Filtriramo gradove prema odabranoj regiji
    gradovi_regije = list(REGIJE_GRADOVI_TEMP[regija].keys())
    
    # Sortiramo gradove po abecedi
    gradovi_regije.sort()
    
    # Pronalazimo trenutni grad (ako postoji)
    trenutni_index = 0
    trenutna_temp = data.get("temperatures", {}).get("outdoor", 0)
    
    for i, grad in enumerate(gradovi_regije):
        if REGIJE_GRADOVI_TEMP[regija][grad] == trenutna_temp:
            trenutni_index = i
            break
    
    grad = st.selectbox(
        "Odaberite grad:",
        gradovi_regije,
        index=trenutni_index,
        help="Odaberite najbliži grad vašoj lokaciji"
    )
    
    # Automatsko postavljanje lokacije prema odabranom gradu
    data["location"] = f"{grad}, {regija}"
    
    # Osiguraj da postoji rječnik za temperature
    if "temperatures" not in data:
        data["temperatures"] = {"outdoor": -20.0, "indoor": 20.0}
    
    data["temperatures"]["outdoor"] = REGIJE_GRADOVI_TEMP[regija][grad]
    st.info(f"Vanjska projektna temperatura za {grad}: {data['temperatures']['outdoor']} °C")
    
    # Unutarnja temperatura kao sljedeći važan parametar
    data["temperatures"]["indoor"] = st.number_input(
        "Unutarnja temperatura [°C]", 
        min_value=18.0, 
        max_value=26.0, 
        value=data.get("temperatures", {}).get("indoor", 20.0), 
        step=1.0,
        help="Projektna unutarnja temperatura prostora"
    )
    
    # Podaci o prostoru
    st.subheader("Dimenzije prostora")
    data["area"] = st.number_input(
        "Površina prostora [m²]", 
        min_value=1.0, 
        max_value=1000.0, 
        value=data.get("area", 80.0), 
        step=1.0,
        help="Ukupna površina prostora koji se ventilira"
    )
    
    data["height"] = st.number_input(
        "Visina prostora [m]", 
        min_value=2.0, 
        max_value=10.0, 
        value=data.get("height", 3.0), 
        step=0.1,
        help="Prosječna visina prostora"
    )
    
    # Izračun volumena
    data["volume"] = data["area"] * data["height"]
    st.metric("Volumen prostora", f"{data['volume']:.1f} m³")
    
    # Podaci o broju osoba
    st.subheader("Broj korisnika")
    data["occupants"] = st.number_input(
        "Maksimalni broj osoba", 
        min_value=1, 
        max_value=200, 
        value=data.get("occupants", 30), 
        step=1,
        help="Maksimalni broj osoba u prostoru"
    )
    
    # Princip ventilacije
    st.subheader("Princip ventilacije")
    data["ventilation_principle"] = st.radio(
        "Odaberite princip ventilacije",
        options=["balanced", "supply_dominant", "extract_dominant"],
        format_func=lambda x: {
            "balanced": "Balansirana ventilacija",
            "supply_dominant": "Nadtlačna ventilacija (dominira tlak)",
            "extract_dominant": "Podtlačna ventilacija (dominira odsis)"
        }.get(x, x),
        index=0 if data.get("ventilation_principle", "balanced") == "balanced" else
              1 if data.get("ventilation_principle") == "supply_dominant" else 2,
        help="Odaberite princip rada ventilacijskog sustava"
    )
        
    # Ažuriranje podataka u ostalim tabovima
    # Protok zraka - metoda prema broju osoba
    airflow_data = st.session_state.ventilation_recovery_data["airflow"]
    
    # Osiguraj da postoji methods rječnik
    if "methods" not in airflow_data:
        airflow_data["methods"] = {
            "by_occupants": {"enabled": True, "parameters": {}, "result": 0.0},
            "by_area": {"enabled": False, "parameters": {}, "result": 0.0},
            "by_thermal_load": {"enabled": False, "parameters": {}, "result": 0.0},
            "by_air_changes": {"enabled": False, "parameters": {}, "result": 0.0}
        }
    
    # Osiguraj da postoji parameters rječnik
    for method in ["by_occupants", "by_area", "by_thermal_load", "by_air_changes"]:
        if method not in airflow_data["methods"]:
            airflow_data["methods"][method] = {"enabled": False, "parameters": {}, "result": 0.0}
        if "parameters" not in airflow_data["methods"][method]:
            airflow_data["methods"][method]["parameters"] = {}
    
    # Ažuriranje parametara
    if "by_occupants" in airflow_data["methods"]:
        airflow_data["methods"]["by_occupants"]["parameters"]["occupants"] = data["occupants"]
    
    # Protok zraka - metoda prema površini
    if "by_area" in airflow_data["methods"]:
        airflow_data["methods"]["by_area"]["parameters"]["area"] = data["area"]
    
    # Protok zraka - metoda prema izmjenama zraka
    if "by_air_changes" in airflow_data["methods"]:
        airflow_data["methods"]["by_air_changes"]["parameters"]["volume"] = data["volume"]
    
    # Ažuriranje podataka u session_state
    st.session_state.ventilation_recovery_data["basic_info"] = data
    calculator.mark_as_changed()