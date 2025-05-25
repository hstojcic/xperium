"""
Specifične konstante za kalkulator unutarnje hidrantske mreže.
"""

class FireLoadFlowTable:
    """Implementacija tablice 1 iz Pravilnika o hidrantskoj mreži za gašenje požara."""
    
    def __init__(self):
        # Vrijednosti iz tablice 1 (specifično požarno opterećenje -> protok)
        self.table = {
            300: 25,   # do 300 MJ/m² -> 25 l/min
            400: 30,   # do 400 MJ/m² -> 30 l/min
            500: 40,   # do 500 MJ/m² -> 40 l/min
            600: 50,   # do 600 MJ/m² -> 50 l/min
            700: 60,   # do 700 MJ/m² -> 60 l/min
            800: 100,  # do 800 MJ/m² -> 100 l/min
            1000: 150, # do 1000 MJ/m² -> 150 l/min
            2000: 300, # do 2000 MJ/m² -> 300 l/min
            float('inf'): 450  # preko 2000 MJ/m² -> 450 l/min
        }
    
    def get_flow_for_load(self, fire_load):
        """Vraća potrebnu protočnu količinu vode za zadano požarno opterećenje."""
        for limit, flow in sorted(self.table.items()):
            if fire_load <= limit:
                return flow
        return self.table[float('inf')]

# Instanca tablice
FIRE_LOAD_FLOW_TABLE = FireLoadFlowTable()

# Minimalno vrijeme opskrbe vodom za unutarnju hidrantsku mrežu
MIN_SUPPLY_DURATION_INTERNAL = 60  # minuta

# Default visina hidranta od poda
DEFAULT_HYDRANT_HEIGHT = 1.5  # m