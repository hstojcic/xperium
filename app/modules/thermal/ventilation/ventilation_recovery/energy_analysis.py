# modules/thermal/ventilation/ventilation_recovery/energy_analysis.py

def calculate_electricity_consumption(model_or_power, hours, speed_factors=None):
    """
    Izračunava godišnju potrošnju električne energije rekuperatora.
    
    Args:
        model_or_power: Nazivna snaga uređaja u W ili naziv modela rekuperatora
        hours (int): Godišnji broj sati rada
        speed_factors (dict): Rječnik s postotkom vremena rada na različitim brzinama
        
    Returns:
        float: Godišnja potrošnja električne energije u kWh
    """
    # Provjera tipa - ako je string, dohvati podatke o modelu
    if isinstance(model_or_power, str):
        from modules.thermal.ventilation.ventilation_recovery.models_database import get_model_by_name
        model_data = get_model_by_name(model_or_power)
        if model_data and "power_consumption" in model_data:
            power = model_data["power_consumption"].get("speed_4", 0)  # Maksimalna snaga
        else:
            power = 0
    else:
        power = model_or_power

    if speed_factors is None:
        # Pretpostavljamo rad pri maksimalnoj brzini
        return power * hours / 1000
    
    # Izračun s različitim brzinama rada
    total_consumption = 0
    
    # Faktori snage za različite brzine (aproksimacija)
    power_reduction = {
        "speed_4": 1.0,  # 100% snage
        "speed_3": 0.5,  # 50% snage
        "speed_2": 0.25,  # 25% snage
        "speed_1": 0.1   # 10% snage
    }
    
    for speed, percentage in speed_factors.items():
        if speed in power_reduction:
            reduced_power = power * power_reduction[speed]
            hours_at_speed = hours * percentage / 100
            consumption = reduced_power * hours_at_speed / 1000
            total_consumption += consumption
    
    return total_consumption

def calculate_heater_consumption(heater_power, outdoor_temp, target_temp, hours, degree_days):
    """
    Izračunava godišnju potrošnju električnog grijača.
    
    Args:
        heater_power (float): Snaga grijača u kW
        outdoor_temp (float): Projektna vanjska temperatura u °C
        target_temp (float): Ciljna temperatura nakon grijača u °C
        hours (int): Godišnji broj sati rada
        degree_days (float): Stupanj-dani grijanja
        
    Returns:
        float: Godišnja potrošnja električne energije grijača u kWh
    """
    # Sigurnosna provjera
    if not isinstance(heater_power, (int, float)) or heater_power < 0:
        heater_power = 0
        
    if not isinstance(outdoor_temp, (int, float)):
        outdoor_temp = -15
        
    if not isinstance(target_temp, (int, float)):
        target_temp = 2
    
    # Temperaturna razlika za projektno stanje
    design_temp_diff = target_temp - outdoor_temp
    if design_temp_diff <= 0:
        return 0  # Nema potrebe za grijanjem
    
    # Prosječna temperaturna razlika tijekom sezone grijanja
    # Određuje se pomoću stupanj-dana
    avg_temp_diff = degree_days * 24 / hours if hours > 0 else 0
    
    # Faktor opterećenja grijača (omjer stvarne i projektne temperaturne razlike)
    load_factor = avg_temp_diff / design_temp_diff if design_temp_diff > 0 else 0
    
    # Godišnja potrošnja energije
    annual_consumption = heater_power * hours * load_factor
    
    return annual_consumption

def calculate_cost_savings(energy_savings, electricity_consumption, heater_consumption, energy_price, electricity_price):
    """
    Izračunava financijske uštede na temelju uštede energije.
    
    Args:
        energy_savings (float): Ušteda energije grijanja u kWh
        electricity_consumption (float): Potrošnja električne energije rekuperatora u kWh
        heater_consumption (float): Potrošnja električnog grijača u kWh
        energy_price (float): Cijena toplinske energije u €/kWh
        electricity_price (float): Cijena električne energije u €/kWh
        
    Returns:
        float: Financijska ušteda u €
    """
    # Ušteda energije za grijanje
    heating_savings = energy_savings * energy_price
    
    # Trošak električne energije za rekuperator i grijač
    electricity_cost = (electricity_consumption + heater_consumption) * electricity_price
    
    # Ukupna ušteda
    total_savings = heating_savings - electricity_cost
    
    return total_savings

def calculate_payback_period(investment_cost, annual_savings):
    """
    Izračunava jednostavni period povrata investicije.
    
    Args:
        investment_cost (float): Trošak investicije
        annual_savings (float): Godišnja ušteda
        
    Returns:
        float: Period povrata u godinama
    """
    if annual_savings <= 0:
        return float('inf')
    
    return investment_cost / annual_savings

def calculate_co2_reduction(energy_savings, electricity_consumption, heater_consumption):
    """
    Izračunava smanjenje emisije CO2.
    
    Args:
        energy_savings (float): Ušteda energije u kWh
        electricity_consumption (float): Potrošnja električne energije rekuperatora u kWh
        heater_consumption (float): Potrošnja električnog grijača u kWh
        
    Returns:
        float: Smanjenje emisije CO2 u kg
    """
    # Faktori emisije CO2 (kg/kWh)
    heating_co2_factor = 0.25  # Primjer za prirodni plin
    electricity_co2_factor = 0.35  # Primjer za mix električne energije u Hrvatskoj
    
    # Smanjenje emisije CO2 zbog uštede energije za grijanje
    heating_co2_reduction = energy_savings * heating_co2_factor
    
    # Povećanje emisije CO2 zbog potrošnje električne energije
    electricity_co2_emission = (electricity_consumption + heater_consumption) * electricity_co2_factor
    
    # Ukupno smanjenje emisije CO2
    total_co2_reduction = heating_co2_reduction - electricity_co2_emission
    
    return total_co2_reduction