"""
UI komponente za unos osnovnih parametara.
"""
import streamlit as st
from ...common.constants import FIRE_LOAD_CATEGORIES
from ..constants import FIRE_LOAD_FLOW_TABLE

def render_basic_params(calculator):
    """Renderira dio sučelja za unos osnovnih parametara."""
    st.subheader("Parametri tlaka i požarnog opterećenja")
    
    # Tlak na priključku
    st.number_input(
        "Raspoloživi tlak na mjestu priključka [bar]",
        min_value=0.0, max_value=10.0, value=4.5, step=0.1,
        key="inlet_pressure",
        help="Osigurani tlak na mjestu priključenja hidrantske mreže",
        on_change=calculator.update_calculation
    )
    
    # Specifično požarno opterećenje
    fire_load = st.slider(
        "Specifično požarno opterećenje [MJ/m²]",
        min_value=100, max_value=2500, value=500, step=50,
        key="fire_load",
        on_change=calculator.update_calculation
    )
    
    # Automatski izračun protoka po hidrantu prema tablici
    flow_per_hydrant = FIRE_LOAD_FLOW_TABLE.get_flow_for_load(fire_load)
    
    # Prikaz protoka s infoboxom
    st.info(f"📊 Potrebna protočna količina vode po hidrantu: **{flow_per_hydrant} l/min**")
    
    # Određivanje kategorije požarnog opterećenja
    category = determine_fire_load_category(fire_load)
    st.markdown(f"**Kategorija požarnog opterećenja:** {category}")
    
    # Broj etaža i hidranata
    col1, col2 = st.columns(2)
    with col1:
        st.number_input(
            "Broj etaža",
            min_value=1, max_value=50, value=3, step=1,
            key="floor_count",
            on_change=calculator.update_calculation
        )
    
    with col2:
        st.number_input(
            "Broj hidranata po etaži",
            min_value=1, max_value=20, value=3, step=1,
            key="hydrants_per_floor",
            on_change=calculator.update_calculation
        )
    
    # Izračun ukupnog broja hidranata
    total_hydrants = st.session_state.floor_count * st.session_state.hydrants_per_floor
    st.markdown(f"**Ukupan broj hidranata u objektu:** {total_hydrants}")
    
    # Odabir broja istovremeno korištenih hidranata
    max_simultaneous = min(total_hydrants, 5)  # Ograničimo na razuman broj
    st.select_slider(
        "Broj istovremeno korištenih hidranata za dimenzioniranje",
        options=list(range(1, max_simultaneous + 1)),
        value=min(2, max_simultaneous),
        key="simultaneous_hydrants",
        on_change=calculator.update_calculation
    )
    
    # Izračun ukupnog protoka
    total_flow_l_min = flow_per_hydrant * st.session_state.simultaneous_hydrants
    total_flow_l_s = total_flow_l_min / 60
    
    # Prikaz ukupnog protoka
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Ukupni potrebni protok",
            value=f"{total_flow_l_min} l/min",
            delta=f"{total_flow_l_s:.2f} l/s",
            delta_color="normal"
        )

def determine_fire_load_category(fire_load):
    """Određuje kategoriju požarnog opterećenja prema vrijednosti."""
    for category, (min_val, max_val) in FIRE_LOAD_CATEGORIES.items():
        if min_val <= fire_load < max_val:
            return category.upper()
    return "VISOKO"  # Default ako nema podudaranja