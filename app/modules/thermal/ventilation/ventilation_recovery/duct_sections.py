# modules/thermal/ventilation/ventilation_recovery/duct_sections.py

import uuid
from modules.thermal.ventilation.ventilation_recovery.utils import get_velocity_indicators
from modules.thermal.ventilation.ventilation_recovery.duct_sizing import (
    calculate_velocity_round,
    calculate_velocity_rectangular,
    get_recommended_round_duct,
    get_recommended_rectangular_duct
)
from modules.thermal.ventilation.ventilation_recovery.pressure_drop import calculate_total_pressure_drop

def create_new_section(section_type="main", duct_type="round", name="Nova dionica"):
    """
    Stvara novu dionicu ventilacijskog kanala.
    
    Args:
        section_type (str): Tip dionice ("main", "branch", "terminal")
        duct_type (str): Tip kanala ("round", "rectangular")
        name (str): Naziv dionice
        
    Returns:
        dict: Nova dionica s zadanim vrijednostima
    """
    section_id = str(uuid.uuid4())
    
    section = {
        "id": section_id,
        "name": name,
        "section_type": section_type,
        "duct_type": duct_type,
        "flow_rate": 100.0,  # m³/h
        "length": 5.0,  # m
        "dimensions": {
            "diameter": 200 if duct_type == "round" else None,  # mm
            "width": 300 if duct_type == "rectangular" else None,  # mm
            "height": 200 if duct_type == "rectangular" else None  # mm
        },
        "velocity": 0.0,  # m/s (izračunat će se)
        "local_elements": [],
        "pressure_drop": {
            "linear": 0.0,
            "local": 0.0,
            "total": 0.0
        }
    }
    
    # Izračun početne brzine
    update_section_velocity(section)
    
    return section

def update_section_velocity(section):
    """
    Ažurira brzinu zraka u dionici nakon promjene dimenzija ili protoka.
    
    Args:
        section (dict): Podaci o dionici
        
    Returns:
        dict: Ažurirana dionica
    """
    duct_type = section["duct_type"]
    flow_rate = section["flow_rate"]
    
    if duct_type == "round":
        diameter = section["dimensions"]["diameter"]
        if diameter and diameter > 0:
            velocity = calculate_velocity_round(flow_rate, diameter)
            section["velocity"] = round(velocity, 2)
    else:  # rectangular
        width = section["dimensions"]["width"]
        height = section["dimensions"]["height"]
        if width and height and width > 0 and height > 0:
            velocity = calculate_velocity_rectangular(flow_rate, width, height)
            section["velocity"] = round(velocity, 2)
    
    return section

def apply_recommended_dimensions(section, desired_velocity):
    """
    Primjenjuje preporučene dimenzije kanala prema željenom protoku i brzini.
    
    Args:
        section (dict): Podaci o dionici
        desired_velocity (float): Željena brzina zraka u m/s
        
    Returns:
        dict: Ažurirana dionica
    """
    duct_type = section["duct_type"]
    flow_rate = section["flow_rate"]
    
    if duct_type == "round":
        recommended = get_recommended_round_duct(flow_rate, desired_velocity)
        section["dimensions"]["diameter"] = recommended["diameter"]
        section["velocity"] = round(recommended["velocity"], 2)
    else:  # rectangular
        # Zadržavamo postojeći omjer stranica ako je moguće
        if section["dimensions"]["width"] and section["dimensions"]["height"]:
            current_ratio = section["dimensions"]["width"] / section["dimensions"]["height"] \
                          if section["dimensions"]["height"] > 0 else 1.5
        else:
            current_ratio = 1.5
        
        recommended = get_recommended_rectangular_duct(flow_rate, desired_velocity, current_ratio)
        section["dimensions"]["width"] = recommended["width"]
        section["dimensions"]["height"] = recommended["height"]
        section["velocity"] = round(recommended["velocity"], 2)
    
    return section

def get_section_status(section):
    """
    Vraća status dionice na temelju brzine zraka.
    
    Args:
        section (dict): Podaci o dionici
        
    Returns:
        dict: Status dionice
    """
    velocity = section["velocity"]
    section_type = section["section_type"]
    
    # Pretvorba iz section_type u duct_type za funkciju get_velocity_indicators
    duct_type_map = {
        "main": "main_duct",
        "branch": "branch",
        "terminal": "terminal"
    }
    duct_type = duct_type_map.get(section_type, "main_duct")
    
    color, message = get_velocity_indicators(velocity, duct_type)
    
    return {
        "color": color,
        "message": message,
        "is_optimal": color == "green"
    }

def update_section_pressure_drop(section):
    """
    Ažurira pad tlaka za dionicu.
    
    Args:
        section (dict): Podaci o dionici
        
    Returns:
        dict: Ažurirana dionica s izračunatim padom tlaka
    """
    pressure_drop = calculate_total_pressure_drop(section)
    section["pressure_drop"] = pressure_drop
    
    return section

def get_initial_section_from_recuperator(recuperator_data, system_type):
    """
    Stvara početnu dionicu na temelju priključka rekuperatora.
    
    Args:
        recuperator_data (dict): Podaci o odabranom rekuperatoru
        system_type (str): Tip sustava ("fresh_air", "supply", "extract", "exhaust")
        
    Returns:
        dict: Nova dionica prilagođena rekuperatoru
    """
    if not recuperator_data:
        return create_new_section()
    
    # Nazivi dionica prema tipu sustava
    section_names = {
        "fresh_air": "Svježi zrak (ulaz u rekuperator)",
        "supply": "Tlačni kanal (iz rekuperatora)",
        "extract": "Odsisni kanal (prema rekuperatoru)",
        "exhaust": "Istrošeni zrak (izlaz iz rekuperatora)"
    }
    
    name = section_names.get(system_type, "Nova dionica")
    
    # Stvaranje nove dionice
    section = create_new_section(section_type="main", duct_type="round", name=name)
    
    # Postavljanje protoka prema rekuperatoru
    if "flow_capacity" in recuperator_data:
        section["flow_rate"] = recuperator_data["flow_capacity"]
    
    # Postavljanje dimenzija prema priključku rekuperatora
    if "diameter" in recuperator_data:
        section["dimensions"]["diameter"] = recuperator_data["diameter"]
    
    # Ažuriranje brzine i pada tlaka
    update_section_velocity(section)
    update_section_pressure_drop(section)
    
    return section