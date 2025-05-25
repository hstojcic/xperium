"""
Modul koji sadrži klasu Etaza za rad s etažama u proračunu toplinskih gubitaka.
"""

import uuid

class Etaza:
    """Klasa koja predstavlja jednu etažu u proračunu."""
    def __init__(self, id=None, naziv="Nova etaža", redni_broj=1, visina_etaze=2.5, prostorije=None, broj_etaze=None):
        self.id = id if id is not None else uuid.uuid4().hex
        self.naziv = naziv
        self.redni_broj = int(redni_broj)
        self.broj_etaze = broj_etaze if broj_etaze is not None else redni_broj  # Broj etaže za numeraciju prostorija
        self.visina_etaze = float(visina_etaze)
        self.prostorije = prostorije if prostorije is not None else []
        self.stambene_jedinice = []  # Nova lista stambenih jedinica na ovoj etaži
        
    def dodaj_stambenu_jedinicu(self, stambena_jedinica_id):
        """Dodaje stambenu jedinicu na ovu etažu."""
        if stambena_jedinica_id not in self.stambene_jedinice:
            self.stambene_jedinice.append(stambena_jedinica_id)
    
    def ukloni_stambenu_jedinicu(self, stambena_jedinica_id):
        """Uklanja stambenu jedinicu s ove etaže."""
        if stambena_jedinica_id in self.stambene_jedinice:
            self.stambene_jedinice.remove(stambena_jedinica_id)
    
    def dohvati_prostorije_za_stambenu_jedinicu(self, stambena_jedinica_id):
        """Dohvaća prostorije koje pripadaju određenoj stambenoj jedinici na ovoj etaži."""
        return [p for p in self.prostorije if hasattr(p, 'stambena_jedinica_id') and p.stambena_jedinica_id == stambena_jedinica_id]

    def to_dict(self):
        """Pretvara objekt Etaza u rječnik za spremanje."""
        return {
            "id": self.id,
            "naziv": self.naziv,
            "redni_broj": self.redni_broj,
            "broj_etaze": self.broj_etaze,
            "visina_etaze": self.visina_etaze,
            "prostorije": [p.id if hasattr(p, 'id') else p for p in self.prostorije] if self.prostorije else [],
            "stambene_jedinice": self.stambene_jedinice  # Dodano u serializaciju
        }

    @classmethod
    def from_dict(cls, data):
        """Stvara objekt Etaza iz rječnika."""
        etaza = cls(
            id=data.get("id"),
            naziv=data.get("naziv", "Nova etaža"),
            redni_broj=int(data.get("redni_broj", 1)),
            broj_etaze=data.get("broj_etaze"),
            visina_etaze=float(data.get("visina_etaze", 2.5)),
            prostorije=data.get("prostorije", [])
        )
        etaza.stambene_jedinice = data.get("stambene_jedinice", [])  # Učitavanje stambenih jedinica
        return etaza
