"""
Modul koji sadrži funkcije za prikaz i upravljanje građevinskim elementima u UI-u.
"""

import streamlit as st
from ..models.elementi.constants import TIPOVI_ELEMENATA
from ..utils.validators import validate_number

def prikazi_manager_gradevinski_elementi(model, elementi_controller):
    """
    Prikazuje sučelje za upravljanje građevinskim elementima.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s podacima
    elementi_controller : ElementiController
        Kontroler za upravljanje građevinskim elementima
    """
    st.header("Upravljanje građevinskim elementima")
    
    # Kreiranje tabova za različite kategorije građevinskih elemenata
    tabs = st.tabs([
        "Podovi", 
        "Stropovi", 
        "Vanjski zidovi", 
        "Unutarnji zidovi", 
        "Vanjska vrata", 
        "Unutarnja vrata", 
        "Prozori"
    ])
    
    # Tab za podove
    with tabs[0]:
        prikazi_tab_gradevinski_elementi(model, elementi_controller, "POD")
    
    # Tab za stropove
    with tabs[1]:
        prikazi_tab_gradevinski_elementi(model, elementi_controller, "STROP")
    
    # Tab za vanjske zidove
    with tabs[2]:
        prikazi_tab_gradevinski_elementi(model, elementi_controller, "VANJSKI_ZID")
    
    # Tab za unutarnje zidove
    with tabs[3]:
        prikazi_tab_gradevinski_elementi(model, elementi_controller, "UNUTARNJI_ZID")
    
    # Tab za vanjska vrata
    with tabs[4]:
        prikazi_tab_gradevinski_elementi(model, elementi_controller, "VANJSKA_VRATA")
    
    # Tab za unutarnja vrata
    with tabs[5]:
        prikazi_tab_gradevinski_elementi(model, elementi_controller, "UNUTARNJA_VRATA")
    
    # Tab za prozore
    with tabs[6]:
        prikazi_tab_gradevinski_elementi(model, elementi_controller, "PROZOR")

def prikazi_tab_gradevinski_elementi(model, elementi_controller, tip_elementa):
    """
    Prikazuje tab za određeni tip građevinskog elementa.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s podacima
    elementi_controller : ElementiController
        Kontroler za upravljanje građevinskim elementima
    tip_elementa : str
        Tip građevinskog elementa (POD, STROP, itd.)
    """
    elementi = elementi_controller.dohvati_elemente_po_tipu(tip_elementa)
    
    # Kreiranje forme za dodavanje novog elementa
    with st.expander(f"Dodaj novi {TIPOVI_ELEMENATA.get(tip_elementa, 'element').lower()}", expanded=False):
        prikaziFormuZaDodavanjeElementa(model, elementi_controller, tip_elementa)
      # Prikaz postojećih elemenata
    if not elementi:
        st.info(f"Nema definiranih elemenata tipa {TIPOVI_ELEMENATA.get(tip_elementa, tip_elementa)}. "
                f"Dodajte novi element koristeći formu iznad.")
        return
    
    st.subheader(f"Postojeći elementi - {TIPOVI_ELEMENATA.get(tip_elementa, tip_elementa)}")
    
    # Sortiramo elemente po nazivu
    elementi = sorted(elementi, key=lambda e: e.naziv)
    
    # Prikaz elemenata u tablici
    if "VRATA" in tip_elementa or "PROZOR" in tip_elementa:
        # Za vrata i prozore prikazujemo dimenzije i U-vrijednost
        table_data = []
        for element in elementi:
            sirina = element.sirina if hasattr(element, 'sirina') else 0
            visina = element.visina if hasattr(element, 'visina') else 0
            povrsina = sirina * visina
            row = {
                "Naziv": element.naziv,
                "Širina [m]": f"{sirina:.2f}",
                "Visina [m]": f"{visina:.2f}",
                "Površina [m²]": f"{povrsina:.2f}",
                "U-vrijednost [W/m²K]": f"{element.u_vrijednost:.2f}"
            }
            table_data.append(row)
        
        st.dataframe(table_data, hide_index=True, use_container_width=True)
    elif "ZID" in tip_elementa:
        # Za zidove prikazujemo debljinu i U-vrijednost
        table_data = []
        for element in elementi:
            debljina = element.debljina if hasattr(element, 'debljina') else 0
            debljina_izolacije = element.debljina_izolacije if hasattr(element, 'debljina_izolacije') else 0
            ukupna_debljina = debljina + debljina_izolacije
            row = {
                "Naziv": element.naziv,
                "Debljina zida [m]": f"{debljina:.2f}",
                "Debljina izolacije [m]": f"{debljina_izolacije:.2f}",
                "Ukupna debljina [m]": f"{ukupna_debljina:.2f}",
                "U-vrijednost [W/m²K]": f"{element.u_vrijednost:.2f}"
            }
            table_data.append(row)
        
        st.dataframe(table_data, hide_index=True, use_container_width=True)
    elif tip_elementa in ["POD", "STROP"]:
        # Za podove i stropove prikazujemo debljine i U-vrijednost
        table_data = []
        for element in elementi:
            debljina_konstrukcije = getattr(element, 'debljina_konstrukcije', 0)
            debljina_dodatnih_slojeva = getattr(element, 'debljina_dodatnih_slojeva', 0)
            tip = getattr(element, 'tip', "")
            ukupna_debljina = debljina_konstrukcije + debljina_dodatnih_slojeva
            row = {
                "Naziv": element.naziv,
                "Tip": tip,
                "Debljina konstrukcije [m]": f"{debljina_konstrukcije:.2f}",
                "Debljina dodatnih slojeva [m]": f"{debljina_dodatnih_slojeva:.2f}",
                "Ukupna debljina [m]": f"{ukupna_debljina:.2f}",
                "U-vrijednost [W/m²K]": f"{element.u_vrijednost:.2f}"
            }
            table_data.append(row)
        
        st.dataframe(table_data, hide_index=True, use_container_width=True)
    
    # Prikaz svakog elementa za detaljni pregled i uređivanje
    for i, element in enumerate(elementi):
        prikazi_gradevinski_element(element, elementi_controller, i)

def prikaziFormuZaDodavanjeElementa(model, elementi_controller, tip_elementa):
    """
    Prikazuje formu za dodavanje novog građevinskog elementa.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s podacima
    elementi_controller : ElementiController
        Kontroler za upravljanje građevinskim elementima
    tip_elementa : str
        Tip građevinskog elementa (POD, STROP, itd.)
    """
    with st.form(f"forma_novi_element_{tip_elementa}"):
        naziv = st.text_input("Naziv elementa", f"Novi {TIPOVI_ELEMENATA.get(tip_elementa, 'element').lower()}")
        
        u_vrijednost = st.number_input(
            "U-vrijednost [W/m²K]", 
            min_value=0.01, 
            max_value=5.0, 
            value=0.3 if "ZID" in tip_elementa else 0.2, 
            step=0.01
        )
          # Dodatna polja specifična za tip elementa
        if "VRATA" in tip_elementa or "PROZOR" in tip_elementa:
            sirina = st.number_input("Širina [m]", min_value=0.1, max_value=3.0, value=1.0, step=0.1)
            visina = st.number_input("Visina [m]", min_value=0.1, max_value=3.0, value=2.0, step=0.1)
            povrsina = sirina * visina
            st.text(f"Površina: {povrsina:.2f} m²")
            dodatni_podaci = {"sirina": sirina, "visina": visina, "povrsina": povrsina}
        elif "ZID" in tip_elementa:
            # Različiti parametri za unutarnje i vanjske zidove
            if "VANJSKI" in tip_elementa:
                debljina = st.number_input("Debljina zida [m]", min_value=0.1, max_value=1.0, value=0.25, step=0.01)
                debljina_izolacije = st.number_input("Debljina izolacije [m]", min_value=0.0, max_value=0.5, value=0.1, step=0.01)
                ukupna_debljina = debljina + debljina_izolacije
                st.text(f"Ukupna debljina: {ukupna_debljina:.2f} m")
                dodatni_podaci = {
                    "debljina": debljina, 
                    "debljina_izolacije": debljina_izolacije, 
                    "ukupna_debljina": ukupna_debljina, 
                    "tip": "vanjski"
                }
            else:
                debljina = st.number_input("Debljina zida [m]", min_value=0.1, max_value=1.0, value=0.2, step=0.01)
                dodatni_podaci = {"debljina": debljina, "tip": "unutarnji"}
        elif tip_elementa == "POD":
            debljina_konstrukcije = st.number_input("Debljina konstrukcije [m]", min_value=0.1, max_value=3.0, value=0.15, step=0.01)
            debljina_dodatnih_slojeva = st.number_input("Debljina dodatnih slojeva [m]", min_value=0.01, max_value=1.0, value=0.05, step=0.01)
            ukupna_debljina = debljina_konstrukcije + debljina_dodatnih_slojeva
            st.text(f"Ukupna debljina: {ukupna_debljina:.2f} m")
            tip_poda = st.selectbox("Tip poda", ["na tlu", "prema negrijanom", "međukatna"])
            dodatni_podaci = {
                "debljina_konstrukcije": debljina_konstrukcije, 
                "debljina_dodatnih_slojeva": debljina_dodatnih_slojeva, 
                "ukupna_debljina": ukupna_debljina,
                "tip": tip_poda
            }
        elif tip_elementa == "STROP":
            debljina_konstrukcije = st.number_input("Debljina konstrukcije [m]", min_value=0.1, max_value=3.0, value=0.2, step=0.01)
            debljina_dodatnih_slojeva = st.number_input("Debljina dodatnih slojeva [m]", min_value=0.01, max_value=1.0, value=0.05, step=0.01)
            ukupna_debljina = debljina_konstrukcije + debljina_dodatnih_slojeva
            st.text(f"Ukupna debljina: {ukupna_debljina:.2f} m")
            tip_stropa = st.selectbox("Tip stropa", ["prema negrijanom", "ravni krov", "kosi krov", "međukatna"])
            dodatni_podaci = {
                "debljina_konstrukcije": debljina_konstrukcije, 
                "debljina_dodatnih_slojeva": debljina_dodatnih_slojeva, 
                "ukupna_debljina": ukupna_debljina,
                "tip": tip_stropa
            }
        else:
            dodatni_podaci = {}
          # Gumb za dodavanje novog elementa
        submitted = st.form_submit_button(f"Dodaj {TIPOVI_ELEMENATA.get(tip_elementa, 'element').lower()}")
        
        if submitted:
            # Priprema parametara za dodaj_element, spajamo osnovne s dodatnima
            params = {
                "naziv": naziv,
                "u_vrijednost": u_vrijednost,
                "opis": f"Dodano kroz UI formu - {TIPOVI_ELEMENATA.get(tip_elementa, 'element')}"
            }
            # Dodajemo dodatne podatke
            params.update(dodatni_podaci)
            
            if elementi_controller.dodaj_element(tip_elementa, **params):
                st.success(f"{TIPOVI_ELEMENATA.get(tip_elementa, 'Element')} '{naziv}' uspješno dodan!")
                st.rerun()
            else:
                st.error(f"Greška prilikom dodavanja elementa '{naziv}'!")

def prikazi_gradevinski_element(element, elementi_controller, index):
    """
    Prikazuje pojedinačni građevinski element s opcijama za uređivanje.
    
    Parameters:
    -----------
    element : GradevinskiElement
        Građevinski element koji se prikazuje
    elementi_controller : ElementiController
        Kontroler za upravljanje građevinskim elementima
    index : int
        Indeks elementa (za generiranje jedinstvenih ključeva)
    """
    with st.container():
        st.markdown("---")
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"### {element.naziv}")
            st.markdown(f"**U-vrijednost:** {element.u_vrijednost:.3f} W/m²K")
              # Prikaz dodatnih podataka ako postoje
            if hasattr(element, 'dodatni_podaci') and element.dodatni_podaci:
                for key, value in element.dodatni_podaci.items():
                    if key in ['sirina', 'visina']:
                        st.markdown(f"**{key.replace('_', ' ').capitalize()}:** {value:.2f} m")
                    elif key in ['debljina_konstrukcije', 'debljina_dodatnih_slojeva']:
                        # Convert to centimeters and display as whole number
                        cm_value = int(value * 100)
                        st.markdown(f"**{key.replace('_', ' ').capitalize()}:** {cm_value} cm")
                    elif key != 'tip':
                        st.markdown(f"**{key.replace('_', ' ').capitalize()}:** {value}")
        
        with col2:
            # Gumb za uređivanje
            edit_key = f"edit_element_{element.id}"
            if st.button("Uredi", key=f"edit_btn_{element.id}"):
                st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                st.rerun()
        
        with col3:
            # Gumb za brisanje
            if st.button("Obriši", key=f"delete_btn_{element.id}"):
                if elementi_controller.ukloni_element(element.id):
                    st.success(f"Element '{element.naziv}' uspješno uklonjen!")
                    st.rerun()
                else:
                    st.error(f"Greška prilikom brisanja elementa '{element.naziv}'!")
        
        # Prikaz forme za uređivanje ako je otvorena
        if st.session_state.get(edit_key, False):
            with st.form(f"forma_uredi_element_{element.id}"):
                st.subheader(f"Uredi element: {element.naziv}")
                
                novi_naziv = st.text_input("Naziv elementa", element.naziv)
                nova_u_vrijednost = st.number_input(
                    "U-vrijednost [W/m²K]", 
                    min_value=0.01, 
                    max_value=5.0, 
                    value=element.u_vrijednost, 
                    step=0.01
                )
                
                # Dodatan unos za elemente koji imaju dimenzije
                dodatni_podaci = {}
                if hasattr(element, 'dodatni_podaci') and element.dodatni_podaci:
                    if 'sirina' in element.dodatni_podaci and 'visina' in element.dodatni_podaci:
                        sirina = st.number_input(
                            "Širina [m]", 
                            min_value=0.1, 
                            max_value=3.0, 
                            value=element.dodatni_podaci.get('sirina', 1.0), 
                            step=0.1
                        )
                        visina = st.number_input(
                            "Visina [m]", 
                            min_value=0.1, 
                            max_value=3.0, 
                            value=element.dodatni_podaci.get('visina', 2.0), 
                            step=0.1
                        )
                        dodatni_podaci = {"sirina": sirina, "visina": visina}
                    elif 'debljina_konstrukcije' in element.dodatni_podaci or 'debljina_dodatnih_slojeva' in element.dodatni_podaci:
                        debljina_konstrukcije = st.number_input(
                            "Debljina konstrukcije [m]", 
                            min_value=0.1, 
                            max_value=3.0, 
                            value=element.dodatni_podaci.get('debljina_konstrukcije', 0.15), 
                            step=0.01
                        )
                        debljina_dodatnih_slojeva = st.number_input(
                            "Debljina dodatnih slojeva [m]", 
                            min_value=0.01, 
                            max_value=1.0, 
                            value=element.dodatni_podaci.get('debljina_dodatnih_slojeva', 0.05), 
                            step=0.01
                        )
                        dodatni_podaci = {"debljina_konstrukcije": debljina_konstrukcije, "debljina_dodatnih_slojeva": debljina_dodatnih_slojeva}
                
                col1, col2 = st.columns(2)
                with col1:
                    submit_edit = st.form_submit_button("Spremi promjene")
                
                with col2:
                    cancel_edit = st.form_submit_button("Odustani")
                
                if submit_edit:
                    if elementi_controller.azuriraj_element(
                        element_id=element.id,
                        naziv=novi_naziv,
                        u_vrijednost=nova_u_vrijednost,
                        dodatni_podaci=dodatni_podaci
                    ):
                        st.success(f"Element '{novi_naziv}' uspješno ažuriran!")
                        st.session_state[edit_key] = False
                        st.rerun()
                    else:
                        st.error(f"Greška prilikom ažuriranja elementa '{novi_naziv}'!")
                
                if cancel_edit:
                    st.session_state[edit_key] = False
                    st.rerun()
