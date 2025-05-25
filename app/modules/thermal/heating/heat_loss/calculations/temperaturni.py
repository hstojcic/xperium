"""
Modul za izračun i upravljanje temperaturama u proračunu toplinskih gubitaka.

Ovaj modul sadrži funkcije za izračun temperaturnih korekcija, dohvaćanje projektnih
temperatura, izračunavanje temperaturnih faktora i određivanje temperatura tla prema 
normama EN 12831 i EN ISO 13370.

Glavne funkcionalnosti:
- Dohvaćanje projektnih vanjskih temperatura za gradove u Hrvatskoj
- Izračun temperatura tla na različitim dubinama
- Izračun sezonskih varijacija temperature tla
- Izračun temperaturnih korekcijskih faktora za elemente prostorija 
- Izračun temperatura na granicama slojeva građevinskih elemenata (za kondenzaciju)
- Izračun stupanj-dana grijanja i sezonskih temperatura

Funkcije u ovom modulu također pružaju podatke za dinamičku analizu toplinskih 
svojstava zgrade tijekom cijele godine.
"""

from ..models.elementi.constants import VANJSKE_TEMP_PO_GRADOVIMA

def dohvati_projektnu_vanjsku_temperaturu(grad=None):
    """
    Dohvaća projektnu vanjsku temperaturu za određeni grad.
    
    Parameters:
    -----------
    grad : str, optional
        Ime grada za koji se dohvaća temperatura. Ako nije naveden, vraća default vrijednost.
        
    Returns:
    --------
    float
        Projektna vanjska temperatura u °C
    """
    if grad and grad in VANJSKE_TEMP_PO_GRADOVIMA:
        return VANJSKE_TEMP_PO_GRADOVIMA[grad]
    return -15.0  # Default vrijednost ako grad nije naveden ili ne postoji u rječniku

def izracunaj_temperaturne_korekcije(prostorija, temperatura_vanjska, temperatura_susjednih_negrijanih=None):
    """
    Izračunava temperaturne korekcije za različite elemente prostorije.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju temperaturne korekcije
    temperatura_vanjska : float
        Vanjska projektna temperatura
    temperatura_susjednih_negrijanih : float
        Temperatura susjednih negrijanih prostora (ako nije navedena, uzima se iz prostorije)
        
    Returns:
    --------
    dict
        Rječnik s temperaturnim korekcijama za različite elemente
    """
    # Temperatura u prostoriji
    temp_unutarnja = prostorija.temp_unutarnja
    
    # Temperatura susjednih negrijanih prostora
    if temperatura_susjednih_negrijanih is None:
        temperatura_susjednih_negrijanih = prostorija.temperatura_susjednog_negrijanog
    
    # Temperaturne razlike
    delta_t_vanjski = temp_unutarnja - temperatura_vanjska
    delta_t_negrijani = temp_unutarnja - temperatura_susjednih_negrijanih
    
    # Faktor korekcije za različite elemente
    # Koristi se formula f_i = (θ_int - θ_e,i) / (θ_int - θ_e)
    # gdje je:
    # - θ_int temperatura u prostoriji
    # - θ_e vanjska projektna temperatura
    # - θ_e,i temperatura s druge strane elementa
    
    # Izračun faktora korekcije za različite tipove elemenata
    f_vanjski = 1.0  # Vanjski elementi (zidovi, prozori, vrata) - bez korekcije
    f_negrijani = delta_t_negrijani / delta_t_vanjski  # Elementi prema negrijanim prostorima
    
    # Određivanje faktora korekcije za pod i strop
    f_pod = 1.0
    if prostorija.pod_tip == "Prema tlu":
        # Za pod prema tlu, temperaturna razlika je manja
        temp_tla = izracunaj_temperaturu_tla(temperatura_vanjska)
        f_pod = (temp_unutarnja - temp_tla) / delta_t_vanjski
    elif prostorija.pod_tip == "Prema negrijanom prostoru":
        f_pod = f_negrijani
    elif prostorija.pod_tip == "Prema vanjskom prostoru":
        f_pod = f_vanjski
    
    f_strop = 1.0
    if prostorija.strop_tip == "Prema negrijanom prostoru":
        f_strop = f_negrijani
    elif prostorija.strop_tip == "Prema vanjskom prostoru":
        f_strop = f_vanjski
    
    # Faktori korekcije za različite elemente
    korekcije = {
        "vanjski_zid": f_vanjski,
        "prozor": f_vanjski,
        "vrata": f_vanjski,
        "zid_prema_negrijanom": f_negrijani,
        "pod": f_pod,
        "strop": f_strop
    }
    
    return korekcije

def izracunaj_temperaturu_tla(temperatura_vanjska, dubina=0.5):
    """
    Izračunava temperaturu tla na određenoj dubini.
    
    Prema EN 12831, temperatura tla se može procijeniti ovisno o vanjskoj temperaturi.
    
    Parameters:
    -----------
    temperatura_vanjska : float
        Vanjska projektna temperatura u °C
    dubina : float
        Dubina tla u metrima
        
    Returns:
    --------
    float
        Procijenjena temperatura tla u °C
    """
    # Pojednostavljena formula za procjenu temperature tla
    # Temperatura tla na dubini od oko 0.5m je obično viša od vanjske temperature
    # i manje varira s promjenom godišnjeg doba
    
    # Za dubinu 0.5m, koristimo korekciju od oko +7°C u odnosu na vanjsku temperaturu
    if temperatura_vanjska < -15:
        return 5.0  # Minimalna temperatura tla
    
    procjena = temperatura_vanjska + 7.0 + (dubina * 2.0)
    
    # Ograničenje vrijednosti
    return max(5.0, min(procjena, 12.0))  # Temperatura tla je obično između 5°C i 12°C

def izracunaj_temperaturu_tla_po_mjesecima(grad="Zagreb", dubina=0.5):
    """
    Izračunava temperaturu tla za svaki mjesec u godini na određenoj dubini.
    
    Temperatura tla varira kroz godinu, ali s manjom amplitudom i 
    s vremenskim pomakom u odnosu na vanjsku temperaturu.
    
    Parameters:
    -----------
    grad : str
        Ime grada za koji se izračunava temperatura tla
    dubina : float
        Dubina tla u metrima
        
    Returns:
    --------
    dict
        Rječnik s temperaturama tla za svaki mjesec
    """
    # Dohvaćanje temperaturnog profila kroz godinu
    temp_profil = izracunaj_temperaturni_profil_godine(grad)
    
    # Izračun temperatura tla po mjesecima
    # S povećanjem dubine, varijacije temperature se smanjuju i 
    # javlja se veći vremenski pomak u odnosu na vanjsku temperaturu
    
    # Parametri za modeliranje temperature tla
    amplitude_reduction = max(0.1, 1.0 - (dubina * 0.4))  # Smanjenje amplitude s dubinom
    time_lag_months = min(3, int(dubina * 2.0))  # Vremenski pomak u mjesecima (max 3 mjeseca)
    
    # Izračun srednje godišnje temperature
    srednja_godisnja = izracunaj_srednju_godisnju_temperaturu(grad)
    
    temp_tla = {}
    for mjesec in range(1, 13):
        # Određivanje mjeseca iz kojeg uzimamo vanjsku temperaturu (s vremenskim pomakom)
        mjesec_vani = (mjesec - time_lag_months) % 12
        if mjesec_vani == 0:
            mjesec_vani = 12
        
        # Izračun razlike od srednje temperature (uz smanjenu amplitudu)
        razlika = (temp_profil[mjesec_vani] - srednja_godisnja) * amplitude_reduction
        
        # Konačna temperatura tla
        temp_tla[mjesec] = srednja_godisnja + razlika
        
        # Ograničenje vrijednosti
        temp_tla[mjesec] = max(4.0, min(temp_tla[mjesec], 20.0))
    
    return temp_tla

def izracunaj_temperaturu_tla_po_dubini(srednja_godisnja_temp, dubine=None):
    """
    Izračunava temperaturu tla na različitim dubinama za srednju godišnju temperaturu.
    
    Na većim dubinama, temperatura tla se približava srednjoj godišnjoj temperaturi zraka.
    
    Parameters:
    -----------
    srednja_godisnja_temp : float
        Srednja godišnja temperatura zraka na lokaciji u °C
    dubine : list of float, optional
        Lista dubina za koje se računa temperatura (u metrima)
        Ako nije navedeno, koriste se standardne dubine: 0.5, 1.0, 2.0, 3.0, 5.0 m
        
    Returns:
    --------
    dict
        Rječnik s temperaturama tla na različitim dubinama
    """
    # Standardne dubine ako nisu navedene
    if dubine is None:
        dubine = [0.5, 1.0, 2.0, 3.0, 5.0]
    
    rezultati = {}
    
    for dubina in dubine:
        # Na dubini 0m, temperatura je približna vanjskoj temperaturi
        # S porastom dubine, približava se srednjoj godišnjoj temperaturi s korekcijom
        
        # Korekcija za dubinu (temperatura se stabilizira s dubinom)
        if dubina < 0.5:
            # Plitki sloj tla pod velikim utjecajem vanjske temperature
            korekcija = -2.0  # Malo hladnije od srednje godišnje temperature
        elif dubina < 1.0:
            korekcija = -1.0
        elif dubina < 2.0:
            korekcija = -0.5
        elif dubina < 4.0:
            korekcija = 0.0  # Na dubini 2-4m, temperatura je približno jednaka srednjoj godišnjoj
        else:
            korekcija = 0.5  # Na većim dubinama, blagi porast temperature
        
        # Izračun temperature na određenoj dubini
        temperatura = srednja_godisnja_temp + korekcija
        
        # Ograničenje na razumne vrijednosti
        temperatura = max(4.0, min(temperatura, 20.0))
        
        rezultati[dubina] = temperatura
    
    return rezultati

def izracunaj_korekcijski_faktor_B(temperatura_unutarnja, temperatura_vanjska, tip_elementa, dubina=None):
    """
    Izračunava korekcijski faktor B za toplinske gubitke prema tlu prema normi EN ISO 13370.
    
    Parameters:
    -----------
    temperatura_unutarnja : float
        Unutarnja projektna temperatura u °C
    temperatura_vanjska : float
        Vanjska projektna temperatura u °C
    tip_elementa : str
        Tip elementa: 'pod_na_tlu', 'zid_prema_tlu', 'pod_podruma'
    dubina : float, optional
        Dubina elementa u tlu (za zidove prema tlu i podove podruma)
        
    Returns:
    --------
    float
        Korekcijski faktor B (bezdimenzionalni)
    """
    # Temperaturna razlika između unutarnje i vanjske temperature
    delta_t = temperatura_unutarnja - temperatura_vanjska
    
    # Izračun temperature tla ovisno o tipu elementa
    temperatura_tla = 0.0
    
    if tip_elementa == 'pod_na_tlu':
        temperatura_tla = izracunaj_temperaturu_tla(temperatura_vanjska, dubina=0.5)
    elif tip_elementa == 'zid_prema_tlu':
        if dubina is None:
            dubina = 1.0  # Pretpostavljena dubina ako nije navedena
        temperatura_tla = izracunaj_temperaturu_tla(temperatura_vanjska, dubina=dubina)
    elif tip_elementa == 'pod_podruma':
        if dubina is None:
            dubina = 2.0  # Pretpostavljena dubina ako nije navedena
        temperatura_tla = izracunaj_temperaturu_tla(temperatura_vanjska, dubina=dubina)
    
    # Izračun korekcijskog faktora B
    # B = (θi - θg) / (θi - θe)
    # θi - unutarnja temperatura
    # θg - temperatura tla
    # θe - vanjska temperatura
    
    if delta_t == 0:
        return 0.0  # Izbjegavanje dijeljenja s nulom
    
    faktor_B = (temperatura_unutarnja - temperatura_tla) / delta_t
    
    # Ograničenje vrijednosti faktora B
    return max(0.0, min(faktor_B, 1.0))

def izracunaj_temperaturne_faktore_prostorije(prostorija, temperatura_vanjska, temperatura_susjednih_negrijanih=None):
    """
    Izračunava detaljne temperaturne faktore za sve tipove elemenata prostorije.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija za koju se računaju temperaturni faktori
    temperatura_vanjska : float
        Vanjska projektna temperatura u °C
    temperatura_susjednih_negrijanih : float, optional
        Temperatura susjednih negrijanih prostorija. Ako nije navedena,
        koristi se temperatura_susjednog_negrijanog iz prostorije, a ako je
        dostupna izračunata temperatura negrijane prostorije, koristi se ona.
        
    Returns:
    --------
    dict
        Rječnik s detaljnim temperaturnim faktorima za različite elemente
    """
    # Temperatura u prostoriji
    temp_unutarnja = prostorija.temp_unutarnja
    
    # Temperaturna razlika između unutarnje i vanjske temperature
    delta_t = temp_unutarnja - temperatura_vanjska
    
    # Izračun temperature tla
    temperatura_tla = izracunaj_temperaturu_tla(temperatura_vanjska)
    
    # Temperatura susjednih negrijanih prostora - koristimo najprecizniju dostupnu
    if temperatura_susjednih_negrijanih is not None:
        temperatura_susjednih = temperatura_susjednih_negrijanih
    elif hasattr(prostorija, 'izracunata_temp_negrijane') and prostorija.izracunata_temp_negrijane is not None:
        temperatura_susjednih = prostorija.izracunata_temp_negrijane
    else:
        temperatura_susjednih = prostorija.temperatura_susjednog_negrijanog
    
    # Izračun faktora za različite tipove elemenata
    faktori = {
        # Osnovni faktori
        "vanjski_zid": 1.0,
        "prozor": 1.0,
        "vanjska_vrata": 1.0,
        
        # Pod
        "pod_na_tlu": izracunaj_korekcijski_faktor_B(temp_unutarnja, temperatura_vanjska, 'pod_na_tlu'),
        "pod_prema_podrumu": (temp_unutarnja - temperatura_susjednih) / delta_t if delta_t != 0 else 0.0,
        "pod_iznad_vanjskog_prostora": 1.0,
        
        # Strop i krov
        "strop_prema_tavanu": (temp_unutarnja - temperatura_susjednih) / delta_t if delta_t != 0 else 0.0,
        "ravni_krov": 1.0,
        "kosi_krov": 1.0,
        
        # Zidovi
        "zid_prema_negrijanom": (temp_unutarnja - temperatura_susjednih) / delta_t if delta_t != 0 else 0.0,
        "zid_prema_tlu": izracunaj_korekcijski_faktor_B(temp_unutarnja, temperatura_vanjska, 'zid_prema_tlu'),
    }
    
    # Osiguravamo da su svi faktori u validnom rasponu [0, 1]
    for kljuc in faktori:
        faktori[kljuc] = max(0.0, min(faktori[kljuc], 1.0))
    
    return faktori

def izracunaj_temperature_negrijanih_prostorija_iterativno(model, temperatura_vanjska, max_iteracija=10, prag_konvergencije=0.1):
    """
    Izračunava temperature negrijanih prostorija iterativnim postupkom
    do konvergencije ili maksimalnog broja iteracija. Implementira napredni algoritam
    s postupnim ujednačavanjem temperatura za bolje i brže približavanje rješenju.
    
    Koristi poboljšani relaksacijski algoritam koji pomaže u bržoj konvergenciji i
    sprječava oscilacije u slučajevima složenih međuovisnosti više negrijanih prostorija.
    Algoritam uključuje:
    - Adaptivni relaksacijski faktor za poboljšanu stabilnost
    - Sortiranje negrijanih prostorija prema povezanosti s grijanim prostorijama
    - Detekciju i korekciju oscilacija temperature tijekom iteracija
    - Praćenje povijesti temperatura za bolje razumijevanje konvergencije

    Parameters:
    -----------
    model : MultiRoomModel
        Model zgrade s prostorijama
    temperatura_vanjska : float
        Vanjska projektna temperatura
    max_iteracija : int, optional
        Maksimalni broj iteracija (default=10)
    prag_konvergencije : float, optional
        Prag za provjeru konvergencije temperature (u °C) (default=0.1)

    Returns:
    --------
    dict
        Rječnik s ID-evima negrijanih prostorija i izračunatim temperaturama
    """
    # Za svaku negrijanu prostoriju dohvaćamo povezane prostorije
    negrijane_prostorije = [p for p in model.prostorije if hasattr(p, 'grijana') and not p.grijana]
    if not negrijane_prostorije:
        return {}  # Ako nema negrijanih prostorija, vraćamo prazan rječnik

    # U ovoj strukturi pratimo prethodne temperature za analizu konvergencije
    povijest_temperatura = {}
    for prostorija in negrijane_prostorije:
        povijest_temperatura[prostorija.id] = []
    
    # Početne vrijednosti - prvotni izračun
    for prostorija in negrijane_prostorije:
        # Početna procjena temelji se direktno na okolnim prostorima
        pocetna_temp = prostorija.izracunaj_temperaturu_negrijane_prostorije(temperatura_vanjska)
        prostorija.izracunata_temp_negrijane = round(pocetna_temp, 1)
        povijest_temperatura[prostorija.id].append(prostorija.izracunata_temp_negrijane)
    
    # Sortiranje negrijanih prostorija prema broju susjednih prostorija
    # Prioritet dajemo prostorijama s više susjednih grijanih prostora jer je njihov
    # izračun stabilniji (više poznatih temperatura)
    def broji_susjedne_grijane(prostorija):
        susjedne_grijane = 0
        for zid in prostorija.zidovi:
            if zid.get("tip") == "prema_prostoriji" and zid.get("povezana_prostorija_id"):
                povezana = model.dohvati_prostoriju(zid.get("povezana_prostorija_id"))
                if povezana and hasattr(povezana, 'grijana') and povezana.grijana:
                    susjedne_grijane += 1
        return susjedne_grijane
    
    # Sortiramo prostorije po broju susjednih grijanih prostorija (primarno)
    # i ukupnom broju povezanih prostorija (sekundarno)
    sortirane_prostorije = sorted(
        negrijane_prostorije, 
        key=lambda p: (broji_susjedne_grijane(p), 
                      len([zid for zid in p.zidovi if zid.get("tip") == "prema_prostoriji"])),
        reverse=True
    )
        
    # Izračun težine pri relaksaciji za optimalno približavanje rješenju
    relaksacijski_faktor = 0.7  # Faktor između 0 i 1: 
                               # Manje vrijednosti - sporija ali stabilnija konvergencija
                               # Veće vrijednosti - brža ali potencijalno nestabilnija konvergencija
    
    # Detekcija oscilacija po prostorijama
    oscilacije_po_prostoriji = {p.id: False for p in negrijane_prostorije}
    
    # Iterativni postupak
    for iteracija in range(max_iteracija):
        najveca_razlika = 0.0
        
        # Za svaku negrijanu prostoriju:
        for prostorija in sortirane_prostorije:
            prethodna_temperatura = prostorija.izracunata_temp_negrijane
            
            # Izračunaj novu temperaturu koristeći trenutne vrijednosti okolnih prostorija
            nova_temperatura = prostorija.izracunaj_temperaturu_negrijane_prostorije(temperatura_vanjska)
            
            # Primjena adaptivnog relaksacijskog faktora za stabilizaciju konvergencije
            # Ako prostorija ima povijest oscilacija, koristimo niži faktor
            lokalni_relaksacijski_faktor = relaksacijski_faktor
            if oscilacije_po_prostoriji[prostorija.id]:
                lokalni_relaksacijski_faktor = max(0.3, relaksacijski_faktor * 0.7)
            
            # Ti+1 = Ti + relaksacijski_faktor * (Ti_nova - Ti)
            if prethodna_temperatura is not None:
                prilagodjena_temperatura = prethodna_temperatura + lokalni_relaksacijski_faktor * (nova_temperatura - prethodna_temperatura)
                prostorija.izracunata_temp_negrijane = round(prilagodjena_temperatura, 1)
            else:
                prostorija.izracunata_temp_negrijane = round(nova_temperatura, 1)
            
            # Provjeri konvergenciju
            razlika = abs(prostorija.izracunata_temp_negrijane - prethodna_temperatura) if prethodna_temperatura is not None else float('inf')
            najveca_razlika = max(najveca_razlika, razlika)
            
            # Spremanje u povijest za analizu konvergencije
            povijest_temperatura[prostorija.id].append(prostorija.izracunata_temp_negrijane)
            
        # Ako je postignuta konvergencija, prekidamo iteraciju
        if najveca_razlika <= prag_konvergencije:
            break
            
        # Provjera oscilacija po prostorijama
        if iteracija >= 3:
            for prostorija in negrijane_prostorije:
                zadnje_temp = povijest_temperatura[prostorija.id][-4:] if len(povijest_temperatura[prostorija.id]) >= 4 else povijest_temperatura[prostorija.id]
                
                # Provjera za oscilacije (uzlazno-silazni ili silazno-uzlazni uzorak)
                if len(zadnje_temp) >= 3:
                    # Detekcija klasične oscilacije
                    if (zadnje_temp[-3] > zadnje_temp[-2] and zadnje_temp[-2] < zadnje_temp[-1]) or \
                       (zadnje_temp[-3] < zadnje_temp[-2] and zadnje_temp[-2] > zadnje_temp[-1]):
                        oscilacije_po_prostoriji[prostorija.id] = True
                    
                    # Detekcija divergentne oscilacije (povećanje amplitude)
                    if len(zadnje_temp) >= 4:
                        if ((zadnje_temp[-4] > zadnje_temp[-3] and zadnje_temp[-3] < zadnje_temp[-2] and 
                             zadnje_temp[-2] > zadnje_temp[-1] and 
                             abs(zadnje_temp[-4] - zadnje_temp[-3]) < abs(zadnje_temp[-2] - zadnje_temp[-1])) or
                            (zadnje_temp[-4] < zadnje_temp[-3] and zadnje_temp[-3] > zadnje_temp[-2] and 
                             zadnje_temp[-2] < zadnje_temp[-1] and 
                             abs(zadnje_temp[-4] - zadnje_temp[-3]) < abs(zadnje_temp[-2] - zadnje_temp[-1]))):
                            # Detektirana jača oscilacija, dodatno smanjujemo globalni relaksacijski faktor
                            relaksacijski_faktor = max(0.2, relaksacijski_faktor * 0.6)
            
            # Ako je detektirana oscilacija kod barem jedne prostorije, smanjujemo globalni relaksacijski faktor
            if any(oscilacije_po_prostoriji.values()):
                relaksacijski_faktor = max(0.3, relaksacijski_faktor * 0.8)

    # Stvaranje rječnika s rezultatima
    rezultati = {}
    for prostorija in negrijane_prostorije:
        rezultati[prostorija.id] = prostorija.izracunata_temp_negrijane
    
    return rezultati

def izracunaj_temperature_za_model(model, grad=None):
    """
    Izračunava i priprema temperature za cijeli model zgrade.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model za koji se izračunavaju temperature
    grad : str, optional
        Ime grada za koji se dohvaća vanjska temperatura. Ako nije naveden,
        koristi se zadana vrijednost.
        
    Returns:
    --------
    dict
        Rječnik s temperaturnim podacima za cijeli model
    """
    # Dohvat vanjske projektne temperature
    temperatura_vanjska = dohvati_projektnu_vanjsku_temperaturu(grad)
    
    # Izračun temperature tla
    temperatura_tla = izracunaj_temperaturu_tla(temperatura_vanjska)
    
    # Izračun srednje godišnje temperature
    srednja_godisnja = izracunaj_srednju_godisnju_temperaturu(grad)
    
    # Izračun temperatura tla po dubinama
    temperature_tla_po_dubini = izracunaj_temperaturu_tla_po_dubini(srednja_godisnja)
    
    # Izračun sezonskih temperatura
    sezonske_temperature = izracunaj_sezonske_temperature(grad, izracunaj_vlagu=True)
      # Izračun temperatura negrijanih prostorija iterativnim postupkom
    temperature_negrijanih = izracunaj_temperature_negrijanih_prostorija_iterativno(
        model, 
        temperatura_vanjska,
        max_iteracija=15,  # Povećani broj iteracija za veću preciznost
        prag_konvergencije=0.1  # Prag konvergencije usklađen s točnošću temperature (0.1°C)
    )
    
    # Osvježavanje temperature_susjednog_negrijanog u svim prostorijama
    # nakon što smo izračunali temperature negrijanih prostorija
    for prostorija in model.prostorije:
        if hasattr(prostorija, 'grijana') and not prostorija.grijana and hasattr(prostorija, 'izracunata_temp_negrijane'):
            if prostorija.izracunata_temp_negrijane is not None:
                prostorija.temperatura_susjednog_negrijanog = prostorija.izracunata_temp_negrijane
    
    # Izračun stupanj-dana grijanja (za standardnu temperaturu 20°C)
    stupanj_dani = izracunaj_stupanj_dane_grijanja(grad, 20.0)
    
    # Rezultati za sve etaže i prostorije
    rezultati = {
        "vanjska": temperatura_vanjska,  # Key za pristup iz drugih funkcija
        "vanjska_temperatura": temperatura_vanjska,  # Original key - zadržan za kompatibilnost
        "temperatura_tla": temperatura_tla,
        "srednja_godisnja_temperatura": srednja_godisnja,
        "temperature_tla_po_dubini": temperature_tla_po_dubini,
        "sezonske_temperature": sezonske_temperature,
        "stupanj_dani_grijanja": stupanj_dani,
        "temperature_negrijanih": temperature_negrijanih,
        "etaze": {}
    }  
      
    # Izračun za svaku etažu i prostoriju
    for etaza in model.etaze:
        rezultati["etaze"][etaza.id] = {
            "prostorije": {}
        }
        
        # Dohvatimo prostorije za etažu iz modela
        prostorije_etaze = model.dohvati_prostorije_za_etazu(etaza.id)
            
        for prostorija in prostorije_etaze:
            # Odredimo stvarnu temperaturu prostorije
            stvarna_temp = prostorija.temp_unutarnja
            
            # Za negrijane prostorije, koristimo izračunatu temperaturu
            if hasattr(prostorija, 'grijana') and not prostorija.grijana and hasattr(prostorija, 'izracunata_temp_negrijane'):
                if prostorija.izracunata_temp_negrijane is not None:
                    stvarna_temp = prostorija.izracunata_temp_negrijane
            
            # Izračun temperaturnih korekcija za prostoriju
            korekcije = izracunaj_temperaturne_korekcije(
                prostorija,
                temperatura_vanjska,
                # Ako je prostorija negrijana, koristimo izračunatu temperaturu
                temperatura_susjednih_negrijanih=prostorija.izracunata_temp_negrijane if 
                    (hasattr(prostorija, 'grijana') and not prostorija.grijana and 
                     hasattr(prostorija, 'izracunata_temp_negrijane') and 
                     prostorija.izracunata_temp_negrijane is not None) 
                    else None
            )
              
            # Izračun detaljnih temperaturnih faktora
            detaljni_faktori = izracunaj_temperaturne_faktore_prostorije(
                prostorija,
                temperatura_vanjska,
                # Ako je prostorija negrijana, koristimo izračunatu temperaturu
                temperatura_susjednih_negrijanih=prostorija.izracunata_temp_negrijane if 
                    (hasattr(prostorija, 'grijana') and not prostorija.grijana and 
                     hasattr(prostorija, 'izracunata_temp_negrijane') and 
                     prostorija.izracunata_temp_negrijane is not None) 
                    else None
            )
            
            rezultati["etaze"][etaza.id]["prostorije"][prostorija.id] = {
                "unutarnja_temperatura": stvarna_temp,
                "korekcije": korekcije,
                "temperaturni_faktori": detaljni_faktori
            }
    
    return rezultati

def izracunaj_temperaturu_susjednog_prostora(prostorija_ref, prostorija_susjedna):
    """
    Izračunava učinak temperature susjedne prostorije na referentnu prostoriju.
    
    Parameters:
    -----------
    prostorija_ref : Prostorija
        Referentna prostorija za koju se računa učinak
    prostorija_susjedna : Prostorija
        Susjedna prostorija koja utječe na referentnu
        
    Returns:
    --------
    float
        Temperaturna korekcija za zajednički zid
    """
    # Temperaturna razlika između prostorija
    delta_t = prostorija_ref.temp_unutarnja - prostorija_susjedna.temp_unutarnja
    
    # Ako je susjedna prostorija toplija, ne postoji toplinski gubitak
    if delta_t <= 0:
        return 0.0
    
    # Inače, izračunavamo korekcijski faktor
    return delta_t

def izracunaj_srednju_godisnju_temperaturu(grad="Zagreb"):
    """
    Izračunava srednju godišnju temperaturu za određeni grad.
    
    Parameters:
    -----------
    grad : str
        Ime grada za koji se izračunava srednja godišnja temperatura
        
    Returns:
    --------
    float
        Srednja godišnja temperatura u °C
    """
    # Pojednostavljena procjena srednje godišnje temperature
    # U stvarnosti, ovo bi se trebalo temeljiti na stvarnim podacima
    
    # Projektna temperatura je zimska ekstremna temperatura
    projektna_temp = dohvati_projektnu_vanjsku_temperaturu(grad)
    
    # Za procjenu srednje godišnje temperature koristimo korekciju
    # Hrvatska u prosjeku ima srednju godišnju temperaturu između 10°C i 16°C
    if projektna_temp < -15:  # Kontinentalna Hrvatska (hladnija područja)
        return 10.5
    elif projektna_temp < -10:  # Kontinentalna Hrvatska (umjerena područja)
        return 11.5
    elif projektna_temp < -5:  # Unutrašnjost Istre i Gorski kotar
        return 12.5
    elif projektna_temp < 0:  # Obalno područje (sjever)
        return 14.0
    else:  # Obalno područje (jug)
        return 16.0

def izracunaj_temperaturni_profil_godine(grad="Zagreb"):
    """
    Izračunava približni temperaturni profil za cijelu godinu za odabrani grad.
    
    Parameters:
    -----------
    grad : str
        Ime grada za koji se izračunava temperaturni profil
        
    Returns:
    --------
    dict
        Rječnik s prosječnim temperaturama za svaki mjesec
    """
    # Projektna temperatura (zimski ekstrem)
    projektna_temp = dohvati_projektnu_vanjsku_temperaturu(grad)
    
    # Srednja godišnja temperatura
    srednja_temp = izracunaj_srednju_godisnju_temperaturu(grad)
    
    # Ljetni ekstrem (procjena)
    ljetni_ekstrem = 35.0 if projektna_temp < -10 else 32.0
    
    # Mjesečne temperature (okvirne vrijednosti)
    return {
        1: srednja_temp - 8.0,  # Siječanj
        2: srednja_temp - 6.0,  # Veljača
        3: srednja_temp - 2.0,  # Ožujak
        4: srednja_temp + 2.0,  # Travanj
        5: srednja_temp + 6.0,  # Svibanj
        6: srednja_temp + 9.0,  # Lipanj
        7: srednja_temp + 12.0,  # Srpanj
        8: srednja_temp + 11.0,  # Kolovoz
        9: srednja_temp + 7.0,  # Rujan
        10: srednja_temp + 3.0,  # Listopad
        11: srednja_temp - 1.0,  # Studeni
        12: srednja_temp - 5.0   # Prosinac
    }

def izracunaj_temperaturu_na_granici_slojeva(temperatura_unutarnja, temperatura_vanjska, 
                                            u_vrijednost_ukupna, r_vrijednosti_slojeva):
    """
    Izračunava temperature na granicama slojeva konstrukcije.
    
    Parameters:
    -----------
    temperatura_unutarnja : float
        Unutarnja projektna temperatura u °C
    temperatura_vanjska : float
        Vanjska projektna temperatura u °C
    u_vrijednost_ukupna : float
        Ukupni koeficijent prolaza topline konstrukcije u W/(m²K)
    r_vrijednosti_slojeva : list of float
        Lista toplinskih otpora slojeva konstrukcije (R = d/λ) u m²K/W,
        uključujući i otpore prijelaza topline na unutarnjoj i vanjskoj strani
        
    Returns:
    --------
    list of float
        Lista temperatura na granicama slojeva (uključujući unutarnju i vanjsku površinu)
    """
    # Temperaturna razlika
    delta_t = temperatura_unutarnja - temperatura_vanjska
    
    # Ukupni toplinski otpor konstrukcije
    r_ukupno = sum(r_vrijednosti_slojeva)
    
    # Provjera konzistentnosti podataka
    if abs(1/u_vrijednost_ukupna - r_ukupno) > 0.1:
        # Ako se U-vrijednost ne podudara s ukupnim otporom, koristimo R_ukupno
        print(f"Upozorenje: U-vrijednost ({u_vrijednost_ukupna}) ne odgovara ukupnom otporu ({r_ukupno})")
    
    # Izračun temperatura na granicama slojeva
    temperature = [temperatura_unutarnja]  # Početak s unutarnjom temperaturom
    
    r_kumulativno = 0
    for i, r_sloj in enumerate(r_vrijednosti_slojeva[:-1]):  # Izuzimamo zadnji sloj jer njegovu vanjsku temperaturu računamo posebno
        r_kumulativno += r_sloj
        pad_temperature = delta_t * (r_kumulativno / r_ukupno)
        temperature.append(temperatura_unutarnja - pad_temperature)
    
    # Dodavanje vanjske temperature (na kraju zadnjeg sloja)
    temperature.append(temperatura_vanjska)
    
    return temperature

def izracunaj_stupanj_dane_grijanja(grad="Zagreb", bazna_temperatura=20.0):
    """
    Izračunava stupanj-dane grijanja za cijelu godinu za određeni grad.
    Stupanj-dani grijanja su suma dnevnih razlika između bazne temperature i 
    srednje dnevne temperature za sve dane kada je srednja dnevna temperatura 
    niža od bazne temperature.
    
    Parameters:
    -----------
    grad : str
        Ime grada za koji se računaju stupanj-dani grijanja
    bazna_temperatura : float
        Bazna temperatura (obično unutarnja projektna temperatura) u °C
        
    Returns:
    --------
    dict
        Rječnik s brojem stupanj-dana grijanja po mjesecima i ukupno
    """
    # Dohvaćanje prosječnih temperatura po mjesecima
    temp_profil = izracunaj_temperaturni_profil_godine(grad)
    
    # Broj dana u svakom mjesecu
    dani_u_mjesecu = {
        1: 31,  # Siječanj
        2: 28,  # Veljača (nije prijestupna godina)
        3: 31,  # Ožujak
        4: 30,  # Travanj
        5: 31,  # Svibanj
        6: 30,  # Lipanj
        7: 31,  # Srpanj
        8: 31,  # Kolovoz
        9: 30,  # Rujan
        10: 31,  # Listopad
        11: 30,  # Studeni
        12: 31   # Prosinac
    }
    
    # Izračun stupanj-dana grijanja za svaki mjesec
    stupanj_dani = {}
    ukupno = 0
    
    for mjesec, temp in temp_profil.items():
        # Ako je prosječna temperatura mjeseca niža od bazne temperature,
        # računamo stupanj-dane grijanja za taj mjesec
        if temp < bazna_temperatura:
            stupanj_dani_mjeseca = (bazna_temperatura - temp) * dani_u_mjesecu[mjesec]
            stupanj_dani[mjesec] = round(stupanj_dani_mjeseca, 1)
            ukupno += stupanj_dani_mjeseca
        else:
            stupanj_dani[mjesec] = 0.0
    
    # Dodavanje ukupnog broja stupanj-dana grijanja
    stupanj_dani["ukupno"] = round(ukupno, 1)
    
    return stupanj_dani

def izracunaj_sezonske_temperature(grad="Zagreb", dubina_tla=0.5, izracunaj_vlagu=False):
    """
    Izračunava sezonske temperature i opcijski relativnu vlažnost za određeni grad.
    
    Parameters:
    -----------
    grad : str
        Ime grada za koji se izračunavaju sezonske temperature
    dubina_tla : float
        Dubina tla za izračun temperature tla u metrima
    izracunaj_vlagu : bool
        Ako je True, izračunava i prosječnu relativnu vlažnost po sezonama
        
    Returns:
    --------
    dict
        Rječnik s temperaturama i opcijski vlažnosti po sezonama
    """
    # Definicija sezona (mjeseci)
    sezone = {
        "zima": [12, 1, 2],     # Prosinac, Siječanj, Veljača
        "proljeće": [3, 4, 5],  # Ožujak, Travanj, Svibanj
        "ljeto": [6, 7, 8],     # Lipanj, Srpanj, Kolovoz
        "jesen": [9, 10, 11]    # Rujan, Listopad, Studeni
    }
    
    # Dohvaćanje mjesečnih temperatura
    temp_profil = izracunaj_temperaturni_profil_godine(grad)
    
    # Dohvaćanje temperatura tla po mjesecima
    temp_tla_profil = izracunaj_temperaturu_tla_po_mjesecima(grad, dubina=dubina_tla)
    
    # Prosječne relativne vlažnosti po sezonama za različite klimatske regije
    # Ovo su aproksimacije i trebale bi se zamijeniti stvarnim podacima
    relativna_vlaznost = {}
    
    if izracunaj_vlagu:
        # Određivanje klimatske regije iz projektne temperature
        projektna_temp = dohvati_projektnu_vanjsku_temperaturu(grad)
        
        if projektna_temp < -15:  # Kontinentalna Hrvatska (hladnija područja)
            relativna_vlaznost = {
                "zima": 85,      # Zima - visoka vlažnost
                "proljeće": 70,  # Proljeće - umjerena vlažnost
                "ljeto": 65,     # Ljeto - niža vlažnost
                "jesen": 80      # Jesen - povišena vlažnost
            }
        elif projektna_temp < -5:  # Kontinentalna Hrvatska (umjerena područja)
            relativna_vlaznost = {
                "zima": 80,
                "proljeće": 65,
                "ljeto": 60,
                "jesen": 75
            }
        else:  # Obalno područje
            relativna_vlaznost = {
                "zima": 75,
                "proljeće": 70,
                "ljeto": 65,
                "jesen": 75
            }
    
    # Izračun prosječnih temperatura po sezonama
    rezultati = {
        "temperatura_zraka": {},
        "temperatura_tla": {}
    }
    
    if izracunaj_vlagu:
        rezultati["relativna_vlaznost"] = relativna_vlaznost
    
    for sezona, mjeseci in sezone.items():
        # Izračun prosječne temperature zraka za sezonu
        ukupno_temp = sum(temp_profil[mjesec] for mjesec in mjeseci)
        prosjecna_temp = ukupno_temp / len(mjeseci)
        rezultati["temperatura_zraka"][sezona] = round(prosjecna_temp, 1)
        
        # Izračun prosječne temperature tla za sezonu
        ukupno_temp_tla = sum(temp_tla_profil[mjesec] for mjesec in mjeseci)
        prosjecna_temp_tla = ukupno_temp_tla / len(mjeseci)
        rezultati["temperatura_tla"][sezona] = round(prosjecna_temp_tla, 1)
    
    return rezultati
