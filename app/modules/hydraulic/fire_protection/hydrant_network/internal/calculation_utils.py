"""
Pomoćne funkcije za izračune u kalkulatoru unutarnje hidrantske mreže.
"""
import math
from ..common.constants import (
    WATER_DENSITY, WATER_VISCOSITY, GRAVITY, M_WATER_TO_BAR,
    LOCAL_RESISTANCE_COEFFICIENTS
)
from ..common.pipe_data import PIPE_DATA

def calculate_pipe_diameter(flow_l_s, velocity_m_s):
    """Izračunava potreban promjer cijevi u mm za zadani protok i brzinu."""
    # Pretvori protok iz l/s u m³/s
    flow_m3_s = flow_l_s / 1000
    
    # Formula: D = sqrt(4 * Q / (π * v))
    required_diameter_m = math.sqrt((4 * flow_m3_s) / (math.pi * velocity_m_s))
    
    # Pretvori iz m u mm
    return required_diameter_m * 1000

def calculate_velocity(flow_l_s, pipe_dn):
    """Izračunava brzinu vode u cijevi za zadani protok i promjer."""
    # Pretvori protok iz l/s u m³/s
    flow_m3_s = flow_l_s / 1000
    
    # Izračunaj površinu presjeka cijevi
    section_area = PIPE_DATA.calculate_section_area(pipe_dn)
    
    # Formula: v = Q / A
    velocity = flow_m3_s / section_area
    
    return velocity

def check_velocity_optimality(velocity):
    """Provjerava je li brzina u optimalnom rasponu."""
    if 1.0 <= velocity <= 2.5:
        return "optimalno"
    elif 0.5 <= velocity < 1.0 or 2.5 < velocity <= 3.0:
        return "prihvatljivo"
    else:
        return "neprihvatljivo"

def calculate_friction_factor(inner_diameter_m, roughness_m, reynolds):
    """Izračunava faktor trenja koristeći Swamee-Jain aproksimaciju za Colebrook-White formulu."""
    return 0.25 / (math.log10(roughness_m / (3.7 * inner_diameter_m) + 5.74 / reynolds**0.9))**2

def calculate_linear_losses(length, diameter_dn, velocity, material="Pocinčani čelik"):
    """Izračunava linijske gubitke tlaka u cijevima."""
    # Dohvati unutarnji promjer cijevi u m
    inner_diameter_m = PIPE_DATA.get_inner_diameter_m(diameter_dn)
    
    # Dohvati koeficijent hrapavosti materijala
    roughness = PIPE_DATA.roughness.get(material, 0.15) / 1000  # mm -> m
    
    # Izračunaj Reynolds broj
    reynolds = (WATER_DENSITY * velocity * inner_diameter_m) / WATER_VISCOSITY
    
    # Izračunaj faktor trenja
    friction_factor = calculate_friction_factor(inner_diameter_m, roughness, reynolds)
    
    # Izračunaj gubitak tlaka po Darcy-Weisbach formuli
    loss_m = friction_factor * (length / inner_diameter_m) * (velocity**2 / (2 * GRAVITY))
    
    # Pretvori gubitak iz m vodenog stupca u bar
    loss_bar = loss_m * M_WATER_TO_BAR
    
    return loss_bar

def calculate_local_losses(local_elements, velocity):
    """Izračunava lokalne gubitke tlaka na fitinzima i ventilima."""
    # Izračunaj ukupni koeficijent lokalnog otpora
    total_coefficient = 0
    for element, count in local_elements.items():
        coefficient = LOCAL_RESISTANCE_COEFFICIENTS.get(element, 0)
        total_coefficient += coefficient * count
    
    # Izračunaj gubitak tlaka
    loss_m = total_coefficient * (velocity**2 / (2 * GRAVITY))
    
    # Pretvori iz m vodenog stupca u bar
    loss_bar = loss_m * M_WATER_TO_BAR
    
    return loss_bar

def calculate_geodetic_loss(height_difference):
    """Izračunava geodetski gubitak tlaka zbog visinske razlike."""
    # Pretvori m u bar
    return height_difference * M_WATER_TO_BAR

def calculate_pressure_losses(parameters):
    """Izračunava ukupne gubitke tlaka kroz cijelu hidrantsku mrežu."""
    # Dohvat parametara
    pipe_lengths = parameters["pipe_lengths"]
    pipe_diameters = parameters["pipe_diameters"]
    local_elements = parameters["local_elements"]
    height_difference = parameters["total_height"]
    flow_l_s = parameters["total_flow_l_s"]
    
    # Izračun brzina u pojedinim dionicama
    velocities = {}
    for section, diameter in pipe_diameters.items():
        velocities[section] = calculate_velocity(flow_l_s, diameter)
    
    # Izračun linijskih gubitaka
    linear_losses = {}
    total_linear_loss = 0
    
    # Horizontalni vod i etažni vod
    for section, length in pipe_lengths.items():
        loss = calculate_linear_losses(length, pipe_diameters[section], velocities[section])
        linear_losses[section] = loss
        total_linear_loss += loss
    
    # Usponski vod - izračunaj gubitke za usponski vod
    # Uzimamo visinu usponskog voda iz total_height
    riser_loss = calculate_linear_losses(height_difference, pipe_diameters["riser"], velocities["riser"])
    linear_losses["riser"] = riser_loss
    total_linear_loss += riser_loss
    
    # Izračun lokalnih gubitaka
    local_losses = {}
    total_local_loss = 0
    for section, elements in local_elements.items():
        loss = calculate_local_losses(elements, velocities[section])
        local_losses[section] = loss
        total_local_loss += loss
    
    # Izračun geodetskog gubitka
    geodetic_loss = calculate_geodetic_loss(height_difference)
    
    # Ukupni gubitak tlaka
    total_loss = total_linear_loss + total_local_loss + geodetic_loss
    
    return {
        "velocities": velocities,
        "linear_losses": linear_losses,
        "local_losses": local_losses,
        "total_linear_loss": total_linear_loss,
        "total_local_loss": total_local_loss,
        "geodetic_loss": geodetic_loss,
        "total_loss": total_loss
    }

def calculate_hydrant_height(ground_to_first, standard_height, different_heights, floor_heights, target_floor, hydrant_height):
    """Izračunava ukupnu visinu hidranta od tla.
    
    Parametri:
    ground_to_first - Visina od tla do poda prve etaže
    standard_height - Standardna visina etaže
    different_heights - Koriste li se različite visine etaža
    floor_heights - Rječnik s visinama pojedinih etaža
    target_floor - Etaža na kojoj se nalazi hidrant (1, 2, 3...)
    hydrant_height - Visina hidranta od poda
    
    Logika izračuna:
    1. Započnemo s visinom od tla do poda prve etaže
    2. Za svaku etažu od 1 do target_floor - 1, dodajemo visinu etaže
       (koristimo definirane visine ako postoje, inače standardnu)
    3. Dodajemo visinu etaže na kojoj se nalazi hidrant
    4. Dodajemo visinu hidranta od poda
    """
    # Započnemo s visinom od tla do poda prve etaže
    total_height = ground_to_first
    
    # Ako je hidrant na prvoj etaži, nema dodatnih etaža za zbrajanje
    if target_floor == 1:
        # Samo dodaj visinu hidranta od poda
        total_height += hydrant_height
        return total_height
    
    # Za hidrant na višim etažama (2 i više)
    if different_heights and floor_heights:
        # Zbroji visine svih etaža do ciljne etaže (uključivo)
        for i in range(1, target_floor):
            # Visine etaža od prve do predzadnje
            floor_height = floor_heights.get(i, standard_height)
            total_height += floor_height
            
        # Dodaj visinu ciljne etaže do poda hidranta
        floor_height = floor_heights.get(target_floor, standard_height)
        total_height += hydrant_height
    else:
        # Standardne visine za sve etaže iznad prve
        # Dodajemo (target_floor - 1) etaža standardne visine
        total_height += standard_height * (target_floor - 1)
        # Dodajemo visinu hidranta od poda
        total_height += hydrant_height
    
    return total_height