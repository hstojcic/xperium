"""
Modul koji sadrži funkcije za konverziju postojećih zidova u fizičke zidove.
"""

def konvertiraj_u_fizicke_zidove(model):
    """
    Konvertira sve postojeće zidove u sustav fizičkih zidova.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s prostorijama i zidovima
        
    Returns:
    --------
    int
        Broj konvertiranih zidova
    """
    from .elementi.fizicki_zid import FizickiZid
    from .elementi.wall_elements import WallElements
    
    # Preslikajmo što trebamo za referancu
    povezani_zidovi = {}  # {(prostorija_id, zid_id): (povezana_prostorija_id, povezani_zid_id), ...}
    
    # Prvo mapiramo povezane zidove
    for prostorija in model.prostorije:
        for zid in prostorija.zidovi:
            zid_id = zid.get("id")
            povezana_prostorija_id = zid.get("povezana_prostorija_id")
            povezani_zid_id = zid.get("povezani_zid_id")
            
            if povezana_prostorija_id and povezani_zid_id:
                key = (prostorija.id, zid_id)
                val = (povezana_prostorija_id, povezani_zid_id)
                povezani_zidovi[key] = val
    
    # Sada stvaramo fizičke zidove
    stvoreni_fizicki_zidovi = {}  # {(prostorija_id, zid_id): fizicki_zid_id, ...}
    broj_konvertiranih = 0
    
    for prostorija in model.prostorije:
        for zid in prostorija.zidovi:
            zid_id = zid.get("id")
            key = (prostorija.id, zid_id)
            
            # Ako već postoji fizički zid za ovaj zid, preskačemo
            if "fizicki_zid_id" in zid and zid["fizicki_zid_id"] in model.fizicki_zidovi:
                continue
                
            # Ako je zid već obrađen kroz povezani zid, preskačemo
            if key in stvoreni_fizicki_zidovi:
                continue
                
            # Provjeravamo je li ovaj zid povezan s drugim
            if key in povezani_zidovi:
                povezana_prostorija_id, povezani_zid_id = povezani_zidovi[key]
                povezani_key = (povezana_prostorija_id, povezani_zid_id)
                
                # Ako je povezani zid već obrađen, koristimo njegov fizički zid
                if povezani_key in stvoreni_fizicki_zidovi:
                    fizicki_zid_id = stvoreni_fizicki_zidovi[povezani_key]
                    zid["fizicki_zid_id"] = fizicki_zid_id
                    if fizicki_zid_id in model.fizicki_zidovi:
                        model.fizicki_zidovi[fizicki_zid_id].dodaj_povezanu_prostoriju(prostorija.id, zid_id)
                    continue
            
            # Stvaramo novi fizički zid
            elementi = zid.get("elementi")
            if not isinstance(elementi, WallElements):
                elementi = WallElements()
                
            segmenti = zid.get("segmenti", [])
                
            fizicki_zid = FizickiZid(
                tip=zid.get("tip", "vanjski"),
                orijentacija=zid.get("orijentacija"),
                duzina=float(zid.get("duzina", 5.0)),
                visina=float(zid.get("visina")) if zid.get("visina") is not None else None,
                je_segmentiran=zid.get("je_segmentiran", False),
                segmenti=segmenti,
                elementi=elementi
            )
                
            # Dodajemo prostoriju kao povezanu s fizičkim zidom
            fizicki_zid.dodaj_povezanu_prostoriju(prostorija.id, zid_id)
            
            # Dodajemo fizički zid u model
            model.fizicki_zidovi[fizicki_zid.id] = fizicki_zid
            
            # Ažuriramo zid u prostoriji da koristi fizički zid
            zid["fizicki_zid_id"] = fizicki_zid.id
            
            # Ako je ovaj zid povezan s drugim, dodajemo poveznicu
            if key in povezani_zidovi:
                povezana_prostorija_id, povezani_zid_id = povezani_zidovi[key]
                povezani_key = (povezana_prostorija_id, povezani_zid_id)
                
                # Dodajemo fizički zid za povezani zid
                stvoreni_fizicki_zidovi[povezani_key] = fizicki_zid.id
                
                # Dodajemo povezanu prostoriju na fizički zid
                fizicki_zid.dodaj_povezanu_prostoriju(povezana_prostorija_id, povezani_zid_id)
                
                # Pronađimo povezani zid i ažurirajmo ga
                povezana_prostorija = model.dohvati_prostoriju(povezana_prostorija_id)
                if povezana_prostorija:
                    for povezani_zid in povezana_prostorija.zidovi:
                        if povezani_zid.get("id") == povezani_zid_id:
                            povezani_zid["fizicki_zid_id"] = fizicki_zid.id
                            break
            
            # Pamtimo da smo obradili ovaj zid
            stvoreni_fizicki_zidovi[key] = fizicki_zid.id
            broj_konvertiranih += 1
    
    # Spremamo promjene
    model._spremi_u_session_state()
    
    return broj_konvertiranih
