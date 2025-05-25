"""
Zajedničke konstante za kalkulatore hidrantskih mreža (unutarnje i vanjske).
"""

# Minimalni tlak na hidrantu prema Pravilniku (MPa i bar)
MIN_REQUIRED_PRESSURE_MPA = 0.25
MIN_REQUIRED_PRESSURE_BAR = 2.5

# Kategorije požarnog opterećenja
FIRE_LOAD_CATEGORIES = {
    "nisko": (0, 1000),    # Nisko: do 1000 MJ/m²
    "srednje": (1000, 2000),  # Srednje: 1000-2000 MJ/m²
    "visoko": (2000, float('inf'))  # Visoko: preko 2000 MJ/m²
}

# Koeficijenti lokalnog otpora za različite elemente
LOCAL_RESISTANCE_COEFFICIENTS = {
    "koljeno_90": 0.9,
    "koljeno_45": 0.5,
    "t_spoj_prolaz": 0.3,
    "t_spoj_odvajanje": 1.3,
    "ventil_zapor": 0.3,
    "ventil_nepovr": 2.0,
    "redukcija": 0.5,
    "vodomjer": 2.5
}

# Konverzijski faktor: m vodenog stupca -> bar
M_WATER_TO_BAR = 0.1

# Gravitacijska konstanta
GRAVITY = 9.81  # m/s²

# Parametri vode
WATER_DENSITY = 998  # kg/m³
WATER_VISCOSITY = 1.002e-3  # Pa·s

# Raspon brzina u cijevima
VELOCITY_RANGES = {
    "minimalna": 0.5,  # m/s
    "optimalna_min": 1.0,  # m/s
    "optimalna_max": 2.5,  # m/s
    "maksimalna": 3.0  # m/s
}

# Optimalna brzina za dimenzioniranje cijevi
OPTIMAL_DESIGN_VELOCITY = 1.5  # m/s