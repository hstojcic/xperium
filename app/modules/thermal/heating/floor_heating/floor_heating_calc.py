import streamlit as st
import pandas as pd
import math
import json
from datetime import datetime
from modules.base import BaseCalculation
from modules.thermal.heating.floor_heating.constants import *
from modules.thermal.heating.floor_heating.kh_values import KH_VALUES
from modules.thermal.heating.floor_heating.utils import *
from modules.thermal.heating.floor_heating.flow_adjuster import FlowAdjuster
from modules.thermal.heating.floor_heating.floor_heating_calculator_core import FloorHeatingCalculatorCore
from modules.thermal.heating.floor_heating.floor_heating_ui import FloorHeatingUI, apply_custom_styles
from modules.thermal.heating.floor_heating.floor_heating_data import FloorHeatingDataManager


class FloorHeatingCalc(BaseCalculation):
    """Kalkulator podnog grijanja."""
    
    def __init__(self, name="Proračun podnog grijanja"):
        """Inicijalizacija kalkulatora podnog grijanja."""
        super().__init__(name)
        
        # Initialize core calculator
        self.core_calculator = FloorHeatingCalculatorCore()
        
        # Initialize UI and data managers
        self.data_manager = FloorHeatingDataManager(self)
        self.ui_manager = FloorHeatingUI(self)
        
        # Inicijalizacija session state varijabli ako ne postoje
        self.initialize_session_state()
    
    def get_calculation_id(self):
        """
        Generira jedinstveni ID za trenutni izračun.
        Koristi se za praćenje kada je kreiran novi izračun.
        """
        # Dohvati trenutni ID izračuna iz BaseCalculation klase
        if hasattr(self, 'calculation_id') and self.calculation_id:
            return self.calculation_id
        
        # Ako nemamo ID iz BaseCalculation, generiraj novi
        import uuid
        return str(uuid.uuid4())
    
    def initialize_session_state(self, force_reset=False):
        """Inicijalizira session state varijable za kalkulator podnog grijanja."""
        # Ako je postavljen force_reset ili imamo novi ID kalkulacije, resetiraj sve
        calc_id = self.get_calculation_id()
        current_calc_id = st.session_state.get("floor_heating_calc_id", None)
        
        if force_reset or calc_id != current_calc_id:
            # Resetiraj sve varijable za novi izračun
            st.session_state.floor_heating_data = self.data_manager.initialize_data_structure()
            st.session_state.floor_heating_flow_adjustments = {}
            st.session_state.floor_heating_changed = False
            st.session_state.floor_heating_first_load = True
            st.session_state.floor_heating_calc_id = calc_id
        else:
            # Samo inicijaliziraj ako ne postoje
            if "floor_heating_data" not in st.session_state:
                st.session_state.floor_heating_data = self.data_manager.initialize_data_structure()
                
            if "floor_heating_flow_adjustments" not in st.session_state:
                st.session_state.floor_heating_flow_adjustments = {}
                
            if "floor_heating_changed" not in st.session_state:
                st.session_state.floor_heating_changed = False
                
            if "floor_heating_first_load" not in st.session_state:
                st.session_state.floor_heating_first_load = True
    
    def render(self):
        """Prikazuje sučelje kalkulatora"""
        apply_custom_styles()
        
        # Dohvati podatke iz sesije
        data = st.session_state.floor_heating_data
        
        # Migracija podataka iz stare u novu strukturu ako je potrebno
        self.data_manager.migrate_data_if_needed(data)
        
        # Kreiraj tabove
        tab_building, tab_loops, tab_results = st.tabs(["Zgrada i razdjelnici", "Petlje podnog grijanja", "Rezultati"])
        
        # Tab za zgradu i razdjelnike
        with tab_building:
            self.ui_manager.render_building_tab(data)
            
        # Tab za petlje podnog grijanja
        with tab_loops:
            self.ui_manager.render_loops_tab(data)
            
        # Tab za rezultate
        with tab_results:
            self.ui_manager.render_results_tab(data)
            
        # Izračunaj sve petlje pri prvom otvaranju
        if st.session_state.get("floor_heating_first_load", True):
            self.calculate_all_loops(data)
            st.session_state.floor_heating_first_load = False
    
    def mark_as_changed(self):
        """Označava da su napravljene promjene u proračunu."""
        # Postavi zastavicu da su napravljene promjene - korisno za praćenje spremanja
        st.session_state.floor_heating_changed = True
        
        # Ažuriraj vrijeme modificiranja
        data = st.session_state.floor_heating_data
        if "meta" in data:
            data["meta"]["modified"] = datetime.now().isoformat()
    
    def calculate_all_loops(self, data):
        """Izračunava sve petlje u zgradi."""
        # Proći kroz sve etaže, razdjelnike i petlje
        for floor in data["building"]["floors"]:
            for manifold in floor["manifolds"]:
                for loop in manifold["loops"]:
                    # Izračunaj petlju samo ako ima sve potrebne podatke
                    has_area = "area" in loop and loop["area"] is not None and loop["area"] > 0
                    has_manifold_distance = "manifold_distance" in loop and loop["manifold_distance"] is not None
                    has_pipe_spacing = "pipe_spacing" in loop and loop["pipe_spacing"] is not None
                    
                    if has_area and has_manifold_distance and has_pipe_spacing:
                        # Kreiraj prilagođene parametre za ovu petlju
                        custom_params = {
                            "screed_thickness": floor.get("screed_thickness", 45),
                            "flow_temperature": manifold.get("flow_temperature", 35),
                            "delta_t": manifold.get("delta_t", 5),
                            "pipe_diameter": manifold.get("pipe_diameter", "16x2,0")
                        }
                        self._calculate_single_loop(loop, custom_params)
    
    def _calculate_single_loop(self, loop, custom_params=None):
        """Izračunava pojedinu petlju."""
        try:
            if not custom_params:
                custom_params = st.session_state.floor_heating_data["common_params"]
            
            # Provjeri jesu li potrebni parametri uneseni
            if "area" not in loop or loop["area"] is None or loop["area"] <= 0:
                return
            
            if "manifold_distance" not in loop or loop["manifold_distance"] is None:
                return
            
            # Dohvati potrebne parametre
            area = loop["area"]
            room_temp = loop["room_temperature"]
            pipe_spacing = loop["pipe_spacing"]
            r_lambda = loop["r_lambda"]
            manifold_distance = loop["manifold_distance"]
            
            # Izračunaj rezultate - ispravka naziva metode
            results = self.core_calculator.calculate_single_loop(
                loop=loop,
                common_params=custom_params
            )
            
            # Spremi rezultate
            loop["results"] = results
            
        except Exception as e:
            st.error(f"Greška pri izračunu petlje: {str(e)}")
            raise e
    
    # === Event handleri za UI komponentu ===
    def _on_building_name_change(self, data):
        """Handler za promjenu imena zgrade."""
        if "building_name" in st.session_state:
            data["building"]["name"] = st.session_state.building_name
            self.mark_as_changed()
    
    def _add_floor(self, data):
        """Dodaje novu etažu u zgradu."""
        self.data_manager.add_floor(data)
    
    def _delete_floor(self, floor_id, data):
        """Briše etažu po ID-u."""
        self.data_manager.delete_floor(floor_id, data)
    
    def _on_floor_param_change(self, floor_id, param_name, data):
        """Handler za promjenu parametra etaže."""
        # Dohvati novu vrijednost
        param_key = f"{param_name}_{floor_id}"
        if param_key not in st.session_state:
            return
        
        value = st.session_state[param_key]
        
        # Pronađi etažu
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                floor[param_name] = value
                
                # Posebna obrada za debljinu estriha - ažuriraj sve petlje na ovoj etaži
                if param_name == "screed_thickness":
                    for manifold in floor.get("manifolds", []):
                        # Ažuriraj sve petlje u razdjelniku
                        for loop in manifold.get("loops", []):
                            # Izračunaj petlju s novom debljinom estriha (modified common_params)
                            custom_params = data["common_params"].copy()
                            custom_params["screed_thickness"] = value
                            custom_params["flow_temperature"] = manifold.get("flow_temperature", 35)
                            custom_params["delta_t"] = manifold.get("delta_t", 5)
                            custom_params["pipe_diameter"] = manifold.get("pipe_diameter", "16x2,0")
                            self._calculate_single_loop(loop, custom_params)
                
                break
        
        # Označi da ima promjena
        self.mark_as_changed()
    
    def _add_manifold(self, floor, data):
        """Dodaje novi razdjelnik na etažu."""
        self.data_manager.add_manifold(floor, data)
    
    def _delete_manifold(self, floor_id, manifold_id, data):
        """Briše razdjelnik po ID-u."""
        self.data_manager.delete_manifold(floor_id, manifold_id, data)
    
    def _on_manifold_param_change(self, floor_id, manifold_id, param_name, data):
        """Handler za promjenu parametra razdjelnika."""
        # Dohvati novu vrijednost
        param_key = f"{param_name}_{floor_id}_{manifold_id}"
        if param_key not in st.session_state:
            return
        
        value = st.session_state[param_key]
        
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        manifold[param_name] = value
                        
                        # Posebna obrada za parametre koji utječu na proračun petlji
                        recalculate_params = ["flow_temperature", "delta_t", "pipe_diameter"]
                        if param_name in recalculate_params:
                            # Ažuriraj sve petlje u razdjelniku
                            for loop in manifold.get("loops", []):
                                # Izračunaj petlju s novim parametrom
                                custom_params = data["common_params"].copy()
                                custom_params["screed_thickness"] = floor.get("screed_thickness", 45)
                                custom_params["flow_temperature"] = manifold.get("flow_temperature", 35)
                                custom_params["delta_t"] = manifold.get("delta_t", 5)
                                custom_params["pipe_diameter"] = manifold.get("pipe_diameter", "16x2,0")
                                self._calculate_single_loop(loop, custom_params)
                        
                        break
                break
        
        # Označi da ima promjena
        self.mark_as_changed()
    
    def _on_manifold_circuits_change(self, floor_id, manifold_id, data):
        """Handler za promjenu broja krugova razdjelnika."""
        # Dohvati novu vrijednost
        param_key = f"num_circuits_{floor_id}_{manifold_id}"
        if param_key not in st.session_state:
            return
        
        num_circuits = st.session_state[param_key]
        
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        # Spremi stari i novi broj krugova
                        old_num = manifold.get("num_circuits", 4)
                        manifold["num_circuits"] = num_circuits
                        
                        # Automatizirano sinkroniziranje broja prostorija s brojem krugova razdjelnika
                        self.data_manager.sync_rooms_with_circuits(floor_id, manifold_id, data)
                        
                        break
                break
        
        # Označi da ima promjena
        self.mark_as_changed()
    
    def _add_room_to_manifold(self, floor_id, manifold_id, data):
        """Dodaje novu prostoriju na razdjelnik."""
        self.data_manager.add_room_to_manifold(floor_id, manifold_id, data)
    
    def _delete_room_from_manifold(self, floor_id, manifold_id, room_id, data):
        """Briše prostoriju s razdjelnika."""
        self.data_manager.delete_room_from_manifold(floor_id, manifold_id, room_id, data)
    
    def _on_room_param_change(self, floor_id, manifold_id, room_id, param_name, data):
        """Handler za promjenu parametra prostorije."""
        # Dohvati novu vrijednost
        param_key = f"room_name_{floor_id}_{manifold_id}_{room_id}"
        if param_key not in st.session_state:
            return
        
        value = st.session_state[param_key]
        
        # Pronađi prostoriju i odgovarajuću petlju
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        # Ažuriraj ime prostorije
                        for room in manifold.get("rooms", []):
                            if room.get("id") == room_id:
                                room[param_name] = value
                                break
                        
                        # Ažuriraj i odgovarajuću petlju
                        for loop in manifold.get("loops", []):
                            if loop.get("id") == room_id:
                                loop["room_name"] = value
                                
                                # Automatski postavi preporučenu temperaturu
                                default_temp = get_room_temperature_for_name(value)
                                loop["room_temperature"] = default_temp
                                
                                # Izračunaj petlju s novim imenom prostorije ako je potpuna
                                has_area = "area" in loop and loop["area"] is not None and loop["area"] > 0
                                has_manifold_distance = "manifold_distance" in loop and loop["manifold_distance"] is not None
                                has_pipe_spacing = "pipe_spacing" in loop and loop["pipe_spacing"] is not None
                                
                                if has_area and has_manifold_distance and has_pipe_spacing:
                                    # Izračunaj petlju
                                    custom_params = data["common_params"].copy()
                                    custom_params["screed_thickness"] = floor.get("screed_thickness", 45)
                                    custom_params["flow_temperature"] = manifold.get("flow_temperature", 35)
                                    custom_params["delta_t"] = manifold.get("delta_t", 5)
                                    custom_params["pipe_diameter"] = manifold.get("pipe_diameter", "16x2,0")
                                    self._calculate_single_loop(loop, custom_params)
                                
                                break
                        
                        break
                break
        
        # Označi da ima promjena
        self.mark_as_changed()
    
    def _move_room_up(self, floor_id, manifold_id, room_id, data):
        """Pomakni prostoriju jedan korak više na razdjelniku."""
        result = self.data_manager.move_room_up(floor_id, manifold_id, room_id, data)
        
        # Ažuriraj brojeve prostorija nakon pomicanja
        self.data_manager.update_room_numbers(floor_id, manifold_id, data)
        
        return result
    
    def _move_room_down(self, floor_id, manifold_id, room_id, data):
        """Pomakni prostoriju jedan korak niže na razdjelniku."""
        result = self.data_manager.move_room_down(floor_id, manifold_id, room_id, data)
        
        # Ažuriraj brojeve prostorija nakon pomicanja
        self.data_manager.update_room_numbers(floor_id, manifold_id, data)
        
        return result
    
    def _on_floor_or_manifold_selector_change(self):
        """Handler za promjenu odabrane etaže ili razdjelnika u tabu petlji."""
        # Spremi odabrane indekse u session_state
        if "loops_floor_selector" in st.session_state:
            st.session_state.selected_floor_index = st.session_state.loops_floor_selector
        
        if "loops_manifold_selector" in st.session_state:
            st.session_state.selected_manifold_index = st.session_state.loops_manifold_selector
    
    def _auto_calculate_loop_if_possible_with_manifold(self, loop_id, data, floor, manifold):
        """Automatski izračunava petlju ako su svi potrebni parametri uneseni (za petlje iz razdjelnika)."""
        # Pronađi petlju u razdjelniku
        for loop in manifold.get("loops", []):
            if loop.get("id") == loop_id:
                # Provjeri jesu li svi parametri uneseni
                has_area = "area" in loop and loop["area"] is not None and loop["area"] > 0
                has_manifold_distance = "manifold_distance" in loop and loop["manifold_distance"] is not None
                has_pipe_spacing = "pipe_spacing" in loop and loop["pipe_spacing"] is not None
                
                # Ako su svi potrebni parametri uneseni, izračunaj petlju
                if has_area and has_manifold_distance and has_pipe_spacing:
                    # Kreiraj prilagođene parametre za ovu petlju
                    custom_params = self.data_manager.get_custom_params_for_loop(loop, floor, manifold)
                    self._calculate_single_loop(loop, custom_params)
                
                break
    
    def _on_loop_param_change_with_manifold(self, loop_id, param_name, data, floor, manifold):
        """Handler za promjenu parametra petlje za petlje iz razdjelnika."""
        # Provjeri postoji li ključ u session state prije pristupa
        if param_name == "pipe_spacing":
            # Za razmak cijevi koristimo drugačiji ključ (spacing_{loop_id} umjesto pipe_spacing_{loop_id})
            param_key = f"spacing_{loop_id}"
            # Za razmak cijevi izvuci broj iz stringa "15 cm"
            if param_key in st.session_state:
                spacing_str = st.session_state[param_key]
                value = int(spacing_str.split()[0])
            else:
                # Ako ključ ne postoji, koristimo default vrijednost i završavamo funkciju
                return
        else:
            param_key = f"{param_name}_{loop_id}"
            if param_key not in st.session_state:
                return
            value = st.session_state[param_key]
        
        # Ažuriraj podatke petlje
        for loop in manifold.get("loops", []):
            if loop.get("id") == loop_id:
                loop[param_name] = value
                
                # Automatski izračunaj ako su svi potrebni parametri uneseni
                self._auto_calculate_loop_if_possible_with_manifold(loop_id, data, floor, manifold)
                break
        
        # Označi da ima promjena
        self.mark_as_changed()
    
    def _on_covering_change_with_manifold(self, loop_id, data, floor, manifold):
        """Handler za promjenu podne obloge za petlje iz razdjelnika."""
        # Dohvati odabranu opciju iz widgeta samo ako postoji u session state
        covering_key = f"covering_{loop_id}"
        if covering_key not in st.session_state:
            return
            
        selected_covering = st.session_state[covering_key]
        
        # Ponovno generiraj isti covering_options lista kao u _render_loop_card
        covering_options = [cov["name"] + f" (R_λB = {cov['r_lambda']})" for cov in FLOOR_COVERINGS]
        
        # Nađi indeks odabrane opcije
        try:
            covering_index = covering_options.index(selected_covering)
        except ValueError:
            # Fallback ako ne možemo naći točno poklapanje
            st.error(f"Greška: Nije moguće pronaći '{selected_covering}' u opcijama.")
            covering_index = 0  # Default na prvu opciju
        
        # Nađi r_lambda vrijednost
        r_lambda = FLOOR_COVERINGS[covering_index]["r_lambda"]
        covering_name = FLOOR_COVERINGS[covering_index]["name"]
        
        # Ažuriraj podatke petlje
        for loop in manifold.get("loops", []):
            if loop.get("id") == loop_id:
                loop["r_lambda"] = r_lambda
                loop["floor_covering_name"] = covering_name
                
                # Izračunaj petlju
                self._auto_calculate_loop_if_possible_with_manifold(loop_id, data, floor, manifold)
                break
        
        # Označi da ima promjena
        self.mark_as_changed()
    
    def _on_flow_slider_change_with_manifold(self, loop_id, data, floor, manifold):
        """Handler za automatsku primjenu podešavanja protoka prilikom promjene slidera za petlje iz razdjelnika."""
        adjustment = st.session_state[f"flow_adjustment_{loop_id}"]
        self._on_flow_adjustment_with_manifold(loop_id, adjustment, data, floor, manifold)
    
    def _on_flow_adjustment_with_manifold(self, loop_id, adjustment, data, floor, manifold):
        """Handler za podešavanje protoka za petlje iz razdjelnika."""
        # Pronađi petlju
        for loop in manifold.get("loops", []):
            if loop.get("id") == loop_id:
                # Kreiraj prilagođene parametre za ovu petlju
                custom_params = self.data_manager.get_custom_params_for_loop(loop, floor, manifold)
                
                # Podešavanje protoka
                adjusted_results = FlowAdjuster.adjust_flow_by_percentage(
                    loop, custom_params, adjustment
                )
                
                # Spremi podešene rezultate
                if adjusted_results:
                    loop["adjusted_results"] = adjusted_results
                    # Zapamti postotak podešavanja
                    st.session_state.floor_heating_flow_adjustments[loop_id] = adjustment
                else:
                    st.warning("Nije moguće podesiti protok za zadani postotak.")
                
                break
        
        # Označi da ima promjena
        self.mark_as_changed()
    
    def _on_room_type_change(self, floor_id, manifold_id, room_id, data):
        """
        Handler za promjenu tipa prostorije iz padajućeg izbornika.
        Automatski postavlja naziv prostorije i ažurira povezane parametre petlje
        (temperaturu, razmak cijevi, podnu oblogu) prema predefiniranim postavkama.
        """
        # Dohvati odabranu opciju iz padajućeg izbornika
        room_name_key = f"room_name_{floor_id}_{manifold_id}_{room_id}"
        if room_name_key not in st.session_state:
            return
            
        selected_room_type = st.session_state[room_name_key]
        
        # Ako nije odabran tip prostorije, završi
        if not selected_room_type:
            return
        
        # Traži etažu i razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        # Ažuriraj prostoriju
                        for room in manifold.get("rooms", []):
                            if room.get("id") == room_id:
                                # Postavi naziv prostorije
                                room["name"] = selected_room_type
                                
                                # Također ažuriraj odgovarajuću petlju
                                for loop in manifold.get("loops", []):
                                    if loop.get("id") == room_id:
                                        # Postavi naziv prostorije
                                        loop["room_name"] = selected_room_type
                                        
                                        # Postavi preporučenu temperaturu prema tipu prostorije
                                        recommended_temp = self.data_manager.get_room_temperature_for_name(selected_room_type)
                                        loop["room_temperature"] = recommended_temp
                                        
                                        # Postavi preporučeni razmak cijevi prema temperaturi
                                        if recommended_temp >= 24:  # Za kupaonicu i slične (viša temperatura)
                                            recommended_spacing = 10
                                        elif recommended_temp >= 22:  # Za dnevni boravak i sl.
                                            recommended_spacing = 15
                                        else:  # Za ostale prostorije
                                            recommended_spacing = 20
                                        loop["pipe_spacing"] = recommended_spacing
                                        
                                        # Postavi preporučenu podnu oblogu
                                        # Kupaonica obično ima keramičke pločice, dnevni boravak drvo, ostalo prema namjeni
                                        if "Kupao" in selected_room_type:
                                            # Keramičke pločice (prva opcija)
                                            loop["r_lambda"] = 0.00
                                            loop["floor_covering_name"] = "Keramička obloga"
                                        elif "Dnevni" in selected_room_type or "Spava" in selected_room_type:
                                            # Drvena podloga (zadnja opcija)
                                            loop["r_lambda"] = 0.15
                                            loop["floor_covering_name"] = "Drvena obloga"
                                        else:
                                            # Plastična obloga (druga opcija)
                                            loop["r_lambda"] = 0.05
                                            loop["floor_covering_name"] = "Plastična obloga (tanka)"
                                        
                                        # Automatski izračunaj petlju ako su svi potrebni parametri uneseni
                                        self._auto_calculate_loop_if_possible_with_manifold(room_id, data, floor, manifold)
                                        break
                                
                                break
                        
                        break
                break
        
        # Označi da ima promjena
        self.mark_as_changed()