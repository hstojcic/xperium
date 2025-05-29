"""
Base calculation class for all calculators.
"""

import datetime
import streamlit as st
import copy
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseCalculation(ABC):
    """
    Bazna klasa za sve kalkulatore.
    
    Provides common functionality for all calculation modules including:
    - Session state management
    - History tracking
    - Data persistence (serialize/deserialize)
    - State management for undo/redo functionality
    - Export capabilities
    """
    
    def __init__(self, name: str = "Proračun"):
        """
        Initialize base calculation.
        
        Args:
            name (str): Name of the calculator
        """
        self.name = name
        self.history: List[Dict[str, Any]] = []
        self.version = "1.0"
        self.last_calculation = None
        
        # Initialize state and history managers if available
        self.state_manager = getattr(st.session_state, 'state_manager', None)
        self.history_manager = getattr(st.session_state, 'history_manager', None)
    
    @abstractmethod
    def render(self):
        """
        Prikazuje sučelje proračuna
        """
        pass
    
    def record_state(self, action: str, data: Optional[Dict] = None):
        """
        Record action in history.
        
        Args:
            action (str): Description of the action
            data (Dict, optional): Additional data to store
        """
        entry = {
            'timestamp': datetime.datetime.now(),
            'action': action,
            'data': data or {}
        }
        self.history.append(entry)
        
        # Keep only last 50 entries to prevent memory issues
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        # Also record in the application-wide history manager if available
        if self.history_manager:
            state = self.get_state()
            self.history_manager.record_state(state, action)
    
    def get_last_calculation_time(self) -> Optional[datetime.datetime]:
        """
        Get timestamp of last calculation.
        
        Returns:
            datetime.datetime: Timestamp of last calculation, or None if no calculations
        """
        calc_entries = [entry for entry in self.history if 'proračun' in entry['action'].lower()]
        if calc_entries:
            return calc_entries[-1]['timestamp']
        return None
    
    def clear_history(self):
        """Clear calculation history."""
        self.history = []
        self.record_state("Očišćena povijest proračuna")
    
    def export_history(self) -> List[Dict]:
        """
        Export calculation history.
        
        Returns:
            List[Dict]: History entries
        """
        return [
            {
                'timestamp': entry['timestamp'].isoformat(),
                'action': entry['action'],
                'data': entry['data']
            }
            for entry in self.history
        ]
    
    def validate_common_parameters(self, data: Dict) -> tuple:
        """
        Validate common parameters across all calculators.
        
        Args:
            data (Dict): Input data
            
        Returns:
            tuple: (errors, warnings) lists
        """
        errors = []
        warnings = []
        
        # Check for required fields
        if not data:
            errors.append("Nema podataka za validaciju")
            return errors, warnings
        
        # Add common validations here
        return errors, warnings
    
    def get_state(self):
        """
        Vraća trenutno stanje proračuna za undo/redo
        
        Returns:
            Objekt stanja (kopija trenutnog stanja)
        """
        # Stvaramo deep copy svih atributa osim onih koji počinju s "_" 
        # ili su instance key objekata
        excluded_attrs = ['state_manager', 'history_manager', 'name']
        state = {}
        
        for attr_name, attr_value in self.__dict__.items():
            if not attr_name.startswith('_') and attr_name not in excluded_attrs:
                try:
                    state[attr_name] = copy.deepcopy(attr_value)
                except Exception as e:
                    # If we can't deep copy, try regular copy
                    try:
                        state[attr_name] = copy.copy(attr_value)
                    except:
                        # If that fails too, just reference it
                        state[attr_name] = attr_value
        
        return state
    
    def restore_state(self, state: Dict[str, Any]):
        """
        Vraća stanje proračuna iz snimljenog stanja
        
        Args:
            state: Objekt stanja
        """
        for attr_name, attr_value in state.items():
            setattr(self, attr_name, attr_value)
    
    def get_default_filename(self) -> str:
        """
        Vraća standardno ime datoteke za ovaj proračun
        
        Returns:
            String s imenom datoteke
        """
        # Podrazumijevano ime - podklase mogu prepraviti
        sanitized_name = self.name.replace(" ", "_").lower()
        return f"{sanitized_name}.calc"
    
    def serialize(self) -> Dict[str, Any]:
        """
        Pretvara proračun u format za spremanje
        
        Returns:
            Dictionary s podacima proračuna
        """
        # Slično kao get_state, ali za spremanje u datoteku
        serialized_data = {
            'name': self.name,
            'version': self.version,
            'timestamp': datetime.datetime.now().isoformat(),
            'state': self.get_state(),
            'history': self.export_history()
        }
        return serialized_data
    
    def deserialize(self, data: Dict[str, Any]):
        """
        Učitava proračun iz formata za spremanje
        
        Args:
            data: Dictionary s podacima proračuna
        """
        # Učitavanje osnovnih informacija
        if 'name' in data:
            self.name = data['name']
        if 'version' in data:
            self.version = data['version']
        
        # Učitavanje stanja
        if 'state' in data:
            self.restore_state(data['state'])
        
        # Učitavanje povijesti ako postoji
        if 'history' in data:
            self.history = []
            for entry in data['history']:
                restored_entry = {
                    'timestamp': datetime.datetime.fromisoformat(entry['timestamp']),
                    'action': entry['action'],
                    'data': entry['data']
                }
                self.history.append(restored_entry)
    
    def export_to_word(self, doc):
        """
        Izvozi proračun u Word dokument
        
        Args:
            doc: Word dokument (python-docx Document objekt)
        """
        # Podrazumijevana implementacija - podklase trebaju prepraviti
        doc.add_paragraph(f"Proračun: {self.name}")
        doc.add_paragraph("Napomena: Ovaj proračun nema prilagođeni izvoz u Word.")
    
    def reset_to_defaults(self):
        """
        Reset calculator to default values.
        Subclasses should override this to provide specific reset behavior.
        """
        self.last_calculation = None
        self.record_state("Resetiranje na zadane vrijednosti")
    
    def validate_and_calculate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate input data and perform calculation.
        Subclasses should override this method.
        
        Args:
            data: Input data for calculation
            
        Returns:
            Dictionary with calculation results and validation status
        """
        errors, warnings = self.validate_common_parameters(data)
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'results': {}
        }
    
    def format_results_for_display(self, results: Dict[str, Any]) -> str:
        """
        Format calculation results for display.
        Subclasses should override this for custom formatting.
        
        Args:
            results: Calculation results
            
        Returns:
            Formatted string for display
        """
        return str(results)
    
    def get_calculation_summary(self) -> Dict[str, Any]:
        """
        Get summary of calculation for reports and exports.
        
        Returns:
            Dictionary with calculation summary
        """
        return {
            'name': self.name,
            'version': self.version,
            'last_calculation': self.last_calculation,
            'calculation_count': len([e for e in self.history if 'proračun' in e['action'].lower()])
        }