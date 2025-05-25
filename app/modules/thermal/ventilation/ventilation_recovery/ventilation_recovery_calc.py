# modules/thermal/ventilation/ventilation_recovery/ventilation_recovery_calc.py

import streamlit as st
import json
from modules.base import BaseCalculation
from modules.thermal.ventilation.ventilation_recovery.constants import (
    HEAT_LOAD_PERSON,
    LOCAL_RESISTANCE_COEFFICIENTS,
    STANDARD_DUCT_DIAMETERS,
    STANDARD_RECTANGULAR_DIMENSIONS
)
from modules.thermal.ventilation.ventilation_recovery.models_database import (
    get_all_series,
    get_models_by_series,
    find_suitable_models,
    get_model_by_name
)
from modules.thermal.heating.heat_loss.constants import REGIJE_GRADOVI_TEMP
from modules.thermal.ventilation.ventilation_recovery.data_model import initialize_data_structure
from modules.thermal.ventilation.ventilation_recovery.ui import (  # Ispravljeni import
    render_basic_info_tab,
    render_airflow_tab,  # Ispravljeno ime funkcije
    render_ducts_tab,
    render_recuperator_tab,
    render_energy_tab,
    calculate_heater_power as ui_calculate_heater_power  # Preimenovano za izbjegavanje rekurzije
)

# Import other required modules
from modules.thermal.ventilation.ventilation_recovery.heat_recovery import (
    calculate_temperature_after_recuperator,
    calculate_energy_savings,
    calculate_annual_energy_savings
)
from modules.thermal.ventilation.ventilation_recovery.energy_analysis import (
    calculate_electricity_consumption,
    calculate_heater_consumption,
    calculate_cost_savings,
    calculate_payback_period,
    calculate_co2_reduction
)


class VentilationRecoveryCalc(BaseCalculation):
    """Kalkulator za proračun ventilacijskog sustava s rekuperacijom."""
    
    def __init__(self, name="Proračun ventilacije s rekuperacijom"):
        """Inicijalizacija kalkulatora."""
        super().__init__(name)
        
        # Inicijalizacija session state
        if "ventilation_recovery_data" not in st.session_state:
            st.session_state.ventilation_recovery_data = initialize_data_structure()
    
    def get_velocity_indicators(self, velocity, section_type):
        """
        Vraća indikatore brzine zraka za prikaz u sučelju.
        
        Args:
            velocity (float): Brzina zraka u m/s
            section_type (str): Tip dionice ('main_duct', 'branch', 'terminal')
        
        Returns:
            tuple: (boja, poruka) za prikaz statusa
        """
        ranges = {
            "main_duct": {
                "low": 3.0, 
                "optimal_min": 4.0, 
                "optimal_max": 7.0, 
                "high": 8.0
            },
            "branch": {
                "low": 2.0, 
                "optimal_min": 3.0, 
                "optimal_max": 5.0, 
                "high": 6.0
            },
            "terminal": {
                "low": 1.0, 
                "optimal_min": 2.0, 
                "optimal_max": 3.5, 
                "high": 4.0
            }
        }
        
        # Dohvaćamo granice za traženi tip dionice
        section_ranges = ranges.get(section_type, ranges["main_duct"])
        
        # Određujemo status brzine
        if velocity < section_ranges["low"]:
            return ("orange", "Brzina je preniska - mogući problemi s balansiranjem protoka")
        elif velocity <= section_ranges["optimal_min"]:
            return ("#FFC107", "Brzina je prihvatljiva, ali na nižoj granici")
        elif velocity <= section_ranges["optimal_max"]:
            return ("green", "Brzina je u optimalnom rasponu")
        elif velocity <= section_ranges["high"]:
            return ("#FFC107", "Brzina je prihvatljiva, ali na višoj granici - moguća veća buka")
        else:
            return ("red", "Brzina je previsoka - prevelika buka i pad tlaka")
    
    def render(self):
        """Prikazuje sučelje proračuna."""
        st.title(self.name)
        
        # Stvaranje tabova - promijenjeni redoslijed
        tabs = st.tabs([
            "Osnovni podaci", 
            "Protok zraka", 
            "Rekuperator i grijač",
            "Kanali i padovi tlaka", 
            "Energetska analiza"
        ])
        
        # Prikaz pojedinih tabova - promijenjeni redoslijed
        with tabs[0]:
            render_basic_info_tab(self)
        
        with tabs[1]:
            render_airflow_tab(self)  # Ispravljeno ime funkcije
        
        with tabs[2]:
            render_recuperator_tab(self)
            
        with tabs[3]:
            render_ducts_tab(self)
        
        with tabs[4]:
            render_energy_tab(self)
    
    def calculate_heater_power(self):
        """Izračunava potrebnu snagu električnog grijača."""
        ui_calculate_heater_power(self)  # Ispravljeno kako bi izbjegao rekurziju
    
    def mark_as_changed(self):
        """
        Označava da su podaci kalkulatora promijenjeni i bilježi stanje za undo/redo.
        """
        self.record_state("Promjena parametara")

    def get_state(self):
        """Vraća trenutno stanje proračuna za undo/redo."""
        return json.dumps(st.session_state.ventilation_recovery_data)
    
    def restore_state(self, state):
        """Vraća stanje proračuna iz snimljenog stanja."""
        st.session_state.ventilation_recovery_data = json.loads(state)
    
    def get_default_filename(self):
        """Vraća standardno ime datoteke za ovaj proračun."""
        data = st.session_state.ventilation_recovery_data["basic_info"]
        if data["name"]:
            return f"{data['name']}_ventilacija.json"
        else:
            return "ventilacija_s_rekuperacijom.json"
    
    def serialize(self):
        """Pretvara proračun u format za spremanje."""
        return json.dumps(st.session_state.ventilation_recovery_data, indent=2)
    
    def deserialize(self, data):
        """Učitava proračun iz formata za spremanje."""
        try:
            st.session_state.ventilation_recovery_data = json.loads(data)
            return True
        except Exception as e:
            st.error(f"Greška prilikom učitavanja podataka: {e}")
            return False
    
    def export_to_word(self, doc):
        """Izvozi proračun u Word dokument."""
        data = st.session_state.ventilation_recovery_data
        
        # Dodavanje naslova
        doc.add_heading(self.name, level=1)
        
        # Osnovni podaci
        doc.add_heading("Osnovni podaci", level=2)
        basic_info = data["basic_info"]
        
        if basic_info["name"]:
            doc.add_paragraph(f"Naziv projekta: {basic_info['name']}")
        
        if basic_info["location"]:
            doc.add_paragraph(f"Lokacija: {basic_info['location']}")
        
        doc.add_paragraph(f"Površina prostora: {basic_info['area']} m²")
        doc.add_paragraph(f"Visina prostora: {basic_info['height']} m")
        doc.add_paragraph(f"Volumen prostora: {basic_info['volume']} m³")
        doc.add_paragraph(f"Broj osoba: {basic_info['occupants']}")
        doc.add_paragraph(f"Projektna vanjska temperatura: {basic_info['temperatures']['outdoor']} °C")
        doc.add_paragraph(f"Unutarnja temperatura: {basic_info['temperatures']['indoor']} °C")
        
        # Protok zraka
        doc.add_heading("Proračun protoka zraka", level=2)
        airflow = data["airflow"]
        
        # Metode proračuna
        methods_used = []
        for method_name, method_data in airflow["methods"].items():
            if method_data["enabled"]:
                # Prevedeni nazivi metoda
                method_names = {
                    "by_occupants": "prema broju osoba",
                    "by_area": "prema površini",
                    "by_thermal_load": "prema toplinskom opterećenju",
                    "by_air_changes": "prema broju izmjena zraka"
                }
                
                method_label = method_names.get(method_name, method_name)
                methods_used.append(f"{method_label} ({method_data['result']:.1f} m³/h)")
        
        if methods_used:
            doc.add_paragraph(f"Korištene metode proračuna: {', '.join(methods_used)}")
        
        doc.add_paragraph(f"Konačni odabrani protok zraka: {airflow['final_flow']:.1f} m³/h")
        
        # Rekuperator
        recuperator = data["recuperator"]
        if recuperator["selected_model"]:
            doc.add_heading("Odabrani rekuperator", level=2)
            doc.add_paragraph(f"Model: {recuperator['selected_model']}")
            doc.add_paragraph(f"Serija: {recuperator['series']}")
            doc.add_paragraph(f"Priključci: {recuperator['connections']}")
            doc.add_paragraph(f"Protok: {recuperator['flow_capacity']} m³/h")
            doc.add_paragraph(f"Opterećenje: {recuperator['load_percentage']:.1f}%")
            
            if isinstance(recuperator['pressure_capacity'], dict):
                doc.add_paragraph(f"Raspoloživi tlak (dovod/odsis): {recuperator['pressure_capacity']['supply']}/{recuperator['pressure_capacity']['extract']} Pa")
            else:
                doc.add_paragraph(f"Raspoloživi tlak: {recuperator['pressure_capacity']} Pa")
            
            doc.add_paragraph(f"Učinkovitost: {recuperator['efficiency']*100:.0f}%")
        
        # Električni grijač
        heater = data["heater"]
        doc.add_heading("Električni grijač", level=2)
        
        doc.add_paragraph(f"Temperatura nakon rekuperatora: {heater['temperature_after_recuperator']:.1f} °C")
        doc.add_paragraph(f"Ciljna temperatura nakon grijača: {heater['target_temperature']:.1f} °C")
        
        if heater["temperature_after_recuperator"] >= heater["target_temperature"]:
            doc.add_paragraph("Električni grijač nije potreban jer je temperatura nakon rekuperatora već dovoljno visoka.")
        else:
            doc.add_paragraph(f"Potrebna snaga grijača: {heater['required_power']:.2f} kW")
            doc.add_paragraph(f"Snaga s faktorom sigurnosti: {heater['final_power']:.2f} kW")
            doc.add_paragraph(f"Standardna snaga: {heater['standard_power']:.2f} kW")

        # Kanali i padovi tlaka
        doc.add_heading("Kanali i padovi tlaka", level=2)
        ducts = data["ducts"]

        # Ukupni pad tlaka
        doc.add_paragraph(f"Ukupni pad tlaka sustava: {ducts['total_pressure_drop']:.1f} Pa")

        # Pregled po sustavu
        for system_name, system_label in [
            ("fresh_air", "Svježi zrak (vanjski → rekuperator)"),
            ("supply", "Tlačni razvod (rekuperator → prostor)"),
            ("extract", "Odsisni razvod (prostor → rekuperator)"),
            ("exhaust", "Istrošeni zrak (rekuperator → vanjski)")
        ]:
            # Provjera ima li dionica u ovom sustavu
            if system_name in ducts["branch_structure"] and ducts["branch_structure"][system_name]["sections"]:
                doc.add_heading(system_label, level=3)
                
                # Glavne dionice
                for section in ducts["branch_structure"][system_name]["sections"]:
                    doc.add_paragraph(f"Dionica: {section['name']}")
                    doc.add_paragraph(f"  Protok: {section['flow_rate']:.1f} m³/h")
                    doc.add_paragraph(f"  Duljina: {section['length']:.1f} m")
                    
                    if section["duct_type"] == "round":
                        doc.add_paragraph(f"  Tip: Kružni, promjer: {section['dimensions']['diameter']} mm")
                    else:
                        doc.add_paragraph(f"  Tip: Pravokutni, dimenzije: {section['dimensions']['width']} × {section['dimensions']['height']} mm")
                    
                    doc.add_paragraph(f"  Brzina: {section['velocity']:.2f} m/s")
                    doc.add_paragraph(f"  Pad tlaka: {section['pressure_drop']['total']:.1f} Pa")
                
                # Grane (samo za tlačni i odsisni razvod)
                if system_name in ["supply", "extract"] and "branches" in ducts["branch_structure"][system_name]:
                    branches = ducts["branch_structure"][system_name]["branches"]
                    if branches:
                        doc.add_paragraph(f"Broj grana: {len(branches)}")
                        
                        for i, branch in enumerate(branches):
                            doc.add_paragraph(f"Grana {i+1}: {branch.get('name', '')}")
                            
                            for section in branch["sections"]:
                                doc.add_paragraph(f"  Dionica: {section['name']}")
                                doc.add_paragraph(f"    Protok: {section['flow_rate']:.1f} m³/h")
                                doc.add_paragraph(f"    Duljina: {section['length']:.1f} m")
                                
                                if section["duct_type"] == "round":
                                    doc.add_paragraph(f"    Tip: Kružni, promjer: {section['dimensions']['diameter']} mm")
                                else:
                                    doc.add_paragraph(f"    Tip: Pravokutni, dimenzije: {section['dimensions']['width']} × {section['dimensions']['height']} mm")
                                
                                doc.add_paragraph(f"    Brzina: {section['velocity']:.2f} m/s")
                                doc.add_paragraph(f"    Pad tlaka: {section['pressure_drop']['total']:.1f} Pa")

        # Energetska analiza
        energy = data["energy"]
        if energy["annual_savings"] > 0:
            doc.add_heading("Energetska analiza", level=2)
            
            doc.add_paragraph(f"Godišnja ušteda energije: {energy['annual_savings']:.0f} kWh/god")
            doc.add_paragraph(f"Potrošnja rekuperatora: {energy['electricity_consumption']:.0f} kWh/god")
            doc.add_paragraph(f"Potrošnja grijača: {energy['heater_consumption']:.0f} kWh/god")
            
            doc.add_paragraph(f"Godišnja financijska ušteda: {energy['annual_cost_savings']:.0f} €/god")
            
            if energy["payback_period"] > 50:
                doc.add_paragraph("Period povrata investicije: Više od 50 godina")
            else:
                doc.add_paragraph(f"Period povrata investicije: {energy['payback_period']:.1f} godina")
            
            doc.add_paragraph(f"Smanjenje emisije CO2: {energy['co2_reduction']:.0f} kg/god")

        return doc