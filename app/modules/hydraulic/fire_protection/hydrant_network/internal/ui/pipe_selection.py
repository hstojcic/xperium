"""
UI komponente za odabir cijevi.
"""
import streamlit as st
from ...common.pipe_data import PIPE_DATA
from ...common.constants import OPTIMAL_DESIGN_VELOCITY
from ..calculation_utils import calculate_pipe_diameter, calculate_velocity, check_velocity_optimality

def render_pipe_selection(calculator):
    """Renderira dio sučelja za odabir cijevi i prikaz brzina."""
    st.subheader("Odabir cijevi i brzine vode")
    
    # Dobavi podatke o protoku (iz basic_params)
    if "simultaneous_hydrants" not in st.session_state or "fire_load" not in st.session_state:
        st.warning("Molimo najprije unesite osnovne parametre.")
        return
    
    # Izračunaj protok (privremeni izračun za ovu stranicu)
    from ..constants import FIRE_LOAD_FLOW_TABLE
    flow_per_hydrant = FIRE_LOAD_FLOW_TABLE.get_flow_for_load(st.session_state.fire_load)
    total_flow_l_min = flow_per_hydrant * st.session_state.simultaneous_hydrants
    total_flow_l_s = total_flow_l_min / 60
    
    # Izračunaj preporučeni promjer za optimalnu brzinu
    required_diameter_mm = calculate_pipe_diameter(total_flow_l_s, OPTIMAL_DESIGN_VELOCITY)
    recommended_dn = PIPE_DATA.get_standard_diameter(required_diameter_mm)
    
    # Prikaz preporučenog promjera cijevi
    st.success(f"🔧 Preporučeni promjer glavne cijevi: **{recommended_dn}** (za brzinu od {OPTIMAL_DESIGN_VELOCITY} m/s)")
    
    # Prikaz tabele brzina za različite promjere
    st.markdown("### Brzine vode za različite promjere cijevi:")
    
    # Kreiraj tablicu s indikatorima
    pipe_data = []
    for dn in PIPE_DATA.get_all_diameters():
        velocity = calculate_velocity(total_flow_l_s, dn)
        status = check_velocity_optimality(velocity)
        pipe_data.append({
            "dn": dn,
            "velocity": velocity,
            "status": status
        })
    
    # Prikaži tabelu brzina
    cols = st.columns(3)
    
    for i, pipe in enumerate(pipe_data):
        with cols[i % 3]:
            # Odaberi boju na temelju statusa
            if pipe["status"] == "optimalno":
                color = "green"
                icon = "✅"
            elif pipe["status"] == "prihvatljivo":
                color = "orange"
                icon = "⚠️"
            else:  # "neprihvatljivo"
                color = "red"
                icon = "❌"
            
            # Prikaz s bojom i ikonom
            st.markdown(
                f"""
                <div style="padding: 10px; border-radius: 5px; border: 1px solid {color};">
                    <h4 style="color: {color};">{pipe["dn"]} {icon}</h4>
                    <p><b>Brzina:</b> {pipe["velocity"]:.2f} m/s</p>
                    <p><b>Status:</b> <span style="color: {color};">{pipe["status"].upper()}</span></p>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Definicija segmenata cjevovoda
    st.subheader("Definicija segmenata cjevovoda")
    
    # Priključni segment
    st.markdown("#### Priključni segment (od vodomjera)")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input(
            "Duljina horizontalnog cjevovoda [m]",
            min_value=0.0, max_value=100.0, value=10.0, step=1.0,
            key="horizontal_pipe_length",
            on_change=calculator.update_calculation
        )
    
    with col2:
        st.selectbox(
            "Promjer horizontalnog cjevovoda",
            options=PIPE_DATA.get_all_diameters(),
            index=1,  # Default DN 50
            key="horizontal_pipe_diameter",
            on_change=calculator.update_calculation
        )
    
    # Lokalni otpori na horizontalnom cjevovodu
    with st.expander("Lokalni otpori na horizontalnom cjevovodu"):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "Broj koljena 90°",
                min_value=0, value=2, step=1,
                key="horizontal_bends_90",
                on_change=calculator.update_calculation
            )
            st.number_input(
                "Broj T-spojeva (prolaz)",
                min_value=0, value=1, step=1,
                key="horizontal_t_pass",
                on_change=calculator.update_calculation
            )
        with col2:
            st.number_input(
                "Broj ventila",
                min_value=0, value=1, step=1,
                key="horizontal_valves",
                on_change=calculator.update_calculation
            )
            st.number_input(
                "Broj T-spojeva (odvajanje)",
                min_value=0, value=1, step=1,
                key="horizontal_t_branch",
                on_change=calculator.update_calculation
            )
    
    # Usponski vod
    st.markdown("#### Usponski vod")
    st.selectbox(
        "Promjer usponskog voda",
        options=PIPE_DATA.get_all_diameters(),
        index=1,  # Default DN 50
        key="riser_pipe_diameter",
        on_change=calculator.update_calculation
    )
    
    # Lokalni otpori na usponskom vodu
    with st.expander("Lokalni otpori na usponskom vodu"):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "Broj koljena 90°",
                min_value=0, value=2, step=1,
                key="riser_bends_90",
                on_change=calculator.update_calculation
            )
        with col2:
            st.number_input(
                "Broj T-spojeva (odvajanje)",
                min_value=0, value=st.session_state.floor_count, step=1,
                key="riser_t_branch",
                on_change=calculator.update_calculation
            )
    
    # Horizontalni razvod na etaži
    st.markdown("#### Horizontalni razvod na najnepovoljnijoj etaži")
    col1, col2 = st.columns(2)
    with col1:
        st.number_input(
            "Duljina horizontalnog razvoda [m]",
            min_value=0.0, max_value=100.0, value=15.0, step=1.0,
            key="floor_pipe_length",
            on_change=calculator.update_calculation
        )
    
    with col2:
        st.selectbox(
            "Promjer horizontalnog razvoda",
            options=PIPE_DATA.get_all_diameters(),
            index=1,  # Default DN 50
            key="floor_pipe_diameter",
            on_change=calculator.update_calculation
        )
    
    # Lokalni otpori na horizontalnom razvodu etaže
    with st.expander("Lokalni otpori na horizontalnom razvodu etaže"):
        col1, col2 = st.columns(2)
        with col1:
            st.number_input(
                "Broj koljena 90°",
                min_value=0, value=3, step=1,
                key="floor_bends_90",
                on_change=calculator.update_calculation
            )
            st.number_input(
                "Broj T-spojeva (prolaz)",
                min_value=0, value=1, step=1,
                key="floor_t_pass",
                on_change=calculator.update_calculation
            )
        with col2:
            st.number_input(
                "Broj T-spojeva (odvajanje)",
                min_value=0, value=1, step=1,
                key="floor_t_branch",
                on_change=calculator.update_calculation
            )
            st.number_input(
                "Broj ventila",
                min_value=0, value=1, step=1,
                key="floor_valves",
                on_change=calculator.update_calculation
            )