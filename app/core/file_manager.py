import streamlit as st
import json
import os
import datetime
import pickle
import subprocess
import sys
import tempfile
import time
import tkinter as tk
from tkinter import filedialog
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
        Otvara Windows dijalog za odabir putanje za spremanje
        """
        # Inicijaliziramo tkinter root i sakrijemo ga
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)  # Osigurava da dijalog bude iznad Streamlit-a
        
        # Prikazujemo dijalog za spremanje
        file_path = filedialog.asksaveasfilename(
            initialdir=self.default_save_dir,
            initialfile=default_name,
            defaultextension=".calc",
            filetypes=[("Calculation files", "*.calc"), ("All files", "*.*")]
        )
        
        # Uništavamo tkinter root
        root.destroy()
        
        return file_path if file_path else None
    
    def _get_open_file_path(self):
        """
        Otvara Windows dijalog za odabir datoteke za otvaranje
        """
        # Inicijaliziramo tkinter root i sakrijemo ga
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)  # Osigurava da dijalog bude iznad Streamlit-a
        
        # Prikazujemo dijalog za otvaranje
        file_path = filedialog.askopenfilename(
            initialdir=self.default_save_dir,
            defaultextension=".calc",
            filetypes=[("Calculation files", "*.calc"), ("All files", "*.*")]
        )
        
        # Uništavamo tkinter root
        root.destroy()
        
        return file_path if file_path else None
    
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
            # Ako nema putanje, koristimo dijalog za spremanje
            default_name = current_calculation.name if hasattr(current_calculation, 'name') and current_calculation.name else "proračun"
            if not default_name.endswith('.calc'):
                default_name += '.calc'
            
            file_path = self._get_save_file_path(default_name)
            if not file_path:  # Korisnik je otkazao dijalog
                st.info("Otkazano spremanje.")
                return False
        
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
        
        # Otvaramo dijalog za odabir lokacije spremanja
        file_path = self._get_save_file_path(default_name)
        if not file_path:  # Korisnik je otkazao dijalog
            st.info("Otkazano spremanje.")
            return False
            
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
        Otvara postojeći proračun koristeći Windows dijalog
        """
        file_path = self._get_open_file_path()
        
        if not file_path:  # Korisnik je otkazao dijalog
            st.info("Otkazano otvaranje.")
            return False
        
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