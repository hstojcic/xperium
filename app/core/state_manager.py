import streamlit as st

class StateManager:
    """
    Klasa za upravljanje globalnim stanjem aplikacije
    """
    
    def __init__(self):
        if 'current_calculation' not in st.session_state:
            st.session_state.current_calculation = None
        
        if 'current_file_path' not in st.session_state:
            st.session_state.current_file_path = None
            
        if 'calculation_changed' not in st.session_state:
            st.session_state.calculation_changed = False
        
        if 'categories' not in st.session_state:
            # Inicijalizacija kategorija i podkategorija
            st.session_state.categories = {
                "Hidrotehničke instalacije": {
                    "Instalacije vodovoda": [],
                    "Instalacije bazenske tehnike": [],
                    "Instalacije sanitarne kanalizacije": [],
                    "Instalacije oborinske kanalizacije": [],
                    "Instalacije zaštite od požara": []  # Dodana kategorija zaštite od požara
                },
                "Termotehničke instalacije": {
                    "Instalacije plina": [],
                    "Instalacije grijanja": [],
                    "Instalacije grijanja i hlađenja": [],
                    "Instalacije hlađenja": [],
                    "Instalacije ventilacije": []
                }
            }
    
    def get_current_calculation(self):
        """Vraća trenutno aktivni proračun"""
        return st.session_state.current_calculation
    
    def set_current_calculation(self, calculation):
        """Postavlja trenutno aktivni proračun"""
        st.session_state.current_calculation = calculation
    
    def get_current_file_path(self):
        """Vraća putanju trenutno otvorene datoteke"""
        return st.session_state.current_file_path
    
    def set_current_file_path(self, file_path):
        """Postavlja putanju trenutno otvorene datoteke"""
        st.session_state.current_file_path = file_path
    
    def has_unsaved_changes(self):
        """Provjerava ima li nespremljenih promjena"""
        return st.session_state.calculation_changed
    
    def set_calculation_changed(self, changed=True):
        """Označava da je proračun promijenjen"""
        st.session_state.calculation_changed = changed
        
    def get_categories(self):
        """Vraća sve kategorije i podkategorije"""
        return st.session_state.categories