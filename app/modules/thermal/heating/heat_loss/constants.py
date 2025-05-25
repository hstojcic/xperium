"""
Globalne konstante i standardne vrijednosti za proračun toplinskih gubitaka prema EN 12831.
Ova datoteka sadrži konstante koje su zajedničke za cijeli heat_loss modul.
"""

# Zimske projektne temperature po klimatskim zonama
REGIJE_GRADOVI_TEMP = {
    "Kontinentalna Hrvatska": {
        "Belje": -15.8,
        "Bjelovar": -14.3,
        "Daruvar": -14.2,
        "Gradište": -14.3,
        "Koprivnica": -15.0,
        "Krapina": -12.4,
        "Križevci": -14.8,
        "Lipik": -15.7,
        "Našice": -13.2,
        "Osijek": -16.1,
        "Požega": -15.8,
        "Samobor": -12.2,
        "Sisak": -12.2,
        "Slatina": -14.8,
        "Slavonski Brod": -16.4,
        "Stubičke Toplice": -14.8,
        "Sunja": -16.7,
        "Varaždin": -14.9,
        "Vinkovci": -14.6,
        "Zagreb": -12.8,
        "Županja": -13.8
    },
    "Gorska Hrvatska": {
        "Gospić": -17.2,
        "Lokve Brana": -16.0,
        "Ogulin": -14.1,
        "Puntijarka": -17.6,
        "Slunj": -15.4,
        "Topusko": -16.8,
        "Karlovac": -14.5
    },
    "Primorska Hrvatska": {
        "Dubrovnik": -1.6,
        "Hvar": -0.5,
        "Imotski": -5.9,
        "Knin": -8.9,
        "Komiža": 0.0,
        "Makarska": -1.3,
        "Mali Lošinj": -2.7,
        "Pazin": -9.6,
        "Ploče": -2.4,
        "Poreč": -6.5,
        "Pula": -6.2,
        "Rab": -2.4,
        "Rijeka": -7.7,
        "Senj": -9.1,
        "Split": -3.0,
        "Šibenik": -5.7,
        "Zadar": -4.6
    }
}

# Gradovi u Hrvatskoj s vanjskim projektnim temperaturama (°C) - zaravnana lista za kompatibilnost
GRADOVI_TEMP = {}
for regija, gradovi in REGIJE_GRADOVI_TEMP.items():
    GRADOVI_TEMP.update(gradovi)

# Prosječni godišnji broj stupanj-dana grijanja za gradove u Hrvatskoj
STUPANJ_DANI_GRIJANJA = {
    # Kontinentalna Hrvatska
    "Zagreb": 2500,
    "Bjelovar": 2600,
    "Osijek": 2900,
    "Slavonski Brod": 2850,
    "Varaždin": 2800,
    "Sisak": 2550,
    "Koprivnica": 2750,
    "Krapina": 2700,
    
    # Gorska Hrvatska
    "Gospić": 3200,
    "Karlovac": 2650,
    "Ogulin": 2950,
    "Slunj": 3000,
    
    # Primorska Hrvatska
    "Split": 1100,
    "Rijeka": 1800,
    "Dubrovnik": 1000,
    "Zadar": 1400,
    "Šibenik": 1300,
    "Pula": 1600,
    "Makarska": 1150,
    "Knin": 2000,
    "Hvar": 950,
    "Mali Lošinj": 1500
}

# Orijentacije - za orijentaciju zgrada i elemenata
ORIJENTACIJE = ["Sjever", "Sjeveroistok", "Istok", "Jugoistok", "Jug", "Jugozapad", "Zapad", "Sjeverozapad"]

# Faktori za različite orijentacije - za proračune sunčevog zračenja i sl.
ORIJENTACIJE_FAKTORI = {
    "Sjever": 1.20,
    "Sjeveroistok": 1.15,
    "Istok": 1.10,
    "Jugoistok": 1.05,
    "Jug": 1.00,
    "Jugozapad": 1.05,
    "Zapad": 1.10,
    "Sjeverozapad": 1.15
}

# Toplinski mostovi - linearni koeficijenti prolaska topline (W/mK)
TOPLINSKI_MOSTOVI = {
    "Vanjski kut zida": 0.10,
    "Unutarnji kut zida": -0.10,
    "Spoj zid-prozor": 0.15,
    "Spoj zid-vrata": 0.15,
    "Spoj zid-pod": 0.40,
    "Spoj zid-strop": 0.40,
    "Spoj zid-balkon": 0.60,
    "Prekid izolacije": 0.30
}

# CSS stilovi za ujednačen izgled aplikacije
CSS_STYLES = """
    /* Minimal CSS for tabs to ensure compatibility with Streamlit's native styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        white-space: pre-wrap;
        padding: 10px 16px;
    }

    /* Simple highlight for active sections */
    .active-section {
        border-left: 3px solid #1E88E5;
        padding-left: 8px;
    }
    
    /* Utility classes for spacing and layout */
    .mt-1 { margin-top: 0.5rem; }
    .mb-1 { margin-bottom: 0.5rem; }
    .p-1 { padding: 0.5rem; }
    
    /* Light highlight backgrounds for different content sections */
    .bg-light-blue {
        background-color: rgba(33, 150, 243, 0.05);
        border-radius: 4px;
        padding: 8px;
    }
    
    /* Card styles */
    .prostorija-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    
    /* Table styles */
    .fixed-width-table {
        width: 100%;
        table-layout: fixed;
    }
    
    .fixed-width-table th:nth-child(1) {width: 35%;}
    .fixed-width-table th:nth-child(2) {width: 15%;}
    .fixed-width-table th:nth-child(3) {width: 15%;}
    .fixed-width-table th:nth-child(4) {width: 15%;}
    .fixed-width-table th:nth-child(5) {width: 20%;}
"""

# Napomena: Ne importiramo iz models/elementi/constants.py kako bismo izbjegli cirkularni import