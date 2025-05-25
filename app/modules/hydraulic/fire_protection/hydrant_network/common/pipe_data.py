"""
Modul s podacima o cijevima za hidrantske mreže.
"""
import math

class PipeData:
    """Podaci o standardnim promjerima i karakteristikama cijevi."""
    
    def __init__(self):
        # Promjeri cijevi (DN i unutarnji promjer u mm)
        self.diameters = {
            "DN 40": 41.9,  # Unutarnji promjer za DN 40
            "DN 50": 53.1,  # Unutarnji promjer za DN 50
            "DN 65": 68.9,  # Unutarnji promjer za DN 65
            "DN 80": 80.8,  # Unutarnji promjer za DN 80
            "DN 100": 105.3  # Unutarnji promjer za DN 100
        }
        
        # Materijali cijevi
        self.materials = ["Pocinčani čelik", "Nehrđajući čelik", "PPR", "PE-X"]
        
        # Koeficijent hrapavosti za različite materijale (mm)
        self.roughness = {
            "Pocinčani čelik": 0.15,
            "Nehrđajući čelik": 0.03,
            "PPR": 0.01,
            "PE-X": 0.01
        }
    
    def get_inner_diameter(self, dn):
        """Vraća unutarnji promjer cijevi u mm za zadani DN."""
        return self.diameters.get(dn, 0)
    
    def get_inner_diameter_m(self, dn):
        """Vraća unutarnji promjer cijevi u m za zadani DN."""
        return self.get_inner_diameter(dn) / 1000
    
    def get_all_diameters(self):
        """Vraća sve dostupne promjere cijevi."""
        return list(self.diameters.keys())
    
    def get_standard_diameter(self, required_diameter_mm):
        """Određuje najbliži standardni promjer cijevi (DN) na temelju izračunatog promjera."""
        for dn, inner_diameter in sorted(self.diameters.items(), key=lambda x: x[1]):
            if inner_diameter >= required_diameter_mm:
                return dn
        return list(self.diameters.keys())[-1]  # Najveći dostupni promjer
    
    def calculate_section_area(self, dn):
        """Izračunava površinu presjeka cijevi u m² za zadani DN."""
        inner_diameter_m = self.get_inner_diameter_m(dn)
        return math.pi * (inner_diameter_m ** 2) / 4

# Instanca klase s podacima o cijevima
PIPE_DATA = PipeData()