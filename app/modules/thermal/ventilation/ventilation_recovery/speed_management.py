# modules/thermal/ventilation/ventilation_recovery/speed_management.py

def get_speed_options(model_data):
    """
    Vraća dostupne opcije brzina za odabrani model rekuperatora.
    
    Args:
        model_data (dict): Podaci o modelu rekuperatora
        
    Returns:
        list: Lista opcija brzina s pripadajućim podacima
    """
    if not model_data or "flow_rates" not in model_data:
        return []
    
    options = []
    for speed, data in model_data["flow_rates"].items():
        # Formatiranje imena brzine za prikaz
        speed_name = speed.replace("speed_", "Brzina ")
        speed_percentage = "100%" if speed == "speed_4" else \
                          "75%" if speed == "speed_3" else \
                          "50%" if speed == "speed_2" else \
                          "25%"
        
        # Dohvaćanje podataka o protoku i tlaku
        flow = data["flow"]
        if isinstance(data["pressure"], dict):
            pressure = data["pressure"]["supply"]
        else:
            pressure = data["pressure"]
        
        # Dohvaćanje podataka o potrošnji i buci
        power = model_data.get("power_consumption", {}).get(speed, "N/A")
        noise = model_data.get("noise_level", {}).get(speed, "N/A")
        
        options.append({
            "id": speed,
            "name": f"{speed_name} ({speed_percentage})",
            "percentage": speed_percentage,
            "flow": flow,
            "pressure": pressure,
            "power": power,
            "noise": noise
        })
    
    return options

def check_speed_requirements(speed_data, required_flow, required_pressure):
    """
    Provjerava zadovoljava li odabrana brzina zahtjeve za protokom i tlakom.
    
    Args:
        speed_data (dict): Podaci o odabranoj brzini
        required_flow (float): Potreban protok u m³/h
        required_pressure (float): Potreban tlak u Pa
        
    Returns:
        dict: Rezultati provjere
    """
    flow_ok = speed_data["flow"] >= required_flow
    pressure_ok = speed_data["pressure"] >= required_pressure
    
    flow_percentage = required_flow / speed_data["flow"] * 100 if speed_data["flow"] > 0 else float('inf')
    pressure_percentage = required_pressure / speed_data["pressure"] * 100 if speed_data["pressure"] > 0 else float('inf')
    
    return {
        "flow_ok": flow_ok,
        "pressure_ok": pressure_ok,
        "overall_ok": flow_ok and pressure_ok,
        "flow_percentage": flow_percentage,
        "pressure_percentage": pressure_percentage
    }

def suggest_optimal_speed(model_data, required_flow, required_pressure):
    """
    Predlaže optimalnu brzinu rekuperatora.
    
    Args:
        model_data (dict): Podaci o modelu rekuperatora
        required_flow (float): Potreban protok u m³/h
        required_pressure (float): Potreban tlak u Pa
        
    Returns:
        dict: Podaci o optimalnoj brzini ili None ako nijdna brzina ne zadovoljava
    """
    options = get_speed_options(model_data)
    valid_options = []
    
    for option in options:
        check = check_speed_requirements(option, required_flow, required_pressure)
        if check["overall_ok"]:
            valid_options.append((option, check["flow_percentage"]))
    
    if not valid_options:
        return None
    
    # Odabir brzine koja će raditi s najmanjim mogućim opterećenjem
    # ali ne manje od 60% kapaciteta radi učinkovitosti
    optimal = min(valid_options, key=lambda x: abs(x[1] - 80))
    
    return optimal[0]

def create_schedule_template():
    """
    Stvara predložak vremenskog rasporeda brzina.
    
    Returns:
        dict: Struktura vremenskog rasporeda
    """
    return {
        "workdays": {
            "working_hours": {"speed": "speed_3", "hours": 12},
            "reduced_hours": {"speed": "speed_2", "hours": 4},
            "maintenance": {"speed": "speed_1", "hours": 8}
        },
        "weekend": {
            "working_hours": {"speed": "speed_2", "hours": 8},
            "reduced_hours": {"speed": "speed_1", "hours": 16}
        }
    }

def calculate_schedule_energy(model_data, schedule):
    """
    Izračunava potrošnju energije prema rasporedu brzina.
    
    Args:
        model_data (dict): Podaci o modelu rekuperatora
        schedule (dict): Vremenski raspored brzina
        
    Returns:
        dict: Podaci o potrošnji energije
    """
    if not model_data or "power_consumption" not in model_data:
        return {"total": 0, "details": []}
    
    # Dani u godini
    workdays = 5 * 52  # 5 dana tjedno, 52 tjedna
    weekend_days = 2 * 52  # 2 dana tjedno, 52 tjedna
    
    total_consumption = 0
    details = []
    
    # Potrošnja radnim danima
    for period, data in schedule["workdays"].items():
        speed = data["speed"]
        hours = data["hours"]
        annual_hours = hours * workdays
        
        power = model_data["power_consumption"].get(speed, 0)
        consumption = power * annual_hours / 1000  # kWh
        
        total_consumption += consumption
        details.append({
            "period": f"Radni dani - {period}",
            "speed": speed,
            "hours_per_day": hours,
            "annual_hours": annual_hours,
            "power": power,
            "consumption": consumption
        })
    
    # Potrošnja vikendom
    for period, data in schedule["weekend"].items():
        speed = data["speed"]
        hours = data["hours"]
        annual_hours = hours * weekend_days
        
        power = model_data["power_consumption"].get(speed, 0)
        consumption = power * annual_hours / 1000  # kWh
        
        total_consumption += consumption
        details.append({
            "period": f"Vikend - {period}",
            "speed": speed,
            "hours_per_day": hours,
            "annual_hours": annual_hours,
            "power": power,
            "consumption": consumption
        })
    
    return {
        "total": total_consumption,
        "details": details
    }