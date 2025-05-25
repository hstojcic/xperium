"""
Modul koji objedinjuje izračun toplinskih gubitaka.
"""

from ..calculations.transmisijski import izracun_transmisijskih_gubitaka
from ..calculations.ventilacijski import izracun_ventilacijskih_gubitaka, izracun_infiltracije
from ..calculations.toplinski_most import izracun_toplinskih_mostova_po_vrsti, procjena_toplinskih_mostova_postotkom
from ..calculations.temperaturni import izracunaj_temperature_za_model
import streamlit as st

def izracunaj_toplinske_gubitke_prostorije(prostorija, temperature_dict, katalog=None):
    """
    Izračunava ukupne toplinske gubitke za jednu prostoriju.
    
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
        Rječnik s izračunatim gubicima (transmisijski, ventilacijski, toplinski mostovi)
    """
    # Provjera i priprema temperature_dict
    if not isinstance(temperature_dict, dict):
        st.error("Greška: temperature_dict nije rječnik")
        temperature_dict = {"vanjska": -20.0}  # Default vrijednost za vanjsku temperaturu
    
    # Osiguraj da postoji ključ 'vanjska'
    if "vanjska" not in temperature_dict:
        st.warning("Nedostaje vanjska temperatura. Koristim defaultnu vrijednost -20.0°C.")
        temperature_dict["vanjska"] = -20.0
    
    # Spremanje temperature prostorije u session state za izračune međuprostornih zidova
    if "temperature_prostorija" not in st.session_state:
        st.session_state["temperature_prostorija"] = {}
    st.session_state["temperature_prostorija"][prostorija.id] = prostorija.temp_unutarnja
    
    # Izračun transmisijskih gubitaka
    transmisijski = izracun_transmisijskih_gubitaka(prostorija, temperature_dict, katalog)
    
    # Izračun ventilacijskih gubitaka
    ventilacijski = izracun_ventilacijskih_gubitaka(prostorija, temperature_dict["vanjska"])
    
    # Izračun infiltracije
    infiltracija = izracun_infiltracije(prostorija, temperature_dict["vanjska"])    # Izračun osnovnih transmisijskih gubitaka (bez toplinskih mostova)
    osnovni_transmisijski_gubici = transmisijski["ukupno"] - transmisijski["toplinski_mostovi"]
    
    # Izračun toplinskih mostova kao postotak od osnovnih transmisijskih gubitaka
    toplinski_mostovi = procjena_toplinskih_mostova_postotkom(prostorija, osnovni_transmisijski_gubici)
    
    # Detaljniji izračun toplinskih mostova po tipu ako je potrebno
    # toplinski_mostovi_detalji = izracun_toplinskih_mostova_po_vrsti(prostorija, temperature_dict)
    
    # Ukupni gubici = osnovni transmisijski + toplinski mostovi + ventilacijski + infiltracija
    ukupno = osnovni_transmisijski_gubici + toplinski_mostovi + ventilacijski["snaga_gubitaka"] + infiltracija["snaga_gubitaka"]
    
    # Formiranje rezultata
    return {
        "transmisijski": transmisijski,
        "ventilacijski": ventilacijski,
        "infiltracija": infiltracija,
        "toplinski_mostovi": toplinski_mostovi,
        "ukupno": ukupno
    }

def izracunaj_toplinske_gubitke_etaze(model, etaza_id, grad=None):
    """
    Izračunava toplinske gubitke za cijelu etažu.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s podacima o prostorijama i etažama
    etaza_id : str
        ID etaže za koju se računaju gubici
    grad : str, optional
        Grad za koji se koristi projektna vanjska temperatura. Ako nije naveden, 
        koristi se zadana vrijednost u modelu.
        
    Returns:
    --------
    dict
        Rječnik s izračunatim gubicima po prostorijama i ukupno za etažu
    """
    # Dohvati prostorije na etaži
    prostorije = model.dohvati_prostorije_za_etazu(etaza_id)
    
    if not prostorije:
        return {"ukupno": 0.0, "prostorije": {}}
    
    # Izračunaj temperature za model
    try:
        temperature = izracunaj_temperature_za_model(model, grad)
    except Exception as e:
        st.error(f"Greška pri izračunu temperatura: {str(e)}")
        # Osiguraj minimalni set temperatura za nastavak rada
        temperature = {"vanjska": -20.0}
    
    # Inicijalizacija rezultata
    rezultati = {
        "prostorije": {},
        "ukupno": 0.0
    }    # Izračun gubitaka za svaku prostoriju
    for prostorija in prostorije:
        rezultat_prostorije = izracunaj_toplinske_gubitke_prostorije(prostorija, temperature)
        
        # Dohvat thermal bridges status za prikaz u UI
        toplinski_mostovi_ukljuceni = st.session_state.get("toplinski_mostovi", True)
        postotak_toplinskih_mostova = st.session_state.get("postotak_toplinskih_mostova", 15)
          # Priprema osnovnih podataka prostorije
        prostorija_rezultat = {
            "naziv": prostorija.naziv,
            "tip": prostorija.tip,            
            "povrsina": prostorija.povrsina,
            "temperatura": prostorija.temp_unutarnja,
            "grijana": prostorija.grijana,
            "gubici": rezultat_prostorije,
            "toplinski_mostovi_ukljuceni": toplinski_mostovi_ukljuceni,
            "toplinski_mostovi_postotak": postotak_toplinskih_mostova
        }
        
        # Dodaj informacije o zidovima ako postoje
        if hasattr(prostorija, 'zidovi_info'):
            prostorija_rezultat["zidovi_info"] = prostorija.zidovi_info
            
        # Dodaj informacije o prozorima ako postoje
        if hasattr(prostorija, 'prozori_info'):
            prostorija_rezultat["prozori_info"] = prostorija.prozori_info
            
        # Dodaj informacije o vratima ako postoje
        if hasattr(prostorija, 'vrata_info'):
            prostorija_rezultat["vrata_info"] = prostorija.vrata_info
            
        rezultati["prostorije"][prostorija.id] = prostorija_rezultat
        rezultati["ukupno"] += rezultat_prostorije["ukupno"]
    
    return rezultati

def izracunaj_toplinske_gubitke_zgrade(model, grad=None, elements_model=None, u_values_fallback=None, dodatni_parametri=None, temp_vanjska=None):
    """
    Izračunava toplinske gubitke za cijelu zgradu (sve etaže).
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s podacima o prostorijama i etažama
    grad : str, optional
        Grad za koji se koristi projektna vanjska temperatura. Ako nije naveden,
        koristi se zadana vrijednost u modelu.
    elements_model : BuildingElementsModel, optional
        Model građevinskih elemenata (ako postoji)
    u_values_fallback : dict, optional
        Rječnik s U-vrijednostima za fallback
    dodatni_parametri : dict, optional
        Dodatni parametri za proračun
    temp_vanjska : float, optional
        Eksplicitno zadana vanjska temperatura (ako nije zadana, koristi se temperatura grada)
        
    Returns:
    --------
    dict
        Rječnik s izračunatim gubicima po etažama i ukupno za zgradu
    """
    # Dohvati temperature za model
    try:
        temperature_dict = izracunaj_temperature_za_model(model, grad)
    except Exception as e:
        st.error(f"Greška pri izračunu temperatura za zgradu: {str(e)}")
        # Osiguraj minimalni set temperatura za nastavak rada
        temperature_dict = {"vanjska": -20.0}
      # Inicijalizacija rezultata
    rezultati = {
        "zgrada": {
            "etaze": {},
            "ukupno": 0.0,
            "ukupna_povrsina": 0.0,
            "prosjecno_po_m2": 0.0,
            "temperatura_vanjska": temperature_dict.get("vanjska", -20.0),  # Koristi defaultnu vrijednost ako ključ ne postoji
            "ukupni_gubici_kW": 0.0  # Dodano za prikaz u kW
        },
        "etaze": []  # Lista za kompatibilnost s UI prikazom
    }
      # Izračun gubitaka za svaku etažu
    for etaza in model.etaze:
        rezultat_etaze = izracunaj_toplinske_gubitke_etaze(model, etaza.id, grad)
          # Izračun ukupne površine prostorija na etaži
        povrsina_etaze = sum(
            model.dohvati_prostoriju(p_id).povrsina 
            for p_id in rezultat_etaze["prostorije"]
        )
        
        # Izračun ukupnog volumena prostorija na etaži
        volumen_etaze = sum(
            model.dohvati_prostoriju(p_id).povrsina * model.dohvati_prostoriju(p_id).get_actual_height(etaza)
            for p_id in rezultat_etaze["prostorije"]
        )
        
        etaza_info = {
            "naziv": etaza.naziv,
            "povrsina": povrsina_etaze,
            "volumen": volumen_etaze,
            "gubici": rezultat_etaze["ukupno"],
            "prostorije": rezultat_etaze["prostorije"]
        }
        
        rezultati["zgrada"]["etaze"][etaza.id] = etaza_info
        rezultati["etaze"].append(etaza_info)  # Dodaj u listu za UI prikaz
        
        rezultati["zgrada"]["ukupno"] += rezultat_etaze["ukupno"]
        rezultati["zgrada"]["ukupna_povrsina"] += povrsina_etaze
    
    # Izračun prosječnih gubitaka po m²
    if rezultati["zgrada"]["ukupna_povrsina"] > 0:
        rezultati["zgrada"]["prosjecno_po_m2"] = rezultati["zgrada"]["ukupno"] / rezultati["zgrada"]["ukupna_povrsina"]
    
    # Konverzija iz W u kW za prikaz
    rezultati["zgrada"]["ukupni_gubici_kW"] = rezultati["zgrada"]["ukupno"] / 1000.0
    
    return rezultati
