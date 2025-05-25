"""
Pomoćne funkcije za kalkulator podnog grijanja u Streamlit okolini.
"""

import streamlit as st
import pandas as pd
import math
from datetime import datetime
from modules.thermal.heating.floor_heating.constants import ROOM_TYPES, FLOOR_COVERINGS, MANIFOLD_TYPES, FLOOR_NAMES, CONNECTION_PIPE_DATA, PIPE_DATA

def format_number(value, decimal_places=2):
    """
    Formatira broj za prikaz.
    
    Args:
        value: Broj za formatiranje
        decimal_places: Broj decimalnih mjesta
        
    Returns:
        Formatirani string
    """
    if isinstance(value, (int, float)):
        return f"{value:.{decimal_places}f}"
    return str(value)

def get_room_temperature_for_name(room_name):
    """
    Vraća preporučenu temperaturu za tip prostorije.
    
    Args:
        room_name: Naziv prostorije
        
    Returns:
        Preporučena temperatura u °C
    """
    for temp, rooms in ROOM_TYPES.items():
        if room_name in rooms:
            return temp
    return 22  # Standardna temperatura ako nije pronađena

def get_r_lambda_for_covering_index(covering_index):
    """
    Vraća R_lambda vrijednost za indeks podne obloge.
    
    Args:
        covering_index: Indeks podne obloge
        
    Returns:
        R_lambda vrijednost
    """
    if 0 <= covering_index < len(FLOOR_COVERINGS):
        return FLOOR_COVERINGS[covering_index]["r_lambda"]
    return 0.00  # Standardna vrijednost ako nije pronađena

def create_styled_dataframe(data, highlight_cols=None):
    """
    Kreira stiliziranu tablicu rezultata za Streamlit.
    
    Args:
        data: Lista rječnika s podacima
        highlight_cols: Lista stupaca za isticanje
        
    Returns:
        Pandas DataFrame s stilovima
    """
    df = pd.DataFrame(data)
    
    # Primijeni stil na DataFrame
    if highlight_cols:
        # Primjer funkcije za stiliziranje brojeva i isticanje određenih stupaca
        def highlight_cells(val, col_name):
            color = '#D1F2EB' if col_name in highlight_cols else ''
            return f'background-color: {color}'
        
        styled_df = df.style.format(formatter={
            col: lambda x: f"{x:.2f}" for col in df.select_dtypes(include=['float', 'int']).columns
        }).map(highlight_cells)  # Izmijenjeno sa applymap na map
        
        return styled_df
    
    return df

def get_loop_key(loop_id, param_name):
    """
    Generira ključ za pristup podatku petlje u session state.
    
    Args:
        loop_id: ID petlje
        param_name: Naziv parametra
        
    Returns:
        String ključ za session state
    """
    return f"loop_{loop_id}_{param_name}"

def get_all_room_names():
    """
    Vraća popis svih naziva prostorija.
    
    Returns:
        Lista naziva prostorija
    """
    all_rooms = []
    for rooms in ROOM_TYPES.values():
        all_rooms.extend(rooms)
    return all_rooms

def initialize_loop_defaults(loop_id=1):
    """
    Inicijalizira standardne vrijednosti za novu petlju.
    
    Args:
        loop_id: ID petlje
        
    Returns:
        Rječnik s početnim vrijednostima petlje
    """
    return {
        "id": loop_id,
        "room_name": "Dnevni boravak",
        "room_temperature": 22,
        "area": 20.0,
        "r_lambda": 0.00,
        "pipe_spacing": 15,
        "manifold_distance": 2.0,
        "results": {}
    }

def initialize_new_data_structure():
    """
    Inicijalizira novu hijerarhijsku strukturu podataka za proračun podnog grijanja.
    
    Returns:
        Rječnik s početnim vrijednostima hijerarhijske strukture
    """
    return {
        "meta": {
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "version": "2.0",
            "calculation_type": "Proračun podnog grijanja"
        },
        "floors": [
            initialize_floor(1)
        ],
        "system_totals": {
            "total_water_volume": 0.0,  # litara
            "total_pipe_length": 0.0,   # metara
            "total_area": 0.0,          # m²
            "total_power": 0.0          # W
        }
    }

def initialize_floor(floor_id=1, name=None):
    """
    Inicijalizira novu etažu.
    
    Args:
        floor_id: ID etaže
        name: Naziv etaže
        
    Returns:
        Rječnik s početnim vrijednostima etaže
    """
    if name is None:
        # Uzmi naziv iz predefiniranih etaža
        if 1 <= floor_id <= len(FLOOR_NAMES):
            name = FLOOR_NAMES[floor_id - 1]
        else:
            name = f"Etaža {floor_id}"
    
    return {
        "id": floor_id,
        "name": name,
        "screed_thickness": 45,
        "manifolds": [
            initialize_manifold(1)
        ]
    }

def initialize_manifold(manifold_id=1, name=None, type="7-krugova"):
    """
    Inicijalizira novi razdjelnik.
    
    Args:
        manifold_id: ID razdjelnika
        name: Naziv razdjelnika
        type: Tip razdjelnika (ključ iz MANIFOLD_TYPES)
        
    Returns:
        Rječnik s početnim vrijednostima razdjelnika
    """
    if name is None:
        name = f"Razdjelnik {manifold_id}"
    
    return {
        "id": manifold_id,
        "name": name,
        "type": type,
        "flow_temperature": 35,
        "delta_t": 5,
        "pipe_diameter": "16x2,0",
        "distance_from_source": 5.0,
        "connection_pipe_diameter": "20x2,0",
        "loops": []
    }

def initialize_loop_in_manifold(loop_id=1):
    """
    Inicijalizira novu petlju za razdjelnik.
    
    Args:
        loop_id: ID petlje
        
    Returns:
        Rječnik s početnim vrijednostima petlje
    """
    return {
        "id": loop_id,
        "room_name": "Dnevni boravak",
        "room_temperature": 22,
        "area": 20.0,
        "r_lambda": 0.00,
        "pipe_spacing": 15,
        "manifold_distance": 2.0,
        "results": {},
        "adjusted_results": {}
    }

def find_floor_by_id(data, floor_id):
    """
    Pronalazi etažu po ID-u.
    
    Args:
        data: Struktura podataka
        floor_id: ID etaže koju tražimo
        
    Returns:
        Rječnik etaže ili None ako nije pronađena
    """
    for floor in data.get("floors", []):
        if floor.get("id") == floor_id:
            return floor
    return None

def find_manifold_by_id(floor, manifold_id):
    """
    Pronalazi razdjelnik po ID-u.
    
    Args:
        floor: Struktura podataka etaže
        manifold_id: ID razdjelnika koji tražimo
        
    Returns:
        Rječnik razdjelnika ili None ako nije pronađen
    """
    for manifold in floor.get("manifolds", []):
        if manifold.get("id") == manifold_id:
            return manifold
    return None

def find_loop_by_id(manifold, loop_id):
    """
    Pronalazi petlju po ID-u.
    
    Args:
        manifold: Struktura podataka razdjelnika
        loop_id: ID petlje koju tražimo
        
    Returns:
        Rječnik petlje ili None ako nije pronađena
    """
    for loop in manifold.get("loops", []):
        if loop.get("id") == loop_id:
            return loop
    return None

def generate_new_floor_id(data):
    """
    Generira novi jedinstveni ID za etažu.
    
    Args:
        data: Struktura podataka
        
    Returns:
        Novi ID etaže
    """
    if not data.get("floors"):
        return 1
    return max(floor.get("id", 0) for floor in data["floors"]) + 1

def generate_new_manifold_id(floor):
    """
    Generira novi jedinstveni ID za razdjelnik.
    
    Args:
        floor: Struktura podataka etaže
        
    Returns:
        Novi ID razdjelnika
    """
    if not floor.get("manifolds"):
        return 1
    return max(manifold.get("id", 0) for manifold in floor["manifolds"]) + 1

def generate_new_loop_id(manifold):
    """
    Generira novi jedinstveni ID za petlju.
    
    Args:
        manifold: Struktura podataka razdjelnika
        
    Returns:
        Novi ID petlje
    """
    if not manifold.get("loops"):
        return 1
    return max(loop.get("id", 0) for loop in manifold["loops"]) + 1

def calculate_water_volume_in_pipes(pipe_diameter, pipe_length):
    """
    Izračunava volumen vode u cijevima.
    
    Args:
        pipe_diameter: Promjer cijevi (ključ iz PIPE_DATA)
        pipe_length: Duljina cijevi u metrima
        
    Returns:
        Volumen vode u litrama
    """
    if pipe_diameter in PIPE_DATA:
        return PIPE_DATA[pipe_diameter]["volume_per_meter"] * pipe_length
    return 0.0

def calculate_water_volume_in_connection_pipes(pipe_diameter, pipe_length):
    """
    Izračunava volumen vode u spojnim cijevima.
    
    Args:
        pipe_diameter: Promjer spojnih cijevi (ključ iz CONNECTION_PIPE_DATA)
        pipe_length: Duljina cijevi u metrima
        
    Returns:
        Volumen vode u litrama
    """
    if pipe_diameter in CONNECTION_PIPE_DATA:
        return CONNECTION_PIPE_DATA[pipe_diameter]["volume_per_meter"] * pipe_length
    return 0.0

def calculate_water_volume_in_manifold(manifold_type):
    """
    Vraća volumen vode u razdjelniku.
    
    Args:
        manifold_type: Tip razdjelnika (ključ iz MANIFOLD_TYPES)
        
    Returns:
        Volumen vode u litrama
    """
    if manifold_type in MANIFOLD_TYPES:
        return MANIFOLD_TYPES[manifold_type]["volume"]
    return 0.5  # Standardni volumen ako tip nije poznat

def apply_custom_styles():
    """
    Primjenjuje prilagođene CSS stilove za poboljšanje izgleda kalkulatora.
    """
    st.markdown("""
    <style>
    /* Stilovi za zaglavlja sekcija */
    .section-header {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1E88E5;
        border-bottom: 1px solid #eaeaea;
        padding-bottom: 3px;
    }
    
    /* Stilovi za kartice petlji */
    .loop-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Stilovi za kartice etaža */
    .floor-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1.5rem;
        background-color: #f5f9ff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Stilovi za kartice razdjelnika */
    .manifold-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 0.75rem;
        margin: 0.75rem 0;
        background-color: #f9fff5;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Stilovi za istaknute vrijednosti */
    .highlight-value {
        font-weight: bold;
        color: #2E7D32;
    }
    
    /* Stilovi za upozorenja */
    .warning-text {
        color: #FFA000;
        font-weight: bold;
    }
    
    /* Stilovi za rezultate */
    .results-container {
        margin-top: 1rem;
        padding: 0.5rem;
        border-top: 1px solid #eee;
    }
    
    /* Stilovi za tablice rezultata */
    .results-table {
        width: 100%;
        font-size: 0.9em;
        border-collapse: collapse;
    }
    
    .results-table td, .results-table th {
        padding: 4px;
    }
    
    .results-table th {
        background-color: #f1f1f1;
    }
    
    .adjusted-value {
        color: #0078ff;
        font-weight: 500;
    }
    
    /* Stilovi za pomicanje redoslijeda */
    .move-button {
        padding: 0.25rem 0.5rem;
        margin: 0 0.1rem;
        font-size: 0.8em;
    }
    </style>
    """, unsafe_allow_html=True)

def ensure_callback_execution(key, operation=None):
    """
    Osigurava pravilno izvršavanje callback funkcija kod interakcije s UI elementima.
    
    Args:
        key: Jedinstveni ključ elementa
        operation: Funkcija koja se izvršava (npr. lambda za promjenu stanja)
        
    Returns:
        Boolean koji označava je li došlo do promjene
    """
    # Pratimo zadnji klik/promjenu za svaki element
    if "last_element_change" not in st.session_state:
        st.session_state.last_element_change = {}
    
    # Ako postoji operacija, izvrši je
    if operation:
        operation()
    
    # Generiramo jedinstveni ID za ovu interakciju
    import time
    current_time = time.time()
    
    # Provjerimo je li ovo nova interakcija s elementom
    is_new_interaction = False
    if key not in st.session_state.last_element_change:
        is_new_interaction = True
    elif current_time - st.session_state.last_element_change[key] > 0.1:  # 100ms buffer
        is_new_interaction = True
    
    # Zapamtimo vrijeme interakcije
    st.session_state.last_element_change[key] = current_time
    
    return is_new_interaction

def calculate_system_totals(data):
    """
    Izračunava ukupne podatke sustava.
    
    Args:
        data: Struktura podataka s etažama, razdjelnicima i petljama
        
    Returns:
        Rječnik s ukupnim vrijednostima
    """
    total_water_volume = 0.0
    total_pipe_length = 0.0
    total_area = 0.0
    total_power = 0.0
    
    # Prođi kroz sve etaže, razdjelnike i petlje
    for floor in data.get("floors", []):
        for manifold in floor.get("manifolds", []):
            # Dodaj volumen vode u razdjelniku
            total_water_volume += calculate_water_volume_in_manifold(manifold.get("type", "7-krugova"))
            
            # Dodaj volumen vode u spojnim cijevima
            connection_pipe_length = manifold.get("distance_from_source", 0) * 2  # Polaz i povrat
            connection_volume = calculate_water_volume_in_connection_pipes(
                manifold.get("connection_pipe_diameter", "20x2,0"), 
                connection_pipe_length
            )
            total_water_volume += connection_volume
            
            # Dodaj podatke iz petlji
            for loop in manifold.get("loops", []):
                # Provjeri postoje li podešeni rezultati
                results = loop.get("adjusted_results", {}) or loop.get("results", {})
                if results:
                    pipe_length = results.get("pipe_length", 0)
                    heat_load = results.get("heat_load", 0)
                    area = loop.get("area", 0)
                    
                    total_pipe_length += pipe_length
                    total_area += area
                    total_power += heat_load
                    
                    # Dodaj volumen vode u petlji
                    loop_water_volume = calculate_water_volume_in_pipes(
                        manifold.get("pipe_diameter", "16x2,0"), 
                        pipe_length
                    )
                    total_water_volume += loop_water_volume
    
    return {
        "total_water_volume": total_water_volume,
        "total_pipe_length": total_pipe_length,
        "total_area": total_area,
        "total_power": total_power
    }

def migrate_old_to_new_structure(old_data):
    """
    Migrira podatke iz stare strukture u novu hijerarhijsku strukturu.
    
    Args:
        old_data: Stara struktura podataka
        
    Returns:
        Nova struktura podataka
    """
    new_data = initialize_new_data_structure()
    
    # Zadržavamo meta podatke ako postoje
    if "meta" in old_data:
        new_data["meta"] = old_data["meta"]
        new_data["meta"]["version"] = "2.0"  # Postavi novu verziju
    
    # Uzmi jednu etažu, primarna etaža je prizemlje
    floor = new_data["floors"][0]
    floor["name"] = "Prizemlje"
    
    # Kopiraj debljinu estriha iz zajedničkih parametara
    if "common_params" in old_data and "screed_thickness" in old_data["common_params"]:
        floor["screed_thickness"] = old_data["common_params"]["screed_thickness"]
    
    # Uzmi jedan razdjelnik
    if not floor["manifolds"]:
        floor["manifolds"].append(initialize_manifold(1))
    manifold = floor["manifolds"][0]
    
    # Kopiraj zajedničke parametre u razdjelnik
    if "common_params" in old_data:
        common_params = old_data["common_params"]
        manifold["flow_temperature"] = common_params.get("flow_temperature", 35)
        manifold["delta_t"] = common_params.get("delta_t", 5)
        manifold["pipe_diameter"] = common_params.get("pipe_diameter", "16x2,0")
    
    # Kopiraj petlje iz stare strukture
    for old_loop in old_data.get("loops", []):
        new_loop = initialize_loop_in_manifold(old_loop.get("id", 1))
        
        # Kopiraj podatke petlje
        for key in ["id", "room_name", "room_temperature", "area", "r_lambda", 
                    "pipe_spacing", "manifold_distance", "results", "adjusted_results"]:
            if key in old_loop:
                new_loop[key] = old_loop[key]
        
        manifold["loops"].append(new_loop)
    
    # Izračunaj ukupne podatke sustava
    new_data["system_totals"] = calculate_system_totals(new_data)
    
    return new_data