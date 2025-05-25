"""
Modul koji sadrži sučelje za upravljanje povezivanjem zidova.
"""

import streamlit as st
import pandas as pd

def prikazi_analizator_povezanosti_zidova(model, zid_controller):
    """
    Prikazuje sučelje za analizu i povezivanje zidova.
    
    Parameters:
    -----------
    model : MultiRoomModel
        Model s prostorijama i zidovima
    zid_controller : ZidController
        Kontroler za upravljanje zidovima
    """
    st.header("Analiza povezanosti zidova")
    
    # Objašnjenje što ovaj alat radi
    st.write("""
    Ovaj alat analizira sve zidove u vašem modelu i pokušava identificirati one koji bi 
    mogli predstavljati isti fizički zid između različitih prostorija. 
    Time se osigurava konzistentnost u modelu i ispravni izračuni toplinskih gubitaka.
    """)
    
    # Gumb za pokretanje analize
    if st.button("Pokreni analizu povezanosti zidova"):
        with st.spinner("Analiziram povezanost zidova..."):
            potencijalna_povezivanja = zid_controller.analiziraj_povezanost_zidova()
            
            if not potencijalna_povezivanja:
                st.info("Nisu pronađeni potencijalno povezani zidovi.")
            else:
                st.success(f"Pronađeno {len(potencijalna_povezivanja)} potencijalnih povezivanja zidova.")
                
                # Prikaži rezultate u tablici
                st.subheader("Potencijalno povezani zidovi")
                
                # Pripremi podatke za tablicu
                table_data = []
                for i, povezivanje in enumerate(potencijalna_povezivanja):
                    # Dohvati prostorije i zidove
                    prostorija1 = model.dohvati_prostoriju(povezivanje["prostorija1_id"])
                    prostorija2 = model.dohvati_prostoriju(povezivanje["prostorija2_id"])
                    zid1 = prostorija1.dohvati_zid(povezivanje["zid1_id"]) if prostorija1 else None
                    zid2 = prostorija2.dohvati_zid(povezivanje["zid2_id"]) if prostorija2 else None
                    
                    if prostorija1 and prostorija2 and zid1 and zid2:
                        table_data.append({
                            "ID": i+1,
                            "Prostorija 1": prostorija1.naziv,
                            "Zid 1": f"{zid1.get('tip', 'nepoznat')} ({zid1.get('duzina', 0):.2f} m)",
                            "Prostorija 2": prostorija2.naziv,
                            "Zid 2": f"{zid2.get('tip', 'nepoznat')} ({zid2.get('duzina', 0):.2f} m)",
                            "Pouzdanost": f"{povezivanje['pouzdanost']*100:.0f}%",
                            "prostorija1_id": povezivanje["prostorija1_id"],
                            "zid1_id": povezivanje["zid1_id"],
                            "prostorija2_id": povezivanje["prostorija2_id"],
                            "zid2_id": povezivanje["zid2_id"]
                        })
                
                if table_data:
                    # Stvori DataFrame bez tajnih ID-eva za prikaz
                    df_display = pd.DataFrame([{k: v for k, v in item.items() if k not in ["prostorija1_id", "zid1_id", "prostorija2_id", "zid2_id"]} for item in table_data])
                    st.dataframe(df_display.drop(columns=["ID"]), hide_index=True)
                    
                    # Prikaz gumba za povezivanje zidova
                    st.subheader("Povezivanje zidova")
                    st.write("Odaberite koje zidove želite povezati:")
                    
                    for item in table_data:
                        if st.button(f"Poveži: {item['Prostorija 1']} - {item['Prostorija 2']}", key=f"connect_{item['ID']}"):
                            with st.spinner("Povezujem zidove..."):
                                uspjeh = zid_controller.povezi_zidove(
                                    item["prostorija1_id"], item["zid1_id"],
                                    item["prostorija2_id"], item["zid2_id"]
                                )
                                
                                if uspjeh:
                                    st.success(f"Zidovi uspješno povezani! Zidovi između prostorija {item['Prostorija 1']} i {item['Prostorija 2']} sada dijele isti fizički zid.")
                                    # Obriši session state da se ponovno pokrene analiza
                                    if "potencijalna_povezivanja" in st.session_state:
                                        del st.session_state["potencijalna_povezivanja"]
                                    st.rerun()
                                else:
                                    st.error("Došlo je do greške prilikom povezivanja zidova.")
                else:
                    st.info("Nema podataka za prikaz.")
    
    # Prikaz već povezanih zidova
    st.header("Već povezani zidovi")
    
    # Dohvati sve fizičke zidove koji imaju više povezanih prostorija
    povezani_fizicki_zidovi = []
    for zid_id, fizicki_zid in model.fizicki_zidovi.items():
        if len(fizicki_zid.povezane_prostorije) >= 2:
            povezani_fizicki_zidovi.append(fizicki_zid)
    
    if not povezani_fizicki_zidovi:
        st.info("Nema povezanih zidova u modelu.")
    else:
        for fizicki_zid in povezani_fizicki_zidovi:            # Pripremi podatke o povezanim prostorijama
            prostorije_info = []
            for povezana in fizicki_zid.povezane_prostorije:
                prostorija = model.dohvati_prostoriju(povezana["prostorija_id"])
                if prostorija:
                    formatted_broj = prostorija.get_formatted_broj_prostorije()
                    room_name = f"{formatted_broj}. {prostorija.naziv}" if formatted_broj else prostorija.naziv
                    prostorije_info.append(room_name)
            
            # Prikaži informacije o fizičkom zidu
            with st.expander(f"Fizički zid između: {', '.join(prostorije_info)}"):
                st.write(f"**Tip zida:** {fizicki_zid.tip}")
                st.write(f"**Duljina:** {fizicki_zid.duzina:.2f} m")
                st.write(f"**Visina:** {fizicki_zid.visina:.2f} m" if fizicki_zid.visina else "**Visina:** koristi se visina etaže")                  # Prikaži tablicu povezanih prostorija
                povezane_prostorije_data = []
                for povezana in fizicki_zid.povezane_prostorije:
                    prostorija = model.dohvati_prostoriju(povezana["prostorija_id"])
                    if prostorija:
                        formatted_broj = prostorija.get_formatted_broj_prostorije()
                        room_title = f"{formatted_broj}. {prostorija.naziv}" if formatted_broj else prostorija.naziv
                        povezane_prostorije_data.append({
                            "Prostorija": room_title,
                            "Tip": prostorija.tip,
                            "Etaža": model.dohvati_etazu(prostorija.etaza_id).naziv if model.dohvati_etazu(prostorija.etaza_id) else "Nepoznato"
                        })
                
                if povezane_prostorije_data:
                    st.write("**Povezane prostorije:**")
                    st.dataframe(pd.DataFrame(povezane_prostorije_data), hide_index=True)
