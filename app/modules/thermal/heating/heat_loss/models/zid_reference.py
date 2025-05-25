"""
Modul koji sadrži funkcije za obnavljanje referenci između fizičkih zidova i zidova prostorija.
"""

def restore_wall_references(model):
    """
    Obnavlja reference između fizičkih zidova i zidova prostorija.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s prostorijama i fizičkim zidovima
        
    Returns:
    --------
    int
        Broj obnovljenih referenci
    """
    from .elementi.wall_elements import WallElements
    
    broj_obnovljenih = 0
    
    # Za svaki fizički zid, provjeri njegovu povezanost s prostorijama
    for fizicki_zid_id, fizicki_zid in model.fizicki_zidovi.items():
        for povezana in fizicki_zid.povezane_prostorije:
            prostorija_id = povezana["prostorija_id"]
            zid_referenca_id = povezana["zid_referenca_id"]
            
            # Dohvati prostoriju
            prostorija = model.dohvati_prostoriju(prostorija_id)
            if not prostorija:
                continue
                
            # Dohvati zid
            for zid in prostorija.zidovi:
                if zid.get("id") == zid_referenca_id:
                    # Ažuriraj referencu na fizički zid
                    if zid.get("fizicki_zid_id") != fizicki_zid_id:
                        zid["fizicki_zid_id"] = fizicki_zid_id
                        broj_obnovljenih += 1
                    
                    # Osiguraj da zid koristi elemente fizičkog zida
                    if not isinstance(zid.get("elementi"), WallElements):
                        zid["elementi"] = fizicki_zid.elementi
                        broj_obnovljenih += 1
                    elif zid["elementi"] is not fizicki_zid.elementi:
                        zid["elementi"] = fizicki_zid.elementi
                        broj_obnovljenih += 1
                    
                    break
    
    # Osiguraj da povezani zidovi imaju iste reference
    for prostorija in model.prostorije:
        for zid in prostorija.zidovi:
            povezana_prostorija_id = zid.get("povezana_prostorija_id")
            povezani_zid_id = zid.get("povezani_zid_id")
            
            if povezana_prostorija_id and povezani_zid_id:
                povezana_prostorija = model.dohvati_prostoriju(povezana_prostorija_id)
                if not povezana_prostorija:
                    continue
                    
                for povezani_zid in povezana_prostorija.zidovi:
                    if povezani_zid.get("id") == povezani_zid_id:
                        # Ako oba zida imaju fizički zid, trebali bi biti isti
                        fizicki_zid_id1 = zid.get("fizicki_zid_id")
                        fizicki_zid_id2 = povezani_zid.get("fizicki_zid_id")
                        
                        if fizicki_zid_id1 and fizicki_zid_id2 and fizicki_zid_id1 != fizicki_zid_id2:
                            # U slučaju konflikta, koristimo prvi fizički zid
                            povezani_zid["fizicki_zid_id"] = fizicki_zid_id1
                            if fizicki_zid_id1 in model.fizicki_zidovi:
                                model.fizicki_zidovi[fizicki_zid_id1].dodaj_povezanu_prostoriju(
                                    povezana_prostorija_id, povezani_zid_id
                                )
                            broj_obnovljenih += 1
                        
                        # Osiguraj da oba zida dijele iste elemente
                        if zid.get("elementi") is not povezani_zid.get("elementi"):
                            if isinstance(zid.get("elementi"), WallElements):
                                povezani_zid["elementi"] = zid["elementi"]
                                broj_obnovljenih += 1
                            elif isinstance(povezani_zid.get("elementi"), WallElements):
                                zid["elementi"] = povezani_zid["elementi"]
                                broj_obnovljenih += 1
                        
                        break
    
    # Spremamo promjene
    model._spremi_u_session_state()
    
    return broj_obnovljenih
