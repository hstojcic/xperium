# modules/thermal/ventilation/ventilation_recovery/local_elements.py

from modules.thermal.ventilation.ventilation_recovery.constants import LOCAL_RESISTANCE_COEFFICIENTS
from modules.thermal.ventilation.ventilation_recovery.utils import calculate_dynamic_pressure

def get_local_element_resistance(element_type):
    """
    Dohvaća koeficijent otpora za odabrani lokalni element.
    
    Args:
        element_type (str): Tip lokalnog elementa (npr. "bend_90deg")
        
    Returns:
        dict: Informacije o koeficijentu otpora
    """
    if element_type not in LOCAL_RESISTANCE_COEFFICIENTS:
        raise ValueError(f"Nepoznati tip lokalnog elementa: {element_type}")
    
    return LOCAL_RESISTANCE_COEFFICIENTS[element_type]

def get_all_local_elements():
    """
    Vraća listu svih dostupnih lokalnih elemenata.
    
    Returns:
        list: Lista rječnika s informacijama o lokalnim elementima
    """
    elements = []
    for key, data in LOCAL_RESISTANCE_COEFFICIENTS.items():
        elements.append({
            "id": key,
            "name": data["name"],
            "k_factor": data["standard"]
        })
    return elements

def calculate_local_pressure_drop(velocity, k_factor, count=1):
    """
    Izračunava pad tlaka na lokalnom elementu.
    
    Args:
        velocity (float): Brzina zraka u m/s
        k_factor (float): Koeficijent lokalnog otpora
        count (int): Broj istih elemenata
        
    Returns:
        float: Pad tlaka u Pa
    """
    # Izračun dinamičkog tlaka
    dynamic_pressure = calculate_dynamic_pressure(velocity)
    
    # Pad tlaka = koeficijent otpora × dinamički tlak × broj elemenata
    return k_factor * dynamic_pressure * count

def sum_local_pressure_drops(velocity, elements):
    """
    Zbraja padove tlaka na svim lokalnim elementima.
    
    Args:
        velocity (float): Brzina zraka u m/s
        elements (list): Lista lokalnih elemenata s koeficijentima i brojem
        
    Returns:
        float: Ukupni pad tlaka na lokalnim elementima u Pa
    """
    total_drop = 0
    for element in elements:
        k_factor = element.get("k_factor", 0)
        count = element.get("count", 1)
        drop = calculate_local_pressure_drop(velocity, k_factor, count)
        total_drop += drop
    
    return total_drop