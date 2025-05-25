# modules/thermal/ventilation/ventilation_recovery/branching.py

def initialize_branch_structure():
    """
    Inicijalizira strukturu za grananje kanala.
    
    Returns:
        dict: Osnovna struktura za grananje
    """
    return {
        "fresh_air": {
            "sections": []
        },
        "supply": {
            "sections": [],
            "branches": []
        },
        "extract": {
            "sections": [],
            "branches": []
        },
        "exhaust": {
            "sections": []
        }
    }

def add_main_section(branch_structure, system_type, section_data):
    """
    Dodaje glavnu dionicu u strukturu grananja.
    
    Args:
        branch_structure (dict): Struktura grananja
        system_type (str): Tip sustava ("fresh_air", "supply", "extract", "exhaust")
        section_data (dict): Podaci o dionici
        
    Returns:
        dict: Ažurirana struktura grananja
    """
    if system_type not in branch_structure:
        raise ValueError(f"Nepoznati tip sustava: {system_type}")
    
    branch_structure[system_type]["sections"].append(section_data)
    return branch_structure

def add_branch(branch_structure, system_type, branch_data):
    """
    Dodaje granu u strukturu grananja.
    
    Args:
        branch_structure (dict): Struktura grananja
        system_type (str): Tip sustava ("supply", "extract")
        branch_data (dict): Podaci o grani
        
    Returns:
        dict: Ažurirana struktura grananja
    """
    if system_type not in ["supply", "extract"]:
        raise ValueError("Grane se mogu dodavati samo u tlačni ili odsisni sustav")
    
    branch_structure[system_type]["branches"].append(branch_data)
    return branch_structure

def distribute_flow_evenly(total_flow, n_branches):
    """
    Ravnomjerno raspoređuje protok na sve grane.
    
    Args:
        total_flow (float): Ukupni protok u m³/h
        n_branches (int): Broj grana
        
    Returns:
        list: Lista s protocima po granama
    """
    if n_branches <= 0:
        return []
    
    flow_per_branch = total_flow / n_branches
    return [flow_per_branch] * n_branches

def calculate_flow_distribution(total_flow, distribution_factors):
    """
    Izračunava raspodjelu protoka prema zadanim faktorima.
    
    Args:
        total_flow (float): Ukupni protok u m³/h
        distribution_factors (list): Lista faktora raspodjele (suma treba biti 1.0)
        
    Returns:
        list: Lista s protocima po granama
    """
    if not distribution_factors:
        return []
    
    # Normalizacija faktora ako suma nije točno 1.0
    factor_sum = sum(distribution_factors)
    if factor_sum <= 0:
        return [0] * len(distribution_factors)
    
    normalized_factors = [f / factor_sum for f in distribution_factors]
    
    # Izračun protoka po granama
    flows = [total_flow * f for f in normalized_factors]
    
    return flows

def get_critical_path(branch_structure):
    """
    Pronalazi kritičnu putanju s najvećim padom tlaka.
    
    Args:
        branch_structure (dict): Struktura grananja s dionicama i granama
        
    Returns:
        tuple: (kritična putanja, ukupni pad tlaka)
    """
    max_pressure_drop = 0
    critical_path = []
    
    # Prolazak kroz sve tipove sustava
    for system_type, system_data in branch_structure.items():
        # Pad tlaka glavne dionice
        main_drop = sum(s.get("pressure_drop", {}).get("total", 0) for s in system_data.get("sections", []))
        
        # Ako sustav ima grane
        if "branches" in system_data and system_data["branches"]:
            for i, branch in enumerate(system_data["branches"]):
                branch_drop = sum(s.get("pressure_drop", {}).get("total", 0) for s in branch.get("sections", []))
                total_drop = main_drop + branch_drop
                
                if total_drop > max_pressure_drop:
                    max_pressure_drop = total_drop
                    critical_path = {
                        "system": system_type,
                        "main_sections": system_data["sections"],
                        "branch_index": i,
                        "branch_sections": branch.get("sections", [])
                    }
        else:
            # Ako sustav nema grane, samo glavna dionica
            if main_drop > max_pressure_drop:
                max_pressure_drop = main_drop
                critical_path = {
                    "system": system_type,
                    "main_sections": system_data["sections"],
                    "branch_index": None,
                    "branch_sections": []
                }
    
    return critical_path, max_pressure_drop