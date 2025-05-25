"""
Modul za izračun ventilacijskih toplinskih gubitaka.
"""

def izracun_ventilacijskih_gubitaka(prostorija, temperatura_vanjska):
    """
    Izračunava ventilacijske toplinske gubitke za prostoriju.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    temperatura_vanjska : float
        Vanjska projektna temperatura
        
    Returns:
    --------
    dict
        Rječnik s izračunatim ventilacijskim gubicima i detaljima
    """
    # Konstante
    RHO = 1.2      # kg/m³ - gustoća zraka
    CP = 1005      # J/(kg·K) - specifični toplinski kapacitet zraka
    
    # Podaci prostorije
    povrsina = prostorija.povrsina
    etaza = None
    if prostorija.model_ref:
        etaza = prostorija.model_ref.dohvati_etazu(prostorija.etaza_id)
    visina = prostorija.get_actual_height(etaza) if etaza else 2.8
    
    volumen = povrsina * visina  # m³
    
    # Ventilacijski parametri
    izmjene_zraka = prostorija.izmjene_zraka  # h⁻¹
    
    # Temperatura
    temp_unutarnja = prostorija.temp_unutarnja
    delta_t = temp_unutarnja - temperatura_vanjska
    
    # Izračun
    protok_zraka = (volumen * izmjene_zraka) / 3600  # m³/s
    snaga_gubitaka = RHO * CP * protok_zraka * delta_t  # W
    
    return {
        "protok_zraka": protok_zraka * 3600,  # m³/h
        "volumen": volumen,
        "izmjene_zraka": izmjene_zraka,
        "delta_t": delta_t,
        "snaga_gubitaka": snaga_gubitaka
    }

def izracun_infiltracije(prostorija, temperatura_vanjska, stupanj_zabrtvljenosti=1.0):
    """
    Izračunava toplinske gubitke zbog infiltracije zraka.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju gubici
    temperatura_vanjska : float
        Vanjska projektna temperatura
    stupanj_zabrtvljenosti : float
        Koeficijent koji predstavlja kvalitetu brtvljenja (0.5-1.5)
        
    Returns:
    --------
    dict
        Rječnik s izračunatim gubicima zbog infiltracije i detaljima
    """
    # Konstante
    RHO = 1.2      # kg/m³ - gustoća zraka
    CP = 1005      # J/(kg·K) - specifični toplinski kapacitet zraka
    
    # Podaci prostorije
    povrsina = prostorija.povrsina
    etaza = None
    if prostorija.model_ref:
        etaza = prostorija.model_ref.dohvati_etazu(prostorija.etaza_id)
    visina = prostorija.get_actual_height(etaza) if etaza else 2.8
    
    volumen = povrsina * visina  # m³
    
    # Izračun površine ovojnice
    povrsina_ovojnice = izracun_povrsine_ovojnice(prostorija)
    
    # Infiltracija
    # Pojednostavljeni model:
    # - bazira se na površini ovojnice prema vanjskom prostoru
    # - kvaliteta brtvljenja utječe na infiltraciju
    # - pretpostavka: 0.1-0.3 izmjena zraka po satu zbog infiltracije
    faktor_infiltracije = 0.2 * stupanj_zabrtvljenosti  # h⁻¹
    
    # Temperatura
    temp_unutarnja = prostorija.temp_unutarnja
    delta_t = temp_unutarnja - temperatura_vanjska
    
    # Izračun
    protok_zraka = (volumen * faktor_infiltracije) / 3600  # m³/s
    snaga_gubitaka = RHO * CP * protok_zraka * delta_t  # W
    
    return {
        "protok_zraka": protok_zraka * 3600,  # m³/h
        "volumen": volumen,
        "faktor_infiltracije": faktor_infiltracije,
        "delta_t": delta_t,
        "snaga_gubitaka": snaga_gubitaka
    }

def izracun_povrsine_ovojnice(prostorija):
    """
    Izračunava površinu ovojnice prostorije prema vanjskom prostoru.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računa površina ovojnice
        
    Returns:
    --------
    float
        Površina ovojnice u m²
    """
    povrsina_ovojnice = 0.0
    
    # Zbroji površine svih vanjskih zidova
    for zid in prostorija.zidovi:
        if zid.get("tip") == "vanjski":
            duzina = zid.get("duzina", 0.0)
            visina = zid.get("visina", 0.0)
            povrsina_ovojnice += duzina * visina
    
    # Dodaj površinu poda ako je prema vanjskom prostoru
    if prostorija.pod_tip == "Prema vanjskom prostoru":
        povrsina_ovojnice += prostorija.povrsina
    
    # Dodaj površinu stropa ako je prema vanjskom prostoru
    if prostorija.strop_tip == "Prema vanjskom prostoru":
        povrsina_ovojnice += prostorija.povrsina
    
    return povrsina_ovojnice
