"""
Modul koji sadrži funkcije za analizu i povezivanje zidova između prostorija.
"""

def analiziraj_povezanost_zidova(model):
    """
    Analizira prostorije i identificira potencijalno povezane zidove.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s prostorijama
        
    Returns:
    --------
    list
        Lista potencijalnih povezivanja zidova u formatu:
        [
            {
                "prostorija1_id": str,
                "zid1_id": str,
                "prostorija2_id": str,
                "zid2_id": str,
                "pouzdanost": float  # 0.0 - 1.0
            },
            ...
        ]
    """
    potencijalna_povezivanja = []
    
    # Grupiramo prostorije po etažama za efikasniju analizu
    prostorije_po_etazama = {}
    for prostorija in model.prostorije:
        etaza_id = prostorija.etaza_id
        if etaza_id not in prostorije_po_etazama:
            prostorije_po_etazama[etaza_id] = []
        prostorije_po_etazama[etaza_id].append(prostorija)
    
    # Za svaku etažu, analiziramo prostorije
    for etaza_id, prostorije in prostorije_po_etazama.items():
        # Analiziramo svaki par prostorija na istoj etaži
        for i, prostorija1 in enumerate(prostorije):
            for j in range(i + 1, len(prostorije)):
                prostorija2 = prostorije[j]
                
                # Pronađi zidove koji bi mogli biti povezani (na istoj etaži)
                for zid1 in prostorija1.zidovi:
                    if zid1.get("tip") == "prema_prostoriji" and zid1.get("povezana_prostorija_id") == prostorija2.id:
                        # Ovaj zid je već povezan s drugom prostorijom
                        continue
                        
                    for zid2 in prostorija2.zidovi:
                        if zid2.get("tip") == "prema_prostoriji" and zid2.get("povezana_prostorija_id") == prostorija1.id:
                            # Ovaj zid je već povezan s prvom prostorijom
                            continue
                            
                        # Izračunaj pouzdanost da su ova dva zida zapravo isti fizički zid
                        pouzdanost = _izracunaj_pouzdanost_povezivanja(zid1, zid2, prostorija1, prostorija2)
                        
                        if pouzdanost > 0.5:  # Prag pouzdanosti
                            potencijalna_povezivanja.append({
                                "prostorija1_id": prostorija1.id,
                                "zid1_id": zid1.get("id"),
                                "prostorija2_id": prostorija2.id,
                                "zid2_id": zid2.get("id"),
                                "pouzdanost": pouzdanost
                            })
    
    # Sortiraj po pouzdanosti (od najveće prema najmanjoj)
    potencijalna_povezivanja.sort(key=lambda x: x["pouzdanost"], reverse=True)
    
    return potencijalna_povezivanja

def _izracunaj_pouzdanost_povezivanja(zid1, zid2, prostorija1, prostorija2):
    """
    Izračunava pouzdanost da su dva zida zapravo isti fizički zid.
    
    Parameters:
    -----------
    zid1, zid2 : dict
        Zidovi koji se uspoređuju
    prostorija1, prostorija2 : Prostorija
        Prostorije kojima pripadaju zidovi
        
    Returns:
    --------
    float
        Pouzdanost (0.0 - 1.0) da su zidovi isti fizički zid
    """
    pouzdanost = 0.0
    
    # 1. Provjera duljine (ista duljina je dobar indikator)
    duzina1 = float(zid1.get("duzina", 0))
    duzina2 = float(zid2.get("duzina", 0))
    
    if abs(duzina1 - duzina2) < 0.1:  # Tolerancija od 10cm
        pouzdanost += 0.4
    elif abs(duzina1 - duzina2) < 0.5:  # Tolerancija od 50cm
        pouzdanost += 0.2
    
    # 2. Provjera visine (ako su definirane)
    visina1 = zid1.get("visina")
    visina2 = zid2.get("visina")
    
    if visina1 is not None and visina2 is not None:
        if abs(float(visina1) - float(visina2)) < 0.1:  # Tolerancija od 10cm
            pouzdanost += 0.2
    
    # 3. Provjera orijentacije (ako su vanjski zidovi, trebali bi imati suprotne orijentacije)
    orijentacija1 = zid1.get("orijentacija")
    orijentacija2 = zid2.get("orijentacija")
    
    if orijentacija1 and orijentacija2:
        # Mapa suprotnih orijentacija
        suprotne_orijentacije = {
            "Sjever": "Jug",
            "Jug": "Sjever",
            "Istok": "Zapad",
            "Zapad": "Istok",
            "Sjeveroistok": "Jugozapad",
            "Sjeverozapad": "Jugoistok",
            "Jugozapad": "Sjeveroistok",
            "Jugoistok": "Sjeverozapad"
        }
        
        if suprotne_orijentacije.get(orijentacija1) == orijentacija2:
            pouzdanost += 0.2
    
    # 4. Provjera tipa zida (ako su oba zida istog tipa, to povećava pouzdanost)
    if zid1.get("tip") == zid2.get("tip"):
        pouzdanost += 0.2
    
    # Ograniči pouzdanost na 1.0
    return min(pouzdanost, 1.0)

def povezi_zidove(model, prostorija1_id, zid1_id, prostorija2_id, zid2_id):
    """
    Povezuje dva zida u različitim prostorijama kao isti fizički zid.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s prostorijama
    prostorija1_id, prostorija2_id : str
        ID prostorija čiji se zidovi povezuju
    zid1_id, zid2_id : str
        ID zidova koji se povezuju
        
    Returns:
    --------
    bool
        True ako je povezivanje uspjelo, False inače
    """
    # Dohvaćamo prostorije
    prostorija1 = model.dohvati_prostoriju(prostorija1_id)
    prostorija2 = model.dohvati_prostoriju(prostorija2_id)
    
    if not prostorija1 or not prostorija2:
        return False
    
    # Dohvaćamo zidove
    zid1 = prostorija1.dohvati_zid(zid1_id)
    zid2 = prostorija2.dohvati_zid(zid2_id)
    
    if not zid1 or not zid2:
        return False
    
    # Provjera postoji li već fizički zid za neki od zidova
    fizicki_zid_id1 = zid1.get("fizicki_zid_id")
    fizicki_zid_id2 = zid2.get("fizicki_zid_id")
    
    if fizicki_zid_id1 and fizicki_zid_id1 in model.fizicki_zidovi:
        # Koristimo postojeći fizički zid iz zid1
        fizicki_zid = model.fizicki_zidovi[fizicki_zid_id1]
        
        # Dodajemo prostoriju2 i zid2 kao povezane s ovim fizičkim zidom
        fizicki_zid.dodaj_povezanu_prostoriju(prostorija2_id, zid2_id)
        zid2["fizicki_zid_id"] = fizicki_zid.id
        
        # Ažuriramo tip zida
        fizicki_zid.osvjezi_tip_na_temelju_povezanosti()
        zid1["tip"] = "prema_prostoriji"
        zid2["tip"] = "prema_prostoriji"
        zid1["povezana_prostorija_id"] = prostorija2_id
        zid2["povezana_prostorija_id"] = prostorija1_id
        zid1["povezani_zid_id"] = zid2_id
        zid2["povezani_zid_id"] = zid1_id
        
    elif fizicki_zid_id2 and fizicki_zid_id2 in model.fizicki_zidovi:
        # Koristimo postojeći fizički zid iz zid2
        fizicki_zid = model.fizicki_zidovi[fizicki_zid_id2]
        
        # Dodajemo prostoriju1 i zid1 kao povezane s ovim fizičkim zidom
        fizicki_zid.dodaj_povezanu_prostoriju(prostorija1_id, zid1_id)
        zid1["fizicki_zid_id"] = fizicki_zid.id
        
        # Ažuriramo tip zida
        fizicki_zid.osvjezi_tip_na_temelju_povezanosti()
        zid1["tip"] = "prema_prostoriji"
        zid2["tip"] = "prema_prostoriji"
        zid1["povezana_prostorija_id"] = prostorija2_id
        zid2["povezana_prostorija_id"] = prostorija1_id
        zid1["povezani_zid_id"] = zid2_id
        zid2["povezani_zid_id"] = zid1_id
        
    else:
        # Stvaramo novi fizički zid na temelju zid1
        fizicki_zid = model.create_physical_wall_from_wall(zid1)
        
        # Dodajemo obje prostorije kao povezane s ovim fizičkim zidom
        fizicki_zid.dodaj_povezanu_prostoriju(prostorija1_id, zid1_id)
        fizicki_zid.dodaj_povezanu_prostoriju(prostorija2_id, zid2_id)
        
        # Povezujemo zidove s fizičkim zidom
        zid1["fizicki_zid_id"] = fizicki_zid.id
        zid2["fizicki_zid_id"] = fizicki_zid.id
        
        # Ažuriramo tip zidova
        zid1["tip"] = "prema_prostoriji"
        zid2["tip"] = "prema_prostoriji"
        zid1["povezana_prostorija_id"] = prostorija2_id
        zid2["povezana_prostorija_id"] = prostorija1_id
        zid1["povezani_zid_id"] = zid2_id
        zid2["povezani_zid_id"] = zid1_id
        
        # Dodajemo fizički zid u model
        model.fizicki_zidovi[fizicki_zid.id] = fizicki_zid
    
    # Osiguravamo da zidovi dijele iste elemente
    if not isinstance(zid1.get("elementi"), dict):
        zid1["elementi"] = fizicki_zid.elementi
    if not isinstance(zid2.get("elementi"), dict):
        zid2["elementi"] = fizicki_zid.elementi
    
    # Spremamo promjene
    model._spremi_u_session_state()
    
    return True
