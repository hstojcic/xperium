# modules/thermal/ventilation/ventilation_recovery/heat_recovery.py

from modules.thermal.ventilation.ventilation_recovery.constants import AIR_DENSITY, AIR_SPECIFIC_HEAT
from modules.thermal.ventilation.ventilation_recovery.utils import convert_m3h_to_m3s

def calculate_temperature_after_recuperator(outdoor_temp, indoor_temp, efficiency):
    """
    Izračunava temperaturu nakon rekuperatora.
    
    Args:
        outdoor_temp (float): Vanjska temperatura u °C
        indoor_temp (float): Unutarnja temperatura u °C
        efficiency (float): Učinkovitost rekuperatora (0-1)
        
    Returns:
        float: Temperatura nakon rekuperatora u °C
    """
    return outdoor_temp + efficiency * (indoor_temp - outdoor_temp)

def calculate_energy_savings(flow_rate, outdoor_temp, indoor_temp, efficiency, hours):
    """
    Izračunava uštedu energije kroz rekuperaciju.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        outdoor_temp (float): Vanjska temperatura u °C
        indoor_temp (float): Unutarnja temperatura u °C
        efficiency (float): Učinkovitost rekuperatora (0-1)
        hours (float): Broj sati rada
        
    Returns:
        float: Ušteda energije u kWh
    """
    # Konverzija protoka iz m³/h u m³/s
    flow_m3s = convert_m3h_to_m3s(flow_rate)
    
    # Temperatura nakon rekuperatora
    temp_after = calculate_temperature_after_recuperator(outdoor_temp, indoor_temp, efficiency)
    
    # Toplinski kapacitet zraka (cp × ρ)
    heat_capacity = AIR_SPECIFIC_HEAT * AIR_DENSITY
    
    # Toplinski tok koji se rekuperira
    heat_flow = flow_m3s * heat_capacity * (temp_after - outdoor_temp)
    
    # Energija tijekom zadanog perioda
    energy = heat_flow * hours  # Ws
    
    # Konverzija u kWh
    energy_kwh = energy / 3600000
    
    return energy_kwh

def calculate_annual_energy_savings(flow_rate, efficiency, location="continental", operation_hours=8760):
    """
    Procjenjuje godišnju uštedu energije kroz rekuperaciju.
    
    Args:
        flow_rate (float): Protok zraka u m³/h
        efficiency (float): Učinkovitost rekuperatora (0-1)
        location (str): Lokacija ("continental" ili "coastal")
        operation_hours (float): Godišnji broj sati rada
        
    Returns:
        float: Godišnja ušteda energije u kWh
    """
    # Pojednostavljeni model za procjenu uštede na temelju lokacije
    # U stvarnoj implementaciji ovo bi trebalo biti detaljnije s klimatskim podacima
    
    if location == "continental":
        # Kontinentalna Hrvatska
        heating_degree_days = 2800  # stupanj-dani grijanja
        avg_indoor_temp = 21  # °C
        avg_heating_season_temp = 5  # °C
    else:
        # Primorska Hrvatska
        heating_degree_days = 1500  # stupanj-dani grijanja
        avg_indoor_temp = 21  # °C
        avg_heating_season_temp = 10  # °C
    
    # Učinkovitost rekuperacije
    effective_efficiency = efficiency * 0.9  # Uzimamo u obzir gubitke u radu
    
    # Trajanje sezone grijanja u satima (aproksimacija)
    heating_season_hours = heating_degree_days * 24 / (avg_indoor_temp - avg_heating_season_temp)
    
    # Ograničavamo na stvarne sate rada
    heating_hours = min(heating_season_hours, operation_hours)
    
    # Ušteda energije tijekom sezone grijanja
    energy_savings = calculate_energy_savings(
        flow_rate,
        avg_heating_season_temp,
        avg_indoor_temp,
        effective_efficiency,
        heating_hours
    )
    
    return energy_savings

def calculate_energy_efficiency_ratio(recuperator_efficiency, electric_power, flow_rate, temp_diff):
    """
    Izračunava omjer energetske učinkovitosti rekuperatora.
    
    Args:
        recuperator_efficiency (float): Učinkovitost rekuperatora (0-1)
        electric_power (float): Električna snaga uređaja u W
        flow_rate (float): Protok zraka u m³/h
        temp_diff (float): Temperaturna razlika (unutarnja - vanjska) u K
        
    Returns:
        float: Omjer energetske učinkovitosti
    """
    # Konverzija protoka iz m³/h u m³/s
    flow_m3s = convert_m3h_to_m3s(flow_rate)
    
    # Toplinski kapacitet zraka (cp × ρ)
    heat_capacity = AIR_SPECIFIC_HEAT * AIR_DENSITY
    
    # Rekuperirani toplinski tok
    recovered_heat = flow_m3s * heat_capacity * temp_diff * recuperator_efficiency
    
    # Omjer dobivene toplinske energije i utrošene električne energije
    if electric_power > 0:
        ratio = recovered_heat / electric_power
    else:
        ratio = 0
    
    return ratio