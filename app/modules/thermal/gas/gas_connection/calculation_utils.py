"""
Pomoćne funkcije za proračun plinskog priključka.
"""
import math
from .constants import *

def calculate_flow_rate(power, efficiency, simultaneity_factor):
    """
    Izračunava protok plina.
    
    Args:
        power: Snaga uređaja (kW)
        efficiency: Iskoristivost uređaja (0-1)
        simultaneity_factor: Faktor istovremenosti
        
    Returns:
        float: Protok plina (m³/h)
    """
    return (power * simultaneity_factor) / (HD * efficiency)

def calculate_required_diameter(flow_rate, velocity=STANDARD_BRZINA):
    """
    Izračunava potreban promjer cijevi.
    
    Args:
        flow_rate: Protok plina (m³/h)
        velocity: Brzina plina (m/s), default 6.0
        
    Returns:
        float: Potreban promjer (mm)
    """
    # Pretvorba protoka iz m³/h u m³/s
    Q = flow_rate / 3600
    # Izračun promjera u milimetrima
    return math.sqrt((4 * Q)/(math.pi * velocity)) * 1000

def calculate_actual_velocity(flow_rate, diameter_mm):
    """
    Izračunava stvarnu brzinu u cijevi.
    
    Args:
        flow_rate: Protok plina (m³/h)
        diameter_mm: Unutarnji promjer cijevi (mm)
        
    Returns:
        float: Stvarna brzina (m/s)
    """
    # Pretvorba protoka u m³/s i promjera u m
    Q = flow_rate / 3600
    d = diameter_mm / 1000
    
    # Izračun brzine
    return (4 * Q) / (math.pi * pow(d, 2))

def calculate_pressure_drop_low_pressure(flow_rate, length, diameter_mm, pipe_type):
    """
    Izračunava pad tlaka za niskotlačni priključak.
    
    Args:
        flow_rate: Protok plina (m³/h)
        length: Duljina cjevovoda (m)
        diameter_mm: Unutarnji promjer cijevi (mm)
        pipe_type: Tip cijevi (1 - PE-HD, 2 - SMLS)
        
    Returns:
        float: Pad tlaka (mbar)
    """
    # Odabir faktora trenja prema materijalu
    lambda_koef = LAMBDA_PEHD if pipe_type == 1 else LAMBDA_SMLS
    
    # Pretvorba promjera u m
    d_u = diameter_mm / 1000
    
    # Izračun pada tlaka
    dp = 6.25 * lambda_koef * (pow(flow_rate, 2) * RHO_PLIN * length) / pow(100 * d_u, 5)
    
    return dp

def calculate_pressure_drop_medium_pressure(flow_rate, length, diameter_mm, velocity, pipe_type):
    """
    Izračunava pad tlaka za srednjetlačni priključak.
    
    Args:
        flow_rate: Protok plina (m³/h)
        length: Duljina cjevovoda (m)
        diameter_mm: Unutarnji promjer cijevi (mm)
        velocity: Brzina plina (m/s)
        pipe_type: Tip cijevi (1 - PE-HD, 2 - SMLS)
        
    Returns:
        float: Pad tlaka (mbar)
    """
    # Odabir faktora trenja prema materijalu
    lambda_koef = LAMBDA_PEHD if pipe_type == 1 else LAMBDA_SMLS
    
    # Početni tlak (mbar)
    p1 = POCETNI_TLAK_SREDNJETLACNI
    
    # Pretvorba promjera u m
    d_u = diameter_mm / 1000
    
    # Izračun pada tlaka
    desna_strana = (lambda_koef * length * pow(velocity, 2) * RHO_PLIN * p1) / d_u
    p2_kvadrat = pow(p1, 2) - desna_strana
    p2 = math.sqrt(p2_kvadrat)
    dp = p1 - p2
    
    return dp

def select_gas_meter(flow_rate):
    """
    Odabire odgovarajući plinomjer na temelju protoka.
    
    Args:
        flow_rate: Vršni protok (m³/h)
        
    Returns:
        tuple: (oznaka, specifikacije) ili None ako nema odgovarajućeg plinomjera
    """
    from .data_tables import PLINOMJERI
    
    for oznaka, specifikacije in PLINOMJERI.items():
        if flow_rate <= specifikacije['Qmax']:
            return (oznaka, specifikacije)
    
    return None

def validate_pipe_selection(required_diameter, selected_inner_diameter):
    """
    Validira je li odabrana cijev odgovarajuća za potreban promjer.
    
    Args:
        required_diameter: Potreban promjer (mm)
        selected_inner_diameter: Unutarnji promjer odabrane cijevi (mm)
        
    Returns:
        tuple: (je_valjano, poruka)
    """
    if selected_inner_diameter < required_diameter:
        return (False, f"Odabrani promjer cijevi ({selected_inner_diameter:.1f} mm) je manji od potrebnog ({required_diameter:.1f} mm).")
    
    # Ako je promjer više od 50% veći od potrebnog, možda je cijev predimenzionirana
    if selected_inner_diameter > required_diameter * 1.5:
        return (True, f"Odabrani promjer cijevi ({selected_inner_diameter:.1f} mm) je znatno veći od potrebnog ({required_diameter:.1f} mm). Cijev je možda predimenzionirana.")
    
    return (True, "Odabrani promjer cijevi je odgovarajući.")

def validate_velocity(velocity, connection_type):
    """
    Validira je li brzina u granicama preporučenih vrijednosti.
    
    Args:
        velocity: Brzina plina (m/s)
        connection_type: Tip priključka (1 - niskotlačni, 2 - srednjetlačni)
        
    Returns:
        tuple: (je_valjano, poruka)
    """
    max_velocity = STANDARD_BRZINA
    
    if connection_type == 2:  # Srednjetlačni može imati nešto veću brzinu
        max_velocity = 8.0
    
    if velocity > max_velocity:
        return (False, f"Brzina u cijevi ({velocity:.2f} m/s) premašuje preporučenu vrijednost ({max_velocity:.1f} m/s).")
    
    if velocity < 1.0:
        return (True, f"Brzina u cijevi ({velocity:.2f} m/s) je relativno niska. Cijev je možda predimenzionirana.")
    
    return (True, "Brzina u cijevi je u preporučenim granicama.")

def validate_pressure_drop(pressure_drop, connection_type):
    """
    Validira je li pad tlaka u granicama dozvoljenih vrijednosti.
    
    Args:
        pressure_drop: Pad tlaka (mbar)
        connection_type: Tip priključka (1 - niskotlačni, 2 - srednjetlačni)
        
    Returns:
        tuple: (je_valjano, poruka)
    """
    max_drop = MAX_PAD_TLAKA_NISKOTLACNI if connection_type == 1 else MAX_PAD_TLAKA_SREDNJETLACNI
    
    if pressure_drop > max_drop:
        return (False, f"Pad tlaka ({pressure_drop:.2f} mbar) premašuje dozvoljenu vrijednost ({max_drop:.1f} mbar). Odaberite veći promjer cijevi.")
    
    # Ako je pad tlaka manji od 10% maksimalnog, možda je cijev predimenzionirana
    if pressure_drop < max_drop * 0.1:
        return (True, f"Pad tlaka ({pressure_drop:.2f} mbar) je znatno manji od dozvoljenog ({max_drop:.1f} mbar). Cijev je možda predimenzionirana.")
    
    return (True, "Pad tlaka je u dozvoljenim granicama.")

def get_pipe_recommendations(required_diameter, pipe_type):
    """
    Daje preporuke za odabir cijevi.
    
    Args:
        required_diameter: Potreban promjer (mm)
        pipe_type: Tip cijevi (1 - PE-HD, 2 - SMLS)
        
    Returns:
        dict: Dictionary s preporukama
    """
    from .data_tables import PEHD_CIJEVI, SMLS_CIJEVI
    
    cijevi = PEHD_CIJEVI if pipe_type == 1 else SMLS_CIJEVI
    naziv_cijevi = "PE-HD" if pipe_type == 1 else "SMLS"
    
    # Pronađi optimalnu cijev
    optimalna_cijev = None
    preporucena_cijev = None
    alternativna_cijev = None
    
    for i, dims in cijevi.items():
        if dims["unutarnji"] >= required_diameter:
            preporucena_cijev = i
            break
    
    # Ako nije pronađena preporučena cijev, uzmi najveću
    if preporucena_cijev is None and len(cijevi) > 0:
        preporucena_cijev = max(cijevi.keys())
    
    # Pronađi alternativnu cijev (jednu dimenziju veću)
    if preporucena_cijev is not None and preporucena_cijev < max(cijevi.keys()):
        alternativna_cijev = preporucena_cijev + 1
    
    return {
        "preporucena": preporucena_cijev,
        "alternativna": alternativna_cijev,
        "naziv_cijevi": naziv_cijevi
    }