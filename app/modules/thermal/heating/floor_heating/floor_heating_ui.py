import streamlit as st
from modules.thermal.heating.floor_heating.constants import *
from modules.thermal.heating.floor_heating.utils import *
import json


def apply_custom_styles():
    """Primjenjuje prilagođene CSS stilove za izgled kalkulatora."""
    st.markdown("""
    <style>
    .section-header {
        background-color: #f0f0f0;
        padding: 5px;
        border-radius: 5px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


class FloorHeatingUI:
    """Klasa za renderiranje UI komponenti za kalkulator podnog grijanja."""
    
    def __init__(self, calculation_handler):
        """Inicijalizacija UI komponente s handlerom za kalkulacije."""
        self.calculation_handler = calculation_handler
    
    def render_building_tab(self, data):
        """Prikazuje tab za definiranje zgrade, etaža i razdjelnika."""
        st.header("Definiranje zgrade i razdjelnika")
        
        # Sekcija za osnovne podatke o zgradi
        with st.container():
            st.subheader("Podaci o zgradi")
            
            # Informacija o ukupnom broju etaža
            st.caption(f"Ukupno etaža: {len(data['building'].get('floors', []))}")
            
            # Gumb za dodavanje nove etaže
            if st.button("Dodaj novu etažu", key="add_floor_button"):
                self.calculation_handler._add_floor(data)
                st.rerun()
        
        # Sekcija za etaže
        for floor_index, floor in enumerate(data["building"].get("floors", [])):
            with st.expander(f"Etaža {floor_index + 1}: {floor.get('name', 'Etaža')}", expanded=True):
                # Podaci o etaži
                col1, col2 = st.columns(2)
                
                with col1:
                    # Naziv etaže
                    floor_name = st.text_input(
                        "Naziv etaže",
                        value=floor.get("name", "Etaža"),
                        key=f"floor_name_{floor['id']}",
                        on_change=lambda id=floor['id']: self.calculation_handler._on_floor_param_change(id, "name", data)
                    )
                    floor["name"] = floor_name
                
                with col2:
                    # Debljina estriha
                    screed_thickness = st.selectbox(
                        "Debljina estriha [mm]",
                        options=SCREED_THICKNESSES,
                        index=SCREED_THICKNESSES.index(floor.get("screed_thickness", 45)) if floor.get("screed_thickness") in SCREED_THICKNESSES else 0,
                        key=f"screed_thickness_{floor['id']}",
                        on_change=lambda id=floor['id']: self.calculation_handler._on_floor_param_change(id, "screed_thickness", data)
                    )
                    floor["screed_thickness"] = screed_thickness
                
                # Gumb za brisanje etaže
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button(f"Obriši etažu", key=f"delete_floor_{floor['id']}"):
                        if len(data["building"]["floors"]) > 1:  # Ne dozvoli brisanje posljednje etaže
                            self.calculation_handler._delete_floor(floor['id'], data)
                            st.rerun()
                        else:
                            st.error("Nije moguće obrisati posljednju etažu.")
                
                # Gumb za dodavanje razdjelnika
                col1, col2 = st.columns([1, 3])
                with col1:
                    if st.button(f"Dodaj razdjelnik", key=f"add_manifold_{floor['id']}"):
                        self.calculation_handler._add_manifold(floor, data)
                        st.rerun()
                
                # Brojač za prikazivanje svih razdjelnika na etaži
                manifold_count = len(floor.get("manifolds", []))
                st.caption(f"Broj razdjelnika na etaži: {manifold_count}")
                
                # Prikaži razdjelnike
                for manifold_index, manifold in enumerate(floor.get("manifolds", [])):
                    with st.container():
                        st.markdown(f"#### Razdjelnik {manifold_index + 1}: {manifold.get('name', 'Razdjelnik')}")
                        
                        # Osnovni podaci o razdjelniku
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Naziv razdjelnika
                            manifold_name = st.text_input(
                                "Naziv razdjelnika",
                                value=manifold.get("name", "Razdjelnik"),
                                key=f"manifold_name_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_param_change(f_id, m_id, "name", data)
                            )
                            manifold["name"] = manifold_name
                            
                            # Polazna temperatura
                            flow_temp = st.selectbox(
                                "Polazna temperatura [°C]",
                                options=FLOW_TEMPERATURES,
                                index=FLOW_TEMPERATURES.index(manifold.get("flow_temperature", 35)) if manifold.get("flow_temperature") in FLOW_TEMPERATURES else 0,
                                key=f"flow_temperature_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_param_change(f_id, m_id, "flow_temperature", data)
                            )
                            manifold["flow_temperature"] = flow_temp
                            
                            # Temperaturna razlika
                            delta_t = st.selectbox(
                                "Temperaturna razlika (ΔT) [°C]",
                                options=DELTA_T_VALUES,
                                index=DELTA_T_VALUES.index(manifold.get("delta_t", 5)) if manifold.get("delta_t") in DELTA_T_VALUES else 0,
                                key=f"delta_t_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_param_change(f_id, m_id, "delta_t", data)
                            )
                            manifold["delta_t"] = delta_t
                        
                        with col2:
                            # Promjer cijevi petlje
                            pipe_options = {key: data['display'] for key, data in PIPE_DATA.items()}
                            pipe_diameter = st.selectbox(
                                "Promjer cijevi petlji",
                                options=list(pipe_options.keys()),
                                format_func=lambda x: pipe_options[x],
                                index=list(pipe_options.keys()).index(manifold.get("pipe_diameter", "16x2,0")) if manifold.get("pipe_diameter") in pipe_options else 0,
                                key=f"pipe_diameter_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_param_change(f_id, m_id, "pipe_diameter", data)
                            )
                            manifold["pipe_diameter"] = pipe_diameter
                            
                            # Broj krugova
                            num_circuits = st.selectbox(
                                "Broj krugova na razdjelniku",
                                options=list(range(2, 17)),  # 2-16 krugova prema Uponor Vario FM
                                index=min(max(0, manifold.get("num_circuits", 4) - 2), 14),  # Default 4 kruga
                                key=f"num_circuits_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_circuits_change(f_id, m_id, data)
                            )
                            manifold["num_circuits"] = num_circuits
                        
                        # Spojne cijevi - izdvojeno s jasnim naslovom za bolju vidljivost
                        st.markdown("##### Spojne cijevi do razdjelnika")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            # Promjer spojnih cijevi do razdjelnika - promijenjeno ime za bolju jasnoću
                            # Uključene sve dimenzije spojnih cijevi, uključujući 40x4,0 i 50x4,5
                            supply_pipe_options = {key: data['display'] for key, data in CONNECTION_PIPE_DATA.items() if key in ['16×2,0', '20×2,3', '25×2,5', '32×3,0', '40×4,0', '50×4,5']}
                            supply_pipe_diameter = st.selectbox(
                                "Promjer spojnih cijevi",
                                options=list(supply_pipe_options.keys()),
                                format_func=lambda x: supply_pipe_options[x],
                                index=list(supply_pipe_options.keys()).index(manifold.get("supply_pipe_diameter", "32×3,0")) if manifold.get("supply_pipe_diameter") in supply_pipe_options else 3, # default na 32×3,0
                                key=f"supply_pipe_diameter_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_param_change(f_id, m_id, "supply_pipe_diameter", data)
                            )
                            manifold["supply_pipe_diameter"] = supply_pipe_diameter
                            st.caption("Koristi se isti promjer za polaznu i povratnu cijev")
                        
                        with col2:
                            # Duljina polazne cijevi
                            supply_pipe_length = st.number_input(
                                "Duljina polazne cijevi [m]",
                                min_value=0.0, value=float(manifold.get("supply_pipe_length", 5.0)), step=0.5, format="%.1f",
                                key=f"supply_pipe_length_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_param_change(f_id, m_id, "supply_pipe_length", data)
                            )
                            manifold["supply_pipe_length"] = supply_pipe_length
                        
                        with col3:
                            # Duljina povratne cijevi
                            return_pipe_length = st.number_input(
                                "Duljina povratne cijevi [m]",
                                min_value=0.0, value=float(manifold.get("return_pipe_length", 5.0)), step=0.5, format="%.1f",
                                key=f"return_pipe_length_{floor['id']}_{manifold['id']}",
                                on_change=lambda f_id=floor['id'], m_id=manifold['id']: self.calculation_handler._on_manifold_param_change(f_id, m_id, "return_pipe_length", data)
                            )
                            manifold["return_pipe_length"] = return_pipe_length
                        
                        # Gumb za brisanje razdjelnika
                        if st.button(f"Obriši razdjelnik", key=f"delete_manifold_{floor['id']}_{manifold['id']}"):
                            if len(floor.get("manifolds", [])) > 1:  # Ne dozvoli brisanje posljednjeg razdjelnika
                                self.calculation_handler._delete_manifold(floor['id'], manifold['id'], data)
                                st.rerun()
                            else:
                                st.error("Nije moguće obrisati posljednji razdjelnik.")
                        
                        # Prostorije na razdjelniku
                        st.markdown("##### Raspored prostorija na razdjelniku")
                        st.caption("Prva prostorija je lijevo na razdjelniku. Koristite gumbe za promjenu redoslijeda.")
                        
                        # Lista prostorija
                        rooms = sorted(manifold.get("rooms", []), key=lambda x: x.get("position", 0))
                        
                        # Pripremi listu svih tipova prostorija za padajući izbornik
                        all_room_types = []
                        for temp, room_list in ROOM_TYPES.items():
                            all_room_types.extend(room_list)
                        all_room_types.sort()
                        
                        # Prikaži prostorije
                        for room_index, room in enumerate(rooms):
                            room_id = room.get("id")
                            current_room_name = room.get("name", "")
                            
                            # Izmijenjeni raspored - prostorija lijevo, gumbi za gore/dolje desno
                            col1, col2 = st.columns([1, 1])  # Omjer pola-pola umjesto 3:2
                            
                            with col1:
                                selected_room_type = st.selectbox(
                                    f"Prostorija {room_index + 1}",
                                    options=all_room_types,
                                    index=all_room_types.index(current_room_name) if current_room_name in all_room_types else 0,
                                    key=f"room_name_{floor['id']}_{manifold['id']}_{room_id}",
                                    on_change=lambda f_id=floor['id'], m_id=manifold['id'], r_id=room_id: 
                                        self.calculation_handler._on_room_type_change(f_id, m_id, r_id, data)
                                )
                                room["name"] = selected_room_type
                            
                            with col2:
                                # Jednostavniji pristup - koristi direktno HTML elemente za gumbe jedan pored drugog
                                st.write('<div style="height:28px"></div>', unsafe_allow_html=True)  # Razmak za poravnanje s dropdown kontrolom
                                
                                # Stvori kontejner za oba gumba
                                cols = st.columns([0.5, 0.5, 9])  # Dvije kolone širine 10% i treća 80%
                                
                                # Gumb za dolje 
                                with cols[0]:
                                    # Prikazujemo gumb za dolje samo ako prostorija nije zadnja na popisu
                                    if room_index < len(rooms) - 1:
                                        down_clicked = st.button("↓", key=f"move_down_{room_id}", help="Pomakni prostoriju dolje")
                                        if down_clicked:
                                            self.calculation_handler._move_room_down(floor['id'], manifold['id'], room_id, data)
                                            st.rerun()
                                    else:
                                        # Dodaj prazan prostor umjesto gumba za zadnju prostoriju
                                        st.write(" ")
                                
                                # Gumb za gore - odmah desno
                                with cols[1]:
                                    # Prikazujemo gumb za gore samo ako prostorija nije prva na popisu
                                    if room_index > 0:
                                        up_clicked = st.button("↑", key=f"move_up_{room_id}", help="Pomakni prostoriju gore")
                                        if up_clicked:
                                            self.calculation_handler._move_room_up(floor['id'], manifold['id'], room_id, data)
                                            st.rerun()
                                    else:
                                        # Dodaj prazan prostor umjesto gumba za prvu prostoriju
                                        st.write(" ")
                        
                        # Informacija ako nema prostorija
                        if not rooms:
                            st.info("Nema definiranih prostorija na razdjelniku.")
                        
                        # Dodaj separator između razdjelnika
                        st.markdown("---")
    
    def render_loops_tab(self, data):
        """Prikazuje tab s parametrima petlji podnog grijanja."""
        st.header("Parametri petlji podnog grijanja")
        
        # Provjeri postoje li definirane etaže i razdjelnici
        if not data.get("building", {}).get("floors", []):
            st.warning("Potrebno je prvo definirati etaže i razdjelnike u tabu 'Zgrada i razdjelnici'.")
            return
        
        # Odabir etaže i razdjelnika
        col1, col2 = st.columns(2)
        
        # Pripremimo opcije za etaže
        floors = data.get("building", {}).get("floors", [])
        floor_options = [f"{floor['name']}" for floor in floors]
        
        # Ako nema session_state za odabir, postavi na prvu etažu
        if "selected_floor_index" not in st.session_state:
            st.session_state.selected_floor_index = 0
        
        # Ako je indeks izvan granica (npr. nakon brisanja etaže), resetiraj na 0
        if st.session_state.selected_floor_index >= len(floor_options):
            st.session_state.selected_floor_index = 0
        
        with col1:
            selected_floor_index = st.selectbox(
                "Odaberi etažu",
                options=range(len(floor_options)),
                format_func=lambda x: floor_options[x],
                key="loops_floor_selector",
                index=st.session_state.selected_floor_index,
                on_change=self.calculation_handler._on_floor_or_manifold_selector_change
            )
            st.session_state.selected_floor_index = selected_floor_index
        
        # Dohvati odabranu etažu
        selected_floor = floors[selected_floor_index]
        
        # Pripremimo opcije za razdjelnike
        manifolds = selected_floor.get("manifolds", [])
        manifold_options = [f"{manifold['name']}" for manifold in manifolds]
        
        # Ako nema session_state za odabir razdjelnika, postavi na prvi
        if "selected_manifold_index" not in st.session_state:
            st.session_state.selected_manifold_index = 0
        
        # Ako je indeks izvan granica (npr. nakon brisanja razdjelnika), resetiraj na 0
        if st.session_state.selected_manifold_index >= len(manifold_options):
            st.session_state.selected_manifold_index = 0
        
        with col2:
            selected_manifold_index = st.selectbox(
                "Odaberi razdjelnik",
                options=range(len(manifold_options)),
                format_func=lambda x: manifold_options[x],
                key="loops_manifold_selector",
                index=st.session_state.selected_manifold_index,
                on_change=self.calculation_handler._on_floor_or_manifold_selector_change
            )
            st.session_state.selected_manifold_index = selected_manifold_index
        
        # Dohvati odabrani razdjelnik
        selected_manifold = manifolds[selected_manifold_index]
        
        # Prikaži informacije o razdjelniku
        with st.container():
            st.subheader(f"Razdjelnik: {selected_manifold['name']}")
            
            col1, col2, col3, col4 = st.columns(4)            
            col1.metric("Polazna temperatura", f"{selected_manifold.get('flow_temperature', 35):.1f} °C")
            col2.metric("Temperaturna razlika (ΔT)", f"{selected_manifold.get('delta_t', 5):.1f} °C")
            
            # Dohvati display format za promjer cijevi
            pipe_display = PIPE_DATA.get(selected_manifold.get('pipe_diameter', "16x2,0"), {}).get('display', selected_manifold.get('pipe_diameter', "16x2,0"))
            col3.metric("Promjer cijevi", pipe_display)
            col4.metric("Debljina estriha", f"{selected_floor.get('screed_thickness', 45)} mm")
        
        # Petlje podnog grijanja za odabrani razdjelnik
        st.markdown("---")
        st.subheader("Petlje podnog grijanja")
        
        # Dohvati petlje i prostorije za odabrani razdjelnik
        loops = selected_manifold.get("loops", [])
        rooms = sorted(selected_manifold.get("rooms", []), key=lambda x: x.get("position", 0))
        
        # Petlje - organiziraj u dva stupca
        col1, col2 = st.columns(2)
        
        # Ako nema petlji, prikaži upozorenje
        if not loops:
            st.warning("Nema definiranih petlji za odabrani razdjelnik. Dodajte prostorije u tabu 'Zgrada i razdjelnici'.")
            return
        
        # Sinkroniziraj petlje s prostorijama (1:1 odnos prema ID-u)
        # Ovo osigurava da postoji petlja za svaku prostoriju i da su ispravno povezane
        for room in rooms:
            # Pronađi postojeću petlju za ovu prostoriju
            loop_found = False
            for loop in loops:
                if loop.get("id") == room.get("id"):
                    # Ažuriraj naziv prostorije u petlji ako je potrebno
                    if loop.get("room_name") != room.get("name"):
                        loop["room_name"] = room.get("name")
                    loop_found = True
                    break
            
            # Ako petlja ne postoji, kreiraj novu
            if not loop_found:
                new_loop = {
                    "id": room.get("id"),
                    "room_name": room.get("name"),
                    "room_temperature": get_room_temperature_for_name(room.get("name", "")),
                    "r_lambda": 0.00,
                    "pipe_spacing": 15,
                    "area": None,
                    "manifold_distance": None,
                    "results": {}
                }
                loops.append(new_loop)
        
        # Dodatna provjera: ukloni petlje koje nemaju odgovarajuću prostoriju
        valid_room_ids = [room.get("id") for room in rooms]
        loops[:] = [loop for loop in loops if loop.get("id") in valid_room_ids]
        
        # Sortiraj petlje prema redoslijedu prostorija
        sorted_loops = []
        for room in rooms:
            for loop in loops:
                if loop.get("id") == room.get("id"):
                    sorted_loops.append(loop)
                    break
        
        # Podijeli petlje u dva dijela - za lijevu i desnu kolonu
        left_loops = sorted_loops[::2]  # Parni indeksi (0, 2, 4...)
        right_loops = sorted_loops[1::2]  # Neparni indeksi (1, 3, 5...)
        
        # Prikaži petlje u lijevom stupcu
        with col1:
            for loop in left_loops:
                self.render_loop_card(loop, data, selected_floor, selected_manifold)
        
        # Prikaži petlje u desnom stupcu
        with col2:
            for loop in right_loops:
                self.render_loop_card(loop, data, selected_floor, selected_manifold)
    
    def render_loop_card(self, loop, data, floor=None, manifold=None):
        """Prikazuje karticu za pojedinu petlju."""
        loop_id = loop.get("id")
        
        # Ekspander za petlju
        with st.expander(f"Petlja {loop_id}: {loop.get('room_name', '')}", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            # Prva kolona - unos parametara
            with col1:
                st.markdown("<div class='section-header'>Parametri petlje</div>", unsafe_allow_html=True)
                
                # Uklonjen dio s prikazom naziva prostorije jer je već prikazan u naslovu kartice
                
                # Temperatura prostorije
                room_temp = st.number_input(
                    "Temperatura prostorije [°C]",
                    min_value=15, max_value=30, value=get_room_temperature_for_name(loop.get("room_name", "")),
                    key=f"room_temp_{loop_id}",
                    on_change=lambda: self.calculation_handler._on_loop_param_change_with_manifold(loop_id, "room_temperature", data, floor, manifold)
                )
                loop["room_temperature"] = room_temp
                
                # Površina - bez početne vrijednosti
                area = st.number_input(
                    "Površina [m²]",
                    min_value=0.1, max_value=100.0, value=loop.get("area") if loop.get("area") is not None else None, 
                    placeholder="Unesi površinu",
                    key=f"area_{loop_id}",
                    format="%.2f",
                    step=0.5,
                    on_change=lambda: self.calculation_handler._on_loop_param_change_with_manifold(loop_id, "area", data, floor, manifold)
                )
                # Postavi vrijednost samo ako je korisnik unio nešto
                if area is not None:
                    loop["area"] = area
                
                # Podna obloga
                covering_options = [cov["name"] + f" (R_λB = {cov['r_lambda']})" for cov in FLOOR_COVERINGS]
                covering_index = 0
                for i, cov in enumerate(FLOOR_COVERINGS):
                    if cov["r_lambda"] == loop.get("r_lambda", 0.00):
                        covering_index = i
                        break
                covering = st.selectbox(
                    "Podna obloga",
                    options=covering_options,
                    index=covering_index,
                    key=f"covering_{loop_id}",
                    on_change=lambda: self.calculation_handler._on_covering_change_with_manifold(loop_id, data, floor, manifold)
                )
                # r_lambda će se postaviti u _on_covering_change()
                
                # Razmak cijevi
                spacing_options = [f"{spacing} cm" for spacing in PIPE_SPACINGS]
                spacing_index = PIPE_SPACINGS.index(loop.get("pipe_spacing", 15)) if loop.get("pipe_spacing") in PIPE_SPACINGS else 1
                spacing = st.selectbox(
                    "Razmak cijevi",
                    options=spacing_options,
                    index=spacing_index,
                    key=f"spacing_{loop_id}",
                    on_change=lambda: self.calculation_handler._on_loop_param_change_with_manifold(loop_id, "pipe_spacing", data, floor, manifold)
                )
                # pipe_spacing će se postaviti u _on_loop_param_change()
                
                # Udaljenost razdjelnika - bez početne vrijednosti
                manifold_distance = st.number_input(
                    "Udaljenost razdjelnika [m]",
                    min_value=0.0, max_value=20.0, value=loop.get("manifold_distance") if loop.get("manifold_distance") is not None else None, 
                    placeholder="Unesi udaljenost",
                    key=f"manifold_{loop_id}",
                    format="%.2f",
                    step=0.1,
                    on_change=lambda: self.calculation_handler._on_loop_param_change_with_manifold(loop_id, "manifold_distance", data, floor, manifold)
                )
                # Postavi vrijednost samo ako je korisnik unio nešto
                if manifold_distance is not None:
                    loop["manifold_distance"] = manifold_distance
                
                # Dodaj upozorenje ako nedostaje površina ili udaljenost razdjelnika
                if ("area" not in loop or loop.get("area") is None or 
                    "manifold_distance" not in loop or loop.get("manifold_distance") is None):
                    st.warning("Unesite površinu prostorije i udaljenost razdjelnika za izračun.")
                
                # Automatski izračunaj ako su svi potrebni parametri uneseni
                if floor and manifold:
                    self.calculation_handler._auto_calculate_loop_if_possible_with_manifold(loop_id, data, floor, manifold)

            # Druga kolona - originalni rezultati
            with col2:
                st.markdown("<div class='section-header'>Izračunate vrijednosti</div>", unsafe_allow_html=True)
                
                # Dohvati rezultate
                results = loop.get("results", {})
                
                # Originalne vrijednosti s originalnim redoslijedom
                st.metric("Toplinski tok", f"{results.get('heat_flux', 0):.2f} W/m²")
                st.metric("Snaga", f"{results.get('heat_load', 0):.2f} W")
                st.metric("Protok", f"{results.get('flow_rate_l_min', 0):.2f} l/min")
                st.metric("Pad tlaka", f"{results.get('pressure_drop', 0):.2f} kPa")
                
                # Dodana povratna temperatura - izračunata iz polazne temperature i delta T
                flow_temp = manifold.get("flow_temperature", 35) if manifold else 35
                delta_t = manifold.get("delta_t", 5) if manifold else 5
                return_temp = flow_temp - delta_t
                st.metric("Povratna temperatura", f"{return_temp:.2f} °C")
                
                st.metric("Temperatura poda", f"{results.get('floor_surface_temp', 0):.2f} °C")
                st.metric("Duljina cijevi", f"{results.get('pipe_length', 0):.2f} m")
            
            # Treća kolona - podešene vrijednosti i kontrole podešavanja
            with col3:
                # Provjeri postoje li podešeni rezultati
                has_adjusted_results = "adjusted_results" in loop and loop["adjusted_results"]
                adjusted_results = loop.get("adjusted_results", {}) if has_adjusted_results else {}
                
                st.markdown("<div class='section-header'>Podešene vrijednosti</div>", unsafe_allow_html=True)
                
                # Prikaži podešene vrijednosti ako postoje (promijenjen redoslijed da prati isti redoslijed kao original)
                if has_adjusted_results:
                    st.metric("Toplinski tok", f"{adjusted_results.get('heat_flux', 0):.2f} W/m²")
                    st.metric("Snaga", f"{adjusted_results.get('heat_load', 0):.2f} W")
                    st.metric("Protok", f"{adjusted_results.get('flow_rate_l_min', 0):.2f} l/min")
                    st.metric("Pad tlaka", f"{adjusted_results.get('pressure_drop', 0):.2f} kPa")
                    
                    # Koristimo već izračunatu povratnu temperaturu iz flow_adjuster-a
                    # Ona je već pravilno izračunata iterativnim postupkom i spremljena u rezultatima
                    adjusted_return_temp = adjusted_results.get('return_temperature', flow_temp - delta_t)
                    st.metric("Povratna temperatura", f"{adjusted_return_temp:.2f} °C")
                    
                    st.metric("Temperatura poda", f"{adjusted_results.get('floor_surface_temp', 0):.2f} °C")
                    
                    # Informacija o postotku podešavanja - ispravljeno formatiranje
                    adjustment_pct = adjusted_results.get("adjustment_percentage", 0)
                    sign = "+" if adjustment_pct >= 0 else "-"
                    abs_value = abs(adjustment_pct)
                    st.info(f"Protok je podešen za {sign}{abs_value} %")
                else:
                    st.caption("Nema podešenih vrijednosti")
                
                # Kontrole podešavanja
                st.markdown("<div class='section-header'>Podešavanje protoka</div>", unsafe_allow_html=True)
                
                # Slider za podešavanje postotka - dodano on_change za automatsku primjenu
                adjustment = st.slider(
                    "Postotak promjene protoka",
                    min_value=-50, max_value=50, value=0, step=5,
                    key=f"flow_adjustment_{loop_id}",
                    on_change=lambda: self.calculation_handler._on_flow_slider_change_with_manifold(loop_id, data, floor, manifold)
                )

    def render_results_tab(self, data):
        """Prikazuje tab s rezultatima proračuna."""
        st.header("Rezultati proračuna podnog grijanja")
        
        # Provjeri postoje li definirane etaže i razdjelnici
        if not data.get("building", {}).get("floors", []):
            st.warning("Potrebno je prvo definirati etaže i razdjelnike u tabu 'Zgrada i razdjelnici'.")
            return
        
        # Osnovni podaci o projektu
        st.subheader("Podaci o zgradi")
        st.caption(f"Naziv zgrade: {data['building'].get('name', 'Nova zgrada')}")
        
        # Ukupne vrijednosti za cijelu zgradu
        total_area_building = 0
        total_power_building = 0
        total_flow_building = 0
        total_pipe_length_building = 0
        total_water_volume_building = 0
        
        # Za svaku etažu
        for floor in data.get("building", {}).get("floors", []):
            with st.expander(f"Etaža: {floor.get('name', 'Etaža')}", expanded=True):
                st.caption(f"Debljina estriha: {floor.get('screed_thickness', 45)} mm")
                
                # Ukupne vrijednosti za etažu
                total_area_floor = 0
                total_power_floor = 0
                total_flow_floor = 0
                total_pipe_length_floor = 0
                total_water_volume_floor = 0
                
                # Za svaki razdjelnik na etaži
                for manifold in floor.get("manifolds", []):
                    st.markdown(f"#### Razdjelnik: {manifold.get('name', 'Razdjelnik')}")
                    
                    # Podaci o razdjelniku
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Polazna temperatura", f"{manifold.get('flow_temperature', 35)} °C")
                    col2.metric("Temperaturna razlika (ΔT)", f"{manifold.get('delta_t', 5)} °C")
                    
                    # Dohvati display format za promjer cijevi
                    pipe_display = PIPE_DATA.get(manifold.get("pipe_diameter", "16x2,0"), {}).get("display", manifold.get("pipe_diameter", "16x2,0"))
                    col3.metric("Promjer cijevi", pipe_display)
                    col4.metric("Debljina estriha", f"{floor.get('screed_thickness', 45)} mm")
                    
                    # Kreiraj podatke za tablicu petlji
                    table_data = []
                    total_area_manifold = 0
                    total_power_manifold = 0
                    total_flow_manifold = 0
                    total_pipe_length_manifold = 0
                    total_water_volume_manifold = 0
                    
                    # Dohvati sve petlje za ovaj razdjelnik
                    loops = manifold.get("loops", [])
                    rooms = sorted(manifold.get("rooms", []), key=lambda x: x.get("position", 0))
                    
                    # Mapiranje ID-a prostorije u poziciju za sortiranje petlji
                    room_positions = {room.get("id"): i for i, room in enumerate(rooms)}
                    
                    # Sortiraj petlje prema poziciji prostorija
                    sorted_loops = sorted(loops, key=lambda x: room_positions.get(x.get("id"), 999))
                    
                    # Za svaku petlju na razdjelniku
                    for loop in sorted_loops:
                        # Preskoči petlje bez svih potrebnih podataka
                        if not loop.get("results"):
                            continue
                            
                        # Provjeri postoje li podešeni rezultati
                        if "adjusted_results" in loop and loop["adjusted_results"]:
                            results = loop["adjusted_results"]
                        else:
                            results = loop.get("results", {})
                        
                        # Dohvati podatke za prikaz
                        room_name = loop.get("room_name", "")
                        room_temp = loop.get("room_temperature", 0)
                        area = loop.get("area", 0)
                        heat_flux = results.get("heat_flux", 0)
                        heat_load = results.get("heat_load", 0)
                        pipe_length = results.get("pipe_length", 0)
                        flow_rate_l_min = results.get("flow_rate_l_min", 0)
                        pressure_drop = results.get("pressure_drop", 0)
                        floor_temp = results.get("floor_surface_temp", 0)
                        
                        # Izračun volumena vode u petlji
                        try:
                            pipe_data = PIPE_DATA.get(manifold.get("pipe_diameter", "16x2,0"), {})
                            pipe_volume_per_meter = pipe_data.get("volume_per_meter", 0.113)  # Litara po metru
                            water_volume = pipe_volume_per_meter * pipe_length
                        except Exception:
                            water_volume = 0.0                        # Dodaj podatke za tablicu
                        table_data.append({
                            "Prostorija": room_name,
                            "Temp. [°C]": f"{room_temp:.1f}",
                            "Površina [m²]": f"{area:.2f}",
                            "Topl. tok [W/m²]": f"{heat_flux:.1f}",
                            "Snaga [W]": f"{heat_load:.0f}",
                            "Protok [l/min]": f"{flow_rate_l_min:.2f}",
                            "Pad tlaka [kPa]": f"{pressure_drop:.2f}",
                            "Duljina [m]": f"{pipe_length:.2f}",
                            "Voda [l]": f"{water_volume:.2f}",
                            "Temp. poda [°C]": f"{floor_temp:.1f}",
                        })
                        
                        # Dodaj vrijednosti u ukupne sume za razdjelnik
                        total_area_manifold += area
                        total_power_manifold += heat_load
                        total_flow_manifold += flow_rate_l_min
                        total_pipe_length_manifold += pipe_length
                        total_water_volume_manifold += water_volume
                    
                    # Dodaj volumen vode u polaznom i povratnom vodu razdjelnika
                    try:
                        supply_pipe_data = PIPE_DATA.get(manifold.get("supply_pipe_diameter", "20x2,0"), {})
                        supply_pipe_volume_per_meter = supply_pipe_data.get("volume_per_meter", 0.201)  # Litara po metru
                        supply_pipe_length = manifold.get("supply_pipe_length", 5.0)
                        return_pipe_length = manifold.get("return_pipe_length", 5.0)
                        connection_water_volume = supply_pipe_volume_per_meter * (supply_pipe_length + return_pipe_length)
                        total_water_volume_manifold += connection_water_volume
                    except Exception:
                        pass
                        
                    # Dodaj volumen vode u razdjelniku
                    try:
                        manifold_type = manifold.get("type", "7-krugova")
                        manifold_water_volume = MANIFOLD_TYPES.get(manifold_type, {}).get("volume", 1.0)
                        total_water_volume_manifold += manifold_water_volume
                        st.caption(f"Volumen vode u razdjelniku: {manifold_water_volume:.2f} l")
                    except Exception:
                        pass

                    # Prikaži tablicu petlji
                    if table_data:
                        st.dataframe(pd.DataFrame(table_data), use_container_width=True)
                    else:
                        st.info("Nema izračunatih petlji za ovaj razdjelnik.")
                      # Prikaži ukupne vrijednosti za razdjelnik
                    st.markdown("##### Ukupno za razdjelnik:")
                    col1, col2, col3, col4, col5 = st.columns(5)
                    col1.metric("Površina", f"{total_area_manifold:.2f} m²")
                    col2.metric("Snaga", f"{total_power_manifold:.0f} W")
                    col3.metric("Protok", f"{total_flow_manifold:.2f} l/min")
                    col4.metric("Duljina cijevi", f"{total_pipe_length_manifold:.2f} m")
                    col5.metric("Volumen vode", f"{total_water_volume_manifold:.2f} l")
                    
                    # Dodataj vrijednosti u ukupne sume za etažu
                    total_area_floor += total_area_manifold
                    total_power_floor += total_power_manifold
                    total_flow_floor += total_flow_manifold
                    total_pipe_length_floor += total_pipe_length_manifold
                    total_water_volume_floor += total_water_volume_manifold
                  # Prikaži ukupne vrijednosti za etažu
                st.markdown("#### Ukupno za etažu:")
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Površina", f"{total_area_floor:.2f} m²")
                col2.metric("Snaga", f"{total_power_floor:.0f} W")
                col3.metric("Protok", f"{total_flow_floor:.2f} l/min")
                col4.metric("Duljina cijevi", f"{total_pipe_length_floor:.2f} m")
                col5.metric("Volumen vode", f"{total_water_volume_floor:.2f} l")
                
                # Dodaj vrijednosti u ukupne sume za zgradu
                total_area_building += total_area_floor
                total_power_building += total_power_floor
                total_flow_building += total_flow_floor
                total_pipe_length_building += total_pipe_length_floor
                total_water_volume_building += total_water_volume_floor
          # Prikaži ukupne vrijednosti za cijelu zgradu
        st.markdown("### Ukupno za zgradu")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Površina", f"{total_area_building:.2f} m²")
        col2.metric("Snaga", f"{total_power_building:.0f} W")
        col3.metric("Protok", f"{total_flow_building:.2f} l/min")
        col4.metric("Duljina cijevi", f"{total_pipe_length_building:.2f} m")
        col5.metric("Volumen vode", f"{total_water_volume_building:.2f} l")
        
        # Objašnjenje
        if any(any("adjusted_results" in loop for loop in manifold.get("loops", [])) 
               for floor in data.get("building", {}).get("floors", []) 
               for manifold in floor.get("manifolds", [])):
            st.info("Napomena: Podešene vrijednosti protoka korištene su u zbroju umjesto originalnih izračunatih vrijednosti gdje su dostupne.")