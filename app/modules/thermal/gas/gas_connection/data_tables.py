"""
Tablice podataka za proračun plinskog priključka.
"""

# Kotlovi organizirani po proizvođačima i tipovima
KOTLOVI = {
    "Vaillant": {
        "Kondenzacijski": [
            {"model": "ecoTEC plus VUW 11/26 CS/1-5", "Pgr": 11.9, "Pptv": 25.7},
            {"model": "ecoTEC plus VUW 20/26 CS/1-5", "Pgr": 21.0, "Pptv": 26.0},
            {"model": "ecoTEC plus VUW 25/26 CS/1-5", "Pgr": 26.4, "Pptv": 26.0},
            {"model": "ecoTEC plus VUW 25/32 CS/1-5", "Pgr": 27.0, "Pptv": 31.8},
            {"model": "ecoTEC plus VUW 30/36 CS/1-5", "Pgr": 33.3, "Pptv": 35.6},
            {"model": "ecoTEC plus VUW 35/40 CS/1-5", "Pgr": 37.7, "Pptv": 39.7},
            {"model": "ecoTEC plus VU 10 CS/1-5", "Pgr": 10.9, "Pptv": 20.0},
            {"model": "ecoTEC plus VU 20 CS/1-5", "Pgr": 21.0, "Pptv": 24.0},
            {"model": "ecoTEC plus VU 25 CS/1-5", "Pgr": 26.4, "Pptv": 27.5},
            {"model": "ecoTEC plus VU 30 CS/1-5", "Pgr": 33.3, "Pptv": 34.8},
            {"model": "ecoTEC plus VU 35 CS/1-5", "Pgr": 37.7, "Pptv": 39.7}
        ],
        "Klasični": [
            {"model": "atmoTEC plus VU 20", "Pgr": 20.0, "Pptv": 20.0},
            {"model": "atmoTEC plus VU 24", "Pgr": 24.0, "Pptv": 24.0}
        ]
    },
    "Bosch": {
        "Kondenzacijski": [
            {"model": "Condens 2300i W 20/25", "Pgr": 20.0, "Pptv": 25.0},
            {"model": "Condens 2300i W 24/25", "Pgr": 24.0, "Pptv": 25.0}
        ],
        "Klasični": [
            {"model": "Gaz 3000 W 24", "Pgr": 24.0, "Pptv": 24.0}
        ]
    },
    "Viessmann": {
        "Kondenzacijski": [
            {"model": "Vitodens 050-W 19 kW", "Pgr": 19.0, "Pptv": 25.4},
            {"model": "Vitodens 100-W 25 kW", "Pgr": 25.0, "Pptv": 29.6}
        ],
        "Klasični": [
            {"model": "Vitopend 100-W 24 kW", "Pgr": 24.0, "Pptv": 24.0}
        ]
    }
}

# Plinomjeri
PLINOMJERI = {
    'G-4':  {'DN': 25, 'Qmin': 0.04, 'Qmax': 6},
    'G-6':  {'DN': 25, 'Qmin': 0.06, 'Qmax': 10},
    'G-10': {'DN': 40, 'Qmin': 0.10, 'Qmax': 16},
    'G-16': {'DN': 40, 'Qmin': 0.16, 'Qmax': 25},
    'G-25': {'DN': 50, 'Qmin': 0.25, 'Qmax': 40}
}

# Čelične bešavne cijevi (SMLS)
SMLS_CIJEVI = {
    1: {'oznaka': 'DN 15', 'vanjski': 21.3, 'debljina': 2.0, 'unutarnji': 17.3},
    2: {'oznaka': 'DN 20', 'vanjski': 26.9, 'debljina': 2.3, 'unutarnji': 22.3},
    3: {'oznaka': 'DN 25', 'vanjski': 33.7, 'debljina': 2.6, 'unutarnji': 28.5},
    4: {'oznaka': 'DN 32', 'vanjski': 42.4, 'debljina': 2.6, 'unutarnji': 37.2},
    5: {'oznaka': 'DN 40', 'vanjski': 48.3, 'debljina': 2.6, 'unutarnji': 43.1},
    6: {'oznaka': 'DN 50', 'vanjski': 60.3, 'debljina': 2.9, 'unutarnji': 54.5}
}

# Polietilenske cijevi (PE-HD)
PEHD_CIJEVI = {
    1: {'oznaka': 'DN 15', 'vanjski': 20.0, 'debljina': 2.0, 'unutarnji': 16.0},
    2: {'oznaka': 'DN 20', 'vanjski': 25.0, 'debljina': 2.3, 'unutarnji': 20.4},
    3: {'oznaka': 'DN 25', 'vanjski': 32.0, 'debljina': 3.0, 'unutarnji': 26.0},
    4: {'oznaka': 'DN 32', 'vanjski': 40.0, 'debljina': 3.7, 'unutarnji': 32.6},
    5: {'oznaka': 'DN 40', 'vanjski': 50.0, 'debljina': 4.6, 'unutarnji': 40.8},
    6: {'oznaka': 'DN 50', 'vanjski': 63.0, 'debljina': 5.8, 'unutarnji': 51.4}
}