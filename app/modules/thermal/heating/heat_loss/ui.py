"""
Komponente korisničkog sučelja za aplikaciju proračuna toplinskih gubitaka
"""

import streamlit as st
from .models.elementi.constants import TIPOVI_PROSTORIJA, TEMP_FAKTORI, DEFAULT_U_VALUES
from .constants import ORIJENTACIJE
from .utils.validators import prikazuje_upozorenje_o_povrsinama
from .utils.ui_helpers import create_transmission_losses_table, create_ventilation_losses_table, create_losses_pie_chart
from .utils.ui_helpers import create_transmission_losses_table, create_ventilation_losses_table, create_losses_pie_chart

def prikazi_postavke(self):
    """
    Prikazuje postavke koje su bile u bočnoj traci
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.header("Postavke proračuna")
    
    st.subheader("Projektne temperature")
    self.temp_vanjska = st.number_input(
        "Vanjska projektna temperatura [°C]:", 
        min_value=-30, 
        max_value=5, 
        value=int(self.temp_vanjska), 
        step=1
    )
    
    prilagodi_konstante = st.checkbox("Prilagodi konstante i koeficijente", value=False)
    
    if prilagodi_konstante:
        st.subheader("Koeficijenti prolaza topline (U-vrijednosti)")
        self.u_values["Vanjski zid"] = st.number_input(
            "U-vrijednost vanjskog zida [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Vanjski zid"], 
            step=0.01
        )
        self.u_values["Prozor"] = st.number_input(
            "U-vrijednost prozora [W/m²K]:", 
            min_value=0.5, 
            max_value=5.0, 
            value=self.u_values["Prozor"], 
            step=0.1
        )
        self.u_values["Vrata"] = st.number_input(
            "U-vrijednost vanjskih vrata [W/m²K]:", 
            min_value=0.5, 
            max_value=5.0, 
            value=self.u_values["Vrata"], 
            step=0.1
        )
        self.u_values["Pod prema tlu"] = st.number_input(
            "U-vrijednost poda prema tlu [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Pod prema tlu"], 
            step=0.01
        )
        self.u_values["Pod prema negrijanom prostoru"] = st.number_input(
            "U-vrijednost poda prema negrijanom prostoru [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Pod prema negrijanom prostoru"], 
            step=0.01
        )
        self.u_values["Pod prema vanjskom prostoru"] = st.number_input(
            "U-vrijednost poda prema vanjskom prostoru [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Pod prema vanjskom prostoru"], 
            step=0.01
        )
        self.u_values["Strop prema tavanu"] = st.number_input(
            "U-vrijednost stropa prema tavanu [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Strop prema tavanu"], 
            step=0.01
        )
        self.u_values["Strop prema negrijanom prostoru"] = st.number_input(
            "U-vrijednost stropa prema negrijanom prostoru [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Strop prema negrijanom prostoru"], 
            step=0.01
        )
        self.u_values["Ravan krov"] = st.number_input(
            "U-vrijednost ravnog krova [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Ravan krov"], 
            step=0.01
        )
        self.u_values["Kosi krov"] = st.number_input(
            "U-vrijednost kosog krova [W/m²K]:", 
            min_value=0.1, 
            max_value=3.0, 
            value=self.u_values["Kosi krov"], 
            step=0.01
        )
    
    with st.expander("O proračunu prema EN 12831"):
        st.markdown("""
        **Proračun toplinskih gubitaka** se radi prema europskoj normi EN 12831, koja definira metodu za izračun projektnog toplinskog opterećenja.
        
        **Ključni elementi proračuna:**
        - Transmisijski gubici kroz sve građevinske elemente
        - Ventilacijski gubici zbog izmjene zraka
        - Temperaturni korekcijski faktori
        - Dodatak za toplinske mostove
        - Dodatak za sigurnost
        
        **Izračun je usklađen s važećim propisima za energetsku učinkovitost zgrada.**
        """)

def prikazi_osnovne_podatke(self):
    """
    Prikazuje osnovne podatke o prostoriji
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.markdown("<h3 class='subsection-header'>Osnovni podaci</h3>", unsafe_allow_html=True)
    
    self.tip_prostorije = st.selectbox("Tip prostorije:", list(TIPOVI_PROSTORIJA.keys()))
    
    # Automatsko postavljanje temperature i izmjena zraka na osnovu tipa prostorije
    self.temp_unutarnja = st.slider(
        "Unutarnja projektna temperatura [°C]:",
        min_value=10,
        max_value=26,
        value=TIPOVI_PROSTORIJA[self.tip_prostorije]["temp"],
        step=1,
        help="Automatski postavljena na osnovu tipa prostorije, možete mijenjati po potrebi"
    )
    
    self.izmjene_zraka = st.number_input(
        "Broj izmjena zraka [1/h]:",
        min_value=0.1,
        max_value=5.0,
        value=TIPOVI_PROSTORIJA[self.tip_prostorije]["izmjene"],
        step=0.1,
        help="Automatski postavljeno na osnovu tipa prostorije prema EN 12831"
    )

def prikazi_dimenzije_prostorije(self):
    """
    Prikazuje polja za unos dimenzija prostorije
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.markdown("<h3 class='subsection-header'>Dimenzije prostorije</h3>", unsafe_allow_html=True)
    
    self.duljina = st.number_input(
        "Duljina prostorije [m]:", 
        min_value=1.0, 
        max_value=20.0, 
        value=self.duljina, 
        step=0.1
    )
    
    self.sirina = st.number_input(
        "Širina prostorije [m]:", 
        min_value=1.0, 
        max_value=20.0, 
        value=self.sirina, 
        step=0.1
    )
    
    self.visina = st.number_input(
        "Visina prostorije [m]:", 
        min_value=2.0, 
        max_value=6.0, 
        value=self.visina, 
        step=0.1
    )

def prikazi_pod_i_strop(self):
    """
    Prikazuje polja za unos podataka o podu i stropu
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.markdown("<h3 class='subsection-header'>Pod i strop</h3>", unsafe_allow_html=True)
    
    self.pod_tip = st.selectbox("Tip poda (prema):", list(TEMP_FAKTORI.keys()))
    
    if self.pod_tip == "Prema tlu":
        self.u_pod = self.u_values["Pod prema tlu"]
    elif self.pod_tip == "Prema negrijanom prostoru":
        self.u_pod = self.u_values["Pod prema negrijanom prostoru"]
    elif self.pod_tip == "Prema vanjskom prostoru":
        self.u_pod = self.u_values["Pod prema vanjskom prostoru"]
    else:
        self.u_pod = self.u_values["Pod prema tlu"]
    
    self.strop_tip = st.selectbox("Tip stropa (prema):", list(TEMP_FAKTORI.keys()))
    
    if self.strop_tip == "Prema vanjskom prostoru":
        strop_podtip = st.radio("Tip krova:", ["Ravan krov", "Kosi krov"])
        if strop_podtip == "Ravan krov":
            self.u_strop = self.u_values["Ravan krov"]
        else:
            self.u_strop = self.u_values["Kosi krov"]
    elif self.strop_tip == "Prema negrijanom prostoru":
        self.u_strop = self.u_values["Strop prema negrijanom prostoru"]
    elif self.strop_tip == "Prema tlu":
        self.u_strop = self.u_values["Strop prema tavanu"]
    else:
        self.u_strop = self.u_values["Strop prema negrijanom prostoru"]

def prikazi_vanjske_zidove(self):
    """
    Prikazuje polja za unos podataka o vanjskim zidovima
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.markdown("<h3 class='subsection-header'>Vanjski zidovi</h3>", unsafe_allow_html=True)
    
    broj_vanjskih_zidova = st.number_input(
        "Broj vanjskih zidova:", 
        min_value=0, 
        max_value=4, 
        value=sum(1 for zid in self.vanjski_zidovi_info if zid["postoji"]), 
        step=1
    )
    
    # Ažuriramo broj aktivnih zidova
    for i in range(4):
        if i < broj_vanjskih_zidova:
            self.vanjski_zidovi_info[i]["postoji"] = True
        else:
            self.vanjski_zidovi_info[i]["postoji"] = False
    
    for i in range(4):
        if self.vanjski_zidovi_info[i]["postoji"]:
            with st.expander(f"Vanjski zid {i+1}", expanded=True):
                self.vanjski_zidovi_info[i]["orijentacija"] = st.selectbox(
                    f"Orijentacija zida {i+1}:", 
                    ORIJENTACIJE, 
                    index=ORIJENTACIJE.index(self.vanjski_zidovi_info[i]["orijentacija"]),
                    key=f"orijentacija_{i}"
                )
                
                self.vanjski_zidovi_info[i]["duzina"] = st.number_input(
                    f"Duljina zida {i+1} [m]:", 
                    min_value=0.5, 
                    max_value=20.0, 
                    value=self.vanjski_zidovi_info[i]["duzina"], 
                    step=0.1, 
                    key=f"duzina_{i}"
                )
                
                self.vanjski_zidovi_info[i]["povrsina_prozora"] = st.number_input(
                    f"Površina prozora na zidu {i+1} [m²]:", 
                    min_value=0.0, 
                    max_value=20.0, 
                    value=self.vanjski_zidovi_info[i]["povrsina_prozora"], 
                    step=0.1, 
                    key=f"prozor_{i}"
                )
                
                self.vanjski_zidovi_info[i]["povrsina_vrata"] = st.number_input(
                    f"Površina vrata na zidu {i+1} [m²]:", 
                    min_value=0.0, 
                    max_value=5.0, 
                    value=self.vanjski_zidovi_info[i]["povrsina_vrata"], 
                    step=0.1, 
                    key=f"vrata_{i}"
                )
                
                # Provjera da površina prozora i vrata ne premašuje površinu zida
                if prikazuje_upozorenje_o_povrsinama(self.vanjski_zidovi_info[i], self.visina):
                    max_povrsina = self.vanjski_zidovi_info[i]["duzina"] * self.visina
                    st.warning(
                        f"Upozorenje: Ukupna površina prozora i vrata "
                        f"({self.vanjski_zidovi_info[i]['povrsina_prozora'] + self.vanjski_zidovi_info[i]['povrsina_vrata']:.1f} m²) "
                        f"premašuje površinu zida ({max_povrsina:.1f} m²)."
                    )

def prikazi_dodatne_opcije(self):
    """
    Prikazuje dodatne opcije proračuna
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.markdown("<h3 class='subsection-header'>Dodatne opcije</h3>", unsafe_allow_html=True)
    
    # Checkbox for thermal bridges
    # Session state is initialized in HeatLossCalc.__init__
    st.checkbox(
        "Uključi toplinske mostove",
        value=st.session_state.toplinski_mostovi_checkbox, # Read from session state
        key='toplinski_mostovi_checkbox',                 # Links widget to session state
        help="Pojednostavljeni proračun toplinskih mostova prema EN 12831"
    )
    # Update instance variable from session state (source of truth)
    self.toplinski_mostovi = st.session_state.toplinski_mostovi_checkbox
    
    # Slider for safety factor
    # Session state is initialized in HeatLossCalc.__init__
    st.slider(
        "Faktor sigurnosti [%]:",
        min_value=0,
        max_value=30,
        value=st.session_state.faktor_sigurnosti_slider, # Read from session state
        step=5,
        key='faktor_sigurnosti_slider',                  # Links widget to session state
        help="Dodatak za sigurnost prema EN 12831"
    )
    # Update instance variable from session state
    self.faktor_sigurnosti = st.session_state.faktor_sigurnosti_slider

def prikazi_rezultate(self):
    """
    Prikazuje rezultate proračuna
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.markdown("<h2 class='section-header'>Rezultati proračuna</h2>", unsafe_allow_html=True)
    
    # Osnovni podaci o prostoriji
    prikazi_osnovne_rezultate(self)
    
    # Transmisijski gubici
    st.markdown("<h3 class='subsection-header'>Transmisijski gubici</h3>", unsafe_allow_html=True)
    
    # Detalji gubitaka kroz pojedine zidove
    prikazi_detalje_zidova(self)
    
    # Tabela transmisijskih gubitaka
    transmisijski_df = create_transmission_losses_table(self.rezultati)
    st.table(transmisijski_df)
    
    # Ventilacijski gubici
    st.markdown("<h3 class='subsection-header'>Ventilacijski gubici</h3>", unsafe_allow_html=True)
    
    ventilacijski_df = create_ventilation_losses_table(self.rezultati, self.izmjene_zraka)
    st.table(ventilacijski_df)
    
    # Ukupni gubici
    prikazi_ukupne_gubitke(self)
    
    # Vizualizacija raspodjele gubitaka
    st.markdown("<h3 class='subsection-header'>Vizualizacija raspodjele gubitaka</h3>", unsafe_allow_html=True)
    
    # Prikazujemo pie chart
    fig = create_losses_pie_chart(
        self.rezultati, 
        ventilacijski=self.rezultati['gubici_ventilacijski'],
        toplinski_mostovi=self.rezultati.get('gubici_toplinski_mostovi', 0)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Dodatne informacije i preporuke
    prikazi_dodatne_informacije(self)
    
    # Procjena godišnje potrebe energije za grijanje
    prikazi_godisnju_energiju(self)

def prikazi_osnovne_rezultate(self):
    """
    Prikazuje osnovne rezultate proračuna
    
    Parameters:
    -----------
    self : HeatLossCalc
        Instanca HeatLossCalc klase
    """
    st.markdown("<h3 class='subsection-header'>Osnovni podaci o prostoriji</h3>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tip prostorije", self.tip_prostorije)
    with col2:
        st.metric("Površina", f"{self.rezultati['površina_prostorije']:.1f} m²")
    with col3:
        st.metric("Volumen", f"{self.rezultati['volumen_prostorije']:.1f} m³")
    with col4:
        st.metric("ΔT", f"{self.rezultati['delta_t']} °C")

def prikazi_detalje_zidova(self):
    """
    Prikazuje detalje gubitaka kroz zidove
    
    Parameters:
    -----------
    self : HeatLossCalcRefactored
        Instanca HeatLossCalcRefactored klase
    """
    if len(self.rezultati["detalji_zidova"]) > 0:
        st.markdown("#### Gubici kroz vanjske zidove")
        for zid in self.rezultati["detalji_zidova"]:
            with st.expander(f"Zid {zid['index']} - {zid['orijentacija']}", expanded=False):
                st.markdown(f"""
                - **Duljina zida:** {zid['duzina']:.1f} m
                - **Ukupna površina zida:** {zid['ukupna_povrsina']:.1f} m²
                - **Površina bez otvora:** {zid['cista_povrsina']:.1f} m²
                - **Površina prozora:** {zid['povrsina_prozora']:.1f} m²
                - **Površina vrata:** {zid['povrsina_vrata']:.1f} m²
                - **Gubici kroz zid:** {zid['gubitak_zid']:.1f} W
                - **Gubici kroz prozore:** {zid['gubitak_prozor']:.1f} W
                - **Gubici kroz vrata:** {zid['gubitak_vrata']:.1f} W
                - **Ukupni gubici kroz zid:** {zid['gubitak_zid'] + zid['gubitak_prozor'] + zid['gubitak_vrata']:.1f} W
                """)

def prikazi_ukupne_gubitke(self):
    """
    Prikazuje ukupne toplinske gubitke
    
    Parameters:
    -----------
    self : HeatLossCalcRefactored
        Instanca HeatLossCalcRefactored klase
    """
    st.markdown("<h3 class='subsection-header'>Ukupni toplinski gubici</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Transmisijski gubici", f"{self.rezultati['gubici_transmisijski']:.0f} W")
    with col2:
        st.metric("Ventilacijski gubici", f"{self.rezultati['gubici_ventilacijski']:.0f} W")
    with col3:
        if self.faktor_sigurnosti > 0:
            st.metric("Faktor sigurnosti", f"{self.rezultati['faktor_sigurnosti_gubici']:.0f} W", f"+{self.faktor_sigurnosti}%")
    
    # Konačni rezultat
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 class='subsection-header'>UKUPNI TOPLINSKI GUBITAK:</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color:#1E88E5;'>{self.rezultati['ukupni_gubici']:.0f} W</h1>", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 class='subsection-header'>Specifični toplinski gubitak:</h3>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color:#1E88E5;'>{self.rezultati['specificni_gubici']:.1f} W/m²</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def prikazi_dodatne_informacije(self):
    """
    Prikazuje dodatne informacije i preporuke
    
    Parameters:
    -----------
    self : HeatLossCalcRefactored
        Instanca HeatLossCalcRefactored klase
    """
    st.markdown("<h3 class='subsection-header'>Dodatne informacije i preporuke</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown(f"""
    - **Ukupna ogrjevna površina prostorije:** {self.rezultati['površina_prostorije']:.1f} m²
    - **Ukupni volumen prostorije:** {self.rezultati['volumen_prostorije']:.1f} m³
    - **Odnos transmisijskih i ventilacijskih gubitaka:** {self.rezultati['gubici_transmisijski'] / max(1, self.rezultati['gubici_ventilacijski']):.1f} : 1
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Preporuke na osnovu rezultata
    if self.rezultati["specificni_gubici"] > 100:
        st.markdown("<div class='warning-box'>", unsafe_allow_html=True)
        st.markdown("""
        **Preporuke za smanjenje toplinskih gubitaka:**
        - Poboljšajte toplinsku izolaciju zidova
        - Razmotrite zamjenu prozora s boljim U-vrijednostima
        - Poboljšajte zrakonepropusnost objekta za smanjenje infiltracije
        """)
        st.markdown("</div>", unsafe_allow_html=True)

def prikazi_godisnju_energiju(self):
    """
    Prikazuje procjenu godišnje potrebe energije
    
    Parameters:
    -----------
    self : HeatLossCalcRefactored
        Instanca HeatLossCalcRefactored klase
    """
    st.markdown("<h3 class='subsection-header'>Procjena godišnje potrebe za energijom</h3>", unsafe_allow_html=True)
    
    st.markdown("<div class='info-box'>", unsafe_allow_html=True)
    st.markdown(f"""
    Ovo je pojednostavljena procjena godišnje potrebe za energijom grijanja za ovu prostoriju:
    
    - **Procijenjeni stupanj-dani grijanja:** {self.godisnja_energija['stupanj_dani']:.0f} °dan
    - **Procijenjeni sati grijanja:** {self.godisnja_energija['sati_grijanja']} h
    - **Procjenjena godišnja potreba energije:** {self.godisnja_energija['potrebna_energija']:.0f} kWh
    
    *Napomena: Za točniju procjenu potrebno je napraviti cjeloviti proračun prema mjesečnoj metodi.*
    """)
    st.markdown("</div>", unsafe_allow_html=True)
