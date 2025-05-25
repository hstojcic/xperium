"""
Konstante za proračun podnog grijanja.
"""

# Fizikalne konstante
SPECIFIC_HEAT_WATER = 4190.0  # J/(kg·K)
GRAVITATIONAL_ACCELERATION = 9.81  # m/s²
ALPHA_I = 10.8  # W/(m²·K)

# Maksimalne temperature poda za različite tipove prostorija
MAX_FLOOR_TEMP = {
    15: 29,  # Garaža
    18: 29,  # Hodnik
    20: 29,  # Standardne prostorije
    22: 29,  # Dnevni boravak i sl.
    24: 33,  # Kupaonica
}

# Tipovi prostorija grupirani po preporučenoj temperaturi
ROOM_TYPES = {
    15: ['Garaža'],
    18: ['Hodnik'],
    20: ['Kuhinja', 'Spavaća soba', 'WC', 'Garderoba', 'Vešeraj'],
    22: ['Dnevni boravak', 'Blagovaonica', 'Dnevni boravak i kuhinja', 
         'Dnevni boravak i blagovaonica', 'Dnevni boravak, kuhinja i blagovaonica', 
         'Soba', 'Dječja soba', 'Radna soba'],
    24: ['Kupaonica']
}

# Definicije podnih obloga s vrijednostima R_lambda
FLOOR_COVERINGS = [
    {'name': 'Keramička obloga', 'r_lambda': 0.00},
    {'name': 'Plastična obloga (tanka)', 'r_lambda': 0.05},
    {'name': 'Plastična obloga (deblja)', 'r_lambda': 0.10},
    {'name': 'Drvena obloga', 'r_lambda': 0.15}
]

# Dostupne debljine estriha (mm)
SCREED_THICKNESSES = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]

# Reorganizirana struktura za cijevi - sadrži sve potrebne podatke
PIPE_DATA = {
    '14×2,0': {
        'display': 'PE-Xa ∅14×2,0',  # Za prikaz u dropdown-u
        'outer_diameter': 14.0,      # Vanjski promjer (mm)
        'wall_thickness': 2.0,       # Debljina stijenke (mm)
        'inner_diameter': 10.0,      # Unutarnji promjer (mm)
        'max_length': 80,            # Maksimalna duljina (m)
        'volume_per_meter': 0.079,   # litra po metru cijevi
    },
    '16×2,0': {
        'display': 'PE-Xa ∅16×2,0',
        'outer_diameter': 16.0,
        'wall_thickness': 2.0,
        'inner_diameter': 12.0,
        'max_length': 100,
        'volume_per_meter': 0.113,   # litra po metru cijevi
    },
    '17×2,0': {
        'display': 'PE-Xa ∅17×2,0',
        'outer_diameter': 17.0,
        'wall_thickness': 2.0,
        'inner_diameter': 13.0,
        'max_length': 120,
        'volume_per_meter': 0.133,   # litra po metru cijevi
    },
    '20×2,0': {
        'display': 'PE-Xa ∅20×2,0',
        'outer_diameter': 20.0,
        'wall_thickness': 2.0,
        'inner_diameter': 16.0,
        'max_length': 150,
        'volume_per_meter': 0.201,   # litra po metru cijevi
    }
}

# Pomoćni rječnik za direktan pristup maksimalnim duljinama za kompatibilnost s postojećim kodom
PIPE_DIAMETERS = {key: data['max_length'] for key, data in PIPE_DATA.items()}

# Dostupni razmaci cijevi (cm)
PIPE_SPACINGS = [10, 15, 20, 25, 30]

# Dostupne temperature polaza (°C)
FLOW_TEMPERATURES = [35, 40, 45, 50, 55]

# Dostupne vrijednosti za ΔT (°C)
DELTA_T_VALUES = list(range(5, 11))  # 5, 6, 7, 8, 9, 10

# Definicije spojnih cijevi za povezivanje razdjelnika s izvorom topline
CONNECTION_PIPE_DATA = {
    '16×2,0': {
        'display': 'PE-RT/Al/PE-RT ∅16×2,0',
        'outer_diameter': 16.0,
        'wall_thickness': 2.0,
        'inner_diameter': 12.0,
        'volume_per_meter': 0.113,  # litra po metru cijevi
    },
    '20×2,3': {
        'display': 'PE-RT/Al/PE-RT ∅20×2,3',
        'outer_diameter': 20.0,
        'wall_thickness': 2.3,
        'inner_diameter': 15.4,
        'volume_per_meter': 0.186,  # litra po metru cijevi
    },
    '25×2,5': {
        'display': 'PE-RT/Al/PE-RT ∅25×2,5',
        'outer_diameter': 25.0,
        'wall_thickness': 2.5,
        'inner_diameter': 20.0,
        'volume_per_meter': 0.314,  # litra po metru cijevi
    },
    '32×3,0': {
        'display': 'PE-RT/Al/PE-RT ∅32×3,0',
        'outer_diameter': 32.0,
        'wall_thickness': 3.0,
        'inner_diameter': 26.0,
        'volume_per_meter': 0.531,  # litra po metru cijevi
    },
    '40×4,0': {
        'display': 'PE-RT/Al/PE-RT ∅40×4,0',
        'outer_diameter': 40.0,
        'wall_thickness': 4.0,
        'inner_diameter': 32.0,
        'volume_per_meter': 0.804,  # litra po metru cijevi
    },
    '50×4,5': {
        'display': 'PE-RT/Al/PE-RT ∅50×4,5',
        'outer_diameter': 50.0,
        'wall_thickness': 4.5,
        'inner_diameter': 41.0,
        'volume_per_meter': 1.320,  # litra po metru cijevi
    }
}

# Definicije razdjelnika
MANIFOLD_TYPES = {
    '2-kruga': {
        'display': 'Razdjelnik 2 kruga',
        'max_loops': 2,
        'volume': 0.5,  # litara vode u razdjelniku
    },
    '3-kruga': {
        'display': 'Razdjelnik 3 kruga',
        'max_loops': 3,
        'volume': 0.6,
    },
    '4-kruga': {
        'display': 'Razdjelnik 4 kruga',
        'max_loops': 4,
        'volume': 0.7,
    },
    '5-krugova': {
        'display': 'Razdjelnik 5 krugova',
        'max_loops': 5,
        'volume': 0.8,
    },
    '6-krugova': {
        'display': 'Razdjelnik 6 krugova',
        'max_loops': 6,
        'volume': 0.9,
    },
    '7-krugova': {
        'display': 'Razdjelnik 7 krugova',
        'max_loops': 7,
        'volume': 1.0,
    },
    '8-krugova': {
        'display': 'Razdjelnik 8 krugova',
        'max_loops': 8,
        'volume': 1.1,
    },
    '9-krugova': {
        'display': 'Razdjelnik 9 krugova',
        'max_loops': 9,
        'volume': 1.2,
    },
    '10-krugova': {
        'display': 'Razdjelnik 10 krugova',
        'max_loops': 10,
        'volume': 1.3,
    },
    '11-krugova': {
        'display': 'Razdjelnik 11 krugova',
        'max_loops': 11,
        'volume': 1.4,
    },
    '12-krugova': {
        'display': 'Razdjelnik 12 krugova',
        'max_loops': 12,
        'volume': 1.5,
    }
}

# Predlošci naziva etaža
FLOOR_NAMES = [
    'Podrum',
    'Suteren',
    'Prizemlje',
    '1. kat',
    '2. kat',
    '3. kat',
    '4. kat',
    '5. kat',
    'Potkrovlje'
]