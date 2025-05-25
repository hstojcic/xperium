"""
Modul za izračun transmisijskih toplinskih gubitaka.
"""

def izracun_transmisijskih_gubitaka(prostorija, temperature_dict, katalog=None):
    """
    Izračunava transmisijske toplinske gubitke za prostoriju.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    temperature_dict : dict
        Rječnik s temperaturama (vanjska, susjednih negrijanih prostora, itd.)
    katalog : dict
        Katalog s definiranim tipovima zidova, podova, stropova, prozora i vrata
        
    Returns:
    --------
    dict
        Rječnik s izračunatim gubicima po elementima i ukupno
    """
    gubici = {
        "zidovi": {},
        "prozori": 0.0,
        "vrata": 0.0,
        "pod": 0.0,
        "strop": 0.0,
        "toplinski_mostovi": 0.0,
        "ukupno": 0.0
    }
    
    # Temperatura u prostoriji
    temp_unutarnja = prostorija.temp_unutarnja
    
    # Gubici kroz zidove
    ukupni_gubici_zidova = 0
    ukupni_gubici_prozora = 0
    ukupni_gubici_vrata = 0
    
    # Inicijalizacija za praćenje ukupnih površina i U-vrijednosti
    ukupna_povrsina_prozora = 0
    ukupna_u_vrijednost_prozora = 0
    broj_prozora = 0
    ukupna_povrsina_vrata = 0
    ukupna_u_vrijednost_vrata = 0
    broj_vrata = 0
    
    # Popis svih prozora i vrata iz svih zidova - za detaljno praćenje
    svi_prozori = []
    sva_vrata = []
    
    # Kreiramo dict za informacije o zidovima ako ga nema
    if "zidovi_info" not in prostorija.__dict__:
        prostorija.zidovi_info = {}
    
    for zid in prostorija.zidovi:
        rezultat_zida = izracun_gubitaka_kroz_zid(zid, temp_unutarnja, temperature_dict, katalog)
        
        # Ako je rezultat_zida broj (stara implementacija), pretvaramo ga u rječnik za kompatibilnost
        if isinstance(rezultat_zida, (int, float)):
            gubici_zida = rezultat_zida
            gubici_prozora_zida = 0
            gubici_vrata_zida = 0
        else:
            # Nova implementacija vraća rječnik s detaljnim podacima
            gubici_zida = rezultat_zida.get("zid", 0)
            gubici_prozora_zida = rezultat_zida.get("prozori", 0)
            gubici_vrata_zida = rezultat_zida.get("vrata", 0)
            
            # Prikupljamo dodatne informacije o prozorima i vratima
            if "prozori_detalji" in rezultat_zida:
                prozori_detalji = rezultat_zida["prozori_detalji"]
                broj_prozora += prozori_detalji["broj"]
                
                # Dodajemo površinu prozora u ukupnu površinu
                povrsina_prozora_zida = prozori_detalji["ukupna_povrsina"]
                ukupna_povrsina_prozora += povrsina_prozora_zida
                
                # Ako postoje prozori u ovom zidu, dodajemo njihovu prosječnu U-vrijednost
                if prozori_detalji["broj"] > 0:
                    ukupna_u_vrijednost_prozora += prozori_detalji["prosjecna_u_vrijednost"] * prozori_detalji["broj"]
                
                # Dodajemo sve prozore iz ovog zida u ukupnu listu
                if "elementi" in prozori_detalji:
                    svi_prozori.extend(prozori_detalji["elementi"])
            
            if "vrata_detalji" in rezultat_zida:
                vrata_detalji = rezultat_zida["vrata_detalji"]
                broj_vrata += vrata_detalji["broj"]
                
                # Dodajemo površinu vrata u ukupnu površinu
                povrsina_vrata_zida = vrata_detalji["ukupna_povrsina"]
                ukupna_povrsina_vrata += povrsina_vrata_zida
                
                # Ako postoje vrata u ovom zidu, dodajemo njihovu prosječnu U-vrijednost
                if vrata_detalji["broj"] > 0:
                    ukupna_u_vrijednost_vrata += vrata_detalji["prosjecna_u_vrijednost"] * vrata_detalji["broj"]
                
                # Dodajemo sva vrata iz ovog zida u ukupnu listu
                if "elementi" in vrata_detalji:
                    sva_vrata.extend(vrata_detalji["elementi"])
        
        # Spremamo gubitke zida
        gubici["zidovi"][zid.get("id")] = gubici_zida
        
        # Spremamo informacije o tipu zida za kasnije korištenje u UI-u
        zid_id = zid.get("id")
        if zid_id:
            tip_zida = zid.get("tip", "vanjski")  # Default "vanjski" ako tip nije definiran
            duzina = zid.get("duzina", 0.0)
            visina = zid.get("visina")
            if visina is None and hasattr(prostorija, 'visina'):
                visina = prostorija.visina
            elif visina is None:
                visina = 2.5  # Default visina
            
            # Izračun površine zida
            povrsina_zida = duzina * visina
            
            # Dohvat U-vrijednosti
            u_vrijednost = 0.25  # Default
            if katalog:
                tip_zida_id = zid.get("tip_zida_id")
                if tip_zida_id and tip_zida_id in katalog.get("zidovi", {}):
                    u_vrijednost = katalog["zidovi"][tip_zida_id].u_vrijednost
            
            # Spremanje podataka o zidu s dodatnim informacijama
            prostorija.zidovi_info[zid_id] = {
                "tip": tip_zida,
                "povrsina": povrsina_zida,
                "u_vrijednost": u_vrijednost,
                "orijentacija": zid.get("orijentacija"),
                "povezana_prostorija_id": zid.get("povezana_prostorija_id"),
                "povezani_zid_id": zid.get("povezani_zid_id"),
                "fizicki_zid_id": zid.get("fizicki_zid_id", None),
                "duzina": duzina,
                "visina": visina
            }
        
        # Zbrajamo gubitke prozora i vrata za ukupan iznos
        if gubici_prozora_zida > 0:
            ukupni_gubici_prozora += gubici_prozora_zida
        
        if gubici_vrata_zida > 0:
            ukupni_gubici_vrata += gubici_vrata_zida
        
        # Za ukupne gubitke zidova, uzimamo samo pozitivne vrijednosti
        if gubici_zida > 0:
            ukupni_gubici_zidova += gubici_zida
      
    # Spremamo ukupne gubitke prozora i vrata
    gubici["prozori"] = ukupni_gubici_prozora
    gubici["vrata"] = ukupni_gubici_vrata
    
    # Izračun prosječne U-vrijednosti prozora i vrata
    prosjecna_u_prozori = ukupna_u_vrijednost_prozora / broj_prozora if broj_prozora > 0 else 1.4
    prosjecna_u_vrata = ukupna_u_vrijednost_vrata / broj_vrata if broj_vrata > 0 else 1.8
    
    # Dodajemo informacije o prozorima i vratima
    if not hasattr(prostorija, 'prozori_info'):
        prostorija.prozori_info = {}
    if not hasattr(prostorija, 'vrata_info'):
        prostorija.vrata_info = {}
    
    # Spremanje podataka o prozorima i vratima
    prostorija.prozori_info = {
        "ukupna_povrsina": ukupna_povrsina_prozora,
        "u_vrijednost": prosjecna_u_prozori,
        "broj_prozora": broj_prozora,
        "detalji": svi_prozori
    }
    
    prostorija.vrata_info = {
        "ukupna_povrsina": ukupna_povrsina_vrata,
        "u_vrijednost": prosjecna_u_vrata,
        "broj_vrata": broj_vrata,
        "detalji": sva_vrata
    }
    
    # Also add this information directly to the transmisijski result dict 
    # so it can be easily picked up by the results processing function
    gubici["prozori_info"] = {
        "ukupna_povrsina": ukupna_povrsina_prozora,
        "u_vrijednost": prosjecna_u_prozori,
        "broj_prozora": broj_prozora,
        "detalji": svi_prozori
    }
    
    gubici["vrata_info"] = {
        "ukupna_povrsina": ukupna_povrsina_vrata,
        "u_vrijednost": prosjecna_u_vrata,
        "broj_vrata": broj_vrata,
        "detalji": sva_vrata
    }
            
    # Dodajemo gubitke zidova u ukupne gubitke
    gubici["ukupno"] += ukupni_gubici_zidova + ukupni_gubici_prozora + ukupni_gubici_vrata
    
    # Gubici kroz pod
    gubici_poda = izracun_gubitaka_kroz_pod(prostorija, temp_unutarnja, temperature_dict, katalog)
    gubici["pod"] = gubici_poda
    gubici["ukupno"] += gubici_poda
    
    # Gubici kroz strop
    gubici_stropa = izracun_gubitaka_kroz_strop(prostorija, temp_unutarnja, temperature_dict, katalog)
    gubici["strop"] = gubici_stropa
    gubici["ukupno"] += gubici_stropa
    
    # Izračunaj sumu osnovnih transmisijskih gubitaka (bez toplinskih mostova)
    osnovni_transmisijski_gubici = gubici["ukupno"]
    
    # Toplinski mostovi - pojednostavljena procjena
    gubici_toplinskih_mostova = procjena_gubitaka_kroz_toplinske_mostove(prostorija, osnovni_transmisijski_gubici)
    gubici["toplinski_mostovi"] = gubici_toplinskih_mostova
    gubici["ukupno"] += gubici_toplinskih_mostova
    
    return gubici

def izracun_gubitaka_kroz_zid(zid, temp_unutarnja, temperature_dict, katalog=None):
    """
    Izračunava transmisijske toplinske gubitke kroz zid.
    
    Parameters:
    -----------
    zid : dict
        Rječnik koji predstavlja zid
    temp_unutarnja : float
        Temperatura u prostoriji
    temperature_dict : dict
        Rječnik s temperaturama (vanjska, susjednih negrijanih prostora, itd.)
    katalog : dict
        Katalog s definiranim tipovima zidova
        
    Returns:
    --------
    float
        Gubici kroz zid u W
    """
    import streamlit as st
    
    tip_zida = zid.get("tip")
    duzina = zid.get("duzina", 0.0)
    visina = zid.get("visina", 0.0)
    povrsina_ukupna = duzina * visina
      # Određivanje temperature s druge strane zida
    temp_druga_strana = None
    
    if tip_zida == "vanjski":
        temp_druga_strana = temperature_dict.get("vanjska", -20.0)
    elif tip_zida == "prema_negrijanom":
        temp_druga_strana = temperature_dict.get("negrijanom", 10.0)
    elif tip_zida == "prema_tlu":
        temp_druga_strana = temperature_dict.get("tlo", 10.0)
    elif tip_zida == "prema_prostoriji":
        # Ako je zid povezan s drugom prostorijom, koristimo temp te prostorije
        povezana_prostorija_id = zid.get("povezana_prostorija_id")
        if povezana_prostorija_id:
            # Ako imamo sesiju s temperaturama, pokušavamo dohvatiti
            if "temperature_prostorija" in st.session_state:
                temp_druga_strana = st.session_state["temperature_prostorija"].get(
                    povezana_prostorija_id, 20.0  # Default temperatura ako nema podatka
                )
            else:
                # Default za sobu
                temp_druga_strana = 20.0
        else:
            # Nema povezane prostorije - možda pogrešna konfiguracija?
            # Pretpostavljamo neku razumnu temperaturu
            temp_druga_strana = 20.0
            
        # Ako je temperatura ista kao u trenutnoj prostoriji, nema protoka topline
        if abs(temp_unutarnja - temp_druga_strana) < 0.1:
            return 0.0
    else:
        # Nepoznat tip zida
        return 0.0
    
    delta_t = temp_unutarnja - temp_druga_strana
    
    # Izračun površina prozora i vrata
    elementi = zid.get("elementi", {})
    prozori = elementi.get("prozori", [])
    vrata = elementi.get("vrata", [])
      # Izračun površina prozora i vrata s provjerom None vrijednosti
    povrsina_prozora = 0
    prozori_detalji = []
    for p in prozori:
        # Inicijalizacija površine za ovaj prozor
        prozor_povrsina = 0
        prozor_tip_id = None
        prozor_u_vrijednost = 1.4  # Default U-vrijednost
        
        # Ako prozor koristi standardne dimenzije iz kataloga
        if p.get("koristiti_standardne_dimenzije", True):
            tip_id = p.get("tip_id")
            prozor_tip_id = tip_id  # Čuvamo ID tipa za kasnije
            
            if katalog and tip_id in katalog.get("prozori", {}):
                prozor_tip = katalog["prozori"][tip_id]
                
                # Čuvamo U-vrijednost iz kataloga ako postoji
                if hasattr(prozor_tip, "u_vrijednost") and prozor_tip.u_vrijednost is not None and prozor_tip.u_vrijednost > 0:
                    prozor_u_vrijednost = prozor_tip.u_vrijednost
                
                # Koristimo površinu iz kataloga ako je definirana
                if hasattr(prozor_tip, "povrsina") and prozor_tip.povrsina is not None and prozor_tip.povrsina > 0:
                    prozor_povrsina = prozor_tip.povrsina
                # Ili računamo iz širine i visine ako su definirane
                elif hasattr(prozor_tip, "sirina") and hasattr(prozor_tip, "visina") and prozor_tip.sirina is not None and prozor_tip.visina is not None and prozor_tip.sirina > 0 and prozor_tip.visina > 0:
                    prozor_povrsina = prozor_tip.sirina * prozor_tip.visina
                else:
                    # Default dimenzije ako nema u katalogu ili su dimension nevaljane
                    prozor_povrsina = 1.2 * 1.2  # Standardni prozor 1.2m × 1.2m
        else:
            # Ako prozor ima vlastite dimenzije
            sirina = p.get("sirina", 0)
            visina = p.get("visina", 0)
            # Osiguraj da su vrijednosti brojevi, a ne None
            sirina = 1.2 if sirina is None or sirina <= 0 else float(sirina)
            visina = 1.2 if visina is None or visina <= 0 else float(visina)
            prozor_povrsina = sirina * visina
        
        # Dodajemo površinu prozora u ukupnu površinu
        povrsina_prozora += prozor_povrsina
        
        # Dodajemo detalje o ovom prozoru u listu
        prozori_detalji.append({
            "tip_id": prozor_tip_id,
            "povrsina": prozor_povrsina,
            "u_vrijednost": prozor_u_vrijednost
        })
    
    povrsina_vrata = 0
    vrata_detalji = []
    for v in vrata:
        # Inicijalizacija površine za ova vrata
        vrata_povrsina = 0
        vrata_tip_id = None
        vrata_u_vrijednost = 1.8  # Default U-vrijednost
        
        # Ako vrata koriste standardne dimenzije iz kataloga
        if v.get("koristiti_standardne_dimenzije", True):
            tip_id = v.get("tip_id")
            vrata_tip_id = tip_id  # Čuvamo ID tipa za kasnije
            
            if katalog and tip_id in katalog.get("vrata", {}):
                vrata_tip = katalog["vrata"][tip_id]
                
                # Čuvamo U-vrijednost iz kataloga ako postoji
                if hasattr(vrata_tip, "u_vrijednost") and vrata_tip.u_vrijednost is not None and vrata_tip.u_vrijednost > 0:
                    vrata_u_vrijednost = vrata_tip.u_vrijednost
                
                # Koristimo površinu iz kataloga ako je definirana
                if hasattr(vrata_tip, "povrsina") and vrata_tip.povrsina is not None and vrata_tip.povrsina > 0:
                    vrata_povrsina = vrata_tip.povrsina
                # Ili računamo iz širine i visine ako su definirane
                elif hasattr(vrata_tip, "sirina") and hasattr(vrata_tip, "visina") and vrata_tip.sirina is not None and vrata_tip.visina is not None and vrata_tip.sirina > 0 and vrata_tip.visina > 0:
                    vrata_povrsina = vrata_tip.sirina * vrata_tip.visina
                # Treći pokušaj - podrška za stariji naziv "sirna" umjesto "sirina"
                elif hasattr(vrata_tip, "sirna") and hasattr(vrata_tip, "visina") and vrata_tip.sirna is not None and vrata_tip.visina is not None and vrata_tip.sirna > 0 and vrata_tip.visina > 0:
                    vrata_povrsina = vrata_tip.sirna * vrata_tip.visina
                else:
                    # Default dimenzije ako nema u katalogu
                    vrata_povrsina = 0.9 * 2.05  # Standardna vrata 0.9m × 2.05m
        else:
            # Ako vrata imaju vlastite dimenzije
            sirina = v.get("sirina", 0)
            visina = v.get("visina", 0)
            # Osiguraj da su vrijednosti brojevi, a ne None
            sirina = 0.9 if sirina is None or sirina <= 0 else float(sirina)
            visina = 2.05 if visina is None or visina <= 0 else float(visina)
            vrata_povrsina = sirina * visina
        
        # Dodajemo površinu vrata u ukupnu površinu
        povrsina_vrata += vrata_povrsina
        
        # Dodajemo detalje o ovim vratima u listu
        vrata_detalji.append({
            "tip_id": vrata_tip_id,
            "povrsina": vrata_povrsina,
            "u_vrijednost": vrata_u_vrijednost
        })
    
    # Preostala površina zida
    povrsina_zida = povrsina_ukupna - povrsina_prozora - povrsina_vrata
    if povrsina_zida < 0:
        povrsina_zida = 0  # Zaštita od negativne površine
    
    # Dohvat U-vrijednosti iz kataloga
    u_vrijednost_zida = 0.25  # Defaultna vrijednost ako katalog nije dostupan
    u_vrijednost_prozora = 1.4
    u_vrijednost_vrata = 1.8
    
    # Ako imamo katalog, koristimo vrijednosti iz njega
    if katalog:
        # Dohvaćamo stvarni tip zida i njegove karakteristike
        tip_zida_id = zid.get("tip_zida_id")
        if tip_zida_id and tip_zida_id in katalog.get("zidovi", {}):
            u_vrijednost_zida = katalog["zidovi"][tip_zida_id].u_vrijednost
        
        # Računamo prosječnu U-vrijednost za prozore i vrata ako imamo više elemenata
        if prozori_detalji:
            ukupna_u_prozori = sum(p["u_vrijednost"] for p in prozori_detalji)
            u_vrijednost_prozora = ukupna_u_prozori / len(prozori_detalji) if len(prozori_detalji) > 0 else 1.4
        
        if vrata_detalji:
            ukupna_u_vrata = sum(v["u_vrijednost"] for v in vrata_detalji)
            u_vrijednost_vrata = ukupna_u_vrata / len(vrata_detalji) if len(vrata_detalji) > 0 else 1.8
    # Izračun gubitaka kroz zid, prozore i vrata
    gubici_zida = povrsina_zida * u_vrijednost_zida * delta_t
    gubici_prozora = povrsina_prozora * u_vrijednost_prozora * delta_t
    gubici_vrata = povrsina_vrata * u_vrijednost_vrata * delta_t
    
    # Ukupni gubici
    gubici_ukupno = gubici_zida + gubici_prozora + gubici_vrata
    
    # Stvaranje detaljnijeg objekta s rezultatima po elementima
    # Ovo omogućuje praćenje udjela prozora i vrata u transmisijskim gubicima
    rezultat = {
        "zid": gubici_zida,
        "prozori": gubici_prozora,
        "vrata": gubici_vrata,
        "ukupno": gubici_ukupno,
        # Dodajemo detalje o prozorima i vratima
        "prozori_detalji": {
            "broj": len(prozori_detalji),
            "ukupna_povrsina": povrsina_prozora, 
            "prosjecna_u_vrijednost": u_vrijednost_prozora,
            "elementi": prozori_detalji
        },
        "vrata_detalji": {
            "broj": len(vrata_detalji),
            "ukupna_povrsina": povrsina_vrata,
            "prosjecna_u_vrijednost": u_vrijednost_vrata,
            "elementi": vrata_detalji
        }
    }
    
    # Za zidove između prostorija, omogućujemo i negativne vrijednosti
    # koje predstavljaju toplinski dobitak (kad je druga prostorija toplija)
    # To omogućuje preciznije praćenje svih tokova topline u zgradi
    return rezultat

def izracun_gubitaka_kroz_pod(prostorija, temp_unutarnja, temperature_dict, katalog=None):
    """
    Izračunava transmisijske toplinske gubitke kroz pod.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    temp_unutarnja : float
        Temperatura u prostoriji
    temperature_dict : dict
        Rječnik s temperaturama (vanjska, susjednih negrijanih prostora, itd.)
    katalog : dict
        Katalog s definiranim tipovima podova
        
    Returns:
    --------
    float
        Gubici kroz pod u W
    """
    povrsina = prostorija.povrsina
    pod_tip = prostorija.pod_tip
      # Određivanje temperature s druge strane poda
    temp_druga_strana = None
    
    if pod_tip == "Prema tlu":
        temp_druga_strana = temperature_dict.get("tlo", 10.0)
    elif pod_tip == "Prema negrijanom prostoru":
        temp_druga_strana = temperature_dict.get("negrijanom", 10.0)
    elif pod_tip == "Prema vanjskom prostoru":
        temp_druga_strana = temperature_dict.get("vanjska", -20.0)
    elif pod_tip == "Prema grijanom prostoru":
        # Pretpostavljamo da nema gubitaka između grijanih prostora s istom temperaturom
        # Ovo bi trebalo dorađivati s točnim temperaturama grijanih prostora
        return 0.0
    else:
        # Nepoznat tip poda
        return 0.0
    
    delta_t = temp_unutarnja - temp_druga_strana
    
    # Dohvat U-vrijednosti iz kataloga
    u_vrijednost = 0.35  # W/(m²·K) - zadana vrijednost ako nema kataloga ili specifičnog tipa
    
    # Ako imamo katalog, koristimo vrijednosti iz njega
    pod_tip_id = getattr(prostorija, 'pod_tip_id', None)  # Sigurni pristup atributu
    if katalog and pod_tip_id:
        if pod_tip_id in katalog.get("podovi", {}):
            u_vrijednost = katalog["podovi"][pod_tip_id].u_vrijednost
    
    return povrsina * u_vrijednost * delta_t

def izracun_gubitaka_kroz_strop(prostorija, temp_unutarnja, temperature_dict, katalog=None):
    """
    Izračunava transmisijske toplinske gubitke kroz strop.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    temp_unutarnja : float
        Temperatura u prostoriji
    temperature_dict : dict
        Rječnik s temperaturama (vanjska, susjednih negrijanih prostora, itd.)
    katalog : dict
        Katalog s definiranim tipovima stropova
        
    Returns:
    --------
    float
        Gubici kroz strop u W
    """
    povrsina = prostorija.povrsina
    strop_tip = prostorija.strop_tip
    strop_tip_id = getattr(prostorija, 'strop_tip_id', None)  # ID tipa stropa iz kataloga
    
    # Određivanje temperature s druge strane stropa
    temp_druga_strana = None
    
    if strop_tip == "Prema tavanu":
        temp_druga_strana = temperature_dict.get("tavan", 5.0)
    elif strop_tip == "Prema negrijanom prostoru":
        temp_druga_strana = temperature_dict.get("negrijanom", 10.0)
    elif strop_tip == "Prema vanjskom prostoru":
        temp_druga_strana = temperature_dict.get("vanjska", -20.0)
    elif strop_tip == "Prema grijanom prostoru":
        # Ako je već grijano, nema ili su minimalni gubici
        # Ovo bi trebalo unaprijediti s točnim temperaturama grijanih prostora
        return 0.0
    elif strop_tip == "Ravni krov":
        temp_druga_strana = temperature_dict.get("vanjska", -20.0)
    else:
        # Nepoznat tip stropa
        return 0.0
    
    delta_t = temp_unutarnja - temp_druga_strana
    
    # Dohvat U-vrijednosti iz kataloga
    u_vrijednost = 0.20  # W/(m²·K) - zadana vrijednost ako nema kataloga ili specifičnog tipa
    
    # Ako imamo katalog, koristimo vrijednosti iz njega
    if katalog and strop_tip_id:
        if strop_tip_id in katalog.get("stropovi", {}):
            u_vrijednost = katalog["stropovi"][strop_tip_id].u_vrijednost
    
    return povrsina * u_vrijednost * delta_t

def procjena_gubitaka_kroz_toplinske_mostove(prostorija, osnovni_transmisijski_gubici):
    """
    Procjenjuje toplinske gubitke kroz toplinske mostove.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    osnovni_transmisijski_gubici : float
        Ukupni osnovni transmisijski gubici bez toplinskih mostova
        
    Returns:
    --------
    float
        Procijenjeni gubici kroz toplinske mostove u W
    """
    import streamlit as st
    
    # Dohvat postavki za toplinske mostove iz session state
    toplinski_mostovi_ukljuceni = st.session_state.get("toplinski_mostovi", True)
    postotak_toplinskih_mostova = st.session_state.get("postotak_toplinskih_mostova", 15)
    
    # Ako su toplinski mostovi isključeni, vraćamo 0
    if not toplinski_mostovi_ukljuceni:
        return 0.0
    
    # Izračun postotka od osnovnih transmisijskih gubitaka
    return osnovni_transmisijski_gubici * (postotak_toplinskih_mostova / 100.0)
