"""
UI komponente za prikaz rezultata.
"""
import streamlit as st
import pandas as pd
from ...common.constants import MIN_REQUIRED_PRESSURE_BAR

def render_results(calculator):
    """Renderira dio sučelja za prikaz rezultata proračuna."""
    st.header("Rezultati proračuna")
    
    # Dohvati rezultate
    data = st.session_state.internal_hydrant_data
    
    if not "results" in data or not data["results"]:
        st.warning("Unesite sve parametre za izračun.")
        return
    
    # Prikaz osnovnih rezultata
    st.subheader("Osnovni parametri")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Protok po hidrantu",
            f"{data['results']['flow_per_hydrant']} l/min"
        )
    
    with col2:
        st.metric(
            "Ukupni protok",
            f"{data['results']['total_flow_l_min']} l/min",
            f"{data['results']['total_flow_l_s']:.2f} l/s"
        )
    
    with col3:
        st.metric(
            "Broj istovremenih hidranata",
            f"{data['parameters']['simultaneous_hydrants']}"
        )
    
    # Prikaz segmenata cjevovoda i protoka
    st.subheader("Segmenti cjevovoda")
    render_pipe_segments(data)
    
    # Prikaz gubitaka tlaka
    st.subheader("Gubici tlaka")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Linijski gubici",
            f"{data['results']['total_linear_loss']:.2f} bar"
        )
    
    with col2:
        st.metric(
            "Lokalni gubici",
            f"{data['results']['total_local_loss']:.2f} bar"
        )
    
    with col3:
        st.metric(
            "Geodetski gubici",
            f"{data['results']['geodetic_loss']:.2f} bar"
        )
    
    # Prikaz ukupnog gubitka i preostalog tlaka
    st.subheader("Ukupni rezultati")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Ukupni gubitak tlaka",
            f"{data['results']['total_loss']:.2f} bar"
        )
    
    with col2:
        # Razlika od minimalnog potrebnog tlaka
        remaining_pressure = data['results']['remaining_pressure']
        delta = remaining_pressure - MIN_REQUIRED_PRESSURE_BAR
        
        st.metric(
            "Preostali tlak na hidrantu",
            f"{remaining_pressure:.2f} bar",
            f"{delta:.2f} bar",
            delta_color="normal" if delta >= 0 else "inverse"
        )
    
    # Indikator zadovoljenja uvjeta
    if data['results']['meets_requirements']:
        st.success(f"✅ Tlak na hidrantu ({remaining_pressure:.2f} bar) zadovoljava minimalni uvjet od {MIN_REQUIRED_PRESSURE_BAR} bar.")
    else:
        st.error(f"❌ Tlak na hidrantu ({remaining_pressure:.2f} bar) NE zadovoljava minimalni uvjet od {MIN_REQUIRED_PRESSURE_BAR} bar.")
        
        # Predložena rješenja ako uvjet nije zadovoljen
        st.warning("Moguća rješenja:")
        st.markdown("""
        1. Povećanje promjera cijevi u kritičnim dionicama
        2. Ugradnja uređaja za povišenje tlaka
        3. Smanjenje duljine cjevovoda do najnepovoljnijeg hidranta
        4. Osiguranje većeg tlaka na mjestu priključka
        """)
        
        # Dodajemo gumb za iteraciju kada uvjet nije zadovoljen
        st.subheader("Želite li nastaviti s iteracijama?")
        iterate_col1, iterate_col2 = st.columns(2)
        
        with iterate_col1:
            if st.button("Da, nastavi iterirati", key="continue_iterate"):
                st.session_state.internal_hydrant_data["show_iteration_guidance"] = True
                st.rerun()
        
        with iterate_col2:
            if st.button("Ne, završi proračun", key="stop_iterate"):
                st.session_state.internal_hydrant_data["show_iteration_guidance"] = False
                st.info("Proračun završen. Možete ručno prilagoditi parametre u odjeljcima iznad.")
        
        # Prikaz smjernica za iteraciju ako je korisnik odabrao nastavak
        if st.session_state.internal_hydrant_data.get("show_iteration_guidance", False):
            st.subheader("Smjernice za iteraciju")
            st.info("""
            Za poboljšanje rezultata, preporučujemo:
            
            1. **Povećanje promjera cijevi**: Povećajte promjer cijevi u kritičnim dionicama za smanjenje linijskih gubitaka.
               - Trenutni promjer horizontalnog voda: {horizontal_diameter}
               - Trenutni promjer usponskog voda: {riser_diameter}
               - Trenutni promjer etažnog voda: {floor_diameter}
            
            2. **Smanjenje duljine cjevovoda**: Pokušajte optimizirati trasu cjevovoda.
               - Trenutna duljina horizontalnog voda: {horizontal_length:.1f} m
               - Trenutna duljina etažnog voda: {floor_length:.1f} m
            
            3. **Povećanje ulaznog tlaka**: Ako je moguće, povećajte ulazni tlak.
               - Trenutni ulazni tlak: {inlet_pressure:.2f} bar
            """.format(
                horizontal_diameter=data["parameters"]["pipe_diameters"]["horizontal"],
                riser_diameter=data["parameters"]["pipe_diameters"]["riser"],
                floor_diameter=data["parameters"]["pipe_diameters"]["floor"],
                horizontal_length=data["parameters"]["pipe_lengths"]["horizontal"],
                floor_length=data["parameters"]["pipe_lengths"]["floor"],
                inlet_pressure=data["parameters"]["inlet_pressure"]
            ))
    
    # Vizualizacija rezultata
    st.subheader("Vizualizacija rezultata")
    
    # Prikaz grafova protoka i tlaka
    tab1, tab2 = st.tabs(["Protok vode", "Gubici tlaka"])
    
    with tab1:
        render_flow_chart(data)
    
    with tab2:
        render_pressure_chart(data)

def render_pipe_segments(data):
    """Renderira vizualizaciju segmenata cjevovoda s dimenzijama i protocima."""
    # Pripremi podatke za tablicu segmenata cjevovoda
    segments = []
    
    # Horizontalni segment
    horizontal_length = data["parameters"]["pipe_lengths"]["horizontal"]
    horizontal_diameter = data["parameters"]["pipe_diameters"]["horizontal"]
    total_flow = data["results"]["total_flow_l_s"]
    horizontal_velocity = data["results"]["velocities"]["horizontal"]
    horizontal_linear_loss = data["results"]["linear_losses"]["horizontal"]
    horizontal_local_loss = data["results"]["local_losses"]["horizontal"]
    
    segments.append({
        "Segment": "Horizontalni vod",
        "Duljina [m]": f"{horizontal_length:.1f}",
        "Promjer": horizontal_diameter,
        "Protok [l/s]": f"{total_flow:.2f}",
        "Brzina [m/s]": f"{horizontal_velocity:.2f}",
        "Linijski gubici [bar]": f"{horizontal_linear_loss:.2f}",
        "Lokalni gubici [bar]": f"{horizontal_local_loss:.2f}"
    })
    
    # Usponski segment
    riser_height = data["results"]["total_hydrant_height"]
    riser_diameter = data["parameters"]["pipe_diameters"]["riser"]
    riser_velocity = data["results"]["velocities"]["riser"]
    riser_linear_loss = data["results"]["linear_losses"]["riser"]
    riser_local_loss = data["results"]["local_losses"]["riser"]
    
    segments.append({
        "Segment": "Usponski vod",
        "Duljina [m]": f"{riser_height:.1f}",
        "Promjer": riser_diameter,
        "Protok [l/s]": f"{total_flow:.2f}",
        "Brzina [m/s]": f"{riser_velocity:.2f}",
        "Linijski gubici [bar]": f"{riser_linear_loss:.2f}",
        "Lokalni gubici [bar]": f"{riser_local_loss:.2f}"
    })
    
    # Etažni segment
    floor_length = data["parameters"]["pipe_lengths"]["floor"]
    floor_diameter = data["parameters"]["pipe_diameters"]["floor"]
    floor_velocity = data["results"]["velocities"]["floor"]
    floor_linear_loss = data["results"]["linear_losses"]["floor"]
    floor_local_loss = data["results"]["local_losses"]["floor"]
    
    segments.append({
        "Segment": "Etažni vod",
        "Duljina [m]": f"{floor_length:.1f}",
        "Promjer": floor_diameter,
        "Protok [l/s]": f"{total_flow:.2f}",
        "Brzina [m/s]": f"{floor_velocity:.2f}",
        "Linijski gubici [bar]": f"{floor_linear_loss:.2f}",
        "Lokalni gubici [bar]": f"{floor_local_loss:.2f}"
    })
    
    # Prikaži tablicu
    df = pd.DataFrame(segments)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Vizualni prikaz cjevovoda
    st.subheader("Shema cjevovoda")
    
    # Korištenje SVG za vizualni prikaz cjevovoda
    svg_height = 400
    svg_width = 800
    
    # Definiranje pozicija segmenata
    horizontal_x_start = 50
    horizontal_x_end = 250
    riser_x = horizontal_x_end
    riser_y_start = 300
    riser_y_end = 100
    floor_x_start = riser_x
    floor_x_end = 700
    floor_y = riser_y_end
    
    # Boje za segmente
    color_horizontal = "#1f77b4"  # plava
    color_riser = "#ff7f0e"       # narančasta
    color_floor = "#2ca02c"       # zelena
    
    # Generiranje SVG-a
    svg_code = f"""
    <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Horizontalni vod -->
        <line x1="{horizontal_x_start}" y1="{riser_y_start}" x2="{horizontal_x_end}" y2="{riser_y_start}" 
              stroke="{color_horizontal}" stroke-width="10" />
        
        <!-- Usponski vod -->
        <line x1="{riser_x}" y1="{riser_y_start}" x2="{riser_x}" y2="{riser_y_end}" 
              stroke="{color_riser}" stroke-width="10" />
        
        <!-- Etažni vod -->
        <line x1="{floor_x_start}" y1="{floor_y}" x2="{floor_x_end}" y2="{floor_y}" 
              stroke="{color_floor}" stroke-width="10" />
        
        <!-- Hidrant -->
        <circle cx="{floor_x_end}" cy="{floor_y}" r="15" fill="red" />
        
        <!-- Oznake -->
        <text x="{horizontal_x_start + (horizontal_x_end - horizontal_x_start)/2}" y="{riser_y_start + 30}" 
              text-anchor="middle" fill="black">Horizontalni vod ({horizontal_diameter}, {horizontal_length}m)</text>
        
        <text x="{riser_x - 30}" y="{riser_y_start - (riser_y_start - riser_y_end)/2}" 
              text-anchor="end" fill="black">Usponski vod ({riser_diameter}, {riser_height:.1f}m)</text>
        
        <text x="{floor_x_start + (floor_x_end - floor_x_start)/2}" y="{floor_y - 20}" 
              text-anchor="middle" fill="black">Etažni vod ({floor_diameter}, {floor_length}m)</text>
        
        <text x="{floor_x_end}" y="{floor_y - 30}" 
              text-anchor="middle" fill="black">Hidrant</text>
        
        <!-- Protokok -->
        <text x="{horizontal_x_start + (horizontal_x_end - horizontal_x_start)/2}" y="{riser_y_start + 50}" 
              text-anchor="middle" fill="{color_horizontal}">Q = {total_flow:.2f} l/s, v = {horizontal_velocity:.2f} m/s</text>
        
        <text x="{riser_x - 30}" y="{riser_y_start - (riser_y_start - riser_y_end)/2 + 20}" 
              text-anchor="end" fill="{color_riser}">Q = {total_flow:.2f} l/s, v = {riser_velocity:.2f} m/s</text>
        
        <text x="{floor_x_start + (floor_x_end - floor_x_start)/2}" y="{floor_y - 40}" 
              text-anchor="middle" fill="{color_floor}">Q = {total_flow:.2f} l/s, v = {floor_velocity:.2f} m/s</text>
    </svg>
    """
    
    st.markdown(svg_code, unsafe_allow_html=True)

def render_flow_chart(data):
    """Renderira vizualizaciju protoka vode."""
    # Pripremi podatke za vizualizaciju
    protok_l_min = data["results"]["total_flow_l_min"]
    protok_l_s = data["results"]["total_flow_l_s"]
    
    # Korištenje Streamlit komponenti za vizualizaciju
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Protok", f"{protok_l_min} l/min")
        # Kreiranje podataka za chart
        chart_data = pd.DataFrame({
            'Protok [l/min]': [protok_l_min]
        }, index=['Ukupni protok'])
        # Prikaz bar charta
        st.bar_chart(chart_data)
        
    with col2:
        st.metric("Protok", f"{protok_l_s:.2f} l/s")
        # Kreiranje podataka za chart
        chart_data = pd.DataFrame({
            'Protok [l/s]': [protok_l_s]
        }, index=['Ukupni protok'])
        # Prikaz bar charta
        st.bar_chart(chart_data)

def render_pressure_chart(data):
    """Renderira vizualizaciju gubitaka tlaka."""
    # Podaci za vizualizaciju
    inlet_pressure = data["parameters"]["inlet_pressure"]
    total_loss = data["results"]["total_loss"]
    linear_losses = data["results"]["total_linear_loss"]
    local_losses = data["results"]["total_local_loss"]
    geodetic_losses = data["results"]["geodetic_loss"]
    remaining_pressure = data["results"]["remaining_pressure"]
    
    # Kreiranje DataFrame za vizualizaciju
    df = pd.DataFrame({
        'Kategorija': ['Raspoloživi tlak', 'Linijski gubici', 'Lokalni gubici', 'Geodetski gubici', 'Preostali tlak'],
        'Vrijednost [bar]': [inlet_pressure, -linear_losses, -local_losses, -geodetic_losses, remaining_pressure]
    })
    
    # Prikaz gubitaka tlaka putem bar charta
    st.bar_chart(
        df.set_index('Kategorija')
    )
    
    # Prikaz detalja gubitaka
    st.subheader("Detalji gubitaka tlaka")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Raspoloživi tlak", f"{inlet_pressure:.2f} bar")
        
    with col2:
        st.metric("Ukupni gubici", f"{total_loss:.2f} bar", delta=f"-{total_loss:.2f}", delta_color="inverse")
        
    with col3:
        st.metric("Preostali tlak", f"{remaining_pressure:.2f} bar")
    
    # Popis gubitaka
    gubici_df = pd.DataFrame({
        'Vrsta gubitka': ['Linijski gubici', 'Lokalni gubici', 'Geodetski gubici', 'Ukupni gubici'],
        'Vrijednost [bar]': [linear_losses, local_losses, geodetic_losses, total_loss],
        'Postotak [%]': [
            linear_losses / total_loss * 100 if total_loss > 0 else 0,
            local_losses / total_loss * 100 if total_loss > 0 else 0,
            geodetic_losses / total_loss * 100 if total_loss > 0 else 0,
            100
        ]
    })
    
    st.dataframe(gubici_df, use_container_width=True, hide_index=True)