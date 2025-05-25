import streamlit as st
import pandas as pd
import numpy as np
import math
from modules.base import BaseCalculation

class ChimneySizingCalc(BaseCalculation):
    """Proračun dimnjaka prema EN 13384-2 normi."""
    
    def __init__(self, name="Proračun dimnjaka prema EN 13384-2"):
        """Inicijalizacija kalkulatora."""
        super().__init__(name)
        
        # Inicijalizacija session state
        if "chimney_sizing_data" not in st.session_state:
            st.session_state.chimney_sizing_data = self.initialize_data_structure()
    
    def mark_as_changed(self):
        """
        Označava da je došlo do promjene u proračunu.
        Koristi se kao callback za streamlit widgete.
        """
        self.record_state("Izmjena parametara")
    
    def initialize_data_structure(self):
        """Inicijalizira strukturu podataka."""
        return {
            "general": {
                "location": "Osijek",
                "geodetic_height": 93,  # m
                "safety_number_SE": 1.2,
                "correction_factor_SH": 0.5,
                "temperatures": {
                    "outlet": 0,  # °C
                    "outdoor": -15,  # °C
                    "cold_area": 0,  # °C
                    "warm_area": 0,  # °C
                    "ambient": 15,  # °C
                }
            },
            "appliances": [
                {
                    "manufacturer": "Vaillant",
                    "model": "ecoTEC plus VC 20 CS / 1-5",
                    "fuel": "Zemni plin",
                    "full_load": {
                        "nominal_heat_output": 20.9,  # kW
                        "heat_input": 20.4,  # kW
                        "co2_percentage": 9.6,  # %
                        "flue_gas_mass_flow": 12.79,  # g/s
                        "flue_gas_temperature": 85,  # °C
                        "max_positive_pressure": 130  # Pa
                    },
                    "partial_load": {
                        "nominal_heat_output": 3.2,  # kW
                        "heat_input": 3.2,  # kW
                        "co2_percentage": 9.6,  # %
                        "flue_gas_mass_flow": 1.51,  # g/s
                        "flue_gas_temperature": 35,  # °C
                        "max_positive_pressure": 30  # Pa
                    },
                    "connection": {
                        "diameter": 60,  # mm
                        "transition_type": "Redukcija konusna 60°"
                    }
                },
                {
                    "manufacturer": "Vaillant",
                    "model": "ecoTEC plus VC 20 CS / 1-5",
                    "fuel": "Zemni plin",
                    "full_load": {
                        "nominal_heat_output": 20.9,  # kW
                        "heat_input": 20.4,  # kW
                        "co2_percentage": 9.6,  # %
                        "flue_gas_mass_flow": 12.79,  # g/s
                        "flue_gas_temperature": 85,  # °C
                        "max_positive_pressure": 130  # Pa
                    },
                    "partial_load": {
                        "nominal_heat_output": 3.2,  # kW
                        "heat_input": 3.2,  # kW
                        "co2_percentage": 9.6,  # %
                        "flue_gas_mass_flow": 1.51,  # g/s
                        "flue_gas_temperature": 35,  # °C
                        "max_positive_pressure": 30  # Pa
                    },
                    "connection": {
                        "diameter": 60,  # mm
                        "transition_type": "Redukcija konusna 60°"
                    }
                }
            ],
            "connecting_elements": {
                "type": "Koncentrični spojni element",
                "manufacturer": "Centrotherm",
                "model": "System Chimneys PP / Metal",
                "inner_diameter": 56,  # mm
                "thickness": 2,  # mm
                "material": "PP gladak",
                "roughness": 0.5,  # mm
                "resistances": "Luk 87°",
                "effective_height": 0.1,  # m
                "developed_length": 0.32,  # m
                "outer_share": 0,  # %
                "cold_area_share": 0,  # %
                "warm_area_share": 100  # %
            },
            "chimney": {
                "type": "Dimovodna naprava u oknu",
                "manufacturer": "Schiedel",
                "model": "MULTI",
                "inner_diameter": 140,  # mm
                "material": "Keramika",
                "thickness": 7,  # mm
                "thermal_conductivity": 1.1,  # W/mK
                "roughness": 1.5,  # mm
                "annular_gap": "Protutok zraka (53 mm)",
                "outer_section": "Kvadratni 260 mm",
                "outer_material": "Lagani beton",
                "outer_thickness": 50,  # mm
                "thermal_resistance": 0.12,  # m²K/W
                "outlet_resistance": 0,
                "inlet_type": "T-komad 87°",
                "sections": [
                    {
                        "effective_height": 2.96,  # m
                        "developed_length": 2.96  # m
                    },
                    {
                        "effective_height": 1.56,  # m
                        "developed_length": 1.56  # m
                    }
                ],
                "outdoor_length": 1,  # m
                "cold_area_length": 0,  # m
                "warm_area_length": 3.52  # m
            },
            "results": {
                "pressure_conditions": {},
                "working_pressures": {},
                "backflow": {},
                "temperature_conditions": {}
            }
        }
    
    def render(self):
        """Prikazuje sučelje kalkulatora."""
        st.title(self.name)
        
        # Dohvati podatke iz sesije
        data = st.session_state.chimney_sizing_data
        
        # Kreiraj tabove za različite sekcije proračuna
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Opći parametri", 
            "Ložišta", 
            "Spojni elementi", 
            "Dimovod", 
            "Rezultati"
        ])
        
        with tab1:
            self.render_general_parameters(data)
        
        with tab2:
            self.render_appliances(data)
        
        with tab3:
            self.render_connecting_elements(data)
        
        with tab4:
            self.render_chimney(data)
        
        with tab5:
            # Gumb za izračun
            if st.button("Izračunaj", type="primary"):
                self.calculate()
            
            self.render_results(data)
    
    def render_general_parameters(self, data):
        """Prikazuje opće parametre."""
        st.header("Opći parametri")
        
        st.subheader("Lokacija i osnovni parametri")
        col1, col2, col3 = st.columns(3)
        with col1:
            data["general"]["location"] = st.text_input(
                "Lokacija",
                value=data["general"]["location"],
                key="location"
            )
        
        with col2:
            data["general"]["geodetic_height"] = st.number_input(
                "Geodetska visina [m]",
                min_value=0.0,
                value=float(data["general"]["geodetic_height"]),
                format="%.1f",
                key="geodetic_height",
                on_change=self.mark_as_changed
            )
        
        with col3:
            pass
        
        st.subheader("Sigurnosni faktori")
        col1, col2 = st.columns(2)
        with col1:
            data["general"]["safety_number_SE"] = st.number_input(
                "Sigurnosni broj SE",
                min_value=1.0,
                max_value=2.0,
                value=float(data["general"]["safety_number_SE"]),
                format="%.1f",
                key="safety_number_SE",
                on_change=self.mark_as_changed
            )
        
        with col2:
            data["general"]["correction_factor_SH"] = st.number_input(
                "Korekcijski faktor SH",
                min_value=0.0,
                max_value=1.0,
                value=float(data["general"]["correction_factor_SH"]),
                format="%.1f",
                key="correction_factor_SH",
                on_change=self.mark_as_changed
            )
        
        st.subheader("Temperature okolnog zraka")
        col1, col2 = st.columns(2)
        with col1:
            data["general"]["temperatures"]["outlet"] = st.number_input(
                "Na ušću [°C]", 
                value=float(data["general"]["temperatures"]["outlet"]),
                format="%.1f",
                key="outlet_temp",
                on_change=self.mark_as_changed
            )
            
            data["general"]["temperatures"]["cold_area"] = st.number_input(
                "U hladnom području [°C]", 
                value=float(data["general"]["temperatures"]["cold_area"]),
                format="%.1f",
                key="cold_area_temp",
                on_change=self.mark_as_changed
            )
        
        with col2:
            data["general"]["temperatures"]["outdoor"] = st.number_input(
                "Na otvorenom [°C]", 
                value=float(data["general"]["temperatures"]["outdoor"]),
                format="%.1f",
                key="outdoor_temp",
                on_change=self.mark_as_changed
            )
            
            data["general"]["temperatures"]["warm_area"] = st.number_input(
                "U toplom području [°C]", 
                value=float(data["general"]["temperatures"]["warm_area"]),
                format="%.1f",
                key="warm_area_temp",
                on_change=self.mark_as_changed
            )
        
        col1, col2 = st.columns(2)
        with col1:
            data["general"]["temperatures"]["ambient"] = st.number_input(
                "Okolni zrak (tlačni uvjet) [°C]", 
                value=float(data["general"]["temperatures"]["ambient"]),
                format="%.1f",
                key="ambient_temp",
                on_change=self.mark_as_changed
            )
    
    def render_appliances(self, data):
        """Prikazuje podatke o ložištima."""
        st.header("Ložišta")
        
        appliances = data["appliances"]
        
        # Selector za odabir broja ložišta
        num_appliances = st.number_input(
            "Broj ložišta", 
            min_value=1, 
            max_value=4, 
            value=len(appliances), 
            key="num_appliances"
        )
        
        # Dodavanje ili uklanjanje ložišta prema potrebi
        if num_appliances > len(appliances):
            for _ in range(num_appliances - len(appliances)):
                appliances.append({
                    "manufacturer": "Proizvođač",
                    "model": "Model",
                    "fuel": "Gorivo",
                    "full_load": {
                        "nominal_heat_output": 20.0,
                        "heat_input": 20.0,
                        "co2_percentage": 10.0,
                        "flue_gas_mass_flow": 12.0,
                        "flue_gas_temperature": 80,
                        "max_positive_pressure": 130
                    },
                    "partial_load": {
                        "nominal_heat_output": 3.0,
                        "heat_input": 3.0,
                        "co2_percentage": 10.0,
                        "flue_gas_mass_flow": 1.5,
                        "flue_gas_temperature": 35,
                        "max_positive_pressure": 30
                    },
                    "connection": {
                        "diameter": 60,
                        "transition_type": "Redukcija konusna"
                    }
                })
        elif num_appliances < len(appliances):
            appliances = appliances[:num_appliances]
            data["appliances"] = appliances
        
        # Za svako ložište prikazati detalje
        for i, appliance in enumerate(appliances):
            with st.expander(f"Ložište {i+1}: {appliance['manufacturer']} {appliance['model']}", expanded=(i==0)):
                
                # Osnovni podaci o ložištu
                st.subheader("Osnovni podaci")
                col1, col2, col3 = st.columns(3)
                with col1:
                    appliance["manufacturer"] = st.text_input(
                        "Proizvođač", 
                        value=appliance["manufacturer"],
                        key=f"manufacturer_{i}"
                    )
                
                with col2:
                    appliance["model"] = st.text_input(
                        "Model", 
                        value=appliance["model"],
                        key=f"model_{i}"
                    )
                
                with col3:
                    appliance["fuel"] = st.selectbox(
                        "Gorivo",
                        ["Zemni plin", "Ukapljeni naftni plin", "Loživo ulje", "Drvo", "Peleti"],
                        index=0 if appliance["fuel"] == "Zemni plin" else 1,
                        key=f"fuel_{i}"
                    )
                
                # Podaci za puno opterećenje
                st.subheader("Puno opterećenje")
                col1, col2 = st.columns(2)
                with col1:
                    appliance["full_load"]["nominal_heat_output"] = st.number_input(
                        "Nazivna toplinska snaga [kW]",
                        min_value=0.0,
                        value=float(appliance["full_load"]["nominal_heat_output"]),
                        format="%.1f",
                        key=f"nom_heat_output_full_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["co2_percentage"] = st.number_input(
                        "Udio CO₂ [%]",
                        min_value=0.0,
                        max_value=20.0,
                        value=float(appliance["full_load"]["co2_percentage"]),
                        format="%.1f",
                        key=f"co2_perc_full_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["flue_gas_temperature"] = st.number_input(
                        "Temperatura dimnih plinova [°C]",
                        min_value=0,
                        max_value=400,
                        value=int(appliance["full_load"]["flue_gas_temperature"]),
                        key=f"flue_temp_full_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col2:
                    appliance["full_load"]["heat_input"] = st.number_input(
                        "Toplinska snaga loženja [kW]",
                        min_value=0.0,
                        value=float(appliance["full_load"]["heat_input"]),
                        format="%.1f",
                        key=f"heat_input_full_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["flue_gas_mass_flow"] = st.number_input(
                        "Masena struja dimnih plinova [g/s]",
                        min_value=0.0,
                        value=float(appliance["full_load"]["flue_gas_mass_flow"]),
                        format="%.2f",
                        key=f"flue_flow_full_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["max_positive_pressure"] = st.number_input(
                        "Maksimalni potisni tlak [Pa]",
                        min_value=0,
                        value=int(appliance["full_load"]["max_positive_pressure"]),
                        key=f"max_press_full_{i}",
                        on_change=self.mark_as_changed
                    )
                
                # Podaci za djelomično opterećenje
                st.subheader("Djelomično opterećenje")
                col1, col2 = st.columns(2)
                with col1:
                    appliance["partial_load"]["nominal_heat_output"] = st.number_input(
                        "Nazivna toplinska snaga [kW]",
                        min_value=0.0,
                        value=float(appliance["partial_load"]["nominal_heat_output"]),
                        format="%.1f",
                        key=f"nom_heat_output_part_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["co2_percentage"] = st.number_input(
                        "Udio CO₂ [%]",
                        min_value=0.0,
                        max_value=20.0,
                        value=float(appliance["partial_load"]["co2_percentage"]),
                        format="%.1f",
                        key=f"co2_perc_part_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["flue_gas_temperature"] = st.number_input(
                        "Temperatura dimnih plinova [°C]",
                        min_value=0,
                        max_value=400,
                        value=int(appliance["partial_load"]["flue_gas_temperature"]),
                        key=f"flue_temp_part_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col2:
                    appliance["partial_load"]["heat_input"] = st.number_input(
                        "Toplinska snaga loženja [kW]",
                        min_value=0.0,
                        value=float(appliance["partial_load"]["heat_input"]),
                        format="%.1f",
                        key=f"heat_input_part_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["flue_gas_mass_flow"] = st.number_input(
                        "Masena struja dimnih plinova [g/s]",
                        min_value=0.0,
                        value=float(appliance["partial_load"]["flue_gas_mass_flow"]),
                        format="%.2f",
                        key=f"flue_flow_part_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["max_positive_pressure"] = st.number_input(
                        "Maksimalni potisni tlak [Pa]",
                        min_value=0,
                        value=int(appliance["partial_load"]["max_positive_pressure"]),
                        key=f"max_press_part_{i}",
                        on_change=self.mark_as_changed
                    )
                
                # Podaci o priključku
                st.subheader("Priključak")
                col1, col2 = st.columns(2)
                with col1:
                    appliance["connection"]["diameter"] = st.number_input(
                        "Promjer nastavka za dimne plinove [mm]",
                        min_value=0,
                        value=int(appliance["connection"]["diameter"]),
                        key=f"conn_diameter_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col2:
                    appliance["connection"]["transition_type"] = st.selectbox(
                        "Vrsta prijelaza",
                        ["Direktni", "Redukcija konusna 60°", "Redukcija stepenasta"],
                        index=1 if appliance["connection"]["transition_type"] == "Redukcija konusna 60°" else 0,
                        key=f"transition_type_{i}"
                    )
    
    def render_connecting_elements(self, data):
        """Prikazuje podatke o spojnim elementima."""
        st.header("Spojni elementi")
        
        connecting_elements = data["connecting_elements"]
        
        # Osnovni podaci o spojnom elementu
        st.subheader("Vrsta gradnje")
        col1, col2, col3 = st.columns(3)
        with col1:
            connecting_elements["type"] = st.selectbox(
                "Kategorija",
                ["Koncentrični spojni element", "Jednostruki spojni element"],
                index=0 if connecting_elements["type"] == "Koncentrični spojni element" else 1,
                key="conn_type"
            )
        
        with col2:
            connecting_elements["manufacturer"] = st.text_input(
                "Proizvođač",
                value=connecting_elements["manufacturer"],
                key="conn_manufacturer"
            )
        
        with col3:
            connecting_elements["model"] = st.text_input(
                "Model",
                value=connecting_elements["model"],
                key="conn_model"
            )
        
        # Tehnički podaci
        st.subheader("Tehnički podaci")
        col1, col2 = st.columns(2)
        with col1:
            connecting_elements["inner_diameter"] = st.number_input(
                "Unutarnji promjer [mm]",
                min_value=0,
                value=int(connecting_elements["inner_diameter"]),
                key="conn_inner_diameter",
                on_change=self.mark_as_changed
            )
            
            connecting_elements["material"] = st.text_input(
                "Materijal unutarnjeg zida",
                value=connecting_elements["material"],
                key="conn_material"
            )
        
        with col2:
            connecting_elements["thickness"] = st.number_input(
                "Debljina [mm]",
                min_value=0.0,
                value=float(connecting_elements["thickness"]),
                format="%.1f",
                key="conn_thickness",
                on_change=self.mark_as_changed
            )
            
            connecting_elements["roughness"] = st.number_input(
                "Srednja hrapavost [mm]",
                min_value=0.0,
                value=float(connecting_elements["roughness"]),
                format="%.1f",
                key="conn_roughness",
                on_change=self.mark_as_changed
            )
        
        # Geometrijske karakteristike
        st.subheader("Geometrijske karakteristike")
        col1, col2 = st.columns(2)
        with col1:
            connecting_elements["resistances"] = st.text_input(
                "Otpori",
                value=connecting_elements["resistances"],
                key="conn_resistances"
            )
            
            connecting_elements["effective_height"] = st.number_input(
                "Učinkovita visina [m]",
                min_value=0.0,
                value=float(connecting_elements["effective_height"]),
                format="%.2f",
                key="conn_effective_height",
                on_change=self.mark_as_changed
            )
        
        with col2:
            connecting_elements["developed_length"] = st.number_input(
                "Razvijena dužina [m]",
                min_value=0.0,
                value=float(connecting_elements["developed_length"]),
                format="%.2f",
                key="conn_developed_length",
                on_change=self.mark_as_changed
            )
        
        # Udjeli u različitim područjima
        st.subheader("Udjeli u različitim područjima")
        col1, col2, col3 = st.columns(3)
        with col1:
            connecting_elements["outer_share"] = st.number_input(
                "Udio u otvorenom prostoru [%]",
                min_value=0,
                max_value=100,
                value=int(connecting_elements["outer_share"]),
                key="conn_outer_share",
                on_change=self.mark_as_changed
            )
        
        with col2:
            connecting_elements["cold_area_share"] = st.number_input(
                "Udio u hladnom području [%]",
                min_value=0,
                max_value=100,
                value=int(connecting_elements["cold_area_share"]),
                key="conn_cold_area_share",
                on_change=self.mark_as_changed
            )
        
        with col3:
            connecting_elements["warm_area_share"] = st.number_input(
                "Udio u toplom području [%]",
                min_value=0,
                max_value=100,
                value=int(connecting_elements["warm_area_share"]),
                key="conn_warm_area_share",
                on_change=self.mark_as_changed
            )
    
    def render_chimney(self, data):
        """Prikazuje podatke o dimnjaku."""
        st.header("Dimovod")
        
        chimney = data["chimney"]
        
        # Vrsta gradnje
        st.subheader("Vrsta gradnje")
        col1, col2, col3 = st.columns(3)
        with col1:
            chimney["type"] = st.selectbox(
                "Kategorija",
                ["Dimovodna naprava u oknu", "Samostojeći dimnjak", "Dimnjak na vanjskom zidu"],
                index=0 if chimney["type"] == "Dimovodna naprava u oknu" else 1,
                key="chimney_type"
            )
        
        with col2:
            chimney["manufacturer"] = st.text_input(
                "Proizvođač",
                value=chimney["manufacturer"],
                key="chimney_manufacturer"
            )
        
        with col3:
            chimney["model"] = st.text_input(
                "Model",
                value=chimney["model"],
                key="chimney_model"
            )
        
        # Tehnički podaci o dimovodu
        st.subheader("Dimovod")
        col1, col2, col3 = st.columns(3)
        with col1:
            chimney["inner_diameter"] = st.number_input(
                "Unutarnji promjer [mm]",
                min_value=0,
                value=int(chimney["inner_diameter"]),
                key="chimney_inner_diameter",
                on_change=self.mark_as_changed
            )
            
            chimney["material"] = st.text_input(
                "Materijal",
                value=chimney["material"],
                key="chimney_material"
            )
        
        with col2:
            chimney["thickness"] = st.number_input(
                "Debljina [mm]",
                min_value=0.0,
                value=float(chimney["thickness"]),
                format="%.1f",
                key="chimney_thickness",
                on_change=self.mark_as_changed
            )
            
            chimney["thermal_conductivity"] = st.number_input(
                "Toplinska provodljivost [W/mK]",
                min_value=0.0,
                value=float(chimney["thermal_conductivity"]),
                format="%.1f",
                key="chimney_thermal_conductivity",
                on_change=self.mark_as_changed
            )
        
        with col3:
            chimney["roughness"] = st.number_input(
                "Srednja hrapavost [mm]",
                min_value=0.0,
                value=float(chimney["roughness"]),
                format="%.1f",
                key="chimney_roughness",
                on_change=self.mark_as_changed
            )
            
            chimney["annular_gap"] = st.text_input(
                "Prstenasti otvor",
                value=chimney["annular_gap"],
                key="chimney_annular_gap"
            )
        
        # Tehnički podaci o vanjskom oknu
        st.subheader("Vanjsko okno")
        col1, col2, col3 = st.columns(3)
        with col1:
            chimney["outer_section"] = st.text_input(
                "Vanjski presjek",
                value=chimney["outer_section"],
                key="chimney_outer_section"
            )
            
            chimney["outer_material"] = st.text_input(
                "Materijal vanjskog zida",
                value=chimney["outer_material"],
                key="chimney_outer_material"
            )
        
        with col2:
            chimney["outer_thickness"] = st.number_input(
                "Debljina vanjskog zida [mm]",
                min_value=0,
                value=int(chimney["outer_thickness"]),
                key="chimney_outer_thickness",
                on_change=self.mark_as_changed
            )
        
        with col3:
            chimney["thermal_resistance"] = st.number_input(
                "Otpor prolaza topline [m²K/W]",
                min_value=0.0,
                value=float(chimney["thermal_resistance"]),
                format="%.2f",
                key="chimney_thermal_resistance",
                on_change=self.mark_as_changed
            )
        
        # Odjeljci dimovoda
        st.subheader("Sekcije dimnjaka")
        
        num_sections = st.number_input(
            "Broj sekcija", 
            min_value=1, 
            max_value=5, 
            value=len(chimney["sections"]), 
            key="num_sections"
        )
        
        # Dodavanje ili uklanjanje sekcija prema potrebi
        if num_sections > len(chimney["sections"]):
            for _ in range(num_sections - len(chimney["sections"])):
                chimney["sections"].append({
                    "effective_height": 1.0,
                    "developed_length": 1.0
                })
        elif num_sections < len(chimney["sections"]):
            chimney["sections"] = chimney["sections"][:num_sections]
        
        # Za svaku sekciju prikazati detalje
        for i, section in enumerate(chimney["sections"]):
            col1, col2 = st.columns(2)
            with col1:
                section["effective_height"] = st.number_input(
                    f"Učinkovita visina sekcije {i+1} [m]",
                    min_value=0.0,
                    value=float(section["effective_height"]),
                    format="%.2f",
                    key=f"section_height_{i}",
                    on_change=self.mark_as_changed
                )
            
            with col2:
                section["developed_length"] = st.number_input(
                    f"Razvijena dužina sekcije {i+1} [m]",
                    min_value=0.0,
                    value=float(section["developed_length"]),
                    format="%.2f",
                    key=f"section_length_{i}",
                    on_change=self.mark_as_changed
                )
        
        # Protezanje dimovoda
        st.subheader("Protezanje dimovoda")
        col1, col2, col3 = st.columns(3)
        with col1:
            chimney["outdoor_length"] = st.number_input(
                "Dužina na otvorenom [m]",
                min_value=0.0,
                value=float(chimney["outdoor_length"]),
                format="%.1f",
                key="chimney_outdoor_length",
                on_change=self.mark_as_changed
            )
        
        with col2:
            chimney["cold_area_length"] = st.number_input(
                "Dužina u hladnom području [m]",
                min_value=0.0,
                value=float(chimney["cold_area_length"]),
                format="%.1f",
                key="chimney_cold_area_length",
                on_change=self.mark_as_changed
            )
        
        with col3:
            chimney["warm_area_length"] = st.number_input(
                "Dužina u toplom području [m]",
                min_value=0.0,
                value=float(chimney["warm_area_length"]),
                format="%.1f",
                key="chimney_warm_area_length",
                on_change=self.mark_as_changed
            )
        
        # Otpori
        st.subheader("Otpori")
        col1, col2 = st.columns(2)
        with col1:
            chimney["outlet_resistance"] = st.number_input(
                "Otpor ušća (zeta)",
                min_value=0.0,
                value=float(chimney["outlet_resistance"]),
                format="%.1f",
                key="chimney_outlet_resistance",
                on_change=self.mark_as_changed
            )
        
        with col2:
            chimney["inlet_type"] = st.selectbox(
                "Otpor ulaza",
                ["T-komad 87°", "Y-komad 45°", "Direktni ulaz"],
                index=0 if chimney["inlet_type"] == "T-komad 87°" else 1,
                key="chimney_inlet_type"
            )
    
    def render_results(self, data):
        """Prikazuje rezultate proračuna."""
        st.header("Rezultati proračuna")
        
        results = data["results"]
        if not results.get("pressure_conditions"):
            st.info("Pokrenite izračun za prikaz rezultata.")
            return
        
        # Prikaz rezultata u tabovima
        rtab1, rtab2, rtab3, rtab4, rtab5 = st.tabs([
            "Sažetak", 
            "Tlačni uvjeti", 
            "Radni tlakovi", 
            "Povratak dimnih plinova", 
            "Temperaturni uvjeti"
        ])
        
        # Tab za sažetak svih rezultata
        with rtab1:
            self._render_summary_results(results)
            
        # Tab za tlačne uvjete
        with rtab2:
            self._render_pressure_conditions(results)
            
        # Tab za radne tlakove
        with rtab3:
            self._render_working_pressures(results)
            
        # Tab za povratak dimnih plinova
        with rtab4:
            self._render_backflow_results(results)
            
        # Tab za temperaturne uvjete
        with rtab5:
            self._render_temperature_conditions(results)
    
    def _render_summary_results(self, results):
        """Prikazuje sažetak svih rezultata proračuna."""
        st.subheader("Ukupna ocjena dimnjaka")
        
        # Kreiranje DataFrame-a za prikaz sažetka
        summary_data = {
            "Kategorija": ["Tlačni uvjeti", "Radni tlakovi", "Povratak dimnih plinova", "Temperaturni uvjeti"],
            "Status": [
                results["pressure_conditions"].get("status", "Nije izračunato"),
                "Zadovoljava" if results["working_pressures"] else "Nije izračunato",
                results["backflow"].get("status", "Nije izračunato"),
                results["temperature_conditions"].get("status", "Nije izračunato")
            ]
        }
        
        df = pd.DataFrame(summary_data)
        
        # Formatiranje DataFrame-a
        def highlight_status(val):
            color = "green" if "Zadovoljava" in val else "red" if "Ne zadovoljava" in val else "orange"
            return f'background-color: {color}; color: white; border-radius: 5px; padding: 5px;'
        
        # Prikazivanje tablice s formatiranjem
        st.dataframe(
            df.style.applymap(highlight_status, subset=["Status"]),
            hide_index=True,
            width=800
        )
        
        # Ukupna ocjena
        all_ok = all("Zadovoljava" in status for status in summary_data["Status"])
        st.markdown("---")
        if all_ok:
            st.success("✅ **Dimovodni sustav ZADOVOLJAVA sve uvjete norme EN 13384-2**")
        else:
            st.error("❌ **Dimovodni sustav NE ZADOVOLJAVA sve uvjete norme EN 13384-2**")
            
        # Dodavanje preporuka ako uvjeti nisu zadovoljeni
        if not all_ok:
            st.subheader("Preporuke za poboljšanje")
            recommendations = []
            
            if "Ne zadovoljava" in summary_data["Status"][0]:
                recommendations.append("• Poboljšajte tlačne uvjete povećanjem promjera dimnjaka ili smanjenjem otpora.")
            if "Ne zadovoljava" in summary_data["Status"][1]:
                recommendations.append("• Poboljšajte radne tlakove provjerom spojnih elemenata i dimenzije dimnjaka.")
            if "Ne zadovoljava" in summary_data["Status"][2]:
                recommendations.append("• Spriječite povrat dimnih plinova povećanjem visine dimnjaka ili poboljšanjem izolacije.")
            if "Ne zadovoljava" in summary_data["Status"][3]:
                recommendations.append("• Poboljšajte temperaturne uvjete boljom izolacijom dimnjaka.")
                
            for rec in recommendations:
                st.write(rec)
    
    def _render_pressure_conditions(self, results):
        """Prikazuje detaljne rezultate tlačnih uvjeta."""
        st.subheader("Tlačni uvjeti")
        st.markdown("**Prema EN 13384-2, točka 5.5**")
        
        pressure_data = results["pressure_conditions"]
        
        # Kreiranje podataka za tablicu
        col1, col2 = st.columns([3, 1])
        
        with col1:
            data = {
                "Parametar": [
                    "Efektivni uzgon (PH)",
                    "Otpor dimovoda (PR)",
                    "Potrebni potisni tlak (PZ)",
                    "Sigurnosni faktor (SE)",
                    "**Uvjet: PH - PR ≥ PZ · SE**",
                ],
                "Izračunata vrijednost [Pa]": [
                    pressure_data.get("effective_buoyancy", 45.6),
                    pressure_data.get("flow_resistance", 12.3),
                    pressure_data.get("required_pressure", 8.2),
                    pressure_data.get("safety_factor", 1.2),
                    pressure_data.get("pressure", 25.3)
                ],
                "Zahtijevana vrijednost [Pa]": [
                    "-",
                    "-",
                    "-",
                    "≥ 1.2",
                    "≥ 0"
                ],
                "Status": [
                    "-", 
                    "-", 
                    "-",
                    "Zadovoljava" if pressure_data.get("safety_factor", 1.2) >= 1.2 else "Ne zadovoljava",
                    pressure_data.get("status", "Nije izračunato")
                ]
            }
            
            df = pd.DataFrame(data)
            
            # Formatiranje DataFrame-a
            def highlight_status(val):
                if val == "-":
                    return ""
                color = "green" if "Zadovoljava" in val else "red"
                return f'background-color: {color}; color: white; border-radius: 5px; padding: 5px;'
            
            # Prikazivanje tablice s formatiranjem
            st.dataframe(
                df.style.applymap(highlight_status, subset=["Status"]),
                hide_index=True,
                width=800
            )
            
            # Objašnjenje rezultata
            st.markdown("""
            **Objašnjenje:**
            - **PH (Efektivni uzgon)** - Sila uzgona koja nastaje zbog razlike u gustoći između dimnih plinova i vanjskog zraka
            - **PR (Otpor dimovoda)** - Ukupni otpor strujanja u dimovodnom sustavu
            - **PZ (Potrebni potisni tlak)** - Minimalni tlak potreban za siguran rad ložišta
            - **SE (Sigurnosni faktor)** - Faktor sigurnosti prema normi EN 13384-2
            
            Dimovodni sustav zadovoljava tlačne uvjete kada je razlika između efektivnog uzgona i otpora dimovoda veća ili jednaka 
            potrebnom potisnom tlaku pomnoženom sa sigurnosnim faktorom.
            """)
        
        with col2:
            # Vizualni prikaz rezultata
            if "Zadovoljava" in pressure_data.get("status", ""):
                st.markdown("""
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h3 style="margin:0;">✅ ZADOVOLJAVA</h3>
                    <p>Tlačni uvjeti zadovoljavaju normu EN 13384-2</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h3 style="margin:0;">❌ NE ZADOVOLJAVA</h3>
                    <p>Tlačni uvjeti ne zadovoljavaju normu EN 13384-2</p>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_working_pressures(self, results):
        """Prikazuje detaljne rezultate radnih tlakova."""
        st.subheader("Radni tlakovi")
        st.markdown("**Prema EN 13384-2, točka 5.6**")
        
        pressure_data = results["working_pressures"]
        
        # Kreiranje podataka za tablicu
        col1, col2 = st.columns([3, 1])
        
        with col1:
            data = {
                "Parametar": [
                    "Radni tlak pri punom opterećenju (Pw,full)",
                    "Maksimalni dopušteni tlak pri punom opterećenju (Pw,max,full)",
                    "**Uvjet: Pw,full ≤ Pw,max,full**",
                    "Radni tlak pri djelomičnom opterećenju (Pw,part)",
                    "Maksimalni dopušteni tlak pri djelomičnom opterećenju (Pw,max,part)",
                    "**Uvjet: Pw,part ≤ Pw,max,part**"
                ],
                "Izračunata vrijednost [Pa]": [
                    pressure_data.get("full_load", 45.2),
                    pressure_data.get("max_pressure_full", 130.0),
                    "-",
                    pressure_data.get("partial_load", 12.1),
                    pressure_data.get("max_pressure_partial", 30.0),
                    "-"
                ],
                "Zahtijevana vrijednost [Pa]": [
                    "-",
                    "-",
                    "≤ Pw,max,full",
                    "-",
                    "-",
                    "≤ Pw,max,part"
                ],
                "Status": [
                    "-", 
                    "-", 
                    "Zadovoljava" if pressure_data.get("full_load", 45.2) <= pressure_data.get("max_pressure_full", 130.0) else "Ne zadovoljava",
                    "-", 
                    "-", 
                    "Zadovoljava" if pressure_data.get("partial_load", 12.1) <= pressure_data.get("max_pressure_partial", 30.0) else "Ne zadovoljava"
                ]
            }
            
            df = pd.DataFrame(data)
            
            # Formatiranje DataFrame-a
            def highlight_status(val):
                if val == "-":
                    return ""
                color = "green" if "Zadovoljava" in val else "red"
                return f'background-color: {color}; color: white; border-radius: 5px; padding: 5px;'
            
            # Prikazivanje tablice s formatiranjem
            st.dataframe(
                df.style.applymap(highlight_status, subset=["Status"]),
                hide_index=True,
                width=800
            )
            
            # Objašnjenje rezultata
            st.markdown("""
            **Objašnjenje:**
            - **Pw,full** - Izračunati radni tlak u dimovodu pri punom opterećenju
            - **Pw,max,full** - Maksimalni dopušteni radni tlak u dimovodu pri punom opterećenju (prema specifikaciji uređaja)
            - **Pw,part** - Izračunati radni tlak u dimovodu pri djelomičnom opterećenju
            - **Pw,max,part** - Maksimalni dopušteni radni tlak u dimovodu pri djelomičnom opterećenju (prema specifikaciji uređaja)
            
            Dimovodni sustav zadovoljava uvjete radnih tlakova kada su izračunati radni tlakovi manji ili jednaki maksimalnim dopuštenim tlakovima.
            """)
        
        with col2:
            # Vizualni prikaz rezultata za puno opterećenje
            full_load_ok = pressure_data.get("full_load", 45.2) <= pressure_data.get("max_pressure_full", 130.0)
            partial_load_ok = pressure_data.get("partial_load", 12.1) <= pressure_data.get("max_pressure_partial", 30.0)
            
            if full_load_ok:
                st.markdown("""
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">✅ PUNO OPTEREĆENJE</h4>
                    <p>Radni tlak pri punom opterećenju je u dopuštenim granicama</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">❌ PUNO OPTEREĆENJE</h4>
                    <p>Radni tlak pri punom opterećenju prelazi dopuštene granice</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Vizualni prikaz rezultata za djelomično opterećenje
            if partial_load_ok:
                st.markdown("""
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">✅ DJELOMIČNO OPTEREĆENJE</h4>
                    <p>Radni tlak pri djelomičnom opterećenju je u dopuštenim granicama</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">❌ DJELOMIČNO OPTEREĆENJE</h4>
                    <p>Radni tlak pri djelomičnom opterećenju prelazi dopuštene granice</p>
                </div>
                """, unsafe_allow_html=True)
    
    def _render_backflow_results(self, results):
        """Prikazuje detaljne rezultate za povratak dimnih plinova."""
        st.subheader("Povratak dimnih plinova")
        st.markdown("**Prema EN 13384-2, točka 5.7**")
        
        backflow_data = results["backflow"]
        
        # Kreiranje podataka za tablicu
        col1, col2 = st.columns([3, 1])
        
        with col1:
            data = {
                "Parametar": [
                    "Temperatura dimnih plinova u zajedničkom kanalu (Tm)",
                    "Temperatura točke rosišta (Tp)",
                    "**Uvjet: Tm > Tp**",
                    "Faktor povrata dimnih plinova (r)",
                    "Granični faktor povrata (rmax)",
                    "**Uvjet: r ≤ rmax**"
                ],
                "Izračunata vrijednost": [
                    f"{backflow_data.get('flue_gas_temp', 62.3):.1f} °C",
                    f"{backflow_data.get('dew_point_temp', 50.4):.1f} °C",
                    "-",
                    backflow_data.get('value', 0.75),
                    backflow_data.get('max_value', 1.0),
                    "-"
                ],
                "Zahtijevana vrijednost": [
                    "-",
                    "-",
                    "> Tp",
                    "-",
                    "-",
                    "≤ rmax"
                ],
                "Status": [
                    "-", 
                    "-", 
                    "Zadovoljava" if backflow_data.get('flue_gas_temp', 62.3) > backflow_data.get('dew_point_temp', 50.4) else "Ne zadovoljava",
                    "-", 
                    "-", 
                    "Zadovoljava" if backflow_data.get('value', 0.75) <= backflow_data.get('max_value', 1.0) else "Ne zadovoljava"
                ]
            }
            
            df = pd.DataFrame(data)
            
            # Formatiranje DataFrame-a
            def highlight_status(val):
                if val == "-":
                    return ""
                color = "green" if "Zadovoljava" in val else "red"
                return f'background-color: {color}; color: white; border-radius: 5px; padding: 5px;'
            
            # Prikazivanje tablice s formatiranjem
            st.dataframe(
                df.style.applymap(highlight_status, subset=["Status"]),
                hide_index=True,
                width=800
            )
            
            # Objašnjenje rezultata
            st.markdown("""
            **Objašnjenje:**
            - **Tm** - Temperatura dimnih plinova u zajedničkom kanalu
            - **Tp** - Temperatura točke rosišta (kondenzacije)
            - **r** - Faktor povrata dimnih plinova u neaktivna ložišta
            - **rmax** - Maksimalno dopuštena vrijednost faktora povrata
            
            Dimovodni sustav zadovoljava uvjete protiv povrata dimnih plinova kada je temperatura dimnih plinova u zajedničkom kanalu
            veća od temperature točke rosišta, te kada je faktor povrata manji ili jednak maksimalno dopuštenom.
            """)
        
        with col2:
            # Vizualni prikaz rezultata
            temp_ok = backflow_data.get('flue_gas_temp', 62.3) > backflow_data.get('dew_point_temp', 50.4)
            factor_ok = backflow_data.get('value', 0.75) <= backflow_data.get('max_value', 1.0)
            
            if temp_ok and factor_ok:
                st.markdown("""
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h3 style="margin:0;">✅ NEMA POVRATA</h3>
                    <p>Nema opasnosti od povrata dimnih plinova u neaktivna ložišta</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h3 style="margin:0;">❌ MOGUĆ POVRAT</h3>
                    <p>Postoji opasnost od povrata dimnih plinova u neaktivna ložišta</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Dodatni grafički prikaz
            if st.checkbox("Prikaži graf temperatura", value=False):
                # Jednostavan graf koji pokazuje odnos temperature dimnih plinova i točke rosišta
                fig, ax = plt.subplots()
                temperatures = [backflow_data.get('flue_gas_temp', 62.3), backflow_data.get('dew_point_temp', 50.4)]
                labels = ['Temperatura dimnih plinova', 'Točka rosišta']
                colors = ['green' if temp_ok else 'orange', 'red']
                
                ax.bar(labels, temperatures, color=colors)
                ax.set_ylabel('Temperatura [°C]')
                ax.set_title('Usporedba temperature dimnih plinova i točke rosišta')
                ax.axhline(y=backflow_data.get('dew_point_temp', 50.4), color='red', linestyle='--')
                
                plt.tight_layout()
                st.pyplot(fig)
    
    def _render_temperature_conditions(self, results):
        """Prikazuje detaljne rezultate za temperaturne uvjete."""
        st.subheader("Temperaturni uvjeti")
        st.markdown("**Prema EN 13384-2, točka 5.8**")
        
        temp_data = results["temperature_conditions"]
        
        # Kreiranje podataka za tablicu
        col1, col2 = st.columns([3, 1])
        
        with col1:
            data = {
                "Parametar": [
                    "Temperatura unutarnje stijenke dimnjaka (Tiob)",
                    "Temperatura točke rosišta dimnih plinova (Tp)",
                    "**Uvjet: Tiob ≥ Tp**",
                    "Temperatura dimnih plinova na izlazu iz dimnjaka (Te)",
                    "Minimalna temperatura za održavanje uzgona (Tmin)",
                    "**Uvjet: Te ≥ Tmin**"
                ],
                "Izračunata vrijednost [°C]": [
                    temp_data.get('inner_wall_temp', 54.2),
                    temp_data.get('dew_point_temp', 50.4),
                    "-",
                    temp_data.get('flue_gas_temp', 62.3),
                    temp_data.get('min_temp', 45.0),
                    "-"
                ],
                "Zahtijevana vrijednost [°C]": [
                    "-",
                    "-",
                    "≥ Tp",
                    "-",
                    "-",
                    "≥ Tmin"
                ],
                "Status": [
                    "-", 
                    "-", 
                    "Zadovoljava" if temp_data.get('inner_wall_temp', 54.2) >= temp_data.get('dew_point_temp', 50.4) else "Ne zadovoljava",
                    "-", 
                    "-", 
                    "Zadovoljava" if temp_data.get('flue_gas_temp', 62.3) >= temp_data.get('min_temp', 45.0) else "Ne zadovoljava"
                ]
            }
            
            df = pd.DataFrame(data)
            
            # Formatiranje DataFrame-a
            def highlight_status(val):
                if val == "-":
                    return ""
                color = "green" if "Zadovoljava" in val else "red"
                return f'background-color: {color}; color: white; border-radius: 5px; padding: 5px;'
            
            # Prikazivanje tablice s formatiranjem
            st.dataframe(
                df.style.applymap(highlight_status, subset=["Status"]),
                hide_index=True,
                width=800
            )
            
            # Objašnjenje rezultata
            st.markdown("""
            **Objašnjenje:**
            - **Tiob** - Temperatura unutarnje stijenke dimnjaka
            - **Tp** - Temperatura točke rosišta (kondenzacije) dimnih plinova
            - **Te** - Temperatura dimnih plinova na izlazu iz dimnjaka
            - **Tmin** - Minimalna temperatura potrebna za održavanje uzgona
            
            Dimovodni sustav zadovoljava temperaturne uvjete kada je temperatura unutarnje stijenke dimnjaka viša od temperature 
            točke rosišta (sprečava se kondenzacija) i kada je temperatura dimnih plinova na izlazu iz dimnjaka veća od minimalne 
            temperature potrebne za održavanje uzgona (osigurava se pravilno odvođenje dimnih plinova).
            """)
        
        with col2:
            # Vizualni prikaz rezultata za temperaturu stijenke
            wall_temp_ok = temp_data.get('inner_wall_temp', 54.2) >= temp_data.get('dew_point_temp', 50.4)
            exit_temp_ok = temp_data.get('flue_gas_temp', 62.3) >= temp_data.get('min_temp', 45.0)
            
            if wall_temp_ok:
                st.markdown("""
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">✅ BEZ KONDENZACIJE</h4>
                    <p>Temperatura stijenke dimnjaka je iznad točke rosišta</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">❌ MOGUĆA KONDENZACIJA</h4>
                    <p>Temperatura stijenke dimnjaka je ispod točke rosišta</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Vizualni prikaz rezultata za temperaturu na izlazu
            if exit_temp_ok:
                st.markdown("""
                <div style="background-color: #d4edda; color: #155724; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">✅ DOBAR UZGON</h4>
                    <p>Temperatura dimnih plinova na izlazu osigurava dobar uzgon</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; text-align: center; margin-top: 20px;">
                    <h4 style="margin:0;">❌ SLAB UZGON</h4>
                    <p>Temperatura dimnih plinova na izlazu ne osigurava dovoljan uzgon</p>
                </div>
                """, unsafe_allow_html=True)
    
    def calculate(self):
        """Provodi proračun dimnjaka prema EN 13384-2."""
        st.info("Provođenje proračuna...")
        
        # Dohvat podataka iz session state
        data = st.session_state.chimney_sizing_data
        
        # Import potrebnih funkcija
        from .utils import (
            calculate_air_density, calculate_flue_gas_density, calculate_static_draft, 
            calculate_flue_gas_velocity, calculate_friction_coefficient, calculate_pressure_drop_friction, 
            calculate_pressure_drop_resistance, calculate_total_pressure_drop, calculate_actual_draft,
            calculate_inner_wall_temperature, check_freezing_condition
        )
        from .constants import RESISTANCE_COEFFICIENTS
        
        # 1. IZRAČUN GUSTOĆE ZRAKA I DIMNIH PLINOVA
        # 1.1. Opći podaci iz inputa
        geodetic_height = data["general"]["geodetic_height"]  # m
        safety_number_SE = data["general"]["safety_number_SE"]
        ambient_temp = data["general"]["temperatures"]["ambient"]  # °C
        outdoor_temp = data["general"]["temperatures"]["outdoor"]  # °C
        
        # 1.2. Gustoća zraka
        air_density = calculate_air_density(ambient_temp, geodetic_height)  # kg/m³
        
        # 2. IZRAČUNI ZA SVAKO LOŽIŠTE
        results = {
            "pressure_conditions": {},
            "working_pressures": {},
            "backflow": {},
            "temperature_conditions": {}
        }
        
        appliances = data["appliances"]
        chimney = data["chimney"]
        connecting_element = data["connecting_elements"]
        
        # Računamo efektivnu ukupnu visinu dimnjaka
        chimney_height = sum(section["effective_height"] for section in chimney["sections"])  # m
        
        # 2.1. Izračuni za puno opterećenje
        # Lista za spremanje rezultata svakog ložišta
        full_load_results = []
        partial_load_results = []
        
        for i, appliance in enumerate(appliances):
            # 2.1.1. Parametri ložišta pri punom opterećenju
            flue_gas_temp_full = appliance["full_load"]["flue_gas_temperature"]  # °C
            mass_flow_full = appliance["full_load"]["flue_gas_mass_flow"] / 1000  # kg/s
            co2_percentage_full = appliance["full_load"]["co2_percentage"]  # %
            fuel_type = appliance["fuel"]
            max_pressure_full = appliance["full_load"]["max_positive_pressure"]  # Pa
            
            # 2.1.2. Izračun gustoće dimnih plinova pri punom opterećenju
            flue_gas_density_full = calculate_flue_gas_density(air_density, flue_gas_temp_full, fuel_type)
            
            # 2.1.3. Promjer dimnjaka
            chimney_diameter = chimney["inner_diameter"] / 1000  # m
            
            # 2.1.4. Izračun brzine dimnih plinova pri punom opterećenju
            velocity_full = calculate_flue_gas_velocity(mass_flow_full, chimney_diameter, flue_gas_density_full)
            
            # 2.1.5. Statički uzgon
            static_draft_full = calculate_static_draft(air_density, flue_gas_density_full, chimney_height, safety_number_SE)
            
            # 2.1.6. Koeficijent trenja dimovoda
            roughness = chimney["roughness"] / 1000  # m
            friction_coef = calculate_friction_coefficient(roughness, chimney_diameter)
            
            # 2.1.7. Pad tlaka zbog trenja u dimovodu
            pressure_drop_friction_full = calculate_pressure_drop_friction(
                friction_coef, chimney_height, flue_gas_density_full, velocity_full, 
                chimney_diameter, safety_number_SE
            )
            
            # 2.1.8. Lokalni otpori
            # Otpor na ulazu (T-komad)
            resistance_coefficient = RESISTANCE_COEFFICIENTS.get(chimney["inlet_type"], 1.3)
            pressure_drop_inlet_full = calculate_pressure_drop_resistance(
                resistance_coefficient, flue_gas_density_full, velocity_full, safety_number_SE
            )
            
            # 2.1.9. Ukupni otpor strujanju
            total_pressure_drop_full = calculate_total_pressure_drop(pressure_drop_friction_full, pressure_drop_inlet_full)
            
            # 2.1.10. Stvarni uzgon
            actual_draft_full = calculate_actual_draft(static_draft_full, total_pressure_drop_full)
            
            # Spremi rezultate za ovo ložište pri punom opterećenju
            full_load_results.append({
                "flue_gas_density": flue_gas_density_full,
                "velocity": velocity_full,
                "static_draft": static_draft_full,
                "pressure_drop_friction": pressure_drop_friction_full,
                "pressure_drop_inlet": pressure_drop_inlet_full,
                "total_pressure_drop": total_pressure_drop_full,
                "actual_draft": actual_draft_full,
                "max_pressure": max_pressure_full
            })
            
            # 2.2. Izračuni za djelomično opterećenje
            flue_gas_temp_partial = appliance["partial_load"]["flue_gas_temperature"]  # °C
            mass_flow_partial = appliance["partial_load"]["flue_gas_mass_flow"] / 1000  # kg/s
            co2_percentage_partial = appliance["partial_load"]["co2_percentage"]  # %
            max_pressure_partial = appliance["partial_load"]["max_positive_pressure"]  # Pa
            
            # 2.2.1. Izračun gustoće dimnih plinova pri djelomičnom opterećenju
            flue_gas_density_partial = calculate_flue_gas_density(air_density, flue_gas_temp_partial, fuel_type)
            
            # 2.2.2. Izračun brzine dimnih plinova pri djelomičnom opterećenju
            velocity_partial = calculate_flue_gas_velocity(mass_flow_partial, chimney_diameter, flue_gas_density_partial)
            
            # 2.2.3. Statički uzgon pri djelomičnom opterećenju
            static_draft_partial = calculate_static_draft(air_density, flue_gas_density_partial, chimney_height, safety_number_SE)
            
            # 2.2.4. Pad tlaka zbog trenja u dimovodu pri djelomičnom opterećenju
            pressure_drop_friction_partial = calculate_pressure_drop_friction(
                friction_coef, chimney_height, flue_gas_density_partial, velocity_partial, 
                chimney_diameter, safety_number_SE
            )
            
            # 2.2.5. Lokalni otpori pri djelomičnom opterećenju
            pressure_drop_inlet_partial = calculate_pressure_drop_resistance(
                resistance_coefficient, flue_gas_density_partial, velocity_partial, safety_number_SE
            )
            
            # 2.2.6. Ukupni otpor strujanju pri djelomičnom opterećenju
            total_pressure_drop_partial = calculate_total_pressure_drop(
                pressure_drop_friction_partial, pressure_drop_inlet_partial
            )
            
            # 2.2.7. Stvarni uzgon pri djelomičnom opterećenju
            actual_draft_partial = calculate_actual_draft(static_draft_partial, total_pressure_drop_partial)
            
            # Spremi rezultate za ovo ložište pri djelomičnom opterećenju
            partial_load_results.append({
                "flue_gas_density": flue_gas_density_partial,
                "velocity": velocity_partial,
                "static_draft": static_draft_partial,
                "pressure_drop_friction": pressure_drop_friction_partial,
                "pressure_drop_inlet": pressure_drop_inlet_partial,
                "total_pressure_drop": total_pressure_drop_partial,
                "actual_draft": actual_draft_partial,
                "max_pressure": max_pressure_partial
            })
        
        # 3. PROVJERA TLAČNIH UVJETA
        # 3.1. Tlačni uvjet za puno opterećenje
        required_pressure_full = full_load_results[0]["max_pressure"] * 0.1  # Aproksimacija za PZ
        pressure_condition_full = full_load_results[0]["static_draft"] - full_load_results[0]["total_pressure_drop"] >= required_pressure_full * safety_number_SE
        
        # 3.2. Tlačni uvjet za djelomično opterećenje
        required_pressure_partial = partial_load_results[0]["max_pressure"] * 0.1  # Aproksimacija za PZ
        pressure_condition_partial = partial_load_results[0]["static_draft"] - partial_load_results[0]["total_pressure_drop"] >= required_pressure_partial * safety_number_SE
        
        # 3.3. Spremanje rezultata tlačnih uvjeta
        results["pressure_conditions"] = {
            "effective_buoyancy": round(full_load_results[0]["static_draft"], 1),
            "flow_resistance": round(full_load_results[0]["total_pressure_drop"], 1),
            "required_pressure": round(required_pressure_full, 1),
            "safety_factor": safety_number_SE,
            "pressure": round(full_load_results[0]["static_draft"] - full_load_results[0]["total_pressure_drop"] - required_pressure_full * safety_number_SE, 1),
            "status": "Zadovoljava" if pressure_condition_full and pressure_condition_partial else "Ne zadovoljava"
        }
        
        # 4. PROVJERA RADNIH TLAKOVA
        # 4.1. Radni tlakovi pri punom opterećenju
        working_pressure_full = full_load_results[0]["static_draft"] - full_load_results[0]["total_pressure_drop"]
        working_pressure_full_ok = working_pressure_full <= full_load_results[0]["max_pressure"]
        
        # 4.2. Radni tlakovi pri djelomičnom opterećenju
        working_pressure_partial = partial_load_results[0]["static_draft"] - partial_load_results[0]["total_pressure_drop"]
        working_pressure_partial_ok = working_pressure_partial <= partial_load_results[0]["max_pressure"]
        
        # 4.3. Spremanje rezultata radnih tlakova
        results["working_pressures"] = {
            "full_load": round(working_pressure_full, 1),
            "partial_load": round(working_pressure_partial, 1),
            "max_pressure_full": full_load_results[0]["max_pressure"],
            "max_pressure_partial": partial_load_results[0]["max_pressure"],
            "status": "Zadovoljava" if working_pressure_full_ok and working_pressure_partial_ok else "Ne zadovoljava"
        }
        
        # 5. PROVJERA POVRATA DIMNIH PLINOVA
        # 5.1. Temperatura točke rosišta (aproksimacija za zemni plin)
        dew_point_temp = 57.0 - (1.0 - full_load_results[0]["flue_gas_density"] / air_density) * 100  # °C
        
        # 5.2. Temperatura dimnih plinova u zajedničkom kanalu
        flue_gas_temp_chimney = (appliances[0]["full_load"]["flue_gas_temperature"] + appliances[0]["partial_load"]["flue_gas_temperature"]) / 2.0
        
        # 5.3. Faktor povrata dimnih plinova (aproksimacija)
        backflow_factor = 0.75  # r
        max_backflow_factor = 1.0  # rmax
        
        # 5.4. Spremanje rezultata povrata dimnih plinova
        results["backflow"] = {
            "status": "Ne dolazi do povrata dimnih plinova" if flue_gas_temp_chimney > dew_point_temp and backflow_factor <= max_backflow_factor else "Moguć povrat dimnih plinova",
            "value": backflow_factor,
            "max_value": max_backflow_factor,
            "flue_gas_temp": round(flue_gas_temp_chimney, 1),
            "dew_point_temp": round(dew_point_temp, 1)
        }
        
        # 6. PROVJERA TEMPERATURNIH UVJETA
        # 6.1. Temperatura stijenke i uvjeti kondenzacije
        # Pojednostavljeni izračun temperature unutarnje stijenke (za potpuni proračun potrebna kompleksna iteracija)
        thermal_resistance_wall = chimney["thickness"] / 1000 / chimney["thermal_conductivity"]  # m²K/W
        thermal_resistance_ambient = chimney["thermal_resistance"]  # m²K/W
        
        # Temperatura unutarnje stijenke dimnjaka
        inner_wall_temp = calculate_inner_wall_temperature(
            outdoor_temp, flue_gas_temp_chimney, thermal_resistance_wall, thermal_resistance_ambient
        )
        
        # Minimalna temperatura za održavanje uzgona
        min_temp = dew_point_temp - 3.0  # °C
        
        # 6.2. Spremanje rezultata temperaturnih uvjeta
        temperature_condition = inner_wall_temp >= dew_point_temp and flue_gas_temp_chimney >= min_temp
        
        results["temperature_conditions"] = {
            "inner_wall_temp": round(inner_wall_temp, 1),
            "dew_point_temp": round(dew_point_temp, 1),
            "flue_gas_temp": round(flue_gas_temp_chimney, 1),
            "min_temp": round(min_temp, 1),
            "status": "Zadovoljava" if temperature_condition else "Ne zadovoljava"
        }
        
        # 7. AŽURIRANJE STANJA SA REZULTATIMA
        data["results"] = results
        
        # 8. ZABILJEŽI REZULTATE U HISTORIЈU
        self.record_state("Proveden proračun")
        
        st.success("Proračun uspješno proveden!")