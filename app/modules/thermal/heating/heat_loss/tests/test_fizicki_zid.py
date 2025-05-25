"""
Modul koji sadrži osnovne testove za fizičke zidove.
"""

import unittest
from unittest.mock import MagicMock
from ..models.elementi.fizicki_zid import FizickiZid

class TestFizickiZid(unittest.TestCase):
    """Testovi za klasu FizickiZid."""
    
    def setUp(self):
        """Priprema za testove."""
        self.fizicki_zid = FizickiZid(
            id="test-zid",
            tip="vanjski",
            orijentacija="Sjever",
            duzina=5.0,
            visina=2.8
        )
    
    def test_init(self):
        """Test inicijalizacije fizičkog zida."""
        self.assertEqual(self.fizicki_zid.id, "test-zid")
        self.assertEqual(self.fizicki_zid.tip, "vanjski")
        self.assertEqual(self.fizicki_zid.orijentacija, "Sjever")
        self.assertEqual(self.fizicki_zid.duzina, 5.0)
        self.assertEqual(self.fizicki_zid.visina, 2.8)
        self.assertFalse(self.fizicki_zid.je_segmentiran)
        self.assertEqual(len(self.fizicki_zid.segmenti), 0)
        self.assertEqual(len(self.fizicki_zid.povezane_prostorije), 0)
    
    def test_dodaj_povezanu_prostoriju(self):
        """Test dodavanja povezane prostorije."""
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1")
        self.assertEqual(len(self.fizicki_zid.povezane_prostorije), 1)
        self.assertEqual(self.fizicki_zid.povezane_prostorije[0]["prostorija_id"], "prostorija1")
        self.assertEqual(self.fizicki_zid.povezane_prostorije[0]["zid_referenca_id"], "zid1")
        
        # Dodaj još jednu prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija2", "zid2")
        self.assertEqual(len(self.fizicki_zid.povezane_prostorije), 2)
        
        # Ažuriraj postojeću prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1-novo")
        self.assertEqual(len(self.fizicki_zid.povezane_prostorije), 2)
        for povezana in self.fizicki_zid.povezane_prostorije:
            if povezana["prostorija_id"] == "prostorija1":
                self.assertEqual(povezana["zid_referenca_id"], "zid1-novo")
    
    def test_ukloni_povezanu_prostoriju(self):
        """Test uklanjanja povezane prostorije."""
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1")
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija2", "zid2")
        
        # Ukloni prostoriju
        result = self.fizicki_zid.ukloni_povezanu_prostoriju("prostorija1")
        self.assertTrue(result)
        self.assertEqual(len(self.fizicki_zid.povezane_prostorije), 1)
        self.assertEqual(self.fizicki_zid.povezane_prostorije[0]["prostorija_id"], "prostorija2")
        
        # Pokušaj ukloniti nepostojeću prostoriju
        result = self.fizicki_zid.ukloni_povezanu_prostoriju("nepostojeca")
        self.assertFalse(result)
        self.assertEqual(len(self.fizicki_zid.povezane_prostorije), 1)
    
    def test_dohvati_povezanu_referencu(self):
        """Test dohvaćanja reference na zid u prostoriji."""
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1")
        
        # Dohvati referencu
        referenca = self.fizicki_zid.dohvati_povezanu_referencu("prostorija1")
        self.assertEqual(referenca, "zid1")
        
        # Dohvati nepostojeću referencu
        referenca = self.fizicki_zid.dohvati_povezanu_referencu("nepostojeca")
        self.assertIsNone(referenca)
    
    def test_azuriraj_tip(self):
        """Test ažuriranja tipa zida."""
        self.assertEqual(self.fizicki_zid.tip, "vanjski")
        self.assertEqual(self.fizicki_zid.orijentacija, "Sjever")
        
        # Ažuriraj tip
        self.fizicki_zid.azuriraj_tip("prema_prostoriji")
        self.assertEqual(self.fizicki_zid.tip, "prema_prostoriji")
        self.assertIsNone(self.fizicki_zid.orijentacija)
    
    def test_ima_suprotnu_stranu(self):
        """Test provjere ima li zid suprotnu stranu."""
        self.assertFalse(self.fizicki_zid.ima_suprotnu_stranu())
        
        # Dodaj jednu prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1")
        self.assertFalse(self.fizicki_zid.ima_suprotnu_stranu())
        
        # Dodaj drugu prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija2", "zid2")
        self.assertTrue(self.fizicki_zid.ima_suprotnu_stranu())
    
    def test_treba_biti_prema_prostoriji(self):
        """Test provjere treba li zid biti tipa 'prema_prostoriji'."""
        self.assertFalse(self.fizicki_zid.treba_biti_prema_prostoriji())
        
        # Dodaj jednu prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1")
        self.assertFalse(self.fizicki_zid.treba_biti_prema_prostoriji())
        
        # Dodaj drugu prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija2", "zid2")
        self.assertTrue(self.fizicki_zid.treba_biti_prema_prostoriji())
    
    def test_osvjezi_tip_na_temelju_povezanosti(self):
        """Test osvježavanja tipa zida na temelju povezanosti."""
        self.assertEqual(self.fizicki_zid.tip, "vanjski")
        
        # Dodaj jednu prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1")
        self.fizicki_zid.osvjezi_tip_na_temelju_povezanosti()
        self.assertEqual(self.fizicki_zid.tip, "vanjski")
        
        # Dodaj drugu prostoriju
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija2", "zid2")
        self.fizicki_zid.osvjezi_tip_na_temelju_povezanosti()
        self.assertEqual(self.fizicki_zid.tip, "prema_prostoriji")
    
    def test_to_dict(self):
        """Test pretvaranja u rječnik."""
        self.fizicki_zid.dodaj_povezanu_prostoriju("prostorija1", "zid1")
        
        rjecnik = self.fizicki_zid.to_dict()
        self.assertEqual(rjecnik["id"], "test-zid")
        self.assertEqual(rjecnik["tip"], "vanjski")
        self.assertEqual(rjecnik["orijentacija"], "Sjever")
        self.assertEqual(rjecnik["duzina"], 5.0)
        self.assertEqual(rjecnik["visina"], 2.8)
        self.assertFalse(rjecnik["je_segmentiran"])
        self.assertEqual(len(rjecnik["segmenti"]), 0)
        self.assertEqual(len(rjecnik["povezane_prostorije"]), 1)
        self.assertEqual(rjecnik["povezane_prostorije"][0]["prostorija_id"], "prostorija1")
        self.assertEqual(rjecnik["povezane_prostorije"][0]["zid_referenca_id"], "zid1")
    
    def test_from_dict(self):
        """Test stvaranja iz rječnika."""
        rjecnik = {
            "id": "test-zid-2",
            "tip": "prema_prostoriji",
            "orijentacija": None,
            "duzina": 4.0,
            "visina": 3.0,
            "je_segmentiran": True,
            "segmenti": [],
            "elementi": {},
            "povezane_prostorije": [
                {"prostorija_id": "prostorija1", "zid_referenca_id": "zid1"},
                {"prostorija_id": "prostorija2", "zid_referenca_id": "zid2"}
            ]
        }
        
        fizicki_zid = FizickiZid.from_dict(rjecnik)
        self.assertEqual(fizicki_zid.id, "test-zid-2")
        self.assertEqual(fizicki_zid.tip, "prema_prostoriji")
        self.assertIsNone(fizicki_zid.orijentacija)
        self.assertEqual(fizicki_zid.duzina, 4.0)
        self.assertEqual(fizicki_zid.visina, 3.0)
        self.assertTrue(fizicki_zid.je_segmentiran)
        self.assertEqual(len(fizicki_zid.povezane_prostorije), 2)
        self.assertEqual(fizicki_zid.povezane_prostorije[0]["prostorija_id"], "prostorija1")
        self.assertEqual(fizicki_zid.povezane_prostorije[0]["zid_referenca_id"], "zid1")
        self.assertEqual(fizicki_zid.povezane_prostorije[1]["prostorija_id"], "prostorija2")
        self.assertEqual(fizicki_zid.povezane_prostorije[1]["zid_referenca_id"], "zid2")
