"""
Modul koji sadrži klasu SegmentZida za rad sa segmentima zidova.
"""

import uuid

class SegmentZida:
    """Klasa koja predstavlja segment unutarnjeg zida."""
    def __init__(self, id=None, duljina=1.0, tip_segmenta="prema_prostoriji", 
                 povezana_prostorija_id=None, orijentacija=None):
        self.id = id if id else str(uuid.uuid4())
        self.duljina = duljina
        self.tip_segmenta = tip_segmenta  # Moguće vrijednosti: "prema_negrijanom", "prema_prostoriji"
        self.povezana_prostorija_id = povezana_prostorija_id
        self.orijentacija = orijentacija

    def to_dict(self):
        """Pretvara segment zida u rječnik za spremanje."""
        return {
            "id": self.id,
            "duljina": self.duljina,
            "tip_segmenta": self.tip_segmenta,
            "povezana_prostorija_id": self.povezana_prostorija_id,
            "orijentacija": self.orijentacija
        }

    @classmethod
    def from_dict(cls, data):
        """Stvara objekt SegmentZida iz rječnika."""
        return cls(
            id=data.get("id"),
            duljina=data.get("duljina", 1.0),
            tip_segmenta=data.get("tip_segmenta", "prema_prostoriji"),
            povezana_prostorija_id=data.get("povezana_prostorija_id"),
            orijentacija=data.get("orijentacija")
        )
