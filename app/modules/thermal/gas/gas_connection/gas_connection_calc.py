"""
Glavna klasa kalkulatora za proračun plinskog priključka.
"""
import streamlit as st
import math
from modules.base import BaseCalculation
from .constants import *
from .data_tables import *
from .ui_components import *
from .calculation_utils import *
from .reporting import export_to_word as export_proracun_to_word

def styled_latex(formula):
    """
    Funkcija koja stilizira LaTeX formule.
    
    Args:
        formula: LaTeX formula kao string
    
    Returns:
        Stilizirana LaTeX formula
    """
    # Jednostavniji pristup - koristimo samo displaystyle
    return r"\displaystyle " + formula

def styled_text_as_latex(text):
    """
    Pretvara običan tekst u LaTeX stil teksta.
    
    Args:
        text: Običan tekst za stiliziranje
        
    Returns:
        LaTeX stiliziran tekst
    """
    # Jednostavniji pristup - direktno korištenje \text
    return r"\text{" + text + "}"

class GasConnectionCalc(BaseCalculation):
    """Kalkulator za proračun plinskog priključka."""
    
    def __init__(self, name="Proračun plinskog priključka"):
        """Inicijalizacija kalkulatora."""
        super().__init__(name)
        
        # Inicijalizacija session state
        if "gas_connection_data" not in st.session_state:
            st.session_state.gas_connection_data = self.initialize_data_structure()
    
    def initialize_data_structure(self):
        """Inicijalizira strukturu podataka."""
        return {
            # Osnovni podaci o zgradi
            "zgrada": {
                "tip": 1,  # 1 - stambena, 2 - višestambena, 3 - poslovna
                "broj_jedinica": 1,  # Broj stambenih jedinica (za višestambenu)
                "opis": "Obiteljska kuća"  # Opis zgrade
            },
            
            # Osnovni podaci o priključku
            "tip_prikljucka": 1,  # 1 - niskotlačni, 2 - srednjetlačni
            
            # Stambene jedinice i njihovi uređaji
            "stambene_jedinice": [
                {
                    "id": 1,
                    "naziv": "Stan 1",
                    # Podaci o kotlu
                    "kotao": {
                        "ima_kotao": True,  # True ako ima kotao
                        "tip": 1,            # 1 - kondenzacijski, 2 - klasični
                        "proizvodjac": "Vaillant",   # Proizvođač kotla
                        "model": "ecoTEC plus VUW 20/26 CS/1-5",         # Model kotla
                        "broj_kotlova": 1,   # Broj kotlova
                        "snaga_grijanja": 21.0,  # Snaga grijanja (kW)
                        "snaga_ptv": 26.0,       # Snaga PTV-a (kW)
                        "eta": ETA_KONDENZACIJSKI,         # Iskoristivost
                        "faktor": F_KOTAO[1],        # Faktor istovremenosti
                        "vrsni_protok": 0.0  # Vršni protok za kotao
                    },
                    
                    # Podaci o ploči/štednjaku
                    "plinski_uredjaj": {
                        "ima_uredjaj": False,  # True ako ima ploču/štednjak
                        "tip": 1,              # 1 - ploča, 2 - štednjak
                        "naziv": "Plinska ploča",  # Naziv uređaja
                        "broj_uredjaja": 1,    # Broj uređaja
                        "broj_plamenika": 2,   # Broj plamenika
                        "ima_pecnicu": False,  # True ako ima pećnicu
                        "snaga_jedinicna": 4.0,  # Snaga jednog uređaja (kW)
                        "snaga_ukupna": 4.0,     # Ukupna snaga (kW)
                        "eta": ETA_PLOCA,           # Iskoristivost
                        "faktor": F_PLOCA_2[1],     # Faktor istovremenosti
                        "vrsni_protok": 0.0  # Vršni protok za plinski uređaj
                    },
                    
                    # Ukupni vršni protok za stambenu jedinicu
                    "vrsni_protok": 0.0
                }
            ],
            
            # Podaci o cijevi
            "cijev": {
                "tip": 1,              # 1 - PE-HD, 2 - SMLS
                "oznaka": "",          # Oznaka cijevi
                "duljina": 10.0,       # Duljina cjevovoda (m)
                "dimenzije": {
                    "vanjski": 0.0,    # Vanjski promjer (mm)
                    "debljina": 0.0,   # Debljina stijenke (mm)
                    "unutarnji": 0.0   # Unutarnji promjer (mm)
                }
            },
            
            # Rezultati proračuna
            "rezultati": {
                "vrsni_protok": 0.0,     # Ukupni vršni protok (m³/h)
                "vrsni_protok_po_jedinici": [],  # Lista vršnih protoka po jedinici
                "potreban_promjer": 0.0,  # Potreban promjer (mm)
                "stvarna_brzina": 0.0,    # Stvarna brzina (m/s)
                "pad_tlaka": 0.0,         # Pad tlaka (mbar)
                "plinomjer": None         # Odabrani plinomjer
            }
        }
    
    def render(self):
        """Prikazuje sučelje kalkulatora."""
        st.title(self.name)
        
        # Definiranje tabova
        tab1, tab2, tab3 = st.tabs(["Podaci o objektu", "Dimenzioniranje priključka", "Rezultati"])
        
        with tab1:
            self.render_building_data()
            
        with tab2:
            self.render_connection_data()
            
        with tab3:
            self.render_results_section()
    
    def render_building_data(self):
        """Prikaz prvog taba - podaci o objektu i uređajima."""
        data = st.session_state.gas_connection_data
        
        # Objašnjenje kalkulatora
        with st.expander("O kalkulatoru", expanded=False):
            st.markdown("""
            ### Proračun plinskog priključka
            
            Ovaj kalkulator omogućava dimenzioniranje plinskog priključka za stambene i poslovne objekte. Kalkulator provodi proračun:
            - vršnog protoka plina na temelju odabranih uređaja
            - potrebnog promjera cijevi
            - stvarne brzine plina u cijevi
            - pada tlaka za odabranu cijev i duljinu cjevovoda
            - odabira odgovarajućeg plinomjera
            
            Proračun se provodi prema važećim tehničkim propisima za plinske instalacije.
            """)
        
        # Odabir vrste zgrade
        st.subheader("Vrsta objekta")
        
        building_options = ["Stambena zgrada", "Višestambena zgrada", "Poslovna zgrada"]
        
        zgrada_tip = st.radio(
            "Odaberite vrstu objekta:",
            options=building_options,
            index=data["zgrada"]["tip"] - 1,
            horizontal=True
        )
        
        # Postavljanje tipa zgrade
        data["zgrada"]["tip"] = building_options.index(zgrada_tip) + 1
        
        # Za višestambenu zgradu definiramo broj jedinica
        if data["zgrada"]["tip"] == 2:  # Višestambena
            broj_jedinica = st.number_input(
                "Broj stambenih jedinica:",
                min_value=2,
                max_value=100,
                value=data["zgrada"]["broj_jedinica"] if data["zgrada"]["broj_jedinica"] > 1 else 2,
                step=1
            )
            
            if broj_jedinica != data["zgrada"]["broj_jedinica"]:
                # Ažuriramo broj stambenih jedinica
                data["zgrada"]["broj_jedinica"] = broj_jedinica
                
                # Stvaramo odgovarajući broj jedinica u listi
                trenutno_jedinica = len(data["stambene_jedinice"])
                
                if broj_jedinica > trenutno_jedinica:
                    # Dodajemo nove jedinice
                    for i in range(trenutno_jedinica + 1, broj_jedinica + 1):
                        nova_jedinica = {
                            "id": i,
                            "naziv": f"Stan {i}",
                            "kotao": {
                                "ima_kotao": True,
                                "tip": 1,
                                "proizvodjac": "Vaillant",
                                "model": "ecoTEC plus VUW 20/26 CS/1-5",
                                "broj_kotlova": 1,
                                "snaga_grijanja": 21.0,
                                "snaga_ptv": 26.0,
                                "eta": ETA_KONDENZACIJSKI,
                                "faktor": F_KOTAO[1],
                                "vrsni_protok": 0.0
                            },
                            "plinski_uredjaj": {
                                "ima_uredjaj": False,
                                "tip": 1,
                                "naziv": "Plinska ploča",
                                "broj_uredjaja": 1,
                                "broj_plamenika": 2,
                                "ima_pecnicu": False,
                                "snaga_jedinicna": 4.0,
                                "snaga_ukupna": 4.0,
                                "eta": ETA_PLOCA,
                                "faktor": F_PLOCA_2[1],
                                "vrsni_protok": 0.0
                            },
                            "vrsni_protok": 0.0
                        }
                        data["stambene_jedinice"].append(nova_jedinica)
                elif broj_jedinica < trenutno_jedinica:
                    # Uklanjamo suvišne jedinice
                    data["stambene_jedinice"] = data["stambene_jedinice"][:broj_jedinica]
            
            # Prikaz taba za odabir jedinice
            stan_tabovi = []
            
            for i in range(broj_jedinica):
                stan_tabovi.append(f"Stan {i+1}")
                
            selected_stan = st.radio(
                "Odaberite stambenu jedinicu:",
                options=stan_tabovi,
                horizontal=True
            )
            
            # Indeks odabrane jedinice
            jedinica_index = stan_tabovi.index(selected_stan)
            
            st.markdown("---")
            st.subheader(f"Uređaji - {selected_stan}")
            
            # Prikaz uređaja za odabranu stambenu jedinicu
            self._render_unit_devices(data["stambene_jedinice"][jedinica_index])
            
        else:  # Stambena ili poslovna zgrada
            data["zgrada"]["broj_jedinica"] = 1
            
            # Osiguravamo da imamo barem jednu stambenu jedinicu
            if len(data["stambene_jedinice"]) == 0:
                data["stambene_jedinice"].append({
                    "id": 1,
                    "naziv": "Stan 1",
                    "kotao": {
                        "ima_kotao": True,
                        "tip": 1,
                        "proizvodjac": "Vaillant",
                        "model": "ecoTEC plus VUW 20/26 CS/1-5",
                        "broj_kotlova": 1,
                        "snaga_grijanja": 21.0,
                        "snaga_ptv": 26.0,
                        "eta": ETA_KONDENZACIJSKI,
                        "faktor": F_KOTAO[1],
                        "vrsni_protok": 0.0
                    },
                    "plinski_uredjaj": {
                        "ima_uredjaj": False,
                        "tip": 1,
                        "naziv": "Plinska ploča",
                        "broj_uredjaja": 1,
                        "broj_plamenika": 2,
                        "ima_pecnicu": False,
                        "snaga_jedinicna": 4.0,
                        "snaga_ukupna": 4.0,
                        "eta": ETA_PLOCA,
                        "faktor": F_PLOCA_2[1],
                        "vrsni_protok": 0.0
                    },
                    "vrsni_protok": 0.0
                })
            
            # Radi jednostavnosti ograničavamo na jednu jedinicu
            if len(data["stambene_jedinice"]) > 1:
                data["stambene_jedinice"] = data["stambene_jedinice"][:1]
            
            st.markdown("---")
            st.subheader("Plinski uređaji")
            
            # Prikaz uređaja za jedinu stambenu jedinicu
            self._render_unit_devices(data["stambene_jedinice"][0])
            
        # Automatski izračun vršnog protoka za svaku jedinicu
        self._calculate_flow_rates()
        
        # Pregled izračunatih vršnih protoka
        st.markdown("---")
        st.subheader("Pregled vršnih protoka")
        
        for i, jedinica in enumerate(data["stambene_jedinice"]):
            # Ako je stambena zgrada, ne prikazuj "Stan 1" nego samo vršni protok
            if data["zgrada"]["tip"] == 1:  # Stambena zgrada
                st.markdown(f"**Vršni protok**: {jedinica['vrsni_protok']:.2f} m³/h")
            else:  # Višestambena ili poslovna zgrada
                st.markdown(f"**{jedinica['naziv']}**: {jedinica['vrsni_protok']:.2f} m³/h")
            
            # Detaljan prikaz
            if data["zgrada"]["tip"] == 1:
                # Za stambenu zgradu ne navodi se ime stambene jedinice
                expander_title = "Detalji izračuna"
            else:
                expander_title = f"Detalji izračuna - {jedinica['naziv']}"
                
            with st.expander(expander_title, expanded=False):
                if jedinica["kotao"]["ima_kotao"]:
                    st.write(f"**Kotao**: {jedinica['kotao']['vrsni_protok']:.2f} m³/h")
                    
                    P_koristeno = max(
                        jedinica["kotao"]["snaga_grijanja"],
                        jedinica["kotao"]["snaga_ptv"]
                    ) * jedinica["kotao"]["broj_kotlova"]
                    
                    st.write(f"P = {P_koristeno:.2f} kW")
                    st.write(f"η = {jedinica['kotao']['eta']:.2f}")
                    st.write(f"f = {jedinica['kotao']['faktor']:.3f}")
                    st.write(f"Hd = {HD:.2f} kWh/m³")
                    
                    st.latex(styled_latex(f"Qk = \\frac{{P \\cdot f}}{{Hd \\cdot \\eta}} = \\frac{{{P_koristeno:.2f} \\cdot {jedinica['kotao']['faktor']:.3f}}}{{{HD:.2f} \\cdot {jedinica['kotao']['eta']:.2f}}} = {jedinica['kotao']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
                
                if jedinica["plinski_uredjaj"]["ima_uredjaj"]:
                    st.write(f"**{jedinica['plinski_uredjaj']['naziv']}**: {jedinica['plinski_uredjaj']['vrsni_protok']:.2f} m³/h")
                    
                    st.write(f"P = {jedinica['plinski_uredjaj']['snaga_ukupna']:.2f} kW")
                    st.write(f"η = {jedinica['plinski_uredjaj']['eta']:.2f}")
                    st.write(f"f = {jedinica['plinski_uredjaj']['faktor']:.3f}")
                    st.write(f"Hd = {HD:.2f} kWh/m³")
                    
                    st.latex(styled_latex(f"Qp = \\frac{{P \\cdot f}}{{Hd \\cdot \\eta}} = \\frac{{{jedinica['plinski_uredjaj']['snaga_ukupna']:.2f} \\cdot {jedinica['plinski_uredjaj']['faktor']:.3f}}}{{{HD:.2f} \\cdot {jedinica['plinski_uredjaj']['eta']:.2f}}} = {jedinica['plinski_uredjaj']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
        
        # Ukupni vršni protok priključka
        ukupni_vrsni_protok = data["rezultati"]["vrsni_protok"]
        st.markdown(f"### Ukupni vršni protok priključka: {ukupni_vrsni_protok:.2f} m³/h")
        
        if data["zgrada"]["tip"] == 2 and len(data["stambene_jedinice"]) > 1:
            st.info(f"""
            **Napomena:** Za višestambene zgrade primjenjuje se posebna logika izračuna ukupnog vršnog protoka.
            Svaka stambena jedinica se računa zasebno, s vlastitim faktorima istovremenosti,
            a njihovi se vršni protoci zatim zbrajaju, uzimajući u obzir dodatni faktor istovremenosti između stanova.
            """)
    
    def _render_unit_devices(self, jedinica):
        """Prikaz uređaja za pojedinu stambenu jedinicu."""
        # Odabir kotla
        render_boiler_selection(jedinica["kotao"])
        st.markdown("---")
        
        # Odabir plinskog štednjaka/ploče
        render_stove_selection(jedinica["plinski_uredjaj"])
        
        # Poruka ako nema uređaja
        if not jedinica["kotao"]["ima_kotao"] and not jedinica["plinski_uredjaj"]["ima_uredjaj"]:
            st.warning("Odaberite barem jedan plinski uređaj za proračun.")
    
    def render_connection_data(self):
        """Prikaz drugog taba - podaci o priključku i dimenzioniranje cijevi."""
        data = st.session_state.gas_connection_data
        
        # Provjerimo prvo ima li uređaja
        has_devices = False
        for jedinica in data["stambene_jedinice"]:
            if jedinica["kotao"]["ima_kotao"] or jedinica["plinski_uredjaj"]["ima_uredjaj"]:
                has_devices = True
                break
                
        if not has_devices:
            st.warning("Prvo odaberite plinske uređaje u tabu 'Podaci o objektu'.")
            return
        
        # Odabir vrste plinskog priključka
        render_connection_type_selection(data)
        
        # Prikaz vršnog protoka plina
        st.subheader("Vršni protok plina")
        st.info(f"Ukupni vršni protok plina: **{data['rezultati']['vrsni_protok']:.2f} m³/h**")
        
        # Izračun potrebnog promjera na temelju vršnog protoka
        data["rezultati"]["potreban_promjer"] = calculate_required_diameter(data["rezultati"]["vrsni_protok"])
        st.info(f"Potreban promjer cijevi: **{data['rezultati']['potreban_promjer']:.2f} mm**")
        
        st.markdown("---")
        
        # Unos duljine cjevovoda
        render_pipe_length_input(data)
        
        st.markdown("---")
        
        # Odabir cijevi
        render_pipe_selection(data)
        
        # Izračun stvarne brzine i pada tlaka
        if data["cijev"]["oznaka"] and data["cijev"]["dimenzije"]["unutarnji"] > 0:
            # Izračun stvarne brzine
            data["rezultati"]["stvarna_brzina"] = calculate_actual_velocity(
                data["rezultati"]["vrsni_protok"], data["cijev"]["dimenzije"]["unutarnji"])
            
            # Izračun pada tlaka ovisno o vrsti priključka
            if data["tip_prikljucka"] == 1:  # Niskotlačni
                data["rezultati"]["pad_tlaka"] = calculate_pressure_drop_low_pressure(
                    data["rezultati"]["vrsni_protok"], 
                    data["cijev"]["duljina"], 
                    data["cijev"]["dimenzije"]["unutarnji"], 
                    data["cijev"]["tip"]
                )
            else:  # Srednjetlačni
                data["rezultati"]["pad_tlaka"] = calculate_pressure_drop_medium_pressure(
                    data["rezultati"]["vrsni_protok"], 
                    data["cijev"]["duljina"], 
                    data["cijev"]["dimenzije"]["unutarnji"], 
                    data["rezultati"]["stvarna_brzina"], 
                    data["cijev"]["tip"]
                )
            
            # Prikaz rezultata dimenzioniranja
            st.markdown("---")
            st.subheader("Rezultati dimenzioniranja")
            
            # Dodana informacija o unutarnjem promjeru s potvrdom da zadovoljava potreban promjer
            # i smještanje stvarne brzine i pada tlaka u isti red
            col1, col2, col3 = st.columns(3)
            
            if data["rezultati"]["stvarna_brzina"] > 0:
                with col1:
                    unutarnji_promjer = data['cijev']['dimenzije']['unutarnji']
                    potreban_promjer = data['rezultati']['potreban_promjer']
                    je_zadovoljen = unutarnji_promjer >= potreban_promjer
                    
                    st.metric(
                        "Unutarnji promjer", 
                        f"{unutarnji_promjer:.2f} mm",
                        delta=f"Potreban: {potreban_promjer:.2f} mm",
                        delta_color="normal" if je_zadovoljen else "inverse",
                        help=f"Unutarnji promjer odabrane cijevi. Mora biti veći ili jednak potrebnom promjeru ({potreban_promjer:.2f} mm)."
                    )
                
                with col2:
                    # Indikator brzine s bojom ovisno o graničnoj vrijednosti
                    je_u_granicama_brzina = data["rezultati"]["stvarna_brzina"] <= STANDARD_BRZINA * 1.1
                    
                    st.metric(
                        "Stvarna brzina", 
                        f"{data['rezultati']['stvarna_brzina']:.2f} m/s",
                        delta=f"Max: {STANDARD_BRZINA:.1f} m/s",
                        delta_color="normal" if je_u_granicama_brzina else "inverse",
                        help="Stvarna brzina protoka plina u odabranoj cijevi"
                    )
                
                if data["rezultati"]["pad_tlaka"] > 0:
                    with col3:
                        # Indikator pada tlaka s bojom ovisno o graničnoj vrijednosti
                        max_pad = MAX_PAD_TLAKA_NISKOTLACNI if data["tip_prikljucka"] == 1 else MAX_PAD_TLAKA_SREDNJETLACNI
                        je_u_granicama_tlak = data["rezultati"]["pad_tlaka"] <= max_pad
                        
                        st.metric(
                            "Pad tlaka", 
                            f"{data['rezultati']['pad_tlaka']:.2f} mbar",
                            delta=f"Max: {max_pad:.1f} mbar",
                            delta_color="normal" if je_u_granicama_tlak else "inverse",
                            help=f"Pad tlaka kroz cjevovod duljine {data['cijev']['duljina']:.1f} m"
                        )
        
        # Odabir plinomjera
        data["rezultati"]["plinomjer"] = select_gas_meter(data["rezultati"]["vrsni_protok"])
        
        # Zabilježimo promjene
        self.record_state("Dimenzioniranje plinskog priključka")
        self.state_manager.set_calculation_changed(True)
    
    def _calculate_flow_rates(self):
        """Izračunava vršne protoke za svaku stambenu jedinicu i ukupni vršni protok."""
        data = st.session_state.gas_connection_data
        
        # Resetiramo rezultate vršnih protoka
        data["rezultati"]["vrsni_protok"] = 0.0
        data["rezultati"]["vrsni_protok_po_jedinici"] = []
        
        # Izračunavamo protok za svaku jedinicu
        for i, jedinica in enumerate(data["stambene_jedinice"]):
            jedinica_protok = 0.0
            
            # Protok za kotao
            if jedinica["kotao"]["ima_kotao"]:
                P_koristeno = max(
                    jedinica["kotao"]["snaga_grijanja"],
                    jedinica["kotao"]["snaga_ptv"]
                ) * jedinica["kotao"]["broj_kotlova"]
                
                # Vršni protok kotla = (P * f) / (Hd * eta)
                vrsni_protok_kotao = calculate_flow_rate(P_koristeno, jedinica["kotao"]["eta"], jedinica["kotao"]["faktor"])
                jedinica["kotao"]["vrsni_protok"] = vrsni_protok_kotao
                jedinica_protok += vrsni_protok_kotao
            else:
                jedinica["kotao"]["vrsni_protok"] = 0.0
            
            # Protok za plinski uređaj
            if jedinica["plinski_uredjaj"]["ima_uredjaj"]:
                # Vršni protok plinskog uređaja = (P * f) / (Hd * eta)
                vrsni_protok_uredjaj = calculate_flow_rate(
                    jedinica["plinski_uredjaj"]["snaga_ukupna"], 
                    jedinica["plinski_uredjaj"]["eta"], 
                    jedinica["plinski_uredjaj"]["faktor"]
                )
                jedinica["plinski_uredjaj"]["vrsni_protok"] = vrsni_protok_uredjaj
                jedinica_protok += vrsni_protok_uredjaj
            else:
                jedinica["plinski_uredjaj"]["vrsni_protok"] = 0.0
            
            # Spremanje vršnog protoka za stambenu jedinicu
            jedinica["vrsni_protok"] = jedinica_protok
            data["rezultati"]["vrsni_protok_po_jedinici"].append(jedinica_protok)
        
        # Izračun ukupnog vršnog protoka prema tipu zgrade
        if data["zgrada"]["tip"] == 2 and len(data["stambene_jedinice"]) > 1:
            # Višestambena zgrada - koristimo posebnu logiku
            # Primjenjujemo faktor istovremenosti između stanova
            broj_jedinica = len(data["stambene_jedinice"])
            faktor_istovremenosti_stanova = 1.0 / math.sqrt(broj_jedinica - 1) if broj_jedinica > 1 else 1.0
            
            # Ograničimo faktor istovremenosti na minimalno 0.5 i maksimalno 1.0
            faktor_istovremenosti_stanova = max(0.5, min(1.0, faktor_istovremenosti_stanova))
            
            # Ukupni vršni protok je suma vršnih protoka po jedinicama pomnožena faktorom istovremenosti
            data["rezultati"]["vrsni_protok"] = sum(data["rezultati"]["vrsni_protok_po_jedinici"]) * faktor_istovremenosti_stanova
        else:
            # Stambena ili poslovna zgrada - jednostavna suma
            data["rezultati"]["vrsni_protok"] = sum(data["rezultati"]["vrsni_protok_po_jedinici"])

    def render_results_section(self):
        """Prikaz trećeg taba - rezultati proračuna."""
        st.subheader("Rezultati proračuna")
        
        data = st.session_state.gas_connection_data
        
        # Provjeri ima li uređaja
        has_devices = False
        for jedinica in data["stambene_jedinice"]:
            if jedinica["kotao"]["ima_kotao"] or jedinica["plinski_uredjaj"]["ima_uredjaj"]:
                has_devices = True
                break
                
        if not has_devices:
            st.warning("Odaberite barem jedan plinski uređaj za prikaz rezultata proračuna.")
            return
        
        # Prikaži informaciju ako još nema rezultata
        if data["rezultati"]["vrsni_protok"] == 0.0:
            st.info("Unesite podatke u prethodnim tabovima za prikaz rezultata.")
            return
        
        # Osnovni podaci
        st.write("### Osnovni parametri proračuna")
        
        # Vrsta objekta
        zgrada_tipovi = ["Stambena zgrada", "Višestambena zgrada", "Poslovna zgrada"]
        zgrada_tip = zgrada_tipovi[data["zgrada"]["tip"] - 1]
        
        # Ako je višestambena, prikaži broj jedinica
        if data["zgrada"]["tip"] == 2:
            st.write(f"**Vrsta objekta:** {zgrada_tip} ({data['zgrada']['broj_jedinica']} stambenih jedinica)")
        else:
            st.write(f"**Vrsta objekta:** {zgrada_tip}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tip_prikljucka = "Niskotlačni" if data["tip_prikljucka"] == 1 else "Srednjetlačni"
            st.metric(
                "Vrsta plinskog priključka", 
                tip_prikljucka, 
                help="Niskotlačni: do 100 mbar, Srednjetlačni: 0,1-5,0 bar"
            )
        
        with col2:
            st.metric(
                "Duljina cjevovoda", 
                f"{data['cijev']['duljina']:.1f} m",
                help="Ukupna duljina cjevovoda od priključnog mjesta do plinomjera"
            )
        
        # Prikaz rezultata proračuna
        st.markdown("---")
        st.write("### Rezultati izračuna")
        
        # Prikaz preko metrika - 2 reda po 2 stupca
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Vršni protok", 
                f"{data['rezultati']['vrsni_protok']:.2f} m³/h",
                help="Ukupni vršni protok plina za sve odabrane uređaje"
            )
        
        with col2:
            st.metric(
                "Potreban promjer", 
                f"{data['rezultati']['potreban_promjer']:.2f} mm",
                help="Minimalni potrebni unutarnji promjer cijevi za protok plina"
            )
        
        # Odabrana cijev - premješteno nakon rezultata izračuna
        if data["cijev"]["oznaka"]:
            st.markdown("---")
            st.write("### Odabrana cijev")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Promijenjeno da prikazuje puni naziv cijevi s kraticom u zagradi
                if data["cijev"]["tip"] == 1:
                    naziv_cijevi = "Polietilen visoke gustoće (PE-HD)"
                else:
                    naziv_cijevi = "Bešavna čelična cijev (SMLS)"
                st.metric("Vrsta cijevi", naziv_cijevi)
            
            with col2:
                st.metric("Oznaka cijevi", data["cijev"]["oznaka"])
            
            with col3:
                st.metric(
                    "Dimenzije cijevi", 
                    f"Ø{data['cijev']['dimenzije']['vanjski']}×{data['cijev']['dimenzije']['debljina']} mm"
                )
                
            # Dodana informacija o unutarnjem promjeru s potvrdom da zadovoljava potreban promjer
            col1, col2, col3 = st.columns(3)
            
            if data["rezultati"]["stvarna_brzina"] > 0:
                with col1:
                    unutarnji_promjer = data['cijev']['dimenzije']['unutarnji']
                    potreban_promjer = data['rezultati']['potreban_promjer']
                    je_zadovoljen = unutarnji_promjer >= potreban_promjer
                    
                    st.metric(
                        "Unutarnji promjer", 
                        f"{unutarnji_promjer:.2f} mm",
                        delta=f"Potreban: {potreban_promjer:.2f} mm",
                        delta_color="normal" if je_zadovoljen else "inverse",
                        help=f"Unutarnji promjer odabrane cijevi. Mora biti veći ili jednak potrebnom promjeru ({potreban_promjer:.2f} mm)."
                    )
                
                with col2:
                    # Indikator brzine s bojom ovisno o graničnoj vrijednosti
                    je_u_granicama_brzina = data["rezultati"]["stvarna_brzina"] <= STANDARD_BRZINA * 1.1
                    
                    st.metric(
                        "Stvarna brzina", 
                        f"{data['rezultati']['stvarna_brzina']:.2f} m/s",
                        delta=f"Max: {STANDARD_BRZINA:.1f} m/s",
                        delta_color="normal" if je_u_granicama_brzina else "inverse",
                        help="Stvarna brzina protoka plina u odabranoj cijevi"
                    )
                
                if data["rezultati"]["pad_tlaka"] > 0:
                    with col3:
                        # Indikator pada tlaka s bojom ovisno o graničnoj vrijednosti
                        max_pad = MAX_PAD_TLAKA_NISKOTLACNI if data["tip_prikljucka"] == 1 else MAX_PAD_TLAKA_SREDNJETLACNI
                        je_u_granicama_tlak = data["rezultati"]["pad_tlaka"] <= max_pad
                        
                        st.metric(
                            "Pad tlaka", 
                            f"{data['rezultati']['pad_tlaka']:.2f} mbar",
                            delta=f"Max: {max_pad:.1f} mbar",
                            delta_color="normal" if je_u_granicama_tlak else "inverse",
                            help=f"Pad tlaka kroz cjevovod duljine {data['cijev']['duljina']:.1f} m"
                        )
        
        # Odabir plinomjera
        if data["rezultati"]["plinomjer"]:
            oznaka, spec = data["rezultati"]["plinomjer"]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Oznaka plinomjera", oznaka)
            
            with col2:
                st.metric("Nazivni promjer", f"DN {spec['DN']}")
            
            with col3:
                st.metric(
                    "Raspon protoka", 
                    f"{spec['Qmin']} - {spec['Qmax']} m³/h",
                    help=f"Minimalni protok: {spec['Qmin']} m³/h, Maksimalni protok: {spec['Qmax']} m³/h"
                )
            
            # Provjera odgovara li plinomjer potrebnom protoku
            if data["rezultati"]["vrsni_protok"] > spec['Qmax']:
                st.error(f"UPOZORENJE: Vršni protok ({data['rezultati']['vrsni_protok']:.2f} m³/h) premašuje maksimalni protok plinomjera ({spec['Qmax']} m³/h)!")
        
        # Detalji proračuna
        with st.expander("Detalji proračuna", expanded=False):
            # Naslov sekcije - normalan tekst
            st.write("#### Proračun vršnog protoka")
            
            # Prikaz vršnog protoka po jedinicama
            for i, jedinica in enumerate(data["stambene_jedinice"]):
                # Naziv jedinice i protok - LaTeX stil
                st.latex(styled_latex(f"\\textbf{{{jedinica['naziv']}}}: {jedinica['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
                
                if jedinica["kotao"]["ima_kotao"]:
                    P_koristeno = max(
                        jedinica["kotao"]["snaga_grijanja"],
                        jedinica["kotao"]["snaga_ptv"]
                    ) * jedinica["kotao"]["broj_kotlova"]
                    
                    # Informacije o kotlu - LaTeX stil
                    st.latex(styled_latex(f"\\text{{Kotao: }} {jedinica['kotao']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
                    st.latex(styled_latex(f"P = {P_koristeno:.2f} \\, \\text{{kW}}"))
                    st.latex(styled_latex(f"\\eta = {jedinica['kotao']['eta']:.2f}"))
                    st.latex(styled_latex(f"f = {jedinica['kotao']['faktor']:.3f}"))
                    st.latex(styled_latex(f"H_d = {HD:.2f} \\, \\text{{kWh/m}}^3"))
                    
                    # Formula za izračun protoka
                    st.latex(styled_latex(f"Q_k = \\frac{{P \\cdot f}}{{H_d \\cdot \\eta}} = \\frac{{{P_koristeno:.2f} \\cdot {jedinica['kotao']['faktor']:.3f}}}{{{HD:.2f} \\cdot {jedinica['kotao']['eta']:.2f}}} = {jedinica['kotao']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
                
                if jedinica["plinski_uredjaj"]["ima_uredjaj"]:
                    # Informacije o plinskom uređaju - LaTeX stil
                    st.latex(styled_latex(f"\\text{{{jedinica['plinski_uredjaj']['naziv']}: }} {jedinica['plinski_uredjaj']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
                    st.latex(styled_latex(f"P = {jedinica['plinski_uredjaj']['snaga_ukupna']:.2f} \\, \\text{{kW}}"))
                    st.latex(styled_latex(f"\\eta = {jedinica['plinski_uredjaj']['eta']:.2f}"))
                    st.latex(styled_latex(f"f = {jedinica['plinski_uredjaj']['faktor']:.3f}"))
                    st.latex(styled_latex(f"H_d = {HD:.2f} \\, \\text{{kWh/m}}^3"))
                    
                    # Formula za izračun protoka
                    st.latex(styled_latex(f"Q_p = \\frac{{P \\cdot f}}{{H_d \\cdot \\eta}} = \\frac{{{jedinica['plinski_uredjaj']['snaga_ukupna']:.2f} \\cdot {jedinica['plinski_uredjaj']['faktor']:.3f}}}{{{HD:.2f} \\cdot {jedinica['plinski_uredjaj']['eta']:.2f}}} = {jedinica['plinski_uredjaj']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
            
            # Za višestambene zgrade prikaži faktor istovremenosti između stanova
            if data["zgrada"]["tip"] == 2 and len(data["stambene_jedinice"]) > 1:
                broj_jedinica = len(data["stambene_jedinice"])
                faktor_istovremenosti_stanova = 1.0 / math.sqrt(broj_jedinica - 1) if broj_jedinica > 1 else 1.0
                faktor_istovremenosti_stanova = max(0.5, min(1.0, faktor_istovremenosti_stanova))
                
                # Faktor istovremenosti - LaTeX stil
                st.latex(styled_latex(f"\\text{{Faktor istovremenosti između stanova: }} {faktor_istovremenosti_stanova:.3f}"))
                st.latex(styled_latex(f"f_{{si}} = \\frac{{1}}{{\\sqrt{{n-1}}}} = \\frac{{1}}{{\\sqrt{{{broj_jedinica}-1}}}} = {faktor_istovremenosti_stanova:.3f}"))
                
                # Ukupni vršni protok - LaTeX stil
                st.latex(styled_latex(f"\\text{{Ukupni vršni protok: }} {sum(data['rezultati']['vrsni_protok_po_jedinici']):.2f} \\, \\text{{m}}^3\\text{{/h}} \\times {faktor_istovremenosti_stanova:.3f} = {data['rezultati']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
                st.latex(styled_latex(f"Q_{{vrs}} = \\sum Q_i \\cdot f_{{si}} = {sum(data['rezultati']['vrsni_protok_po_jedinici']):.2f} \\cdot {faktor_istovremenosti_stanova:.3f} = {data['rezultati']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
            else:
                # Ukupni vršni protok - LaTeX stil
                st.latex(styled_latex(f"\\text{{Ukupni vršni protok: }} {data['rezultati']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
            
            # Naslov sekcije - normalan tekst
            st.write("#### Proračun potrebnog promjera cijevi")
            
            # Vrijednosti protoka i brzine - LaTeX stil
            st.latex(styled_latex(f"Q = {data['rezultati']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}} = {data['rezultati']['vrsni_protok']/3600:.6f} \\, \\text{{m}}^3\\text{{/s}}"))
            st.latex(styled_latex(f"w = {STANDARD_BRZINA:.1f} \\, \\text{{m/s}}"))
            
            # LaTeX formula za promjer cijevi
            st.latex(styled_latex(r"d = \sqrt{\frac{4 \cdot Q}{\pi \cdot w}}"))
            st.latex(styled_latex(f"d = \\sqrt{{\\frac{{4 \\cdot {data['rezultati']['vrsni_protok']/3600:.6f}}}{{\\pi \\cdot {STANDARD_BRZINA:.1f}}}}} = {data['rezultati']['potreban_promjer']:.2f} \\, \\text{{mm}}"))
            
            if data["rezultati"]["stvarna_brzina"] > 0:
                # Naslov sekcije - normalan tekst
                st.write("#### Proračun stvarne brzine u cijevi")
                
                # Vrijednosti protoka i promjera - LaTeX stil
                st.latex(styled_latex(f"Q = {data['rezultati']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}} = {data['rezultati']['vrsni_protok']/3600:.6f} \\, \\text{{m}}^3\\text{{/s}}"))
                st.latex(styled_latex(f"d = {data['cijev']['dimenzije']['unutarnji']:.2f} \\, \\text{{mm}} = {data['cijev']['dimenzije']['unutarnji']/1000:.6f} \\, \\text{{m}}"))
                
                # LaTeX formula za brzinu
                st.latex(styled_latex(r"w = \frac{4 \cdot Q}{\pi \cdot d^2}"))
                st.latex(styled_latex(f"w = \\frac{{4 \\cdot {data['rezultati']['vrsni_protok']/3600:.6f}}}{{\\pi \\cdot {data['cijev']['dimenzije']['unutarnji']/1000:.6f}^2}} = {data['rezultati']['stvarna_brzina']:.2f} \\, \\text{{m/s}}"))
            
            if data["rezultati"]["pad_tlaka"] > 0:
                # Naslov sekcije - normalan tekst
                st.write("#### Proračun pada tlaka")
                
                lambda_koef = LAMBDA_PEHD if data["cijev"]["tip"] == 1 else LAMBDA_SMLS
                naziv_cijevi = "PE-HD" if data["cijev"]["tip"] == 1 else "SMLS"
                
                # Materijal cijevi - LaTeX stil
                st.latex(styled_latex(f"\\text{{Materijal cijevi: }} {naziv_cijevi}"))
                st.latex(styled_latex(f"\\lambda = {lambda_koef}"))
                
                if data["tip_prikljucka"] == 1:  # Niskotlačni
                    # Parametri - LaTeX stil
                    st.latex(styled_latex(f"Q_v = {data['rezultati']['vrsni_protok']:.2f} \\, \\text{{m}}^3\\text{{/h}}"))
                    st.latex(styled_latex(f"\\rho = {RHO_PLIN} \\, \\text{{kg/m}}^3"))
                    st.latex(styled_latex(f"L = {data['cijev']['duljina']:.2f} \\, \\text{{m}}"))
                    st.latex(styled_latex(f"d_u = {data['cijev']['dimenzije']['unutarnji']:.2f} \\, \\text{{mm}} = {data['cijev']['dimenzije']['unutarnji']/1000:.6f} \\, \\text{{m}}"))
                    
                    # LaTeX formula za pad tlaka (niskotlačni)
                    st.latex(styled_latex(r"\Delta p = 6.25 \cdot \lambda \cdot \frac{Q_v^2 \cdot \rho_{pl} \cdot L}{100 \cdot d_u^5}"))
                    st.latex(styled_latex(f"\\Delta p = 6.25 \\cdot {lambda_koef} \\cdot \\frac{{{data['rezultati']['vrsni_protok']:.2f}^2 \\cdot {RHO_PLIN} \\cdot {data['cijev']['duljina']:.2f}}}{{100 \\cdot {data['cijev']['dimenzije']['unutarnji']/1000:.6f}^5}} = {data['rezultati']['pad_tlaka']:.4f} \\, \\text{{mbar}}"))
                    
                else:  # Srednjetlačni
                    # Parametri - LaTeX stil
                    st.latex(styled_latex(f"\\lambda = {lambda_koef}"))
                    st.latex(styled_latex(f"L = {data['cijev']['duljina']:.2f} \\, \\text{{m}}"))
                    st.latex(styled_latex(f"w = {data['rezultati']['stvarna_brzina']:.2f} \\, \\text{{m/s}}"))
                    st.latex(styled_latex(f"\\rho = {RHO_PLIN} \\, \\text{{kg/m}}^3"))
                    st.latex(styled_latex(f"d_u = {data['cijev']['dimenzije']['unutarnji']:.2f} \\, \\text{{mm}} = {data['cijev']['dimenzije']['unutarnji']/1000:.6f} \\, \\text{{m}}"))
                    st.latex(styled_latex(f"p_1 = {POCETNI_TLAK_SREDNJETLACNI} \\, \\text{{mbar}}"))
                    
                    # LaTeX formula za pad tlaka (srednjetlačni)
                    st.latex(styled_latex(r"p_1^2 - p_2^2 = \frac{\lambda \cdot L \cdot w_1^2 \cdot \rho_{pl,1} \cdot p_1}{d_u}"))
                    
                    desna_strana = (lambda_koef * data['cijev']['duljina'] * pow(data['rezultati']['stvarna_brzina'], 2) * RHO_PLIN * POCETNI_TLAK_SREDNJETLACNI) / (data['cijev']['dimenzije']['unutarnji']/1000)
                    st.latex(styled_latex(f"p_1^2 - p_2^2 = \\frac{{{lambda_koef} \\cdot {data['cijev']['duljina']:.2f} \\cdot {data['rezultati']['stvarna_brzina']:.2f}^2 \\cdot {RHO_PLIN} \\cdot {POCETNI_TLAK_SREDNJETLACNI}}}{{{data['cijev']['dimenzije']['unutarnji']/1000:.6f}}}"))
                    
                    p2_kvadrat = pow(POCETNI_TLAK_SREDNJETLACNI, 2) - desna_strana
                    p2 = math.sqrt(p2_kvadrat)
                    
                    st.latex(styled_latex(f"p_2 = \\sqrt{{p_1^2 - \\frac{{\\lambda \\cdot L \\cdot w_1^2 \\cdot \\rho_{{pl,1}} \\cdot p_1}}{{d_u}}}} = {p2:.2f} \\, \\text{{mbar}}"))
                    st.latex(styled_latex(f"\\Delta p = p_1 - p_2 = {POCETNI_TLAK_SREDNJETLACNI} - {p2:.2f} = {data['rezultati']['pad_tlaka']:.2f} \\, \\text{{mbar}}"))
        
        # Zaključak
    
    def get_state(self):
        """Vraća trenutno stanje proračuna za undo/redo."""
        return st.session_state.gas_connection_data.copy()
    
    def restore_state(self, state):
        """Vraća stanje proračuna iz snimljenog stanja."""
        st.session_state.gas_connection_data = state
    
    def serialize(self):
        """Pretvara proračun u format za spremanje."""
        return st.session_state.gas_connection_data
    
    def deserialize(self, data):
        """Učitava proračun iz formata za spremanje.""" 
        st.session_state.gas_connection_data = data
    
    def export_to_word(self, doc):
        """Izvozi proračun u Word dokument."""
        export_proracun_to_word(doc, st.session_state.gas_connection_data)