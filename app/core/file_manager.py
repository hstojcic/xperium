import streamlit as st
import json
import os
import datetime
import pickle
import subprocess
import sys
import tempfile
import time
import traceback

class FileManager:
    """
    Klasa za upravljanje datotekama proračuna
    """
    
    def __init__(self):
        self.state_manager = st.session_state.state_manager
        
        # Stvaranje mape za proračune ako ne postoji
        os.makedirs("saved_calculations", exist_ok=True)
        
        # Definiramo zadani direktorij za spremanje
        self.default_save_dir = os.path.join(os.path.expanduser("~"), "Documents", "Strojarski proračuni")
        os.makedirs(self.default_save_dir, exist_ok=True)
    
    def _get_save_file_path(self, default_name="proračun.calc"):
        """
        Streamlit implementacija za odabir putanje za spremanje
        """
        # Koristeći session_state za persistentnost dijaloga
        if 'save_filename' not in st.session_state:
            st.session_state.save_filename = default_name
            
        # Koristimo Streamlit komponente za unos imena datoteke
        st.sidebar.markdown("### Spremi proračun")
        filename = st.sidebar.text_input("Naziv datoteke:", st.session_state.save_filename, key="save_file_input")
        
        # Dodajemo .calc ekstenziju ako korisnik nije
        if filename and not filename.lower().endswith('.calc'):
            filename += '.calc'
        
        # Predložimo nekoliko uobičajenih lokacija
        save_locations = {
            "Mapa proračuna": os.path.join(os.getcwd(), "saved_calculations"),
            "Moji dokumenti": os.path.join(os.path.expanduser("~"), "Documents"),
            "Strojarski proračuni": self.default_save_dir
        }
        
        selected_location = st.sidebar.selectbox(
            "Lokacija:", 
            list(save_locations.keys()),
            key="save_location_select"
        )
        
        # Gumbi za spremanje ili odustajanje
        col1, col2 = st.sidebar.columns(2)
        save_clicked = col1.button("Spremi", key="save_file_confirm")
        cancel_clicked = col2.button("Odustani", key="save_file_cancel")
        
        if cancel_clicked:
            # Čistimo dialog
            if 'save_filename' in st.session_state:
                del st.session_state.save_filename
            return None
            
        if save_clicked and filename:
            # Formiramo putanju
            full_path = os.path.join(save_locations[selected_location], filename)
            st.session_state.save_filename = filename  # Pamtimo za sljedeći put
            
            # Ako datoteka već postoji, pitamo korisnika za potvrdu
            if os.path.exists(full_path):
                overwrite = st.sidebar.warning(f"Datoteka {filename} već postoji!")
                confirm_overwrite = st.sidebar.button("Prepiši", key="confirm_overwrite")
                cancel_overwrite = st.sidebar.button("Odustani", key="cancel_overwrite")
                
                if confirm_overwrite:
                    return full_path
                elif cancel_overwrite:
                    return None
                else:
                    # Čekamo korisnički odgovor
                    return "waiting"
            
            # Vraćamo putanju za spremanje
            return full_path
            
        return "waiting"  # Čekamo da korisnik ispuni podatke
    
    def _get_open_file_path(self):
        """
        Streamlit implementacija za odabir datoteke za otvaranje
        """
        st.sidebar.markdown("### Otvori proračun")
        
        # Definiramo lokacije za pretraživanje
        open_locations = {
            "Mapa proračuna": os.path.join(os.getcwd(), "saved_calculations"),
            "Moji dokumenti": os.path.join(os.path.expanduser("~"), "Documents"),
            "Strojarski proračuni": self.default_save_dir
        }
        
        selected_location = st.sidebar.selectbox(
            "Lokacija:", 
            list(open_locations.keys()),
            key="open_location_select"
        )
        
        # Dohvaćamo popis datoteka s odabrane lokacije
        location_path = open_locations[selected_location]
        
        try:
            if os.path.exists(location_path):
                # Filtriramo samo .calc datoteke
                files = [f for f in os.listdir(location_path) if f.endswith('.calc')]
                
                if not files:
                    st.sidebar.info(f"Nema dostupnih proračuna u {selected_location}")
                    
                # Sortiramo po datumu izmjene (najnovije prvo)
                files = sorted(files, key=lambda f: os.path.getmtime(os.path.join(location_path, f)), reverse=True)
                
                # Prikazujemo popis datoteka
                selected_file = st.sidebar.selectbox(
                    "Odaberi proračun:", 
                    files,
                    key="open_file_select"
                )
                
                # Gumbi za otvaranje ili odustajanje
                col1, col2 = st.sidebar.columns(2)
                open_clicked = col1.button("Otvori", key="open_file_confirm")
                cancel_clicked = col2.button("Odustani", key="open_file_cancel")
                
                if open_clicked and selected_file:
                    return os.path.join(location_path, selected_file)
                
                if cancel_clicked:
                    return None
            else:
                st.sidebar.error(f"Lokacija {selected_location} ne postoji")
        except Exception as e:
            st.sidebar.error(f"Greška pri čitanju lokacije: {str(e)}")
        
        return "waiting"  # Čekamo da korisnik odabere
    
    def save_calculation(self):
        """
        Sprema trenutni proračun
        """
        current_calculation = self.state_manager.get_current_calculation()
        if not current_calculation:
            st.error("Nema otvorenog proračuna za spremanje.")
            return False
        
        file_path = self.state_manager.get_current_file_path()
        
        if not file_path:
            # Ako nema putanje, koristimo Streamlit dijalog za spremanje
            default_name = current_calculation.name if hasattr(current_calculation, 'name') and current_calculation.name else "proračun"
            if not default_name.endswith('.calc'):
                default_name += '.calc'
            
            # Postavimo zastavicu za prikaz dijaloga
            if "showing_save_dialog" not in st.session_state:
                st.session_state.showing_save_dialog = True
                st.rerun()
                
            file_path = self._get_save_file_path(default_name)
            
            if file_path == "waiting":
                return "waiting"
                
            if not file_path:  # Korisnik je otkazao dijalog
                st.session_state.showing_save_dialog = False
                st.info("Otkazano spremanje.")
                st.rerun()
                return False
                
            # Resetiramo zastavicu dijaloga jer smo završili s odabirom
            st.session_state.showing_save_dialog = False
        
        # Spremanje proračuna - koristimo postojeću putanju
        success = self._save_to_file(current_calculation, file_path)
        if success:
            self.state_manager.set_current_file_path(file_path)
            self.state_manager.set_calculation_changed(False)
            st.success(f"Proračun spremljen u: {os.path.basename(file_path)}")
            return True
        return False
    
    def save_calculation_as(self):
        """
        Sprema trenutni proračun pod novim imenom
        """
        current_calculation = self.state_manager.get_current_calculation()
        if not current_calculation:
            st.error("Nema otvorenog proračuna za spremanje.")
            return False
        
        # Dobavljamo zadani naziv iz proračuna za dijalog
        default_name = current_calculation.name if hasattr(current_calculation, 'name') and current_calculation.name else "proračun"
        if not default_name.endswith('.calc'):
            default_name += '.calc'
        
        # Postavimo zastavicu za prikaz dijaloga
        if "showing_save_as_dialog" not in st.session_state:
            st.session_state.showing_save_as_dialog = True
            st.rerun()
            
        # Otvaramo Streamlit dijalog za odabir lokacije spremanja
        file_path = self._get_save_file_path(default_name)
        
        if file_path == "waiting":
            return "waiting"
            
        if not file_path:  # Korisnik je otkazao dijalog
            st.session_state.showing_save_as_dialog = False
            st.info("Otkazano spremanje.")
            st.rerun()
            return False
            
        # Resetiramo zastavicu dijaloga jer smo završili s odabirom
        st.session_state.showing_save_as_dialog = False
            
        # Spremi proračun pod tim imenom
        success = self._save_to_file(current_calculation, file_path)
        if success:
            self.state_manager.set_current_file_path(file_path)
            self.state_manager.set_calculation_changed(False)
            st.success(f"Proračun spremljen u: {os.path.basename(file_path)}")
            return True
        return False
    
    def open_calculation(self):
        """
        Otvara postojeći proračun koristeći Streamlit sučelje
        """
        # Postavljamo zastavicu za prikaz dijaloga za otvaranje
        if "showing_open_dialog" not in st.session_state:
            st.session_state.showing_open_dialog = True
            st.rerun()
        
        file_path = self._get_open_file_path()
        
        if file_path == "waiting":
            return "waiting"
            
        if not file_path:  # Korisnik je otkazao dijalog
            st.session_state.showing_open_dialog = False
            st.info("Otkazano otvaranje.")
            st.rerun()
            return False
            
        # Resetiramo zastavicu dijaloga jer smo završili s odabirom
        st.session_state.showing_open_dialog = False
        
        try:
            calculation = self._load_from_file(file_path)
            self.state_manager.set_current_calculation(calculation)
            self.state_manager.set_current_file_path(file_path)
            self.state_manager.set_calculation_changed(False)
            
            # Resetiramo zastavicu za kategorije jer otvaramo proračun
            if 'show_category_selection' in st.session_state:
                st.session_state.show_category_selection = False
                
            st.success(f"Proračun učitan: {os.path.basename(file_path)}")
            # Potrebno reloadati stranicu kako bi se prikazao učitani proračun
            st.rerun()
            return True
        except Exception as e:
            st.error(f"Greška prilikom otvaranja: {str(e)}")
            st.error(traceback.format_exc())
            return False
    
    def open_specific_file(self, file_path):
        """
        Otvara specifični proračun s točno određene putanje
        
        Args:
            file_path: Putanja do datoteke proračuna
            
        Returns:
            bool: True ako je uspješno, False inače
        """
        try:
            calculation = self._load_from_file(file_path)
            self.state_manager.set_current_calculation(calculation)
            self.state_manager.set_current_file_path(file_path)
            self.state_manager.set_calculation_changed(False)
            
            # Resetiramo zastavicu za kategorije jer otvaramo proračun
            if 'show_category_selection' in st.session_state:
                st.session_state.show_category_selection = False
                
            st.success(f"Proračun učitan: {os.path.basename(file_path)}")
            return True
        except Exception as e:
            st.error(f"Greška prilikom otvaranja: {str(e)}")
            st.error(traceback.format_exc())
            return False
    
    def _save_to_file(self, calculation, file_path):
        """
        Sprema proračun u datoteku
        
        Args:
            calculation: Instanca proračuna
            file_path: Putanja za spremanje
        """
        try:
            # Pretvaranje u dictionary za spremanje
            data = {
                'type': calculation.__class__.__module__ + '.' + calculation.__class__.__name__,
                'name': calculation.name,
                'timestamp': datetime.datetime.now().isoformat(),
                'data': calculation.serialize()
            }
            
            # Stvaramo direktorij ako ne postoji
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Spremanje u datoteku
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
                
            return True
        except Exception as e:
            st.error(f"Greška prilikom spremanja: {str(e)}")
            st.error(traceback.format_exc())
            return False
    
    def _load_from_file(self, file_path):
        """
        Učitava proračun iz datoteke
        
        Args:
            file_path: Putanja do datoteke
            
        Returns:
            Instanca proračuna
        """
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        # Dobivanje modula i klase
        module_path, class_name = data['type'].rsplit('.', 1)
        
        # Dinamičko učitavanje
        import importlib
        module = importlib.import_module(module_path)
        calculation_class = getattr(module, class_name)
        
        # Stvaranje instance
        calculation = calculation_class()
        
        # Učitavanje podataka
        calculation.deserialize(data['data'])
        
        return calculation