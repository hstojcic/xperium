"""
Poboljšane konstante i tablice podataka za proračun dimnjaka prema EN 13384-2 normi.
Dodane konstante za nova poboljšanja i ispravke prema normi.
"""

# Standardna gustoća zraka pri 0°C i 1013 hPa [kg/m³]
RHO_L0 = 1.293

# Gravitacijsko ubrzanje [m/s²]
GRAVITY = 9.81

# Standardne vrijednosti sigurnosnih faktora prema EN 13384-2
DEFAULT_SAFETY_NUMBER_SE = 1.2
DEFAULT_CORRECTION_FACTOR_SH = 0.5

# ISPRAVKA: Prošireni koeficijenti otpora za različite elemente dimovoda
RESISTANCE_COEFFICIENTS = {
    "Luk 87°": 0.7,
    "Luk 45°": 0.4,
    "Luk 30°": 0.2,
    "T-komad 87°": 1.3,
    "Y-komad 45°": 0.9,
    "Y-komad 30°": 0.6,
    "Direktni ulaz": 0.1,
    "Otvoreno ušće": 0.0,
    "Jednostavna kišna kapa": 1.0,      # DODANO
    "Kišna kapa s deflektorom": 1.5,     # ISPRAVKA naziva
    "Rotacijska kapa": 2.0,             # DODANO
    "Kišna kapa - standardna": 1.2,     # DODANO
    "Redukcija postepena": 0.3,         # DODANO
    "Redukcija nagla": 0.8,             # DODANO
    "Čišćenjak": 0.4                    # DODANO
}

# Poboljšani koeficijenti vodene pare za različita goriva
WATER_VAPOR_COEFFICIENTS = {
    "Zemni plin": 0.16,
    "Ukapljeni naftni plin": 0.14,
    "Loživo ulje EL": 0.12,
    "Loživo ulje S": 0.11,
    "Drvo": 0.20,
    "Peleti": 0.18,
    "Biomasa": 0.22,                    # DODANO
    "Ugljen": 0.08                      # DODANO
}

# Toplinske provodljivosti materijala [W/mK]
THERMAL_CONDUCTIVITY = {
    "Keramika": 1.1,
    "Nehrđajući čelik": 15,
    "Aluminij": 200,
    "Lagani beton": 0.6,
    "PP": 0.22,
    "PE": 0.35,                         # DODANO
    "PVC": 0.16,                        # DODANO
    "Čelik": 50,                        # DODANO
    "Vatrostalna cigla": 0.8,           # DODANO
    "Šamot": 1.0                        # DODANO
}

# Tipične srednje hrapavosti površina [mm]
ROUGHNESS = {
    "PP gladak": 0.5,
    "PP": 0.7,                          # DODANO
    "PE": 0.6,                          # DODANO
    "Keramika": 1.5,
    "Keramika glazirana": 0.8,          # DODANO
    "Nehrđajući čelik": 0.1,
    "Nehrđajući čelik brušen": 0.05,   # DODANO
    "Čelik": 0.5,                      # DODANO
    "Zidani dimnjak": 5.0,
    "Zidani dimnjak glačan": 3.0,      # DODANO
    "Lagani beton": 3.0,
    "Šamot": 2.0,                      # DODANO
    "Vatrostalni beton": 2.5            # DODANO
}

# DODANO: Minimalne temperature za različita goriva [°C]
MIN_TEMPERATURES = {
    "Zemni plin": 25,
    "Ukapljeni naftni plin": 30,
    "Loživo ulje": 35,
    "Drvo": 40,
    "Peleti": 35,
    "Ugljen": 45
}

# DODANO: Tipične točke rosišta za različita goriva pri optimalnom izgaranju [°C]
TYPICAL_DEW_POINTS = {
    "Zemni plin": 57,
    "Ukapljeni naftni plin": 52,
    "Loživo ulje": 47,
    "Drvo": 45,
    "Peleti": 48
}

# DODANO: Preporučeni CO2 udjeli za različita goriva [%]
OPTIMAL_CO2_RANGES = {
    "Zemni plin": (9.0, 11.5),
    "Ukapljeni naftni plin": (10.0, 12.5),
    "Loživo ulje": (11.0, 13.5),
    "Drvo": (12.0, 16.0),
    "Peleti": (10.0, 14.0)
}

# Predefinirani kondenzacijski kotlovi s dodatnim modelima
CONDENSING_BOILERS = {
    "Vaillant ecoTEC plus VC 20 CS / 1-5": {
        "fuel": "Zemni plin",
        "full_load": {
            "nominal_heat_output": 20.9,
            "heat_input": 20.4,
            "co2_percentage": 9.6,
            "flue_gas_mass_flow": 12.79,
            "flue_gas_temperature": 85,
            "max_positive_pressure": 130
        },
        "partial_load": {
            "nominal_heat_output": 3.2,
            "heat_input": 3.2,
            "co2_percentage": 9.6,
            "flue_gas_mass_flow": 1.51,
            "flue_gas_temperature": 35,
            "max_positive_pressure": 30
        },
        "connection": {
            "diameter": 60,
            "transition_type": "Redukcija konusna 60°"
        }
    },
    "Vaillant ecoTEC plus VU 25 CS / 1-5": {
        "fuel": "Zemni plin",
        "full_load": {
            "nominal_heat_output": 25.5,
            "heat_input": 25.0,
            "co2_percentage": 9.6,
            "flue_gas_mass_flow": 15.3,
            "flue_gas_temperature": 85,
            "max_positive_pressure": 145
        },
        "partial_load": {
            "nominal_heat_output": 3.5,
            "heat_input": 3.5,
            "co2_percentage": 9.6,
            "flue_gas_mass_flow": 1.75,
            "flue_gas_temperature": 35,
            "max_positive_pressure": 30
        },
        "connection": {
            "diameter": 60,
            "transition_type": "Redukcija konusna 60°"
        }
    },
    # DODANI NOVI MODELI
    "Viessmann Vitodens 100-W 26 kW": {
        "fuel": "Zemni plin",
        "full_load": {
            "nominal_heat_output": 26.0,
            "heat_input": 25.4,
            "co2_percentage": 9.2,
            "flue_gas_mass_flow": 16.8,
            "flue_gas_temperature": 80,
            "max_positive_pressure": 150
        },
        "partial_load": {
            "nominal_heat_output": 3.8,
            "heat_input": 3.8,
            "co2_percentage": 9.2,
            "flue_gas_mass_flow": 2.1,
            "flue_gas_temperature": 40,
            "max_positive_pressure": 35
        },
        "connection": {
            "diameter": 60,
            "transition_type": "Redukcija konusna 60°"
        }
    },
    "Buderus Logamax plus GB172-24": {
        "fuel": "Zemni plin",
        "full_load": {
            "nominal_heat_output": 24.0,
            "heat_input": 23.5,
            "co2_percentage": 9.4,
            "flue_gas_mass_flow": 15.1,
            "flue_gas_temperature": 82,
            "max_positive_pressure": 140
        },
        "partial_load": {
            "nominal_heat_output": 3.6,
            "heat_input": 3.6,
            "co2_percentage": 9.4,
            "flue_gas_mass_flow": 1.9,
            "flue_gas_temperature": 38,
            "max_positive_pressure": 32
        },
        "connection": {
            "diameter": 60,
            "transition_type": "Redukcija konusna 60°"
        }
    }
}

# Predefinirani dimovodni sustavi s dodatnim modelima
CHIMNEY_SYSTEMS = {
    "Schiedel MULTI 140": {
        "type": "Dimovodna naprava u oknu",
        "manufacturer": "Schiedel",
        "model": "MULTI",
        "inner_diameter": 140,
        "material": "Keramika",
        "thickness": 7,
        "thermal_conductivity": 1.1,
        "roughness": 1.5,
        "annular_gap": "Protutok zraka (53 mm)",
        "outer_section": "Kvadratni 260 mm",
        "outer_material": "Lagani beton",
        "outer_thickness": 50,
        "thermal_resistance": 0.12
    },
    "Schiedel MULTI 160": {
        "type": "Dimovodna naprava u oknu",
        "manufacturer": "Schiedel",
        "model": "MULTI",
        "inner_diameter": 160,
        "material": "Keramika",
        "thickness": 7,
        "thermal_conductivity": 1.1,
        "roughness": 1.5,
        "annular_gap": "Protutok zraka (53 mm)",
        "outer_section": "Kvadratni 300 mm",
        "outer_material": "Lagani beton",
        "outer_thickness": 65,
        "thermal_resistance": 0.14
    },
    # DODANI NOVI SUSTAVI
    "Schiedel MULTI 180": {
        "type": "Dimovodna naprava u oknu",
        "manufacturer": "Schiedel",
        "model": "MULTI",
        "inner_diameter": 180,
        "material": "Keramika",
        "thickness": 8,
        "thermal_conductivity": 1.1,
        "roughness": 1.5,
        "annular_gap": "Protutok zraka (53 mm)",
        "outer_section": "Kvadratni 340 mm",
        "outer_material": "Lagani beton",
        "outer_thickness": 70,
        "thermal_resistance": 0.16
    },
    "Jeremias DW-ECO 2.0 Ø130": {
        "type": "Dvostruki dimovod od nehrđajućeg čelika",
        "manufacturer": "Jeremias",
        "model": "DW-ECO 2.0",
        "inner_diameter": 130,
        "material": "Nehrđajući čelik",
        "thickness": 0.6,
        "thermal_conductivity": 15,
        "roughness": 0.1,
        "annular_gap": "Mineralna vuna 30 mm",
        "outer_section": "Cijev Ø200",
        "outer_material": "Nehrđajući čelik",
        "outer_thickness": 0.5,
        "thermal_resistance": 0.85
    }
}

# Predefinirani spojni elementi s dodatnim modelima
CONNECTING_ELEMENTS = {
    "Centrotherm DN 60/100": {
        "type": "Koncentrični spojni element",
        "manufacturer": "Centrotherm",
        "model": "System Chimneys PP / Metal",
        "inner_diameter": 56,
        "thickness": 2,
        "material": "PP gladak",
        "roughness": 0.5,
    },
    "Centrotherm DN 80/125": {
        "type": "Koncentrični spojni element",
        "manufacturer": "Centrotherm",
        "model": "System Chimneys PP / Metal",
        "inner_diameter": 76,
        "thickness": 2,
        "material": "PP gladak",
        "roughness": 0.5,
    },
    # DODANI NOVI ELEMENTI
    "Ubbink DN 60/100 PP": {
        "type": "Koncentrični spojni element",
        "manufacturer": "Ubbink",
        "model": "Rolux PP",
        "inner_diameter": 56,
        "thickness": 2.3,
        "material": "PP",
        "roughness": 0.7,
    },
    "Viessmann DN 80/125 PP": {
        "type": "Koncentrični spojni element",
        "manufacturer": "Viessmann",
        "model": "Vitotec",
        "inner_diameter": 76,
        "thickness": 2.5,
        "material": "PP gladak",
        "roughness": 0.5,
    }
}

# DODANO: Validacijski parametri prema EN 13384-2
VALIDATION_LIMITS = {
    "min_chimney_height": 3.0,          # m
    "max_chimney_height": 50.0,         # m
    "min_chimney_diameter": 80,         # mm
    "max_chimney_diameter": 600,        # mm
    "min_flue_gas_temp": 30,           # °C
    "max_flue_gas_temp": 300,          # °C
    "min_co2_percentage": 5.0,         # %
    "max_co2_percentage": 18.0,        # %
    "min_mass_flow": 0.5,              # g/s
    "max_mass_flow": 200.0,            # g/s
    "min_outdoor_temp": -30,           # °C
    "max_outdoor_temp": 40,            # °C
    "max_appliances": 5                # broj ložišta prema EN 13384-2
}

# DODANO: Preporučene brzine strujanja dimnih plinova [m/s]
RECOMMENDED_VELOCITIES = {
    "min_velocity": 2.0,               # m/s - minimum za dobar vuk
    "max_velocity": 20.0,              # m/s - maksimum zbog buke i erozije
    "optimal_range": (4.0, 12.0)      # m/s - optimalan raspon
}

# DODANO: Faktori sigurnosti za različite slučajeve
SAFETY_FACTORS = {
    "standard": 1.2,                   # Standardni slučaj
    "multiple_appliances": 1.3,        # Više ložišta
    "high_building": 1.4,              # Visoka zgrada
    "difficult_conditions": 1.5        # Težki uvjeti (vjetar, lokacija)
}