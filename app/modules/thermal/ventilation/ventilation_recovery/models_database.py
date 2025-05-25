# modules/thermal/ventilation/ventilation_recovery/models_database.py

# Baza podataka Mitsubishi Lossnay rekuperatora
LOSSNAY_MODELS = {
    "LGH-RVX3": [
        {
            "model": "LGH-15RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 150, "pressure": 120},
                "speed_3": {"flow": 113, "pressure": 68},
                "speed_2": {"flow": 75, "pressure": 30},
                "speed_1": {"flow": 38, "pressure": 8},
            },
            "connections": "Ø97.5 (Ø110)",
            "diameter": 110,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 38,  # W
                "speed_3": 20,
                "speed_2": 11,
                "speed_3": 5
            },
            "noise_level": {
                "speed_4": 30,  # dB(A)
                "speed_3": 25,
                "speed_2": 19,
                "speed_1": 17
            },
            "efficiency": 0.80  # 80% učinkovitost rekuperacije
        },
        {
            "model": "LGH-25RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 250, "pressure": 120},
                "speed_3": {"flow": 188, "pressure": 68},
                "speed_2": {"flow": 125, "pressure": 30},
                "speed_1": {"flow": 63, "pressure": 8},
            },
            "connections": "Ø142 (Ø160)",
            "diameter": 160,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 48,  # W
                "speed_3": 26,
                "speed_2": 13,
                "speed_3": 6
            },
            "noise_level": {
                "speed_4": 32,  # dB(A)
                "speed_3": 26,
                "speed_2": 20,
                "speed_1": 17
            },
            "efficiency": 0.80  # 80% učinkovitost rekuperacije
        },
        {
            "model": "LGH-35RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 350, "pressure": 160},
                "speed_3": {"flow": 263, "pressure": 90},
                "speed_2": {"flow": 175, "pressure": 40},
                "speed_1": {"flow": 88, "pressure": 10},
            },
            "connections": "Ø142 (Ø160)",
            "diameter": 160,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 92,  # W
                "speed_3": 46,
                "speed_2": 18,
                "speed_3": 7
            },
            "noise_level": {
                "speed_4": 34,  # dB(A)
                "speed_3": 27,
                "speed_2": 20,
                "speed_1": 17
            },
            "efficiency": 0.80  # 80% učinkovitost rekuperacije
        },
        {
            "model": "LGH-50RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 500, "pressure": 150},
                "speed_3": {"flow": 375, "pressure": 85},
                "speed_2": {"flow": 250, "pressure": 38},
                "speed_1": {"flow": 125, "pressure": 10},
            },
            "connections": "Ø192 (Ø208)",
            "diameter": 208,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 190,  # W
                "speed_3": 92,
                "speed_2": 38,
                "speed_3": 15
            },
            "noise_level": {
                "speed_4": 36,  # dB(A)
                "speed_3": 29,
                "speed_2": 23,
                "speed_1": 18
            },
            "efficiency": 0.78  # 78% učinkovitost rekuperacije
        },
        {
            "model": "LGH-65RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 650, "pressure": 150},
                "speed_3": {"flow": 488, "pressure": 85},
                "speed_2": {"flow": 325, "pressure": 38},
                "speed_1": {"flow": 163, "pressure": 10},
            },
            "connections": "Ø192 (Ø208)",
            "diameter": 208,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 265,  # W
                "speed_3": 140,
                "speed_2": 60,
                "speed_3": 20
            },
            "noise_level": {
                "speed_4": 37,  # dB(A)
                "speed_3": 30,
                "speed_2": 23,
                "speed_1": 18
            },
            "efficiency": 0.78  # 78% učinkovitost rekuperacije
        },
        {
            "model": "LGH-80RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 800, "pressure": 170},
                "speed_3": {"flow": 600, "pressure": 96},
                "speed_2": {"flow": 400, "pressure": 43},
                "speed_1": {"flow": 200, "pressure": 11},
            },
            "connections": "Ø242 (Ø258)",
            "diameter": 258,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 340,  # W
                "speed_3": 180,
                "speed_2": 78,
                "speed_3": 24
            },
            "noise_level": {
                "speed_4": 37,  # dB(A)
                "speed_3": 31,
                "speed_2": 24,
                "speed_1": 19
            },
            "efficiency": 0.78  # 78% učinkovitost rekuperacije
        },
        {
            "model": "LGH-100RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 1000, "pressure": 190},
                "speed_3": {"flow": 750, "pressure": 107},
                "speed_2": {"flow": 500, "pressure": 48},
                "speed_1": {"flow": 250, "pressure": 12},
            },
            "connections": "Ø242 (Ø258)",
            "diameter": 258,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 420,  # W
                "speed_3": 220,
                "speed_2": 90,
                "speed_3": 30
            },
            "noise_level": {
                "speed_4": 38,  # dB(A)
                "speed_3": 32,
                "speed_2": 25,
                "speed_1": 20
            },
            "efficiency": 0.77  # 77% učinkovitost rekuperacije
        },
        {
            "model": "LGH-160RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 1600, "pressure": 170},
                "speed_3": {"flow": 1200, "pressure": 96},
                "speed_2": {"flow": 800, "pressure": 43},
                "speed_1": {"flow": 400, "pressure": 11},
            },
            "connections": "Ø242 (Ø258)",
            "diameter": 258,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 670,  # W
                "speed_3": 380,
                "speed_2": 170,
                "speed_3": 70
            },
            "noise_level": {
                "speed_4": 40,  # dB(A)
                "speed_3": 33,
                "speed_2": 26,
                "speed_1": 21
            },
            "efficiency": 0.77  # 77% učinkovitost rekuperacije
        },
        {
            "model": "LGH-200RVX3-E",
            "flow_rates": {
                "speed_4": {"flow": 2000, "pressure": 170},
                "speed_3": {"flow": 1500, "pressure": 96},
                "speed_2": {"flow": 1000, "pressure": 43},
                "speed_1": {"flow": 500, "pressure": 11},
            },
            "connections": "Ø242 (Ø258)",
            "diameter": 258,
            "series": "RVX3",
            "type": "ERV",
            "power_consumption": {
                "speed_4": 850,  # W
                "speed_3": 460,
                "speed_2": 180,
                "speed_3": 80
            },
            "noise_level": {
                "speed_4": 40,  # dB(A)
                "speed_3": 34,
                "speed_2": 27,
                "speed_1": 21
            },
            "efficiency": 0.77  # 77% učinkovitost rekuperacije
        }
    ],
    "LGH-RVXT": [
        {
            "model": "LGH-150RVXT-E",
            "flow_rates": {
                "speed_4": {"flow": 1500, "pressure": {"supply": 175, "extract": 100}},
                "speed_3": {"flow": 1125, "pressure": {"supply": 98, "extract": 56}},
                "speed_2": {"flow": 750, "pressure": {"supply": 44, "extract": 25}},
                "speed_1": {"flow": 375, "pressure": {"supply": 11, "extract": 6}},
            },
            "connections": "Ø250",
            "diameter": 250,
            "series": "RVXT",
            "type": "ERV-Thin",
            "power_consumption": {
                "speed_4": 720,  # W
                "speed_3": 400,
                "speed_2": 180,
                "speed_3": 80
            },
            "noise_level": {
                "speed_4": 39,  # dB(A)
                "speed_3": 35,
                "speed_2": 28,
                "speed_1": 22
            },
            "efficiency": 0.80  # 80% učinkovitost rekuperacije
        },
        {
            "model": "LGH-200RVXT-E",
            "flow_rates": {
                "speed_4": {"flow": 2000, "pressure": {"supply": 175, "extract": 100}},
                "speed_3": {"flow": 1500, "pressure": {"supply": 98, "extract": 56}},
                "speed_2": {"flow": 1000, "pressure": {"supply": 44, "extract": 25}},
                "speed_1": {"flow": 500, "pressure": {"supply": 11, "extract": 6}},
            },
            "connections": "Ø250",
            "diameter": 250,
            "series": "RVXT",
            "type": "ERV-Thin",
            "power_consumption": {
                "speed_4": 900,  # W
                "speed_3": 500,
                "speed_2": 220,
                "speed_3": 90
            },
            "noise_level": {
                "speed_4": 40,  # dB(A)
                "speed_3": 36,
                "speed_2": 29,
                "speed_1": 23
            },
            "efficiency": 0.80  # 80% učinkovitost rekuperacije
        },
        {
            "model": "LGH-250RVXT-E",
            "flow_rates": {
                "speed_4": {"flow": 2500, "pressure": {"supply": 175, "extract": 100}},
                "speed_3": {"flow": 1875, "pressure": {"supply": 98, "extract": 56}},
                "speed_2": {"flow": 1250, "pressure": {"supply": 44, "extract": 25}},
                "speed_1": {"flow": 625, "pressure": {"supply": 11, "extract": 6}},
            },
            "connections": "Ø250",
            "diameter": 250,
            "series": "RVXT",
            "type": "ERV-Thin",
            "power_consumption": {
                "speed_4": 1100,  # W
                "speed_3": 620,
                "speed_2": 250,
                "speed_3": 100
            },
            "noise_level": {
                "speed_4": 41,  # dB(A)
                "speed_3": 37,
                "speed_2": 30,
                "speed_1": 24
            },
            "efficiency": 0.80  # 80% učinkovitost rekuperacije
        }
    ],
    "LGH-RVS": [
        {
            "model": "LGH-50RVS-E",
            "flow_rates": {
                "speed_4": {"flow": 500, "pressure": 150},
                "speed_3": {"flow": 375, "pressure": 84},
                "speed_2": {"flow": 250, "pressure": 38},
                "speed_1": {"flow": 125, "pressure": 9},
            },
            "connections": "Ø192 (Ø208)",
            "diameter": 208,
            "series": "RVS",
            "type": "HRV",
            "power_consumption": {
                "speed_4": 200,  # W
                "speed_3": 100,
                "speed_2": 42,
                "speed_3": 16
            },
            "noise_level": {
                "speed_4": 36.5,  # dB(A)
                "speed_3": 30,
                "speed_2": 24,
                "speed_1": 19
            },
            "efficiency": 0.75  # 75% učinkovitost rekuperacije
        },
        {
            "model": "LGH-80RVS-E",
            "flow_rates": {
                "speed_4": {"flow": 800, "pressure": 170},
                "speed_3": {"flow": 600, "pressure": 96},
                "speed_2": {"flow": 400, "pressure": 43},
                "speed_1": {"flow": 200, "pressure": 11},
            },
            "connections": "Ø242 (Ø258)",
            "diameter": 258,
            "series": "RVS",
            "type": "HRV",
            "power_consumption": {
                "speed_4": 350,  # W
                "speed_3": 180,
                "speed_2": 78,
                "speed_3": 25
            },
            "noise_level": {
                "speed_4": 38,  # dB(A)
                "speed_3": 32,
                "speed_2": 25,
                "speed_1": 20
            },
            "efficiency": 0.75  # 75% učinkovitost rekuperacije
        },
        {
            "model": "LGH-100RVS-E",
            "flow_rates": {
                "speed_4": {"flow": 1000, "pressure": 190},
                "speed_3": {"flow": 750, "pressure": 107},
                "speed_2": {"flow": 500, "pressure": 48},
                "speed_1": {"flow": 250, "pressure": 12},
            },
            "connections": "Ø242 (Ø258)",
            "diameter": 258,
            "series": "RVS",
            "type": "HRV",
            "power_consumption": {
                "speed_4": 420,  # W
                "speed_3": 230,
                "speed_2": 95,
                "speed_3": 32
            },
            "noise_level": {
                "speed_4": 39,  # dB(A)
                "speed_3": 33,
                "speed_2": 26,
                "speed_1": 21
            },
            "efficiency": 0.75  # 75% učinkovitost rekuperacije
        }
    ]
}

def get_all_series():
    """Vraća sve dostupne serije rekuperatora."""
    return list(LOSSNAY_MODELS.keys())

def get_models_by_series(series):
    """Vraća sve modele unutar određene serije."""
    if series in LOSSNAY_MODELS:
        return LOSSNAY_MODELS[series]
    return []

def find_suitable_models(required_flow, required_pressure):
    """
    Pronalazi odgovarajuće modele za zadani protok i tlak.
    
    Args:
        required_flow (float): Potreban protok zraka u m³/h
        required_pressure (float): Potreban vanjski statički tlak u Pa
        
    Returns:
        list: Lista odgovarajućih modela
    """
    suitable_models = []
    
    for series, models in LOSSNAY_MODELS.items():
        for model in models:
            # Provjera za svaku brzinu
            for speed, data in model["flow_rates"].items():
                # Izračun postotka opterećenja
                flow_percentage = required_flow / data["flow"] * 100 if data["flow"] > 0 else float('inf')
                
                # Provjera tlaka
                if isinstance(data["pressure"], dict):  # RVXT modeli imaju različite tlakove za dovod i odsis
                    pressure_ok = (data["pressure"]["supply"] >= required_pressure)
                else:
                    pressure_ok = (data["pressure"] >= required_pressure)
                
                # Ako model zadovoljava i protok i tlak
                if flow_percentage <= 100 and pressure_ok:
                    suitable_models.append({
                        "model": model["model"],
                        "series": model["series"],
                        "flow_capacity": data["flow"],
                        "load_percentage": flow_percentage,
                        "max_pressure": data["pressure"],
                        "speed": speed,
                        "connections": model["connections"],
                        "diameter": model["diameter"],
                        "efficiency": model["efficiency"],
                        "power": model["power_consumption"][speed],
                        "noise": model["noise_level"][speed]
                    })
                    break  # Našli smo odgovarajuću brzinu, idemo na sljedeći model
    
    # Sortiranje prema postotku opterećenja (preferiramo modele koji rade bliže punom kapacitetu)
    return sorted(suitable_models, key=lambda x: -x["load_percentage"])

def get_model_by_name(model_name):
    """
    Dohvaća detalje modela prema njegovom imenu.
    
    Args:
        model_name (str): Ime modela (npr. "LGH-50RVX3-E")
        
    Returns:
        dict: Detalji modela ili None ako model nije pronađen
    """
    for series, models in LOSSNAY_MODELS.items():
        for model in models:
            if model["model"] == model_name:
                return model
    return None