"""
Proračun toplinskih gubitaka prema EN 12831
"""

import math
from .constants import ORIJENTACIJE, TEMP_FAKTORI

def izracunaj_toplinske_gubitke(duljina, sirina, visina, temp_unutarnja, temp_vanjska,
                               vanjski_zidovi, pod_tip, strop_tip, 
                               u_zid, u_prozor, u_vrata, u_pod, u_strop, 
                               izmjene_zraka, toplinski_mostovi=True, faktor_sigurnosti=10):
    """
    Izračunava toplinske gubitke za jednu prostoriju prema EN 12831
    
    Parameters:
    -----------
    duljina : float
        Duljina prostorije u metrima
    sirina : float
        Širina prostorije u metrima
    visina : float
        Visina prostorije u metrima
    temp_unutarnja : float
        Unutarnja projektna temperatura u °C
    temp_vanjska : float
        Vanjska projektna temperatura u °C
    vanjski_zidovi : list
        Lista zidova s atributima orijentacija, prozori, vrata
    pod_tip : str
        Tip poda (npr. "pod_na_tlu", "pod_prema_podrumu")
    strop_tip : str
        Tip stropa (npr. "ravan_krov", "prema_tavanu")
    u_zid : float
        Koeficijent prolaza topline zida u W/(m²·K)
    u_prozor : float
        Koeficijent prolaza topline prozora u W/(m²·K)
    u_vrata : float
        Koeficijent prolaza topline vrata u W/(m²·K)
    u_pod : float
        Koeficijent prolaza topline poda u W/(m²·K)
    u_strop : float
        Koeficijent prolaza topline stropa u W/(m²·K)
    izmjene_zraka : float
        Broj izmjena zraka u prostoriji po satu (h⁻¹)
    toplinski_mostovi : bool
        Uključiti toplinske mostove u proračun
    faktor_sigurnosti : float, optional
        Dodatni postotak za sigurnost (default 10%)
        
    Returns:
    --------
    dict
        Rezultati izračuna toplinskih gubitaka
    """
    # 1. Osnovni podaci
    # Površina i volumen prostorije
    povrsina = duljina * sirina
    volumen = povrsina * visina
    
    # Razlika temperature (projektne temperature)
    delta_t = temp_unutarnja - temp_vanjska
    
    # 2. Transmisijski gubici
    # 2.1. Zidovi, prozori i vrata
    gubici_zidovi = 0
    gubici_prozori = 0
    gubici_vrata = 0
    
    for zid in vanjski_zidovi:
        orijentacija = zid.get("orijentacija", "sjever")
        duzina_zida = zid.get("duzina", 0)
        
        # Površina zida (bez prozora i vrata)
        povrsina_zida_bruto = duzina_zida * visina
        
        # Prozori
        prozori = zid.get("prozori", [])
        povrsina_prozora = sum(p.get("sirina", 0) * p.get("visina", 0) for p in prozori)
        
        # Vrata
        vrata = zid.get("vrata", [])
        povrsina_vrata = sum(v.get("sirina", 0) * v.get("visina", 0) for v in vrata)
        
        # Čista površina zida
        povrsina_zida_neto = povrsina_zida_bruto - povrsina_prozora - povrsina_vrata
        
        # Gubici kroz zid
        faktor_orijentacije = ORIJENTACIJE.get(orijentacija, 1.0)
        gubici_zidovi += povrsina_zida_neto * u_zid * delta_t * faktor_orijentacije
        
        # Gubici kroz prozore i vrata
        gubici_prozori += povrsina_prozora * u_prozor * delta_t * faktor_orijentacije
        gubici_vrata += povrsina_vrata * u_vrata * delta_t * faktor_orijentacije
    
    # 2.2. Pod 
    temp_faktor_pod = TEMP_FAKTORI.get(pod_tip, 1.0) # Faktor za različite tipove poda
    gubici_pod = povrsina * u_pod * delta_t * temp_faktor_pod
    
    # 2.3. Strop
    temp_faktor_strop = TEMP_FAKTORI.get(strop_tip, 1.0) # Faktor za različite tipove stropa
    gubici_strop = povrsina * u_strop * delta_t * temp_faktor_strop
      # Najprije izračunamo osnovne transmisijske gubitke (bez toplinskih mostova)
    osnovni_transmisijski_gubici = gubici_zidovi + gubici_prozori + gubici_vrata + gubici_pod + gubici_strop
    
    # 2.4. Toplinski mostovi
    gubici_toplinski_mostovi = 0
    
    if toplinski_mostovi:
        # Dodatak od 10% na osnovne transmisijske gubitke (bez toplinskih mostova)
        gubici_toplinski_mostovi = 0.1 * osnovni_transmisijski_gubici
    
    # Ukupni transmisijski gubici
    gubici_transmisijski = osnovni_transmisijski_gubici + gubici_toplinski_mostovi
    
    # 3. Ventilacijski gubici
    protok_zraka = volumen * izmjene_zraka
    gubici_ventilacijski = 0.34 * protok_zraka * delta_t
    
    # 4. Ukupni gubici
    ukupni_gubici_prije_dodatka = gubici_transmisijski + gubici_ventilacijski
    
    # 5. Faktor sigurnosti
    dodatak_sigurnosti = ukupni_gubici_prije_dodatka * (faktor_sigurnosti / 100)
    ukupni_gubici = ukupni_gubici_prije_dodatka + dodatak_sigurnosti
    
    # Specifični gubici W/m²
    specificni_gubici = ukupni_gubici / povrsina if povrsina > 0 else 0
    
    # Procjena godišnje energije za grijanje
    stupanj_dani = 2800  # Stupanj-dani grijanja (približno za kontinentalnu Hrvatsku)
    sati_grijanja = 4500  # Približan broj sati grijanja u sezoni
    potrebna_energija = (ukupni_gubici * sati_grijanja) / 1000  # kWh
    
    return {
        "povrsina": povrsina,
        "volumen": volumen,
        "gubici_zidovi": gubici_zidovi,
        "gubici_prozori": gubici_prozori,
        "gubici_vrata": gubici_vrata,
        "gubici_pod": gubici_pod,
        "gubici_strop": gubici_strop,
        "gubici_toplinski_mostovi": gubici_toplinski_mostovi,
        "gubici_transmisijski": gubici_transmisijski,
        "gubici_ventilacijski": gubici_ventilacijski,
        "ukupni_gubici": ukupni_gubici,
        "specificni_gubici": specificni_gubici,
        "stupanj_dani": stupanj_dani,
        "sati_grijanja": sati_grijanja,
        "potrebna_energija": potrebna_energija
    }

def izracunaj_toplinske_gubitke_vise_prostorija(model, temp_vanjska, u_values, faktor_sigurnosti=0.0, toplinski_mostovi_faktor=0.10):
    """
    Izračunava toplinske gubitke za više prostorija prema EN 12831
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s više prostorija
    temp_vanjska : float
        Vanjska projektna temperatura u °C
    u_values : dict
        Rječnik s U-vrijednostima
    faktor_sigurnosti : float, optional
        Dodatni postotak za sigurnost (default 0.0)
    toplinski_mostovi_faktor : float, optional
        Faktor za izračun toplinskih mostova (default 0.10, što odgovara 10%)
        
    Returns:
    --------
    dict
        Rezultati izračuna toplinskih gubitaka za sve prostorije    """
    # Rezultati za svaku prostoriju
    rezultati = {}
    
    # Osiguravamo da je toplinski_mostovi_faktor validan broj
    if toplinski_mostovi_faktor is None:
        toplinski_mostovi_faktor = 0.0
    
    # Sume za ukupne gubitke
    ukupni_gubici_svih_prostorija = 0
    ukupna_povrsina_svih_prostorija = 0
    for prostorija in model.prostorije:
        # Osnovni podaci za prostoriju
        prostorija_id = prostorija.id
        povrsina = prostorija.povrsina  # Koristimo postojeću površinu iz modela
        
        # Dohvaćamo visinu prostorije
        etaza = model.dohvati_etazu(prostorija.etaza_id)
        visina = prostorija.get_actual_height(etaza) if etaza else 2.8
        
        temp_unutarnja = prostorija.temp_unutarnja
        delta_t_vanjski = temp_unutarnja - temp_vanjska
        
        # Izračunavanje volumena
        volumen = povrsina * visina
        
        # Izračunavanje svih gubitaka za ovu prostoriju
        # 1. TRANSMISIJSKI GUBICI
        gubici_zidovi_cisti = 0
        gubici_prozori = 0
        gubici_vrata = 0
        gubici_spojni_zidovi = 0  # Gubici prema drugim prostorijama
        gubici_pod = 0
        gubici_strop = 0
        gubici_toplinski_mostovi = 0
        
        # Za praćenje detalja svakog zida
        detalji_zidova = []
        
        # Izračun za svaki zid
        for zid in prostorija.zidovi:
            # Izračun površine
            ukupna_povrsina_zida = zid["duzina"] * visina
            
            # Izračun površine prozora
            povrsina_prozora_na_zidu = 0
            for prozor in zid.get("prozori", []):
                sirina_prozora = prozor.get("sirina", 0)
                visina_prozora = prozor.get("visina", 0)
                povrsina_prozora_na_zidu += sirina_prozora * visina_prozora
            
            # Izračun površine vrata
            povrsina_vrata_na_zidu = 0
            for vrata in zid.get("vrata", []):
                sirina_vrata = vrata.get("sirina", 0)
                visina_vrata = vrata.get("visina", 0)
                povrsina_vrata_na_zidu += sirina_vrata * visina_vrata
            
            # Izračun čiste površine zida (oduzeti prozori i vrata)
            cista_povrsina_zida_iter = ukupna_povrsina_zida - povrsina_prozora_na_zidu - povrsina_vrata_na_zidu

            if zid["tip"] == "vanjski":
                delta_t_za_racun = delta_t_vanjski
                u_wall_val = u_values.get("Vanjski zid", 1.0) # Fallback U-value
                u_window_val = u_values.get("Prozor", 1.5)
                u_door_val = u_values.get("Vrata", 2.0)
                faktor_orijentacije = ORIJENTACIJE.get(zid.get("orijentacija"), 1.0)

                gubitak_cistog_zida = cista_povrsina_zida_iter * u_wall_val * delta_t_za_racun * faktor_orijentacije
                gubitak_prozora = povrsina_prozora_na_zidu * u_window_val * delta_t_za_racun * faktor_orijentacije
                gubitak_vrata = povrsina_vrata_na_zidu * u_door_val * delta_t_za_racun * faktor_orijentacije

                gubici_zidovi_cisti += gubitak_cistog_zida
                gubici_prozori += gubitak_prozora
                gubici_vrata += gubitak_vrata
                # Sigurna provjera za množenje s toplinski_mostovi_faktor
                if toplinski_mostovi_faktor:
                    gubici_toplinski_mostovi += (gubitak_cistog_zida + gubitak_prozora + gubitak_vrata) * toplinski_mostovi_faktor

                detalji_zidova.append({
                    "id": zid.get("id"),
                    "orijentacija": zid.get("orijentacija"),
                    "tip": "vanjski",
                    "duzina": zid["duzina"],
                    "ukupna_povrsina": ukupna_povrsina_zida,
                    "cista_povrsina": cista_povrsina_zida_iter,
                    "povrsina_prozora": povrsina_prozora_na_zidu,
                    "povrsina_vrata": povrsina_vrata_na_zidu,
                    "gubitak_zid": gubitak_cistog_zida,
                    "gubitak_prozor": gubitak_prozora,
                    "gubitak_vrata": gubitak_vrata,
                    "ukupni_gubitak_elementa": gubitak_cistog_zida + gubitak_prozora + gubitak_vrata
                })

            elif zid["tip"] == "prema_negrijanom":
                temp_susjednog_negrijanog = prostorija.temperatura_susjednog_negrijanog
                delta_t_za_racun = temp_unutarnja - temp_susjednog_negrijanog

                if delta_t_za_racun > 0:
                    u_wall_val = u_values.get("Zid prema negrijanom", u_values.get("Vanjski zid", 1.0))
                    u_window_val = u_values.get("Prozor prema negrijanom", u_values.get("Prozor", 1.5))
                    u_door_val = u_values.get("Vrata prema negrijanom", u_values.get("Vrata", 2.0))
                    faktor_orijentacije = 1.0 # Nema orijentacije za unutarnje zidove

                    gubitak_cistog_zida = cista_povrsina_zida_iter * u_wall_val * delta_t_za_racun * faktor_orijentacije
                    gubitak_prozora = povrsina_prozora_na_zidu * u_window_val * delta_t_za_racun * faktor_orijentacije
                    gubitak_vrata = povrsina_vrata_na_zidu * u_door_val * delta_t_za_racun * faktor_orijentacije

                    gubici_zidovi_cisti += gubitak_cistog_zida
                    gubici_prozori += gubitak_prozora
                    gubici_vrata += gubitak_vrata
                    gubici_toplinski_mostovi += (gubitak_cistog_zida + gubitak_prozora + gubitak_vrata) * toplinski_mostovi_faktor
                    
                    detalji_zidova.append({
                        "id": zid.get("id"),
                        "orijentacija": None,
                        "tip": "prema_negrijanom",
                        "duzina": zid["duzina"],
                        "delta_t_negrijano": delta_t_za_racun,
                        "ukupna_povrsina": ukupna_povrsina_zida,
                        "cista_povrsina": cista_povrsina_zida_iter,
                        "povrsina_prozora": povrsina_prozora_na_zidu,
                        "povrsina_vrata": povrsina_vrata_na_zidu,
                        "gubitak_zid": gubitak_cistog_zida,
                        "gubitak_prozor": gubitak_prozora,
                        "gubitak_vrata": gubitak_vrata,
                        "ukupni_gubitak_elementa": gubitak_cistog_zida + gubitak_prozora + gubitak_vrata
                    })
                else:
                     detalji_zidova.append({
                        "id": zid.get("id"),
                        "orijentacija": None,
                        "tip": "prema_negrijanom",
                        "duzina": zid["duzina"],
                        "delta_t_negrijano": delta_t_za_racun,
                        "ukupna_povrsina": ukupna_povrsina_zida,
                        "cista_povrsina": cista_povrsina_zida_iter,
                        "povrsina_prozora": povrsina_prozora_na_zidu,
                        "povrsina_vrata": povrsina_vrata_na_zidu,
                        "gubitak_zid": 0,
                        "gubitak_prozor": 0,
                        "gubitak_vrata": 0,
                        "ukupni_gubitak_elementa": 0
                    })

            elif zid["tip"] == "prema_prostoriji":
                # Ovaj zid prenosi toplinu prema jednoj drugoj GRIJANOJ prostoriji
                gubitak_cistog_zida_unutarnji = 0
                gubitak_prozora_unutarnji = 0
                gubitak_vrata_unutarnji = 0
                ukupni_gubitak_ovog_elementa = 0

                povezana_prostorija_id = zid.get("povezana_prostorija_id")
                detalji_za_ovaj_zid = {
                    "id": zid.get("id"),
                    "orijentacija": None,
                    "tip": "prema_prostoriji",
                    "duzina": zid["duzina"],
                    "ukupna_povrsina": ukupna_povrsina_zida, # Bruto površina za informaciju
                    "cista_povrsina": cista_povrsina_zida_iter, # Neto površina zida
                    "povrsina_prozora": povrsina_prozora_na_zidu, # Površina prozora na ovom zidu
                    "povrsina_vrata": povrsina_vrata_na_zidu, # Površina vrata na ovom zidu
                    "povezana_prostorija_naziv": None,
                    "delta_t_prostorije": 0,
                    "gubitak_zid": 0,
                    "gubitak_prozor": 0,
                    "gubitak_vrata": 0,
                    "ukupni_gubitak_elementa": 0
                }

                # Ako je zid povezan s drugom prostorijom
                if povezana_prostorija_id:
                    povezana_prostorija = model.dohvati_prostoriju(povezana_prostorija_id)
                    if povezana_prostorija:
                        detalji_za_ovaj_zid["povezana_prostorija_naziv"] = povezana_prostorija.naziv

                        # Razlika u temperaturi između dviju prostorija
                        temp_povezane = povezana_prostorija.temp_unutarnja
                        delta_t_prostorije = temp_unutarnja - temp_povezane
                        detalji_za_ovaj_zid["delta_t_prostorije"] = delta_t_prostorije

                        # Samo ako je delta_t pozitivna (naša prostorija je toplija)
                        if delta_t_prostorije > 0:
                            u_wall_val = u_values.get("Unutarnji zid", 1.0)
                            u_window_val = u_values.get("Unutarnji prozor", 1.2)
                            u_door_val = u_values.get("Unutarnja vrata", 1.8)
                            faktor_orijentacije = 1.0 # Nema orijentacije za unutarnje zidove

                            gubitak_cistog_zida_unutarnji = cista_povrsina_zida_iter * u_wall_val * delta_t_prostorije * faktor_orijentacije
                            gubitak_prozora_unutarnji = povrsina_prozora_na_zidu * u_window_val * delta_t_prostorije * faktor_orijentacije
                            gubitak_vrata_unutarnji = povrsina_vrata_na_zidu * u_door_val * delta_t_prostorije * faktor_orijentacije
                            ukupni_gubitak_ovog_elementa = gubitak_cistog_zida_unutarnji + gubitak_prozora_unutarnji + gubitak_vrata_unutarnji

                            gubici_spojni_zidovi += ukupni_gubitak_ovog_elementa

                            # Ažuriramo detalje s izračunatim vrijednostima
                            detalji_za_ovaj_zid["gubitak_zid"] = gubitak_cistog_zida_unutarnji
                            detalji_za_ovaj_zid["gubitak_prozor"] = gubitak_prozora_unutarnji
                            detalji_za_ovaj_zid["gubitak_vrata"] = gubitak_vrata_unutarnji
                            detalji_za_ovaj_zid["ukupni_gubitak_elementa"] = ukupni_gubitak_ovog_elementa

                detalji_zidova.append(detalji_za_ovaj_zid)

            else:
                pass  # Ne računamo gubitke za ovaj tip zida (npr. unutarnji)
        
        # Izračun za pod i strop
        u_pod_val = u_values.get(prostorija.pod_tip, u_values.get("Pod na tlu", 0.3))
        u_strop_val = u_values.get(prostorija.strop_tip, u_values.get("Strop prema tavanu", 0.25))
        
        # Podešavanje faktora za pod i strop
        temp_faktor_pod = TEMP_FAKTORI.get(prostorija.pod_tip, 1.0)
        temp_faktor_strop = TEMP_FAKTORI.get(prostorija.strop_tip, 1.0)
        
        delta_t_pod = delta_t_vanjski
        delta_t_strop = delta_t_vanjski
        
        # Ako je posebna temperatura za negrijane prostore, koristi se ta
        if prostorija.pod_tip == "Pod prema negrijanom prostoru":
            delta_t_pod = temp_unutarnja - prostorija.temperatura_susjednog_negrijanog
        elif prostorija.pod_tip == "Pod iznad grijanog prostora":
            # Ako je iznad grijanog prostora, TEMP_FAKTORI bi trebali ovo riješiti
            delta_t_pod = delta_t_vanjski # Oslanjamo se na temp_faktor_pod
        
        if prostorija.strop_tip == "Prema negrijanom prostoru":
            delta_t_strop = temp_unutarnja - prostorija.temperatura_susjednog_negrijanog
        elif prostorija.strop_tip == "Ispod grijanog prostora":
            # Slično kao pod iznad grijanog, TEMP_FAKTORI bi trebali ovo riješiti
            delta_t_strop = delta_t_vanjski # Oslanjamo se na temp_faktor_strop

        gubitak_pod = povrsina * u_pod_val * delta_t_pod * temp_faktor_pod
        if prostorija.pod_tip == "Pod iznad grijanog prostora" and gubitak_pod < 0:
            gubitak_pod = 0
        if delta_t_pod < 0 and prostorija.pod_tip == "Pod prema negrijanom prostoru":
            gubitak_pod = 0
        
        gubici_pod += gubitak_pod
        
        gubitak_strop = povrsina * u_strop_val * delta_t_strop * temp_faktor_strop
        if prostorija.strop_tip == "Ispod grijanog prostora" and gubitak_strop < 0:
            gubitak_strop = 0
        if delta_t_strop < 0 and prostorija.strop_tip == "Prema negrijanom prostoru":
            gubitak_strop = 0

        gubici_strop += gubitak_strop        # Izračunaj osnovne transmisijske gubitke (bez toplinskih mostova)
        osnovni_transmisijski_gubici = (gubici_zidovi_cisti + gubici_prozori + gubici_vrata +
                                        gubici_spojni_zidovi + gubici_pod + gubici_strop)
        
        # Toplinski mostovi se računaju na osnovne transmisijske gubitke
        gubici_toplinski_mostovi = osnovni_transmisijski_gubici * toplinski_mostovi_faktor
        
        # Ukupni transmisijski gubici
        gubici_transmisijski = osnovni_transmisijski_gubici + gubici_toplinski_mostovi

        # 2. VENTILACIJSKI GUBICI
        protok_zraka = volumen * prostorija.izmjene_zraka
        gubici_ventilacijski = 0.34 * protok_zraka * delta_t_vanjski # Koristi se ρ*cp zraka = 1.2 kg/m3 * 1005 J/kgK / 3600 s/h ≈ 0.335 Wh/m3K

        # 3. UKUPNI GUBICI
        ukupni_gubici_prije_dodatka = gubici_transmisijski + gubici_ventilacijski
        
        # 4. DODATAK ZA SIGURNOST
        dodatak_sigurnosti = ukupni_gubici_prije_dodatka * (faktor_sigurnosti / 100) if faktor_sigurnosti > 0 else 0
        ukupni_gubici = ukupni_gubici_prije_dodatka + dodatak_sigurnosti
        
        # Specifični gubici W/m²
        specificni_gubici = ukupni_gubici / povrsina if povrsina > 0 else 0
        
        # Spremanje rezultata za ovu prostoriju
        rezultati[prostorija_id] = {
            "površina_prostorije": povrsina,
            "volumen_prostorije": volumen,
            "gubici_zidovi_cisti": gubici_zidovi_cisti,
            "gubici_prozori": gubici_prozori,
            "gubici_vrata": gubici_vrata,
            "gubici_spojni_zidovi": gubici_spojni_zidovi,
            "gubici_pod": gubici_pod,
            "gubici_strop": gubici_strop,
            "gubici_toplinski_mostovi": gubici_toplinski_mostovi,
            "gubici_transmisijski_ukupno": gubici_transmisijski,
            "protok_zraka": protok_zraka,
            "gubici_ventilacijski": gubici_ventilacijski,
            "dodatak_sigurnosti": dodatak_sigurnosti,
            "ukupni_gubici": ukupni_gubici,
            "specificni_gubici": specificni_gubici,
            "detalji_zidova": detalji_zidova
        }
        
        # Ažuriranje ukupnih suma
        ukupni_gubici_svih_prostorija += ukupni_gubici
        ukupna_povrsina_svih_prostorija += povrsina
    
    # Dodajemo ukupne rezultate
    rezultati["ukupno"] = {
        "ukupni_gubici": ukupni_gubici_svih_prostorija,
        "ukupna_površina": ukupna_povrsina_svih_prostorija,
        "specifični_gubici": ukupni_gubici_svih_prostorija / ukupna_povrsina_svih_prostorija if ukupna_povrsina_svih_prostorija > 0 else 0
    }
    
    return rezultati

def izracunaj_godisnju_potrebu_energije_vise_prostorija(rezultati, model, stupanj_dani=2800, sati_grijanja=4500):
    """
    Izračunava godišnju potrebu za energijom za više prostorija prema EN 12831
    
    Parameters:
    -----------
    rezultati : dict
        Rezultati izračuna toplinskih gubitaka
    model : MultiRoomModel
        Model s više prostorija
    stupanj_dani : int, optional
        Stupanj-dani grijanja (default 2800)
    sati_grijanja : int, optional
        Broj sati grijanja u sezoni (default 4500)
        
    Returns:
    --------
    dict
        Rezultati izračuna godišnje energije
    """
    # Ukupna godišnja energija
    ukupna_energija = 0.0
    
    # Energija po prostorijama
    energija_po_prostorijama = {}
    
    # Zbroj po etažama
    energija_po_etazama = {}
    povrsina_po_etazama = {}
    
    # Inicijaliziramo sume po etažama
    for etaza in model.etaze:
        energija_po_etazama[etaza.id] = 0.0
        povrsina_po_etazama[etaza.id] = 0.0
    
    for prostorija in model.prostorije:
        prostorija_id = prostorija.id
        
        if prostorija_id in rezultati:
            gubici = rezultati[prostorija_id]["ukupni_gubici"]
            povrsina = rezultati[prostorija_id]["površina_prostorije"]
            
            # Izračun godišnje energije
            godisnja_energija = (gubici * sati_grijanja) / 1000  # kWh
            energija_po_prostorijama[prostorija_id] = godisnja_energija
            
            ukupna_energija += godisnja_energija
            
            # Sumiranje po etažama
            if prostorija.etaza_id in energija_po_etazama:
                energija_po_etazama[prostorija.etaza_id] += godisnja_energija
                povrsina_po_etazama[prostorija.etaza_id] += povrsina
    
    # Specifična energija po etažama
    specificna_energija_po_etazama = {}
    for etaza_id, energija in energija_po_etazama.items():
        povrsina = povrsina_po_etazama.get(etaza_id, 0)
        specifična_energija = energija / povrsina if povrsina > 0 else 0
        specificna_energija_po_etazama[etaza_id] = specifična_energija
    
    # Ukupna specifična energija
    specificna_energija_ukupno = ukupna_energija / sum(povrsina_po_etazama.values()) if sum(povrsina_po_etazama.values()) > 0 else 0
    
    return {
        "ukupna_energija": ukupna_energija,
        "specifična_energija_ukupno": specificna_energija_ukupno,
        "stupanj_dani": stupanj_dani,
        "sati_grijanja": sati_grijanja,
        "energija_po_prostorijama": energija_po_prostorijama,
        "energija_po_etazama": energija_po_etazama,
        "specifična_energija_po_etazama": specificna_energija_po_etazama
    }
