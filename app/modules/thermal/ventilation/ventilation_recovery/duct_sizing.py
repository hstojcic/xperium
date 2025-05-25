# modules/thermal/ventilation/ventilation_recovery/duct_sizing.py

import math
from modules.thermal.ventilation.ventilation_recovery.utils import (
    convert_m3h_to_m3s,
    find_nearest_standard_diameter,
    find_standard_rectangular_dimensions,
    calculate_equivalent_diameter,
    convert_mm_to_m
)

def calculate_round_duct_diameter(flow_rate, velocity):
    """
    Izračunava potreban promjer kružnog kanala.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        velocity (float): Željena brzina zraka u m/s
        
    Returns:
        float: Potreban promjer kanala u mm
    """
    # Konverzija protoka iz m³/h u m³/s
    flow_m3s = convert_m3h_to_m3s(flow_rate)
    
    # Izračun potrebne površine presjeka
    area = flow_m3s / velocity if velocity > 0 else 0
    
    # Izračun promjera
    diameter = math.sqrt((4 * area) / math.pi)
    
    # Konverzija u mm
    diameter_mm = diameter * 1000
    
    return diameter_mm

def calculate_rectangular_duct_dimensions(flow_rate, velocity, aspect_ratio=1.5):
    """
    Izračunava potrebne dimenzije pravokutnog kanala.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        velocity (float): Željena brzina zraka u m/s
        aspect_ratio (float): Omjer širine i visine
        
    Returns:
        tuple: (širina, visina) kanala u mm
    """
    # Konverzija protoka iz m³/h u m³/s
    flow_m3s = convert_m3h_to_m3s(flow_rate)
    
    # Izračun potrebne površine presjeka
    area = flow_m3s / velocity if velocity > 0 else 0
    
    # Izračun dimenzija za zadani omjer
    area_mm2 = area * 1000000  # Pretvorba u mm²
    
    # Izračun dimenzija
    height = math.sqrt(area_mm2 / aspect_ratio)
    width = area_mm2 / height if height > 0 else 0
    
    return (width, height)

def calculate_velocity_round(flow_rate, diameter):
    """
    Izračunava brzinu zraka u kružnom kanalu.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        diameter (float): Promjer kanala u mm
        
    Returns:
        float: Brzina zraka u m/s
    """
    if diameter <= 0:
        return 0
    
    # Konverzija promjera iz mm u m
    diameter_m = convert_mm_to_m(diameter)
    
    # Konverzija protoka iz m³/h u m³/s
    flow_m3s = convert_m3h_to_m3s(flow_rate)
    
    # Površina presjeka
    area = math.pi * (diameter_m / 2) ** 2
    
    # Brzina
    velocity = flow_m3s / area if area > 0 else 0
    
    return velocity

def calculate_velocity_rectangular(flow_rate, width, height):
    """
    Izračunava brzinu zraka u pravokutnom kanalu.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        width (float): Širina kanala u mm
        height (float): Visina kanala u mm
        
    Returns:
        float: Brzina zraka u m/s
    """
    if width <= 0 or height <= 0:
        return 0
    
    # Konverzija dimenzija iz mm u m
    width_m = convert_mm_to_m(width)
    height_m = convert_mm_to_m(height)
    
    # Konverzija protoka iz m³/h u m³/s
    flow_m3s = convert_m3h_to_m3s(flow_rate)
    
    # Površina presjeka
    area = width_m * height_m
    
    # Brzina
    velocity = flow_m3s / area if area > 0 else 0
    
    return velocity

def get_recommended_round_duct(flow_rate, desired_velocity):
    """
    Vraća preporučeni standardni promjer kružnog kanala.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        desired_velocity (float): Željena brzina zraka u m/s
        
    Returns:
        dict: Preporučene vrijednosti promjera i stvarne brzine
    """
    # Izračun teoretskog promjera
    diameter_mm = calculate_round_duct_diameter(flow_rate, desired_velocity)
    
    # Pronalazak najbližeg standardnog promjera
    standard_diameter = find_nearest_standard_diameter(diameter_mm)
    
    # Izračun stvarne brzine sa standardnim promjerom
    actual_velocity = calculate_velocity_round(flow_rate, standard_diameter)
    
    return {
        "diameter": standard_diameter,
        "velocity": actual_velocity
    }

def get_recommended_rectangular_duct(flow_rate, desired_velocity, aspect_ratio=1.5):
    """
    Vraća preporučene standardne dimenzije pravokutnog kanala.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        desired_velocity (float): Željena brzina zraka u m/s
        aspect_ratio (float): Omjer širine i visine
        
    Returns:
        dict: Preporučene vrijednosti dimenzija i stvarne brzine
    """
    # Izračun teoretskih dimenzija
    width, height = calculate_rectangular_duct_dimensions(flow_rate, desired_velocity, aspect_ratio)
    
    # Pronalazak najbližih standardnih dimenzija
    standard_width, standard_height = find_standard_rectangular_dimensions(width * height, aspect_ratio)
    
    # Izračun stvarne brzine sa standardnim dimenzijama
    actual_velocity = calculate_velocity_rectangular(flow_rate, standard_width, standard_height)
    
    return {
        "width": standard_width,
        "height": standard_height,
        "velocity": actual_velocity
    }