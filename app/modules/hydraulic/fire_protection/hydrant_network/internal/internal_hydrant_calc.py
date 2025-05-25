"""
Glavna klasa kalkulatora unutarnje hidrantske mreže.
"""
from modules.base import BaseCalculation
import streamlit as st

from .constants import FIRE_LOAD_FLOW_TABLE
from .calculation_utils import calculate_pressure_losses, calculate_hydrant_height
from ..common.constants import MIN_REQUIRED_PRESSURE_BAR
from ..common.pipe_data import PIPE_DATA

from .ui.basic_params import render_basic_params
from .ui.height_params import render_height_params
from .ui.pipe_selection import render_pipe_selection
from .ui.results import render_results

class InternalHydrantCalculator(BaseCalculation):
    """Kalkulator unutarnje hidrantske mreže za gašenje požara."""
    
    def __init__(self, name="Kalkulator unutarnje hidrantske mreže"):
        """Inicijalizacija kalkulatora."""
        super().__init__(name)
        if "internal_hydrant_data" not in st.session_state:
            st.session_state.internal_hydrant_data = self.initialize_data_structure()
    
    def initialize_data_structure(self):
        """Inicijalizira strukturu podataka."""
        return {
            "parameters": {
                # Osnovni parametri
                "inlet_pressure": 4.5,  # bar
                "fire_load": 500,  # MJ/m²
                "floor_count": 3,
                "hydrants_per_floor": 3,
                "simultaneous_hydrants": 2,
                
                # Visinski parametri
                "pipe_depth": 1.0,  # m
                "ground_to_first_floor": 0.5,  # m
                "standard_floor_height": 3.0,  # m
                "different_floor_heights": False,
                "floor_heights": {},
                "hydrant_height": 1.5,  # m
                "worst_case_floor": 3,
                
                # Parametri cjevovoda
                "pipe_lengths": {
                    "horizontal": 10.0,  # m
                    "floor": 15.0  # m
                },
                "pipe_diameters": {
                    "horizontal": "DN 50",
                    "riser": "DN 50",
                    "floor": "DN 50"
                },
                "local_elements": {
                    "horizontal": {
                        "koljeno_90": 2,
                        "t_spoj_prolaz": 1,
                        "t_spoj_odvajanje": 1,
                        "ventil_zapor": 1
                    },
                    "riser": {
                        "koljeno_90": 2,
                        "t_spoj_odvajanje": 3
                    },
                    "floor": {
                        "koljeno_90": 3,
                        "t_spoj_prolaz": 1,
                        "t_spoj_odvajanje": 1,
                        "ventil_zapor": 1
                    }
                }
            },
            "results": {}
        }
    
    def render(self):
        """Glavna metoda za prikaz korisničkog sučelja."""
        st.title(self.name)
        
        # Organizacija kroz tabove
        tab1, tab2, tab3 = st.tabs(["Osnovni parametri", "Cjevovod i promjeri", "Rezultati"])
        
        with tab1:
            render_basic_params(self)
            render_height_params(self)
        
        with tab2:
            render_pipe_selection(self)
        
        with tab3:
            render_results(self)
    
    def update_calculation(self):
        """Callback funkcija koja se poziva pri svakoj promjeni inputa."""
        self.sync_inputs_to_state()
        self.calculate()
        self.state_manager.set_calculation_changed(True)
    
    def sync_inputs_to_state(self):
        """Sinkronizira ulazne vrijednosti iz widgeta u strukturu podataka."""
        data = st.session_state.internal_hydrant_data
        params = data["parameters"]
        
        # Osnovni parametri
        for key in ["inlet_pressure", "fire_load", "floor_count", "hydrants_per_floor", "simultaneous_hydrants"]:
            if key in st.session_state:
                params[key] = st.session_state[key]
        
        # Visinski parametri
        for key in ["pipe_depth", "ground_to_first_floor", "standard_floor_height", 
                   "different_floor_heights", "hydrant_height", "worst_case_floor"]:
            if key in st.session_state:
                params[key] = st.session_state[key]
        
        # Visine pojedinih etaža
        if params["different_floor_heights"]:
            params["floor_heights"] = {}
            for i in range(1, params["floor_count"] + 1):
                key = f"floor_height_{i}"
                if key in st.session_state:
                    params["floor_heights"][i] = st.session_state[key]
        
        # Parametri cjevovoda
        # Duljine cijevi
        for section in ["horizontal", "floor"]:
            key = f"{section}_pipe_length"
            if key in st.session_state:
                params["pipe_lengths"][section] = st.session_state[key]
        
        # Promjeri cijevi
        for section in ["horizontal", "riser", "floor"]:
            key = f"{section}_pipe_diameter"
            if key in st.session_state:
                params["pipe_diameters"][section] = st.session_state[key]
        
        # Lokalni elementi
        for section in ["horizontal", "riser", "floor"]:
            for element_type in ["bends_90", "t_pass", "t_branch", "valves"]:
                key = f"{section}_{element_type}"
                if key in st.session_state:
                    element_key = "koljeno_90" if element_type == "bends_90" else \
                                 "t_spoj_prolaz" if element_type == "t_pass" else \
                                 "t_spoj_odvajanje" if element_type == "t_branch" else \
                                 "ventil_zapor"
                    params["local_elements"][section][element_key] = st.session_state[key]
    
    def calculate(self):
        """Izvodi glavne izračune."""
        data = st.session_state.internal_hydrant_data
        
        # 1. Izračunaj potreban protok po hidrantu
        flow_per_hydrant = FIRE_LOAD_FLOW_TABLE.get_flow_for_load(data["parameters"]["fire_load"])
        data["results"]["flow_per_hydrant"] = flow_per_hydrant
        
        # 2. Izračunaj ukupni protok
        total_flow_l_min = flow_per_hydrant * data["parameters"]["simultaneous_hydrants"]
        total_flow_l_s = total_flow_l_min / 60
        data["results"]["total_flow_l_min"] = total_flow_l_min
        data["results"]["total_flow_l_s"] = total_flow_l_s
        data["parameters"]["total_flow_l_s"] = total_flow_l_s  # Za korištenje u proračunu
        
        # 3. Izračunaj ukupnu visinu hidranta
        total_height = calculate_hydrant_height(
            data["parameters"]["ground_to_first_floor"],
            data["parameters"]["standard_floor_height"],
            data["parameters"]["different_floor_heights"],
            data["parameters"]["floor_heights"],
            data["parameters"]["worst_case_floor"],
            data["parameters"]["hydrant_height"]
        )
        data["results"]["total_hydrant_height"] = total_height
        
        # 4. Izračunaj ukupnu visinsku razliku (uračunaj dubinu cijevi)
        # Ukupna visinska razlika = visina hidranta od tla + dubina horizontalnog voda od vodomjera
        pipe_depth = data["parameters"]["pipe_depth"]
        total_height_difference = total_height + pipe_depth
        
        data["results"]["total_height_difference"] = total_height_difference
        data["parameters"]["total_height"] = total_height_difference  # Za korištenje u proračunu
        
        # 5. Izračunaj gubitke tlaka
        pressure_losses = calculate_pressure_losses(data["parameters"])
        data["results"].update(pressure_losses)
        
        # 6. Izračunaj preostali tlak
        remaining_pressure = data["parameters"]["inlet_pressure"] - data["results"]["total_loss"]
        data["results"]["remaining_pressure"] = remaining_pressure
        
        # 7. Provjeri zadovoljenje uvjeta
        data["results"]["meets_requirements"] = remaining_pressure >= MIN_REQUIRED_PRESSURE_BAR
        
        return data["results"]
    
    def export_to_word(self, doc):
        """Izvozi proračun u Word dokument."""
        data = st.session_state.internal_hydrant_data
        
        # Naslov dokumenta
        doc.add_heading(self.name, level=1)
        
        # Osnovni parametri
        doc.add_heading("Osnovni parametri", level=2)
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        
        # Zaglavlje tablice
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Parametar"
        hdr_cells[1].text = "Vrijednost"
        
        # Dodavanje osnovnih parametara
        params = [
            ("Specifično požarno opterećenje", f"{data['parameters']['fire_load']} MJ/m²"),
            ("Raspoloživi tlak na priključku", f"{data['parameters']['inlet_pressure']} bar"),
            ("Broj etaža", str(data['parameters']['floor_count'])),
            ("Broj hidranata po etaži", str(data['parameters']['hydrants_per_floor'])),
            ("Broj istovremeno korištenih hidranata", str(data['parameters']['simultaneous_hydrants'])),
            ("Protok po hidrantu", f"{data['results']['flow_per_hydrant']} l/min"),
            ("Ukupni protok", f"{data['results']['total_flow_l_min']} l/min")
        ]
        
        for param, value in params:
            row_cells = table.add_row().cells
            row_cells[0].text = param
            row_cells[1].text = value
        
        # Visinski parametri
        doc.add_heading("Visinski parametri", level=2)
        table = doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'
        
        # Zaglavlje tablice
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = "Parametar"
        hdr_cells[1].text = "Vrijednost"
        
        height_params = [
            ("Dubina horizontalnog voda", f"{data['parameters']['pipe_depth']} m"),
            ("Visina od tla do prve etaže", f"{data['parameters']['ground_to_first_floor']} m"),
            ("Visina etaže", f"{data['parameters']['standard_floor_height']} m"),
            ("Etaža najnepovoljnijeg hidranta", str(data['parameters']['worst_case_floor'])),
            ("Visina hidranta od poda", f"{data['parameters']['hydrant_height']} m"),
            ("Ukupna visina hidranta od tla", f"{data['results']['total_hydrant_height']:.2f} m"),
            ("Ukupna visinska razlika", f"{data['results']['total_height_difference']:.2f} m")
        ]
        
        for param, value in height_params:
            row_cells = table.add_row().cells
            row_cells[0].text = param
            row_cells[1].text = value