import streamlit as st
import os
import sys

# Dodajemo trenutni direktorij u PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Provjera jesmo li na Streamlit Cloudu
is_streamlit_cloud = "STREAMLIT_SHARING" in os.environ or "IS_STREAMLIT_CLOUD" in os.environ

from core.navigation import Navigation
from core.state_manager import StateManager
from core.file_manager import FileManager
from core.history_manager import HistoryManager
from core.word_export import WordExport
from core.module_manager import ModuleManager

def main():
    # Postavljamo layout aplikacije - MORA BITI PRVA STREAMLIT NAREDBA
    st.set_page_config(layout="wide", page_title="Proračuni instalacija")
    
    # Inicijalizacija stanja aplikacije ako nije već
    if 'initialized' not in st.session_state:
        st.session_state.state_manager = StateManager()
        st.session_state.file_manager = FileManager()
        st.session_state.history_manager = HistoryManager()
        st.session_state.word_export = WordExport()
        st.session_state.navigation = Navigation()
        st.session_state.initialized = True
        st.session_state.current_calculation = None
        st.session_state.calculation_changed = False
        
        # Inicijalizacija zastavica za tracking stanja
        st.session_state.show_category_selection = False
        
        # Inicijalizacija i pokretanje ModuleManager-a za automatsko otkrivanje kalkulatora
        st.session_state.module_manager = ModuleManager(st.session_state.state_manager)
        st.session_state.module_manager.discover_calculations()
    
    # Dohvaćanje instanci iz session_state
    navigation = st.session_state.navigation
    state_manager = st.session_state.state_manager
    file_manager = st.session_state.file_manager
    history_manager = st.session_state.history_manager
    word_export = st.session_state.word_export
    
    # Dodajemo CSS za konzistentan razmak i poboljšanu navigaciju
    st.markdown("""
    <style>
    /* Stiliziranje gumba u navigaciji */
    div.stButton > button {
        width: 100%;
        height: 2.5rem;
        margin: 8px 0 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
    }
    
    /* Konzistentni razmaci oko dividera */
    hr {
        margin: 20px 0 !important;
    }
    
    /* Osigurava da prvi gumb nakon dividera ima isti razmak kao zadnji prije dividera */
    .stSidebar > div:first-child > div:first-child > div > div > div > div > hr + div {
        margin-top: 20px !important;
    }
    
    /* Razmaci između grupa gumba */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 20px;
        padding-bottom: 20px;
    }
    
    /* Razmak između gumba za undo/redo */
    .stColumn > div[data-testid="column"] {
        padding: 0 5px;
    }
    
    /* Stilovi za dijalog nespremljenih promjena */
    div.stButton[key="dialog_save"] > button, 
    div.stButton[key="dialog_continue"] > button, 
    div.stButton[key="dialog_cancel"] > button {
        margin-top: 4px !important;
        margin-bottom: 4px !important;
    }
    
    div.stButton[key="dialog_save"] > button {
        background-color: #4CAF50;
        color: white;
    }
    
    div.stButton[key="dialog_continue"] > button {
        background-color: #FFA726;
        color: white;
    }
    
    div.stButton[key="dialog_cancel"] > button {
        background-color: #F44336;
        color: white;
    }

    /* Stiliziranje custom ikona */
    .icon-undo, .icon-redo {
        margin-right: 5px;
        font-size: 14px;
    }
    </style>
    
    <!-- Dodajemo FontAwesome biblioteku -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    """, unsafe_allow_html=True)
    
    # Provjera trenutnog stanja aplikacije
    has_active_calculation = state_manager.get_current_calculation() is not None
    
    # Prikazujemo odgovarajući dijalog ili standardnu navigaciju
    with st.sidebar:
        # Ako je aktivan bilo koji dijalog, prikaži samo njega
        if st.session_state.get('showing_unsaved_dialog', False):
            navigation.render_unsaved_dialog()
        elif st.session_state.get('showing_save_dialog', False):
            navigation.render_save_dialog()
        elif st.session_state.get('showing_save_as_dialog', False):
            navigation.render_save_as_dialog()
        else:
            # Standardna navigacija ako nema aktivnog dijaloga
            # --- GUMBI KOJI SU UVIJEK VIDLJIVI ---
            # Novi proračun - uvijek vidljiv
            if st.button("Novi proračun", key="nav_new", use_container_width=True):
                if navigation.check_unsaved_changes('new'):
                    st.session_state['show_category_selection'] = True
                    st.rerun()
            
            # Otvori proračun - uvijek vidljiv
            if st.button("Otvori proračun", key="nav_open", use_container_width=True):
                if navigation.check_unsaved_changes('open'):
                    # Direktno otvaramo dijalog za odabir datoteke
                    success = file_manager.open_calculation()
                    if success:
                        st.rerun()
            
            # --- GUMBI KOJI SU VIDLJIVI SAMO KAD JE PRORAČUN AKTIVAN ---
            if has_active_calculation:
                # Gumbi za spremanje
                if st.button("Spremi", key="nav_save", use_container_width=True):
                    success = file_manager.save_calculation()
                    if success:
                        st.rerun()
                
                if st.button("Spremi kao", key="nav_save_as", use_container_width=True):
                    success = file_manager.save_calculation_as()
                    if success:
                        st.rerun()
                
                # Gumb za zatvaranje proračuna
                if st.button("Zatvori proračun", key="nav_close", use_container_width=True):
                    if navigation.check_unsaved_changes('close'):
                        navigation.close_current_calculation()
                        st.rerun()
                
                # Gumb za izvoz
                if st.button("Izvoz u Word", key="nav_export", use_container_width=True):
                    word_export.export_current_calculation()
                
                # Gumbi za undo/redo
                history_col1, history_col2 = st.columns([1, 1])
                with history_col1:
                    undo_disabled = not history_manager.can_undo()
                    if st.button(
                        "⟲ Poništi", 
                        key="nav_undo", 
                        disabled=undo_disabled, 
                        use_container_width=True
                    ):
                        history_manager.undo()
                
                with history_col2:
                    redo_disabled = not history_manager.can_redo()
                    if st.button(
                        "⟳ Ponovi", 
                        key="nav_redo", 
                        disabled=redo_disabled,
                        use_container_width=True
                    ):
                        history_manager.redo()
    
    # Glavni sadržaj aplikacije zauzima cijeli ekran
    if 'show_category_selection' in st.session_state and st.session_state['show_category_selection']:
        navigation.show_category_selection()
        if st.button("Povratak na početnu stranicu", key="back_to_home"):
            st.session_state['show_category_selection'] = False
            st.rerun()
    elif state_manager.get_current_calculation():
        state_manager.get_current_calculation().render()
    else:
        navigation.render_home_screen()
            
if __name__ == "__main__":
    main()