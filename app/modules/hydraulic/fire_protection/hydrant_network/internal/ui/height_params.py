"""
UI komponente za unos visinskih parametara.
"""
import streamlit as st
from ..calculation_utils import calculate_hydrant_height

def render_height_params(calculator):
    """Renderira dio sučelja za unos visinskih parametara."""
    st.subheader("Referentne visine")
    
    # Tlo kao referentna kota
    st.info("Tlo je referentna kota 0.")
    
    # Osnovni parametri
    col1, col2 = st.columns(2)
    with col1:
        st.number_input(
            "Dubina horizontalnog voda od vodomjera [m]",
            min_value=0.0, max_value=10.0, value=1.0, step=0.1,
            key="pipe_depth",
            on_change=calculator.update_calculation
        )
        
        st.number_input(
            "Visina od tla do poda prve etaže [m]",
            min_value=0.0, max_value=10.0, value=0.5, step=0.1,
            key="ground_to_first_floor",
            on_change=calculator.update_calculation
        )
    
    with col2:
        st.number_input(
            "Standardna visina etaže [m]",
            min_value=2.0, max_value=10.0, value=3.0, step=0.1,
            key="standard_floor_height",
            on_change=calculator.update_calculation
        )
    
    # Prekidač za različite visine etaža
    different_heights = st.checkbox(
        "Etaže imaju različite visine",
        key="different_floor_heights",
        on_change=calculator.update_calculation
    )
    
    # Dinamički prikaz polja za unos visina pojedinih etaža
    if different_heights:
        st.subheader("Visine pojedinačnih etaža")
        
        # Kreiraj dva stupca za bolji raspored
        cols = st.columns(2)
        
        for i in range(1, st.session_state.floor_count + 1):
            key_name = f"floor_height_{i}"
            
            # Osiguraj da postoji u session_state
            if key_name not in st.session_state:
                st.session_state[key_name] = st.session_state.standard_floor_height
            
            # Rasporedi po stupcima
            with cols[i % 2]:
                st.number_input(
                    f"Etaža {i} [m]",
                    min_value=2.0, max_value=10.0, value=st.session_state[key_name], step=0.1,
                    key=key_name,
                    on_change=calculator.update_calculation
                )
    
    # Parametri hidranta
    st.subheader("Pozicija hidranta")
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input(
            "Visina hidranta od poda [m]",
            min_value=0.5, max_value=2.5, value=1.5, step=0.1,
            key="hydrant_height",
            on_change=calculator.update_calculation
        )
    
    with col2:
        st.selectbox(
            "Etaža najnepovoljnijeg hidranta",
            options=list(range(1, st.session_state.floor_count + 1)),
            index=st.session_state.floor_count - 1,  # Default je zadnja etaža
            key="worst_case_floor",
            on_change=calculator.update_calculation
        )
    
    # Izračun i prikaz ukupne visine najnepovoljnijeg hidranta
    # Dohvati podatke za izračun
    pipe_depth = st.session_state.pipe_depth
    ground_to_first = st.session_state.ground_to_first_floor
    standard_height = st.session_state.standard_floor_height
    different_heights_enabled = st.session_state.different_floor_heights
    target_floor = st.session_state.worst_case_floor
    hydrant_height = st.session_state.hydrant_height
    
    # Pripremi rječnik s visinama etaža ako je potrebno
    floor_heights = {}
    if different_heights_enabled:
        for i in range(1, st.session_state.floor_count + 1):
            key = f"floor_height_{i}"
            if key in st.session_state:
                floor_heights[i] = st.session_state[key]
    
    # Izračunaj visinu hidranta
    total_height = calculate_hydrant_height(
        ground_to_first, standard_height, different_heights_enabled, 
        floor_heights, target_floor, hydrant_height
    )
    
    # Izračunaj ukupnu visinsku razliku između točke priključka i hidranta
    total_height_difference = total_height + pipe_depth
    
    # Prikaži informacije o visinama
    st.info(f"📏 Ukupna visina najnepovoljnijeg hidranta od tla: **{total_height:.2f} m**")
    st.info(f"📏 Ukupna visinska razlika (od priključka do hidranta): **{total_height_difference:.2f} m**")