"""
Konstante i tablice podataka za proračun dimnjaka prema EN 13384-2 normi.
"""

# Standardna gustoća zraka pri 0°C i 1013 hPa [kg/m³]
RHO_L0 = 1.293

# Gravitacijsko ubrzanje [m/s²]
GRAVITY = 9.81

# Standardne vrijednosti sigurnosnih faktora
DEFAULT_SAFETY_NUMBER_SE = 1.2
DEFAULT_CORRECTION_FACTOR_SH = 0.5

# Koeficijenti otpora za različite elemente dimovoda
RESISTANCE_COEFFICIENTS = {
    "Luk 87°": 0.7,
    "Luk 45°": 0.4,
    "T-komad 87°": 1.3,
    "Y-komad 45°": 0.9,
    "Direktni ulaz": 0.1,
    "Otvoreno ušće": 0.0,
    "Kišna kapa": 1.5
}

# Koeficijenti vodene pare za različita goriva
WATER_VAPOR_COEFFICIENTS = {
    "Zemni plin": 0.16,
    "Ukapljeni naftni plin": 0.14,
    "Loživo ulje": 0.12,
    "Drvo": 0.20,
    "Peleti": 0.18
}

# Toplinske provodljivosti materijala [W/mK]
THERMAL_CONDUCTIVITY = {
    "Keramika": 1.1,
    "Nehrđajući čelik": 15,
    "Aluminij": 200,
    "Lagani beton": 0.6,
    "PP": 0.22
}

# Tipične srednje hrapavosti površina [mm]
ROUGHNESS = {
    "PP gladak": 0.5,
    "Keramika": 1.5,
    "Nehrđajući čelik": 0.1,
    "Zidani dimnjak": 5.0,
    "Lagani beton": 3.0
}

# Predefinirani kondenzacijski kotlovi
CONDENSING_BOILERS = {
    "Vaillant ecoTEC plus VC 20 CS / 1-5": {
        "fuel": "Zemni plin",
        "full_load": {
            "nominal_heat_output": 20.9,  # kW
            "heat_input": 20.4,  # kW
            "co2_percentage": 9.6,  # %
            "flue_gas_mass_flow": 12.79,  # g/s
            "flue_gas_temperature": 85,  # °C
            "max_positive_pressure": 130  # Pa
        },
        "partial_load": {
            "nominal_heat_output": 3.2,  # kW
            "heat_input": 3.2,  # kW
            "co2_percentage": 9.6,  # %
            "flue_gas_mass_flow": 1.51,  # g/s
            "flue_gas_temperature": 35,  # °C
            "max_positive_pressure": 30  # Pa
        },
        "connection": {
            "diameter": 60,  # mm
            "transition_type": "Redukcija konusna 60°"
        }
    },
    "Vaillant ecoTEC plus VU 25 CS / 1-5": {
        "fuel": "Zemni plin",
        "full_load": {
            "nominal_heat_output": 25.5,  # kW
            "heat_input": 25.0,  # kW
            "co2_percentage": 9.6,  # %
            "flue_gas_mass_flow": 15.3,  # g/s
            "flue_gas_temperature": 85,  # °C
            "max_positive_pressure": 145  # Pa
        },
        "partial_load": {
            "nominal_heat_output": 3.5,  # kW
            "heat_input": 3.5,  # kW
            "co2_percentage": 9.6,  # %
            "flue_gas_mass_flow": 1.75,  # g/s
            "flue_gas_temperature": 35,  # °C
            "max_positive_pressure": 30  # Pa
        },
        "connection": {
            "diameter": 60,  # mm
            "transition_type": "Redukcija konusna 60°"
        }
    }
}

# Predefinirani dimovodni sustavi
CHIMNEY_SYSTEMS = {
    "Schiedel MULTI 140": {
        "type": "Dimovodna naprava u oknu",
        "manufacturer": "Schiedel",
        "model": "MULTI",
        "inner_diameter": 140,  # mm
        "material": "Keramika",
        "thickness": 7,  # mm
        "thermal_conductivity": 1.1,  # W/mK
        "roughness": 1.5,  # mm
        "annular_gap": "Protutok zraka (53 mm)",
        "outer_section": "Kvadratni 260 mm",
        "outer_material": "Lagani beton",
        "outer_thickness": 50,  # mm
        "thermal_resistance": 0.12  # m²K/W
    },
    "Schiedel MULTI 160": {
        "type": "Dimovodna naprava u oknu",
        "manufacturer": "Schiedel",
        "model": "MULTI",
        "inner_diameter": 160,  # mm
        "material": "Keramika",
        "thickness": 7,  # mm
        "thermal_conductivity": 1.1,  # W/mK
        "roughness": 1.5,  # mm
        "annular_gap": "Protutok zraka (53 mm)",
        "outer_section": "Kvadratni 300 mm",
        "outer_material": "Lagani beton",
        "outer_thickness": 65,  # mm
        "thermal_resistance": 0.14  # m²K/W
    }
}

# Predefinirani spojni elementi
CONNECTING_ELEMENTS = {
    "Centrotherm DN 60/100": {
        "type": "Koncentrični spojni element",
        "manufacturer": "Centrotherm",
        "model": "System Chimneys PP / Metal",
        "inner_diameter": 56,  # mm
        "thickness": 2,  # mm
        "material": "PP gladak",
        "roughness": 0.5,  # mm
    },
    "Centrotherm DN 80/125": {
        "type": "Koncentrični spojni element",
        "manufacturer": "Centrotherm",
        "model": "System Chimneys PP / Metal",
        "inner_diameter": 76,  # mm
        "thickness": 2,  # mm
        "material": "PP gladak",
        "roughness": 0.5,  # mm
    }
}