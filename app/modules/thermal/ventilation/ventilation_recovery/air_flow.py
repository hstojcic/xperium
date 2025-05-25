# modules/thermal/ventilation/ventilation_recovery/air_flow.py

from modules.thermal.ventilation.ventilation_recovery.constants import (
    AIR_QUALITY_CATEGORIES,
    AREA_USAGE_INTENSITY,
    AIR_CHANGE_RATES,
    DELTA_T_RANGES,
    AIR_DENSITY,
    AIR_SPECIFIC_HEAT
)

def calculate_by_occupants(n_people, air_quality_category="II"):
    """
    Izračunava potreban protok zraka prema broju osoba.
    
    Args:
        n_people (int): Broj osoba
        air_quality_category (str): Kategorija kvalitete zraka ("I", "II", "III")
        
    Returns:
        float: Potreban protok zraka u m³/h
    """
    if air_quality_category not in AIR_QUALITY_CATEGORIES:
        raise ValueError(f"Nepoznata kategorija kvalitete zraka: {air_quality_category}")
    
    specific_flow = AIR_QUALITY_CATEGORIES[air_quality_category]["flow_rate"]  # m³/h po osobi
    return n_people * specific_flow

def calculate_by_area(area, usage_intensity="medium"):
    """
    Izračunava potreban protok zraka prema površini.
    
    Args:
        area (float): Površina prostora u m²
        usage_intensity (str): Intenzitet korištenja ("low", "medium", "high")
        
    Returns:
        float: Potreban protok zraka u m³/h
    """
    if usage_intensity not in AREA_USAGE_INTENSITY:
        raise ValueError(f"Nepoznati intenzitet korištenja: {usage_intensity}")
    
    specific_flow = AREA_USAGE_INTENSITY[usage_intensity]["flow_rate"]  # m³/(h·m²)
    return area * specific_flow

def calculate_by_air_changes(volume, ach_rate="medium"):
    """
    Izračunava potreban protok zraka prema broju izmjena zraka.
    
    Args:
        volume (float): Volumen prostora u m³
        ach_rate (str): Intenzitet izmjena ("low", "medium", "high")
        
    Returns:
        float: Potreban protok zraka u m³/h
    """
    if ach_rate not in AIR_CHANGE_RATES:
        raise ValueError(f"Nepoznati intenzitet izmjena: {ach_rate}")
    
    rate = AIR_CHANGE_RATES[ach_rate]["rate"]  # broj izmjena po satu
    return volume * rate

def calculate_by_thermal_load(thermal_load, delta_t="medium"):
    """
    Izračunava potreban protok zraka prema toplinskom opterećenju.
    
    Args:
        thermal_load (float): Toplinsko opterećenje u W
        delta_t (str): Raspon temperaturne razlike ("small", "medium", "large")
        
    Returns:
        float: Potreban protok zraka u m³/h
    """
    if delta_t not in DELTA_T_RANGES:
        raise ValueError(f"Nepoznati temperaturni raspon: {delta_t}")
    
    dt_value = DELTA_T_RANGES[delta_t]["value"]  # K
    
    # Protok u m³/s
    flow_m3s = thermal_load / (AIR_DENSITY * AIR_SPECIFIC_HEAT * dt_value)
    
    # Pretvorba u m³/h
    return flow_m3s * 3600

def get_final_flow_rate(methods, values):
    """
    Određuje konačni protok zraka iz svih metoda.
    
    Args:
        methods (dict): Rječnik s Boolean vrijednostima za svaku metodu
        values (dict): Rječnik s vrijednostima protoka za svaku metodu
        
    Returns:
        float: Konačni protok zraka u m³/h
    """
    max_flow = 0
    
    if methods.get("by_occupants", False) and "by_occupants" in values:
        max_flow = max(max_flow, values["by_occupants"])
    
    if methods.get("by_area", False) and "by_area" in values:
        max_flow = max(max_flow, values["by_area"])
    
    if methods.get("by_air_changes", False) and "by_air_changes" in values:
        max_flow = max(max_flow, values["by_air_changes"])
    
    if methods.get("by_thermal_load", False) and "by_thermal_load" in values:
        max_flow = max(max_flow, values["by_thermal_load"])
    
    return max_flow

def calculate_room_flow_rates(rooms):
    """
    Izračunava protok zraka za svaku prostoriju prema zadanoj površini i stopama protoka.
    
    Args:
        rooms (list): Lista prostorija s podacima o površini i stopama protoka
        
    Returns:
        list: Lista prostorija s izračunatim protocima
    """
    for room in rooms:
        # Izračun protoka dobavnog zraka
        room["supply_flow"] = room["area"] * room["supply_rate"]
        
        # Izračun protoka odsisnog zraka
        room["extract_flow"] = room["area"] * room["extract_rate"]
    
    return rooms

def calculate_total_flow_rate(rooms):
    """
    Izračunava ukupni protok zraka na temelju prostorija.
    
    Args:
        rooms (list): Lista prostorija s izračunatim protocima
        
    Returns:
        float: Ukupni protok zraka u m³/h
    """
    total_supply = sum(room["supply_flow"] for room in rooms)
    total_extract = sum(room["extract_flow"] for room in rooms)
    
    # Uzimamo maksimalnu vrijednost između dobave i odsisa za balansiran sustav
    return max(total_supply, total_extract)