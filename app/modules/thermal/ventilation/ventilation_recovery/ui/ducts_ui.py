# modules/thermal/ventilation/ventilation_recovery/ui/ducts_ui.py

"""
UI components for the ducts tab of the ventilation recovery calculator.
"""

import streamlit as st
from modules.thermal.ventilation.ventilation_recovery.duct_sections import (
    create_new_section, 
    update_section_velocity,
    update_section_pressure_drop,
    get_initial_section_from_recuperator
)
from modules.thermal.ventilation.ventilation_recovery.branching import (
    initialize_branch_structure,
    add_main_section
)

def render_ducts_tab(calculator):
    """Prikazuje tab za dimenzioniranje kanala i proračun pada tlaka."""
    st.header("Dimenzioniranje kanala i proračun pada tlaka")
    
    data = st.session_state.ventilation_recovery_data["ducts"]
    airflow_data = st.session_state.ventilation_recovery_data["airflow"]
    recuperator_data = st.session_state.ventilation_recovery_data["recuperator"]
    
    # Provjera je li izračunat protok zraka
    if airflow_data["final_flow"] <= 0:
        st.warning("Prije dimenzioniranja kanala potrebno je izračunati protok zraka u koraku 'Protok zraka'.")
        return
    
    # Određivanje protoka za dimenzioniranje
    if recuperator_data.get("selected_model"):
        # Ako je odabran rekuperator, koristimo njegov protok
        design_flow = recuperator_data["flow_capacity"]
        st.info(f"Dimenzioniranje kanala koristi protok odabranog rekuperatora: {design_flow} m³/h")
    else:
        # Inače koristimo izračunati protok
        design_flow = airflow_data["final_flow"]
        
    # Kartice za različite tipove dionica
    duct_tabs = st.tabs([
        "Pregled sustava",
        "Svježi zrak (vanjski → rekuperator)",
        "Tlačni razvod (rekuperator → prostor)",
        "Odsisni razvod (prostor → rekuperator)",
        "Istrošeni zrak (rekuperator → vanjski)"
    ])
    
    # Inicijalizacija strukture dionica ako je prazna
    if not data.get("branch_structure") or not data.get("branch_structure", {}).get("fresh_air", {}).get("sections"):
        # Inicijalizacija strukture
        if not data.get("branch_structure"):
            data["branch_structure"] = initialize_branch_structure()
        
        # Provjera je li odabran rekuperator
        if recuperator_data.get("selected_model"):
            # Inicijalizacija dionica s podacima iz rekuperatora
            for system_type in ["fresh_air", "supply", "extract", "exhaust"]:
                if not data["branch_structure"][system_type].get("sections"):
                    initial_section = get_initial_section_from_recuperator(recuperator_data, system_type)
                    # Postavljanje protoka na odabrani protok
                    initial_section["flow_rate"] = design_flow
                    data["branch_structure"] = add_main_section(data["branch_structure"], system_type, initial_section)
        else:
            # Inicijalizacija praznih dionica
            for system_type in ["fresh_air", "supply", "extract", "exhaust"]:
                if not data["branch_structure"][system_type].get("sections"):
                    default_name = {
                        "fresh_air": "Svježi zrak (ulaz u rekuperator)",
                        "supply": "Tlačni kanal (iz rekuperatora)",
                        "extract": "Odsisni kanal (prema rekuperatoru)",
                        "exhaust": "Istrošeni zrak (izlaz iz rekuperatora)"
                    }.get(system_type, "Nova dionica")
                    
                    initial_section = create_new_section(section_type="main", duct_type="round", name=default_name)
                    initial_section["flow_rate"] = design_flow
                    update_section_velocity(initial_section)
                    update_section_pressure_drop(initial_section)
                    
                    data["branch_structure"] = add_main_section(data["branch_structure"], system_type, initial_section)

    # Pregled sustava
    with duct_tabs[0]:
        _render_system_overview(data, recuperator_data)
    
    # Svježi zrak (vanjski → rekuperator)
    with duct_tabs[1]:
        edit_system_ducts("fresh_air", "svježi zrak (vanjski → rekuperator)", data, design_flow, calculator)
    
    # Tlačni razvod (rekuperator → prostor)
    with duct_tabs[2]:
        edit_system_ducts("supply", "tlačni razvod (rekuperator → prostor)", data, design_flow, calculator)
    
    # Odsisni razvod (prostor → rekuperator)
    with duct_tabs[3]:
        edit_system_ducts("extract", "odsisni razvod (prostor → rekuperator)", data, design_flow, calculator)
    
    # Istrošeni zrak (rekuperator → vanjski)
    with duct_tabs[4]:
        edit_system_ducts("exhaust", "istrošeni zrak (rekuperator → vanjski)", data, design_flow, calculator)
    
    # Ažuriranje podataka u session_state
    st.session_state.ventilation_recovery_data["ducts"] = data
    calculator.mark_as_changed()


def _render_system_overview(data, recuperator_data):
    """Prikazuje pregled ventilacijskog sustava s ukupnim padom tlaka."""
    st.subheader("Pregled ventilacijskog sustava")
    
    # Izračun ukupnog pada tlaka
    total_drop = 0
    drops_by_system = {}
    
    for system_type, system_data in data.get("branch_structure", {}).items():
        system_drop = 0
        
        # Glavne dionice
        for section in system_data.get("sections", []):
            section_drop = section.get("pressure_drop", {}).get("total", 0)
            system_drop += section_drop
        
        # Dodavanje pada tlaka iz grana (za tlačni i odsisni razvod)
        if system_type in ["supply", "extract"] and "branches" in system_data:
            branch_drops = []
            for branch in system_data.get("branches", []):
                branch_drop = sum(s.get("pressure_drop", {}).get("total", 0) for s in branch.get("sections", []))
                branch_drops.append(branch_drop)
            
            # Uzimamo najveći pad tlaka grane
            if branch_drops:
                system_drop += max(branch_drops)
        
        drops_by_system[system_type] = system_drop
        total_drop += system_drop
    
    # Dodajemo pad tlaka rekuperatora
    recuperator_drop = recuperator_data.get("pressure_capacity", 0) if recuperator_data else 0
    total_drop += recuperator_drop
    
    # Ažuriranje ukupnog pada tlaka
    data["total_pressure_drop"] = total_drop
    
    # Prikaz ukupnog pada tlaka
    st.subheader("Ukupni pad tlaka sustava")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Svježi zrak", f"{drops_by_system.get('fresh_air', 0):.1f} Pa")
    with col2:
        st.metric("Tlačni razvod", f"{drops_by_system.get('supply', 0):.1f} Pa")
    with col3:
        st.metric("Odsisni razvod", f"{drops_by_system.get('extract', 0):.1f} Pa")
    with col4:
        st.metric("Istrošeni zrak", f"{drops_by_system.get('exhaust', 0):.1f} Pa")
    
    st.metric("Pad tlaka rekuperatora", f"{recuperator_drop:.1f} Pa")
    st.success(f"UKUPNI PAD TLAKA: {total_drop:.1f} Pa")
    
    # Provjera potrebnog tlaka rekuperatora
    if recuperator_data and recuperator_data.get("selected_model"):
        available_pressure = recuperator_data.get("pressure_capacity", 0)
        pressure_diff = available_pressure - total_drop
        
        if pressure_diff >= 0:
            st.success(f"Odabrani rekuperator {recuperator_data['selected_model']} ima dovoljan raspoloživi tlak: {available_pressure:.1f} Pa")
        else:
            st.error(f"Odabrani rekuperator {recuperator_data['selected_model']} nema dovoljan raspoloživi tlak (nedostaje {-pressure_diff:.1f} Pa)")
    else:
        st.info("Odaberite rekuperator u kartici 'Rekuperator i grijač' za provjeru raspoloživog tlaka.")


def edit_system_ducts(system_type, system_label, data, design_flow, calculator):
    """Uređuje dionice za određeni podsustav ventilacije."""
    if not data.get("branch_structure") or system_type not in data.get("branch_structure", {}):
        data["branch_structure"] = initialize_branch_structure()
    
    system_data = data["branch_structure"][system_type]
    
    st.subheader(f"Dionice za {system_label}")
    
    # Prikaz i uređivanje glavnih dionica
    st.write("### Glavne dionice")
    
    for i, section in enumerate(system_data.get("sections", [])):
        # Ensure local_resistances exists in each section
        if "local_resistances" not in section:
            section["local_resistances"] = {}
            
        # Ensure pressure_drop exists with required keys
        if "pressure_drop" not in section:
            section["pressure_drop"] = {"friction": 0, "total": 0}
        elif "friction" not in section["pressure_drop"]:
            section["pressure_drop"]["friction"] = 0
        elif "total" not in section["pressure_drop"]:
            section["pressure_drop"]["total"] = 0
            
        with st.expander(f"Dionica: {section.get('name', f'Dionica {i+1}')}", expanded=False):
            # Naziv dionice
            section["name"] = st.text_input(
                "Naziv dionice", 
                value=section.get("name", f"Dionica {i+1}"),
                key=f"{system_type}_section_{i}_name"
            )
            
            # Protok zraka
            col1, col2 = st.columns(2)
            
            with col1:
                section["flow_rate"] = st.number_input(
                    "Protok zraka [m³/h]",
                    min_value=10.0,
                    max_value=10000.0,
                    value=section.get("flow_rate", 100.0),
                    step=10.0,
                    key=f"{system_type}_section_{i}_flow"
                )
            
            with col2:
                section["length"] = st.number_input(
                    "Duljina dionice [m]",
                    min_value=0.1,
                    max_value=100.0,
                    value=section.get("length", 5.0),
                    step=0.5,
                    key=f"{system_type}_section_{i}_length"
                )
            
            # Tip kanala (kružni ili pravokutni)
            section["duct_type"] = st.selectbox(
                "Tip kanala",
                options=["round", "rectangular"],
                index=0 if section.get("duct_type", "round") == "round" else 1,
                format_func=lambda x: "Kružni" if x == "round" else "Pravokutni",
                key=f"{system_type}_section_{i}_type"
            )
            
            # Dimenzije kanala
            if section["duct_type"] == "round":
                # Kružni kanal - promjer
                if "dimensions" not in section:
                    section["dimensions"] = {"diameter": 200}
                
                std_diameters = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000]
                
                # Pronađi najbliži standardni promjer
                current_diameter = section["dimensions"].get("diameter", 200)
                closest_idx = 0
                min_diff = float('inf')
                
                for idx, diam in enumerate(std_diameters):
                    diff = abs(diam - current_diameter)
                    if diff < min_diff:
                        min_diff = diff
                        closest_idx = idx
                
                section["dimensions"]["diameter"] = st.selectbox(
                    "Promjer [mm]",
                    options=std_diameters,
                    index=closest_idx,
                    key=f"{system_type}_section_{i}_diameter"
                )
                # Brisanje nepotrebnih dimenzija za pravokutni kanal
                if "width" in section["dimensions"]:
                    del section["dimensions"]["width"]
                if "height" in section["dimensions"]:
                    del section["dimensions"]["height"]
            else:
                # Pravokutni kanal - širina i visina
                if "dimensions" not in section:
                    section["dimensions"] = {"width": 300, "height": 200}
                
                std_dims = [100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1200]
                
                # Pronađi najbliže standardne dimenzije
                current_width = section["dimensions"].get("width", 300)
                closest_width_idx = 0
                min_width_diff = float('inf')
                
                for idx, width in enumerate(std_dims):
                    diff = abs(width - current_width)
                    if diff < min_width_diff:
                        min_width_diff = diff
                        closest_width_idx = idx
                
                current_height = section["dimensions"].get("height", 200)
                closest_height_idx = 0
                min_height_diff = float('inf')
                
                for idx, height in enumerate(std_dims):
                    diff = abs(height - current_height)
                    if diff < min_height_diff:
                        min_height_diff = diff
                        closest_height_idx = idx
                
                col1, col2 = st.columns(2)
                with col1:
                    section["dimensions"]["width"] = st.selectbox(
                        "Širina [mm]",
                        options=std_dims,
                        index=closest_width_idx,
                        key=f"{system_type}_section_{i}_width"
                    )
                
                with col2:
                    section["dimensions"]["height"] = st.selectbox(
                        "Visina [mm]",
                        options=std_dims,
                        index=closest_height_idx,
                        key=f"{system_type}_section_{i}_height"
                    )
                
                # Brisanje nepotrebne dimenzije za kružni kanal
                if "diameter" in section["dimensions"]:
                    del section["dimensions"]["diameter"]
            
            # Lokalni otpori
            _render_local_resistances(section, system_type, i)
            
            # Gumb za izračun brzine i pada tlaka
            if st.button("Izračunaj brzinu i pad tlaka", key=f"{system_type}_section_{i}_calculate"):
                update_section_velocity(section)
                update_section_pressure_drop(section)
            
            # Prikaz rezultata
            st.write("#### Rezultati izračuna")
            
            col1, col2, col3 = st.columns(3)
            
            velocity = section.get("velocity", 0)
            try:
                color, message = calculator.get_velocity_indicators(velocity, "main_duct")
            except Exception as e:
                color, message = "red", f"Greška: {str(e)}"
            
            with col1:
                st.metric("Brzina", f"{velocity:.2f} m/s", delta=message, delta_color="normal" if color == "green" else ("inverse" if color == "red" else "off"))
            
            with col2:
                st.metric("Pad tlaka po trenju", f"{section.get('pressure_drop', {}).get('friction', 0):.1f} Pa")
            
            with col3:
                st.metric("Pad tlaka ukupno", f"{section.get('pressure_drop', {}).get('total', 0):.1f} Pa")
            
            # Gumb za brisanje dionice
            if len(system_data.get("sections", [])) > 1:  # Ne dopuštamo brisanje jedine dionice
                if st.button("Ukloni dionicu", key=f"{system_type}_section_{i}_delete"):
                    system_data["sections"].pop(i)
                    st.rerun()
        
        # Razmak između dionica
        st.markdown("---")
    
    # Dodavanje nove dionice
    if st.button("Dodaj novu dionicu", key=f"{system_type}_add_section"):
        new_section = create_new_section(
            section_type="main",
            duct_type="round",
            name=f"Nova dionica {len(system_data.get('sections', [])) + 1}"
        )
        new_section["flow_rate"] = design_flow / (len(system_data.get("sections", [])) + 1)
        update_section_velocity(new_section)
        update_section_pressure_drop(new_section)
        
        if "sections" not in system_data:
            system_data["sections"] = []
        
        system_data["sections"].append(new_section)
        st.rerun()
    
    # Prikaz i uređivanje grana za tlačni i odsisni razvod
    if system_type in ["supply", "extract"]:
        _render_branches(system_data, system_type, design_flow, calculator)


def _render_local_resistances(section, system_type, section_index):
    """Prikazuje i uređuje lokalne otpore za dionicu."""
    st.write("#### Lokalni otpori")
    
    # Lista lokalnih otpora
    local_resistance_types = [
        "bend_90deg", "bend_45deg", "t_junction_straight", "t_junction_branch",
        "sudden_expansion", "sudden_contraction", "duct_inlet", "duct_outlet", 
        "diffuser", "extract_grille"
    ]
    
    local_resistance_names = {
        "bend_90deg": "Koljeno 90°",
        "bend_45deg": "Koljeno 45°",
        "t_junction_straight": "T-komad (prolaz)",
        "t_junction_branch": "T-komad (odvajanje)",
        "sudden_expansion": "Naglo proširenje",
        "sudden_contraction": "Naglo suženje",
        "duct_inlet": "Ulaz u kanal",
        "duct_outlet": "Izlaz iz kanala",
        "diffuser": "Difuzor",
        "extract_grille": "Odsisna rešetka"
    }
    
    # Inicijalizacija local_resistances ako ne postoji
    if "local_resistances" not in section:
        section["local_resistances"] = {}
    
    # Ažuriranje lokalnih otpora
    col1, col2 = st.columns(2)
    
    for j, resistance_type in enumerate(local_resistance_types):
        col = col1 if j % 2 == 0 else col2
        with col:
            element_count = section["local_resistances"].get(resistance_type, 0)
            
            section["local_resistances"][resistance_type] = st.number_input(
                f"{local_resistance_names.get(resistance_type, resistance_type)}",
                min_value=0,
                max_value=20,
                value=element_count,
                step=1,
                key=f"{system_type}_section_{section_index}_resistance_{resistance_type}"
            )


def _render_branches(system_data, system_type, design_flow, calculator):
    """Prikazuje i uređuje grane ventilacijskog sustava."""
    st.write("### Grane")
    
    # Inicijalizacija grana ako ne postoje
    if "branches" not in system_data:
        system_data["branches"] = []
    
    if not system_data.get("branches"):
        st.info("Nema definiranih grana. Kliknite na 'Dodaj novu granu' da dodate granu.")
    else:
        for b_idx, branch in enumerate(system_data.get("branches", [])):
            with st.expander(f"Grana {b_idx + 1}: {branch.get('name', f'Grana {b_idx + 1}')}", expanded=False):
                # Naziv grane
                branch["name"] = st.text_input(
                    "Naziv grane", 
                    value=branch.get("name", f"Grana {b_idx + 1}"),
                    key=f"{system_type}_branch_{b_idx}_name"
                )
                
                # Dionice grane
                st.write("#### Dionice grane")
                
                if "sections" not in branch:
                    branch["sections"] = []
                    
                for s_idx, section in enumerate(branch.get("sections", [])):
                    _render_branch_section(branch, s_idx, section, system_type, b_idx, design_flow, calculator)
                
                # Dodavanje nove dionice u granu
                if st.button("Dodaj novu dionicu", key=f"{system_type}_branch_{b_idx}_add_section"):
                    new_section = create_new_section(
                        section_type="branch",
                        duct_type="round",
                        name=f"Nova dionica {len(branch.get('sections', [])) + 1}"
                    )
                    # Procjena protoka za novu dionicu
                    if branch.get("sections"):
                        new_section["flow_rate"] = sum(s.get("flow_rate", 0) for s in branch.get("sections", [])) / len(branch.get("sections", []))
                    else:
                        new_section["flow_rate"] = design_flow / 4  # Pretpostavka za 4 grane
                    
                    update_section_velocity(new_section)
                    update_section_pressure_drop(new_section)
                    
                    branch["sections"].append(new_section)
                    st.rerun()
                
                # Gumb za brisanje grane
                if st.button("Ukloni granu", key=f"{system_type}_branch_{b_idx}_delete"):
                    system_data["branches"].pop(b_idx)
                    st.rerun()
            
            # Razmak između grana
            st.markdown("---")
    
    # Dodavanje nove grane
    if st.button("Dodaj novu granu", key=f"{system_type}_add_branch"):
        new_branch = {
            "name": f"Nova grana {len(system_data.get('branches', [])) + 1}",
            "sections": []
        }
        
        # Dodavanje početne dionice
        initial_section = create_new_section(
            section_type="branch",
            duct_type="round",
            name="Početna dionica"
        )
        # Procjena protoka za početnu dionicu nove grane
        initial_section["flow_rate"] = design_flow / 4  # Pretpostavka za 4 grane
        
        update_section_velocity(initial_section)
        update_section_pressure_drop(initial_section)
        
        new_branch["sections"].append(initial_section)
        system_data["branches"].append(new_branch)
        st.rerun()


def _render_branch_section(branch, s_idx, section, system_type, b_idx, design_flow, calculator):
    """Prikazuje i uređuje dionicu u grani."""
    with st.expander(f"Dionica: {section.get('name', f'Dionica {s_idx+1}')}", expanded=False):
        # Naziv dionice
        section["name"] = st.text_input(
            "Naziv dionice", 
            value=section.get("name", f"Dionica {s_idx+1}"),
            key=f"{system_type}_branch_{b_idx}_section_{s_idx}_name"
        )
        
        # Protok zraka
        col1, col2 = st.columns(2)
        
        with col1:
            section["flow_rate"] = st.number_input(
                "Protok zraka [m³/h]",
                min_value=10.0,
                max_value=design_flow,
                value=section.get("flow_rate", 100.0),
                step=10.0,
                key=f"{system_type}_branch_{b_idx}_section_{s_idx}_flow"
            )
        
        with col2:
            section["length"] = st.number_input(
                "Duljina dionice [m]",
                min_value=0.1,
                max_value=100.0,
                value=section.get("length", 5.0),
                step=0.5,
                key=f"{system_type}_branch_{b_idx}_section_{s_idx}_length"
            )
        
        # Tip kanala (kružni ili pravokutni)
        section["duct_type"] = st.selectbox(
            "Tip kanala",
            options=["round", "rectangular"],
            index=0 if section.get("duct_type", "round") == "round" else 1,
            format_func=lambda x: "Kružni" if x == "round" else "Pravokutni",
            key=f"{system_type}_branch_{b_idx}_section_{s_idx}_type"
        )
        
        # Dimenzije kanala
        if section["duct_type"] == "round":
            # Kružni kanal - promjer
            if "dimensions" not in section:
                section["dimensions"] = {"diameter": 200}
            
            std_diameters = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000]
            
            # Pronađi najbliži standardni promjer
            current_diameter = section["dimensions"].get("diameter", 200)
            closest_idx = 0
            min_diff = float('inf')
            
            for idx, diam in enumerate(std_diameters):
                diff = abs(diam - current_diameter)
                if diff < min_diff:
                    min_diff = diff
                    closest_idx = idx
            
            section["dimensions"]["diameter"] = st.selectbox(
                "Promjer [mm]",
                options=std_diameters,
                index=closest_idx,
                key=f"{system_type}_branch_{b_idx}_section_{s_idx}_diameter"
            )
            # Brisanje nepotrebnih dimenzija za pravokutni kanal
            if "width" in section["dimensions"]:
                del section["dimensions"]["width"]
            if "height" in section["dimensions"]:
                del section["dimensions"]["height"]
        else:
            # Pravokutni kanal - širina i visina
            if "dimensions" not in section:
                section["dimensions"] = {"width": 300, "height": 200}
            
            std_dims = [100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1200]
            
            # Pronađi najbliže standardne dimenzije
            current_width = section["dimensions"].get("width", 300)
            closest_width_idx = 0
            min_width_diff = float('inf')
            
            for idx, width in enumerate(std_dims):
                diff = abs(width - current_width)
                if diff < min_width_diff:
                    min_width_diff = diff
                    closest_width_idx = idx
            
            current_height = section["dimensions"].get("height", 200)
            closest_height_idx = 0
            min_height_diff = float('inf')
            
            for idx, height in enumerate(std_dims):
                diff = abs(height - current_height)
                if diff < min_height_diff:
                    min_height_diff = diff
                    closest_height_idx = idx
            
            col1, col2 = st.columns(2)
            with col1:
                section["dimensions"]["width"] = st.selectbox(
                    "Širina [mm]",
                    options=std_dims,
                    index=closest_width_idx,
                    key=f"{system_type}_branch_{b_idx}_section_{s_idx}_width"
                )
            
            with col2:
                section["dimensions"]["height"] = st.selectbox(
                    "Visina [mm]",
                    options=std_dims,
                    index=closest_height_idx,
                    key=f"{system_type}_branch_{b_idx}_section_{s_idx}_height"
                )
            
            # Brisanje nepotrebne dimenzije za kružni kanal
            if "diameter" in section["dimensions"]:
                del section["dimensions"]["diameter"]
        
        # Korištenje funkcije za prikaz lokalnih otpora (umjesto dupliciranja koda)
        key_prefix = f"{system_type}_branch_{b_idx}_section_{s_idx}"
        _render_local_resistances_for_branch(section, key_prefix)
        
        # Gumb za izračun brzine i pada tlaka
        if st.button("Izračunaj brzinu i pad tlaka", key=f"{key_prefix}_calculate"):
            update_section_velocity(section)
            update_section_pressure_drop(section)
        
        # Prikaz rezultata
        st.write("#### Rezultati izračuna")
        
        col1, col2, col3 = st.columns(3)
        
        velocity = section.get("velocity", 0)
        try:
            color, message = calculator.get_velocity_indicators(velocity, "branch")
        except Exception as e:
            color, message = "red", f"Greška: {str(e)}"
        
        with col1:
            st.metric("Brzina", f"{velocity:.2f} m/s", delta=message, delta_color="normal" if color == "green" else ("inverse" if color == "red" else "off"))
        
        with col2:
            st.metric("Pad tlaka po trenju", f"{section.get('pressure_drop', {}).get('friction', 0):.1f} Pa")
        
        with col3:
            st.metric("Pad tlaka ukupno", f"{section.get('pressure_drop', {}).get('total', 0):.1f} Pa")
        
        # Gumb za brisanje dionice
        if len(branch.get("sections", [])) > 1:  # Ne dopuštamo brisanje jedine dionice
            if st.button("Ukloni dionicu", key=f"{key_prefix}_delete"):
                branch["sections"].pop(s_idx)
                st.rerun()
        
        # Razmak između dionica
        st.markdown("---")

def _render_local_resistances_for_branch(section, key_prefix):
    """Prikazuje i uređuje lokalne otpore za dionicu grane."""
    st.write("#### Lokalni otpori")
    
    # Lista lokalnih otpora
    local_resistance_types = [
        "bend_90deg", "bend_45deg", "t_junction_straight", "t_junction_branch",
        "sudden_expansion", "sudden_contraction", "duct_inlet", "duct_outlet", 
        "diffuser", "extract_grille"
    ]
    
    local_resistance_names = {
        "bend_90deg": "Koljeno 90°",
        "bend_45deg": "Koljeno 45°",
        "t_junction_straight": "T-komad (prolaz)",
        "t_junction_branch": "T-komad (odvajanje)",
        "sudden_expansion": "Naglo proširenje",
        "sudden_contraction": "Naglo suženje",
        "duct_inlet": "Ulaz u kanal",
        "duct_outlet": "Izlaz iz kanala",
        "diffuser": "Difuzor",
        "extract_grille": "Odsisna rešetka"
    }
    
    # Inicijalizacija local_resistances ako ne postoji
    if "local_resistances" not in section:
        section["local_resistances"] = {}
    
    # Ažuriranje lokalnih otpora
    col1, col2 = st.columns(2)
    
    for j, resistance_type in enumerate(local_resistance_types):
        col = col1 if j % 2 == 0 else col2
        with col:
            element_count = section["local_resistances"].get(resistance_type, 0)
            
            section["local_resistances"][resistance_type] = st.number_input(
                f"{local_resistance_names.get(resistance_type, resistance_type)}",
                min_value=0,
                max_value=20,
                value=element_count,
                step=1,
                key=f"{key_prefix}_resistance_{resistance_type}"
            )