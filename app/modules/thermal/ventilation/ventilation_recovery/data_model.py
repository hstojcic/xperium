# modules/thermal/ventilation/ventilation_recovery/data_model.py

"""
This module handles the data structure for the ventilation recovery calculator.
It provides functions to initialize and manage the data model.
"""

from modules.thermal.ventilation.ventilation_recovery.branching import initialize_branch_structure


def initialize_data_structure():
    """
    Initializes the data structure for the ventilation recovery calculator.
    
    Returns:
        dict: The default data structure for the calculator.
    """
    return {
        "basic_info": {
            "name": "",
            "location": "",
            "area": 80.0,  # m²
            "height": 3.0,  # m
            "volume": 240.0,  # m³ (automatski izračunato)
            "occupants": 30,
            "temperatures": {"outdoor": -20.0, "indoor": 20.0},
            "ventilation_principle": "balanced"  # dodano za konzistentnost s UI
        },
        "airflow": {
            "calculation_method": "by_people",  # Dodano novo polje za usklađivanje s UI
            "number_of_people": 4,  # Dodano za by_people metodu
            "activity_level": "light",  # Dodano za by_people metodu
            "ventilation_rate_per_person": 30.0,  # Dodano za by_people metodu
            "total_area": 100.0,  # Dodano za by_area metodu
            "ceiling_height": 2.6,  # Dodano za by_area metodu
            "building_type": "office",  # Dodano za by_area metodu
            "ventilation_rate_per_area": 3.0,  # Dodano za by_area metodu
            "rooms": [],  # Dodano za by_room metodu
            "safety_factor": 1.15,  # Dodano za usklađivanje s UI
            "supply_extract_ratio": 1.0,  # Dodano za usklađivanje s UI
            "methods": {
                "by_occupants": {
                    "enabled": True, 
                    "parameters": {
                        "occupants": 30,
                        "quality_category": "II",  # I, II, ili III
                        "specific_flow": 25.2  # automatski po kategoriji
                    }, 
                    "result": 0.0
                },
                "by_area": {
                    "enabled": False, 
                    "parameters": {
                        "area": 80.0,
                        "usage_intensity": "medium",  # low, medium, high
                        "specific_flow": 2.5  # automatski po intenzitetu
                    }, 
                    "result": 0.0
                },
                "by_thermal_load": {
                    "enabled": False, 
                    "parameters": {
                        "thermal_load": 5000.0,  # W
                        "delta_t": "medium",  # small, medium, large
                        "delta_t_value": 5.0  # K, automatski po delta_t
                    }, 
                    "result": 0.0
                },
                "by_air_changes": {
                    "enabled": False, 
                    "parameters": {
                        "volume": 240.0,
                        "ach_rate": "medium",  # low, medium, high
                        "ach_value": 8.0  # automatski po ach_rate
                    }, 
                    "result": 0.0
                }
            },
            "final_flow": 0.0  # maksimalna vrijednost iz aktivnih metoda
        },
        "ducts": {
            "branch_structure": initialize_branch_structure(),
            "total_pressure_drop": 0.0,  # ukupni pad tlaka sustava
            "critical_path": None  # putanja s najvećim padom tlaka
        },
        "recuperator": {
            "selected_model": "",
            "series": "",
            "speed": "speed_4",  # Brzina 4 (100%)
            "efficiency": 0.75,
            "flow_capacity": 0.0,
            "pressure_capacity": 0.0,
            "load_percentage": 0.0,
            "connections": "",
            "diameter": 0
        },
        "heater": {
            "required_power": 0.0,  # kW
            "temperature_after_recuperator": 0.0,  # °C
            "target_temperature": 2.0,  # °C
            "safety_factor": 1.15,
            "final_power": 0.0,  # kW
            "standard_power": 0.0  # kW
        },
        "energy": {
            "location_type": "continental",  # Dodano za usklađivanje s UI
            "daily_operation": 12,  # Dodano za usklađivanje s UI
            "yearly_operation": 300,  # Dodano za usklađivanje s UI
            "energy_price": 0.15,  # Dodano za usklađivanje s UI
            "electricity_price": 0.18,  # Dodano za usklađivanje s UI
            "annual_savings": 0.0,  # kWh/godina
            "electricity_consumption": 0.0,  # kWh/godina
            "heater_consumption": 0.0,  # kWh/godina
            "total_consumption": 0.0,  # kWh/godina
            "co2_reduction": 0.0,  # kg/godina
            "investment_cost": 5000.0,  # Dodana zadana vrijednost
            "annual_cost_savings": 0.0,
            "payback_period": 0.0  # godina
        }
    }