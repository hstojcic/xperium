import streamlit as st
import os
import importlib
import inspect
import sys
import pkgutil
from modules.base import BaseCalculation

class ModuleManager:
    """
    Klasa za upravljanje modulima i automatsko otkrivanje dostupnih kalkulatora
    """
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.globally_registered_classes = set()  # Initialize the set here
        
    def discover_calculations(self):
        """
        Skenira strukturu modula i otkriva sve dostupne kalkulatore
        """
        self.globally_registered_classes.clear()  # Clear the set
        # Inicijalizacija strukture podataka za kalkulatore
        if 'available_calculations' not in st.session_state:
            st.session_state.available_calculations = {}
        
        # Inicijalizacija kategorija ako već ne postoje
        categories = self.state_manager.get_categories()
        for main_category, subcategories in categories.items():
            if main_category not in st.session_state.available_calculations:
                st.session_state.available_calculations[main_category] = {}
                
            for subcategory in subcategories:
                if subcategory not in st.session_state.available_calculations[main_category]:
                    st.session_state.available_calculations[main_category][subcategory] = []
        
        # Uvoz glavnog modula
        import modules
        
        # Skeniranje podmodula za pronalaženje kalkulatora
        self._scan_module(modules)
        
    def refresh_calculations(self):
        """
        Ponovno skenira module i osvježava dostupne kalkulatore.
        Korisno nakon dodavanja novih modula/kalkulatora tijekom rada aplikacije.
        """
        self.globally_registered_classes.clear()  # Clear the set
        # Privremeno spremimo postojeće kalkulatore
        old_calcs = {}
        if 'available_calculations' in st.session_state:
            old_calcs = st.session_state.available_calculations
        
        # Resetiramo strukturu kalkulatora
        st.session_state.available_calculations = {}
        
        # Ponovo inicijaliziramo kategorije
        categories = self.state_manager.get_categories()
        for main_category, subcategories in categories.items():
            st.session_state.available_calculations[main_category] = {}
            for subcategory in subcategories:
                st.session_state.available_calculations[main_category][subcategory] = []
        
        # Ponovno otkrivamo kalkulatore
        import modules
        importlib.reload(modules)  # Ponovno učitavanje modula
        self._scan_module(modules, depth=0)  # Initial call with depth 0
        
        # Vraćamo informaciju o uspjehu
        return True
        
    def _scan_module(self, module, depth=0):  # Added depth parameter
        """
        Rekurzivno skeniranje modula i podmodula za pronalaženje kalkulatora
        """
        indent = "  " * depth
        # st.info(f"{indent}Scanning in module: {module.__name__} (Path: {module.__path__ if hasattr(module, '__path__') else 'N/A - Not a package'}) at depth {depth}")

        if not hasattr(module, '__path__'):
            # st.warning(f"{indent}Module {module.__name__} is not a package, cannot iterate with pkgutil. Checking for classes directly.")
            # This case handles when a module file itself is passed, though the primary path is through packages.
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and
                    issubclass(attr, BaseCalculation) and
                    attr != BaseCalculation and
                    attr.__module__ == module.__name__):  # Ensure class is defined in *this* module
                    # st.success(f"{indent}  Found BaseCalculation subclass: {attr.__name__} directly in module {module.__name__}")
                    self._register_calculation(attr, module.__name__)
            return

        found_submodules_or_calculators = False
        for finder, name, ispkg in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
            found_submodules_or_calculators = True
            # st.info(f"{indent}  Found by pkgutil: name={name}, ispkg={ispkg}")
            try:
                submodule = importlib.import_module(name)
                # st.success(f"{indent}  Successfully imported: {name}")

                if ispkg:
                    # st.info(f"{indent}  Descending into package: {name}")
                    self._scan_module(submodule, depth + 1)
                else:
                    # This is a module file (e.g., some_calc.py)
                    # st.info(f"{indent}  Processing module file: {name}")
                    for attr_name in dir(submodule):
                        attr = getattr(submodule, attr_name)
                        if (inspect.isclass(attr) and
                            issubclass(attr, BaseCalculation) and
                            attr != BaseCalculation and
                            attr.__module__ == name):  # Crucial: class must be defined in *this specific submodule*
                            # st.success(f"{indent}    Found BaseCalculation subclass: {attr.__name__} in {name}")
                            self._register_calculation(attr, name)  # 'name' is the full module path
                            found_submodules_or_calculators = True  # Re-affirm if a calc is found
            except ImportError as ie:
                # st.error(f"{indent}  ImportError processing {name}: {str(ie)}. Check dependencies and __init__.py files.")
                print(f"ImportError processing {name}: {str(ie)}") # Keep critical errors for console
            except Exception as e:
                # st.error(f"{indent}  General error processing {name}: {str(e)}")
                print(f"General error processing {name}: {str(e)}") # Keep critical errors for console
            continue  # Continue to next item found by pkgutil
    
        if not found_submodules_or_calculators and depth > 0:  # Avoid warning for the initial 'modules' scan if it's truly empty of direct calcs
            # Check if the current module (package) itself has calculator classes directly in its __init__.py
            # st.info(f"{indent}No submodules via pkgutil in {module.__name__}. Checking for calculators directly in {module.__name__}/__init__.py")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and
                    issubclass(attr, BaseCalculation) and
                    attr != BaseCalculation and
                    attr.__module__ == module.__name__):  # Class defined in this package's __init__.py
                    # st.success(f"{indent}  Found BaseCalculation subclass: {attr.__name__} directly in {module.__name__}'s __init__.py")
                    self._register_calculation(attr, module.__name__)
                    found_submodules_or_calculators = True

        # if not found_submodules_or_calculators and depth > 0:  # Re-check after direct __init__.py scan
            # st.warning(f"{indent}No submodules or direct calculators found by pkgutil or in __init__.py for {module.__name__}")
    
    def _register_calculation(self, calculation_class, module_path):
        """
        Registrira pronađeni kalkulator u odgovarajuću kategoriju i podkategoriju
        """
        fully_qualified_name = calculation_class.__module__ + '.' + calculation_class.__name__
        if fully_qualified_name in self.globally_registered_classes:
            # st.warning(f"Kalkulator {calculation_class.__name__} ({fully_qualified_name}) je već globalno registriran, preskačem.")
            return

        try:
            # Inicijaliziramo instancu za dohvaćanje imena
            instance = calculation_class()
            
            # Mapiranje putanje modula na kategoriju i podkategoriju
            category, subcategory = self._get_category_from_path(module_path)
            
            # Ako nismo uspjeli odrediti kategoriju, preskačemo
            if not category or not subcategory:
                # st.warning(f"Ne mogu odrediti kategoriju za {calculation_class.__name__} iz {module_path}, preskačem")
                return
            
            # Registracija kalkulatora u odgovarajuću kategoriju/podkategoriju
            module_relative_path = module_path.replace("modules.", "")
              # Stvaramo zapis za kalkulator
            calc_info = {
                "name": instance.name,
                "module": module_relative_path,
                "class": calculation_class.__name__
            }
            
            # Dodajemo kalkulator u odgovarajuću podkategoriju ako već ne postoji
            calc_exists = False
            for existing_calc in st.session_state.available_calculations[category][subcategory]:
                if (existing_calc["module"] == module_relative_path and 
                    existing_calc["class"] == calculation_class.__name__):
                    calc_exists = True
                    break
            
            if not calc_exists:
                st.session_state.available_calculations[category][subcategory].append(calc_info)
                self.globally_registered_classes.add(fully_qualified_name)  # Add to set after successful registration
                # st.success(f"Registriran kalkulator: {calculation_class.__name__} u {category}/{subcategory} iz modula {module_relative_path}")
        
        except Exception as e:
            # st.error(f"Greška prilikom registracije kalkulatora {calculation_class.__name__}: {str(e)}")
            print(f"Greška prilikom registracije kalkulatora {calculation_class.__name__}: {str(e)}") # Keep critical errors for console
    
    def _get_category_from_path(self, module_path):
        """
        Određuje kategoriju i podkategoriju na temelju putanje modula
        """
        # Ekstrahiramo relativnu putanju i dijelimo na komponente
        
        path_after_modules_prefix = ""
        # Handle paths like "app.modules.thermal.heating..."
        if module_path.startswith("app.modules."):
            path_after_modules_prefix = module_path.split("app.modules.", 1)[-1]
        # Handle paths like "modules.thermal.heating..."
        elif module_path.startswith("modules."):
            path_after_modules_prefix = module_path.split("modules.", 1)[-1]
        else:
            # st.warning(f"Module path '{module_path}' does not start with 'app.modules.' or 'modules.'. Cannot determine category structure.")
            return None, None

        parts = path_after_modules_prefix.split('.')
        
        # Ako nemamo dovoljno dijelova, ne možemo odrediti kategoriju
        if len(parts) < 2:
            # st.warning(f"Path '{module_path}' (processed to '{path_after_modules_prefix}') does not have enough parts for category/subcategory.")
            return None, None
        
        category_key = parts[0]
        subcategory_key = parts[1]
        
        # Prvi dio određuje glavnu kategoriju
        if category_key == "thermal":
            category = "Termotehničke instalacije"
        elif category_key == "hydraulic":
            category = "Hidrotehničke instalacije"
        else:
            # st.warning(f"Unknown main category key: '{category_key}' derived from path '{module_path}' (processed part: '{path_after_modules_prefix}').")
            return None, None
        
        # Drugi dio mapiramo na podkategoriju
        subcat_mapping = {
            # Hidrotehničke instalacije
            'water_supply': 'Instalacije vodovoda',
            'sanitary_drainage': 'Instalacije sanitarne kanalizacije',
            'rainwater_drainage': 'Instalacije oborinske kanalizacije',
            'fire_protection': 'Instalacije zaštite od požara',
            'pool_systems': 'Instalacije bazenske tehnike',
            
            # Termotehničke instalacije
            'gas': 'Instalacije plina',
            'heating': 'Instalacije grijanja',
            'cooling': 'Instalacije hlađenja',
            'hvac': 'Instalacije grijanja i hlađenja',
            'ventilation': 'Instalacije ventilacije'
        }
        
        # Ako je drugi dio u mapiranju, koristimo ga
        subcategory = None
        if subcategory_key in subcat_mapping:
            subcategory = subcat_mapping[subcategory_key]
        else:
            # st.warning(f"Unknown subcategory key: '{subcategory_key}' (from path '{path_after_modules_prefix}') in subcat_mapping. Available keys: {list(subcat_mapping.keys())}")
            return None, None
        
        return category, subcategory