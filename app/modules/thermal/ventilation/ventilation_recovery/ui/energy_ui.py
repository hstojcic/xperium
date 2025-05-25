# modules/thermal/ventilation/ventilation_recovery/ui/energy_ui.py

import streamlit as st
from modules.thermal.ventilation.ventilation_recovery.energy_analysis import (
    calculate_electricity_consumption,
    calculate_heater_consumption,
    calculate_cost_savings,
    calculate_payback_period,
    calculate_co2_reduction
)
from modules.thermal.ventilation.ventilation_recovery.heat_recovery import (
    calculate_annual_energy_savings
)

def render_energy_tab(calculator):
    """Prikazuje tab za energetsku analizu."""
    st.header("Energetska analiza")
    
    data = st.session_state.ventilation_recovery_data["energy"]
    recuperator_data = st.session_state.ventilation_recovery_data["recuperator"]
    heater_data = st.session_state.ventilation_recovery_data["heater"]
    basic_info = st.session_state.ventilation_recovery_data["basic_info"]
    airflow_data = st.session_state.ventilation_recovery_data["airflow"]
    
    # Provjera je li odabran rekuperator
    if not recuperator_data.get("selected_model"):
        st.warning("Prije energetske analize potrebno je odabrati rekuperator u koraku 'Rekuperator i grijač'.")
        return
    
    # Parametri za energetsku analizu
    st.subheader("Parametri za izračun")
    
    col1, col2 = st.columns(2)
    
    with col1:
        location_type = st.radio(
            "Lokacija objekta",
            options=["Kontinentalna Hrvatska", "Primorska Hrvatska"],
            index=0 if data.get("location_type", "continental") == "continental" else 1,
            help="Lokacija utječe na klimatske uvjete i stupanj-dane grijanja"
        )
        
        energy_price = st.number_input(
            "Cijena toplinske energije [€/kWh]",
            min_value=0.01,
            max_value=0.5,
            value=data.get("energy_price", 0.15),
            step=0.01,
            help="Prosječna cijena energije za grijanje (ovisi o energentu)"
        )
        
        electricity_price = st.number_input(
            "Cijena električne energije [€/kWh]",
            min_value=0.05,
            max_value=0.5,
            value=data.get("electricity_price", 0.18),
            step=0.01,
            help="Cijena električne energije za pogon rekuperatora i grijača"
        )
    
    with col2:
        daily_operation = st.number_input(
            "Dnevni rad sustava [h/dan]",
            min_value=1,
            max_value=24,
            value=data.get("daily_operation", 12),
            step=1,
            help="Prosječni dnevni broj sati rada ventilacijskog sustava"
        )
        
        yearly_operation = st.number_input(
            "Godišnji rad sustava [dana/god]",
            min_value=1,
            max_value=365,
            value=data.get("yearly_operation", 300),
            step=10,
            help="Broj dana rada ventilacijskog sustava u godini"
        )
        
        investment_cost = st.number_input(
            "Trošak investicije [€]",
            min_value=0,
            max_value=100000,
            value=data.get("investment_cost", 5000),
            step=500,
            help="Ukupni trošak investicije u ventilacijski sustav s rekuperacijom"
        )
        
    # Spremi parametre
    data["location_type"] = "continental" if location_type == "Kontinentalna Hrvatska" else "coastal"
    data["energy_price"] = energy_price
    data["electricity_price"] = electricity_price
    data["daily_operation"] = daily_operation
    data["yearly_operation"] = yearly_operation
    data["investment_cost"] = investment_cost
    
    # Izračun ukupnog godišnjeg broja sati rada
    operation_hours = daily_operation * yearly_operation
    
    # Gumb za izračun energetske analize
    if st.button("Izračunaj energetske uštede"):
        try:
            # Dohvaćamo potrebne parametre
            flow_rate = airflow_data.get("final_flow", 0)  # m³/h
            recuperator_efficiency = recuperator_data.get("efficiency", 0.75)  # decimalni broj (0-1)
            
            # Izračun godišnje uštede energije
            annual_savings = calculate_annual_energy_savings(
                flow_rate, 
                recuperator_efficiency,
                data["location_type"],
                operation_hours
            )
            data["annual_savings"] = annual_savings
            
            # Izračun potrošnje električne energije rekuperatora
            if recuperator_data.get("selected_model"):
                electricity_consumption = calculate_electricity_consumption(
                    recuperator_data["selected_model"],
                    operation_hours
                )
            else:
                electricity_consumption = 0
            data["electricity_consumption"] = electricity_consumption
            
            # Izračun potrošnje grijača
            if heater_data.get("standard_power", 0) > 0:
                location_degree_days = 2800 if data["location_type"] == "continental" else 1500
                heater_consumption = calculate_heater_consumption(
                    heater_data["standard_power"], 
                    basic_info["temperatures"].get("outdoor", -15),
                    heater_data.get("target_temperature", 2),
                    operation_hours, 
                    location_degree_days
                )
            else:
                heater_consumption = 0
            data["heater_consumption"] = heater_consumption
            
            # Izračun financijske uštede
            annual_cost_savings = calculate_cost_savings(
                annual_savings,
                electricity_consumption,
                heater_consumption,
                energy_price,
                electricity_price
            )
            data["annual_cost_savings"] = annual_cost_savings
            
            # Izračun perioda povrata investicije
            payback_period = calculate_payback_period(
                investment_cost,
                annual_cost_savings
            )
            data["payback_period"] = payback_period
            
            # Izračun smanjenja emisije CO2
            co2_reduction = calculate_co2_reduction(
                annual_savings,
                electricity_consumption,
                heater_consumption
            )
            data["co2_reduction"] = co2_reduction
            
            st.success("Energetska analiza uspješno izračunata!")
        except Exception as e:
            st.error(f"Greška prilikom izračuna energetske analize: {e}")
    
    # Prikaz rezultata ako postoje
    if data.get("annual_savings", 0) > 0:
        st.subheader("Rezultati energetske analize")
        
        # Energetske uštede
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Godišnja ušteda energije", f"{data['annual_savings']:.0f} kWh/god")
            st.metric("Potrošnja električne energije rekuperatora", f"{data['electricity_consumption']:.0f} kWh/god")
            
        with col2:
            st.metric("Potrošnja električnog grijača", f"{data['heater_consumption']:.0f} kWh/god")
            st.metric("Godišnja financijska ušteda", f"{data['annual_cost_savings']:.0f} €/god")
        
        # Period povrata investicije
        if data.get("payback_period", 0) > 50:
            st.warning("Period povrata investicije: Više od 50 godina")
        else:
            st.success(f"Period povrata investicije: {data['payback_period']:.1f} godina")
        
        # Ekološki učinak
        st.metric("Smanjenje emisije CO₂", f"{data['co2_reduction']:.0f} kg/god")
        
        # Vizualizacija energetskih tokova
        st.subheader("Energetski tokovi")
        st.info("Ovdje bi se mogla dodati vizualizacija energetskih tokova i ušteda...")
    
    # Ažuriranje podataka u session_state
    st.session_state.ventilation_recovery_data["energy"] = data
    calculator.mark_as_changed()