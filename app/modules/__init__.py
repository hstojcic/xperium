# Inicijalizacijska datoteka za 'modules' paket

# Napomena: Prethodna implementacija ručne registracije zamijenjena 
# automatskim otkrivanjem kalkulatora kroz ModuleManager klasu.
# Pogledajte core/module_manager.py za implementaciju.

# Inicijalizacija prazne strukture ako je potrebno
def init_calculation_structure():
    """
    Inicijalizira strukturu za dostupne proračune ako još ne postoji.
    """
    import streamlit as st
    
    if 'available_calculations' not in st.session_state:
        st.session_state.available_calculations = {}

# Poziv inicijalizacije pri importu modula
init_calculation_structure()