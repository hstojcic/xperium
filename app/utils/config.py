"""
Konfiguracija aplikacije
"""

# Konstante aplikacije
APP_NAME = "Proračuni instalacija"
APP_VERSION = "1.0.0"

# Putanje
SAVE_DIR = "saved_calculations"
EXPORT_DIR = "exports"

# Postavke
DEFAULT_EXTENSION = ".calc"
AUTO_SAVE_INTERVAL = 300  # sekundi (5 minuta)

# Definicije kategorija (možda će biti korištene u budućnosti)
CATEGORY_DEFINITIONS = {
    "Hidrotehničke instalacije": {
        "description": "Proračuni vezani za vodovodne, bazenske, sanitarne i oborinske instalacije",
        "subcategories": {
            "Instalacije vodovoda": "Proračuni vodovodnih instalacija",
            "Instalacije bazenske tehnike": "Proračuni bazenskih sustava",
            "Instalacije sanitarne kanalizacije": "Proračuni sanitarne kanalizacije",
            "Instalacije oborinske kanalizacije": "Proračuni oborinske kanalizacije"
        }
    },
    "Termotehničke instalacije": {
        "description": "Proračuni vezani za plinske, grijanje, hlađenje i ventilaciju",
        "subcategories": {
            "Instalacije plina": "Proračuni plinskih instalacija",
            "Instalacije grijanja": "Proračuni sustava grijanja",
            "Instalacije grijanja i hlađenja": "Kombinirani proračuni grijanja i hlađenja",
            "Instalacije hlađenja": "Proračuni sustava hlađenja",
            "Instalacije ventilacije": "Proračuni ventilacijskih sustava"
        }
    }
}