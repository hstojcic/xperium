"""
Modul koji sadrži funkcije za prikaz i upravljanje zidovima u UI-u.
"""

import streamlit as st
from ..constants import ORIJENTACIJE
from ..utils.validators import validate_number
from ..models.elementi.building_elements_model import BuildingElementsModel, inicijaliziraj_elemente # Added import

def prikaz_zidova(prostorija, model, on_zid_selected=None):
    """
    Prikazuje pregled svih zidova u prostoriji.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija čiji se zidovi prikazuju
    model : MultiRoomModel
        Model u kojem se nalazi prostor                # Prilagođeni prikaz ID-a ovisno o tipu zida (plavi badge za fizičke zidove)
                if tip_zida_naziv == "prema_prostoriji" and zid.get("fizicki_zid_id"):
                    st.markdown(f"**{naziv_za_prikaz}** ({dimenzije})")
                    st.info(f"ID: {zid_id_display}")
                else:
                    st.markdown(f"**{naziv_za_prikaz}** ({dimenzije})")
                    st.caption(f"ID: {zid_id_display}")   on_zid_selected : function
        Funkcija koja se poziva kad se odabere zid
    """
    if not prostorija.zidovi:
        st.info(f"Prostorija '{prostorija.naziv}' nema definiranih zidova.")
        return None
    st.subheader("Zidovi prostorije")
      # Razdvoji zidove na vanjske i unutarnje
    vanjski_zidovi = []
    unutarnji_zidovi = []
    
    for i, zid in enumerate(prostorija.zidovi):
        tip_zida = zid.get("tip", "nepoznat")
        duzina = zid.get("duzina", 0.0)
        fizicki_zid_id = zid.get("fizicki_zid_id")
        povezana_prostorija_id = zid.get("povezana_prostorija_id")
        povezani_zid_id = zid.get("povezani_zid_id")
        
        # Standardizirani format opisa
        if tip_zida == "vanjski":
            orijentacija = zid.get("orijentacija", "nepoznata")
            opis = f"Vanjski zid | {orijentacija}"
            vanjski_zidovi.append({
                "Br.": i + 1,
                "Tip": opis,
                "Dužina": f"{duzina:.2f} m",
                "Zid ID": zid.get("id")
            })
        elif tip_zida == "prema_prostoriji":
            povezana_prostorija = model.dohvati_prostoriju(povezana_prostorija_id) if povezana_prostorija_id else None
            naziv_povezane = povezana_prostorija.naziv if povezana_prostorija else "nepoznata"
            opis = f"Prema prostoriji | {naziv_povezane}"
            
            # Dodaj fizički ID zida kao zasebnu kolonu umjesto u opis
            if fizicki_zid_id:
                opis += f" | Fiz.ID: {fizicki_zid_id}"
            
            unutarnji_zidovi.append({
                "Br.": i + 1,
                "Tip": opis,
                "Dužina": f"{duzina:.2f} m",
                "Zid ID": zid.get("id")
            })
        elif tip_zida == "prema_negrijanom":
            opis = "Prema negrijanom prostoru"
            unutarnji_zidovi.append({
                "Br.": i + 1,
                "Tip": opis,
                "Dužina": f"{duzina:.2f} m",
                "Zid ID": zid.get("id")
            })
        # Check if the wall has internal wall indicators in its ID
        elif 'unutarnji' in zid.get('id', '').lower() or 'int' in zid.get('id', '').lower() or 'prema' in zid.get('id', '').lower():
            opis = "Unutarnji zid"
            unutarnji_zidovi.append({
                "Br.": i + 1,
                "Tip": opis,
                "Dužina": f"{duzina:.2f} m",
                "Zid ID": zid.get("id")
            })
        # Check if the wall is connected to another wall or room
        elif povezana_prostorija_id or povezani_zid_id or fizicki_zid_id:
            opis = "Unutarnji zid"
            if povezana_prostorija_id:
                povezana_prostorija = model.dohvati_prostoriju(povezana_prostorija_id)
                if povezana_prostorija:
                    opis += f" | Prema: {povezana_prostorija.naziv}"
            
            unutarnji_zidovi.append({
                "Br.": i + 1,
                "Tip": opis,
                "Dužina": f"{duzina:.2f} m",
                "Zid ID": zid.get("id")
            })
        else:
            opis = "Nepoznat tip zida"
            # By default, unknown walls go to external walls
            vanjski_zidovi.append({
                "Br.": i + 1,
                "Tip": opis,
                "Dužina": f"{duzina:.2f} m",
                "Zid ID": zid.get("id")
            })
      # Prikaži vanjske zidove
    if vanjski_zidovi:
        st.markdown("### Vanjski zidovi")
        st.dataframe(vanjski_zidovi, hide_index=True, use_container_width=True)
    else:
        st.info("Nema vanjskih zidova.")
    
    # Divider između vanjskih i unutarnjih zidova
    st.markdown("---")
    
    # Prikaži unutarnje zidove
    if unutarnji_zidovi:
        st.markdown("### Unutarnji zidovi")
        st.dataframe(unutarnji_zidovi, hide_index=True, use_container_width=True)
    else:
        st.info("Nema unutarnjih zidova.")
        
    # Spoji sve podatke za implementaciju odabira
    data = vanjski_zidovi + unutarnji_zidovi
    
    # Implementacija odabira zida
    if on_zid_selected:
        st.write("Odaberi zid za uređivanje:")
        # Create mapping from display index to actual wall index
        index_mapping = {}
        counter = 0
        
        # Map all external walls first
        for i, zid in enumerate(prostorija.zidovi):
            tip_zida = zid.get("tip", "nepoznat")
            if tip_zida == "vanjski":
                index_mapping[counter] = i
                counter += 1
        
        # Then map all internal walls
        for i, zid in enumerate(prostorija.zidovi):
            tip_zida = zid.get("tip", "nepoznat")
            if tip_zida != "vanjski":
                index_mapping[counter] = i
                counter += 1
        
        # Generate display options
        zid_opcije = [f"{d['Br']}. {d['Tip']} ({d['Dužina']})" for d in data]
        selected_display_index = st.selectbox("Zid:", range(len(zid_opcije)), format_func=lambda i: zid_opcije[i])
        
        # Map the display index to the actual wall index
        selected_index = index_mapping[selected_display_index]
        odabrani_zid = prostorija.zidovi[selected_index]
        on_zid_selected(odabrani_zid)
        
        return odabrani_zid
        
    return None

def forma_za_dodavanje_zida(prostorija, model, callback_nakon_dodavanja=None):
    """
    Prikazuje formu za dodavanje novog zida.
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija u koju se dodaje zid
    model : MultiRoomModel
        Model u kojem se nalazi prostorija
    callback_nakon_dodavanja : function
        Funkcija koja se poziva nakon dodavanja zida
    """
    # Initialize session state key for wall type if it doesn't exist
    if "trenutni_tip_zida" not in st.session_state:
        st.session_state.trenutni_tip_zida = "vanjski"
    
    # Wall type selector outside the form for dynamic UI updates
    tip_zida = st.selectbox(
        "Tip zida", 
        ["vanjski", "prema_prostoriji", "prema_negrijanom"],
        format_func=lambda t: {
            "vanjski": "Vanjski zid", 
            "prema_prostoriji": "Zid prema drugoj prostoriji", 
            "prema_negrijanom": "Zid prema negrijanom prostoru"
        }.get(t, t),
        key="tip_zida_dodavanje",
        index=["vanjski", "prema_prostoriji", "prema_negrijanom"].index(st.session_state.trenutni_tip_zida)
    )
    
    # Save the current wall type to session state
    st.session_state.trenutni_tip_zida = tip_zida
      # Initialize building elements catalog for wall types
    elements_catalog = inicijaliziraj_elemente()
    
    # Now create the form with the remaining fields
    with st.form("forma_novi_zid"):
        duzina = st.number_input("Dužina zida [m]", min_value=0.1, value=5.0, step=0.1)
        
        etaza = model.dohvati_etazu(prostorija.etaza_id)
        visina_etaze = etaza.visina_etaze if etaza else 2.5
        
        koristi_zadanu_visinu = st.checkbox("Koristi visinu etaže", value=True)
        if not koristi_zadanu_visinu:
            visina_zida = st.number_input("Visina zida [m]", min_value=0.1, max_value=6.0, value=visina_etaze, step=0.1)
        else:
            visina_zida = None
        
        # Odabir tipa zida iz kataloga
        tip_zida_id = None
        if tip_zida == "vanjski":
            vanjski_zidovi = [z for z in elements_catalog.zidovi if z.tip == "vanjski"]
            if vanjski_zidovi:
                zid_options = {z.id: f"{z.naziv} (U={z.u_vrijednost:.2f} W/m²K)" for z in vanjski_zidovi}
                tip_zida_id = st.selectbox(
                    "Tip konstrukcije zida", 
                    options=list(zid_options.keys()),
                    format_func=lambda x: zid_options[x]
                )
        elif tip_zida == "prema_prostoriji" or tip_zida == "prema_negrijanom":
            unutarnji_zidovi = [z for z in elements_catalog.zidovi if z.tip != "vanjski"]
            if unutarnji_zidovi:
                zid_options = {z.id: f"{z.naziv} (U={z.u_vrijednost:.2f} W/m²K)" for z in unutarnji_zidovi}
                tip_zida_id = st.selectbox(
                    "Tip konstrukcije zida", 
                    options=list(zid_options.keys()),
                    format_func=lambda x: zid_options[x]
                )
        
        # Dodatna polja ovisno o tipu zida - ova polja se dinamički prikazuju ovisno o odabranom tipu zida
        orijentacija = None
        povezana_prostorija_id = None
        
        if tip_zida == "vanjski":
            orijentacija = st.selectbox("Orijentacija", ORIJENTACIJE)
        elif tip_zida == "prema_prostoriji":
            # Dohvati sve prostorije osim trenutne
            druge_prostorije = [p for p in model.prostorije if p.id != prostorija.id]
            
            if druge_prostorije:
                opcije_prostorija = [(p.id, f"{p.naziv} ({model.dohvati_etazu(p.etaza_id).naziv})") for p in druge_prostorije]
                povezana_prostorija_id = st.selectbox(
                    "Povezana prostorija", 
                    [pid for pid, _ in opcije_prostorija],
                    format_func=lambda pid: next((naziv for id, naziv in opcije_prostorija if id == pid), "")
                )
            else:
                st.warning("Nema drugih prostorija za povezivanje.")
        
        submitted = st.form_submit_button("Dodaj zid")
        
        if submitted:            # Koristimo model za dodavanje zida
            zid_id = model.add_wall_to_room(
                prostorija_id=prostorija.id,
                tip_zida=tip_zida,
                duzina=duzina,
                visina_zida=visina_zida if not koristi_zadanu_visinu else None,
                orijentacija=orijentacija,
                povezana_ciljna_prostorija_id=povezana_prostorija_id,
                tip_zida_id=tip_zida_id
            )
            if zid_id:
                st.success("Zid je uspješno dodan!")
                
                if callback_nakon_dodavanja:
                    novi_zid = prostorija.dohvati_zid(zid_id)
                    callback_nakon_dodavanja(novi_zid)
                
                # Add st.rerun() to refresh the UI after successfully adding a wall
                st.rerun()
                return True
            else:
                st.error("Greška prilikom dodavanja zida!")
    
    return False

def forma_za_uredivanje_zida(zid, prostorija, model, callback_nakon_uredivanja=None):
    """
    Prikazuje formu za uređivanje postojećeg zida.
    
    Parameters:
    -----------
    zid : dict
        Zid koji se uređuje
    prostorija : Prostorija
        Prostorija u kojoj se nalazi zid
    model : MultiRoomModel
        Model u kojem se nalazi prostorija
    callback_nakon_uredivanja : function
        Funkcija koja se poziva nakon uređivanja zida
    """
    with st.form("forma_uredi_zid"):
            # Tip zida se ne može mijenjati nakon stvaranja
            tip_zida = zid.get("tip", "vanjski")
            st.text(f"Tip zida: {tip_zida}")
            
            duzina = st.number_input("Dužina zida [m]", min_value=0.1, value=zid.get("duzina", 5.0), step=0.1)
            etaza = model.dohvati_etazu(prostorija.etaza_id)
            visina_etaze = etaza.visina_etaze if etaza else 2.5
            
            trenutna_visina = zid.get("visina", visina_etaze)
            koristi_zadanu_visinu = st.checkbox("Koristi visinu etaže", value=(trenutna_visina == visina_etaze))
            
            if not koristi_zadanu_visinu:
                visina_zida = st.number_input("Visina zida [m]", min_value=0.1, max_value=6.0, value=trenutna_visina, step=0.1)
            else:
                visina_zida = visina_etaze
            
            # Dodatna polja ovisno o tipu zida
            if tip_zida == "vanjski":
                trenutna_orijentacija = zid.get("orijentacija", ORIJENTACIJE[0])
                try:
                    orijentacija_index = ORIJENTACIJE.index(trenutna_orijentacija)
                except ValueError:
                    orijentacija_index = 0
                
                orijentacija = st.selectbox("Orijentacija", ORIJENTACIJE, index=orijentacija_index)
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Spremi promjene")
            with col2:
                delete_button = st.form_submit_button("Obriši zid", type="secondary")
            
            if submitted:
                # Ažuriranje podataka zida
                zid["duzina"] = validate_number(duzina, min_value=0.1, default=5.0)
                zid["visina"] = visina_zida
                
                if tip_zida == "vanjski":
                    zid["orijentacija"] = orijentacija
                
                # Spremanje promjena u model
                model._spremi_u_session_state()
                
                st.success("Zid je uspješno ažuriran!")
                if callback_nakon_uredivanja:
                    callback_nakon_uredivanja(zid)
                
                # Add st.rerun() to refresh the UI after successfully updating a wall
                st.rerun()
                return zid
            
            if delete_button:
                # Brisanje zida
                success = model.obrisi_zid_iz_prostorije(prostorija.id, zid.get("id"))
                
                if success:
                    st.success("Zid je uspješno obrisan!")
                    if callback_nakon_uredivanja:
                        callback_nakon_uredivanja(None)
                    
                    # Add st.rerun() to refresh the UI after successfully deleting a wall
                    st.rerun()
                    return None
                else:
                    st.error("Greška prilikom brisanja zida!")
    
    return zid

def prikaz_elemenata_zida(zid, prostorija, model, zid_controller, elements_catalog=None): # Modified signature
    """
    Prikazuje elemente (prozore, vrata) na zidu i omogućuje njihovo dodavanje.
    
    Parameters:
    -----------
    zid : dict
        Zid čiji se elementi prikazuju
    prostorija : Prostorija
        Prostorija u kojoj se nalazi zid
    model : MultiRoomModel
        Model u kojem se nalazi prostorija
    zid_controller : ZidController
        Kontroler za upravljanje zidovima i njihovim elementima
    elements_catalog : BuildingElementsModel, optional
        Katalog dostupnih tipova građevinskih elemenata (prozori, vrata)
    """
    # Inicijaliziraj elements_catalog ako nije proslijeđen
    if elements_catalog is None:
        elements_catalog = inicijaliziraj_elemente()
    
    elementi = zid.get("elementi")
      # Prikaz prozora
    prozori_na_zidu = []
    if elementi and hasattr(elementi, 'prozori'):
        prozori_na_zidu = elementi.prozori
        
    if prozori_na_zidu:
        st.subheader("Prozori na zidu")
        prozori_data = []
        for i, prozor in enumerate(prozori_na_zidu):
            # Dohvatimo podatke o tipu prozora iz kataloga ako postoji
            tip_id = prozor.get("tip_id")
            window_type = None
            if elements_catalog and tip_id:
                window_type = elements_catalog.dohvati_prozor(tip_id)
                
            sirina = prozor.get("sirina", window_type.sirina if window_type else 1.2)
            visina = prozor.get("visina", window_type.visina if window_type else 1.2)
            povrsina = sirina * visina
            u_vrijednost = window_type.u_vrijednost if window_type else 1.4
                
            prozori_data.append({
                "Br.": i + 1,
                "Tip": prozor.get("tip_naziv", "Nepoznat tip"),
                "Širina [m]": f"{float(sirina):.2f}",
                "Visina [m]": f"{float(visina):.2f}",
                "Površina [m²]": f"{float(povrsina):.2f}",
                "U-vrijednost [W/m²K]": f"{float(u_vrijednost):.2f}"
            })
        st.dataframe(prozori_data, hide_index=True, use_container_width=True)
    else:
        st.info("Ovaj zid nema definiranih prozora.")
      # Prikaz vrata
    vrata_na_zidu = []
    if elementi and hasattr(elementi, 'vrata'):
        vrata_na_zidu = elementi.vrata

    if vrata_na_zidu:
        st.subheader("Vrata na zidu")
        vrata_data = []
        for i, vrata_item in enumerate(vrata_na_zidu): # Renamed to vrata_item to avoid conflict
            # Dohvatimo podatke o tipu vrata iz kataloga ako postoji
            tip_id = vrata_item.get("tip_id")
            door_type = None
            if elements_catalog and tip_id:
                door_type = elements_catalog.dohvati_vrata(tip_id)
                
            sirina = vrata_item.get("sirina", door_type.sirina if door_type else 0.9)
            visina = vrata_item.get("visina", door_type.visina if door_type else 2.05)
            povrsina = sirina * visina
            u_vrijednost = door_type.u_vrijednost if door_type else 1.8
                
            vrata_data.append({
                "Br.": i + 1,
                "Tip": vrata_item.get("tip_naziv", "Nepoznat tip"),
                "Širina [m]": f"{float(sirina):.2f}",
                "Visina [m]": f"{float(visina):.2f}",
                "Površina [m²]": f"{float(povrsina):.2f}",
                "U-vrijednost [W/m²K]": f"{float(u_vrijednost):.2f}"
            })
        st.dataframe(vrata_data, hide_index=True, use_container_width=True)
    else:
        st.info("Ovaj zid nema definiranih vrata.")

    st.markdown("---") # Separator

    # Provjeri je li zid_controller dostupan prije nastavka
    if zid_controller is None:
        st.warning("Kontroler za zidove nije dostupan. Nije moguće dodavati elemente na zid.")
        return    # Dodavanje novog prozora
    with st.expander("Dodaj novi prozor"):
        window_types = elements_catalog.prozori
        if not window_types:
            st.warning("Nema definiranih tipova prozora u katalogu.")
        else:
            with st.form(f"dodaj_prozor_form_{zid.get('id')}"):
                # Select box za tip prozora
                window_options = {wt.id: wt.naziv for wt in window_types}
                selected_window_id = st.selectbox(
                    "Odaberi tip prozora",
                    options=list(window_options.keys()),
                    format_func=lambda x: window_options[x],
                    key=f"select_window_type_{zid.get('id')}"
                )
                
                # Dohvati podatke o odabranom prozoru
                selected_window_type = None
                if selected_window_id:
                    selected_window_type = elements_catalog.dohvati_prozor(selected_window_id)
                
                # Polja za unos dimenzija i U-vrijednosti
                col1, col2 = st.columns(2)
                with col1:
                    sirina = st.number_input(
                        "Širina [m]", 
                        min_value=0.1, 
                        max_value=5.0, 
                        value=selected_window_type.sirina if selected_window_type else 1.2,
                        step=0.1,
                        key=f"window_width_{zid.get('id')}"
                    )
                with col2:
                    visina = st.number_input(
                        "Visina [m]", 
                        min_value=0.1, 
                        max_value=5.0, 
                        value=selected_window_type.visina if selected_window_type else 1.2,
                        step=0.1,
                        key=f"window_height_{zid.get('id')}"
                    )
                
                # Automatski izračun površine
                povrsina = sirina * visina
                st.text(f"Površina: {povrsina:.2f} m²")
                
                # U-vrijednost
                u_vrijednost = st.number_input(
                    "U-vrijednost [W/m²K]", 
                    min_value=0.1, 
                    max_value=10.0, 
                    value=selected_window_type.u_vrijednost if selected_window_type else 1.4,
                    step=0.1,
                    key=f"window_u_value_{zid.get('id')}"
                )
                
                # Submit button
                submitted = st.form_submit_button("Dodaj prozor")
                if submitted:
                    if selected_window_id:
                        selected_window_type = elements_catalog.dohvati_prozor(selected_window_id)
                        if selected_window_type:
                            try:
                                # Dodaj parametre prozora (širina, visina, U-vrijednost)
                                dodatni_params = {
                                    "sirina": sirina,
                                    "visina": visina,
                                    "u_vrijednost": u_vrijednost,
                                    "povrsina": povrsina,
                                    "koristiti_standardne_dimenzije": False  # Koristimo prilagođene dimenzije
                                }
                                
                                result = zid_controller.dodaj_prozor_na_zid(
                                    prostorija.id, 
                                    zid.get("id"), 
                                    selected_window_type.id, 
                                    selected_window_type.naziv,
                                    dodatni_podaci=dodatni_params
                                )
                                if result:
                                    st.success(f"Prozor '{selected_window_type.naziv}' dodan na zid.")
                                    st.rerun()
                                else:
                                    st.error("Nije moguće dodati prozor. Provjerite konzolu za greške.")
                            except Exception as e:
                                st.error(f"Greška pri dodavanju prozora: {str(e)}")
                        else:
                            st.error("Odabrani tip prozora nije pronađen.")
                    else:
                        st.warning("Molimo odaberite tip prozora.")    # Dodavanje novih vrata
    with st.expander("Dodaj nova vrata"):
        all_door_types = elements_catalog.vrata
        
        # Filtriranje tipova vrata ovisno o tipu zida
        is_external_wall = zid.get("tip") == "vanjski"
        door_types_filtered = [
            dt for dt in all_door_types 
            if (is_external_wall and dt.tip == "vanjska") or \
               (not is_external_wall and dt.tip == "unutarnja")
        ]

        if not door_types_filtered:
            st.info("Nema dostupnih tipova vrata za ovaj tip zida u katalogu.")
        else:
            with st.form(f"dodaj_vrata_form_{zid.get('id')}"):
                # Select box za tip vrata
                door_options = {dt.id: dt.naziv for dt in door_types_filtered}
                selected_door_id = st.selectbox(
                    "Odaberi tip vrata",
                    options=list(door_options.keys()),
                    format_func=lambda x: door_options[x],
                    key=f"select_door_type_{zid.get('id')}"
                )
                
                # Dohvati podatke o odabranom tipu vrata
                selected_door_type = None
                if selected_door_id:
                    selected_door_type = elements_catalog.dohvati_vrata(selected_door_id)
                
                # Polja za unos dimenzija i U-vrijednosti
                col1, col2 = st.columns(2)
                with col1:
                    sirina = st.number_input(
                        "Širina [m]", 
                        min_value=0.1, 
                        max_value=5.0, 
                        value=selected_door_type.sirina if selected_door_type else 0.9,
                        step=0.1,
                        key=f"door_width_{zid.get('id')}"
                    )
                with col2:
                    visina = st.number_input(
                        "Visina [m]", 
                        min_value=0.1, 
                        max_value=5.0, 
                        value=selected_door_type.visina if selected_door_type else 2.05,
                        step=0.1,
                        key=f"door_height_{zid.get('id')}"
                    )
                
                # Automatski izračun površine
                povrsina = sirina * visina
                st.text(f"Površina: {povrsina:.2f} m²")
                
                # U-vrijednost
                u_vrijednost = st.number_input(
                    "U-vrijednost [W/m²K]", 
                    min_value=0.1, 
                    max_value=10.0, 
                    value=selected_door_type.u_vrijednost if selected_door_type else 1.8,
                    step=0.1,
                    key=f"door_u_value_{zid.get('id')}"
                )
                
                # Submit button
                submitted = st.form_submit_button("Dodaj vrata")
                if submitted:
                    if selected_door_id:
                        selected_door_type = elements_catalog.dohvati_vrata(selected_door_id)
                        if selected_door_type:
                            try:
                                # Dodaj parametre vrata (širina, visina, U-vrijednost)
                                dodatni_params = {
                                    "sirina": sirina,
                                    "visina": visina,
                                    "u_vrijednost": u_vrijednost,
                                    "povrsina": povrsina,
                                    "koristiti_standardne_dimenzije": False  # Koristimo prilagođene dimenzije
                                }
                                
                                result = zid_controller.dodaj_vrata_na_zid(
                                    prostorija.id, 
                                    zid.get("id"), 
                                    selected_door_type.id, 
                                    selected_door_type.naziv,
                                    dodatni_podaci=dodatni_params
                                )
                                if result:
                                    st.success(f"Vrata '{selected_door_type.naziv}' dodana na zid.")
                                    st.rerun()
                                else:
                                    st.error("Nije moguće dodati vrata. Provjerite konzolu za greške.")
                            except Exception as e:
                                st.error(f"Greška pri dodavanju vrata: {str(e)}")
                        else:
                            st.error("Odabrani tip vrata nije pronađen.")
                    else:
                        st.warning("Molimo odaberite tip vrata.")

def prikazi_zidove_prostorije(prostorija, model, zid_controller):
    """
    Prikazuje sučelje za upravljanje zidovima prostorije (dodavanje, uređivanje, brisanje).
    
    Parameters:
    -----------
    prostorija : Prostorija
        Prostorija čiji zidovi se prikazuju
    model : MultiRoomModel
        Model s zidovima
    zid_controller : ZidController
        Kontroler za upravljanje zidovima
    """
    st.subheader(f"Zidovi prostorije: {prostorija.naziv}")
    
    elements_catalog = inicijaliziraj_elemente() # Initialize elements catalog
      
    # Dodavanje novog zida
    st.subheader("Dodaj novi zid")
    novi_zid = forma_za_dodavanje_zida(prostorija, model)
    
    # Prikaz postojećih zidova
    if not prostorija.zidovi:
        st.info("Nema definiranih zidova za ovu prostoriju. Dodajte novi zid.")
        return    # Grupiranje zidova u kategorije - vanjski i unutarnji
    # Pošto imamo jasno definirane tipove zidova pri dodavanju, klasifikacija je jednostavna
    vanjski_zidovi = []
    unutarnji_zidovi = []
    
    for zid in prostorija.zidovi:
        tip_zida_naziv = zid.get("tip")
        
        # Jednostavna klasifikacija na temelju tipa zida
        if tip_zida_naziv == "vanjski":
            # Zidovi označeni kao "vanjski" su uvijek vanjski
            vanjski_zidovi.append(zid)
        else:
            # Zidovi prema prostoriji i prema negrijanom su uvijek unutarnji zidovi
            unutarnji_zidovi.append(zid)
    
    # Prikaz vanjskih zidova
    if vanjski_zidovi:
        st.subheader("Vanjski zidovi")
        _prikazi_listu_zidova(vanjski_zidovi, prostorija, model, zid_controller, elements_catalog)
    else:
        st.info("Nema definiranih vanjskih zidova.")
    
    # Separator između vanjskih i unutarnjih zidova
    st.markdown("---")
    
    # Prikaz unutarnjih zidova
    if unutarnji_zidovi:
        st.subheader("Unutarnji zidovi")
        _prikazi_listu_zidova(unutarnji_zidovi, prostorija, model, zid_controller, elements_catalog)
    else:
        st.info("Nema definiranih unutarnjih zidova.")

def _prikazi_listu_zidova(zidovi, prostorija, model, zid_controller, elements_catalog):
    """
    Pomoćna funkcija za prikaz liste zidova.
    
    Parameters:
    -----------
    zidovi : list
        Lista zidova za prikaz
    prostorija : Prostorija
        Prostorija čiji se zidovi prikazuju
    model : MultiRoomModel
        Model s zidovima
    zid_controller : ZidController
        Kontroler za upravljanje zidovima
    elements_catalog : BuildingElementsModel
        Katalog građevinskih elemenata
    """
    for i, zid in enumerate(zidovi):
        # Koristimo kontejner za svaki zid
        with st.container():
            # Definicija tipova zida i generiranje opisa
            tip_zida_naziv = zid.get("tip", "Nepoznat tip")
            zid_id_display = zid.get('id', 'N/A')
            
            # Standardizirana priprema naziva za prikaz
            if tip_zida_naziv == "vanjski":
                orijentacija = zid.get("orijentacija", "")
                naziv_za_prikaz = f"Vanjski zid | {orijentacija}"
            elif tip_zida_naziv == "prema_prostoriji":
                povezana_prostorija_id = zid.get("povezana_prostorija_id")
                fizicki_zid_id = zid.get("fizicki_zid_id")
                povezana_prostorija = model.dohvati_prostoriju(povezana_prostorija_id) if povezana_prostorija_id else None
                povezana_naziv = povezana_prostorija.naziv if povezana_prostorija else "Nije povezan"
                
                # Pojednostavljeni prikaz povezanog zida
                naziv_za_prikaz = f"Prema prostoriji | {povezana_naziv}"
                if fizicki_zid_id:
                    naziv_za_prikaz += f" | Fiz.ID: {fizicki_zid_id}"
            elif tip_zida_naziv == "prema_negrijanom":
                naziv_za_prikaz = "Prema negrijanom prostoru"
            else:
                naziv_za_prikaz = tip_zida_naziv
              # Struktura za prikaz zida i gumba za akcije
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            with col1:
                # Konzistentan prikaz dimenzija
                dimenzije = f"{zid.get('duzina', 0.0):.1f} × {zid.get('visina', 0.0):.1f} m"                # Prilagođeni prikaz ID-a ovisno o tipu zida u istom redu (plavi ili zeleni caption za ID)
                # Koristimo različite HTML stilove za različite tipove zidova
                
                if tip_zida_naziv == "prema_prostoriji" and zid.get("fizicki_zid_id"):
                    # Plavi stil za fizičke zidove i prikaz običnog i fizičkog ID-a
                    fizicki_id = zid.get("fizicki_zid_id")
                    # Prikazujemo i normalni ID i fizički ID za zidove prema prostoriji
                    st.markdown(f"**{naziv_za_prikaz}** ({dimenzije}) <span style='background-color:#d1e7dd; padding:2px 5px; border-radius:3px; color:#0a3622;'>ID: {zid_id_display}</span> <span style='background-color:#cce5ff; padding:2px 5px; border-radius:3px; color:#004085;'>Fizički ID: {fizicki_id}</span>", unsafe_allow_html=True)
                else:
                    # Zeleni zadani stil (kao caption) za ostale zidove
                    st.markdown(f"**{naziv_za_prikaz}** ({dimenzije}) <span style='background-color:#d1e7dd; padding:2px 5px; border-radius:3px; color:#0a3622;'>ID: {zid_id_display}</span>", unsafe_allow_html=True)
            
            with col2:
                if st.button("Detalji", key=f"details_zid_{zid.get('id')}"):
                    st.session_state[f"show_details_zid_{zid.get('id')}"] = not st.session_state.get(f"show_details_zid_{zid.get('id')}", False)
            
            with col3:
                if st.button("Uredi", key=f"edit_zid_{zid.get('id')}"):
                    st.session_state[f"edit_zid_open_{zid.get('id')}"] = True
            
            with col4:
                if st.button("Obriši", key=f"delete_zid_{zid.get('id')}"):
                    if zid_controller.ukloni_zid(prostorija.id, zid.get('id')):
                        st.success(f"Zid uspješno uklonjen!")
                        st.rerun()
                    else:
                        st.error("Greška prilikom brisanja zida.")
        
        # Prikaži detalje ako je otvoreno
        if st.session_state.get(f"show_details_zid_{zid.get('id')}", False):
            with st.container():
                st.divider()  # Koristimo Streamlit divider umjesto HTML separatora
                prikaz_elemenata_zida(zid, prostorija, model, zid_controller, elements_catalog) # Pass controller and catalog
                if st.button("Sakrij detalje", key=f"hide_details_zid_{zid.get('id')}"):
                    st.session_state[f"show_details_zid_{zid.get('id')}"] = False
                    st.rerun()
                st.divider()
        
        # Prikaži formu za uređivanje ako je otvorena
        if st.session_state.get(f"edit_zid_open_{zid.get('id')}", False):
            with st.container():
                st.divider()
                if forma_za_uredivanje_zida(zid, prostorija, model):
                    st.session_state[f"edit_zid_open_{zid.get('id')}"] = False
                    st.rerun()
                if st.button("Odustani", key=f"cancel_edit_zid_{zid.get('id')}"):
                    st.session_state[f"edit_zid_open_{zid.get('id')}"] = False
                    st.rerun()
                st.divider()
        
        # Separator između zidova - koristi Streamlit divider
        if i < len(prostorija.zidovi) - 1:
            st.divider()
