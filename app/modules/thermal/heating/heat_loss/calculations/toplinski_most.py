"""
Modul za izračun toplinskih gubitaka kroz toplinske mostove.
"""

def izracun_toplinskih_mostova_po_vrsti(prostorija, temperature_dict):
    """
    Izračunava toplinske gubitke kroz toplinske mostove za prostoriju, po vrsti mosta.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    temperature_dict : dict
        Rječnik s temperaturama (vanjska, susjednih negrijanih prostora, itd.)
        
    Returns:
    --------
    dict
        Rječnik s izračunatim gubicima po vrsti toplinskog mosta i ukupno
    """
    gubici = {
        "spojevi_zidova": 0.0,
        "spojevi_zid_pod": 0.0,
        "spojevi_zid_strop": 0.0,
        "otvori": 0.0,
        "ukupno": 0.0
    }
    
    # Temperatura u prostoriji
    temp_unutarnja = prostorija.temp_unutarnja
    
    # Dohvati vanjsku temperaturu
    temp_vanjska = temperature_dict.get("vanjska", -15.0)
    
    # Razlika temperatura
    delta_t = temp_unutarnja - temp_vanjska
    
    # Duljine toplinskih mostova
    duljina_spojeva_zidova = izracunaj_duljinu_spojeva_zidova(prostorija)
    duljina_spojeva_zid_pod = izracunaj_duljinu_spojeva_zid_pod(prostorija)
    duljina_spojeva_zid_strop = izracunaj_duljinu_spojeva_zid_strop(prostorija)
    duljina_otvora = izracunaj_duljinu_otvora(prostorija)
    
    # Linearni koeficijenti prolaska topline (W/mK) - pojednostavljeno
    psi_spojevi_zidova = 0.15  # W/mK
    psi_spojevi_zid_pod = 0.40  # W/mK
    psi_spojevi_zid_strop = 0.30  # W/mK
    psi_otvori = 0.25  # W/mK
    
    # Izračun gubitaka
    gubici["spojevi_zidova"] = duljina_spojeva_zidova * psi_spojevi_zidova * delta_t
    gubici["spojevi_zid_pod"] = duljina_spojeva_zid_pod * psi_spojevi_zid_pod * delta_t
    gubici["spojevi_zid_strop"] = duljina_spojeva_zid_strop * psi_spojevi_zid_strop * delta_t
    gubici["otvori"] = duljina_otvora * psi_otvori * delta_t
    
    # Ukupni gubici
    gubici["ukupno"] = (
        gubici["spojevi_zidova"] + 
        gubici["spojevi_zid_pod"] + 
        gubici["spojevi_zid_strop"] + 
        gubici["otvori"]
    )
    
    return gubici

def procjena_toplinskih_mostova_postotkom(prostorija, osnovni_transmisijski_gubici):
    """
    Procjenjuje toplinske gubitke kroz toplinske mostove kao postotak transmisijskih gubitaka.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    osnovni_transmisijski_gubici : float
        Osnovni transmisijski gubici prostorije bez toplinskih mostova (u W)
        
    Returns:
    --------
    float
        Procijenjeni gubici kroz toplinske mostove u W
    """
    import streamlit as st
    
    # Dohvat postavki za toplinske mostove iz session state ako postoje
    toplinski_mostovi_ukljuceni = st.session_state.get("toplinski_mostovi", True)
    postotak_toplinskih_mostova = st.session_state.get("postotak_toplinskih_mostova", 15)
    
    # Ako su toplinski mostovi isključeni, vraćamo 0
    if not toplinski_mostovi_ukljuceni:
        return 0.0
    
    # Izračun postotka od osnovnih transmisijskih gubitaka (samo prema vrijednosti iz slidera)
    return osnovni_transmisijski_gubici * (postotak_toplinskih_mostova / 100.0)

def izracunaj_duljinu_spojeva_zidova(prostorija):
    """
    Izračunava ukupnu duljinu spojeva vanjskih zidova.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računa duljina spojeva
        
    Returns:
    --------
    float
        Ukupna duljina spojeva vanjskih zidova u m
    """
    # Pojednostavljena implementacija
    # Prebroji sve vanjske zidove
    vanjski_zidovi = [z for z in prostorija.zidovi if z.get("tip") == "vanjski"]
    
    # Pretpostavka: svaki vanjski zid ima dva spoja s drugim zidovima
    # U stvarnosti, ovo bi trebalo preciznije računati
    return len(vanjski_zidovi) * 2 * prostorija.get_actual_height(None)

def izracunaj_duljinu_spojeva_zid_pod(prostorija):
    """
    Izračunava ukupnu duljinu spojeva vanjskih zidova s podom.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računa duljina spojeva
        
    Returns:
    --------
    float
        Ukupna duljina spojeva vanjskih zidova s podom u m
    """
    # Pojednostavljena implementacija
    # Zbroji duljine svih vanjskih zidova
    duljina = 0.0
    for zid in prostorija.zidovi:
        if zid.get("tip") == "vanjski":
            duljina += zid.get("duzina", 0.0)
            
    return duljina

def izracunaj_duljinu_spojeva_zid_strop(prostorija):
    """
    Izračunava ukupnu duljinu spojeva vanjskih zidova sa stropom.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računa duljina spojeva
        
    Returns:
    --------
    float
        Ukupna duljina spojeva vanjskih zidova sa stropom u m
    """
    # Pojednostavljena implementacija
    # U većini slučajeva jednako duljini spojeva zid-pod
    return izracunaj_duljinu_spojeva_zid_pod(prostorija)

def izracunaj_duljinu_otvora(prostorija):
    """
    Izračunava ukupnu duljinu spojeva otvora (prozora, vrata) s vanjskim zidovima.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računa duljina spojeva
        
    Returns:
    --------
    float
        Ukupna duljina spojeva otvora s vanjskim zidovima u m
    """
    # Pojednostavljena implementacija
    # Pretpostavke za jednostavniji izračun:
    # - Svaki prozor ima opseg ~6m (2×1,5m prozor)
    # - Svaka vrata imaju opseg ~6m (2×0,9m + 2×2,1m vrata)
    
    duljina = 0.0
    
    for zid in prostorija.zidovi:
        if zid.get("tip") == "vanjski":
            elementi = zid.get("elementi")
            if elementi:
                prozori_count = len(elementi.prozori) if hasattr(elementi, "prozori") else 0
                vrata_count = len(elementi.vrata) if hasattr(elementi, "vrata") else 0
                
                duljina += prozori_count * 6.0
                duljina += vrata_count * 6.0
                
    return duljina
