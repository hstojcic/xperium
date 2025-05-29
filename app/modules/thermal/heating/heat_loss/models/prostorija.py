"""
Modul koji sadrži klasu Prostorija za rad s prostorijama u proračunu toplinskih gubitaka.
"""

import uuid
from .elementi.constants import TIPOVI_PROSTORIJA
from .elementi.zid import create_wall
from .elementi.wall_elements import WallElements
from .elementi.segment_zida import SegmentZida
from .elementi.fizicki_zid import FizickiZid # Added import

class Prostorija:
    """Klasa koja predstavlja jednu prostoriju u proračunu."""
    def __init__(self, id=None, naziv="Nova prostorija", tip="Dnevni boravak", 
                 etaza_id=None, povrsina=20.0, model_ref=None, broj_prostorije=None):        
        self.id = id if id is not None else uuid.uuid4().hex
        self.naziv = naziv
        self.tip = tip
        self.etaza_id = etaza_id
        self.povrsina = float(povrsina)
        self.broj_prostorije = broj_prostorije  # Broj prostorije na etaži
        self.oznaka = ""  # Oznaka prostorije (za interno korištenje)
        self.visina = None  # Može se postaviti kasnije, ili preuzeti s etaže
        self.koristi_zadanu_visinu = True # Ako je False, koristi visinu etaže
        self.grijana = TIPOVI_PROSTORIJA.get(tip, {}).get("grijana", True)  # Dodano svojstvo grijana
        self.temp_unutarnja = TIPOVI_PROSTORIJA.get(tip, {}).get("temp", 20)
        self.izracunata_temp_negrijane = None  # Dodano za izračunatu temperaturu negrijane prostorije
        self.izmjene_zraka = TIPOVI_PROSTORIJA.get(tip, {}).get("izmjene", 0.5)
        self.temperatura_susjednog_negrijanog = 10.0
        self.pod_tip = "Prema tlu"
        self.pod_tip_id = None  # Dodano
        self.strop_tip = "Prema negrijanom prostoru"
        self.strop_tip_id = None  # Dodano
        self.ventilacija_gubitci = 0.0  # Dodano
        self.dodatni_gubici = 0.0  # Dodano
        self.zidovi = []  # Lista rječnika koji predstavljaju zidove
        self.model_ref = model_ref
        
    def get_formatted_broj_prostorije(self):
        """
        Vraća formatirani broj prostorije u formatu etaza.prostorija ili samo prostorija
        ovisno o broju etaža u modelu.
        
        Returns:
        --------
        str
            Formatirani broj prostorije (npr. "1.1" ili "1")
        """
        if not self.broj_prostorije:
            return ""
            
        # Ako nemamo model_ref, vraćamo samo broj prostorije
        if not self.model_ref:
            return str(self.broj_prostorije)
            
        try:
            # Dobijemo broj etaža u modelu
            broj_etaza = len(self.model_ref.etaze) if hasattr(self.model_ref, 'etaze') else 1
            
            # Ako je samo jedna etaža, prikazujemo samo broj prostorije
            if broj_etaza <= 1:
                return str(self.broj_prostorije)
            
            # Ako je više etaža, trebamo broj etaže
            etaza = self.model_ref.dohvati_etazu(self.etaza_id) if self.etaza_id else None
            if etaza and hasattr(etaza, 'broj_etaze') and etaza.broj_etaze is not None:
                return f"{etaza.broj_etaze}.{self.broj_prostorije}"
            else:
                # Fallback - pokušaj pronaći redni broj etaže
                for i, et in enumerate(self.model_ref.etaze, 1):
                    if et.id == self.etaza_id:
                        return f"{i}.{self.broj_prostorije}"
                        
                # Ako ne možemo pronaći etažu, vraćamo samo broj prostorije
                return str(self.broj_prostorije)
                
        except Exception:
            # U slučaju greške, vraćamo samo broj prostorije
            return str(self.broj_prostorije)
        
    def azuriraj_tip_prostorije(self, novi_tip):
        """
        Ažurira tip prostorije i povezane atribute (temperatura, izmjene zraka, grijana).
        """
        self.tip = novi_tip
        if novi_tip in TIPOVI_PROSTORIJA:
            self.temp_unutarnja = TIPOVI_PROSTORIJA[novi_tip].get("temp", self.temp_unutarnja)
            self.izmjene_zraka = TIPOVI_PROSTORIJA[novi_tip].get("izmjene", self.izmjene_zraka)
            self.grijana = TIPOVI_PROSTORIJA[novi_tip].get("grijana", True)
            
    def izracunaj_temperaturu_negrijane_prostorije(self, vanjska_temp, okolne_prostorije=None):
        """
        Izračunava temperaturu negrijane prostorije na temelju okolnih prostorija i vanjske temperature.
        Koristi toplinski model ravnoteže prema EN ISO 13789.
        
        Parameters:
        -----------
        vanjska_temp : float
            Vanjska projektna temperatura
        okolne_prostorije : list
            Lista okolnih prostorija (ako nije navedeno, pokušat će se dohvatiti iz modela)
            
        Returns:
        --------
        float
            Izračunata temperatura negrijane prostorije
        """
        if self.grijana:
            return self.temp_unutarnja  # Ako je prostorija grijana, vraćamo postavljenu temperaturu
            
        # Ako nemamo okolne prostorije, a imamo model_ref, pokušajmo ih dohvatiti
        if okolne_prostorije is None and self.model_ref:
            okolne_prostorije = []
            # Dohvaćamo prostorije povezane preko zidova
            for zid in self.zidovi:
                if zid.get("tip") == "prema_prostoriji" and zid.get("povezana_prostorija_id"):
                    povezana_prostorija = self.model_ref.dohvati_prostoriju(zid.get("povezana_prostorija_id"))
                    if povezana_prostorija and povezana_prostorija.id != self.id:
                        okolne_prostorije.append(povezana_prostorija)
                        
        # Ako nemamo okolne prostorije, vraćamo procijenjenu vrijednost
        if not okolne_prostorije:
            # Vraćamo srednju vrijednost između vanjske temperature i 20°C
            return (vanjska_temp + 20) / 2
        
        # Izračun temperature pomoću toplinskog modela ravnoteže
        # Za svaku okolnu prostoriju, potrebno nam je:
        # - temperatura prostorije
        # - površina zajedničkog zida
        # - U-vrijednost (koeficijent prolaza topline) zajedničkog zida
        
        # Toplinski tokovi prema formuli: Q = U * A * (T1 - T2)
        # Inicijalizacija varijabli za sumu toplinskih tokova
        suma_UA_grijanih = 0.0
        suma_UAt_grijanih = 0.0
        suma_UA_vanjskih = 0.0
        
        # Koeficijent za vanjsku ovojnicu (aproksimativno)
        U_vanjski_default = 0.3  # W/(m²K) - prosječna vrijednost za vanjske zidove
        
        # Izračun učinka okolnih prostorija
        for povezana_prostorija in okolne_prostorije:
            # Tražimo zid prema povezanoj prostoriji
            for zid in self.zidovi:
                if (zid.get("tip") == "prema_prostoriji" and 
                    zid.get("povezana_prostorija_id") == povezana_prostorija.id):
                    
                    # Osnovni podaci zida
                    povrsina_zida = zid.get("duzina", 0.0) * zid.get("visina", 0.0)
                    
                    # Dohvat U-vrijednosti zida (aproksimativno)
                    # Idealno bi bilo dohvatiti točnu vrijednost iz definicije zida
                    u_vrijednost = 1.0  # W/(m²K) - default za unutarnje zidove
                    
                    if hasattr(zid.get("elementi"), "u_vrijednost") and zid.get("elementi").u_vrijednost:
                        u_vrijednost = zid.get("elementi").u_vrijednost
                    
                    # Koeficijent UA (produkt U-vrijednosti i površine)
                    UA = u_vrijednost * povrsina_zida
                    
                    if povezana_prostorija.grijana:
                        # Za grijanu prostoriju: dodajemo doprinos temperaturi
                        suma_UA_grijanih += UA
                        suma_UAt_grijanih += UA * povezana_prostorija.temp_unutarnja
                    else:
                        # Za negrijanu prostoriju koristimo trenutnu izračunatu temperaturu
                        # ako je dostupna, inače koristimo aproksimaciju
                        temp_negrijane = povezana_prostorija.izracunata_temp_negrijane
                        if temp_negrijane is None:
                            # Ako nemamo izračunatu temperaturu, koristimo temperatura_susjednog_negrijananog ili srednju vrijednost
                            temp_negrijane = povezana_prostorija.temperatura_susjednog_negrijananog
                            if temp_negrijane is None or temp_negrijane == 0:
                                temp_negrijane = (vanjska_temp + povezana_prostorija.temp_unutarnja) / 2
                        
                        suma_UA_grijanih += UA
                        suma_UAt_grijanih += UA * temp_negrijane
        
        # Procjena vanjske površine i toplinskog gubitka prema vanjskom prostoru
        # Za pojednostavljeni model, pretpostavljamo da površina koja nije prema drugim
        # prostorijama ide prema vanjskom prostoru
        ukupna_povrsina_ovojnice = 0.0
        
        # Aproksimacija ukupne površine ovojnice (uključujući pod i strop)
        visina_prostorije = 0.0
        for zid in self.zidovi:
            if zid.get("visina"):
                visina_prostorije = zid.get("visina")
                break
        
        if visina_prostorije <= 0.0:
            visina_prostorije = 2.5  # Default vrijednost ako nema podatka
        
        # Površina ovojnice po formuli: P = 2*(duljina + širina)*visina + 2*(duljina*širina)
        obujam_prostorije = self.povrsina * visina_prostorije
        aproks_duljina = (self.povrsina)**0.5  # Pretpostavka kvadratne prostorije
        ukupna_povrsina_ovojnice = 2 * (2 * aproks_duljina) * visina_prostorije + 2 * self.povrsina
        
        # Površina zidova prema vanjskom prostoru
        povrsina_prema_vani = ukupna_povrsina_ovojnice
        
        # Oduzimamo površine zidova prema okolnim prostorijama
        for povezana_prostorija in okolne_prostorije:
            for zid in self.zidovi:
                if (zid.get("tip") == "prema_prostoriji" and 
                    zid.get("povezana_prostorija_id") == povezana_prostorija.id):
                    povrsina_zida = zid.get("duzina", 0.0) * zid.get("visina", 0.0)
                    povrsina_prema_vani -= povrsina_zida
        
        # Toplinski gubitak prema van (minimalni koeficijent 10% ukupne površine)
        povrsina_prema_vani = max(povrsina_prema_vani, 0.1 * ukupna_povrsina_ovojnice)
        suma_UA_vanjskih = U_vanjski_default * povrsina_prema_vani
        
        # Dodatni koeficijent za utjecaj tla (ako je pod_tip == "Prema tlu")
        if self.pod_tip == "Prema tlu":
            temperatura_tla = (vanjska_temp + 7.0)  # Pojednostavljena procjena temperature tla
            temperatura_tla = max(5.0, min(temperatura_tla, 12.0))  # Ograničenje na razumne vrijednosti
            
            # Aproksimacija toplinskog toka prema tlu
            U_tlo_default = 0.25  # W/(m²K) - prosječna vrijednost za pod na tlu
            suma_UA_tlo = U_tlo_default * self.povrsina
            suma_UAt_tlo = suma_UA_tlo * temperatura_tla
            
            # Dodavanje utjecaja tla
            suma_UA_vanjskih += suma_UA_tlo
            suma_UAt_grijanih += suma_UAt_tlo
        
        # Konačni izračun temperature po formuli toplinske ravnoteže
        # Ti = (suma_UAt_grijanih + suma_UA_vanjskih * Te) / (suma_UA_grijanih + suma_UA_vanjskih)
        
        if (suma_UA_grijanih + suma_UA_vanjskih) > 0:
            izracunata_temp = (suma_UAt_grijanih + suma_UA_vanjskih * vanjska_temp) / (suma_UA_grijanih + suma_UA_vanjskih)
        else:
            # Ako nema toplinskih tokova, koristimo jednostavnu aproksimaciju
            izracunata_temp = (vanjska_temp + 15) / 2  # Srednja vrijednost između vanjske temperature i 15°C
        
        # Ograničenje na realnu vrijednost (ne može biti niža od vanjske - 2°C ili viša od unutarnje + 2°C)
        grijane_prostorije = [p for p in okolne_prostorije if hasattr(p, 'grijana') and p.grijana]
        max_temp = max([p.temp_unutarnja for p in grijane_prostorije] or [20.0]) + 2.0
        min_temp = vanjska_temp - 2.0
        izracunata_temp = max(min_temp, min(izracunata_temp, max_temp))
        
        return round(izracunata_temp, 1)
        
    def dodaj_zid(self, tip="vanjski", orijentacija="Sjever", duzina=5.0, visina_zida=None, 
                  povezana_prostorija_obj=None, model_ref=None,
                  postojeci_id_zida_A=None, 
                  je_segmentiran_val=False, 
                  segmenti_val=None, # Expects a list of SegmentZida objects or None
                  elementi_obj=None, # Expects a WallElements object or None
                  fizicki_zid_ref=None, # Reference na fizički zid
                  tip_zida_id=None): # ID tipa zida iz kataloga
        """
        Dodaje novi zid u prostoriju. 
        Ako je tip 'prema_prostoriji' i povezana_prostorija_obj je zadan,
        automatski kreira odgovarajući zid u povezanoj prostoriji.
        """
        try:
            processed_duzina = float(duzina)
            if processed_duzina <= 0:
                # Invalid length, cannot create wall
                return None 
        except (ValueError, TypeError):
            # duzina is not a valid number
            return None

        novi_id_zida_A = postojeci_id_zida_A if postojeci_id_zida_A is not None else uuid.uuid4().hex
        
        # Koristimo elemente iz fizičkog zida ako je dostupan, inače koristimo predani elementi_obj ili stvaramo novi
        dijeljeni_elementi = None
        if fizicki_zid_ref is not None:
            dijeljeni_elementi = fizicki_zid_ref.elementi
        else:
            dijeljeni_elementi = elementi_obj if elementi_obj is not None else WallElements()

        stvarna_visina_zida_A = None
        if visina_zida is not None:
            try:
                candidate_visina = float(visina_zida)
                if candidate_visina > 0:
                    stvarna_visina_zida_A = candidate_visina
            except (ValueError, TypeError):
                pass # stvarna_visina_zida_A remains None, fallback will occur
        
        if stvarna_visina_zida_A is None: # Covers visina_zida being None, invalid, or non-positive
            if model_ref: 
                etaza_A = model_ref.dohvati_etazu(self.etaza_id)
                if etaza_A:
                    stvarna_visina_zida_A = self.get_actual_height(etaza_A)
                else: 
                    stvarna_visina_zida_A = 2.5 # Default if etaza_A not found
            else: 
                stvarna_visina_zida_A = 2.5 # Default if model_ref not available
             
        zid_A = {
            "id": novi_id_zida_A,
            "tip": tip,
            "orijentacija": orijentacija if tip == "vanjski" else None,
            "duzina": processed_duzina, # Use processed_duzina
            "visina": stvarna_visina_zida_A,
            "povezana_prostorija_id": None,
            "povezani_zid_id": None,
            "elementi": dijeljeni_elementi,
            "je_segmentiran": je_segmentiran_val,
            "segmenti": segmenti_val if segmenti_val is not None else [],
            "fizicki_zid_id": fizicki_zid_ref.id if fizicki_zid_ref is not None else None,
            "tip_zida_id": tip_zida_id  # ID tipa zida iz kataloga
        }

        if tip == "prema_prostoriji" and povezana_prostorija_obj and self.id != povezana_prostorija_obj.id:
            novi_id_zida_B = uuid.uuid4().hex
            zid_B = {
                "id": novi_id_zida_B,
                "tip": "prema_prostoriji", 
                "orijentacija": None, 
                "duzina": processed_duzina, # Use processed_duzina
                "visina": stvarna_visina_zida_A, 
                "povezana_prostorija_id": self.id, 
                "povezani_zid_id": novi_id_zida_A, 
                "elementi": dijeljeni_elementi, # Dijeljeni elementi
                "je_segmentiran": je_segmentiran_val, # Preslikavamo segmentaciju
                "segmenti": segmenti_val if segmenti_val is not None else [], # Preslikavamo segmente
                "fizicki_zid_id": fizicki_zid_ref.id if fizicki_zid_ref is not None else None,
                "tip_zida_id": tip_zida_id  # ID tipa zida iz kataloga - dodano za sinkronizaciju
            }
            povezana_prostorija_obj.zidovi.append(zid_B)

            zid_A["povezana_prostorija_id"] = povezana_prostorija_obj.id
            zid_A["povezani_zid_id"] = novi_id_zida_B
            zid_A["tip"] = "prema_prostoriji" 
            zid_A["orijentacija"] = None
        
        self.zidovi.append(zid_A)
        return zid_A

    def ukloni_zid(self, zid_id_za_uklanjanje, model_ref=None):
        """
        Uklanja zid iz prostorije. Ako je zid povezan s drugim zidom 
        u drugoj prostoriji, uklanja i taj povezani zid.
        """
        zid_za_uklanjanje = self.dohvati_zid(zid_id_za_uklanjanje)
        if not zid_za_uklanjanje:
            return False 

        povezana_prostorija_id = zid_za_uklanjanje.get("povezana_prostorija_id")
        povezani_zid_id_u_drugoj_prostoriji = zid_za_uklanjanje.get("povezani_zid_id")

        self.zidovi = [z for z in self.zidovi if z.get("id") != zid_id_za_uklanjanje]

        if povezana_prostorija_id and povezani_zid_id_u_drugoj_prostoriji and model_ref:
            povezana_prostorija_obj = model_ref.dohvati_prostoriju(povezana_prostorija_id)
            if povezana_prostorija_obj:
                povezana_prostorija_obj.zidovi = [
                    z for z in povezana_prostorija_obj.zidovi 
                    if z.get("id") != povezani_zid_id_u_drugoj_prostoriji
                ]
        return True

    def dohvati_zid(self, zid_id):
        """Dohvaća zid iz prostorije na temelju njegovog 'id' atributa."""
        for zid in self.zidovi:
            if zid.get("id") == zid_id:
                return zid
        return None
        
    def get_actual_height(self, parent_etaza):
        """
        Računa stvarnu visinu prostorije.
        """
        default_height_fallback = 2.8

        if not self.koristi_zadanu_visinu:
            if self.visina is not None:
                return float(self.visina)
            elif parent_etaza:
                return float(parent_etaza.visina_etaze)
            else:
                return default_height_fallback
        else:
            if parent_etaza:
                return float(parent_etaza.visina_etaze)
            else:
                return default_height_fallback
                
    def to_dict(self, fizicki_elementi_map=None):
        zidovi_dict_list = []
        for zid_obj in self.zidovi:  # Iterate directly over the list of wall dictionaries
            zid_dict = zid_obj.copy()  # Work with a copy of the wall dictionary

            # Ensure 'elementi' are serializable (e.g., convert WallElements to dict)
            if isinstance(zid_dict.get('elementi'), WallElements):
                zid_dict['elementi'] = zid_dict['elementi'].to_dict()
            
            # Ensure 'segmenti' are serializable (e.g., convert SegmentZida to dict)
            if 'segmenti' in zid_dict and isinstance(zid_dict['segmenti'], list):
                zid_dict['segmenti'] = [
                    seg.to_dict() if isinstance(seg, SegmentZida) else seg 
                    for seg in zid_dict['segmenti']
                ]
            
            # Always make sure we have a fizicki_zid_id field in the dictionary
            # This ensures that the UI can consistently display the physical wall ID
            if "fizicki_zid_id" in zid_dict and zid_dict["fizicki_zid_id"] is not None:
                # We already have a physical wall ID, no need to find it
                pass
            elif fizicki_elementi_map:
                # Search for the physical wall in the fizicki_elementi_map
                for fiz_elem in fizicki_elementi_map.values():
                    if isinstance(fiz_elem, FizickiZid):
                        # Check if this physical wall is connected to this room and wall
                        if hasattr(fiz_elem, 'povezane_prostorije'):
                            for povezana in fiz_elem.povezane_prostorije:
                                if povezana["prostorija_id"] == self.id and povezana["zid_referenca_id"] == zid_dict.get("id"):
                                    # Found the physical wall for this wall
                                    zid_dict["fizicki_zid_id"] = fiz_elem.id
                                    break
                        if "fizicki_zid_id" in zid_dict and zid_dict["fizicki_zid_id"] is not None:
                            break  # Exit the loop if we found the physical wall
            
            # If the wall is internal, find its corresponding FizickiZid
            # and get the povezana_prostorija_id
            if fizicki_elementi_map and zid_dict.get("tip") == "prema_prostoriji":
                for fiz_elem in fizicki_elementi_map.values():
                    if isinstance(fiz_elem, FizickiZid) and fiz_elem.id == zid_dict.get("fizicki_zid_id"):
                        # Check if we have a list of original_wall-room pairs
                        originalni_zid_soba_parovi = getattr(fiz_elem, 'originalni_zid_soba_parovi', None)
                        if originalni_zid_soba_parovi:
                            # Find the pair for this wall and room
                            for par in originalni_zid_soba_parovi:
                                if par.get("originalni_zid_id") == zid_dict.get("id") and par.get("prostorija_id") == self.id:
                                    # Found a match, now set up the povezana_prostorija_id if needed
                                    povezana_prostorija_id = getattr(fiz_elem, 'povezana_prostorija_id', None)
                                    if povezana_prostorija_id is not None:
                                        zid_dict["povezana_prostorija_id"] = povezana_prostorija_id
                                    break
                        # Fallback to old method if no pairs are available
                        elif (getattr(fiz_elem, 'originalni_zid_id', None) == zid_dict.get("id") and 
                              getattr(fiz_elem, 'prostorija_id', None) == self.id):
                            povezana_prostorija_id = getattr(fiz_elem, 'povezana_prostorija_id', None)
                            if povezana_prostorija_id is not None:
                                zid_dict["povezana_prostorija_id"] = povezana_prostorija_id
                            break  # Found the corresponding FizickiZid
            
            zidovi_dict_list.append(zid_dict)        
            return {
            "id": self.id,
            "naziv": self.naziv,
            "broj_prostorije": self.broj_prostorije, # Broj prostorije na etaži
            "oznaka": getattr(self, 'oznaka', ''), # Add oznaka, ensure it exists or default
            "tip": self.tip, # Add type
            "etaza_id": self.etaza_id,
            "temp_unutarnja": self.temp_unutarnja,
            "povrsina": self.povrsina,
            "visina": self.visina,
            "zidovi": zidovi_dict_list,
            "pod_tip": self.pod_tip,
            "pod_tip_id": getattr(self, 'pod_tip_id', None), # Ensure exists or default
            "strop_tip": self.strop_tip,
            "strop_tip_id": getattr(self, 'strop_tip_id', None), # Ensure exists or default
            "ventilacija_gubitci": getattr(self, 'ventilacija_gubitci', 0.0), # Ensure exists or default
            "dodatni_gubici": getattr(self, 'dodatni_gubici', 0.0), # Ensure exists or default
            "grijana": getattr(self, 'grijana', True), # Dodano svojstvo grijana
            "izracunata_temp_negrijane": getattr(self, 'izracunata_temp_negrijane', None) # Dodana izračunata temp
        }
        
    @classmethod
    def from_dict(cls, data, model_ref=None):
        """Stvara objekt Prostorija iz rječnika."""
        instance = cls(
            id=data.get("id"),
            naziv=data.get("naziv", "Nova prostorija"),
            tip=data.get("tip", "Dnevni boravak"),
            etaza_id=data.get("etaza_id"),
            povrsina=float(data.get("povrsina", 20.0)),
            model_ref=model_ref,
            broj_prostorije=data.get("broj_prostorije")
        )
        instance.visina = data.get("visina")
        instance.koristi_zadanu_visinu = data.get("koristi_zadanu_visinu", True)
        instance.oznaka = data.get("oznaka", "")  # Dodaj oznaka polje
        instance.grijana = data.get("grijana", TIPOVI_PROSTORIJA.get(instance.tip, {}).get("grijana", True))
        instance.temp_unutarnja = data.get("temp_unutarnja", TIPOVI_PROSTORIJA.get(instance.tip, {}).get("temp", 20))
        instance.izracunata_temp_negrijane = data.get("izracunata_temp_negrijane")        
        instance.izmjene_zraka = data.get("izmjene_zraka", TIPOVI_PROSTORIJA.get(instance.tip, {}).get("izmjene", 0.5))
        instance.temperatura_susjednog_negrijanog = data.get("temperatura_susjednog_negrijanog", 10.0)
        
        # Učitaj ostale atribute
        instance.pod_tip = data.get("pod_tip", "Prema tlu")
        instance.pod_tip_id = data.get("pod_tip_id")
        instance.strop_tip = data.get("strop_tip", "Prema negrijanom prostoru")
        instance.strop_tip_id = data.get("strop_tip_id")
        instance.ventilacija_gubitci = data.get("ventilacija_gubitci", 0.0)
        instance.dodatni_gubici = data.get("dodatni_gubici", 0.0)
        
        # Učitaj zidove
        zidovi_data = data.get("zidovi", [])
        instance.zidovi = []
        
        for zid_data in zidovi_data:
            zid_dict = zid_data.copy()
            
            # Convert WallElements from dict if needed
            if isinstance(zid_dict.get('elementi'), dict):
                zid_dict['elementi'] = WallElements.from_dict(zid_dict['elementi'])
            elif not isinstance(zid_dict.get('elementi'), WallElements):
                zid_dict['elementi'] = WallElements()
            
            # Convert segments from dict if needed
            if 'segmenti' in zid_dict and isinstance(zid_dict['segmenti'], list):
                converted_segmenti = []
                for seg in zid_dict['segmenti']:
                    if isinstance(seg, dict):
                        converted_segmenti.append(SegmentZida.from_dict(seg))
                    elif isinstance(seg, SegmentZida):
                        converted_segmenti.append(seg)
                zid_dict['segmenti'] = converted_segmenti
            
            instance.zidovi.append(zid_dict)
        
        return instance
