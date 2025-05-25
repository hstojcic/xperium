"""
Komponente korisničkog sučelja za upravljanje građevinskim elementima
"""

import streamlit as st
from .building_elements import inicijaliziraj_elemente, WallElements

def prikazi_manager_elemenata():
    """
    Prikazuje sučelje za upravljanje tipovima građevinskih elemenata
    
    Returns:
    --------
    BuildingElementsModel
        Model s definiranim tipovima elemenata
    """
    # Inicijaliziramo model
    model = inicijaliziraj_elemente()
    
    return model

def prikazi_vanjski_zid_s_elementima(zid, visina_prostorije, elements_model, key_prefix=""):
    """
    Prikazuje vanjski zid s prioritetno prozorima i opcionalno vratima.
    Actions (add/remove elements) are handled directly, followed by st.rerun().
    """
    if "elementi" not in zid or not isinstance(zid["elementi"], WallElements):
        zid["elementi"] = WallElements()
    
    # Inicijalizacija za vrata
    if "ima_vrata" not in zid:
        zid["ima_vrata"] = bool(zid["elementi"].vrata)
    
    # Inicijalizacija za prozore
    if "ima_prozor" not in zid:
        zid["ima_prozor"] = bool(zid["elementi"].prozori)
    
    needs_rerun = False
    # Kvačica za prozore
    ima_prozor_checkbox = st.checkbox(
        "Zid ima prozor",
        value=zid["ima_prozor"],
        key=f"{key_prefix}ima_prozor_{zid.get('id', 'default_zid')}"
    )
    if ima_prozor_checkbox != zid["ima_prozor"]:
        zid["ima_prozor"] = ima_prozor_checkbox
        needs_rerun = True
        # Ako se označi da ima prozor, a nema ga, dodaj prvi s liste ako postoji
        if zid["ima_prozor"] and not zid["elementi"].prozori and elements_model.prozori:
            prvi_prozor = elements_model.prozori[0]
            zid["elementi"].dodaj_prozor(prvi_prozor.id, prvi_prozor.naziv)
    
    # Kvačica za vrata
    ima_vrata_checkbox = st.checkbox(
        "Zid ima vrata", 
        value=zid["ima_vrata"],
        key=f"{key_prefix}ima_vrata_{zid.get('id', 'default_zid')}"
    )
    if ima_vrata_checkbox != zid["ima_vrata"]:
        zid["ima_vrata"] = ima_vrata_checkbox
        needs_rerun = True
        if zid["ima_vrata"] and not zid["elementi"].vrata and elements_model.vrata:
            # Filtriranje vrata za vanjski zid - trebaju biti VANJSKA VRATA (unutarnja=False)
            vanjska_vrata_lista = [v for v in elements_model.vrata if not v.unutarnja]
            if vanjska_vrata_lista:
                prva_vrata = vanjska_vrata_lista[0]
                zid["elementi"].dodaj_vrata(prva_vrata.id, prva_vrata.naziv)
            else:
                st.warning("Nema definiranih vanjskih vrata u elementima.")
    
    # Only rerun if there was a change that requires it
    if needs_rerun:
        st.rerun()
    
    # Prikaz prozora ako je označeno da ih zid ima
    if zid["ima_prozor"]:
        st.markdown("##### Prozori na zidu")
        # Osiguraj da postoji barem jedan prozor ako je označeno da zid ima prozor
        if not zid["elementi"].prozori and elements_model.prozori:
            prvi_prozor = elements_model.prozori[0]
            zid["elementi"].dodaj_prozor(prvi_prozor.id, prvi_prozor.naziv)
            needs_rerun = True
            
        if zid["elementi"].prozori:
            for i, prozor in enumerate(list(zid["elementi"].prozori)):
                zid_id_str = str(zid.get('id', 'default_zid'))
                prozor_id_str = str(prozor.id)
                unique_prozor_key_prefix = f"{key_prefix}prozor_{zid_id_str}_{prozor_id_str}"

                with st.container():
                    col1, col2, col3 = st.columns([4, 2, 1])
                    with col1:
                        opcije_prozora = {p.id: f"{p.naziv} ({p.sirna}x{p.visina}, U:{p.u_vrijednost})" for p in elements_model.prozori}
                        if not opcije_prozora:
                            st.warning("Nema definiranih tipova prozora.")
                            break 
                        
                        odabrani_tip_id = st.selectbox(
                            f"Tip prozora {i+1}:",
                            list(opcije_prozora.keys()),
                            format_func=lambda x: opcije_prozora[x],
                            index=list(opcije_prozora.keys()).index(prozor.tip_id) if prozor.tip_id in opcije_prozora else 0,
                            key=f"{unique_prozor_key_prefix}_tip"
                        )
                        if odabrani_tip_id != prozor.tip_id:
                            odabrani_prozor_tpl = next(p for p in elements_model.prozori if p.id == odabrani_tip_id)
                            prozor.tip_id = odabrani_tip_id
                            prozor.tip_naziv = odabrani_prozor_tpl.naziv
                            if prozor.koristiti_standardne_dimenzije:
                                prozor.sirna = odabrani_prozor_tpl.sirna
                                prozor.visina = odabrani_prozor_tpl.visina
                                prozor.u_vrijednost = odabrani_prozor_tpl.u_vrijednost
                                prozor.povrsina = odabrani_prozor_tpl.povrsina
                            st.rerun()
                
                    with col2:
                        koristi_standardne = st.checkbox(
                            "Standardne dimenzije",
                            value=prozor.koristiti_standardne_dimenzije,
                            key=f"{unique_prozor_key_prefix}_standardne"
                        )
                        if koristi_standardne != prozor.koristiti_standardne_dimenzije:
                            prozor.koristiti_standardne_dimenzije = koristi_standardne
                            if koristi_standardne:
                                odabrani_prozor_tpl = next(p for p in elements_model.prozori if p.id == prozor.tip_id)
                                prozor.sirna = odabrani_prozor_tpl.sirna
                                prozor.visina = odabrani_prozor_tpl.visina
                                prozor.u_vrijednost = odabrani_prozor_tpl.u_vrijednost
                                prozor.povrsina = odabrani_prozor_tpl.povrsina
                            st.rerun()

                    with col3:
                        if st.button("Ukloni", key=f"{unique_prozor_key_prefix}_ukloni"):
                            zid["elementi"].ukloni_prozor(prozor.id)
                            st.rerun()
                
                    if not prozor.koristiti_standardne_dimenzije:
                        col_dim1, col_dim2, col_dim3 = st.columns(3)
                        with col_dim1:
                            sirna = st.number_input("Širina [m]:", value=prozor.sirna, min_value=0.1, step=0.1, key=f"{unique_prozor_key_prefix}_sirina")
                            if sirna != prozor.sirna:
                                prozor.sirna = sirna
                                prozor.povrsina = sirna * prozor.visina
                                st.rerun()
                        with col_dim2:
                            visina = st.number_input("Visina [m]:", value=prozor.visina, min_value=0.1, step=0.1, key=f"{unique_prozor_key_prefix}_visina")
                            if visina != prozor.visina:
                                prozor.visina = visina
                                prozor.povrsina = prozor.sirna * visina
                                st.rerun()
                        with col_dim3:
                            st.metric(label="Površina", value=f"{(prozor.povrsina or 0.0):.2f} m²")
        else:
            st.info("Nema dodanih prozora na ovom zidu.")
        
        if st.button("+ Dodaj prozor", key=f"{key_prefix}dodaj_prozor_{zid.get('id', 'default_zid')}"):
            if elements_model.prozori:
                prvi_prozor_tpl = elements_model.prozori[0]
                zid["elementi"].dodaj_prozor(prvi_prozor_tpl.id, prvi_prozor_tpl.naziv)
                needs_rerun = True
            else:
                st.warning("Nema definiranih tipova prozora. Molimo, prvo definirajte tipove prozora na kartici 'Elementi'.")
    
    # Prikaz vrata ako je označeno da ih zid ima
    if zid["ima_vrata"]:
        st.markdown("##### Vrata na zidu")
        # Osiguraj da postoji barem jedna vrata ako je označeno da zid ima vrata
        if not zid["elementi"].vrata and elements_model.vrata:
            # Filtriranje vrata za vanjski zid - trebaju biti VANJSKA VRATA
            vanjska_vrata_lista = [v for v in elements_model.vrata if not v.unutarnja]
            if vanjska_vrata_lista:
                prva_vrata = vanjska_vrata_lista[0]
                zid["elementi"].dodaj_vrata(prva_vrata.id, prva_vrata.naziv)
                needs_rerun = True
        
        if zid["elementi"].vrata:
            for i, vrata_obj in enumerate(list(zid["elementi"].vrata)):
                zid_id_str = str(zid.get('id', 'default_zid'))
                vrata_id_str = str(vrata_obj.id)
                unique_vrata_key_prefix = f"{key_prefix}vrata_{zid_id_str}_{vrata_id_str}"

                with st.container():
                    col1, col2, col3 = st.columns([4, 2, 1])
                    with col1:
                        # Filtriramo samo vanjska vrata za prikaz u dropdownu
                        vanjska_vrata = [v for v in elements_model.vrata if not v.unutarnja]
                        opcije_vrata = {v.id: f"{v.naziv} ({v.sirna}x{v.visina}, U:{v.u_vrijednost})" for v in vanjska_vrata}
                        
                        if not opcije_vrata: 
                            st.warning("Nema definiranih tipova vanjskih vrata.")
                            break
                        
                        odabrani_tip_id_vrata = st.selectbox(
                            f"Tip vrata {i+1}:",
                            list(opcije_vrata.keys()),
                            format_func=lambda x: opcije_vrata[x],
                            index=list(opcije_vrata.keys()).index(vrata_obj.tip_id) if vrata_obj.tip_id in opcije_vrata else 0,
                            key=f"{unique_vrata_key_prefix}_tip"
                        )
                        if odabrani_tip_id_vrata != vrata_obj.tip_id:
                            odabrana_vrata_tpl = next((v for v in vanjska_vrata if v.id == odabrani_tip_id_vrata), None)
                            if odabrana_vrata_tpl:
                                vrata_obj.tip_id = odabrani_tip_id_vrata
                                vrata_obj.tip_naziv = odabrana_vrata_tpl.naziv
                                if vrata_obj.koristiti_standardne_dimenzije:
                                    vrata_obj.sirna = odabrana_vrata_tpl.sirna
                                    vrata_obj.visina = odabrana_vrata_tpl.visina
                                    vrata_obj.u_vrijednost = odabrana_vrata_tpl.u_vrijednost
                                    vrata_obj.povrsina = odabrana_vrata_tpl.povrsina
                                st.rerun()
                            else:
                                st.error("Odabrani tip vanjskih vrata nije pronađen.")

                    with col2:
                        koristi_standardne_vrata = st.checkbox(
                            "Standardne dimenzije",
                            value=vrata_obj.koristiti_standardne_dimenzije,
                            key=f"{unique_vrata_key_prefix}_standardne"
                        )
                        if koristi_standardne_vrata != vrata_obj.koristiti_standardne_dimenzije:
                            vrata_obj.koristiti_standardne_dimenzije = koristi_standardne_vrata
                            if koristi_standardne_vrata:
                                odabrana_vrata_tpl = next(v for v in elements_model.vrata if v.id == vrata_obj.tip_id)
                                vrata_obj.sirna = odabrana_vrata_tpl.sirna
                                vrata_obj.visina = odabrana_vrata_tpl.visina
                                vrata_obj.u_vrijednost = odabrana_vrata_tpl.u_vrijednost
                                vrata_obj.povrsina = odabrana_vrata_tpl.povrsina
                            st.rerun()
                    
                    with col3:
                        if st.button("Ukloni", key=f"{unique_vrata_key_prefix}_ukloni"):
                            zid["elementi"].ukloni_vrata(vrata_obj.id)
                            st.rerun()

                    if not vrata_obj.koristiti_standardne_dimenzije:
                        col_dim_v1, col_dim_v2, col_dim_v3 = st.columns(3)
                        with col_dim_v1:
                            sirna_v = st.number_input("Širina [m]:", value=vrata_obj.sirna, min_value=0.1, step=0.1, key=f"{unique_vrata_key_prefix}_sirina")
                            if sirna_v != vrata_obj.sirna:
                                vrata_obj.sirna = sirna_v
                                vrata_obj.povrsina = sirna_v * vrata_obj.visina
                                st.rerun()
                        with col_dim_v2:
                            visina_v = st.number_input("Visina [m]:", value=vrata_obj.visina, min_value=0.1, step=0.1, key=f"{unique_vrata_key_prefix}_visina")
                            if visina_v != vrata_obj.visina:
                                vrata_obj.visina = visina_v
                                vrata_obj.povrsina = vrata_obj.sirna * visina_v
                                st.rerun()
                        with col_dim_v3:
                            st.metric(label="Površina", value=f"{(vrata_obj.povrsina or 0.0):.2f} m²")
        else:
            st.info("Nema dodanih vrata na ovom zidu.")
        
        if st.button("+ Dodaj vrata", key=f"{key_prefix}dodaj_vrata_{zid.get('id', 'default_zid')}"):
            # Filtriranje vrata za vanjski zid - trebaju biti VANJSKA VRATA
            vanjska_vrata_lista = [v for v in elements_model.vrata if not v.unutarnja]
            if vanjska_vrata_lista:
                prva_vrata_tpl = vanjska_vrata_lista[0]
                zid["elementi"].dodaj_vrata(prva_vrata_tpl.id, prva_vrata_tpl.naziv)
                needs_rerun = True
            else:
                st.warning("Nema definiranih vanjskih vrata. Molimo, prvo definirajte tipove vanjskih vrata na kartici 'Elementi'.")

    ukupna_povrsina_prozora = zid["elementi"].izracunaj_ukupnu_povrsinu_prozora(elements_model)
    ukupna_povrsina_vrata = zid["elementi"].izracunaj_ukupnu_povrsinu_vrata(elements_model)
    
    zid["povrsina_prozora"] = ukupna_povrsina_prozora
    zid["povrsina_vrata"] = ukupna_povrsina_vrata
    
    ukupna_povrsina_zida = zid.get("duzina", 0) * visina_prostorije
    ukupna_povrsina_elemenata = ukupna_povrsina_prozora + ukupna_povrsina_vrata
    
    if ukupna_povrsina_elemenata > 0 and ukupna_povrsina_zida > 0:
        st.info(f"Ukupna površina elemenata: {ukupna_povrsina_elemenata:.2f} m² od {ukupna_povrsina_zida:.2f} m² ({ukupna_povrsina_elemenata/ukupna_povrsina_zida*100:.1f}%)")
    
    if ukupna_povrsina_elemenata > ukupna_povrsina_zida and ukupna_povrsina_zida > 0:
        st.warning(f"Upozorenje: Ukupna površina elemenata ({ukupna_povrsina_elemenata:.2f} m²) premašuje površinu zida ({ukupna_povrsina_zida:.2f} m²).")
    
    # Single rerun at the end if needed
    if needs_rerun:
        st.rerun()

def prikazi_unutarnji_zid_s_elementima(zid, visina_prostorije, elements_model, povezana_prostorija, key_prefix=""):
    """
    Prikazuje unutarnji zid s prioritetno vratima i opcionalno prozorima.
    Actions (add/remove elements) are handled directly, followed by st.rerun().
    """
    if "elementi" not in zid or not isinstance(zid["elementi"], WallElements):
        zid["elementi"] = WallElements()

    # Inicijalizacija za vrata (prioritet za unutarnje zidove)
    if "ima_vrata" not in zid:
        zid["ima_vrata"] = bool(zid["elementi"].vrata)
    
    # Inicijalizacija za prozore
    if "ima_prozor" not in zid:
        zid["ima_prozor"] = bool(zid["elementi"].prozori)

    needs_rerun_inner = False
    st.markdown(f"##### Elementi na zidu prema prostoriji: {povezana_prostorija.naziv}")
    
    # Kvačica za vrata (unutarnji zid)
    ima_vrata_checkbox_unutarnji = st.checkbox(
        "Zid ima vrata",
        value=zid["ima_vrata"],
        key=f"{key_prefix}ima_vrata_unutarnji_{zid.get('id', 'default_zid')}"
    )
    if ima_vrata_checkbox_unutarnji != zid["ima_vrata"]:
        zid["ima_vrata"] = ima_vrata_checkbox_unutarnji
        needs_rerun_inner = True
        if zid["ima_vrata"] and not zid["elementi"].vrata:
            # Filtriranje vrata za unutarnji zid - trebaju biti UNUTARNJA VRATA
            unutarnja_vrata_lista = [v for v in elements_model.vrata if v.unutarnja]
            if unutarnja_vrata_lista:
                prva_vrata = unutarnja_vrata_lista[0]
                zid["elementi"].dodaj_vrata(prva_vrata.id, prva_vrata.naziv)
            else:
                st.warning("Nema definiranih unutarnjih vrata u elementima.")
    
    # Kvačica za prozore (unutarnji zid)
    ima_prozor_checkbox_unutarnji = st.checkbox(
        "Zid ima prozor",
        value=zid["ima_prozor"],
        key=f"{key_prefix}ima_prozor_unutarnji_{zid.get('id', 'default_zid')}"
    )
    if ima_prozor_checkbox_unutarnji != zid["ima_prozor"]:
        zid["ima_prozor"] = ima_prozor_checkbox_unutarnji
        needs_rerun_inner = True
        if zid["ima_prozor"] and not zid["elementi"].prozori and elements_model.prozori:
            prvi_prozor_tpl = elements_model.prozori[0] # Pretpostavka da su svi prozori OK za unutarnji zid
            zid["elementi"].dodaj_prozor(prvi_prozor_tpl.id, prvi_prozor_tpl.naziv)
    
    # Rerun only once after initial checkbox changes
    if needs_rerun_inner:
        st.rerun()
            
    # Prikaz vrata ako je označeno
    if zid["ima_vrata"]:
        st.markdown("##### Vrata na unutarnjem zidu")
        # Osiguraj da postoji barem jedna vrata ako je označeno da zid ima vrata
        if not zid["elementi"].vrata:
            # Filtriranje vrata za unutarnji zid - trebaju biti UNUTARNJA VRATA
            unutarnja_vrata_lista = [v for v in elements_model.vrata if v.unutarnja]
            if unutarnja_vrata_lista:
                prva_vrata = unutarnja_vrata_lista[0]
                zid["elementi"].dodaj_vrata(prva_vrata.id, prva_vrata.naziv)
                needs_rerun_inner = True
                
        if zid["elementi"].vrata:
            for i, vrata_obj in enumerate(list(zid["elementi"].vrata)):
                zid_id_str = str(zid.get('id', 'default_zid'))
                vrata_id_str = str(vrata_obj.id)
                unique_vrata_key_prefix = f"{key_prefix}vrata_unutarnji_{zid_id_str}_{vrata_id_str}"
                
                with st.container():
                    col1, col2, col3 = st.columns([4, 2, 1])
                    with col1:
                        # Filtriramo samo unutarnja vrata za prikaz u dropdownu
                        unutarnja_vrata = [v for v in elements_model.vrata if v.unutarnja]
                        opcije_vrata = {v.id: f"{v.naziv} ({v.sirna}x{v.visina}, U:{v.u_vrijednost})" for v in unutarnja_vrata}
                        
                        if not opcije_vrata:
                            st.warning("Nema definiranih tipova unutarnjih vrata.")
                            break
                            
                        odabrani_tip_id_vrata = st.selectbox(
                            f"Tip vrata {i+1}:",
                            list(opcije_vrata.keys()),
                            format_func=lambda x: opcije_vrata[x],
                            index=list(opcije_vrata.keys()).index(vrata_obj.tip_id) if vrata_obj.tip_id in opcije_vrata else 0,
                            key=f"{unique_vrata_key_prefix}_tip"
                        )
                        if odabrani_tip_id_vrata != vrata_obj.tip_id:
                            odabrana_vrata_tpl = next((v for v in unutarnja_vrata if v.id == odabrani_tip_id_vrata), None)
                            if odabrana_vrata_tpl:
                                vrata_obj.tip_id = odabrani_tip_id_vrata
                                vrata_obj.tip_naziv = odabrana_vrata_tpl.naziv
                                if vrata_obj.koristiti_standardne_dimenzije:
                                    vrata_obj.sirna = odabrana_vrata_tpl.sirna
                                    vrata_obj.visina = odabrana_vrata_tpl.visina
                                    vrata_obj.u_vrijednost = odabrana_vrata_tpl.u_vrijednost
                                    vrata_obj.povrsina = odabrana_vrata_tpl.povrsina
                                st.rerun()
                            else:
                                st.error("Odabrani tip unutarnjih vrata nije pronađen.")

                    with col2:
                        koristi_standardne_vrata = st.checkbox(
                            "Standardne dimenzije",
                            value=vrata_obj.koristiti_standardne_dimenzije,
                            key=f"{unique_vrata_key_prefix}_standardne"
                        )
                        if koristi_standardne_vrata != vrata_obj.koristiti_standardne_dimenzije:
                            vrata_obj.koristiti_standardne_dimenzije = koristi_standardne_vrata
                            if koristi_standardne_vrata:
                                odabrana_vrata_tpl = next((v for v in unutarnja_vrata if v.id == vrata_obj.tip_id), None)
                                if odabrana_vrata_tpl:
                                    vrata_obj.sirna = odabrana_vrata_tpl.sirna
                                    vrata_obj.visina = odabrana_vrata_tpl.visina
                                    vrata_obj.u_vrijednost = odabrana_vrata_tpl.u_vrijednost
                                    vrata_obj.povrsina = odabrana_vrata_tpl.povrsina
                            st.rerun()
                    
                    with col3:
                        if st.button("Ukloni", key=f"{unique_vrata_key_prefix}_ukloni"):
                            zid["elementi"].ukloni_vrata(vrata_obj.id)
                            st.rerun()

                    if not vrata_obj.koristiti_standardne_dimenzije:
                        col_dim_v1, col_dim_v2, col_dim_v3 = st.columns(3)
                        with col_dim_v1:
                            sirna_v = st.number_input("Širina [m]:", value=vrata_obj.sirna, min_value=0.1, step=0.1, key=f"{unique_vrata_key_prefix}_sirina")
                            if sirna_v != vrata_obj.sirna:
                                vrata_obj.sirna = sirna_v
                                vrata_obj.povrsina = sirna_v * vrata_obj.visina
                                st.rerun()
                        with col_dim_v2:
                            visina_v = st.number_input("Visina [m]:", value=vrata_obj.visina, min_value=0.1, step=0.1, key=f"{unique_vrata_key_prefix}_visina")
                            if visina_v != vrata_obj.visina:
                                vrata_obj.visina = visina_v
                                vrata_obj.povrsina = vrata_obj.sirna * visina_v
                                st.rerun()
                        with col_dim_v3:
                            st.metric(label="Površina", value=f"{(vrata_obj.povrsina or 0.0):.2f} m²")
        else:
            st.info("Nema dodanih vrata na ovom zidu.")
        
        if st.button("+ Dodaj vrata", key=f"{key_prefix}dodaj_vrata_unutarnji_{zid.get('id', 'default_zid')}"):
            # Filtriranje vrata za unutarnji zid - trebaju biti UNUTARNJA VRATA
            unutarnja_vrata_lista = [v for v in elements_model.vrata if v.unutarnja]
            if unutarnja_vrata_lista:
                prva_vrata_tpl = unutarnja_vrata_lista[0]
                zid["elementi"].dodaj_vrata(prva_vrata_tpl.id, prva_vrata_tpl.naziv)
                st.rerun()
            else:
                st.warning("Nema definiranih unutarnjih vrata. Molimo, prvo definirajte tipove unutarnjih vrata na kartici 'Elementi'.")

    # Prikaz prozora ako je označeno
    if zid["ima_prozor"]:
        st.markdown("##### Prozori na unutarnjem zidu")
        # Osiguraj da postoji barem jedan prozor ako je označeno da zid ima prozor
        if not zid["elementi"].prozori and elements_model.prozori:
            prvi_prozor = elements_model.prozori[0]
            zid["elementi"].dodaj_prozor(prvi_prozor.id, prvi_prozor.naziv)
            needs_rerun_inner = True
            
        if zid["elementi"].prozori:
            for i, prozor in enumerate(list(zid["elementi"].prozori)):
                zid_id_str = str(zid.get('id', 'default_zid'))
                prozor_id_str = str(prozor.id)
                unique_prozor_key_prefix = f"{key_prefix}prozor_unutarnji_{zid_id_str}_{prozor_id_str}"

                with st.container():
                    col1, col2, col3 = st.columns([4, 2, 1])
                    with col1:
                        opcije_prozora = {p.id: f"{p.naziv} ({p.sirna}x{p.visina}, U:{p.u_vrijednost})" for p in elements_model.prozori}
                        if not opcije_prozora:
                            st.warning("Nema definiranih tipova prozora.")
                            break
                        
                        odabrani_tip_id = st.selectbox(
                            f"Tip prozora {i+1}:",
                            list(opcije_prozora.keys()),
                            format_func=lambda x: opcije_prozora[x],
                            index=list(opcije_prozora.keys()).index(prozor.tip_id) if prozor.tip_id in opcije_prozora else 0,
                            key=f"{unique_prozor_key_prefix}_tip"
                        )
                        if odabrani_tip_id != prozor.tip_id:
                            odabrani_prozor_tpl = next(p for p in elements_model.prozori if p.id == odabrani_tip_id)
                            prozor.tip_id = odabrani_tip_id
                            prozor.tip_naziv = odabrani_prozor_tpl.naziv
                            if prozor.koristiti_standardne_dimenzije:
                                prozor.sirna = odabrani_prozor_tpl.sirna
                                prozor.visina = odabrani_prozor_tpl.visina
                                prozor.u_vrijednost = odabrani_prozor_tpl.u_vrijednost
                                prozor.povrsina = odabrani_prozor_tpl.povrsina
                            st.rerun()
                    with col2:
                        koristi_standardne = st.checkbox(
                            "Standardne dimenzije",
                            value=prozor.koristiti_standardne_dimenzije,
                            key=f"{unique_prozor_key_prefix}_standardne"
                        )
                        if koristi_standardne != prozor.koristiti_standardne_dimenzije:
                            prozor.koristiti_standardne_dimenzije = koristi_standardne
                            if koristi_standardne:
                                odabrani_prozor_tpl = next(p for p in elements_model.prozori if p.id == prozor.tip_id)
                                prozor.sirna = odabrani_prozor_tpl.sirna
                                prozor.visina = odabrani_prozor_tpl.visina
                                prozor.u_vrijednost = odabrani_prozor_tpl.u_vrijednost
                                prozor.povrsina = odabrani_prozor_tpl.povrsina
                            st.rerun()
                    with col3:
                        if st.button("Ukloni", key=f"{unique_prozor_key_prefix}_ukloni"):
                            zid["elementi"].ukloni_prozor(prozor.id)
                            st.rerun()
        
                    if not prozor.koristiti_standardne_dimenzije:
                        col_dim1, col_dim2, col_dim3 = st.columns(3)
                        with col_dim1:
                            sirna = st.number_input("Širina [m]:", value=prozor.sirna, min_value=0.1, step=0.1, key=f"{unique_prozor_key_prefix}_sirina")
                            if sirna != prozor.sirna:
                                prozor.sirna = sirna
                                prozor.povrsina = sirna * prozor.visina
                                st.rerun()
                        with col_dim2:
                            visina = st.number_input("Visina [m]:", value=prozor.visina, min_value=0.1, step=0.1, key=f"{unique_prozor_key_prefix}_visina")
                            if visina != prozor.visina:
                                prozor.visina = visina
                                prozor.povrsina = prozor.sirna * visina
                                st.rerun()
                        with col_dim3:
                            st.metric(label="Površina", value=f"{(prozor.povrsina or 0.0):.2f} m²")
        else:
            st.info("Nema dodanih prozora na ovom zidu.")
        
        if st.button("+ Dodaj prozor (unutarnji)", key=f"{key_prefix}dodaj_prozor_unutarnji_{zid.get('id', 'default_zid')}"):
            if elements_model.prozori:
                prvi_prozor_tpl = elements_model.prozori[0]
                zid["elementi"].dodaj_prozor(prvi_prozor_tpl.id, prvi_prozor_tpl.naziv)
                needs_rerun_inner = True
            else:
                st.warning("Nema definiranih tipova prozora. Molimo, prvo definirajte tipove prozora na kartici 'Elementi'.")

    ukupna_povrsina_prozora = zid["elementi"].izracunaj_ukupnu_povrsinu_prozora(elements_model)
    ukupna_povrsina_vrata = zid["elementi"].izracunaj_ukupnu_povrsinu_vrata(elements_model)
    
    zid["povrsina_prozora"] = ukupna_povrsina_prozora
    zid["povrsina_vrata"] = ukupna_povrsina_vrata
    
    ukupna_povrsina_zida = zid.get("duzina", 0) * visina_prostorije
    ukupna_povrsina_elemenata = ukupna_povrsina_prozora + ukupna_povrsina_vrata
    
    if ukupna_povrsina_elemenata > 0 and ukupna_povrsina_zida > 0:
        st.info(f"Ukupna površina elemenata: {ukupna_povrsina_elemenata:.2f} m² od {ukupna_povrsina_zida:.2f} m² ({ukupna_povrsina_elemenata/ukupna_povrsina_zida*100:.1f}%)")
    
    if ukupna_povrsina_elemenata > ukupna_povrsina_zida and ukupna_povrsina_zida > 0:
        st.warning(f"Upozorenje: Ukupna površina elemenata ({ukupna_povrsina_elemenata:.2f} m²) premašuje površinu zida ({ukupna_povrsina_zida:.2f} m²).")
    
    # Single rerun at the end if needed
    if needs_rerun_inner:
        st.rerun()
