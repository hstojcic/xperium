# modules/thermal/ventilation_recovery/constants.py

# Konstante za proračun protoka zraka
AIR_QUALITY_CATEGORIES = {
    "I": {"name": "Visoka razina", "flow_rate": 36.0},  # m³/h po osobi
    "II": {"name": "Srednja razina", "flow_rate": 25.2},  # m³/h po osobi
    "III": {"name": "Umjerena razina", "flow_rate": 14.4}  # m³/h po osobi
}

AREA_USAGE_INTENSITY = {
    "low": {"name": "Nizak intenzitet", "flow_rate": 2.0},  # m³/(h·m²)
    "medium": {"name": "Srednji intenzitet", "flow_rate": 2.5},  # m³/(h·m²)
    "high": {"name": "Visok intenzitet", "flow_rate": 3.0}  # m³/(h·m²)
}

AIR_CHANGE_RATES = {
    "low": {"name": "Minimalno", "rate": 6},  # h⁻¹
    "medium": {"name": "Standardno", "rate": 8},  # h⁻¹
    "high": {"name": "Maksimalno", "rate": 10}  # h⁻¹
}

# Vrijednosti za toplinsko opterećenje
HEAT_LOAD_PERSON = {
    "resting": {"name": "U mirovanju", "load": 80},  # W/osobi
    "light": {"name": "Lagana aktivnost", "load": 100},  # W/osobi
    "moderate": {"name": "Umjerena aktivnost", "load": 130}  # W/osobi
}

LIGHTING_POWER_DENSITY = {
    "economic": {"name": "Ekonomična rasvjeta", "power": 10},  # W/m²
    "standard": {"name": "Standardna rasvjeta", "power": 15},  # W/m²
    "intensive": {"name": "Intenzivna rasvjeta", "power": 20}  # W/m²
}

DELTA_T_RANGES = {
    "small": {"name": "Mali ΔT", "value": 3},  # K
    "medium": {"name": "Srednji ΔT", "value": 5},  # K
    "large": {"name": "Veliki ΔT", "value": 8}  # K
}

# Preporučene brzine zraka u kanalima
AIR_VELOCITY_RANGES = {
    "main_duct": {"min": 5.0, "optimal": 6.5, "max": 8.0},  # m/s
    "branch": {"min": 3.0, "optimal": 4.0, "max": 5.0},  # m/s
    "terminal": {"min": 2.0, "optimal": 2.5, "max": 3.0}  # m/s
}

# Lokalni koeficijenti otpora za ventilacijske elemente
LOCAL_RESISTANCE_COEFFICIENTS = {
    "bend_90deg": {
        "name": "Koljeno 90°",
        "min": 0.3,
        "max": 1.5,
        "standard": 0.7
    },
    "bend_45deg": {
        "name": "Koljeno 45°",
        "min": 0.2,
        "max": 0.9,
        "standard": 0.4
    },
    "t_junction_straight": {
        "name": "T-komad (prolaz)",
        "min": 0.3,
        "max": 0.5,
        "standard": 0.4
    },
    "t_junction_branch": {
        "name": "T-komad (odvajanje)",
        "min": 1.0,
        "max": 2.0,
        "standard": 1.3
    },
    "sudden_expansion": {
        "name": "Naglo proširenje",
        "min": 0.5,
        "max": 1.0,
        "standard": 0.7
    },
    "sudden_contraction": {
        "name": "Naglo suženje",
        "min": 0.2,
        "max": 0.5,
        "standard": 0.3
    },
    "duct_inlet": {
        "name": "Ulaz u kanal",
        "min": 0.5,
        "max": 1.0,
        "standard": 0.5
    },
    "duct_outlet": {
        "name": "Izlaz iz kanala",
        "min": 1.0,
        "max": 1.0,
        "standard": 1.0
    },
    "diffuser": {
        "name": "Difuzor",
        "min": 2.0,
        "max": 5.0,
        "standard": 3.0
    },
    "extract_grille": {
        "name": "Odsisna rešetka",
        "min": 1.5,
        "max": 3.0,
        "standard": 2.0
    }
}

# Standardne dimenzije kanala
STANDARD_DUCT_DIAMETERS = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000]  # mm
STANDARD_RECTANGULAR_DIMENSIONS = [100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1200]  # mm

# Fizikalne konstante
AIR_DENSITY = 1.2  # kg/m³ pri standardnim uvjetima
AIR_SPECIFIC_HEAT = 1005  # J/(kg·K)