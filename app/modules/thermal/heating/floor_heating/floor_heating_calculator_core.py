import streamlit as st
import math
from modules.thermal.heating.floor_heating.constants import *
from modules.thermal.heating.floor_heating.kh_values import KH_VALUES
from modules.thermal.heating.floor_heating.utils import *

class FloorHeatingCalculatorCore:
    """Core calculation component for floor heating."""
    
    def __init__(self):
        """Initialize the calculator core."""
        pass
    
    def get_kh_value(self, pipe_diameter, r_lambda, pipe_spacing, screed_thickness):
        """Retrieves KH value from tables."""
        try:
            # KH values are organized by pipe diameter, r_lambda, spacing and screed thickness
            
            # Check if exact value exists
            if (pipe_diameter in KH_VALUES and 
                r_lambda in KH_VALUES[pipe_diameter] and 
                pipe_spacing in KH_VALUES[pipe_diameter][r_lambda] and 
                screed_thickness in KH_VALUES[pipe_diameter][r_lambda][pipe_spacing]):
                
                return KH_VALUES[pipe_diameter][r_lambda][pipe_spacing][screed_thickness]
            
            # If exact value doesn't exist, find closest
            
            # Find closest pipe diameter
            if pipe_diameter not in KH_VALUES:
                available_diameters = list(KH_VALUES.keys())
                pipe_diameter = available_diameters[0]  # Fallback to first available
            
            # Find closest r_lambda
            available_r_lambdas = list(KH_VALUES[pipe_diameter].keys())
            nearest_r_lambda = min(available_r_lambdas, key=lambda x: abs(x - r_lambda))
            
            # Find closest pipe spacing
            available_spacings = list(KH_VALUES[pipe_diameter][nearest_r_lambda].keys())
            nearest_spacing = min(available_spacings, key=lambda x: abs(x - pipe_spacing))
            
            # Find closest screed thickness
            available_thicknesses = list(KH_VALUES[pipe_diameter][nearest_r_lambda][nearest_spacing].keys())
            nearest_thickness = min(available_thicknesses, key=lambda x: abs(x - screed_thickness))
            
            # Get KH value
            return KH_VALUES[pipe_diameter][nearest_r_lambda][nearest_spacing][nearest_thickness]
            
        except Exception as e:
            st.error(f"Problem retrieving KH value: {str(e)}")
            return 4.0  # Fallback value
    
    def calculate_pressure_drop(self, flow_rate_kg_h, pipe_diameter, pipe_length, water_temperature, pipe_spacing, pipe_roughness=0.0015):
        """Calculates pressure drop in pipe."""
        try:
            # Convert pipe diameter to inner diameter in meters
            inner_diameter = 0.0
            
            # First try to get from PIPE_DATA if available
            try:
                if pipe_diameter in PIPE_DATA:
                    inner_diameter = PIPE_DATA[pipe_diameter]["inner_diameter"] / 1000.0  # mm -> m
                else:
                    # Fallback to extracting from string
                    # Format "14x2,0" - first number is outer diameter, second is wall thickness
                    parts = pipe_diameter.replace(',', '.').split('x')
                    outer_diameter = float(parts[0])
                    wall_thickness = float(parts[1])
                    inner_diameter = (outer_diameter - 2 * wall_thickness) / 1000.0  # mm -> m
            except Exception:
                # If all fails, use standard value
                inner_diameter = 0.012  # 12mm = 0.012m is standard value
            
            # Calculate water density and viscosity based on temperature
            water_density = 1000.1 - 0.0864 * water_temperature  # kg/m³
            water_viscosity = (1.777 - 0.0264 * water_temperature) * 1e-3  # Pa·s
            
            # Convert flow rate from kg/h to m³/s
            flow_rate_m3s = flow_rate_kg_h / 3600 / water_density
            
            # Calculate water velocity
            pipe_cross_section = math.pi * (inner_diameter ** 2) / 4
            water_velocity = flow_rate_m3s / pipe_cross_section if pipe_cross_section > 0 else 0
            
            # Check if flow rate is too small for meaningful calculation
            if flow_rate_kg_h < 1 or water_velocity < 0.001:
                return {
                    "pressure_drop_total": 0,
                    "pressure_drop_linear": 0,
                    "pressure_drop_local": 0,
                    "water_velocity": water_velocity,
                    "reynolds": 0,
                    "friction_factor": 0,
                    "num_bends": 0
                }
            
            # Calculate Reynolds number
            reynolds = (water_density * water_velocity * inner_diameter) / water_viscosity if water_viscosity > 0 else 0
            
            # Calculate friction factor (Colebrook-White equation)
            # Use iterative method
            friction_factor = 0.02  # Initial guess
            
            if reynolds > 0:
                for _ in range(20):
                    try:
                        # Colebrook-White equation for friction factor
                        cw_term = -2 * math.log10(
                            (pipe_roughness / (3.7 * inner_diameter)) + 
                            (2.51 / (reynolds * math.sqrt(friction_factor)))
                        )
                        new_factor = 1 / (cw_term ** 2)
                        
                        # Check convergence
                        if abs(friction_factor - new_factor) < 1e-6:
                            break
                            
                        friction_factor = new_factor
                    except (ValueError, ZeroDivisionError):
                        break
            
            # Calculate linear pressure drop (Darcy-Weisbach equation)
            pressure_drop_linear = friction_factor * (pipe_length / inner_diameter) * (water_density * water_velocity ** 2) / 2
            
            # Estimate local losses
            k_inlet = 0.5  # Loss coefficient for loop inlet
            k_outlet = 1.0  # Loss coefficient for loop outlet
            k_bends = 0.2   # Loss coefficient per bend
            
            # Estimate number of bends
            num_bends = int(pipe_length / (2 * pipe_spacing / 100))
            
            # Calculate local pressure drop
            pressure_drop_local = (k_inlet + k_outlet + num_bends * k_bends) * (water_density * water_velocity ** 2) / 2
            
            # Total pressure drop (kPa)
            pressure_drop_total = (pressure_drop_linear + pressure_drop_local) / 1000
            pressure_drop_linear_kpa = pressure_drop_linear / 1000
            pressure_drop_local_kpa = pressure_drop_local / 1000
            
            return {
                "pressure_drop_total": pressure_drop_total,
                "pressure_drop_linear": pressure_drop_linear_kpa,
                "pressure_drop_local": pressure_drop_local_kpa,
                "water_velocity": water_velocity,
                "reynolds": reynolds,
                "friction_factor": friction_factor,
                "num_bends": num_bends
            }
            
        except Exception as e:
            st.error(f"Problem calculating pressure drop: {str(e)}")
            return {
                "pressure_drop_total": 0,
                "pressure_drop_linear": 0,
                "pressure_drop_local": 0,
                "water_velocity": 0,
                "reynolds": 0,
                "friction_factor": 0,
                "num_bends": 0
            }
    
    def calculate_single_loop(self, loop, common_params):
        """Calculates parameters for a single loop."""
        try:
            # Validate required parameters first
            if "area" not in loop or loop["area"] is None or loop["area"] <= 0:
                # Removed the warning message that was showing at the bottom of the page
                return {}
                
            if "pipe_spacing" not in loop or loop["pipe_spacing"] is None:
                st.warning(f"Petlja {loop.get('id')}: Nedostaje razmak cijevi.")
                return {}
                
            if "manifold_distance" not in loop or loop["manifold_distance"] is None:
                st.warning(f"Petlja {loop.get('id')}: Nedostaje udaljenost razdjelnika.")
                return {}
            
            # Get required values
            flow_temperature = common_params["flow_temperature"]
            delta_t = common_params["delta_t"]
            pipe_diameter = common_params["pipe_diameter"]
            screed_thickness = common_params["screed_thickness"]
            
            room_temperature = loop["room_temperature"]
            area = loop["area"]
            r_lambda = loop["r_lambda"]
            pipe_spacing = loop["pipe_spacing"]
            manifold_distance = loop["manifold_distance"]
            
            # Calculate return temperature
            return_temperature = flow_temperature - delta_t
            
            # Calculate KH coefficient
            kh_value = self.get_kh_value(pipe_diameter, r_lambda, pipe_spacing, screed_thickness)
            
            # Calculate mean heating excess temperature
            try:
                mean_heating_excess_temp = (flow_temperature - return_temperature) / (
                    math.log((flow_temperature - room_temperature) / (return_temperature - room_temperature))
                )
            except (ValueError, ZeroDivisionError):
                # Fallback if logarithm calculation is impossible
                mean_heating_excess_temp = flow_temperature - room_temperature
            
            # Calculate heat flux (W/m²)
            heat_flux = kh_value * mean_heating_excess_temp
            
            # Calculate heat load (W)
            heat_load = area * heat_flux
            
            # Calculate pipe length (m)
            pipe_length = area / (pipe_spacing / 100) + 2 * manifold_distance
            
            # Calculate recommended number of loops
            max_pipe_length = 0
            try:
                # Try getting from PIPE_DATA first
                if pipe_diameter in PIPE_DATA:
                    max_pipe_length = PIPE_DATA[pipe_diameter]["max_length"]
                else:
                    # Fallback to PIPE_DIAMETERS if available
                    max_pipe_length = PIPE_DIAMETERS.get(pipe_diameter, 100)
            except Exception:
                max_pipe_length = 100  # Default fallback
                
            if pipe_length > max_pipe_length:
                recommended_loops = math.ceil(pipe_length / max_pipe_length)
                length_per_loop = pipe_length / recommended_loops
                area_per_loop = area / recommended_loops
            else:
                recommended_loops = 1
                length_per_loop = pipe_length
                area_per_loop = area
            
            # Calculate water flow rate (kg/h)
            if delta_t > 0:
                flow_rate_kg_h = (heat_load * 3600) / (SPECIFIC_HEAT_WATER * delta_t)
            else:
                flow_rate_kg_h = 0
            flow_rate_l_min = flow_rate_kg_h / 60
            
            # Calculate floor surface temperature
            floor_surface_temp = room_temperature + (heat_flux / ALPHA_I)
            
            # Calculate pressure drop
            pressure_drop_results = self.calculate_pressure_drop(
                flow_rate_kg_h, pipe_diameter, pipe_length, (flow_temperature + return_temperature) / 2, pipe_spacing
            )
            
            # Maximum floor temperature
            max_floor_temp = MAX_FLOOR_TEMP.get(room_temperature, 29)
            
            # Return calculation results
            return {
                "kh_value": kh_value,
                "mean_heating_excess_temp": mean_heating_excess_temp,
                "heat_flux": heat_flux,
                "heat_load": heat_load,
                "pipe_length": pipe_length,
                "recommended_loops": recommended_loops,
                "length_per_loop": length_per_loop,
                "area_per_loop": area_per_loop,
                "flow_rate_kg_h": flow_rate_kg_h,
                "flow_rate_l_min": flow_rate_l_min,
                "floor_surface_temp": floor_surface_temp,
                "max_floor_temp": max_floor_temp,
                "pressure_drop": pressure_drop_results["pressure_drop_total"],
                "water_velocity": pressure_drop_results["water_velocity"],
                "return_temperature": return_temperature,
                "flow_temperature": flow_temperature
            }
            
        except Exception as e:
            st.error(f"Error in calculation: {str(e)}")
            return {}
