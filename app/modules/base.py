import streamlit as st
from abc import ABC, abstractmethod
import copy

class BaseCalculation(ABC):
    """
    Bazna klasa za sve vrste proračuna
    """
    
    def __init__(self, name="Proračun"):
        self.name = name
        self.state_manager = st.session_state.state_manager
        self.history_manager = st.session_state.history_manager
    
    @abstractmethod
    def render(self):
        """
        Prikazuje sučelje proračuna
        """
        pass
    
    def record_state(self, description):
        """
        Snima trenutno stanje za undo/redo
        
        Args:
            description: Opis akcije koja se snima
        """
        state = self.get_state()
        self.history_manager.record_state(state, description)
    
    def get_state(self):
        """
        Vraća trenutno stanje proračuna za undo/redo
        
        Returns:
            Objekt stanja (kopija trenutnog stanja)
        """
        # Podrazumijevano, stvaramo deep copy svih atributa
        # osim onih koji počinju s "_" ili su instance key objekata
        excluded_attrs = ['state_manager', 'history_manager', 'name']
        state = {}
        
        for attr_name, attr_value in self.__dict__.items():
            if not attr_name.startswith('_') and attr_name not in excluded_attrs:
                state[attr_name] = copy.deepcopy(attr_value)
        
        return state
    
    def restore_state(self, state):
        """
        Vraća stanje proračuna iz snimljenog stanja
        
        Args:
            state: Objekt stanja
        """
        for attr_name, attr_value in state.items():
            setattr(self, attr_name, attr_value)
    
    def get_default_filename(self):
        """
        Vraća standardno ime datoteke za ovaj proračun
        
        Returns:
            String s imenom datoteke
        """
        # Podrazumijevano ime - podklase mogu prepraviti
        sanitized_name = self.name.replace(" ", "_").lower()
        return f"{sanitized_name}.calc"
    
    def serialize(self):
        """
        Pretvara proračun u format za spremanje
        
        Returns:
            Dictionary s podacima proračuna
        """
        # Slično kao get_state, ali za spremanje u datoteku
        return self.get_state()
    
    def deserialize(self, data):
        """
        Učitava proračun iz formata za spremanje
        
        Args:
            data: Dictionary s podacima proračuna
        """
        # Slično kao restore_state, ali za učitavanje iz datoteke
        self.restore_state(data)
    
    def export_to_word(self, doc):
        """
        Izvozi proračun u Word dokument
        
        Args:
            doc: Word dokument (python-docx Document objekt)
        """
        # Podrazumijevana implementacija - podklase trebaju prepraviti
        doc.add_paragraph(f"Proračun: {self.name}")
        doc.add_paragraph("Napomena: Ovaj proračun nema prilagođeni izvoz u Word.")