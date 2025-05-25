"""
Modul za prikaz rezultata proračuna toplinskih gubitaka u UI-u.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def format_power(power_w, precision=0):
    """Formatira snagu iz W u kW i prikazuje s određenom preciznošću."""
    if abs(power_w) >= 1000:
        return f"{power_w/1000:.2f} kW"
    else:
        return f"{int(power_w)} W"

def get_formatted_room_display(prostorija_rezultat):
    """
    Dohvaća formatirani prikaz broja prostorije koristeći dinamičko formatiranje.
    
    Parameters:
    -----------
    prostorija_rezultat : dict
        Rječnik s rezultatima za prostoriju
        
    Returns:
    --------
    str
        Formatirani prikaz prostorije
    """
    # Try to get the formatted room number from the model
    if st.session_state.get('heat_loss_model') and prostorija_rezultat.get('id'):
        model = st.session_state.heat_loss_model
        try:
            prostorija = model.dohvati_prostoriju(prostorija_rezultat['id'])
            if prostorija:
                formatted_number = prostorija.get_formatted_broj_prostorije()
                if formatted_number:
                    return f"{formatted_number}. {prostorija_rezultat['naziv']}"
        except Exception:
            pass  # Fall back to default behavior
    
    # Fallback to old behavior if model is not available
    if 'broj_prostorije' in prostorija_rezultat and prostorija_rezultat['broj_prostorije']:
        return f"{prostorija_rezultat['broj_prostorije']}. {prostorija_rezultat['naziv']}"
    else:
        return prostorija_rezultat['naziv']

def prikaz_rezultata_prostorije(prostorija_rezultat, temperatura_vanjska):
    """
    Prikazuje rezultate za jednu prostoriju.
    
    Parameters:
    -----------
    prostorija_rezultat : dict
        Rječnik s rezultatima za prostoriju
    temperatura_vanjska : float
        Vanjska projektna temperatura
    """    
    # Container s obrubom za osnovne podatke o prostoriji i pregled toplinskih gubitaka
    with st.container(border=True):
        # Prvi red: broj prostorije, naziv, površina, volumen
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Show room number in first column using dynamic formatting
            formatted_broj = None
            if st.session_state.get('heat_loss_model') and prostorija_rezultat.get('id'):
                model = st.session_state.heat_loss_model
                try:
                    prostorija = model.dohvati_prostoriju(prostorija_rezultat['id'])
                    if prostorija:
                        formatted_broj = prostorija.get_formatted_broj_prostorije()
                except Exception:
                    pass
                    
            if not formatted_broj and 'broj_prostorije' in prostorija_rezultat:
                formatted_broj = prostorija_rezultat['broj_prostorije']
                
            if formatted_broj:
                st.metric("Broj prostorije", formatted_broj)
            else:
                st.metric("Broj prostorije", "Nije dodijeljen")
        
        with col2:
            # Show room name in second column
            st.metric("Naziv prostorije", prostorija_rezultat['naziv'])
        
        with col3:
            st.metric("Površina", f"{prostorija_rezultat['povrsina']:.2f} m²")
            
        with col4:
            # Calculate exact volume from room area and floor height
            if 'volumen' in prostorija_rezultat:
                volumen_text = f"{prostorija_rezultat['volumen']:.2f} m³"
            else:
                # Get the etaza for the room to get the height
                etaza = None
                if prostorija_rezultat.get('etaza_id') and st.session_state.get('heat_loss_model'):
                    etaza = st.session_state.heat_loss_model.dohvati_etazu(prostorija_rezultat.get('etaza_id'))
                  # Use the etaza height or fallback to a standard value
                visina = etaza.visina_etaze if etaza else 2.5
                calculated_volume = prostorija_rezultat['povrsina'] * visina
                volumen_text = f"{calculated_volume:.2f} m³"
            st.metric("Volumen", volumen_text)
        
        # Drugi red: status, temperatura, gubici
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            # Dodaj status grijanja prostorije
            grijana_status = prostorija_rezultat.get('grijana', True)
            status_text = "Grijana" if grijana_status else "Negrijana" 
            st.metric("Status prostorije", status_text)
            
        with col2:
            st.metric("Unutarnja projektna temperatura", f"{prostorija_rezultat['temperatura']:.1f} °C")
            
        with col3:
            st.metric("Ukupni toplinski gubici", format_power(prostorija_rezultat['gubici']['ukupno'], precision=2))
            
        with col4:
            specifican_gubitak = prostorija_rezultat['gubici']['ukupno']/prostorija_rezultat['povrsina'] if prostorija_rezultat['povrsina'] > 0 else 0
            st.metric("Ukupni specifični toplinski gubici", f"{specifican_gubitak:.1f} W/m²")
        
        # Podjela gubitaka
        gubici = prostorija_rezultat['gubici']
        
        # Priprema podataka za grafikon
        # Transmisijski su samo osnovni transmisijski gubici bez toplinskih mostova
        transmisijski = gubici['transmisijski']['ukupno'] - gubici['toplinski_mostovi']
        ventilacijski = gubici['ventilacijski']['snaga_gubitaka']
        infiltracija = gubici['infiltracija']['snaga_gubitaka']
        toplinski_mostovi = gubici['toplinski_mostovi']
        # Get transmisijski data for window and door losses
        trans_gubici = gubici['transmisijski']
        
        # Get window and door losses values
        prozori_gubici = trans_gubici.get('prozori', 0)
        vrata_gubici = trans_gubici.get('vrata', 0)
        
        # Ensure we have numeric values for window and door losses
        # Handle case when prozori_gubici or vrata_gubici might be dictionaries
        if isinstance(prozori_gubici, dict):
            if 'ukupno' in prozori_gubici:
                prozori_gubici = prozori_gubici['ukupno']
            else:
                prozori_gubici = 0
                
        if isinstance(vrata_gubici, dict):
            if 'ukupno' in vrata_gubici:
                vrata_gubici = vrata_gubici['ukupno']
            else:
                vrata_gubici = 0
                  # Ensure we have numeric values        prozori_gubici = float(prozori_gubici) if prozori_gubici is not None else 0
        vrata_gubici = float(vrata_gubici) if vrata_gubici is not None else 0
        
        # Pregled toplinskih gubitaka
        st.markdown("### Pregled toplinskih gubitaka")
        
        # Tabela s gubicima
        gubici_df = pd.DataFrame({
            "Vrsta gubitaka": [
                "Transmisijski", 
                "Prozori",
                "Vrata",
                "Ventilacijski", 
                "Infiltracija", 
                "Toplinski mostovi", 
                "Ukupno"
            ],
            "Snaga": [
                format_power(transmisijski),
                format_power(prozori_gubici),
                format_power(vrata_gubici),
                format_power(ventilacijski),
                format_power(infiltracija),
                format_power(toplinski_mostovi),
                format_power(gubici['ukupno'])
            ],
            "Udio [%]": [
                f"{transmisijski/gubici['ukupno']*100:.1f}%",
                f"{prozori_gubici/gubici['ukupno']*100:.1f}%",
                f"{vrata_gubici/gubici['ukupno']*100:.1f}%",
                f"{ventilacijski/gubici['ukupno']*100:.1f}%",
                f"{infiltracija/gubici['ukupno']*100:.1f}%",
                f"{toplinski_mostovi/gubici['ukupno']*100:.1f}%",
                "100.0%"
            ],
            "Po površini [W/m²]": [
                f"{transmisijski/prostorija_rezultat['povrsina']:.1f}",
                f"{prozori_gubici/prostorija_rezultat['povrsina']:.1f}",
                f"{vrata_gubici/prostorija_rezultat['povrsina']:.1f}",
                f"{ventilacijski/prostorija_rezultat['povrsina']:.1f}",
                f"{infiltracija/prostorija_rezultat['povrsina']:.1f}",
                f"{toplinski_mostovi/prostorija_rezultat['povrsina']:.1f}",
                f"{gubici['ukupno']/prostorija_rezultat['povrsina']:.1f}"
            ],
            "Vrsta izmjene": [
                "Toplinski gubitak 🔴" if transmisijski > 0 else "Toplinski dobitak 🟢" if transmisijski < 0 else "Nema izmjene 🔵",
                "Toplinski gubitak 🔴" if prozori_gubici > 0 else "Toplinski dobitak 🟢" if prozori_gubici < 0 else "Nema izmjene 🔵",
                "Toplinski gubitak 🔴" if vrata_gubici > 0 else "Toplinski dobitak 🟢" if vrata_gubici < 0 else "Nema izmjene 🔵",
                "Toplinski gubitak 🔴" if ventilacijski > 0 else "Toplinski dobitak 🟢" if ventilacijski < 0 else "Nema izmjene 🔵",
                "Toplinski gubitak 🔴" if infiltracija > 0 else "Toplinski dobitak 🟢" if infiltracija < 0 else "Nema izmjene 🔵",
                "Toplinski gubitak 🔴" if toplinski_mostovi > 0 else "Toplinski dobitak 🟢" if toplinski_mostovi < 0 else "Nema izmjene 🔵",
                "Toplinski gubitak 🔴" if gubici['ukupno'] > 0 else "Toplinski dobitak 🟢" if gubici['ukupno'] < 0 else "Nema izmjene 🔵"
            ]
        })
        
        st.dataframe(gubici_df, hide_index=True)
    # Detailed transmission losses section
    with st.container(border=True):
        st.markdown("### Detaljni prikaz transmisijskih gubitaka")
        # Display transmission losses as separate containers for each group
        # First row: Pod and Strop
        row1_col1, row1_col2 = st.columns(2)
        
        # Pod (floor) losses
        if 'pod' in trans_gubici:
            with row1_col1:
                with st.container(border=True):
                    st.subheader("Pod")
                    pod_gubici = trans_gubici['pod']
                    pod_info = {}
                    # Format losses using format_power function
                    pod_info["Toplinski gubici"] = format_power(pod_gubici)
                    
                    # Default values if needed
                    povrsina_poda = None
                    u_vrijednost_poda = None
                    debljina_poda = None
                    
                    # Try getting floor data from multiple sources
                    pod_info_data = prostorija_rezultat.get('pod_info', {})
                    trans_pod_info = trans_gubici.get('pod_info', {})
                    
                    # 1. Try from pod_info
                    if isinstance(pod_info_data, dict):
                        if 'povrsina' in pod_info_data:
                            try:
                                povrsina_poda = float(pod_info_data['povrsina'])
                            except (ValueError, TypeError): pass
                        
                        if 'u_vrijednost' in pod_info_data:
                            try:
                                u_vrijednost_poda = float(pod_info_data['u_vrijednost'])
                            except (ValueError, TypeError): pass
                            
                        if 'debljina' in pod_info_data:
                            try:
                                debljina_poda = float(pod_info_data['debljina'])
                            except (ValueError, TypeError): pass
                    
                    # 2. Try from trans_gubici.pod_info
                    if isinstance(trans_pod_info, dict):
                        if povrsina_poda is None and trans_pod_info.get('povrsina') is not None:
                            try:
                                povrsina_poda = float(trans_pod_info['povrsina'])
                            except (ValueError, TypeError): pass
                        
                        if u_vrijednost_poda is None and trans_pod_info.get('u_vrijednost') is not None:
                            try:
                                u_vrijednost_poda = float(trans_pod_info['u_vrijednost'])
                            except (ValueError, TypeError): pass
                            
                        if debljina_poda is None and trans_pod_info.get('debljina') is not None:
                            try:
                                debljina_poda = float(trans_pod_info['debljina'])
                            except (ValueError, TypeError): pass
                    
                    # 3. If still no area, calculate from room data
                    if povrsina_poda is None and 'povrsina' in prostorija_rezultat:
                        povrsina_poda = prostorija_rezultat['povrsina']
                        
                    # 4. Use defaults for remaining None values                    if u_vrijednost_poda is None:
                        u_vrijednost_poda = 0.35  # Default U-value for floors
                        
                    if debljina_poda is None:
                        debljina_poda = 30.0  # Default thickness in cm                    # Add values to display
                      # Add specific heat loss immediately after toplinski gubici
                    if povrsina_poda is not None and povrsina_poda > 0:
                        pod_info["Specifični toplinski gubici"] = f"{pod_gubici/povrsina_poda:.1f} W/m²"
                        
                    if povrsina_poda is not None:
                        pod_info["Površina"] = f"{povrsina_poda:.2f} m²"
                    
                    # Display as metrics
                    cols = st.columns(len(pod_info))
                    for i, (key, value) in enumerate(pod_info.items()):
                        cols[i].metric(key, value)
                    
                    # If we have floor type info
                    if prostorija_rezultat.get('pod_tip'):
                        st.info(f"Tip poda: {prostorija_rezultat['pod_tip']}")
        
        # Strop (ceiling) losses
        if 'strop' in trans_gubici:
            with row1_col2:
                with st.container(border=True):
                    st.subheader("Strop")
                    strop_gubici = trans_gubici['strop']
                    strop_info = {}
                    # Format losses using format_power function
                    strop_info["Toplinski gubici"] = format_power(strop_gubici)
                    
                    # Default values if needed
                    povrsina_stropa = None
                    u_vrijednost_stropa = None
                    debljina_stropa = None
                    
                    # Try getting ceiling data from multiple sources
                    strop_info_data = prostorija_rezultat.get('strop_info', {})
                    trans_strop_info = trans_gubici.get('strop_info', {})
                    
                    # 1. Try from strop_info
                    if isinstance(strop_info_data, dict):
                        if 'povrsina' in strop_info_data:
                            try:
                                povrsina_stropa = float(strop_info_data['povrsina'])
                            except (ValueError, TypeError): pass
                        
                        if 'u_vrijednost' in strop_info_data:
                            try:
                                u_vrijednost_stropa = float(strop_info_data['u_vrijednost'])
                            except (ValueError, TypeError): pass
                            
                        if 'debljina' in strop_info_data:
                            try:
                                debljina_stropa = float(strop_info_data['debljina'])
                            except (ValueError, TypeError): pass
                    
                    # 2. Try from trans_gubici.strop_info
                    if isinstance(trans_strop_info, dict):
                        if povrsina_stropa is None and trans_strop_info.get('povrsina') is not None:
                            try:
                                povrsina_stropa = float(trans_strop_info['povrsina'])
                            except (ValueError, TypeError): pass
                        
                        if u_vrijednost_stropa is None and trans_strop_info.get('u_vrijednost') is not None:
                            try:
                                u_vrijednost_stropa = float(trans_strop_info['u_vrijednost'])
                            except (ValueError, TypeError): pass
                            
                        if debljina_stropa is None and trans_strop_info.get('debljina') is not None:
                            try:
                                debljina_stropa = float(trans_strop_info['debljina'])
                            except (ValueError, TypeError): pass
                    
                    # 3. If still no area, calculate from room data
                    if povrsina_stropa is None and 'povrsina' in prostorija_rezultat:
                        povrsina_stropa = prostorija_rezultat['povrsina']
                        
                    # 4. Use defaults for remaining None values
                    if u_vrijednost_stropa is None:
                        u_vrijednost_stropa = 0.30  # Default U-value for ceilings
                        
                    if debljina_stropa is None:
                        debljina_stropa = 25.0  # Default thickness in cm
                    
                    # Add values to display
                      # Add specific heat loss immediately after toplinski gubici
                    if povrsina_stropa is not None and povrsina_stropa > 0:
                        strop_info["Specifični toplinski gubici"] = f"{strop_gubici/povrsina_stropa:.1f} W/m²"
                        
                    if povrsina_stropa is not None:
                        strop_info["Površina"] = f"{povrsina_stropa:.2f} m²"
                    
                    # Display as metrics
                    cols = st.columns(len(strop_info))
                    for i, (key, value) in enumerate(strop_info.items()):
                        cols[i].metric(key, value)
                    
                    # If we have ceiling type info
                    if prostorija_rezultat.get('strop_tip'):
                        st.info(f"Tip stropa: {prostorija_rezultat['strop_tip']}")
          # Second row: Vanjski and Unutarnji zidovi
        row2_col1, row2_col2 = st.columns(2)
        
        # Initialize wall data lists
        vanjski_zidovi = []
        unutarnji_zidovi = []        # Jednostavno prikupljanje podataka za zidove - samo osnovna klasifikacija
        if 'zidovi' in trans_gubici and trans_gubici['zidovi']:# Provjeri postoje li zidovi u modelu i dohvati direktnu vezu na njih
            if st.session_state.get('heat_loss_model') and prostorija_rezultat.get('id'):
                model = st.session_state.heat_loss_model
                try:
                    prostorija = model.dohvati_prostoriju(prostorija_rezultat['id'])
                    if prostorija and hasattr(prostorija, 'zidovi'):
                        # Ako imamo definicije zidova u modelu, ali ne u rezultatima, direktno ih koristimo
                        if not prostorija_rezultat.get('zidovi_info') and len(prostorija.zidovi) > 0:
                            # Kreirajmo zidovi_info strukturu ako ne postoji
                            prostorija_rezultat['zidovi_info'] = {}
                            
                            for zid in prostorija.zidovi:
                                zid_id = zid.get('id')
                                if zid_id and zid_id in trans_gubici['zidovi']:
                                    # Kopirajmo informacije o zidu iz modela u rezultate
                                    prostorija_rezultat['zidovi_info'][zid_id] = {
                                        'tip': zid.get('tip', 'vanjski'),
                                        'povrsina': zid.get('povrsina', zid.get('duzina', 0) * (prostorija.visina or 2.5)),
                                        'u_vrijednost': zid.get('u_vrijednost', 0.3),  # Default vrijednost ako nije definirana
                                        'orijentacija': zid.get('orijentacija'),
                                        'povezana_prostorija_id': zid.get('povezana_prostorija_id')
                                    }
                except Exception as e:
                    pass  # Ignoriraj pogreške i nastavi dalje
            
            # Prođi kroz sve zidove u rezultatima
            for zid_id, gubici_zida in trans_gubici['zidovi'].items():
                # Provjeri postoji li dodatna informacija o zidu
                if prostorija_rezultat.get('zidovi_info') and zid_id in prostorija_rezultat.get('zidovi_info', {}):
                    zid_info = prostorija_rezultat['zidovi_info'][zid_id]                    # Osnovni podaci zida
                    zid_data = {
                        "ID": zid_id,
                        "Toplinski gubici": format_power(gubici_zida),
                    }
                    
                    # Dodaj površinu i U-vrijednost ako postoji
                    if zid_info.get('povrsina'):
                        zid_data["Površina"] = f"{zid_info.get('povrsina'):.2f} m²"
                    if zid_info.get('u_vrijednost'):
                        zid_data["U [W/m²K]"] = f"{zid_info.get('u_vrijednost'):.2f}"
                      # Jednostavna klasifikacija zidova prema tipu
                    tip_zida = zid_info.get('tip', 'nepoznat')
                    
                    if not tip_zida or tip_zida == 'nepoznat':
                        # Pokušaj odrediti tip zida na temelju ostalih podataka
                        if zid_info.get('orijentacija'):
                            tip_zida = "vanjski"
                        elif zid_info.get('povezana_prostorija_id'):
                            tip_zida = "prema_prostoriji"
                        
                    # Klasifikacija zida
                    if tip_zida == "vanjski":
                        vanjski_zidovi.append(zid_data)
                    elif tip_zida == "prema_prostoriji" or tip_zida == "prema_negrijanom":
                        unutarnji_zidovi.append(zid_data)
                    else:
                        # Ako tip zida nije jasno definiran, stavljamo ga u kategoriju vanjskih zidova
                        vanjski_zidovi.append(zid_data)
                else:                # Skip addition of debug info for missing wall details
                      # Pokušaj alternativno klasificirati zidove direktno iz podataka o gubicima                    # Pretpostavljamo da je vanjski zid ako ne možemo utvrditi drugačije
                    zid_data = {
                        "ID": zid_id,
                        "Toplinski gubici": format_power(gubici_zida),
                    }
                    
                    # Dodatne informacije o zidu koje možemo dobiti iz drugih izvora
                    if st.session_state.get('heat_loss_model'):
                        model = st.session_state.heat_loss_model
                        # Pokušajmo naći informacije o zidu kroz model
                        for etaza in model.etaze:
                            for prost in etaza.prostorije:
                                for z in prost.zidovi:
                                    if z.get('id') == zid_id:
                                        # Našli smo zid u modelu
                                        if 'povrsina' in z:
                                            zid_data["Površina"] = f"{z.get('povrsina'):.2f} m²"
                                        elif 'duzina' in z and prost.visina:
                                            povrsina = z.get('duzina') * prost.visina
                                            zid_data["Površina"] = f"{povrsina:.2f} m²"
                                        
                                        if 'u_vrijednost' in z:
                                            zid_data["U [W/m²K]"] = f"{z.get('u_vrijednost'):.2f}"                # Pokušaj odrediti tip zida iz zidovi_info koji se dodao u transmisijski.py
                    if 'zidovi_info' in prostorija_rezultat and zid_id in prostorija_rezultat.get('zidovi_info', {}):
                        # Prioritet - koristimo podatak o tipu zida iz zidovi_info
                        tip_zida = prostorija_rezultat['zidovi_info'][zid_id].get('tip', 'vanjski')
                    elif isinstance(gubici_zida, dict) and 'tip' in gubici_zida:
                        # Ako imamo direktno informaciju o tipu u gubicima
                        tip_zida = gubici_zida.get('tip')
                    elif 'povezani_zidovi' in prostorija_rezultat and zid_id in prostorija_rezultat.get('povezani_zidovi', []):
                        # Ako je u listi povezanih zidova, to je unutarnji zid
                        tip_zida = "prema_prostoriji"
                    else:
                        # Inače pretpostavljamo da je vanjski zid
                        # Dodatna provjera - ako imamo modifikatore zida koji upućuju na tip
                        # Pretpostavljamo da vanjski zidovi mogu imati orijentaciju
                        if isinstance(gubici_zida, dict) and gubici_zida.get('orijentacija'):
                            tip_zida = "vanjski"
                        elif prostorija_rezultat.get('id') and isinstance(gubici_zida, dict) and gubici_zida.get('povezana_prostorija_id'):
                            tip_zida = "prema_prostoriji"
                        else:
                            # Provjera temeljem najboljeg nagađanja
                            # Zidovi s većim gubicima obično su vanjski
                            gubici_vrijednost = float(gubici_zida) if isinstance(gubici_zida, (int, float, str)) else 0
                            tip_zida = "vanjski" if gubici_vrijednost > 100 else "prema_prostoriji"
                      # Klasifikacija zida na temelju pretpostavljenog tipa
                    if tip_zida == "prema_prostoriji" or tip_zida == "prema_negrijanom":
                        unutarnji_zidovi.append(zid_data)
                    else:
                        vanjski_zidovi.append(zid_data)
                              # Add additional wall info from zidovi_info to the data if available
                        if 'zidovi_info' in prostorija_rezultat and zid_id in prostorija_rezultat.get('zidovi_info', {}):
                            wall_info = prostorija_rezultat['zidovi_info'][zid_id]
                            if 'povrsina' in wall_info and 'Površina' not in zid_data:
                                zid_data["Površina"] = f"{wall_info['povrsina']:.2f} m²"
                            if 'u_vrijednost' in wall_info and 'U [W/m²K]' not in zid_data:
                                zid_data["U [W/m²K]"] = f"{wall_info['u_vrijednost']:.2f}"
                            if 'orijentacija' in wall_info and wall_info['orijentacija']:
                                zid_data["Orijentacija"] = wall_info['orijentacija']
        
        # Ako imamo zidove u transmisijskim gubicima ali nisu klasificirani, pokušajmo ih klasificirati
        if 'zidovi' in trans_gubici and trans_gubici['zidovi'] and not (vanjski_zidovi or unutarnji_zidovi):
            # Može se dogoditi da imamo zidove, ali nisu ispravno klasificirani
            # Podijelit ćemo ih nasumično/po pola kao vanjski/unutarnji da se ipak nešto prikaže
            zid_ids = list(trans_gubici['zidovi'].keys())
            half_index = len(zid_ids) // 2
            
            # Prvu polovicu smatramo vanjskim zidovima
            for zid_id in zid_ids[:half_index]:
                gubici_zida = trans_gubici['zidovi'][zid_id]
                zid_data = {
                    "ID": zid_id,
                    "Toplinski gubici": format_power(gubici_zida if isinstance(gubici_zida, (int, float)) else 0)
                }
                vanjski_zidovi.append(zid_data)
                
            # Drugu polovicu smatramo unutarnjim zidovima
            for zid_id in zid_ids[half_index:]:
                gubici_zida = trans_gubici['zidovi'][zid_id]
                zid_data = {
                    "ID": zid_id,
                    "Toplinski gubici": format_power(gubici_zida if isinstance(gubici_zida, (int, float)) else 0)
                }
                unutarnji_zidovi.append(zid_data)
          # Display vanjski zidovi (external walls)
        with row2_col1:
            with st.container(border=True):
                st.subheader("Vanjski zidovi")
                if vanjski_zidovi:                    # Calculate aggregate values for all external walls
                    ukupni_gubici = 0
                    for zid_data in vanjski_zidovi:
                        if "Toplinski gubici" in zid_data:
                            gubici_str = zid_data["Toplinski gubici"]
                            if " kW" in gubici_str:
                                ukupni_gubici += float(gubici_str.replace(" kW", "")) * 1000
                            else:
                                ukupni_gubici += float(gubici_str.replace(" W", ""))
                        elif "Toplinski gubici [W]" in zid_data:
                            ukupni_gubici += float(zid_data["Toplinski gubici [W]"])
                    
                    # Calculate total area if available
                    ukupna_povrsina = 0
                    has_area = False
                    for zid_data in vanjski_zidovi:
                        if "Površina" in zid_data:
                            ukupna_povrsina += float(zid_data["Površina"].replace(" m²", ""))
                            has_area = True
                    
                    # Calculate average U-value if available
                    ukupna_u_vrijednost = 0
                    u_count = 0
                    for zid_data in vanjski_zidovi:
                        if "U [W/m²K]" in zid_data:
                            ukupna_u_vrijednost += float(zid_data["U [W/m²K]"])
                            u_count += 1                    # Display summary metrics
                    vanjski_info = {}
                    vanjski_info["Toplinski gubici"] = format_power(ukupni_gubici)
                    # Add specific heat loss as the second item
                    if has_area and ukupna_povrsina > 0:
                        vanjski_info["Specifični toplinski gubici"] = f"{ukupni_gubici/ukupna_povrsina:.1f} W/m²"
                    vanjski_info["Broj vanjskih zidova"] = f"{len(vanjski_zidovi)}"
                    if has_area:
                        vanjski_info["Površina"] = f"{ukupna_povrsina:.2f} m²"
                    
                    # Display as metrics
                    cols = st.columns(len(vanjski_info))
                    for i, (key, value) in enumerate(vanjski_info.items()):
                        cols[i].metric(key, value)
                    # Display only summary information without detailed breakdown
                    # No detailed view for external walls
                else:
                    st.info("Nema vanjskih zidova.")
          # Display unutarnji zidovi (internal walls)
        with row2_col2:
            with st.container(border=True):
                st.subheader("Unutarnji zidovi")
                if unutarnji_zidovi:                    # Calculate aggregate values for all internal walls
                    ukupni_gubici = 0
                    for zid_data in unutarnji_zidovi:
                        if "Toplinski gubici" in zid_data:
                            gubici_str = zid_data["Toplinski gubici"]
                            if " kW" in gubici_str:
                                ukupni_gubici += float(gubici_str.replace(" kW", "")) * 1000
                            else:
                                ukupni_gubici += float(gubici_str.replace(" W", ""))
                        elif "Toplinski gubici [W]" in zid_data:
                            ukupni_gubici += float(zid_data["Toplinski gubici [W]"])
                    
                    # Calculate total area if available
                    ukupna_povrsina = 0
                    has_area = False
                    for zid_data in unutarnji_zidovi:
                        if "Površina" in zid_data:
                            ukupna_povrsina += float(zid_data["Površina"].replace(" m²", ""))
                            has_area = True
                    
                    # Calculate average U-value if available
                    ukupna_u_vrijednost = 0
                    u_count = 0
                    for zid_data in unutarnji_zidovi:
                        if "U [W/m²K]" in zid_data:
                            ukupna_u_vrijednost += float(zid_data["U [W/m²K]"])
                            u_count += 1
                      # Display summary metrics
                    unutarnji_info = {}
                    unutarnji_info["Toplinski gubici"] = format_power(ukupni_gubici)
                    # Add specific heat loss as the second item
                    if has_area and ukupna_povrsina > 0:
                        unutarnji_info["Specifični toplinski gubici"] = f"{ukupni_gubici/ukupna_povrsina:.1f} W/m²"
                    unutarnji_info["Broj unutarnjih zidova"] = f"{len(unutarnji_zidovi)}"
                    if has_area:
                        unutarnji_info["Površina"] = f"{ukupna_povrsina:.2f} m²"
                    
                    # Display as metrics
                    cols = st.columns(len(unutarnji_info))
                    for i, (key, value) in enumerate(unutarnji_info.items()):
                        cols[i].metric(key, value)
                    # Display only summary information without detailed breakdown
                    # No detailed view for internal walls
                else:
                    st.info("Nema unutarnjih zidova.")
            # Third row: Vrata and Prozori
        row3_col1, row3_col2 = st.columns(2)
          # Vrata (doors) losses
        with row3_col1:
            with st.container(border=True):
                st.subheader("Vrata")
                
                _gubici_vrata_raw = trans_gubici.get('vrata', 0)
                if isinstance(_gubici_vrata_raw, dict):
                    _gubici_vrata_val = _gubici_vrata_raw.get('ukupno', 0)
                else:
                    _gubici_vrata_val = _gubici_vrata_raw
                
                try:
                    gubici_vrata_numeric = float(_gubici_vrata_val)
                except (ValueError, TypeError):
                    gubici_vrata_numeric = 0.0
                
                vrata_info_data = prostorija_rezultat.get('vrata_info', {})
                trans_vrata_info = trans_gubici.get('vrata_info', {})
                
                broj_vrata_direct = vrata_info_data.get('broj_vrata', 0) if isinstance(vrata_info_data, dict) else 0
                broj_vrata_trans = trans_vrata_info.get('broj_vrata', 0) if isinstance(trans_vrata_info, dict) else 0
                broj_vrata = max(broj_vrata_direct, broj_vrata_trans)
                
                has_vrata = (
                    broj_vrata > 0 or 
                    gubici_vrata_numeric > 0 or
                    (isinstance(vrata_info_data, dict) and vrata_info_data.get('ukupna_povrsina', 0) > 0) or
                    (isinstance(trans_vrata_info, dict) and trans_vrata_info.get('ukupna_povrsina', 0) > 0)
                )
                
                if has_vrata:
                    vrata_info = {}
                    # Format door losses using format_power function
                    vrata_info["Toplinski gubici"] = format_power(gubici_vrata_numeric)
                    
                    povrsina_final = None

                    # 1. Try direct_info (prostorija_rezultat.vrata_info)
                    if isinstance(vrata_info_data, dict):
                        if vrata_info_data.get('ukupna_povrsina') is not None:
                            try:
                                p_direct = float(vrata_info_data['ukupna_povrsina'])
                                if p_direct >= 0: # Accept 0 or positive
                                    povrsina_final = p_direct
                            except (ValueError, TypeError): pass
                    
                    # 2. Try trans_info (trans_gubici.vrata_info)
                    if isinstance(trans_vrata_info, dict):
                        if povrsina_final is None and trans_vrata_info.get('ukupna_povrsina') is not None:
                            try:
                                p_trans = float(trans_vrata_info['ukupna_povrsina'])
                                if p_trans >= 0: # Accept 0 or positive
                                    povrsina_final = p_trans
                            except (ValueError, TypeError): pass

                    # 3. If area still None (no explicit area found), and doors exist, use default area calculation
                    if povrsina_final is None and broj_vrata > 0:
                        povrsina_final = broj_vrata * 1.85 

                    # Calculate specific heat loss (per m²)
                    if povrsina_final is not None and povrsina_final > 0:
                        specifični_gubici = gubici_vrata_numeric / povrsina_final
                        vrata_info["Specifični toplinski gubici"] = f"{specifični_gubici:.1f} W/m²"
                    
                    vrata_info["Broj vrata"] = f"{broj_vrata}"
                    if povrsina_final is not None and povrsina_final > 0:
                        vrata_info["Površina"] = f"{povrsina_final:.2f} m²"
                    
                    if vrata_info: # Should always be true if has_vrata, due to Gubici and Broj
                        cols = st.columns(len(vrata_info))
                        for i, (key, value) in enumerate(vrata_info.items()):
                            cols[i].metric(key, value)
                else:
                    st.info("Nema vrata.")
          # Prozori (windows) losses
        with row3_col2:
            with st.container(border=True):
                st.subheader("Prozori")
                
                _gubici_prozori_raw = trans_gubici.get('prozori', 0)
                if isinstance(_gubici_prozori_raw, dict):
                    _gubici_prozori_val = _gubici_prozori_raw.get('ukupno', 0)
                else:
                    _gubici_prozori_val = _gubici_prozori_raw
                
                try:
                    gubici_prozori_numeric = float(_gubici_prozori_val)
                except (ValueError, TypeError):
                    gubici_prozori_numeric = 0.0
                
                prozori_info_data = prostorija_rezultat.get('prozori_info', {})
                trans_prozori_info = trans_gubici.get('prozori_info', {})
                
                broj_prozora_direct = prozori_info_data.get('broj_prozora', 0) if isinstance(prozori_info_data, dict) else 0
                broj_prozora_trans = trans_prozori_info.get('broj_prozora', 0) if isinstance(trans_prozori_info, dict) else 0
                broj_prozora = max(broj_prozora_direct, broj_prozora_trans)
                
                has_prozore = (
                    broj_prozora > 0 or 
                    gubici_prozori_numeric > 0 or
                    (isinstance(prozori_info_data, dict) and prozori_info_data.get('ukupna_povrsina', 0) > 0) or
                    (isinstance(trans_prozori_info, dict) and trans_prozori_info.get('ukupna_povrsina', 0) > 0)
                )
                
                if has_prozore:
                    prozori_info = {}
                    # Format window losses using format_power function
                    prozori_info["Toplinski gubici"] = format_power(gubici_prozori_numeric)

                    povrsina_final = None

                    # 1. Try direct_info (prostorija_rezultat.prozori_info)
                    if isinstance(prozori_info_data, dict):
                        if prozori_info_data.get('ukupna_povrsina') is not None:
                            try:
                                p_direct = float(prozori_info_data['ukupna_povrsina'])
                                if p_direct >= 0: # Accept 0 or positive
                                    povrsina_final = p_direct
                            except (ValueError, TypeError): pass
                    
                    # 2. Try trans_info (trans_gubici.prozori_info)
                    if isinstance(trans_prozori_info, dict):
                        if povrsina_final is None and trans_prozori_info.get('ukupna_povrsina') is not None:
                            try:
                                p_trans = float(trans_prozori_info['ukupna_povrsina'])
                                if p_trans >= 0: # Accept 0 or positive
                                    povrsina_final = p_trans
                            except (ValueError, TypeError): pass

                    # 3. If area still None (no explicit area found), and windows exist, use default area
                    if povrsina_final is None and broj_prozora > 0:
                        povrsina_final = broj_prozora * 1.44

                    # Calculate specific heat loss (per m²)
                    if povrsina_final is not None and povrsina_final > 0:
                        specifični_gubici = gubici_prozori_numeric / povrsina_final
                        prozori_info["Specifični toplinski gubici"] = f"{specifični_gubici:.1f} W/m²"

                    prozori_info["Broj prozora"] = f"{broj_prozora}"
                    
                    if povrsina_final is not None and povrsina_final > 0:
                        prozori_info["Površina"] = f"{povrsina_final:.2f} m²"

                    if prozori_info:
                        cols = st.columns(len(prozori_info))
                        for i, (key, value) in enumerate(prozori_info.items()):
                            cols[i].metric(key, value)
                else:
                    st.info("Nema prozora.")      # Add spacing between sections
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Outer container for both ventilation and infiltration
    with st.container(border=True):
        # Detailed ventilation losses header inside the container
        st.markdown("### Detaljni prikaz ventilacijskih gubitaka")
        
        # Organize in a grid layout similar to transmission losses
        row1_col1, row1_col2 = st.columns(2)                # Ventilacijski gubici
        with row1_col1:
            with st.container(border=True):
                st.subheader("Ventilacija")
                vent_gubici = gubici['ventilacijski']
                vent_info = {}                
                vent_info["Toplinski gubici"] = format_power(vent_gubici.get('snaga_gubitaka', 0))
                
                # Add specific heat loss immediately after toplinski gubici
                if 'snaga_gubitaka' in vent_gubici and prostorija_rezultat['povrsina'] > 0:
                    vent_info["Specifični toplinski gubici"] = f"{vent_gubici.get('snaga_gubitaka', 0)/prostorija_rezultat['povrsina']:.1f} W/m²"
                
                vent_info["Protok zraka"] = f"{vent_gubici.get('protok_zraka', 0):.0f} m³/h"
                vent_info["Broj izmjena"] = f"{vent_gubici.get('izmjene_zraka', 0):.1f} h⁻¹"
                
                # Additional ventilation parameters if available
                if 'temperatura_dobavnog_zraka' in vent_gubici:
                    vent_info["Temperatura dobave [°C]"] = f"{vent_gubici.get('temperatura_dobavnog_zraka', 20):.1f}"
                    
                # Display as metrics in one row with appropriate columns
                metric_cols = st.columns(len(vent_info))
                for i, (key, value) in enumerate(vent_info.items()):
                    metric_cols[i].metric(key, value)                # Ne prikazujemo detaljne podatke o ventilaciji                # Infiltracijski gubici
        with row1_col2:
            with st.container(border=True):
                st.subheader("Infiltracija")
                inf_gubici = gubici['infiltracija']
                inf_info = {}
                inf_info["Toplinski gubici"] = format_power(inf_gubici.get('snaga_gubitaka', 0))
                  # Add specific heat loss immediately after toplinski gubici
                if 'snaga_gubitaka' in inf_gubici and prostorija_rezultat['povrsina'] > 0:
                    inf_info["Specifični toplinski gubici"] = f"{inf_gubici.get('snaga_gubitaka', 0)/prostorija_rezultat['povrsina']:.1f} W/m²"
                
                inf_info["Protok zraka"] = f"{inf_gubici.get('protok_zraka', 0):.0f} m³/h"
                inf_info["Broj izmjena"] = f"{inf_gubici.get('faktor_infiltracije', 0):.1f} h⁻¹"
                
                # Additional infiltration parameters if available
                if 'izlozenost_vjetru' in inf_gubici:
                    inf_info["Izloženost vjetru"] = inf_gubici.get('izlozenost_vjetru', 'Srednja')
                      # Display as metrics in one row
                metric_cols = st.columns(len(inf_info))
                for i, (key, value) in enumerate(inf_info.items()):
                    metric_cols[i].metric(key, value)
      
    # Thermal bridges section - using column layout to position it on the left side of the screen
    col1, col2 = st.columns(2)
    with col1:
        # Outer container for thermal bridges (only spans half the width because it's inside col1)
        with st.container(border=True):
            # Header for thermal bridges section
            st.markdown("### Detaljni prikaz toplinskih mostova")
            
            # Inner container for the actual thermal bridges content
            with st.container(border=True):
                st.subheader("Toplinski mostovi")
                # Get thermal bridges data
                toplinski_mostovi = gubici['toplinski_mostovi']
                # Check if thermal bridges are explicitly included/excluded in calculation
                toplinski_mostovi_ukljuceni = prostorija_rezultat.get('toplinski_mostovi_ukljuceni', True)
                if toplinski_mostovi_ukljuceni:
                    # Create detailed thermal bridges information
                    tm_info = {}
                    # Format thermal bridge losses using format_power function
                    tm_info["Toplinski gubici"] = format_power(toplinski_mostovi)
                    # Calculate specific heat loss
                    if prostorija_rezultat['povrsina'] > 0:
                        tm_info["Specifični toplinski gubici"] = f"{toplinski_mostovi/prostorija_rezultat['povrsina']:.1f} W/m²"
                    # Get the percentage used for thermal bridges calculation
                    if prostorija_rezultat.get('toplinski_mostovi_postotak'):
                        tm_info["Postotak"] = f"{prostorija_rezultat.get('toplinski_mostovi_postotak', 0):.0f}%"
                    
                    # Display as metrics
                    cols = st.columns(len(tm_info))
                    for i, (key, value) in enumerate(tm_info.items()):
                        cols[i].metric(key, value)
                else:
                    # Show message only when thermal bridges are explicitly disabled in the UI
                    st.info("Toplinski mostovi nisu uzeti u obzir u proračunu.")
                # Ne prikazujemo detaljne podatke o toplinskim mostovima

def prikaz_rezultata_etaze(etaza_rezultat, temperatura_vanjska):
    """
    Prikazuje rezultate za jednu etažu.
    
    Parameters:
    -----------
    etaza_rezultat : dict
        Rječnik s rezultatima za etažu
    temperatura_vanjska : float
        Vanjska projektna temperatura
    """      # Osnovni podaci o etaži
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Naziv etaže", etaza_rezultat['naziv'])
    with col2:
        st.metric("Ukupna površina", f"{etaza_rezultat['povrsina']:.2f} m²")
    with col3:
        # Display volume if available, otherwise calculate it
        if 'volumen' in etaza_rezultat and etaza_rezultat['volumen'] is not None:
            st.metric("Ukupni volumen", f"{etaza_rezultat['volumen']:.2f} m³")
        else:
            # Fallback calculation if volume not available in data
            st.metric("Ukupni volumen", "N/A")
    with col4:
        st.metric("Ukupni toplinski gubici", format_power(etaza_rezultat['gubici'], 2))
    with col5:
        # Always display the specific heat loss metric, even if it's 0
        if etaza_rezultat['povrsina'] > 0:
            specific_losses = etaza_rezultat['gubici'] / etaza_rezultat['povrsina']
            st.metric("Ukupni specifični toplinski gubici", f"{specific_losses:.1f} W/m²")
        else:
            # Show the metric even when there's no calculation (povrsina = 0)
            st.metric("Ukupni specifični toplinski gubici", "0.0 W/m²")
    
    # Prikaz prostorija u etaži
    if etaza_rezultat['prostorije']:
        st.subheader("Pregled prostorija")
        
        prostorije_data = []
          # Provjera je li 'prostorije' rječnik (dict) ili lista (list)
        if isinstance(etaza_rezultat['prostorije'], dict):        # Ako je rječnik, iterirajmo kroz njegove parove ključ-vrijednost
            for p_result in etaza_rezultat['prostorije'].values():                
                gubici_ukupno = p_result['gubici']['ukupno']
                room_display = get_formatted_room_display(p_result)
                prostorije_data.append({
                    "Prostorija": room_display,
                    "Površina": f"{p_result['povrsina']:.2f} m²",
                    "Temperatura [°C]": f"{p_result['temperatura']:.1f}",
                    "Toplinski gubici [W]": f"{gubici_ukupno:.0f}",
                    "Specifični toplinski gubici": f"{gubici_ukupno/p_result['povrsina']:.1f} W/m²"
                })
        elif isinstance(etaza_rezultat['prostorije'], list):
            # Ako je lista, iterirajmo kroz listu
            for p_result in etaza_rezultat['prostorije']:
                gubici_ukupno = p_result['gubici']['ukupno']
                room_display = get_formatted_room_display(p_result)
                
                prostorije_data.append({
                    "Prostorija": room_display,
                    "Površina": f"{p_result['povrsina']:.2f} m²",
                    "Temperatura [°C]": f"{p_result['temperatura']:.1f}",
                    "Toplinski gubici [W]": f"{gubici_ukupno:.0f}",
                    "Specifični toplinski gubici": f"{gubici_ukupno/p_result['povrsina']:.1f} W/m²"
                })
        
        prostorije_df = pd.DataFrame(prostorije_data)
        st.dataframe(prostorije_df, hide_index=True) # Osigurano da je hide_index=True
          # Detaljni prikaz za svaku prostoriju
        st.subheader("Detaljni prikaz prostorija")
          # Slično kao prije, prilagođavamo se formatu podataka (rječnik ili lista)
        if isinstance(etaza_rezultat['prostorije'], dict):
            for p_id, p_result in etaza_rezultat['prostorije'].items():
                room_title = get_formatted_room_display(p_result)
                with st.expander(room_title):
                    prikaz_rezultata_prostorije(p_result, temperatura_vanjska)
        elif isinstance(etaza_rezultat['prostorije'], list):
            for p_result in etaza_rezultat['prostorije']:
                room_title = get_formatted_room_display(p_result)
                with st.expander(room_title):
                    prikaz_rezultata_prostorije(p_result, temperatura_vanjska)
        
        # Graphs were removed as per user request
    else:
        st.warning("Nema podataka o prostorijama na ovoj etaži.")

def prikaz_rezultata_zgrade(zgrada_rezultat):
    """
    Prikazuje rezultate za cijelu zgradu.
    
    Parameters:
    -----------
    zgrada_rezultat : dict
        Rječnik s rezultatima za zgradu
    """
    st.title("Rezultati proračuna toplinskih gubitaka")
    
    # Osnovna kartica s podacima o zgradi
    with st.container():
        st.markdown("""
        <style>
        .data-card {
            border: 1px solid #f0f2f6;
            border-radius: 5px;
            padding: 10px;
            background-color: #f8f9fa;
        }
        .highlight-metric {
            color: #1e88e5;
            font-weight: bold;
            font-size: 1.2em;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.metric("Ukupna površina", f"{zgrada_rezultat['ukupna_povrsina']:.2f} m²")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.metric("Ukupni gubici", format_power(zgrada_rezultat['ukupno'], 2))
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col3:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            prosjecni_gubici = zgrada_rezultat['prosjecno_po_m2']
            # Add color indicator based on average heat loss value
            if prosjecni_gubici < 50:
                metric_description = "Vrlo dobro"
                delta_color = "normal"  # Green for good values
            elif prosjecni_gubici < 80:
                metric_description = "Dobro"
                delta_color = "normal"  # Green for good values
            elif prosjecni_gubici < 120:
                metric_description = "Prosječno"
                delta_color = "off"  # Neutral for average values
            else:
                metric_description = "Visoko"
                delta_color = "inverse"  # Red for high values
            
            st.metric(
                "Prosječni gubici", 
                f"{prosjecni_gubici:.0f} W/m²", 
                delta=metric_description,
                delta_color=delta_color
            )
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Vanjska temperatura i dodatne informacije
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Vanjska projektna temperatura**: {zgrada_rezultat['temperatura_vanjska']:.1f} °C")
    
    # Etaže
    if zgrada_rezultat['etaze']:        # Prikaz etaža u tablici
        etaze_data = []
        for e_id, e_result in zgrada_rezultat['etaze'].items():
            udio_postotak = f"{(e_result['gubici']/zgrada_rezultat['ukupno']*100):.1f}%" if zgrada_rezultat['ukupno'] > 0 else "0.0%"
            etaze_data.append({
                "Etaža": e_result['naziv'],
                "Ukupna površina": f"{e_result['povrsina']:.2f} m²",
                "Ukupni volumen": f"{e_result.get('volumen', 0):.2f} m³",
                "Toplinski gubici [W]": f"{e_result['gubici']:.0f}",
                "Udio [%]": udio_postotak,
                "Ukupni specifični toplinski gubici": f"{e_result['gubici']/e_result['povrsina']:.1f} W/m²" if e_result['povrsina'] > 0 else "N/A"
            })
        
        etaze_df = pd.DataFrame(etaze_data)
        st.dataframe(etaze_df, hide_index=True)
    else:
        st.warning("Nema podataka o etažama u ovoj zgradi.")