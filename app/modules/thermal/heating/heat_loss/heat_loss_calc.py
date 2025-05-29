"""
Proračun toplinskih gubitaka prema EN 12831
"""

import streamlit as st
import pandas as pd
from modules.base import BaseCalculation

# Importi iz modulariziranih komponenti
from .models.elementi.constants import TIPOVI_PROSTORIJA, TEMP_FAKTORI, DEFAULT_U_VALUES as ORIGINAL_U_VALUES
from .constants import GRADOVI_TEMP, REGIJE_GRADOVI_TEMP, ORIJENTACIJE, CSS_STYLES
from .calculations.heat_loss_calculation import izracunaj_toplinske_gubitke_zgrade, izracunaj_toplinske_gubitke_etaze, izracunaj_toplinske_gubitke_prostorije
from .calculations.transmisijski import izracun_transmisijskih_gubitaka
from .models.model import MultiRoomModel
from .utils.session_manager import is_valid_session_data, initialize_session_data
from .utils.validators import prikazuje_upozorenje_o_povrsinama

# UI komponente
from .ui.etaza_ui import prikazi_manager_etaza, prikazi_postavke_etaze
from .ui.prostorija_ui import prikazi_manager_prostorija, prikazi_osnovne_podatke_prostorije, prikazi_dimenzije_prostorije, prikazi_pod_i_strop_prostorije
from .ui.zid_ui import prikazi_zidove_prostorije
from .ui.results_ui import prikaz_rezultata_zgrade, prikaz_rezultata_etaze, prikaz_rezultata_prostorije
from .ui.gradevinski_elementi_ui import prikazi_manager_gradevinski_elementi

# Kontroleri
from .controllers.etaza_controller import EtazaController
from .controllers.prostorija_controller import ProstorijaController
from .controllers.zid_controller import ZidController
from .controllers.elementi_controller import ElementiController

# Elementi zgrade
from .models.elementi.wall_elements import WallElements
from .models.elementi.building_elements_model import inicijaliziraj_elemente, BuildingElementsModel


class HeatLossCalc(BaseCalculation):
    """
    Klasa za proračun toplinskih gubitaka prema EN 12831
    
    Ova klasa implementira modularnu arhitekturu s jasno odvojenim modelima, 
    kontrolerima i UI komponentama za proračun toplinskih gubitaka.
    """
    
    def __init__(self):
        super().__init__("Proračun toplinskih gubitaka")
        # Definicija ključa za session state za ovaj kalkulator
        self.session_key = "heat_loss_calculator_model"  # Jedinstveni ključ
        self.results_session_key = f"{self.session_key}_rezultati"
        
        # Inicijalizacija parametara proračuna
        self.temp_vanjska = -16.1  # Za Osijek
        self.u_values = ORIGINAL_U_VALUES.copy()
        
        # Initialize thermal bridges parameters with clean defaults
        self.toplinski_mostovi = False
        self.postotak_toplinskih_mostova = 0
        
        # Initialize faktor_sigurnosti
        if 'faktor_sigurnosti_slider' not in st.session_state:
            st.session_state.faktor_sigurnosti_slider = 0
        self.faktor_sigurnosti = st.session_state.faktor_sigurnosti_slider
        
        # Rezultati
        self.rezultati = {}
        self.godisnja_energija = {}
        
        # Modeli i Kontroleri
        self.multi_room_model = None
        self.etaza_controller = None
        self.prostorija_controller = None
        self.zid_controller = None
        
        # Javni API za kompatibilnost s originalnom implementacijom
        self.izracunaj_toplinske_gubitke_prostorije = izracunaj_toplinske_gubitke_prostorije
        self.izracunaj_toplinske_gubitke_etaze = izracunaj_toplinske_gubitke_etaze
        self.izracunaj_toplinske_gubitke_zgrade = izracunaj_toplinske_gubitke_zgrade
        
    def inicijaliziraj_kontrolere(self, model, elements_model):
            """
            Inicijalizira kontrolere za rad s modelom.
            
            Parameters:
            -----------
            model : MultiRoomModel
                Model s više prostorija
            elements_model : BuildingElementsModel
                Model građevinskih elemenata
            """
            self.etaza_controller = EtazaController(model)
            self.prostorija_controller = ProstorijaController(model)            
            self.zid_controller = ZidController(model)
            self.elementi_controller = ElementiController(elements_model)
        
    def render(self):
        """
        Prikazuje sučelje proračuna
        
        Implementacija apstraktne metode iz BaseCalculation
        """
        self._inicijaliziraj_model()

    def _inicijaliziraj_model(self):
        """
        Inicijalizira model i kontrolere za proračun toplinskih gubitaka.
        
        Ova metoda stvara novu instancu MultiRoomModel-a i kontrolera za upravljanje
        modelom, te vrši konverziju modela u sustav fizičkih zidova ako je potrebno.
        """
        # 1. Inicijalizacija modela građevinskih elemenata
        if "elements_model" not in st.session_state:
            st.session_state.elements_model = inicijaliziraj_elemente()
        elements_model = st.session_state.elements_model

        # 2. Inicijalizacija MultiRoomModel-a
        # Konstruktor MultiRoomModel-a interno upravlja učitavanjem stanja
        # iz session_state (ako postoji) ili inicijalizacijom novog modela
        self.multi_room_model = MultiRoomModel(self.session_key)
        
        # 4. Obnavljamo reference između zidova
        self.multi_room_model.restore_shared_elements_references()
        
        # 5. Inicijalizacija kontrolera
        self.inicijaliziraj_kontrolere(self.multi_room_model, elements_model)
        
        # 6. Učitavanje rezultata iz session state-a
        if self.results_session_key in st.session_state:
            self.rezultati = st.session_state[self.results_session_key]
        else:
            self.rezultati = {}        # Definiramo tabove
        tab_names = ["Opće postavke", "Postavke zgrade", "Rezultati po prostorijama", "Rezultati po etažama"]
        tab1, tab2, tab3, tab4 = st.tabs(tab_names)

        with tab1:  # Opće postavke
            self._prikazi_opce_postavke(elements_model)

        with tab2:  # Postavke zgrade
            st.header("Postavke zgrade")
            
            # Pass prostorija_controller and zid_controller to prikazi_manager_etaza
            if self.multi_room_model and self.etaza_controller and self.prostorija_controller and self.zid_controller:
                # Make sure we have the latest model data
                self.multi_room_model._ucitaj_iz_session_state()
                
                # Osiguravamo da se prikaže uputa korisniku ako nije odabrana etaža za upravljanje
                if 'selected_etaza_for_rooms' not in st.session_state:
                    st.info("Da biste upravljali prostorijama na etaži, kliknite na 'Upravljaj prostorijama' pokraj željene etaže.")
                  # Display the floor and room management UI
                prikazi_manager_etaza(self.multi_room_model, self.etaza_controller, self.prostorija_controller, self.zid_controller)
            else:
                st.error("Model zgrade ili potrebni kontroleri nisu pravilno inicijalizirani.")
        
        with tab3:  # Rezultati po prostorijama
            # Automatski pokreni izračun ako već nije pokrenut
            self._pokreni_izracun(elements_model)
                
            if self.rezultati and self.rezultati.get("etaze"):
                if isinstance(self.rezultati["etaze"], list) and len(self.rezultati["etaze"]) > 0:                    # Get the external temperature from the results
                    temperatura_vanjska = self.rezultati.get("zgrada", {}).get("temperatura_vanjska", -20.0)
                      # Prikazujemo prostorije grupirane po etažama u kontejnerima
                    for etaza_rezultat in self.rezultati["etaze"]:
                        # Koristi container s border=True za vizualno odvajanje etaža
                        with st.container(border=True):                            # Koristimo funkciju iz results_ui.py za konzistentan prikaz
                            # Funkcija prikaz_rezultata_etaze već sadrži kompletan prikaz (metriku, tablicu prostorija i expandere)
                            prikaz_rezultata_etaze(etaza_rezultat, temperatura_vanjska)
                else:
                    st.info("Nema dostupnih rezultata za prostorije ili format nije ispravan.")
            else:
                st.info("Nema dostupnih rezultata za prostorije. Provjerite postavke zgrade i pokušajte ponovno.")
        
        with tab4:  # Rezultati po etažama
            st.header("Rezultati proračuna - Po etažama")
            # Automatski pokreni izračun kada se otvori tab s rezultatima
            self._pokreni_izracun(elements_model)
            
            if self.rezultati and self.rezultati.get("zgrada"):# Import the format_power function for use in this scope
                from .ui.results_ui import format_power
            if self.rezultati and self.rezultati.get("zgrada"):
                # Prvo prikazujemo rezultate za cijelu zgradu
                
                # Zatim prikazujemo rezultate po etažama bez detaljnog prikaza prostorija
                if self.rezultati.get("etaze") and isinstance(self.rezultati["etaze"], list) and len(self.rezultati["etaze"]) > 0:
                    st.subheader("Pregled po etažama")
                    temperatura_vanjska = self.rezultati.get("zgrada", {}).get("temperatura_vanjska", -20.0)
                    
                    # Create a list to hold all floors data
                    etaze_data = []
                    
                    # Iterate through floors and collect basic data
                    for etaza_rezultat in self.rezultati["etaze"]:
                        # Get total room count
                        broj_prostorija = 0
                        if isinstance(etaza_rezultat.get('prostorije'), dict):
                            broj_prostorija = len(etaza_rezultat['prostorije'])
                        elif isinstance(etaza_rezultat.get('prostorije'), list):
                            broj_prostorija = len(etaza_rezultat['prostorije'])
                            
                        # Compute average temperature if available
                        prosjecna_temp = None
                        ukupna_povrsina = 0
                        
                        if isinstance(etaza_rezultat.get('prostorije'), dict):
                            temp_sum = 0
                            for p_id, p_result in etaza_rezultat['prostorije'].items():
                                temp_sum += p_result['temperatura'] * p_result['povrsina']
                                ukupna_povrsina += p_result['povrsina']
                            if ukupna_povrsina > 0:
                                prosjecna_temp = temp_sum / ukupna_povrsina
                          # Create the row data
                        specific_loss = etaza_rezultat['gubici'] / etaza_rezultat['povrsina'] if etaza_rezultat['povrsina'] > 0 else 0
                        
                        # Add data to the list
                        etaze_data.append({
                            "Etaža": etaza_rezultat['naziv'],
                            "Ukupna površina": f"{etaza_rezultat['povrsina']:.2f} m²",
                            "Ukupni volumen": f"{etaza_rezultat.get('volumen', 0):.2f} m³",
                            "Broj prostorija": f"{broj_prostorija}",
                            "Ukupni toplinski gubici [W]": f"{etaza_rezultat['gubici']:.0f}",
                            "Ukupni specifični toplinski gubici": f"{specific_loss:.1f} W/m²",
                            "Prosječna temp. [°C]": f"{prosjecna_temp:.1f}" if prosjecna_temp is not None else "N/A"
                        })
                    
                    # Display the table
                    etaze_df = pd.DataFrame(etaze_data)
                    st.dataframe(etaze_df, hide_index=True)
                      # Display expanded floor data with room listing but without detailed room information
                    for etaza_rezultat in self.rezultati["etaze"]:
                        with st.container(border=True):
                            # Koristimo funkciju iz results_ui.py za konzistentan prikaz
                            prikaz_rezultata_etaze(etaza_rezultat, temperatura_vanjska)
                            
                            # Table of rooms in the floor
                            if etaza_rezultat['prostorije']:
                                # Create table data
                                prostorije_data = []
                                
                                # Check if 'prostorije' is a dictionary or a list
                                if isinstance(etaza_rezultat['prostorije'], dict):
                                    # If it's a dictionary, iterate through its key-value pairs
                                    for p_id, p_result in etaza_rezultat['prostorije'].items():
                                        gubici_ukupno = p_result['gubici']['ukupno']
                                        prostorije_data.append({
                                            "Prostorija": p_result['naziv'],
                                            "Površina [m²]": f"{p_result['povrsina']:.2f}",
                                            "Temperatura [°C]": f"{p_result['temperatura']:.1f}",
                                            "Toplinski gubici [W]": f"{gubici_ukupno:.0f}",
                                            "Specifični toplinski gubici": f"{gubici_ukupno/p_result['povrsina']:.1f} W/m²" if p_result['povrsina'] > 0 else "N/A"
                                        })
                                elif isinstance(etaza_rezultat['prostorije'], list):
                                    # If it's a list, iterate through the list
                                    for p_result in etaza_rezultat['prostorije']:
                                        gubici_ukupno = p_result['gubici']['ukupno']
                                        prostorije_data.append({
                                            "Prostorija": p_result['naziv'],
                                            "Površina [m²]": f"{p_result['povrsina']:.2f}",
                                            "Temperatura [°C]": f"{p_result['temperatura']:.1f}",
                                            "Toplinski gubici [W]": f"{gubici_ukupno:.0f}",
                                            "Specifični toplinski gubici": f"{gubici_ukupno/p_result['povrsina']:.1f} W/m²" if p_result['povrsina'] > 0 else "N/A"
                                        })
                                
                                prostorije_df = pd.DataFrame(prostorije_data)
                                st.dataframe(prostorije_df, hide_index=True)
                            else:
                                st.warning("Nema podataka o prostorijama na ovoj etaži.")
            else:
                st.info("Nema dostupnih rezultata za zgradu. Provjerite postavke zgrade i pokušajte ponovno.")
          

    def _pokreni_izracun(self, elements_model):
        # Ensure instance variables are synced with the latest session state before calculation
        if 'toplinski_mostovi_checkbox' in st.session_state:
            self.toplinski_mostovi = st.session_state.toplinski_mostovi_checkbox
        if 'postotak_toplinskih_mostova_slider' in st.session_state:
            self.postotak_toplinskih_mostova = st.session_state.postotak_toplinskih_mostova_slider
        if 'faktor_sigurnosti_slider' in st.session_state:
            self.faktor_sigurnosti = st.session_state.faktor_sigurnosti_slider

        try:
            if not self.multi_room_model or not self.multi_room_model.etaze:
                st.error("Nema definiranih etaža ili prostorija u modelu. Molimo unesite podatke u 'Postavke zgrade'.")
                self.rezultati = {"error": "Nema etaža/prostorija"}
                st.session_state[self.results_session_key] = self.rezultati
                return

            dodatni_parametri = {
                "toplinski_mostovi": self.toplinski_mostovi,
                "postotak_toplinskih_mostova": self.postotak_toplinskih_mostova if self.toplinski_mostovi else 0,
                "faktor_sigurnosti": self.faktor_sigurnosti,
            }
            st.write(f"DEBUG: `dodatni_parametri` u _pokreni_izracun: {dodatni_parametri}") # DEBUG
            # Pronađi grad koji odgovara odabranoj temperaturi
            odabrani_grad = next((grad for grad, temp in GRADOVI_TEMP.items() if temp == self.temp_vanjska), "Osijek")
            
            # Pozovi funkciju s ažuriranim setom parametara
            self.rezultati = self.izracunaj_toplinske_gubitke_zgrade(
                model=self.multi_room_model,
                grad=odabrani_grad,
                elements_model=elements_model,
                u_values_fallback=self.u_values,
                dodatni_parametri=dodatni_parametri,
                temp_vanjska=self.temp_vanjska  # Eksplicitno šaljemo temperaturu
            )
            
            # Spremi rezultate u session state
            st.session_state[self.results_session_key] = self.rezultati

        except Exception as e:
            st.error(f"Greška tijekom izračuna: {e}")
            self.rezultati = {"error": str(e)} # Store error message
            st.session_state[self.results_session_key] = self.rezultati
            import traceback
            traceback.print_exc()
            
    def _prikazi_opce_postavke(self, elements_model):
        """
        Prikazuje opće postavke proračuna
        
        Parameters:
        -----------
        elements_model : BuildingElementsModel
            Model građevinskih elemenata
        """
        import streamlit as st  # Osiguravamo da je st dostupan
        import pandas as pd  # Za tablični prikaz

        # Helper funkcija za prikaz forme za dodavanje i liste postojećih elemenata
        def _prikazi_formu_i_elemente(elem_type_hr, elements_list, add_function, delete_function, fields_config, model_instance):
            st.subheader(f"Dodaj novi tip {elem_type_hr}")
            form_key = f"add_{elem_type_hr.lower().replace(' ', '_').replace('č', 'c').replace('ć', 'c').replace('š', 's').replace('đ', 'd').replace('ž', 'z')}_form"
            
            with st.form(key=form_key):
                inputs = {}
                for field_name, field_label, field_type, default_value, kwargs_tuple in fields_config:
                    kwargs = dict(kwargs_tuple)  # Pretvaranje tuple u dict
                    if field_type == "text_input":
                        inputs[field_name] = st.text_input(field_label, value=default_value, key=f"{form_key}_{field_name}", **kwargs)
                    elif field_type == "number_input":
                        inputs[field_name] = st.number_input(field_label, value=default_value, key=f"{form_key}_{field_name}", **kwargs)
                  
                # Koristimo akuzativ za glagol "dodaj" (dodaj što?)
                # Pretvaramo genitiv množine u akuzativ jednine
                elem_text = ""
                if elem_type_hr == "podova":
                    elem_text = "pod"
                elif elem_type_hr == "stropova":
                    elem_text = "strop"
                elif elem_type_hr == "prozora":
                    elem_text = "prozor"
                elif elem_type_hr == "vanjskih zidova":
                    elem_text = "vanjski zid"
                elif elem_type_hr == "unutarnjih zidova":
                    elem_text = "unutarnji zid"
                elif elem_type_hr == "vanjskih vrata":
                    elem_text = "vanjska vrata"
                elif elem_type_hr == "unutarnjih vrata":
                    elem_text = "unutarnja vrata"
                else:
                    # Generički slučaj - koristimo akuzativ jednine
                    elem_text = elem_type_hr
                
                submitted = st.form_submit_button(f"Dodaj {elem_text}")
                if submitted:
                    try:
                        if not inputs.get("naziv", "").strip():
                            st.error("Naziv ne može biti prazan.")
                        else:
                            add_function(**inputs)
                            model_instance.spremi_elemente()
                            st.success(f"Dodan novi tip: {inputs['naziv']}")
                    except Exception as e:
                        st.error(f"Greška prilikom dodavanja: {e}")
            
            st.subheader(f"Postojeći tipovi {elem_type_hr}")
            if not elements_list:
                st.info(f"Nema definiranih tipova {elem_type_hr}.")
            else:
                # Kreiramo DataFrame za tablični prikaz
                table_data = []                
                for item in elements_list:
                    item_data = {"ID": item.id, "Naziv": item.naziv}
                    if hasattr(item, 'debljina') and item.debljina is not None:
                        # Convert to cm and display as whole number
                        item_data["Debljina [cm]"] = int(item.debljina * 100)
                    if hasattr(item, 'u_vrijednost') and item.u_vrijednost is not None:
                        item_data["U [W/m²K]"] = f"{item.u_vrijednost:.2f}"
                    if hasattr(item, 'tip') and item.tip:
                        item_data["Tip"] = item.tip
                    table_data.append(item_data)
                
                df = pd.DataFrame(table_data)
                
                # Prikazujemo tablicu
                st.dataframe(df.drop(columns=['ID']), hide_index=True)
                
                # Dodajemo gumbe za brisanje ispod tablice
                st.write("Akcije:")
                cols = st.columns(min(4, len(elements_list)))
                for i, item in enumerate(elements_list):
                    col_idx = i % 4
                    item_id_str = str(item.id).replace('-', '_')
                    if cols[col_idx].button(f"Obriši: {item.naziv}", key=f"delete_{elem_type_hr.lower().replace(' ', '_')}_{item_id_str}"):
                        try:
                            delete_function(item.id)
                            model_instance.spremi_elemente()
                            st.success(f"Obrisan tip: {item.naziv}")
                            st.rerun()  # Rerun da se lista osvježi
                        except Exception as e:
                            st.error(f"Greška prilikom brisanja: {e}")
        
        # Projektne temperature i Dodatne opcije
        # st.header("Projektne temperature") # Zakomentirano

        st.subheader("Vanjska projektna temperatura")
        regija = st.selectbox("Odaberite regiju:", list(REGIJE_GRADOVI_TEMP.keys()), key="opce_regija_selector")
        
        gradovi_u_regiji = list(REGIJE_GRADOVI_TEMP[regija].keys())
        # Pronalazi indeks trenutno odabranog grada ili postavlja na prvi ako nije pronađen
        try:
            # Pokušavamo naći grad koji odgovara trenutnoj vanjskoj temperaturi
            current_grad_index = gradovi_u_regiji.index(next(g for g, temp in REGIJE_GRADOVI_TEMP[regija].items() if temp == self.temp_vanjska))
        except (StopIteration, ValueError):
            current_grad_index = 0  # Default na prvi grad ako nema poklapanja

        grad = st.selectbox(
            "Odaberite grad:", 
            gradovi_u_regiji, 
            index=current_grad_index, 
            key="opce_grad_selector"        )
        self.temp_vanjska = REGIJE_GRADOVI_TEMP[regija][grad]
        st.info(f"Vanjska projektna temperatura za {grad}: {self.temp_vanjska} °C")
        
        st.subheader("Dodatne opcije za proračun")
        
        # Thermal bridges - reimplemented from scratch
        self._render_thermal_bridges_ui()

        # Safety factor number input
        st.number_input(
            "Faktor sigurnosti [%]:", 
            min_value=0, 
            max_value=30, 
            value=st.session_state.faktor_sigurnosti_slider, # Read from session state
            step=1,
            key='faktor_sigurnosti_slider',                  # Links widget to session state
            help="Dodatak na ukupne gubitke zbog nesigurnosti u proračunu."
        )
        self.faktor_sigurnosti = st.session_state.faktor_sigurnosti_slider # Update instance var
        
        st.markdown("---")  # Separator prije Tipova građevinskih elemenata
        
        # Korištenje modularnog sučelja za upravljanje građevinskim elementima
        if hasattr(self, 'elementi_controller') and self.elementi_controller is not None:
            # Prikazujemo sučelje za upravljanje građevinskim elementima
            try:
                prikazi_manager_gradevinski_elementi(self.multi_room_model, self.elementi_controller)
            except Exception as e:
                st.error(f"Greška pri prikazivanju sučelja za građevinske elemente: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            st.error("ElementiController nije inicijaliziran. Ne mogu prikazati sučelje za upravljanje građevinskim elementima.")
            
    def _prepare_data_for_calculation(self):
        if self.multi_room_model is None:
            st.error("Model nije inicijaliziran.")
            return [], None

        self.multi_room_model.create_physical_elements_from_rooms()
        self.multi_room_model.restore_shared_elements_references()
        
        prostorije_za_izracun = []
        fizicki_elementi_map = self.multi_room_model.fizicki_elementi
        
        # Handle both dictionary and list cases for etaze
        if isinstance(self.multi_room_model.etaze, dict):
            for _, etaza_data in self.multi_room_model.etaze.items():
                if isinstance(etaza_data.prostorije, dict):
                    for _, prostorija_obj in etaza_data.prostorije.items():
                        # Pass fizicki_elementi_map to to_dict method
                        prostorija_dict = prostorija_obj.to_dict(fizicki_elementi_map)
                        prostorije_za_izracun.append(prostorija_dict)
        else:
            # Handle list case
            for etaza in self.multi_room_model.etaze:
                if hasattr(etaza, 'prostorije'):
                    if isinstance(etaza.prostorije, dict):
                        for _, prostorija_obj in etaza.prostorije.items():
                            prostorija_dict = prostorija_obj.to_dict(fizicki_elementi_map)
                            prostorije_za_izracun.append(prostorija_dict)
                    elif isinstance(etaza.prostorije, list):
                        for prostorija_obj in etaza.prostorije:
                            prostorija_dict = prostorija_obj.to_dict(fizicki_elementi_map)
                            prostorije_za_izracun.append(prostorija_dict)
        
        return prostorije_za_izracun, self.multi_room_model.katalog_elemenata
        
    def calculate_heat_loss(self):
        self.rezultati_izracuna = {"prostorije": {}, "ukupno": 0.0}
        self.status = "Calculating"

        if not self.multi_room_model or not self.multi_room_model.etaze:
            st.warning("Nema definiranih etaža ili prostorija za izračun.")
            self.status = "Completed"
            return self.rezultati_izracuna

        # Populate temperature_prostorija in session_state for transmisijski.py
        temperature_prostorija_map = {}
        
        # Handle both dictionary and list cases for etaze
        if isinstance(self.multi_room_model.etaze, dict):
            for etaza_data in self.multi_room_model.etaze.values():
                if isinstance(etaza_data.prostorije, dict):
                    for prostorija_id, prostorija_obj in etaza_data.prostorije.items():
                        temperature_prostorija_map[prostorija_id] = prostorija_obj.temp_unutarnja
        else:
            # Handle list case
            for etaza in self.multi_room_model.etaze:
                if hasattr(etaza, 'prostorije'):
                    if isinstance(etaza.prostorije, dict):
                        for prostorija_id, prostorija_obj in etaza.prostorije.items():
                            temperature_prostorija_map[prostorija_id] = prostorija_obj.temp_unutarnja
                    elif isinstance(etaza.prostorije, list):
                        for prostorija_obj in etaza.prostorije:
                            temperature_prostorija_map[prostorija_obj.id] = prostorija_obj.temp_unutarnja
        
        st.session_state["temperature_prostorija"] = temperature_prostorija_map
        
        # Set up global temperatures for calculations
        globalne_temperature = {
            "vanjska": self.temp_vanjska,  # Use the temperature set in the UI
            "tlo": 10.0,                  # Default value for ground temperature
            "negrijanom": 5.0,            # Default value for unheated spaces
            "tavan": 5.0                  # Default value for attic spaces
        }

        prostorije_data, katalog = self._prepare_data_for_calculation()

        if not prostorije_data:
            st.warning("Nema pripremljenih podataka o prostorijama za izračun.")
            self.status = "Completed"
            return self.rezultati_izracuna

        ukupni_gubici_objekta = 0.0

        for prostorija_dict in prostorije_data:
            # Ensure Prostorija object (or dict) and temperatures are valid
            if not prostorija_dict or "temp_unutarnja" not in prostorija_dict:
                st.error(f"Nedostaju podaci za prostoriju ID: {prostorija_dict.get('id', 'Nepoznat ID')}")
                continue

            # Use the globalne_temperature dict we created above
            rezultat_prostorije = izracun_transmisijskih_gubitaka(
                prostorija_dict, 
                globalne_temperature,
                katalog
            )
            
            # Ventilacijski gubici se dodaju ovdje ako su izračunati
            # gubici_ventilacije = izracun_ventilacijskih_gubitaka(prostorija_obj, self.globalne_temperature["vanjska"], ...)
            # rezultat_prostorije["ventilacija"] = gubici_ventilacije
            # rezultat_prostorije["ukupno"] += gubici_ventilacije
            
            # Dodatni gubici (npr. zbog prekida grijanja)
            # ako su definirani kao postotak ili fiksna vrijednost
            # dodatni_gubici_iznos = ... 
            # rezultat_prostorije["dodatni_gubici"] = dodatni_gubici_iznos
            # rezultat_prostorije["ukupno"] += dodatni_gubici_iznos

            self.rezultati_izracuna["prostorije"][prostorija_dict["id"]] = rezultat_prostorije
            ukupni_gubici_objekta += rezultat_prostorije.get("ukupno", 0)

        self.rezultati_izracuna["ukupno"] = ukupni_gubici_objekta
        self.status = "Completed"
        # st.success("Izračun toplinskih gubitaka je završen.")
        return self.rezultati_izracuna
        
    def _render_thermal_bridges_ui(self):
        """Renders thermal bridges UI with conditional slider display."""
        # Checkbox for enabling/disabling thermal bridges
        thermal_bridges_enabled = st.checkbox(
            "Uračunaj dodatak za toplinske mostove",
            value=False,  # Default to False
            help="Dodaje postotak na transmisijske gubitke zbog toplinskih mostova."
        )
        
        # Set instance variables and session state
        self.toplinski_mostovi = thermal_bridges_enabled
        st.session_state['toplinski_mostovi'] = thermal_bridges_enabled
          # Only show slider if thermal bridges are enabled
        if thermal_bridges_enabled:
            # Use regular numeric slider with 5% increments
            thermal_bridges_percentage = st.slider(
                "Postotak za toplinske mostove:",
                min_value=5,
                max_value=25,
                value=15,  # Default value
                step=5,
                format="%d%%"  # Format as percentage with % sign
            )            # Show reference values in a blue info box
            st.info("""
**Referentne vrijednosti:**

5% - vrlo dobra konstrukcija

10% - dobra konstrukcija

15% - standardna konstrukcija

20% - slaba konstrukcija

25% - vrlo slaba konstrukcija
""")
            
            # Update instance variables and session state
            self.postotak_toplinskih_mostova = thermal_bridges_percentage
            st.session_state['postotak_toplinskih_mostova'] = thermal_bridges_percentage
        else:
            # When disabled, set percentage to 0
            self.postotak_toplinskih_mostova = 0
            st.session_state['postotak_toplinskih_mostova'] = 0
