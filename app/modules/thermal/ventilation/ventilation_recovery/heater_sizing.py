# modules/thermal/ventilation/ventilation_recovery/heater_sizing.py

from modules.thermal.ventilation.ventilation_recovery.constants import AIR_DENSITY, AIR_SPECIFIC_HEAT
from modules.thermal.ventilation.ventilation_recovery.utils import convert_m3h_to_m3s
from modules.thermal.ventilation.ventilation_recovery.heat_recovery import calculate_temperature_after_recuperator

def calculate_heater_power(flow_rate, outdoor_temp, indoor_temp, target_temp, recuperator_efficiency):
    """
    Izračunava potrebnu snagu električnog grijača.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        outdoor_temp (float): Vanjska temperatura u °C
        indoor_temp (float): Unutarnja temperatura u °C
        target_temp (float): Ciljna temperatura nakon grijača u °C
        recuperator_efficiency (float): Učinkovitost rekuperatora (0-1)
        
    Returns:
        float: Potrebna snaga grijača u W
    """
    # Izračun temperature nakon rekuperatora
    temp_after_recuperator = calculate_temperature_after_recuperator(
        outdoor_temp, indoor_temp, recuperator_efficiency
    )
    
    # Provjera je li grijač potreban
    if temp_after_recuperator >= target_temp:
        return 0, temp_after_recuperator
    
    # Konverzija protoka iz m³/h u m³/s
    flow_m3s = convert_m3h_to_m3s(flow_rate)
    
    # Izračun snage
    power = flow_m3s * AIR_DENSITY * AIR_SPECIFIC_HEAT * (target_temp - temp_after_recuperator)
    
    return power, temp_after_recuperator

def calculate_frost_protection_temperature(recuperator_efficiency):
    """
    Izračunava minimalnu vanjsku temperaturu pri kojoj nema opasnosti od smrzavanja.
    
    Args:
        recuperator_efficiency (float): Učinkovitost rekuperatora (0-1)
        
    Returns:
        float: Minimalna sigurna temperatura u °C
    """
    # Pretpostavka: unutarnja temperatura 21°C, relativna vlažnost 50%
    # Točka rosišta oko 10°C
    # Temperatura na kojoj bi se kondenzat mogao smrznuti: 0°C
    
    # Minimalna temperatura na rekuperatoru da bi se izbjeglo smrzavanje
    min_recuperator_temp = 0
    
    # Pretpostavljena unutarnja temperatura
    indoor_temp = 21
    
    # Rješavamo za minimalnu vanjsku temperaturu:
    # min_recuperator_temp = outdoor_temp + efficiency * (indoor_temp - outdoor_temp)
    # min_recuperator_temp = outdoor_temp * (1 - efficiency) + indoor_temp * efficiency
    # outdoor_temp = (min_recuperator_temp - indoor_temp * efficiency) / (1 - efficiency)
    
    if recuperator_efficiency >= 1.0:
        return -30  # Praktično ograničenje
    
    outdoor_temp = (min_recuperator_temp - indoor_temp * recuperator_efficiency) / (1 - recuperator_efficiency)
    
    return outdoor_temp

def calculate_final_heater_power(required_power, safety_factor=1.15):
    """
    Izračunava konačnu snagu grijača uključujući sigurnosni faktor.
    
    Args:
        required_power (float): Potrebna snaga grijača u W
        safety_factor (float): Sigurnosni faktor
        
    Returns:
        float: Konačna snaga grijača u kW
    """
    # Dodavanje sigurnosnog faktora i konverzija u kW
    return required_power * safety_factor / 1000

def select_standard_heater_power(required_power):
    """
    Odabire standardnu snagu grijača.
    
    Args:
        required_power (float): Potrebna snaga grijača u kW
        
    Returns:
        float: Standardna snaga grijača u kW
    """
    # Standardne snage grijača u kW
    standard_powers = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0]
    
    # Odabir najbliže veće standardne snage
    for power in standard_powers:
        if power >= required_power:
            return power
    
    # Ako je potrebna snaga veća od najveće standardne, vraćamo najbližu
    return standard_powers[-1]