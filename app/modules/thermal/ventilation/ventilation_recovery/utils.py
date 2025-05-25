# modules/thermal/ventilation/ventilation_recovery/utils.py

import math
from modules.thermal.ventilation.ventilation_recovery.constants import (
    STANDARD_DUCT_DIAMETERS, 
    STANDARD_RECTANGULAR_DIMENSIONS,
    AIR_VELOCITY_RANGES
)

def convert_m3h_to_m3s(flow_m3h):
    """Pretvara protok iz m³/h u m³/s."""
    return flow_m3h / 3600

def convert_m3s_to_m3h(flow_m3s):
    """Pretvara protok iz m³/s u m³/h."""
    return flow_m3s * 3600

def convert_mm_to_m(length_mm):
    """Pretvara duljinu iz mm u m."""
    return length_mm / 1000

def convert_m_to_mm(length_m):
    """Pretvara duljinu iz m u mm."""
    return length_m * 1000

def calculate_duct_area_round(diameter_mm):
    """
    Izračunava površinu presjeka kružnog kanala.
    
    Args:
        diameter_mm (float): Promjer kanala u mm
        
    Returns:
        float: Površina presjeka u m²
    """
    diameter_m = convert_mm_to_m(diameter_mm)
    return math.pi * (diameter_m / 2) ** 2

def calculate_duct_area_rectangular(width_mm, height_mm):
    """
    Izračunava površinu presjeka pravokutnog kanala.
    
    Args:
        width_mm (float): Širina kanala u mm
        height_mm (float): Visina kanala u mm
        
    Returns:
        float: Površina presjeka u m²
    """
    width_m = convert_mm_to_m(width_mm)
    height_m = convert_mm_to_m(height_mm)
    return width_m * height_m

def calculate_equivalent_diameter(width_mm, height_mm):
    """
    Izračunava ekvivalentni promjer pravokutnog kanala.
    
    Args:
        width_mm (float): Širina kanala u mm
        height_mm (float): Visina kanala u mm
        
    Returns:
        float: Ekvivalentni promjer u mm
    """
    a = width_mm
    b = height_mm
    return 1.3 * ((a * b) ** 0.625) / ((a + b) ** 0.25)

def get_velocity_indicators(velocity, duct_type="main_duct"):
    """
    Vraća indikatore prihvatljivosti brzine.
    
    Args:
        velocity (float): Brzina zraka u m/s
        duct_type (str): Tip kanala ("main_duct", "branch", "terminal")
        
    Returns:
        tuple: (boja, poruka)
    """
    ranges = AIR_VELOCITY_RANGES[duct_type]
    
    if velocity < ranges["min"]:
        return "blue", f"⚠️ Preniska brzina (min. {ranges['min']} m/s)"
    elif velocity <= ranges["optimal"]:
        return "green", f"✅ Optimalna brzina"
    elif velocity <= ranges["max"]:
        return "orange", f"⚠️ Prihvatljiva brzina"
    else:
        return "red", f"❌ Previsoka brzina (max. {ranges['max']} m/s)"

def find_nearest_standard_diameter(diameter_mm):
    """
    Pronalazi najbližu standardnu dimenziju za kružni kanal.
    
    Args:
        diameter_mm (float): Izračunati promjer u mm
        
    Returns:
        int: Najbliži standardni promjer u mm
    """
    return min(STANDARD_DUCT_DIAMETERS, key=lambda x: abs(x - diameter_mm))

def find_standard_rectangular_dimensions(area_mm2, aspect_ratio=1.5):
    """
    Pronalazi standardne dimenzije za pravokutni kanal.
    
    Args:
        area_mm2 (float): Potrebna površina u mm²
        aspect_ratio (float): Željeni omjer širina:visina
        
    Returns:
        tuple: (širina, visina) u mm kao standardne dimenzije
    """
    height = math.sqrt(area_mm2 / aspect_ratio)
    width = area_mm2 / height
    
    standard_height = min(STANDARD_RECTANGULAR_DIMENSIONS, key=lambda x: abs(x - height))
    standard_width = min(STANDARD_RECTANGULAR_DIMENSIONS, key=lambda x: abs(x - width))
    
    return (standard_width, standard_height)

def calculate_dynamic_pressure(velocity):
    """
    Izračunava dinamički tlak na temelju brzine.
    
    Args:
        velocity (float): Brzina zraka u m/s
        
    Returns:
        float: Dinamički tlak u Pa
    """
    # Dinamički tlak = ρ * v² / 2, gdje je ρ gustoća zraka (1.2 kg/m³)
    return 0.6 * velocity ** 2  # Pojednostavljeno: 1.2 / 2 = 0.6

def calculate_reynolds_number(velocity, hydraulic_diameter):
    """
    Izračunava Reynoldsov broj za strujanje u kanalu.
    
    Args:
        velocity (float): Brzina zraka u m/s
        hydraulic_diameter (float): Hidraulički promjer u m
        
    Returns:
        float: Reynoldsov broj
    """
    # Re = ρ * v * Dh / μ, gdje je:
    # ρ = gustoća zraka (1.2 kg/m³)
    # μ = dinamička viskoznost zraka (1.8 * 10⁻⁵ Pa·s)
    return 66667 * velocity * hydraulic_diameter  # Pojednostavljeno: 1.2 / (1.8 * 10⁻⁵) = 66667