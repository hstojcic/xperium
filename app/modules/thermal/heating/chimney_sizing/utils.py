"""
Pomoćne funkcije za proračun dimnjaka prema EN 13384-2 normi.
"""

import math
from .constants import RHO_L0, GRAVITY, WATER_VAPOR_COEFFICIENTS

def calculate_air_density(temperature, altitude):
    """
    Izračunava gustoću zraka na temelju temperature i nadmorske visine.
    
    Args:
        temperature (float): Temperatura zraka [°C]
        altitude (float): Nadmorska visina [m]
    
    Returns:
        float: Gustoća zraka [kg/m³]
    """
    # Temperatura zraka u Kelvinima
    T_L = temperature + 273.15  # K
    
    # Atmosferski tlak na nadmorskoj visini lokacije (približna formula)
    p_L = 1013 * math.exp(-0.0001184 * altitude)  # hPa
    
    # Izračun gustoće zraka
    rho_L = RHO_L0 * (273.15 / T_L) * (p_L / 1013)
    
    return rho_L

def calculate_flue_gas_density(air_density, flue_gas_temperature, fuel_type):
    """
    Izračunava gustoću dimnih plinova.
    
    Args:
        air_density (float): Gustoća zraka [kg/m³]
        flue_gas_temperature (float): Temperatura dimnih plinova [°C]
        fuel_type (str): Vrsta goriva
    
    Returns:
        float: Gustoća dimnih plinova [kg/m³]
    """
    # Temperatura dimnih plinova u Kelvinima
    T_M = flue_gas_temperature + 273.15  # K
    
    # Udio vodene pare za odabrano gorivo
    x_H2O = WATER_VAPOR_COEFFICIENTS.get(fuel_type, 0.16)
    
    # Izračun gustoće dimnih plinova
    rho_M = air_density * (273.15 / T_M) * (1 - 0.378 * x_H2O)
    
    return rho_M

def calculate_static_draft(air_density, flue_gas_density, chimney_height, safety_number):
    """
    Izračunava statički uzgon dimnjaka.
    
    Args:
        air_density (float): Gustoća zraka [kg/m³]
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
        chimney_height (float): Efektivna visina dimnjaka [m]
        safety_number (float): Sigurnosni broj
    
    Returns:
        float: Statički uzgon [Pa]
    """
    return GRAVITY * chimney_height * (air_density - flue_gas_density) * safety_number

def calculate_flue_gas_velocity(mass_flow, diameter, flue_gas_density):
    """
    Izračunava brzinu strujanja dimnih plinova.
    
    Args:
        mass_flow (float): Maseni protok dimnih plinova [kg/s]
        diameter (float): Unutarnji promjer dimovoda [m]
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
    
    Returns:
        float: Brzina strujanja dimnih plinova [m/s]
    """
    return (4 * mass_flow) / (math.pi * diameter**2 * flue_gas_density)

def calculate_friction_coefficient(roughness, diameter):
    """
    Izračunava koeficijent trenja u dimovodu.
    
    Args:
        roughness (float): Srednja hrapavost [m]
        diameter (float): Unutarnji promjer dimovoda [m]
    
    Returns:
        float: Koeficijent trenja
    """
    return 0.0054 + 0.15 * (roughness/diameter)**0.33

def calculate_pressure_drop_friction(friction_coefficient, chimney_height, flue_gas_density, 
                                    flue_gas_velocity, diameter, safety_number):
    """
    Izračunava pad tlaka zbog trenja u dimovodu.
    
    Args:
        friction_coefficient (float): Koeficijent trenja
        chimney_height (float): Efektivna visina dimnjaka [m]
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
        flue_gas_velocity (float): Brzina strujanja dimnih plinova [m/s]
        diameter (float): Unutarnji promjer dimovoda [m]
        safety_number (float): Sigurnosni broj
    
    Returns:
        float: Pad tlaka zbog trenja [Pa]
    """
    return (friction_coefficient * chimney_height * flue_gas_density * flue_gas_velocity**2) / (2 * diameter) * safety_number

def calculate_pressure_drop_resistance(resistance_coefficient, flue_gas_density, flue_gas_velocity, safety_number):
    """
    Izračunava pad tlaka zbog lokalnih otpora.
    
    Args:
        resistance_coefficient (float): Koeficijent lokalnog otpora
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
        flue_gas_velocity (float): Brzina strujanja dimnih plinova [m/s]
        safety_number (float): Sigurnosni broj
    
    Returns:
        float: Pad tlaka zbog lokalnih otpora [Pa]
    """
    return resistance_coefficient * flue_gas_density * flue_gas_velocity**2 / 2 * safety_number

def calculate_total_pressure_drop(pressure_drop_friction, pressure_drop_resistance):
    """
    Izračunava ukupni pad tlaka u dimovodu.
    
    Args:
        pressure_drop_friction (float): Pad tlaka zbog trenja [Pa]
        pressure_drop_resistance (float): Pad tlaka zbog lokalnih otpora [Pa]
    
    Returns:
        float: Ukupni pad tlaka [Pa]
    """
    return pressure_drop_friction + pressure_drop_resistance

def calculate_actual_draft(static_draft, total_pressure_drop):
    """
    Izračunava stvarni uzgon dimnjaka.
    
    Args:
        static_draft (float): Statički uzgon [Pa]
        total_pressure_drop (float): Ukupni pad tlaka [Pa]
    
    Returns:
        float: Stvarni uzgon [Pa]
    """
    return static_draft - total_pressure_drop

def calculate_inner_wall_temperature(ambient_temperature, flue_gas_temperature, 
                                     thermal_resistance_wall, thermal_resistance_ambient):
    """
    Izračunava temperaturu unutarnje stijenke dimnjaka.
    
    Args:
        ambient_temperature (float): Temperatura okolnog zraka [°C]
        flue_gas_temperature (float): Temperatura dimnih plinova [°C]
        thermal_resistance_wall (float): Toplinski otpor stijenke [m²K/W]
        thermal_resistance_ambient (float): Toplinski otpor prema vanjskom okolišu [m²K/W]
    
    Returns:
        float: Temperatura unutarnje stijenke [°C]
    """
    # Pojednostavljena formula za temperaturu unutarnje stijenke
    # Za kompletan izračun potrebno je koristiti iterativni postupak prema EN 13384-2
    ri = 0.1  # Pretpostavljeni koeficijent prijenosa topline [m²K/W]
    
    tiob = ambient_temperature + (flue_gas_temperature - ambient_temperature) * ri / (ri + thermal_resistance_wall + thermal_resistance_ambient)
    
    return tiob

def check_freezing_condition(inner_wall_temperature, freezing_temperature=0):
    """
    Provjerava uvjet zaleđivanja.
    
    Args:
        inner_wall_temperature (float): Temperatura unutarnje stijenke [°C]
        freezing_temperature (float, optional): Točka ledišta [°C]. Standardno 0°C.
    
    Returns:
        bool: True ako nema opasnosti od zaleđivanja, False inače
    """
    return inner_wall_temperature > freezing_temperature