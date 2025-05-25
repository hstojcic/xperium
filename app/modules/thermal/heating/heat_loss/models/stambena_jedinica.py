"""
Modul koji sadrži klasu StambenaJedinica za rad s stambenim jedinicama u proračunu toplinskih gubitaka.
"""

import uuid

class StambenaJedinica:
    """Klasa koja predstavlja jednu stambenu jedinicu u proračunu."""
    
    def __init__(self, id=None, naziv="Nova stambena jedinica", tip="Stan", opis="", etaza_id=None):
        self.id = id if id is not None else uuid.uuid4().hex
        self.naziv = naziv
        self.tip = tip  # "Stan", "Poslovni prostor", "Zajednički prostori", "Garaža", itd.
        self.opis = opis
        self.etaza_id = etaza_id  # ID etaže na kojoj se nalazi ova stambena jedinica
        self.prostorije = []  # Lista ID-jeva prostorija koje pripadaju ovoj stambenoj jedinici
        
        # Kalkulirana svojstva (ažuriravaju se tijekom proračuna)
        self.ukupna_povrsina = 0.0
        self.ukupni_gubici = 0.0
        self.specificni_gubici = 0.0  # W/m²
        
    def dodaj_prostoriju(self, prostorija_id):
        """Dodaje prostoriju u ovu stambenu jedinicu."""
        if prostorija_id not in self.prostorije:
            self.prostorije.append(prostorija_id)
    
    def ukloni_prostoriju(self, prostorija_id):
        """Uklanja prostoriju iz ove stambene jedinice."""
        if prostorija_id in self.prostorije:
            self.prostorije.remove(prostorija_id)
    
    def azuriraj_kalkulirana_svojstva(self, ukupna_povrsina, ukupni_gubici):
        """Ažurira kalkulirana svojstva na temelju proračuna."""
        self.ukupna_povrsina = float(ukupna_povrsina)
        self.ukupni_gubici = float(ukupni_gubici)
        self.specificni_gubici = ukupni_gubici / ukupna_povrsina if ukupna_povrsina > 0 else 0.0
    
    def get_formatted_naziv(self):
        """Vraća formatirani naziv stambene jedinice s tipom."""
        if self.tip == "Zajednički prostori":
            return f"{self.naziv}"
        else:
            return f"{self.naziv} ({self.tip})"
    
    def to_dict(self):
        """Pretvara objekt StambenaJedinica u rječnik za spremanje."""
        return {
            "id": self.id,
            "naziv": self.naziv,
            "tip": self.tip,
            "opis": self.opis,
            "etaza_id": self.etaza_id,
            "prostorije": self.prostorije,
            "ukupna_povrsina": self.ukupna_povrsina,
            "ukupni_gubici": self.ukupni_gubici,
            "specificni_gubici": self.specificni_gubici
        }

    @classmethod
    def from_dict(cls, data):
        """Stvara objekt StambenaJedinica iz rječnika."""
        stambena_jedinica = cls(
            id=data.get("id"),
            naziv=data.get("naziv", "Nova stambena jedinica"),
            tip=data.get("tip", "Stan"),
            opis=data.get("opis", ""),
            etaza_id=data.get("etaza_id")
        )
        stambena_jedinica.prostorije = data.get("prostorije", [])
        stambena_jedinica.ukupna_povrsina = float(data.get("ukupna_povrsina", 0.0))
        stambena_jedinica.ukupni_gubici = float(data.get("ukupni_gubici", 0.0))
        stambena_jedinica.specificni_gubici = float(data.get("specificni_gubici", 0.0))
        return stambena_jedinica

# Konstante za tipove stambenih jedinica
TIPOVI_STAMBENIH_JEDINICA = {
    "Stan": {
        "opis": "Stambeni prostor s kompletnom opremom za stanovanje",
        "ikona": "🏠"
    },
    "Poslovni prostor": {
        "opis": "Prostor namijenjen obavljanju gospodarske djelatnosti", 
        "ikona": "🏢"
    },
    "Zajednički prostori": {
        "opis": "Prostori koje koriste svi korisnici zgrade",
        "ikona": "🚪"
    },
    "Garaža": {
        "opis": "Prostor za parkiranje vozila",
        "ikona": "🚗"
    },
    "Ostalo": {
        "opis": "Ostali prostori",
        "ikona": "📦"
    }
}
