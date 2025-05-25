"""
Konstante za proračun plinskog priključka.
"""

# Ogrijevna vrijednost (kWh/m³)
HD = 9.25

# Iskoristivost uređaja
ETA_KONDENZACIJSKI = 0.99
ETA_KLASICNI = 0.84
ETA_PLOCA = 0.57

# Lambda vrijednosti za različite materijale
LAMBDA_PEHD = 0.0100  # PE-HD cijevi
LAMBDA_SMLS = 0.0200  # čelične bešavne cijevi

# Gustoća plina (kg/m³)
RHO_PLIN = 0.69

# Faktori za kotlove (fG UWH)
F_KOTAO = {
    1: 1.000,
    2: 0.874,
    3: 0.809,
    4: 0.765,
    5: 0.733,
    6: 0.708,
    7: 0.687,
    8: 0.670,
    9: 0.655,
    10: 0.642
}

# Faktori za 2-plamene ploče/štednjake
F_PLOCA_2 = {
    1: 0.781, 2: 0.561, 3: 0.463, 4: 0.405,
    5: 0.366, 6: 0.336, 7: 0.314, 8: 0.295,
    9: 0.280, 10: 0.267
}

# Faktori za 3-plamene i 4-plamene ploče/štednjake
F_PLOCA_3_4 = {
    1: 0.692, 2: 0.498, 3: 0.412, 4: 0.361,
    5: 0.326, 6: 0.300, 7: 0.280, 8: 0.264,
    9: 0.251, 10: 0.239
}

# Faktori za štednjake s 4 plamenika i pećnicom
F_STEDNJAK_PECNICA = {
    1: 0.594, 2: 0.429, 3: 0.356, 4: 0.312,
    5: 0.282, 6: 0.260, 7: 0.243, 8: 0.229,
    9: 0.218, 10: 0.208
}

# Standardna brzina za proračun (m/s)
STANDARD_BRZINA = 6.0

# Maksimalni pad tlaka (mbar)
MAX_PAD_TLAKA_NISKOTLACNI = 1.0
MAX_PAD_TLAKA_SREDNJETLACNI = 100.0

# Početni tlak za srednjetlačni priključak (mbar)
POCETNI_TLAK_SREDNJETLACNI = 1000.0