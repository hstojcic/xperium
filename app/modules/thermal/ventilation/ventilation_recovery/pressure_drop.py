# modules/thermal/ventilation/ventilation_recovery/pressure_drop.py

import math
from modules.thermal.ventilation.ventilation_recovery.utils import (
    convert_mm_to_m,
    calculate_equivalent_diameter,
    calculate_reynolds_number,
    calculate_dynamic_pressure
)
from modules.thermal.ventilation.ventilation_recovery.local_elements import sum_local_pressure_drops

def calculate_friction_factor(reynolds, roughness=0.15, hydraulic_diameter=0.2):
    """
    Izračunava faktor trenja za strujanje u kanalu.
    
    Args:
        reynolds (float): Reynoldsov broj
        roughness (float): Relativna hrapavost površine (mm)
        hydraulic_diameter (float): Hidraulički promjer kanala (m)
        
    Returns:
        float: Faktor trenja
    """
    # Pretvorba relativne hrapavosti iz mm u m
    roughness_m = roughness / 1000
    
    # Relativna hrapavost
    relative_roughness = roughness_m / hydraulic_diameter
    
    # Colebrook-White formula za turbulentan tok (pojednostavljena)
    if reynolds > 4000:
        # Za standardne ventilacijske kanale možemo koristiti pojednostavljeni pristup
        if relative_roughness < 0.001:
            # Glatke cijevi
            return 0.0196 * (reynolds ** -0.2)
        else:
            # Hrapave cijevi
            return max(0.018, 0.11 * (relative_roughness ** 0.25))
    else:
        # Laminarni tok
        return 64 / reynolds if reynolds > 0 else 0

def calculate_linear_pressure_drop(length, hydraulic_diameter, velocity, roughness=0.15):
    """
    Izračunava linijski pad tlaka u dionici.
    
    Args:
        length (float): Duljina dionice u m
        hydraulic_diameter (float): Hidraulički promjer u m
        velocity (float): Brzina zraka u m/s
        roughness (float): Hrapavost površine u mm
        
    Returns:
        float: Linijski pad tlaka u Pa
    """
    # Reynoldsov broj
    reynolds = calculate_reynolds_number(velocity, hydraulic_diameter)
    
    # Faktor trenja
    friction_factor = calculate_friction_factor(reynolds, roughness, hydraulic_diameter)
    
    # Izračun pada tlaka po formuli Darcy-Weisbacha
    # Δp = λ × (L / D) × (ρ × v² / 2)
    dynamic_pressure = calculate_dynamic_pressure(velocity)
    
    return friction_factor * (length / hydraulic_diameter) * dynamic_pressure

def calculate_linear_pressure_drop_round(length, diameter, velocity, roughness=0.15):
    """
    Izračunava linijski pad tlaka u kružnoj dionici.
    
    Args:
        length (float): Duljina dionice u m
        diameter (float): Promjer kanala u mm
        velocity (float): Brzina zraka u m/s
        roughness (float): Hrapavost površine u mm
        
    Returns:
        float: Linijski pad tlaka u Pa
    """
    # Pretvorba promjera iz mm u m
    diameter_m = convert_mm_to_m(diameter)
    
    return calculate_linear_pressure_drop(length, diameter_m, velocity, roughness)

def calculate_linear_pressure_drop_rectangular(length, width, height, velocity, roughness=0.15):
    """
    Izračunava linijski pad tlaka u pravokutnoj dionici.
    
    Args:
        length (float): Duljina dionice u m
        width (float): Širina kanala u mm
        height (float): Visina kanala u mm
        velocity (float): Brzina zraka u m/s
        roughness (float): Hrapavost površine u mm
        
    Returns:
        float: Linijski pad tlaka u Pa
    """
    # Izračun ekvivalentnog promjera
    eq_diameter = calculate_equivalent_diameter(width, height)
    
    # Pretvorba iz mm u m
    eq_diameter_m = convert_mm_to_m(eq_diameter)
    
    return calculate_linear_pressure_drop(length, eq_diameter_m, velocity, roughness)

def calculate_total_pressure_drop(section):
    """
    Izračunava ukupni pad tlaka za zadanu dionicu.
    
    Args:
        section (dict): Podaci o dionici
        
    Returns:
        float: Ukupni pad tlaka u Pa
    """
    # Osiguranje da svi potrebni ključevi postoje
    if "length" not in section:
        section["length"] = 0.0
    if "velocity" not in section:
        section["velocity"] = 0.0
    if "duct_type" not in section:
        section["duct_type"] = "round"
    if "dimensions" not in section:
        section["dimensions"] = {}
    
    # Dohvaćanje podataka o dionici
    length = section["length"]
    velocity = section["velocity"]
    duct_type = section["duct_type"]
    
    # Izračun linijskog pada tlaka
    if duct_type == "round":
        diameter = section["dimensions"].get("diameter", 0)
        if diameter <= 0:
            linear_drop = 0
        else:
            linear_drop = calculate_linear_pressure_drop_round(length, diameter, velocity)
    else:  # rectangular
        width = section["dimensions"].get("width", 0)
        height = section["dimensions"].get("height", 0)
        if width <= 0 or height <= 0:
            linear_drop = 0
        else:
            linear_drop = calculate_linear_pressure_drop_rectangular(length, width, height, velocity)
    
    # Izračun lokalnog pada tlaka
    local_elements = section.get("local_elements", [])
    local_resistances = section.get("local_resistances", {})
    
    # Konverzija local_resistances u format koji očekuje sum_local_pressure_drops
    if local_resistances:
        local_elements = []
        for element_type, count in local_resistances.items():
            if count > 0:
                from modules.thermal.ventilation.ventilation_recovery.constants import LOCAL_RESISTANCE_COEFFICIENTS
                k_factor = LOCAL_RESISTANCE_COEFFICIENTS.get(element_type, {}).get("standard", 0)
                local_elements.append({"k_factor": k_factor, "count": count})
    
    local_drop = sum_local_pressure_drops(velocity, local_elements)
    
    # Ukupni pad tlaka
    total_drop = linear_drop + local_drop
    
    # Ovdje je ključna promjena - imenovanje ključeva
    return {
        "friction": linear_drop,  # Promijenjeno iz "linear" u "friction"
        "local": local_drop,
        "total": total_drop
    }

def calculate_system_pressure_drop(sections):
    """
    Izračunava ukupni pad tlaka za cijeli sustav.
    
    Args:
        sections (list): Lista dionica ventilacijskog sustava
        
    Returns:
        float: Ukupni pad tlaka sustava u Pa
    """
    total_drop = 0
    critical_path = []
    
    # Grupiranje dionica po putanjama
    # U stvarnoj implementaciji ovo bi trebalo biti složenije
    # za sada pretpostavljamo da su dionice već pravilno grupirane
    for section in sections:
        section_drop = calculate_total_pressure_drop(section)
        total_drop += section_drop["total"]
    
    return total_drop