# modules/thermal/ventilation/ventilation_recovery/ui/airflow_ui.py

"""
UI components for the airflow calculation tab of the ventilation recovery calculator.
"""

import streamlit as st
import pandas as pd
from modules.thermal.ventilation.ventilation_recovery.constants import (
    AIR_QUALITY_CATEGORIES,
    AREA_USAGE_INTENSITY,
    AIR_CHANGE_RATES,
    DELTA_T_RANGES
)
from modules.thermal.ventilation.ventilation_recovery.air_flow import (
    calculate_by_occupants,
    calculate_by_area,
    calculate_by_air_changes,
    calculate_by_thermal_load
)

def render_airflow_tab(calculator):
    """Prikazuje tab za izračun protoka zraka."""
    st.header("Izračun protoka zraka")
    
    data = st.session_state.ventilation_recovery_data["airflow"]
    basic_info = st.session_state.ventilation_recovery_data["basic_info"]
    
    # Metoda proračuna
    st.subheader("Metoda proračuna")
    
    data["calculation_method"] = st.radio(
        "Odaberi metodu proračuna",
        options=["by_people", "by_area", "by_room", "manual"],
        format_func=lambda x: {
            "by_people": "Po broju osoba",
            "by_area": "Po površini",
            "by_room": "Po prostorijama",
            "manual": "Ručni unos"
        }.get(x, x),
        horizontal=True,
        index=["by_people", "by_area", "by_room", "manual"].index(data.get("calculation_method", "by_people")) 
            if data.get("calculation_method") in ["by_people", "by_area", "by_room", "manual"] else 0
    )
    
    if data["calculation_method"] == "by_room":
        render_by_room_calculation(data, basic_info)
    elif data["calculation_method"] == "by_people":
        render_by_people_calculation(data, basic_info)
    elif data["calculation_method"] == "by_area":
        render_by_area_calculation(data, basic_info)
    elif data["calculation_method"] == "manual":
        render_manual_calculation(data)
    
    # Prikaz izračunatog protoka
    st.subheader("Rezultati izračuna")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Izračunati ukupni protok
        st.metric("Ukupni protok zraka", f"{data['final_flow']:.1f} m³/h")
        
        # Faktor sigurnosti
        data["safety_factor"] = st.number_input(
            "Faktor sigurnosti",
            min_value=1.0,
            max_value=2.0,
            value=data.get("safety_factor", 1.15),
            step=0.05,
            help="Faktor sigurnosti za povećanje proračunskog protoka"
        )
    
    with col2:
        # Izračunati protok s faktorom sigurnosti
        adjusted_flow = data["final_flow"] * data["safety_factor"]
        st.metric("Protok s faktorom sigurnosti", f"{adjusted_flow:.1f} m³/h")
        
        # Koncentrirani protok (za projektiranje)
        if basic_info.get("ventilation_principle", "balanced") == "balanced":
            st.info("Balansirana ventilacija: protok tlaka i odsisa je jednak.")
        else:
            # Nebalansirana ventilacija, korisnik može podesiti omjer
            data["supply_extract_ratio"] = st.slider(
                "Omjer tlak/odsis",
                min_value=0.5,
                max_value=1.5,
                value=data.get("supply_extract_ratio", 1.0),
                step=0.05,
                help="Omjer protoka tlačnog i odsisnog zraka"
            )
            
            if data["supply_extract_ratio"] < 1.0:
                st.info(f"Podtlačni sustav: odsis je {1/data['supply_extract_ratio']:.2f}x veći od tlaka")
            elif data["supply_extract_ratio"] > 1.0:
                st.info(f"Nadtlačni sustav: tlak je {data['supply_extract_ratio']:.2f}x veći od odsisa")
    
    # Ažuriranje konačnog protoka u session_state
    data["final_flow"] = adjusted_flow
    
    # Ažuriranje podataka u session_state
    st.session_state.ventilation_recovery_data["airflow"] = data
    calculator.mark_as_changed()

def render_by_room_calculation(data, basic_info):
    """Prikazuje sučelje za izračun protoka po prostorijama."""
    st.subheader("Izračun protoka po prostorijama")
    
    # Inicijalizacija tablice prostorija ako je prazna
    if not data.get("rooms"):
        data["rooms"] = []
    
    # Dodavanje nove prostorije
    with st.expander("Dodaj novu prostoriju", expanded=len(data.get("rooms", [])) == 0):
        col1, col2 = st.columns(2)
        
        with col1:
            new_room_name = st.text_input("Naziv prostorije", key="new_room_name")
            new_room_area = st.number_input("Površina [m²]", min_value=0.1, step=0.5, key="new_room_area")
        
        with col2:
            new_room_height = st.number_input("Visina [m]", min_value=2.0, max_value=10.0, value=2.6, step=0.1, key="new_room_height")
            
            # Provjera definiranih tipova prostorija
            try:
                from modules.thermal.ventilation.ventilation_recovery.constants import ROOM_TYPES
                room_type_options = list(ROOM_TYPES.keys())
                room_type_format = lambda x: ROOM_TYPES[x]["name"]
            except (ImportError, KeyError):
                # Alternativne vrijednosti ako konstante nisu dostupne
                room_type_options = ["living_room", "bedroom", "kitchen", "bathroom", "office", "meeting_room"]
                room_type_format = lambda x: x.replace("_", " ").title()
            
            selected_room_type = st.selectbox(
                "Tip prostorije",
                options=room_type_options,
                format_func=room_type_format,
                key="new_room_type"
            )
        
        # Dodavanje nove prostorije u listu
        if st.button("Dodaj prostoriju", key="add_room_button"):
            if new_room_name and new_room_area > 0:
                try:
                    # Dohvaćanje stope ventilacije iz ROOM_TYPES
                    from modules.thermal.ventilation.ventilation_recovery.constants import ROOM_TYPES
                    supply_rate = ROOM_TYPES[selected_room_type].get("supply_rate", 0)
                    extract_rate = ROOM_TYPES[selected_room_type].get("extract_rate", 0)
                    description = ROOM_TYPES[selected_room_type].get("name", selected_room_type)
                except (ImportError, KeyError):
                    # Alternativne vrijednosti ako konstante nisu dostupne
                    supply_rate = 3.0
                    extract_rate = 3.0
                    description = selected_room_type.replace("_", " ").title()
                
                room_data = {
                    "name": new_room_name,
                    "area": new_room_area,
                    "height": new_room_height,
                    "type": selected_room_type,
                    "supply_rate": supply_rate,
                    "extract_rate": extract_rate,
                    "supply_flow": new_room_area * supply_rate,
                    "extract_flow": new_room_area * extract_rate,
                    "description": description
                }
                data["rooms"].append(room_data)
                st.rerun()
    
    # Prikaz i uređivanje postojećih prostorija
    if data.get("rooms"):
        st.subheader("Popis prostorija")
        
        # Stvaranje DataFrame-a za tabelu
        rooms_df = pd.DataFrame(data["rooms"])
        
        # Samo prikazi najvažnije stupce
        display_columns = ["name", "area", "height", "description", "supply_rate", "extract_rate"]
        display_columns = [col for col in display_columns if col in rooms_df.columns]
        
        if not display_columns:
            st.warning("Nema podataka za prikaz.")
            return
            
        edited_df = st.data_editor(
            rooms_df[display_columns],
            column_config={
                "name": "Naziv",
                "area": st.column_config.NumberColumn("Površina [m²]", min_value=0.1, step=0.1),
                "height": st.column_config.NumberColumn("Visina [m]", min_value=2.0, max_value=10.0, step=0.1),
                "description": "Tip prostorije",
                "supply_rate": st.column_config.NumberColumn("Dotok zraka [m³/h/m²]", min_value=0.0, step=0.1),
                "extract_rate": st.column_config.NumberColumn("Odsis zraka [m³/h/m²]", min_value=0.0, step=0.1)
            },
            hide_index=True,
            num_rows="dynamic",
            key="rooms_editor"
        )
        
        # Ažuriranje podataka ako su promijenjeni
        if not edited_df.equals(rooms_df[display_columns]):
            # Merge changes back to the original dataframe
            for idx, row in edited_df.iterrows():
                for col in display_columns:
                    if idx < len(data["rooms"]):
                        data["rooms"][idx][col] = row[col]
        
        # Izračun protoka zraka za svaku prostoriju
        if st.button("Izračunaj protok zraka", key="calculate_room_flow"):
            total_supply = 0
            total_extract = 0
            
            for i, room in enumerate(data["rooms"]):
                # Izračun protoka dobavnog zraka
                supply_flow = room["area"] * room["supply_rate"]
                data["rooms"][i]["supply_flow"] = supply_flow
                total_supply += supply_flow
                
                # Izračun protoka odsisnog zraka
                extract_flow = room["area"] * room["extract_rate"]
                data["rooms"][i]["extract_flow"] = extract_flow
                total_extract += extract_flow
            
            # Uzimamo maksimalnu vrijednost između dobave i odsisa za balansiran sustav
            data["final_flow"] = max(total_supply, total_extract)
            st.success(f"Izračunat ukupni protok zraka: {data['final_flow']:.1f} m³/h")
            
            # Prikaz izračunatih protoka po prostoriji
            flow_df = pd.DataFrame([{
                "Prostorija": room["name"],
                "Dobava [m³/h]": room["supply_flow"],
                "Odsis [m³/h]": room["extract_flow"]
            } for room in data["rooms"]])
            
            st.subheader("Izračunati protoci po prostorijama")
            st.dataframe(flow_df, hide_index=True)
    else:
        st.info("Dodajte prostorije za izračun protoka zraka.")

def render_by_people_calculation(data, basic_info):
    """Prikazuje sučelje za izračun protoka prema broju osoba."""
    st.subheader("Izračun protoka prema broju osoba")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data["number_of_people"] = st.number_input(
            "Broj osoba",
            min_value=1,
            max_value=1000,
            value=data.get("number_of_people", basic_info.get("occupants", 4)),
            step=1,
            help="Unesite ukupan broj osoba"
        )
        
        activity_levels = {
            "sedentary": "Sjedeće aktivnosti",
            "light": "Lagane aktivnosti",
            "moderate": "Umjerene aktivnosti",
            "heavy": "Teške aktivnosti"
        }
        
        data["activity_level"] = st.selectbox(
            "Razina aktivnosti",
            options=list(activity_levels.keys()),
            format_func=lambda x: activity_levels.get(x, x),
            index=list(activity_levels.keys()).index(data.get("activity_level", "light")) 
                if data.get("activity_level") in activity_levels else 1,
            help="Odaberite razinu fizičke aktivnosti osoba"
        )
    
    with col2:
        # Stopa ventilacije po osobi (m³/h/osobi)
        try:
            from modules.thermal.ventilation.ventilation_recovery.constants import VENTILATION_RATES
            ventilation_rates = VENTILATION_RATES.get("by_person", {})
            default_rate = ventilation_rates.get(data.get("activity_level", "light"), 30.0)
        except (ImportError, KeyError, AttributeError):
            ventilation_rates = {
                "sedentary": 25.0,
                "light": 30.0,
                "moderate": 35.0,
                "heavy": 45.0
            }
            default_rate = ventilation_rates.get(data.get("activity_level", "light"), 30.0)
        
        data["ventilation_rate_per_person"] = st.number_input(
            "Stopa ventilacije po osobi [m³/h/osobi]",
            min_value=5.0,
            max_value=100.0,
            value=data.get("ventilation_rate_per_person", default_rate),
            step=1.0,
            help="Preporučena stopa izmjene zraka po osobi"
        )
    
    # Izračun protoka
    if st.button("Izračunaj protok zraka", key="calculate_people_flow"):
        flow_rate = data["number_of_people"] * data["ventilation_rate_per_person"]
        data["final_flow"] = flow_rate
        st.success(f"Izračunat protok zraka: {flow_rate:.1f} m³/h")
        
        # Dodatne informacije
        st.info(f"Izračun: {data['number_of_people']} osoba × {data['ventilation_rate_per_person']:.1f} m³/h/osobi = {flow_rate:.1f} m³/h")

def render_by_area_calculation(data, basic_info):
    """Prikazuje sučelje za izračun protoka prema površini prostora."""
    st.subheader("Izračun protoka prema površini prostora")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data["total_area"] = st.number_input(
            "Ukupna površina [m²]",
            min_value=1.0,
            max_value=10000.0,
            value=data.get("total_area", basic_info.get("area", 100.0)),
            step=1.0,
            help="Unesite ukupnu površinu prostora"
        )
        
        data["ceiling_height"] = st.number_input(
            "Visina stropa [m]",
            min_value=2.0,
            max_value=10.0,
            value=data.get("ceiling_height", basic_info.get("height", 2.6)),
            step=0.1,
            help="Unesite prosječnu visinu stropa"
        )
    
    with col2:
        building_types = {
            "residential": "Stambeni prostor",
            "office": "Uredski prostor",
            "retail": "Trgovački prostor",
            "school": "Obrazovna ustanova",
            "healthcare": "Zdravstvena ustanova",
            "industrial": "Industrijski prostor"
        }
        
        data["building_type"] = st.selectbox(
            "Tip prostora",
            options=list(building_types.keys()),
            format_func=lambda x: building_types.get(x, x),
            index=list(building_types.keys()).index(data.get("building_type", "office")) 
                if data.get("building_type") in building_types else 1,
            help="Odaberite tip prostora za određivanje stope ventilacije"
        )
        
        # Stopa ventilacije po površini (m³/h/m²)
        try:
            from modules.thermal.ventilation.ventilation_recovery.constants import VENTILATION_RATES
            ventilation_rates = VENTILATION_RATES.get("by_area", {})
            default_rate = ventilation_rates.get(data.get("building_type", "office"), 3.0)
        except (ImportError, KeyError, AttributeError):
            ventilation_rates = {
                "residential": 2.0,
                "office": 3.0,
                "retail": 4.0,
                "school": 5.0,
                "healthcare": 6.0,
                "industrial": 4.0
            }
            default_rate = ventilation_rates.get(data.get("building_type", "office"), 3.0)
        
        data["ventilation_rate_per_area"] = st.number_input(
            "Stopa ventilacije po površini [m³/h/m²]",
            min_value=0.5,
            max_value=20.0,
            value=data.get("ventilation_rate_per_area", default_rate),
            step=0.1,
            help="Preporučena stopa izmjene zraka po jedinici površine"
        )
    
    # Izračun protoka
    if st.button("Izračunaj protok zraka", key="calculate_area_flow"):
        flow_rate = data["total_area"] * data["ventilation_rate_per_area"]
        data["final_flow"] = flow_rate
        st.success(f"Izračunat protok zraka: {flow_rate:.1f} m³/h")
        
        # Izračun broja izmjena zraka na sat (ACH)
        volume = data["total_area"] * data["ceiling_height"]
        ach = flow_rate / volume
        st.info(f"Broj izmjena zraka na sat: {ach:.2f} ACH")
        st.info(f"Izračun: {data['total_area']:.1f} m² × {data['ventilation_rate_per_area']:.1f} m³/h/m² = {flow_rate:.1f} m³/h")

def render_manual_calculation(data):
    """Prikazuje sučelje za ručni unos protoka zraka."""
    st.subheader("Ručni unos protoka zraka")
    
    data["final_flow"] = st.number_input(
        "Protok zraka [m³/h]",
        min_value=10.0,
        max_value=10000.0,
        value=data.get("final_flow", 150.0),
        step=10.0,
        help="Unesite ručno izračunat ili zahtijevani protok zraka"
    )
    
    # Možda dodati neka dodatna objašnjenja
    st.info("Ručno uneseni protok koristit će se za daljnje proračune ventilacijskog sustava.")