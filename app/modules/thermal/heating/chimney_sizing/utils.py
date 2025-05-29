"""
Poboljšane pomoćne funkcije za proračun dimnjaka prema EN 13384-2 normi.
Ispravke svih kritičnih formula i dodavanje EN 13384-2 specifičnih funkcija.
"""

import math
from .constants import RHO_L0, GRAVITY, WATER_VAPOR_COEFFICIENTS, VALIDATION_LIMITS, OPTIMAL_CO2_RANGES

def calculate_air_density(temperature, altitude):
    """
    Izračunava gustoću zraka na temelju temperature i nadmorske visine.
    
    Args:
        temperature (float): Temperatura zraka [°C]
        altitude (float): Nadmorska visina [m]
    
    Returns:
        float: Gustoća zraka [kg/m³]
    """
    # Temperatura zraka u Kelvinima
    T_L = temperature + 273.15  # K
    
    # Atmosferski tlak na nadmorskoj visini lokacije
    p_L = 1013 * math.exp(-0.0001184 * altitude)  # hPa
    
    # Izračun gustoće zraka
    rho_L = RHO_L0 * (273.15 / T_L) * (p_L / 1013)
    
    return rho_L

def calculate_flue_gas_density_improved(air_density, flue_gas_temperature, co2_percentage, fuel_type):
    """
    POBOLJŠANI izračun gustoće dimnih plinova prema EN 13384-2.
    
    Args:
        air_density (float): Gustoća zraka [kg/m³]
        flue_gas_temperature (float): Temperatura dimnih plinova [°C]
        co2_percentage (float): Udio CO2 u dimnim plinovima [%]
        fuel_type (str): Vrsta goriva
    
    Returns:
        float: Gustoća dimnih plinova [kg/m³]
    """
    # Temperatura dimnih plinova u Kelvinima
    T_M = flue_gas_temperature + 273.15  # K
    
    # Korekcijski faktor ovisno o CO2 udjelu
    if fuel_type == "Zemni plin":
        if co2_percentage >= 10.0:
            # Optimalno izgaranje - veći udio CO2
            molecular_weight_factor = 1.08 + (co2_percentage - 10) * 0.02
        elif co2_percentage >= 8.0:
            # Umjereno izgaranje
            molecular_weight_factor = 1.05 + (co2_percentage - 8) * 0.015
        else:
            # Previše viška zraka - nizak CO2
            molecular_weight_factor = 1.02 + co2_percentage * 0.00375
    elif fuel_type == "Ukapljeni naftni plin":
        molecular_weight_factor = 1.06 + co2_percentage * 0.015
    else:
        # Ostala goriva
        molecular_weight_factor = 1.04 + co2_percentage * 0.012
    
    # Vodena para korekcija
    water_vapor_correction = WATER_VAPOR_COEFFICIENTS.get(fuel_type, 0.16)
    
    # Gustoća dimnih plinova s poboljšanim faktorima
    rho_M = air_density * (273.15 / T_M) * molecular_weight_factor * (1 - 0.378 * water_vapor_correction)
    
    return rho_M

def calculate_flue_gas_density(air_density, flue_gas_temperature, fuel_type):
    """
    Standardni izračun gustoće dimnih plinova (za kompatibilnost).
    Preporuča se korištenje calculate_flue_gas_density_improved().
    """
    # Koristi prosječni CO2 udio za staru kompatibilnost
    avg_co2 = {"Zemni plin": 9.6, "Ukapljeni naftni plin": 11.0, "Loživo ulje": 12.0}.get(fuel_type, 9.6)
    return calculate_flue_gas_density_improved(air_density, flue_gas_temperature, avg_co2, fuel_type)

def calculate_dew_point_temperature(co2_percentage, fuel_type="Zemni plin", excess_air_ratio=1.2):
    """
    ISPRAVKA: Točka rosišta dimnih plinova prema EN 13384-2 i literaturi.
    
    Args:
        co2_percentage (float): Udio CO2 u dimnim plinovima [%]
        fuel_type (str): Vrsta goriva
        excess_air_ratio (float): Omjer viška zraka (lambda)
    
    Returns:
        float: Temperatura točke rosišta [°C]
    """
    if fuel_type == "Zemni plin":
        # Formule prema literaturnim podacima za zemni plin
        if co2_percentage >= 11.0:
            # Visoki CO2 - malo viška zraka, visoka točka rosišta
            tp = 58.0 + (co2_percentage - 11.0) * 0.6
        elif co2_percentage >= 9.0:
            # Normalni CO2 udio
            tp = 54.0 + (co2_percentage - 9.0) * 2.0
        elif co2_percentage >= 7.0:
            # Nizak CO2 - previše viška zraka
            tp = 48.0 + (co2_percentage - 7.0) * 3.0
        else:
            # Vrlo nizak CO2
            tp = 42.0 + co2_percentage * 0.857
        
        # Korekcija za višak zraka
        if excess_air_ratio > 1.5:
            tp -= (excess_air_ratio - 1.5) * 4.0
        
    elif fuel_type == "Ukapljeni naftni plin":
        # UNP ima nešto nižu točku rosišta
        tp_ng = calculate_dew_point_temperature(co2_percentage * 0.85, "Zemni plin", excess_air_ratio)
        tp = tp_ng - 2.5
        
    elif fuel_type == "Loživo ulje":
        # Loživo ulje - niža točka rosišta zbog manje H2
        tp = 45.0 + co2_percentage * 0.4
        
    else:
        # Ostala goriva - konzervativna procjena
        tp = 40.0 + co2_percentage * 0.6
    
    # Ograničenja prema praktičnim vrijednostima
    return max(min(tp, 65.0), 35.0)

def calculate_required_pressure_pz(max_appliance_pressure, chimney_height, num_appliances, fuel_type):
    """
    ISPRAVKA: Potrebni potisni tlak PZ prema EN 13384-2.
    
    Args:
        max_appliance_pressure (float): Maksimalni tlak ložišta [Pa]
        chimney_height (float): Visina dimnjaka [m]
        num_appliances (int): Broj ložišta
        fuel_type (str): Vrsta goriva
    
    Returns:
        float: Potrebni potisni tlak PZ [Pa]
    """
    # Bazni tlak za prirodni vuk according to EN 13384-2
    if fuel_type == "Zemni plin":
        base_pz = 5.0  # Pa
    else:
        base_pz = 8.0  # Pa
    
    # Korekcija za visinu dimnjaka
    if chimney_height < 5.0:
        height_correction = (5.0 - chimney_height) * 2.0
    else:
        height_correction = 0.0
    
    # Korekcija za broj ložišta
    if num_appliances > 1:
        multi_appliance_factor = 1.0 + (num_appliances - 1) * 0.3
    else:
        multi_appliance_factor = 1.0
    
    # Minimalni tlak za siguran rad
    min_operational_pressure = max_appliance_pressure * 0.05  # 5% od max tlaka
    
    pz = (base_pz + height_correction) * multi_appliance_factor + min_operational_pressure
    
    return max(pz, 3.0)  # Apsolutni minimum 3 Pa

def calculate_backflow_factor(static_draft, total_pressure_drop, num_appliances, chimney_type="multi_inlet"):
    """
    ISPRAVKA: Faktor povrata dimnih plinova r prema EN 13384-2.
    
    Args:
        static_draft (float): Statički uzgon [Pa]
        total_pressure_drop (float): Ukupni pad tlaka [Pa]
        num_appliances (int): Broj ložišta
        chimney_type (str): Tip dimnjaka
    
    Returns:
        float: Faktor povrata r [-]
    """
    if num_appliances == 1:
        return 0.0  # Nema povrata s jednim ložištem
    
    # Bazni faktor ovisno o broju ložišta
    if num_appliances == 2:
        base_r = 0.25
    elif num_appliances == 3:
        base_r = 0.40
    elif num_appliances == 4:
        base_r = 0.55
    else:
        base_r = 0.70  # Za više ložišta
    
    # Korekcija ovisno o omjeru uzgona i otpora
    draft_ratio = static_draft / (total_pressure_drop + 0.1)  # +0.1 za izbjegavanje dijeljenja s 0
    
    if draft_ratio > 3.0:
        # Vrlo dobar uzgon
        correction_factor = 0.6
    elif draft_ratio > 2.0:
        # Dobar uzgon
        correction_factor = 0.8
    elif draft_ratio > 1.5:
        # Umjeren uzgon
        correction_factor = 1.0
    else:
        # Slab uzgon - povećan rizik povrata
        correction_factor = 1.3
    
    r = base_r * correction_factor
    
    return min(r, 1.0)  # r ne može biti veći od 1.0

def calculate_minimum_temperature_tmin(dew_point_temp, chimney_height, outdoor_temp, fuel_type):
    """
    ISPRAVKA: Minimalna temperatura za održavanje uzgona Tmin prema EN 13384-2.
    
    Args:
        dew_point_temp (float): Temperatura točke rosišta [°C]
        chimney_height (float): Visina dimnjaka [m]
        outdoor_temp (float): Vanjska temperatura [°C]
        fuel_type (str): Vrsta goriva
    
    Returns:
        float: Minimalna temperatura Tmin [°C]
    """
    # Bazna sigurnost od kondenzacije
    if fuel_type == "Zemni plin":
        condensation_safety = 10.0  # °C iznad točke rosišta
    else:
        condensation_safety = 15.0  # °C
    
    # Korekcija za visinu dimnjaka (viši dimnjak = veće hlađenje)
    if chimney_height > 10.0:
        height_correction = (chimney_height - 10.0) * 1.0
    else:
        height_correction = (10.0 - chimney_height) * 2.0  # Kratki dimnjak potrebuje višu temp
    
    # Korekcija za vanjsku temperaturu
    if outdoor_temp < -10.0:
        temp_correction = (-10.0 - outdoor_temp) * 0.5
    else:
        temp_correction = 0.0
    
    tmin = dew_point_temp + condensation_safety + height_correction + temp_correction
    
    return max(tmin, 25.0)  # Apsolutni minimum za uzgon

def calculate_static_draft(air_density, flue_gas_density, chimney_height, safety_number):
    """
    Izračunava statički uzgon dimnjaka.
    
    Args:
        air_density (float): Gustoća zraka [kg/m³]
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
        chimney_height (float): Efektivna visina dimnjaka [m]
        safety_number (float): Sigurnosni broj
    
    Returns:
        float: Statički uzgon [Pa]
    """
    return GRAVITY * chimney_height * (air_density - flue_gas_density) * safety_number

def calculate_flue_gas_velocity(mass_flow, diameter, flue_gas_density):
    """
    Izračunava brzinu strujanja dimnih plinova.
    
    Args:
        mass_flow (float): Maseni protok dimnih plinova [kg/s]
        diameter (float): Unutarnji promjer dimovoda [m]
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
    
    Returns:
        float: Brzina strujanja dimnih plinova [m/s]
    """
    return (4 * mass_flow) / (math.pi * diameter**2 * flue_gas_density)

def calculate_reynolds_number(mass_flow, diameter, temperature):
    """
    Izračunava Reynolds broj za strujanje dimnih plinova.
    
    Args:
        mass_flow (float): Maseni protok [kg/s]
        diameter (float): Promjer [m]
        temperature (float): Temperatura [°C]
    
    Returns:
        float: Reynolds broj [-]
    """
    # Kinematička viskoznost zraka pri temperaturi (Sutherland formula)
    T = temperature + 273.15  # K
    mu = 1.716e-5 * ((T / 273.15) ** 1.5) * (383.55 / (T + 110.4))  # kg/m/s
    
    # Gustoća pri temperaturi (približno)
    rho = 1.225 * (273.15 / T)  # kg/m³
    
    # Brzina
    velocity = (4 * mass_flow) / (math.pi * diameter**2 * rho)
    
    # Reynolds broj
    Re = rho * velocity * diameter / mu
    
    return Re

def calculate_friction_coefficient(roughness, diameter, reynolds_number=None):
    """
    Poboljšani izračun koeficijenta trenja u dimovodu.
    
    Args:
        roughness (float): Srednja hrapavost [m]
        diameter (float): Unutarnji promjer dimovoda [m]
        reynolds_number (float, optional): Reynolds broj
    
    Returns:
        float: Koeficijent trenja
    """
    # Relativna hrapavost
    relative_roughness = roughness / diameter
    
    if reynolds_number and reynolds_number > 4000:
        # Turbulentno strujanje - Colebrook formula (pojednostavljena)
        if relative_roughness > 0.05:
            # Vrlo hrapava površina
            f = 0.25 / (math.log10(relative_roughness/3.7) ** 2)
        else:
            # Normalna hrapavost
            f = 0.0054 + 0.396 * (relative_roughness ** 0.3)
    else:
        # Standardna formula za dimnjake (EN 13384-2)
        f = 0.0054 + 0.15 * (relative_roughness ** 0.33)
    
    return max(f, 0.005)  # Minimum za sigurnost

def calculate_pressure_drop_friction(friction_coefficient, chimney_height, flue_gas_density, 
                                    flue_gas_velocity, diameter, safety_number):
    """
    Izračunava pad tlaka zbog trenja u dimovodu.
    
    Args:
        friction_coefficient (float): Koeficijent trenja
        chimney_height (float): Efektivna visina dimnjaka [m]
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
        flue_gas_velocity (float): Brzina strujanja dimnih plinova [m/s]
        diameter (float): Unutarnji promjer dimovoda [m]
        safety_number (float): Sigurnosni broj
    
    Returns:
        float: Pad tlaka zbog trenja [Pa]
    """
    return (friction_coefficient * chimney_height * flue_gas_density * flue_gas_velocity**2) / (2 * diameter) * safety_number

def calculate_pressure_drop_resistance(resistance_coefficient, flue_gas_density, flue_gas_velocity, safety_number):
    """
    Izračunava pad tlaka zbog lokalnih otpora.
    
    Args:
        resistance_coefficient (float): Koeficijent lokalnog otpora
        flue_gas_density (float): Gustoća dimnih plinova [kg/m³]
        flue_gas_velocity (float): Brzina strujanja dimnih plinova [m/s]
        safety_number (float): Sigurnosni broj
    
    Returns:
        float: Pad tlaka zbog lokalnih otpora [Pa]
    """
    return resistance_coefficient * flue_gas_density * flue_gas_velocity**2 / 2 * safety_number

def calculate_total_pressure_drop(pressure_drop_friction, pressure_drop_resistance):
    """
    Izračunava ukupni pad tlaka u dimovodu.
    
    Args:
        pressure_drop_friction (float): Pad tlaka zbog trenja [Pa]
        pressure_drop_resistance (float): Pad tlaka zbog lokalnih otpora [Pa]
    
    Returns:
        float: Ukupni pad tlaka [Pa]
    """
    return pressure_drop_friction + pressure_drop_resistance

def calculate_actual_draft(static_draft, total_pressure_drop):
    """
    Izračunava stvarni uzgon dimnjaka.
    
    Args:
        static_draft (float): Statički uzgon [Pa]
        total_pressure_drop (float): Ukupni pad tlaka [Pa]
    
    Returns:
        float: Stvarni uzgon [Pa]
    """
    return static_draft - total_pressure_drop

def calculate_inner_wall_temperature_iterative(outdoor_temp, flue_gas_temp, 
                                              thermal_resistance_wall, thermal_resistance_ambient,
                                              mass_flow, diameter, max_iterations=10):
    """
    POBOLJŠANI iterativni izračun temperature unutarnje stijenke prema EN 13384-2.
    
    Args:
        outdoor_temp (float): Vanjska temperatura [°C]
        flue_gas_temp (float): Temperatura dimnih plinova [°C]
        thermal_resistance_wall (float): Toplinski otpor stijenke [m²K/W]
        thermal_resistance_ambient (float): Toplinski otpor prema vanjskom okolišu [m²K/W]
        mass_flow (float): Maseni protok [kg/s]
        diameter (float): Promjer [m]
        max_iterations (int): Maksimalni broj iteracija
    
    Returns:
        float: Temperatura unutarnje stijenke [°C]
    """
    # Početna procjena temperature stijenke
    tiob = outdoor_temp + (flue_gas_temp - outdoor_temp) * 0.4
    
    for i in range(max_iterations):
        # Reynolds broj za trenutnu temperaturu
        re = calculate_reynolds_number(mass_flow, diameter, tiob)
        
        # Nusselt broj (za strujanje u cijevi)
        if re > 4000:
            # Turbulentno strujanje
            pr = 0.72  # Prandtl broj za zrak
            nu = 0.023 * (re ** 0.8) * (pr ** 0.4)
        else:
            # Laminarno strujanje
            nu = 4.36  # Za konstantnu temperaturu stijenke
        
        # Koeficijent prijenosa topline
        thermal_conductivity_air = 0.025 + (tiob - 20) * 5e-5  # W/mK
        alpha_i = nu * thermal_conductivity_air / diameter  # W/m²K
        ri = 1.0 / alpha_i  # m²K/W
        
        # Nova temperatura stijenke
        total_resistance = ri + thermal_resistance_wall + thermal_resistance_ambient
        tiob_new = outdoor_temp + (flue_gas_temp - outdoor_temp) * ri / total_resistance
        
        # Provjera konvergencije
        if abs(tiob_new - tiob) < 0.1:
            break
            
        tiob = tiob_new
    
    return tiob

def calculate_inner_wall_temperature(outdoor_temp, flue_gas_temp, 
                                     thermal_resistance_wall, thermal_resistance_ambient):
    """
    Pojednostavljeni izračun temperature unutarnje stijenke (za kompatibilnost).
    Preporuča se korištenje calculate_inner_wall_temperature_iterative().
    """
    ri = 0.1  # Pretpostavljeni koeficijent prijenosa topline [m²K/W]
    
    total_resistance = ri + thermal_resistance_wall + thermal_resistance_ambient
    tiob = outdoor_temp + (flue_gas_temp - outdoor_temp) * ri / total_resistance
    
    return tiob

def check_freezing_condition(inner_wall_temperature, freezing_temperature=0):
    """
    Provjerava uvjet zaleđivanja.
    
    Args:
        inner_wall_temperature (float): Temperatura unutarnje stijenke [°C]
        freezing_temperature (float, optional): Točka ledišta [°C]. Standardno 0°C.
    
    Returns:
        bool: True ako nema opasnosti od zaleđivanja, False inače
    """
    return inner_wall_temperature > freezing_temperature

def validate_chimney_data(data):
    """
    Validira podatke dimnjaka prema EN 13384-2.
    
    Args:
        data (dict): Podaci o dimnjaku
        
    Returns:
        tuple: (errors, warnings)
    """
    errors = []
    warnings = []
    
    # Provjera osnovnih parametara
    chimney_height = sum(section.get("effective_height", 0) for section in data.get("chimney", {}).get("sections", []))
    
    if chimney_height < VALIDATION_LIMITS["min_chimney_height"]:
        errors.append(f"Dimnjak je prenizak - minimalno {VALIDATION_LIMITS['min_chimney_height']} m prema EN 13384-2")
    elif chimney_height < 4.0:
        warnings.append("Preporuča se visina dimnjaka minimalno 4.0 m za optimalan rad")
    
    if chimney_height > VALIDATION_LIMITS["max_chimney_height"]:
        warnings.append("Vrlo visok dimnjak - provjerite statičke uvjete")
    
    # Provjera promjera
    diameter = data.get("chimney", {}).get("inner_diameter", 0)
    if diameter < VALIDATION_LIMITS["min_chimney_diameter"]:
        warnings.append("Mali promjer dimnjaka može uzrokovati probleme s uzgonom")
    elif diameter > VALIDATION_LIMITS["max_chimney_diameter"]:
        warnings.append("Veliki promjer dimnjaka - provjerite brzine strujanja")
    
    # Provjera temperatura
    temps = data.get("general", {}).get("temperatures", {})
    outdoor_temp = temps.get("outdoor", 0)
    ambient_temp = temps.get("ambient", 15)
    
    if outdoor_temp > ambient_temp:
        warnings.append("Vanjska temperatura viša od okružujuće - provjerite unos")
    
    if outdoor_temp < VALIDATION_LIMITS["min_outdoor_temp"]:
        warnings.append("Vrlo niska vanjska temperatura - potrebna dodatna provjera")
    
    # Provjera ložišta
    appliances = data.get("appliances", [])
    if len(appliances) > VALIDATION_LIMITS["max_appliances"]:
        errors.append(f"Previše ložišta - maksimalno {VALIDATION_LIMITS['max_appliances']} prema EN 13384-2")
    
    for i, appliance in enumerate(appliances):
        full_load = appliance.get("full_load", {})
        
        flue_temp = full_load.get("flue_gas_temperature", 0)
        if flue_temp < VALIDATION_LIMITS["min_flue_gas_temp"]:
            warnings.append(f"Niska temperatura dimnih plinova u ložištu {i+1} (< {VALIDATION_LIMITS['min_flue_gas_temp']}°C)")
        elif flue_temp > VALIDATION_LIMITS["max_flue_gas_temp"]:
            warnings.append(f"Visoka temperatura dimnih plinova u ložištu {i+1} (> {VALIDATION_LIMITS['max_flue_gas_temp']}°C)")
        
        co2_perc = full_load.get("co2_percentage", 0)
        fuel_type = appliance.get("fuel", "Zemni plin")
        
        if co2_perc < VALIDATION_LIMITS["min_co2_percentage"]:
            warnings.append(f"Nizak CO2 u ložištu {i+1} - možda previše viška zraka")
        elif co2_perc > VALIDATION_LIMITS["max_co2_percentage"]:
            warnings.append(f"Visok CO2 u ložištu {i+1} - provjerite podešavanje ložišta")
        
        # Provjera optimalnog CO2 raspona
        if fuel_type in OPTIMAL_CO2_RANGES:
            min_co2, max_co2 = OPTIMAL_CO2_RANGES[fuel_type]
            if not (min_co2 <= co2_perc <= max_co2):
                warnings.append(f"CO2 u ložištu {i+1} izvan optimalnog raspona ({min_co2}-{max_co2}%) za {fuel_type}")
        
        mass_flow = full_load.get("flue_gas_mass_flow", 0)
        if mass_flow < VALIDATION_LIMITS["min_mass_flow"]:
            warnings.append(f"Mala masena struja dimnih plinova u ložištu {i+1}")
        elif mass_flow > VALIDATION_LIMITS["max_mass_flow"]:
            warnings.append(f"Velika masena struja dimnih plinova u ložištu {i+1}")
    
    return errors, warnings