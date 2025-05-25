import streamlit as st
import copy

class HistoryManager:
    """
    Klasa za upravljanje povijesti promjena (undo/redo)
    """
    
    def __init__(self):
        # Inicijalizacija stogova za undo/redo
        if 'undo_stack' not in st.session_state:
            st.session_state.undo_stack = []
        
        if 'redo_stack' not in st.session_state:
            st.session_state.redo_stack = []
    
    def record_state(self, state_data, description):
        """
        Snima trenutno stanje za kasnije poništavanje
        
        Args:
            state_data: Podaci stanja za spremanje
            description: Opis akcije koja se sprema
        """
        st.session_state.undo_stack.append({
            'data': state_data,
            'description': description
        })
        
        # Čišćenje redo stacka nakon nove akcije
        st.session_state.redo_stack = []
        
        # Označavanje da je došlo do promjene
        st.session_state.state_manager.set_calculation_changed(True)
    
    def can_undo(self):
        """Vraća True ako postoji stanje za poništavanje"""
        return len(st.session_state.undo_stack) > 0
    
    def can_redo(self):
        """Vraća True ako postoji stanje za vraćanje"""
        return len(st.session_state.redo_stack) > 0
    
    def undo(self):
        """
        Poništava zadnju akciju
        """
        if not self.can_undo():
            return
        
        # Dohvaćanje trenutnog proračuna
        current_calculation = st.session_state.state_manager.get_current_calculation()
        if not current_calculation:
            return
        
        # Spremanje trenutnog stanja u redo stack
        current_state = current_calculation.get_state()
        st.session_state.redo_stack.append({
            'data': current_state,
            'description': "Redo"
        })
        
        # Vraćanje prethodnog stanja
        prev_state = st.session_state.undo_stack.pop()
        current_calculation.restore_state(prev_state['data'])
        
        # Ako je ovo zadnja akcija na stogu, nema više promjena
        if not self.can_undo():
            st.session_state.state_manager.set_calculation_changed(False)
    
    def redo(self):
        """
        Vraća poništenu akciju
        """
        if not self.can_redo():
            return
        
        # Dohvaćanje trenutnog proračuna
        current_calculation = st.session_state.state_manager.get_current_calculation()
        if not current_calculation:
            return
        
        # Spremanje trenutnog stanja u undo stack
        current_state = current_calculation.get_state()
        st.session_state.undo_stack.append({
            'data': current_state,
            'description': "Undo"
        })
        
        # Vraćanje "budućeg" stanja
        next_state = st.session_state.redo_stack.pop()
        current_calculation.restore_state(next_state['data'])
        
        # Označavanje da je došlo do promjene
        st.session_state.state_manager.set_calculation_changed(True)