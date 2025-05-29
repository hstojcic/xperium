"""
Proračun dimnjaka prema EN 13384-2 normi.
"""

import streamlit as st
import pandas as pd
import numpy as np
import copy
from typing import Dict, Any, List

# Import lokalnih modula
from .base import BaseCalculation
from .utils import *
from .constants import *


class ChimneySizingCalc(BaseCalculation):
    """Proračun dimnjaka prema EN 13384-2 normi."""
    
    def __init__(self, name="Proračun dimnjaka prema EN 13384-2"):
        super().__init__(name)
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Inicijalizira session state sa default vrijednostima."""
        if "chimney_sizing_data" not in st.session_state:
            st.session_state.chimney_sizing_data = self.initialize_data_structure()
        if "chimney_sizing_changed" not in st.session_state:
            st.session_state.chimney_sizing_changed = False
        if "chimney_sizing_current_calc_id" not in st.session_state:
            st.session_state.chimney_sizing_current_calc_id = None
    
    def mark_as_changed(self):
        """Označava da su podaci promijenjeni."""
        st.session_state.chimney_sizing_changed = True
        self.record_state("Promjena korisničkih podataka")
    
    def get_state(self):
        """Vraća trenutno stanje kalkulatora."""
        return {
            "data": copy.deepcopy(st.session_state.get("chimney_sizing_data", {})),
            "changed": st.session_state.get("chimney_sizing_changed", False)
        }
    
    def restore_state(self, state):
        """Vraća stanje kalkulatora."""
        if "data" in state:
            st.session_state.chimney_sizing_data = copy.deepcopy(state["data"])
        if "changed" in state:
            st.session_state.chimney_sizing_changed = state["changed"]
    
    def serialize(self):
        """Serijalizira podatke za spremanje."""
        return {
            "type": "chimney_sizing",
            "version": "1.0",
            "data": st.session_state.get("chimney_sizing_data", {}),
            "metadata": {
                "name": self.name,
                "changed": st.session_state.get("chimney_sizing_changed", False)
            }
        }
    
    def deserialize(self, data):
        """Deserijalizira spremljene podatke."""
        if data.get("type") == "chimney_sizing" and "data" in data:
            st.session_state.chimney_sizing_data = data["data"]
            if "metadata" in data and "changed" in data["metadata"]:
                st.session_state.chimney_sizing_changed = data["metadata"]["changed"]
            return True
        return False
    
    def reset_session_state(self):
        """Resetira session state na default vrijednosti."""
        st.session_state.chimney_sizing_data = self.initialize_data_structure()
        st.session_state.chimney_sizing_changed = False
        self.clear_widget_states()
    
    def sync_from_session_state(self):
        """Sinkronizira podatke iz session state."""
        if "chimney_sizing_data" not in st.session_state:
            self._initialize_session_state()
      
    def clear_widget_states(self):
        """Briše widget states povezane s ovim kalkulatorom."""
        keys_to_remove = []
        for key in st.session_state.keys():
            if isinstance(key, str) and key.startswith(('chimney_', 'conn_', 'appliance_', 'num_', 'section_')):
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    def initialize_data_structure(self):
        """Inicijalizira osnovnu strukturu podataka."""
        return {
            "general": {
                "location": "Osijek",
                "geodetic_height": 93,
                "safety_number_SE": 1.2,
                "correction_factor_SH": 0.5,
                "temperatures": {
                    "outlet": 5,
                    "outdoor": -15,
                    "cold_area": 5,
                    "warm_area": 20,
                    "ambient": 15,
                }
            },
            "appliances": [
                {
                    "manufacturer": "Vaillant",
                    "model": "ecoTEC plus VC 20 CS / 1-5",
                    "fuel": "Zemni plin",
                    "full_load": {
                        "nominal_heat_output": 20.9,
                        "heat_input": 20.4,
                        "co2_percentage": 9.6,
                        "flue_gas_mass_flow": 12.79,
                        "flue_gas_temperature": 85,
                        "max_positive_pressure": 130
                    },
                    "partial_load": {
                        "nominal_heat_output": 3.2,
                        "heat_input": 3.2,
                        "co2_percentage": 9.6,
                        "flue_gas_mass_flow": 1.51,
                        "flue_gas_temperature": 35,
                        "max_positive_pressure": 30
                    },
                    "connection": {
                        "diameter": 60,
                        "transition_type": "Redukcija konusna 60°"
                    }
                },
                {
                    "manufacturer": "Vaillant",
                    "model": "ecoTEC plus VC 20 CS / 1-5",
                    "fuel": "Zemni plin",
                    "full_load": {
                        "nominal_heat_output": 20.9,
                        "heat_input": 20.4,
                        "co2_percentage": 9.6,
                        "flue_gas_mass_flow": 12.79,
                        "flue_gas_temperature": 85,
                        "max_positive_pressure": 130
                    },
                    "partial_load": {
                        "nominal_heat_output": 3.2,
                        "heat_input": 3.2,
                        "co2_percentage": 9.6,
                        "flue_gas_mass_flow": 1.51,
                        "flue_gas_temperature": 35,
                        "max_positive_pressure": 30
                    },
                    "connection": {
                        "diameter": 60,
                        "transition_type": "Redukcija konusna 60°"
                    }
                }
            ],
            "connecting_elements": {
                "type": "Koncentrični spojni element",
                "manufacturer": "Centrotherm",
                "model": "System Chimneys PP / Metal",
                "inner_diameter": 56,
                "thickness": 2,
                "material": "PP gladak",
                "roughness": 0.5,
                "resistances": "Luk 87°",
                "effective_height": 0.1,
                "developed_length": 0.32,
                "outer_share": 0,
                "cold_area_share": 0,
                "warm_area_share": 100
            },
            "chimney": {
                "type": "Dimovodna naprava u oknu",
                "manufacturer": "Schiedel",
                "model": "MULTI",
                "inner_diameter": 140,
                "material": "Keramika",
                "thickness": 7,
                "thermal_conductivity": 1.1,
                "roughness": 1.5,
                "annular_gap": "Protutok zraka (53 mm)",
                "outer_section": "Kvadratni 260 mm",
                "outer_material": "Lagani beton",
                "outer_thickness": 50,
                "thermal_resistance": 0.12,
                "outlet_resistance": 1.0,
                "inlet_type": "T-komad 87°",
                "sections": [
                    {
                        "effective_height": 2.96,
                        "developed_length": 2.96
                    },
                    {
                        "effective_height": 1.56,
                        "developed_length": 1.56
                    }
                ],
                "outdoor_length": 1,
                "cold_area_length": 0,
                "warm_area_length": 3.52
            },
            "results": {
                "pressure_conditions": {},
                "working_pressures": {},            "backflow": {},
                "temperature_conditions": {}
            }
        }
    
    def render(self):
        """Prikazuje sučelje kalkulatora."""
        # Dodajemo provjeru ID-a za slučaj promjene između kalkulatora
        # Ovo sprječava resetiranje podataka pri povratku na ovaj kalkulator
        calc_id = self.name
        if "chimney_sizing_current_calc_id" not in st.session_state:
            st.session_state.chimney_sizing_current_calc_id = calc_id
        elif st.session_state.chimney_sizing_current_calc_id != calc_id:
            st.session_state.chimney_sizing_current_calc_id = calc_id
        
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
                key="location",
                on_change=self.mark_as_changed
            )
        
        with col2:
            data["general"]["geodetic_height"] = st.number_input(
                "Geodetska visina [m]",
                min_value=0,
                value=int(data["general"]["geodetic_height"]),
                key="geodetic_height",
                on_change=self.mark_as_changed
            )
        
        with col3:
            pass  # Prazna kolona za sada
        
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
            key="num_appliances",
            on_change=self.mark_as_changed
        )
        
        # Dodavanje ili uklanjanje ložišta prema potrebi
        if num_appliances > len(appliances):
            for _ in range(num_appliances - len(appliances)):
                appliances.append(copy.deepcopy(appliances[0]))  # Kopiraj prvi element kao template
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
                        key=f"appliance_manufacturer_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col2:
                    appliance["model"] = st.text_input(
                        "Model",
                        value=appliance["model"],
                        key=f"appliance_model_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col3:
                    appliance["fuel"] = st.selectbox(
                        "Gorivo",
                        ["Zemni plin", "Propan", "Loživo ulje", "Peleti", "Drvo"],
                        index=0 if appliance["fuel"] == "Zemni plin" else 1,
                        key=f"appliance_fuel_{i}",
                        on_change=self.mark_as_changed
                    )
                
                # Podaci za puno opterećenje
                st.subheader("Puno opterećenje")
                col1, col2 = st.columns(2)
                with col1:
                    appliance["full_load"]["nominal_heat_output"] = st.number_input(
                        "Nominalni toplinski učin [kW]",
                        min_value=0.0,
                        value=float(appliance["full_load"]["nominal_heat_output"]),
                        format="%.1f",
                        key=f"appliance_full_heat_output_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["co2_percentage"] = st.number_input(
                        "Udio CO2 u dimnim plinovima [%]",
                        min_value=0.0,
                        max_value=20.0,
                        value=float(appliance["full_load"]["co2_percentage"]),
                        format="%.1f",
                        key=f"appliance_full_co2_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["flue_gas_temperature"] = st.number_input(
                        "Temperatura dimnih plinova [°C]",
                        min_value=0,
                        value=int(appliance["full_load"]["flue_gas_temperature"]),
                        key=f"appliance_full_temp_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col2:
                    appliance["full_load"]["heat_input"] = st.number_input(
                        "Toplinski unos [kW]",
                        min_value=0.0,
                        value=float(appliance["full_load"]["heat_input"]),
                        format="%.1f",
                        key=f"appliance_full_heat_input_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["flue_gas_mass_flow"] = st.number_input(
                        "Maseni protok dimnih plinova [kg/h]",
                        min_value=0.0,
                        value=float(appliance["full_load"]["flue_gas_mass_flow"]),
                        format="%.2f",
                        key=f"appliance_full_mass_flow_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["full_load"]["max_positive_pressure"] = st.number_input(
                        "Maksimalni pozitivni tlak [Pa]",
                        min_value=0,
                        value=int(appliance["full_load"]["max_positive_pressure"]),
                        key=f"appliance_full_pressure_{i}",
                        on_change=self.mark_as_changed
                    )
                
                # Podaci za djelomično opterećenje
                st.subheader("Djelomično opterećenje")
                col1, col2 = st.columns(2)
                with col1:
                    appliance["partial_load"]["nominal_heat_output"] = st.number_input(
                        "Nominalni toplinski učin [kW]",
                        min_value=0.0,
                        value=float(appliance["partial_load"]["nominal_heat_output"]),
                        format="%.1f",
                        key=f"appliance_partial_heat_output_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["co2_percentage"] = st.number_input(
                        "Udio CO2 u dimnim plinovima [%]",
                        min_value=0.0,
                        max_value=20.0,
                        value=float(appliance["partial_load"]["co2_percentage"]),
                        format="%.1f",
                        key=f"appliance_partial_co2_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["flue_gas_temperature"] = st.number_input(
                        "Temperatura dimnih plinova [°C]",
                        min_value=0,
                        value=int(appliance["partial_load"]["flue_gas_temperature"]),
                        key=f"appliance_partial_temp_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col2:
                    appliance["partial_load"]["heat_input"] = st.number_input(
                        "Toplinski unos [kW]",
                        min_value=0.0,
                        value=float(appliance["partial_load"]["heat_input"]),
                        format="%.1f",
                        key=f"appliance_partial_heat_input_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["flue_gas_mass_flow"] = st.number_input(
                        "Maseni protok dimnih plinova [kg/h]",
                        min_value=0.0,
                        value=float(appliance["partial_load"]["flue_gas_mass_flow"]),
                        format="%.2f",
                        key=f"appliance_partial_mass_flow_{i}",
                        on_change=self.mark_as_changed
                    )
                    
                    appliance["partial_load"]["max_positive_pressure"] = st.number_input(
                        "Maksimalni pozitivni tlak [Pa]",
                        min_value=0,
                        value=int(appliance["partial_load"]["max_positive_pressure"]),
                        key=f"appliance_partial_pressure_{i}",
                        on_change=self.mark_as_changed
                    )
                
                # Podaci o priključku
                st.subheader("Priključak")
                col1, col2 = st.columns(2)
                with col1:
                    appliance["connection"]["diameter"] = st.number_input(
                        "Promjer priključka [mm]",
                        min_value=0,
                        value=int(appliance["connection"]["diameter"]),
                        key=f"appliance_conn_diameter_{i}",
                        on_change=self.mark_as_changed
                    )
                
                with col2:
                    appliance["connection"]["transition_type"] = st.selectbox(
                        "Tip prijelaza",
                        ["Redukcija konusna 60°", "Redukcija ostra", "Ekspanzija postupna", "Ekspanzija ostra"],
                        index=0,
                        key=f"appliance_conn_transition_{i}",
                        on_change=self.mark_as_changed
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
                key="conn_type",
                on_change=self.mark_as_changed
            )
        
        with col2:
            connecting_elements["manufacturer"] = st.text_input(
                "Proizvođač",
                value=connecting_elements["manufacturer"],
                key="conn_manufacturer",
                on_change=self.mark_as_changed
            )
        
        with col3:
            connecting_elements["model"] = st.text_input(
                "Model",
                value=connecting_elements["model"],
                key="conn_model",
                on_change=self.mark_as_changed
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
                key="conn_material",
                on_change=self.mark_as_changed
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
                key="conn_resistances",
                on_change=self.mark_as_changed
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
                key="chimney_type",
                on_change=self.mark_as_changed
            )
        
        with col2:
            chimney["manufacturer"] = st.text_input(
                "Proizvođač",
                value=chimney["manufacturer"],
                key="chimney_manufacturer",
                on_change=self.mark_as_changed
            )
        
        with col3:
            chimney["model"] = st.text_input(
                "Model",
                value=chimney["model"],
                key="chimney_model",
                on_change=self.mark_as_changed
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
                key="chimney_material",
                on_change=self.mark_as_changed
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
                key="chimney_annular_gap",
                on_change=self.mark_as_changed
            )
        
        # Tehnički podaci o vanjskom oknu
        st.subheader("Vanjsko okno")
        col1, col2, col3 = st.columns(3)
        with col1:
            chimney["outer_section"] = st.text_input(
                "Vanjski presjek",
                value=chimney["outer_section"],
                key="chimney_outer_section",
                on_change=self.mark_as_changed
            )
            
            chimney["outer_material"] = st.text_input(
                "Materijal vanjskog zida",
                value=chimney["outer_material"],
                key="chimney_outer_material",
                on_change=self.mark_as_changed
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
            key="num_sections",
            on_change=self.mark_as_changed
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
                key="chimney_inlet_type",
                on_change=self.mark_as_changed
            )
    
    def render_results(self, data):
        """Prikazuje rezultate proračuna."""
        st.header("Rezultati proračuna")
        
        results = data["results"]
        if not results.get("pressure_conditions"):
            st.info("Kliknite 'Izračunaj' za prikaz rezultata.")
            if st.button("Izračunaj", type="primary"):
                self.calculate_results(data)
                st.rerun()
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
                results["working_pressures"].get("status", "Nije izračunato"),
                results["backflow"].get("status", "Nije izračunato"),
                results["temperature_conditions"].get("status", "Nije izračunato")
            ]
        }
        
        df = pd.DataFrame(summary_data)
        
        # Formatiranje DataFrame-a za novije verzije pandas
        def highlight_status(val):
            if val == "Prihvaćeno":
                return 'background-color: #d4edda; color: #155724'
            elif val == "Neprihvaćeno":
                return 'background-color: #f8d7da; color: #721c24'
            else:
                return 'background-color: #fff3cd; color: #856404'        # Prikazivanje tablice s formatiranjem (kompatibilno s novijim Pandas verzijama)
        try:
            # Use apply with a function that works on the 'Status' column
            styled_df = df.style.apply(lambda x: [highlight_status(val) if x.name == 'Status' else '' for val in x], axis=0, subset=['Status'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
        except Exception:
            # Fallback za starije verzije
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    def _render_pressure_conditions(self, results):
        """Prikazuje rezultate tlačnih uvjeta."""
        st.subheader("Tlačni uvjeti")
        
        pressure_data = results.get("pressure_conditions", {})
        if not pressure_data:
            st.warning("Nema podataka o tlačnim uvjetima.")
            return
        
        # Prikaz osnovnih rezultata
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Potrebni tlak", f"{pressure_data.get('required_pressure', 0):.2f} Pa")
            st.metric("Dostupni tlak", f"{pressure_data.get('available_pressure', 0):.2f} Pa")
        
        with col2:
            st.metric("Razlika tlaka", f"{pressure_data.get('pressure_difference', 0):.2f} Pa")
            status = pressure_data.get('status', 'Nepoznato')
            if status == "Prihvaćeno":
                st.success(f"Status: {status}")
            else:
                st.error(f"Status: {status}")
    
    def _render_working_pressures(self, results):
        """Prikazuje rezultate radnih tlakova."""
        st.subheader("Radni tlakovi")
        
        working_data = results.get("working_pressures", {})
        if not working_data:
            st.warning("Nema podataka o radnim tlakovima.")
            return
        
        # Prikaz rezultata za svako ložište
        for i, appliance_data in enumerate(working_data.get("appliances", [])):
            st.write(f"**Ložište {i+1}**")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Radni tlak - puno opterećenje", f"{appliance_data.get('full_load_pressure', 0):.2f} Pa")
            with col2:
                st.metric("Radni tlak - djelomično opterećenje", f"{appliance_data.get('partial_load_pressure', 0):.2f} Pa")
    
    def _render_backflow_results(self, results):
        """Prikazuje rezultate analize povratka dimnih plinova."""
        st.subheader("Povratak dimnih plinova")
        
        backflow_data = results.get("backflow", {})
        if not backflow_data:
            st.warning("Nema podataka o povratu dimnih plinova.")
            return
        
        status = backflow_data.get('status', 'Nepoznato')
        if status == "Prihvaćeno":
            st.success("Nema opasnosti od povratka dimnih plinova")
        else:
            st.error("Postoji opasnost od povratka dimnih plinova")
    
    def _render_temperature_conditions(self, results):
        """Prikazuje rezultate temperaturnih uvjeta."""
        st.subheader("Temperaturni uvjeti")
        
        temp_data = results.get("temperature_conditions", {})
        if not temp_data:
            st.warning("Nema podataka o temperaturnim uvjetima.")
            return
        
        # Prikaz temperatura u različitim dijelovima sustava
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperatura na izlazu", f"{temp_data.get('outlet_temperature', 0):.1f} °C")
            st.metric("Minimalna temperatura", f"{temp_data.get('min_temperature', 0):.1f} °C")
        
        with col2:
            st.metric("Temperatura rosišta", f"{temp_data.get('dew_point', 0):.1f} °C")
            status = temp_data.get('status', 'Nepoznato')
            if status == "Prihvaćeno":
                st.success(f"Status: {status}")
            else:
                st.error(f"Status: {status}")
    
    def calculate_results(self, data):
        """Izračunava rezultate proračuna."""
        # Simulacija proračuna - u stvarnoj implementaciji ovdje bi bili složeni izračuni
        # prema EN 13384-2 normi
        
        results = {
            "pressure_conditions": {
                "required_pressure": 15.5,
                "available_pressure": 18.2,
                "pressure_difference": 2.7,
                "status": "Prihvaćeno"
            },
            "working_pressures": {
                "appliances": [
                    {
                        "full_load_pressure": 12.3,
                        "partial_load_pressure": 4.1
                    },
                    {
                        "full_load_pressure": 11.8,
                        "partial_load_pressure": 3.9
                    }
                ],
                "status": "Prihvaćeno"
            },
            "backflow": {
                "risk_level": "Nizak",
                "status": "Prihvaćeno"
            },
            "temperature_conditions": {
                "outlet_temperature": 85.0,
                "min_temperature": 60.0,
                "dew_point": 45.2,
                "status": "Prihvaćeno"
            }
        }
        
        data["results"] = results
        st.session_state.chimney_sizing_data = data
        self.mark_as_changed()
