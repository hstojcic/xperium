"""
Modul za podešavanje protoka i preračunavanje parametara podnog grijanja.
Omogućuje simulaciju promjene protoka i računa nove vrijednosti svih parametara.
"""

import math
from modules.thermal.heating.floor_heating.constants import *

class FlowAdjuster:
    """Klasa za podešavanje protoka i preračunavanje parametara podnog grijanja."""
    
    @staticmethod
    def get_adjustment_options():
        """Vraća opcije za podešavanje protoka."""
        return {
            "-50": "Smanji za 50%",
            "-40": "Smanji za 40%",
            "-30": "Smanji za 30%",
            "-20": "Smanji za 20%",
            "-10": "Smanji za 10%",
            "0": "Bez promjene",
            "+10": "Povećaj za 10%",
            "+20": "Povećaj za 20%",
            "+30": "Povećaj za 30%",
            "+40": "Povećaj za 40%",
            "+50": "Povećaj za 50%"
        }
    
    @staticmethod
    def adjust_flow_by_percentage(loop_data, common_params, percentage):
        """Podešava protok prema zadanom postotku i preračunava sve parametre."""
        # Provjeri postoje li rezultati u petlji
        original_results = loop_data.get("results", {})
        if not original_results:
            return {}
        
        try:
            # Konstante
            specificna_toplina_vode = 4190.0  # J/(kg·K)
            
            # Faktor korekcije iz postotka (-50% do +50%)
            faktor_korekcije = 1 + (percentage / 100)
            
            # Priprema ulaznih parametara
            rezultati = {
                'polazna_temp': original_results.get("flow_temperature", common_params.get("flow_temperature", 45)),
                'temp_prostorije': loop_data.get("room_temperature", 22),
                'povrsina': loop_data.get("area", 0),
                'alpha_i': 10.8,  # W/(m²·K)
                'koeficijent_kh': original_results.get("kh_value", 4.0),
                'toplinsko_opterecenje': original_results.get("heat_load", 0),
                'protok_kg_h': original_results.get("flow_rate_kg_h", 0),
                'duljina_cijevi': original_results.get("pipe_length", 0),
                'odabrani_promjer': common_params.get("pipe_diameter", "16x2,0"),
                'razmak_cijevi': loop_data.get("pipe_spacing", 15)
            }
            
            # Inicijalizacija za prvu iteraciju
            orig_protok = rezultati['protok_kg_h']
            novi_protok = orig_protok * faktor_korekcije
            novi_protok_kg_s = novi_protok / 3600  # kg/s
            
            # Izračun inicijalnog delta_t
            delta_t_pocetni = rezultati['toplinsko_opterecenje'] / (novi_protok_kg_s * specificna_toplina_vode)
            
            # Inicijalni izračun temperature povrata
            temp_povrata_pocetni = rezultati['polazna_temp'] - delta_t_pocetni
            
            # Provjera fizikalne valjanosti
            if temp_povrata_pocetni <= rezultati['temp_prostorije']:
                return {
                    "flow_rate_l_min": original_results.get("flow_rate_l_min", 0),
                    "flow_rate_kg_h": original_results.get("flow_rate_kg_h", 0),
                    "adjusted_area": loop_data.get('area', 0),
                    "heat_load": original_results.get("heat_load", 0),
                    "pipe_length": original_results.get("pipe_length", 0),
                    "water_velocity": original_results.get("water_velocity", 0),
                    "pressure_drop": original_results.get("pressure_drop", 0),
                    "heat_flux": original_results.get("heat_flux", 0),
                    "floor_surface_temp": original_results.get("floor_surface_temp", 0),
                    "adjustment_percentage": 0,  # Reset to 0% if not physically possible
                    "warning": "Fizički nemoguća temperatura povrata niža od temperature prostorije."
                }
            
            # Inicijalni izračun logaritamske temperaturne razlike
            koristena_aritmeticka_sredina = False
            try:
                delta_tln_pocetni = (rezultati['polazna_temp'] - temp_povrata_pocetni) / math.log(
                    (rezultati['polazna_temp'] - rezultati['temp_prostorije']) / 
                    (temp_povrata_pocetni - rezultati['temp_prostorije'])
                )
            except (ValueError, ZeroDivisionError):
                # Koristimo aritmetičku sredinu ako logaritamski pristup nije moguć
                delta_tln_pocetni = ((rezultati['polazna_temp'] - rezultati['temp_prostorije']) + 
                                  (temp_povrata_pocetni - rezultati['temp_prostorije'])) / 2
                koristena_aritmeticka_sredina = True
            
            # Inicijalni izračun topline
            trenutna_toplina = rezultati['koeficijent_kh'] * delta_tln_pocetni * rezultati['povrsina']
            
            # Čuvanje povijesti vrijednosti za praćenje konvergencije
            povijest_toplina = [trenutna_toplina]
            nova_toplina = trenutna_toplina  # Inicijalizacija za prvi prolaz
            
            # Postavke iterativnog procesa
            max_iteracija = 20
            tolerancija_rel = 0.001
            relativna_promjena = float('inf')  # Inicijalizacija za ulazak u petlju
            
            # Iterativni proces
            for i in range(max_iteracija):
                # Izračun delta_t na temelju nove topline iz prethodne iteracije
                delta_t = nova_toplina / (novi_protok_kg_s * specificna_toplina_vode)
                
                # Nova temperatura povrata
                nova_temp_povrata = rezultati['polazna_temp'] - delta_t
                
                # Provjera fizikalne valjanosti
                if nova_temp_povrata <= rezultati['temp_prostorije']:
                    return {
                        "flow_rate_l_min": original_results.get("flow_rate_l_min", 0),
                        "flow_rate_kg_h": original_results.get("flow_rate_kg_h", 0),
                        "adjusted_area": loop_data.get('area', 0),
                        "heat_load": original_results.get("heat_load", 0),
                        "pipe_length": original_results.get("pipe_length", 0),
                        "water_velocity": original_results.get("water_velocity", 0),
                        "pressure_drop": original_results.get("pressure_drop", 0),
                        "heat_flux": original_results.get("heat_flux", 0),
                        "floor_surface_temp": original_results.get("floor_surface_temp", 0),
                        "adjustment_percentage": 0,  # Reset to 0% if not physically possible
                        "warning": f"Fizički nemoguća temperatura povrata u iteraciji {i+1}."
                    }
                
                # Nova logaritamska temperaturna razlika
                if abs((rezultati['polazna_temp'] - rezultati['temp_prostorije']) - 
                       (nova_temp_povrata - rezultati['temp_prostorije'])) < 0.01:
                    # Ako su razlike gotovo jednake, LMTD = delta_T
                    delta_tln = rezultati['polazna_temp'] - rezultati['temp_prostorije']
                else:
                    try:
                        delta_tln = (rezultati['polazna_temp'] - nova_temp_povrata) / math.log(
                            (rezultati['polazna_temp'] - rezultati['temp_prostorije']) / 
                            (nova_temp_povrata - rezultati['temp_prostorije'])
                        )
                    except (ValueError, ZeroDivisionError):
                        # Sigurnosni izračun u slučaju numeričkih problema
                        delta_tln = ((rezultati['polazna_temp'] - rezultati['temp_prostorije']) + 
                                  (nova_temp_povrata - rezultati['temp_prostorije'])) / 2
                        koristena_aritmeticka_sredina = True
                
                # Novi toplinski tok s ORIGINALNIM koeficijentom KH
                novi_toplinski_tok = rezultati['koeficijent_kh'] * delta_tln
                
                # Nova toplina
                nova_toplina = novi_toplinski_tok * rezultati['povrsina']
                
                # Provjera konvergencije (relativna promjena)
                relativna_promjena = abs(nova_toplina - trenutna_toplina) / trenutna_toplina
                if relativna_promjena < tolerancija_rel:
                    break
                    
                # Provjera divergencije i prigušenje
                povijest_toplina.append(nova_toplina)
                if i > 5:  # Provjera nakon nekoliko iteracija
                    # Ako je nova vrijednost dalje od pretprošle vrijednosti, primijeni prigušenje
                    if abs(nova_toplina - povijest_toplina[-3]) > abs(povijest_toplina[-2] - povijest_toplina[-3]):
                        # Jače prigušenje za stabilnost
                        trenutna_toplina = 0.7 * trenutna_toplina + 0.3 * nova_toplina
                    else:
                        # Standardno prigušenje
                        trenutna_toplina = 0.5 * trenutna_toplina + 0.5 * nova_toplina
                else:
                    trenutna_toplina = 0.5 * trenutna_toplina + 0.5 * nova_toplina
            
            # Izračun temperature površine poda
            temp_povrsine = rezultati['temp_prostorije'] + (novi_toplinski_tok / rezultati['alpha_i'])
            
            # Izračun pada tlaka
            temperatura_vode = (rezultati['polazna_temp'] + nova_temp_povrata) / 2
            
            pipe_diameter = common_params.get("pipe_diameter", "16x2,0")
            pipe_spacing = loop_data.get("pipe_spacing", 15)
            
            # Preračunaj duljinu cijevi prema novoj površini
            delta_t = common_params.get("delta_t", 5)
            
            # Jednaka toplina kao u originalnom, ali s novim protokom = drugačiji režim rada petlje
            # Nova površina petlje se ne mijenja
            nova_povrsina = rezultati['povrsina']
            
            # Duljina cijevi ostaje ista kao u originalnom izračunu
            nova_duljina_cijevi = rezultati['duljina_cijevi']
            
            # Izračunaj unutarnji promjer cijevi (mm -> m)
            inner_diameter = 0.0
            try:
                if pipe_diameter in PIPE_DATA:
                    inner_diameter = PIPE_DATA[pipe_diameter]["inner_diameter"] / 1000.0
                else:
                    # Fallback na izvlačenje iz stringa
                    parts = pipe_diameter.replace(',', '.').split('x')
                    outer_diameter = float(parts[0])
                    wall_thickness = float(parts[1])
                    inner_diameter = (outer_diameter - 2 * wall_thickness) / 1000.0
            except Exception:
                inner_diameter = 0.012  # 12mm default
            
            # Izračun gustoće i viskoznosti vode
            water_density = 1000.1 - 0.0864 * temperatura_vode  # kg/m³
            water_viscosity = (1.777 - 0.0264 * temperatura_vode) * 1e-3  # Pa·s
            
            # Pretvori protok iz kg/h u m³/s
            flow_rate_m3s = novi_protok / 3600 / water_density
            
            # Izračun brzine vode
            pipe_cross_section = math.pi * (inner_diameter ** 2) / 4
            brzina_vode = flow_rate_m3s / pipe_cross_section if pipe_cross_section > 0 else 0
            
            # Izračun Reynoldsovog broja
            reynolds = (water_density * brzina_vode * inner_diameter) / water_viscosity if water_viscosity > 0 else 0
            
            # Izračun faktora trenja
            pipe_roughness = 0.0015  # mm
            friction_factor = 0.02  # Početna pretpostavka
            
            if reynolds > 0:
                for _ in range(20):
                    try:
                        cw_term = -2 * math.log10(
                            (pipe_roughness / (3.7 * inner_diameter)) + 
                            (2.51 / (reynolds * math.sqrt(friction_factor)))
                        )
                        new_factor = 1 / (cw_term ** 2)
                        
                        if abs(friction_factor - new_factor) < 1e-6:
                            break
                            
                        friction_factor = new_factor
                    except (ValueError, ZeroDivisionError):
                        break
            
            # Izračun linearnog pada tlaka
            pressure_drop_linear = friction_factor * (nova_duljina_cijevi / inner_diameter) * (water_density * brzina_vode ** 2) / 2
            
            # Procjena lokalnih gubitaka
            k_inlet = 0.5
            k_outlet = 1.0
            k_bends = 0.2
            num_bends = int(nova_duljina_cijevi / (2 * pipe_spacing / 100))
            
            pressure_drop_local = (k_inlet + k_outlet + num_bends * k_bends) * (water_density * brzina_vode ** 2) / 2
            
            # Ukupni pad tlaka (kPa)
            pad_tlaka = (pressure_drop_linear + pressure_drop_local) / 1000
            
            # Provjera režima strujanja
            rezim_strujanja = "laminarno" if reynolds < 2300 else "prijelazno" if reynolds < 4000 else "turbulentno"
            
            # Kreiraj rezultate s podešenim protokom
            adjusted_results = {
                "flow_rate_l_min": novi_protok / 60,
                "flow_rate_kg_h": novi_protok,
                "adjusted_area": nova_povrsina,
                "heat_load": nova_toplina,
                "pipe_length": nova_duljina_cijevi,
                "water_velocity": brzina_vode,
                "pressure_drop": pad_tlaka,
                "heat_flux": novi_toplinski_tok,
                "floor_surface_temp": temp_povrsine,
                "adjustment_percentage": percentage,
                "flow_regime": rezim_strujanja,
                "reynolds": reynolds,
                "iterations": i + 1,
                "delta_t": delta_t,
                "return_temperature": nova_temp_povrata
            }
            
            return adjusted_results
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error in adjust_flow_by_percentage: {str(e)}")
            # Return empty results in case of error
            return {}