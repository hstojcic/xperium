# modules/thermal/ventilation/ventilation_recovery/ui/recuperator_ui.py

"""
UI components for the recuperator tab of the ventilation recovery calculator.
"""

import streamlit as st
import pandas as pd
from modules.thermal.ventilation.ventilation_recovery.models_database import (
    get_all_series,
    find_suitable_models,
    get_model_by_name
)
from modules.thermal.ventilation.ventilation_recovery.heater_sizing import (
    calculate_heater_power as calc_heater_power,
    calculate_final_heater_power,
    select_standard_heater_power
)

def render_recuperator_tab(calculator):
    """Prikazuje tab za rekuperator i električni grijač."""
    st.header("Odabir rekuperatora i dimenzioniranje grijača")
    
    data = st.session_state.ventilation_recovery_data["recuperator"]
    heater_data = st.session_state.ventilation_recovery_data["heater"]
    airflow_data = st.session_state.ventilation_recovery_data["airflow"]
    ducts_data = st.session_state.ventilation_recovery_data["ducts"]
    basic_info = st.session_state.ventilation_recovery_data["basic_info"]
    
    # Provjera je li izračunat protok zraka
    if airflow_data.get("final_flow", 0) <= 0:
        st.warning("Prije odabira rekuperatora potrebno je izračunati protok zraka u koraku 'Protok zraka'.")
        return
    
    # Izračunati parametri
    total_flow = airflow_data.get("final_flow", 0)
    total_pressure = ducts_data.get("total_pressure_drop", 0)
    
    # Prikaz potrebnog protoka i tlaka
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Potreban protok zraka", f"{total_flow:.1f} m³/h")
    with col2:
        st.metric("Potreban vanjski tlak", f"{total_pressure:.1f} Pa")
    
    # Dodavanje faktora sigurnosti
    safety_factor = st.slider(
        "Faktor sigurnosti za dimenzioniranje", 
        min_value=1.0, 
        max_value=1.5, 
        value=1.15, 
        step=0.05,
        help="Preporučuje se dodati 10-15% rezerve na izračunati potrebni protok"
    )
    
    design_flow = total_flow * safety_factor
    
    # Odabir serije rekuperatora
    st.subheader("Odabir Mitsubishi Lossnay rekuperatora")
    series_options = ["Sve serije"] + get_all_series()
    selected_series = st.selectbox("Odaberite seriju rekuperatora", series_options)
    
    # Dohvaćanje svih modela koji zadovoljavaju protok (bez obzira na tlak)
    all_models_in_series = find_suitable_models(design_flow, 0)
    
    # Pronalazimo odgovarajuće modele
    if selected_series == "Sve serije":
        suitable_models = find_suitable_models(design_flow, total_pressure)
        # Filtriramo modele koji nisu prikladni zbog tlaka, ali zadovoljavaju protok
        unsuitable_models = [m for m in all_models_in_series if m not in suitable_models]
    else:
        # Filtriramo samo modele iz odabrane serije
        all_models_in_series = [m for m in all_models_in_series if m.get("series") == selected_series]
        suitable_models = [m for m in all_models_in_series if m in find_suitable_models(design_flow, total_pressure)]
        unsuitable_models = [m for m in all_models_in_series if m not in suitable_models]
    
    # Prikaz prikladnih modela
    if suitable_models:
        st.success(f"Pronađeno {len(suitable_models)} odgovarajućih modela.")
        
        # Stvaramo tablicu prikladnih modela
        model_data = []
        for model in suitable_models:
            if not model:
                continue
                
            flow_pct = (design_flow / model.get("flow_capacity", 1)) * 100 if model.get("flow_capacity", 0) > 0 else 0
            
            # Određujemo raspoloživi tlak
            if isinstance(model.get("max_pressure"), dict):
                pressure_value = model["max_pressure"].get("supply", 0)  # Uzimamo vrijednost za dovod
                pressure_display = f"{model['max_pressure'].get('supply', 0)}/{model['max_pressure'].get('extract', 0)} Pa"
            else:
                pressure_value = model.get("max_pressure", 0)
                pressure_display = f"{model.get('max_pressure', 0)} Pa"
            
            pressure_margin = pressure_value - total_pressure
            pressure_margin_pct = (pressure_margin / pressure_value) * 100 if pressure_value > 0 else 0
            
            model_data.append({
                "Model": model.get("model", ""),
                "Serija": model.get("series", ""),
                "Protok [m³/h]": f"{model.get('flow_capacity', 0)} ({flow_pct:.1f}%)",
                "Tlak [Pa]": f"{pressure_display} ({pressure_margin_pct:.1f}% rezerve)",
                "Učinkovitost": f"{model.get('efficiency', 0)*100:.1f}%",
                "Priključci [mm]": model.get("connections", "")
            })
        
        # Prikazujemo tablicu
        st.table(pd.DataFrame(model_data))
        
        # Odabir modela
        model_names = [model.get("model", "") for model in suitable_models if model]
        if model_names:
            selected_model_name = st.selectbox(
                "Odaberite rekuperator", 
                options=model_names,
                index=0
            )
            
            if st.button("Odaberi rekuperator"):
                # Pronalazimo odabrani model
                selected_model = next((m for m in suitable_models if m.get("model") == selected_model_name), None)
                
                if selected_model:
                    # Ažuriramo podatke o rekuperatoru
                    data["selected_model"] = selected_model.get("model", "")
                    data["series"] = selected_model.get("series", "")
                    data["efficiency"] = selected_model.get("efficiency", 0.75)
                    data["flow_capacity"] = selected_model.get("flow_capacity", 0)
                    
                    # Postavljamo raspoloživi tlak
                    if isinstance(selected_model.get("max_pressure"), dict):
                        data["pressure_capacity"] = selected_model["max_pressure"].get("supply", 0)  # Uzimamo vrijednost za dovod
                    else:
                        data["pressure_capacity"] = selected_model.get("max_pressure", 0)
                    
                    data["load_percentage"] = (design_flow / selected_model.get("flow_capacity", 1)) * 100 if selected_model.get("flow_capacity", 0) > 0 else 0
                    data["connections"] = selected_model.get("connections", "")
                    
                    # Dohvaćamo promjer priključka iz stringa
                    try:
                        if "Ø" in selected_model.get("connections", ""):
                            diameter_str = selected_model.get("connections", "").split("Ø")[1].split()[0]
                            diameter = int(float(diameter_str))
                            data["diameter"] = diameter
                        elif "diameter" in selected_model:
                            data["diameter"] = selected_model["diameter"]
                        else:
                            data["diameter"] = 0
                    except (ValueError, IndexError):
                        data["diameter"] = 0
                    
                    # Izračun snage grijača nakon odabira rekuperatora
                    calculator.calculate_heater_power()
                    
                    st.success(f"Uspješno odabran rekuperator {selected_model.get('model', '')}!")
                    st.rerun()
    else:
        st.warning(f"Nije pronađen odgovarajući model za tražene uvjete (protok {design_flow:.1f} m³/h, tlak {total_pressure:.1f} Pa).")
    
    # Prikaz neadekvatnih modela
    if unsuitable_models:
        with st.expander("Prikaži neadekvatne modele"):
            st.warning(f"Sljedeći modeli zadovoljavaju uvjet protoka, ali ne i tlaka:")
            
            unsuitable_data = []
            for model in unsuitable_models:
                if not model:
                    continue
                    
                if isinstance(model.get("max_pressure"), dict):
                    pressure_display = f"{model['max_pressure'].get('supply', 0)}/{model['max_pressure'].get('extract', 0)} Pa"
                    pressure_value = model['max_pressure'].get('supply', 0)
                else:
                    pressure_value = model.get("max_pressure", 0)
                    pressure_display = f"{pressure_value} Pa"
                
                missing_pressure = max(0, total_pressure - pressure_value)
                
                unsuitable_data.append({
                    "Model": model.get("model", ""),
                    "Serija": model.get("series", ""),
                    "Protok [m³/h]": model.get("flow_capacity", 0),
                    "Tlak [Pa]": pressure_display,
                    "Nedostaje": f"{missing_pressure} Pa"
                })
            
            st.table(pd.DataFrame(unsuitable_data))
    
    # Prikaz detalja o odabranom rekuperatoru
    if data.get("selected_model"):
        st.subheader("Odabrani rekuperator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Model", data.get("selected_model", ""))
            st.metric("Serija", data.get("series", ""))
        
        with col2:
            st.metric("Učinkovitost", f"{data.get('efficiency', 0)*100:.1f}%")
            st.metric("Protok", f"{data.get('flow_capacity', 0)} m³/h")
        
        if data.get("load_percentage", 0) > 0:
            delta = f"{data.get('load_percentage', 0)-100:.1f}%" if data.get('load_percentage', 0) > 100 else None
            st.metric("Opterećenje", f"{data.get('load_percentage', 0):.1f}%", delta=delta)
            
        st.metric("Raspoloživi tlak", f"{data.get('pressure_capacity', 0)} Pa")
        st.metric("Priključci", data.get("connections", ""))
        
        # Dimenzioniranje grijača
        st.subheader("Dimenzioniranje električnog grijača")
        
        # Temperaturni parametri
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Vanjska projektna temperatura", f"{basic_info.get('temperatures', {}).get('outdoor', -20):.1f} °C")
            st.metric("Temperatura nakon rekuperatora", f"{heater_data.get('temperature_after_recuperator', 0):.1f} °C")
        
        with col2:
            st.metric("Unutarnja temperatura", f"{basic_info.get('temperatures', {}).get('indoor', 20):.1f} °C")
            heater_data["target_temperature"] = st.number_input(
                "Ciljna temperatura nakon grijača [°C]",
                min_value=-10.0,
                max_value=30.0,
                value=heater_data.get("target_temperature", 2.0),
                step=1.0,
                help="Preporučena temperatura je 2-5°C za sprečavanje kondenzacije"
            )
        
        # Izračun snage grijača
        if st.button("Izračunaj snagu grijača"):
            calculator.calculate_heater_power()
            st.rerun()
        
        # Faktor sigurnosti za grijač
        heater_data["safety_factor"] = st.slider(
            "Faktor sigurnosti za grijač",
            min_value=1.0,
            max_value=1.5,
            value=heater_data.get("safety_factor", 1.15),
            step=0.05,
            help="Preporučuje se dodati 10-15% na teorijski potrebnu snagu"
        )
        
        # Prikaz rezultata dimenzioniranja grijača
        if heater_data.get("required_power", 0) > 0:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Potrebna snaga", f"{heater_data.get('required_power', 0):.2f} kW")
            
            with col2:
                st.metric("Snaga s faktorom sigurnosti", f"{heater_data.get('final_power', 0):.2f} kW")
            
            with col3:
                st.metric("Standardna snaga", f"{heater_data.get('standard_power', 0):.2f} kW")
        elif heater_data.get("temperature_after_recuperator", 0) > heater_data.get("target_temperature", 0):
            st.success("Grijač nije potreban jer je temperatura nakon rekuperatora već viša od ciljne temperature.")
        else:
            st.info("Kliknite na 'Izračunaj snagu grijača' za dimenzioniranje grijača.")
    
    # Ažuriranje podataka u session_state
    st.session_state.ventilation_recovery_data["recuperator"] = data
    st.session_state.ventilation_recovery_data["heater"] = heater_data
    calculator.mark_as_changed()

def calculate_heater_power(calculator):
    """Izračunava potrebnu snagu električnog grijača."""
    recuperator_data = st.session_state.ventilation_recovery_data["recuperator"]
    heater_data = st.session_state.ventilation_recovery_data["heater"]
    basic_info = st.session_state.ventilation_recovery_data["basic_info"]
    airflow_data = st.session_state.ventilation_recovery_data["airflow"]
    
    # Dohvaćamo potrebne parametre
    flow_rate = airflow_data.get("final_flow", 0)  # m³/h
    outdoor_temp = basic_info.get("temperatures", {}).get("outdoor", -20)  # °C
    indoor_temp = basic_info.get("temperatures", {}).get("indoor", 20)  # °C
    recuperator_efficiency = recuperator_data.get("efficiency", 0.75)  # decimalni broj (0-1)
    target_temp = heater_data.get("target_temperature", 2)  # °C
    
    # Izračun snage grijača i temperature nakon rekuperatora
    power, temp_after_recuperator = calc_heater_power(
        flow_rate, 
        outdoor_temp, 
        indoor_temp, 
        target_temp, 
        recuperator_efficiency
    )
    
    # Ažuriranje vrijednosti
    heater_data["required_power"] = round(power / 1000, 2)  # kW
    heater_data["temperature_after_recuperator"] = round(temp_after_recuperator, 1)  # °C
    
    # Konačna snaga s faktorom sigurnosti
    final_power = calculate_final_heater_power(power, heater_data.get("safety_factor", 1.15))
    heater_data["final_power"] = round(final_power, 2)  # kW
    
    # Odabir standardne snage
    standard_power = select_standard_heater_power(final_power / 1000)
    heater_data["standard_power"] = standard_power  # kW
    
    # Ažuriranje podataka u session_state
    st.session_state.ventilation_recovery_data["heater"] = heater_data