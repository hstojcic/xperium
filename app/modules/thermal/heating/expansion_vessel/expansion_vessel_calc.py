import streamlit as st
import numpy as np
from modules.base import BaseCalculation
import math

class ExpansionVesselCalc(BaseCalculation):
    """
    Proračun ekspanzijske posude za sustave grijanja
    """
    
    def __init__(self):
        super().__init__("Proračun ekspanzijske posude")
        
        # Inicijalizacija parametara proračuna
        self.t_v = 80.0  # temperatura polaza (°C)
        self.t_r = 60.0  # temperatura povrata (°C)
        self.h = 10.0    # visinska razlika (m)
        self.p_min_req = 0.0  # minimalni tlak (bar)
        self.volumes = {
            "Cijevi": [],
            "Uređaji": [],
            "Spremnici": []
        }
        self.total_system_volume = 0.0  # ukupni volumen sustava (l)
        self.p_e = 3.0   # tlak sigurnosnog ventila (bar)
        
        # Rezultati proračuna
        self.results = {
            't_m': 0.0,          # srednja temperatura (°C)
            't_m_rounded': 0,    # zaokružena srednja temperatura (°C)
            'density': 0.0,      # gustoća vode (kg/m³)
            'n': 0.0,            # koeficijent širenja (%)
            'p_st': 0.0,         # statički tlak (bar)
            'p_o': 0.0,          # minimalni radni tlak (bar)
            'v_e': 0.0,          # volumen širenja (l)
            'v_v': 0.0,          # dodatni volumen (l)
            'v_n': 0.0,          # nazivni volumen (l)
            'standard_size': 0   # standardna veličina posude (l)
        }
        
    def render(self):
        """
        Prikazuje sučelje proračuna ekspanzijske posude
        """
        st.title(self.name)
        
        st.write("Proračun volumena zatvorene membranske ekspanzijske posude u sustavima grijanja.")
        
        # Kreiramo tabove za različite korake proračuna - bez numeriranja
        tabs = st.tabs([
            "Temperatura sustava", 
            "Volumen sustava", 
            "Tlakovi i rezultati"
        ])
        
        # ---------------------- TAB: TEMPERATURA SUSTAVA ----------------------
        with tabs[0]:
            st.header("Temperatura sustava")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Sačuvaj stare vrijednosti za usporedbu
                old_tv = self.t_v
                old_tr = self.t_r
                
                # Ulazni parametri
                self.t_v = st.number_input(
                    "Temperatura polaza (°C)",
                    min_value=20.0,
                    max_value=130.0,
                    value=float(self.t_v),
                    step=5.0,
                    key="t_v"
                )
                
                self.t_r = st.number_input(
                    "Temperatura povrata (°C)",
                    min_value=20.0,
                    max_value=100.0,
                    value=float(self.t_r),
                    step=5.0,
                    key="t_r"
                )
                
                # Automatski izračun ako su se promijenili parametri
                if old_tv != self.t_v or old_tr != self.t_r:
                    self.record_state("Promjena temperature sustava")
                    self._calculate_temperature()
            
            with col2:
                st.subheader("Rezultati")
                
                if self.results['t_m'] > 0:
                    st.metric("Srednja temperatura", f"{self.results['t_m']:.2f} °C")
                    st.metric("Gustoća vode", f"{self.results['density']:.2f} kg/m³")
                    st.metric("Koeficijent širenja", f"{self.results['n']:.6f} %")
                
                # Gumb za izračun
                st.button("Izračunaj temperaturu", key="calc_temp", on_click=self._calculate_temperature)
        
        # ---------------------- TAB: VOLUMEN SUSTAVA ----------------------
        with tabs[1]:
            st.header("Volumen sustava")
            
            # Sustav tabova za unos različitih komponenti
            vol_tabs = st.tabs(["Cijevi", "Uređaji", "Spremnici", "Ukupno"])
            
            # -------- Cijevi --------
            with vol_tabs[0]:
                self._render_pipes_input()
            
            # -------- Uređaji --------
            with vol_tabs[1]:
                self._render_devices_input()
            
            # -------- Spremnici --------
            with vol_tabs[2]:
                self._render_containers_input()
            
            # -------- Ukupni volumen --------
            with vol_tabs[3]:
                self._render_volume_summary()
                
                col1, col2 = st.columns(2)
                with col1:
                    # Unos ukupnog volumena ako ga korisnik želi direktno unijeti
                    direct_volume = st.number_input(
                        "Ručni unos volumena (l)",
                        min_value=0.0,
                        max_value=100000.0,
                        value=0.0,
                        step=10.0
                    )
                    
                    if st.button("Postavi", key="set_manual_volume"):
                        if direct_volume > 0:
                            old_volume = self.total_system_volume
                            self.total_system_volume = direct_volume
                            
                            if old_volume != direct_volume:
                                self.record_state("Promjena volumena")
                                # Ponovno izračunaj volumene širenja
                                self._calculate_expansion_volume()
                
                with col2:
                    if self.results['v_e'] > 0:
                        st.metric("Volumen širenja", f"{self.results['v_e']:.2f} l")
                        st.metric("Dodatni volumen", f"{self.results['v_v']:.2f} l")
        
        # ---------------------- TAB: TLAKOVI I REZULTATI ----------------------
        with tabs[2]:
            st.header("Tlakovi i rezultati")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Sačuvaj stare vrijednosti za usporedbu
                old_h = self.h
                old_min_req = self.p_min_req
                old_pe = self.p_e
                
                # Unos parametara
                self.h = st.number_input(
                    "Visinska razlika (m)",
                    min_value=0.1,
                    max_value=100.0,
                    value=float(self.h),
                    step=1.0,
                    key="h"
                )
                
                has_min_req = st.checkbox(
                    "Poseban zahtjev minimalnog tlaka", 
                    value=(self.p_min_req > 0)
                )
                
                if has_min_req:
                    self.p_min_req = st.number_input(
                        "Minimalni tlak (bar)",
                        min_value=0.0,
                        max_value=10.0,
                        value=max(1.0, float(self.p_min_req)),
                        step=0.1,
                        key="p_min_req"
                    )
                else:
                    self.p_min_req = 0.0
                
                # Izračunaj P_o ako su se promijenili parametri
                if old_h != self.h or old_min_req != self.p_min_req:
                    self.record_state("Promjena tlakova")
                    self._calculate_pressure()
                
                # Unos tlaka sigurnosnog ventila
                if self.results['p_o'] > 0:
                    st.markdown("---")
                    st.info(f"Minimalni tlak ventila: {self.results['p_o'] + 0.5:.2f} bar")
                    
                    self.p_e = st.number_input(
                        "Tlak sigurnosnog ventila (bar)",
                        min_value=float(self.results['p_o'] + 0.5),
                        max_value=10.0,
                        value=max(float(self.p_e), float(self.results['p_o'] + 0.5)),
                        step=0.1,
                        key="p_e"
                    )
                    
                    # Izračunaj nazivni volumen ako se promijenio tlak ventila
                    if old_pe != self.p_e:
                        self._calculate_nominal_volume()
            
            with col2:
                st.subheader("Rezultati")
                
                if self.results['p_st'] > 0:
                    st.metric("Statički tlak", f"{self.results['p_st']:.2f} bar")
                    st.metric("Minimalni radni tlak", f"{self.results['p_o']:.2f} bar")
                
                if self.results['v_n'] > 0:
                    st.metric("Nazivni volumen", f"{self.results['v_n']:.2f} l")
                    
                    # Prikaz konačnog rezultata
                    st.markdown("---")
                    st.markdown(
                        f"""
                        <div style="background-color:#f0f8ff; padding:15px; border-radius:5px;">
                            <h3>Potrebna ekspanzijska posuda</h3>
                            <p style="font-size:22px; font-weight:bold;">{self.results['standard_size']} litara</p>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            
            # Gumb za finalni izračun
            if st.button("Izračunaj", key="calc_vessel", use_container_width=True):
                self._calculate_all()
            
            # Gumb za izvoz rezultata
            if self.results['standard_size'] > 0:
                st.button("Izvoz u Word", key="export_word", on_click=lambda: st.session_state.word_export.export_current_calculation())

    def _render_pipes_input(self):
        """
        Prikazuje sučelje za unos cijevi
        """
        st.subheader("Cijevi")
        
        # Prikaži trenutni popis cijevi
        if self.volumes["Cijevi"]:
            st.write("**Dodane cijevi:**")
            for i, pipe in enumerate(self.volumes["Cijevi"]):
                st.write(f"{i+1}. {pipe['tip']} {pipe['dimenzija']}, L={pipe['duljina']:.2f}m: {pipe['volumen']:.2f} l")
            
            # Opcija brisanja
            if st.button("Obriši sve cijevi", key="delete_all_pipes"):
                self.record_state("Brisanje svih cijevi")
                self.volumes["Cijevi"] = []
                self._update_total_volume()
        
        # Nova cijev
        st.markdown("---")
        st.write("**Dodaj novu cijev:**")
        
        pipe_db = self._get_pipe_database()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Odabir vrste cijevi
            pipe_types = list(pipe_db.keys())
            pipe_type = st.selectbox("Vrsta cijevi", options=pipe_types, key="new_pipe_type")
            
            # Odabir dimenzije
            dimensions = list(pipe_db[pipe_type].keys())
            dimension = st.selectbox("Dimenzija", options=dimensions, key="new_pipe_dim")
            
            # Unos duljine
            length = st.number_input("Duljina cijevi (m)", min_value=0.1, value=10.0, step=1.0, key="new_pipe_length")
        
        with col2:
            if pipe_type and dimension and length > 0:
                # Prikaz izabranog promjera
                inner_diameter = pipe_db[pipe_type][dimension]["unutarnji_promjer"]
                st.write(f"**Unutarnji promjer**: {inner_diameter:.1f} mm")
                
                # Izračun volumena
                volume = self._calculate_pipe_volume(inner_diameter, length)
                st.write(f"**Volumen**: {volume:.2f} l")
                
                # Gumb za dodavanje
                if st.button("Dodaj cijev", key="add_pipe"):
                    self.record_state("Dodavanje cijevi")
                    self.volumes["Cijevi"].append({
                        "tip": pipe_type,
                        "dimenzija": dimension,
                        "duljina": length,
                        "volumen": volume
                    })
                    self._update_total_volume()
                    st.experimental_rerun()

    def _render_devices_input(self):
        """
        Prikazuje sučelje za unos uređaja
        """
        st.subheader("Uređaji")
        
        # Prikaži trenutni popis uređaja
        if self.volumes["Uređaji"]:
            st.write("**Dodani uređaji:**")
            for i, device in enumerate(self.volumes["Uređaji"]):
                if "broj_članaka" in device:
                    st.write(f"{i+1}. {device['tip']}, {int(device['broj_članaka'])} članaka: {device['volumen']:.2f} l")
                elif "duljina" in device:
                    st.write(f"{i+1}. {device['tip']}, L={device['duljina']:.2f}m: {device['volumen']:.2f} l")
                else:
                    st.write(f"{i+1}. {device['tip']}: {device['volumen']:.2f} l")
            
            # Opcija brisanja
            if st.button("Obriši sve uređaje", key="delete_all_devices"):
                self.record_state("Brisanje svih uređaja")
                self.volumes["Uređaji"] = []
                self._update_total_volume()
        
        # Novi uređaj
        st.markdown("---")
        st.write("**Dodaj novi uređaj:**")
        
        device_types = ["Kotao", "Radijator člankasti", "Radijator pločasti", "Ventilokonvektor", "Ostali uređaj"]
        device_type = st.selectbox("Vrsta uređaja", options=device_types, key="new_device_type")
        
        if device_type == "Kotao":
            col1, col2 = st.columns(2)
            
            with col1:
                kot_types = ["Plinski zidni (2-5 l)", "Plinski podni (8-25 l)", "Ostali kotao"]
                kot_type = st.selectbox("Tip kotla", options=kot_types)
                
                if kot_type == "Plinski zidni (2-5 l)":
                    st.write("**Tipični volumeni:**")
                    st.write("- 2 l\n- 3 l\n- 4 l\n- 5 l")
                elif kot_type == "Plinski podni (8-25 l)":
                    st.write("**Tipični volumeni:**")
                    st.write("- 8 l\n- 12 l\n- 15 l\n- 20 l\n- 25 l")
                
                volume = st.number_input("Volumen vode u kotlu (l)", min_value=0.1, value=3.0, step=1.0)
            
            with col2:
                if st.button("Dodaj kotao", key="add_boiler"):
                    self.record_state("Dodavanje kotla")
                    self.volumes["Uređaji"].append({
                        "tip": f"Kotao - {kot_type}",
                        "volumen": volume
                    })
                    self._update_total_volume()
                    st.experimental_rerun()
        
        elif device_type == "Radijator člankasti":
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Tipični volumeni po članku:**")
                st.write("- 1 članak ≈ 0,2 l")
                st.write("- 5 članaka ≈ 1,0 l")
                st.write("- 10 članaka ≈ 2,0 l")
                st.write("- 15 članaka ≈ 3,0 l")
                
                num_elements = st.number_input("Broj članaka", min_value=1, value=10, step=1)
                volume = num_elements * 0.2
            
            with col2:
                st.write(f"**Izračunati volumen**: {volume:.2f} l")
                
                if st.button("Dodaj člankasti radijator", key="add_radiator"):
                    self.record_state("Dodavanje člankastog radijatora")
                    self.volumes["Uređaji"].append({
                        "tip": "Radijator člankasti",
                        "broj_članaka": num_elements,
                        "volumen": volume
                    })
                    self._update_total_volume()
                    st.experimental_rerun()
        
        elif device_type == "Radijator pločasti":
            col1, col2 = st.columns(2)
            
            with col1:
                rad_types = {
                    "Tip 11 (1,9 l/m)": 1.9,
                    "Tip 21 (2,7 l/m)": 2.7,
                    "Tip 22 (3,4 l/m)": 3.4,
                    "Tip 33 (5,0 l/m)": 5.0
                }
                
                rad_type = st.selectbox("Tip pločastog radijatora", options=list(rad_types.keys()))
                litara_po_metru = rad_types[rad_type]
                
                length = st.number_input("Duljina radijatora (m)", min_value=0.4, value=1.0, step=0.2)
                volume = length * litara_po_metru
            
            with col2:
                st.write(f"**Izračunati volumen**: {volume:.2f} l")
                
                if st.button("Dodaj pločasti radijator", key="add_panel_radiator"):
                    self.record_state("Dodavanje pločastog radijatora")
                    self.volumes["Uređaji"].append({
                        "tip": rad_type.split(" ")[0] + " " + rad_type.split(" ")[1],
                        "duljina": length,
                        "volumen": volume
                    })
                    self._update_total_volume()
                    st.experimental_rerun()
        
        elif device_type == "Ventilokonvektor":
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Tipični volumeni ventilokonvektora:**")
                st.write("- mali (do 2 kW): 0,5 l")
                st.write("- srednji (2-4 kW): 1,0 l")
                st.write("- veliki (preko 4 kW): 1,5 l")
                
                volume = st.number_input("Volumen vode u ventilokonvektoru (l)", min_value=0.1, value=1.0, step=0.1)
            
            with col2:
                if st.button("Dodaj ventilokonvektor", key="add_fan_coil"):
                    self.record_state("Dodavanje ventilokonvektora")
                    self.volumes["Uređaji"].append({
                        "tip": "Ventilokonvektor",
                        "volumen": volume
                    })
                    self._update_total_volume()
                    st.experimental_rerun()
        
        elif device_type == "Ostali uređaj":
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Naziv uređaja", value="")
                volume = st.number_input("Volumen vode u uređaju (l)", min_value=0.1, value=1.0, step=0.1)
            
            with col2:
                if st.button("Dodaj uređaj", key="add_other_device") and name:
                    self.record_state("Dodavanje uređaja")
                    self.volumes["Uređaji"].append({
                        "tip": name,
                        "volumen": volume
                    })
                    self._update_total_volume()
                    st.experimental_rerun()

    def _render_containers_input(self):
        """
        Prikazuje sučelje za unos spremnika
        """
        st.subheader("Spremnici")
        
        # Prikaži trenutni popis spremnika
        if self.volumes["Spremnici"]:
            st.write("**Dodani spremnici:**")
            for i, container in enumerate(self.volumes["Spremnici"]):
                st.write(f"{i+1}. {container['tip']}: {container['volumen']:.2f} l")
            
            # Opcija brisanja
            if st.button("Obriši sve spremnike", key="delete_all_containers"):
                self.record_state("Brisanje svih spremnika")
                self.volumes["Spremnici"] = []
                self._update_total_volume()
        
        # Novi spremnik
        st.markdown("---")
        st.write("**Dodaj novi spremnik:**")
        
        container_types = [
            "Akumulacijski spremnik (300-2000 l)",
            "Spremnik potrošne tople vode (150-500 l)",
            "Međuspremnik (200-1000 l)",
            "Ostali spremnik"
        ]
        
        container_type = st.selectbox("Vrsta spremnika", options=container_types, key="new_container_type")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if container_type == "Akumulacijski spremnik (300-2000 l)":
                st.write("**Dostupni volumeni:**")
                st.write("- 300 l\n- 500 l\n- 800 l\n- 1000 l\n- 1500 l\n- 2000 l")
                volume = st.number_input("Volumen spremnika (l)", min_value=100.0, value=500.0, step=100.0)
                name = "Akumulacijski spremnik"
                
            elif container_type == "Spremnik potrošne tople vode (150-500 l)":
                st.write("**Dostupni volumeni:**")
                st.write("- 150 l\n- 200 l\n- 300 l\n- 400 l\n- 500 l")
                volume = st.number_input("Volumen spremnika (l)", min_value=50.0, value=200.0, step=50.0)
                name = "Spremnik potrošne tople vode"
                
            elif container_type == "Međuspremnik (200-1000 l)":
                st.write("**Dostupni volumeni:**")
                st.write("- 200 l\n- 300 l\n- 500 l\n- 800 l\n- 1000 l")
                volume = st.number_input("Volumen spremnika (l)", min_value=100.0, value=300.0, step=100.0)
                name = "Međuspremnik"
                
            else:  # Ostali spremnik
                name = st.text_input("Naziv spremnika", value="")
                volume = st.number_input("Volumen spremnika (l)", min_value=1.0, value=100.0, step=10.0)
        
        with col2:
            if st.button("Dodaj spremnik", key="add_container") and (name or container_type != "Ostali spremnik"):
                self.record_state("Dodavanje spremnika")
                self.volumes["Spremnici"].append({
                    "tip": name,
                    "volumen": volume
                })
                self._update_total_volume()
                st.experimental_rerun()

    def _render_volume_summary(self):
        """
        Prikazuje pregled ukupnog volumena sustava
        """
        st.subheader("Ukupni volumen sustava")
        
        total = 0
        
        if self.volumes["Cijevi"]:
            subtotal = sum(pipe['volumen'] for pipe in self.volumes["Cijevi"])
            st.write(f"**Cijevi**: {subtotal:.2f} l")
            total += subtotal
        
        if self.volumes["Uređaji"]:
            subtotal = sum(device['volumen'] for device in self.volumes["Uređaji"])
            st.write(f"**Uređaji**: {subtotal:.2f} l")
            total += subtotal
        
        if self.volumes["Spremnici"]:
            subtotal = sum(container['volumen'] for container in self.volumes["Spremnici"])
            st.write(f"**Spremnici**: {subtotal:.2f} l")
            total += subtotal
        
        st.markdown("---")
        st.write(f"**UKUPNI VOLUMEN VODE U SUSTAVU: {self.total_system_volume:.2f} l")
    
    def _update_total_volume(self):
        """
        Ažurira ukupni volumen sustava
        """
        total = 0
        total += sum(pipe['volumen'] for pipe in self.volumes["Cijevi"])
        total += sum(device['volumen'] for device in self.volumes["Uređaji"])
        total += sum(container['volumen'] for container in self.volumes["Spremnici"])
        
        if total != self.total_system_volume:
            self.total_system_volume = total
            self._calculate_expansion_volume()

    def _calculate_temperature(self):
        """
        Izračunava srednju temperaturu i koeficijent širenja
        """
        try:
            # Srednja temperatura
            self.results['t_m'] = (self.t_v + self.t_r) / 2.0
            
            # Zaokružena temperatura
            t_m_rounded = int(self.results['t_m'] + 0.5)  # Zaokruži na najbliži cijeli broj
            if t_m_rounded < self.results['t_m']:  # Ako je zaokruženo prema dolje, dodaj 1
                t_m_rounded += 1
            self.results['t_m_rounded'] = t_m_rounded
            
            # Gustoća vode
            density = self._get_water_density(t_m_rounded)
            if density is None:
                st.error(f"Temperatura {t_m_rounded} °C izvan je raspona tablice (0-100°C)")
                return
            self.results['density'] = density
            
            # Koeficijent širenja
            self.results['n'] = (999.73/float(density) - 1.0) * 100.0
            
            # Izračunaj volumen širenja ako postoji ukupni volumen
            if self.total_system_volume > 0:
                self._calculate_expansion_volume()
                
        except Exception as e:
            st.error(f"Greška u izračunu temperature: {str(e)}")

    def _calculate_pressure(self):
        """
        Izračunava tlakove u sustavu
        """
        try:
            # Statički tlak
            self.results['p_st'] = self.h * 0.1
            
            # Minimalni radni tlak
            if self.results['t_m_rounded'] <= 100.0:
                self.results['p_o'] = max(self.results['p_st'] + 0.5, 1.2, self.p_min_req)
            else:
                self.results['p_o'] = max(self.results['p_st'] + 0.7, 1.2, self.p_min_req)
            
            # Izračunaj nazivni volumen ako imamo sve potrebne parametre
            if self.p_e > self.results['p_o'] + 0.5 and self.results['v_e'] > 0:
                self._calculate_nominal_volume()
                
        except Exception as e:
            st.error(f"Greška u izračunu tlaka: {str(e)}")

    def _calculate_expansion_volume(self):
        """
        Izračunava volumen širenja vode
        """
        try:
            if self.total_system_volume <= 0 or self.results['n'] <= 0:
                return
            
            # Volumen širenja vode
            self.results['v_e'] = self.total_system_volume * (self.results['n']/100.0)
            
            # Dodatni volumen
            self.results['v_v'] = max(3.0, 0.005 * self.total_system_volume)
            
            # Izračunaj nazivni volumen ako imamo sve potrebne parametre
            if self.p_e > 0 and self.results['p_o'] > 0 and self.p_e > self.results['p_o']:
                self._calculate_nominal_volume()
                
        except Exception as e:
            st.error(f"Greška u izračunu volumena širenja: {str(e)}")

    def _calculate_nominal_volume(self):
        """
        Izračunava nazivni volumen ekspanzijske posude
        """
        try:
            if self.results['v_e'] <= 0 or self.results['v_v'] <= 0:
                return
                
            if self.p_e <= self.results['p_o']:
                st.error(f"Tlak sigurnosnog ventila ({self.p_e:.2f} bar) mora biti veći od minimalnog radnog tlaka ({self.results['p_o']:.2f} bar)")
                return
            
            # Nazivni volumen ekspanzijske posude
            self.results['v_n'] = (self.results['v_e'] + self.results['v_v']) * (self.p_e + 1.0)/(self.p_e - self.results['p_o'])
            
            # Standardna veličina posude
            self.results['standard_size'] = self._get_standard_vessel_size(self.results['v_n'])
            
        except Exception as e:
            st.error(f"Greška u izračunu nazivnog volumena: {str(e)}")

    def _calculate_all(self):
        """
        Provodi kompletan izračun
        """
        self.record_state("Izračun ekspanzijske posude")
        self._calculate_temperature()
        self._calculate_pressure()
        self._calculate_expansion_volume()
        self._calculate_nominal_volume()

    def _get_water_density(self, temp):
        """
        Vraća gustoću vode na temelju temperature
        """
        density_table = {
            0: 999.87, 1: 999.92, 2: 999.97, 3: 999.99, 4: 1000.00,
            5: 999.99, 6: 999.97, 7: 999.93, 8: 999.88, 9: 999.81,
            10: 999.73, 11: 999.63, 12: 999.53, 13: 999.40, 14: 999.27,
            15: 999.12, 16: 998.97, 17: 998.80, 18: 998.62, 19: 998.43,
            20: 998.23, 21: 998.02, 22: 997.80, 23: 997.56, 24: 997.32,
            25: 997.07, 26: 996.81, 27: 996.54, 28: 996.26, 29: 995.97,
            30: 995.67, 31: 995.36, 32: 995.05, 33: 994.73, 34: 994.40,
            35: 994.06, 36: 993.71, 37: 993.36, 38: 993.00, 39: 992.60,
            40: 992.20, 41: 991.85, 42: 991.50, 43: 991.10, 44: 990.70,
            45: 990.25, 46: 989.80, 47: 989.40, 48: 989.00, 49: 988.55,
            50: 988.10, 51: 987.65, 52: 987.20, 53: 986.70, 54: 986.20,
            55: 985.80, 56: 985.30, 57: 984.80, 58: 984.30, 59: 983.80,
            60: 983.20, 61: 982.70, 62: 982.20, 63: 981.70, 64: 981.10,
            65: 980.60, 66: 980.10, 67: 979.50, 68: 978.90, 69: 978.40,
            70: 977.80, 71: 977.30, 72: 976.70, 73: 976.10, 74: 975.50,
            75: 974.90, 76: 974.30, 77: 973.70, 78: 973.10, 79: 972.50,
            80: 971.80, 81: 971.20, 82: 970.60, 83: 970.00, 84: 969.30,
            85: 968.70, 86: 968.00, 87: 967.40, 88: 966.70, 89: 966.00,
            90: 965.30, 91: 964.70, 92: 964.00, 93: 963.30, 94: 962.60,
            95: 961.90, 96: 961.20, 97: 960.50, 98: 959.80, 99: 959.10,
            100: 958.40
        }
        return density_table.get(temp, None)

    def _get_pipe_database(self):
        """
        Vraća bazu podataka o cijevima
        """
        return {
            "PE-Xa cijev": {
                "14x2.0": {"unutarnji_promjer": 10.0},  # 14mm vanjski
                "16x2.0": {"unutarnji_promjer": 12.0},  # 16mm vanjski
                "17x2.0": {"unutarnji_promjer": 13.0},  # 17mm vanjski
                "20x2.0": {"unutarnji_promjer": 16.0},  # 20mm vanjski
                "25x2.3": {"unutarnji_promjer": 20.4},  # 25mm vanjski
            },
            "Bakrena cijev": {
                "12x1.0": {"unutarnji_promjer": 10.0},    # Nominal 10mm
                "15x1.0": {"unutarnji_promjer": 13.0},    # Nominal 12mm
                "18x1.0": {"unutarnji_promjer": 16.0},    # Nominal 15mm
                "22x1.0": {"unutarnji_promjer": 20.0},    # Nominal 20mm
                "28x1.5": {"unutarnji_promjer": 25.0},    # Nominal 25mm
                "35x1.5": {"unutarnji_promjer": 32.0},    # Nominal 32mm
                "42x1.5": {"unutarnji_promjer": 39.0},    # Nominal 40mm
                "54x2.0": {"unutarnji_promjer": 50.0},    # Nominal 50mm
                "64x2.0": {"unutarnji_promjer": 60.0},    # Nominal 60mm
                "76.1x2.0": {"unutarnji_promjer": 72.1},  # Nominal 65mm
                "88.9x2.0": {"unutarnji_promjer": 84.9},  # Nominal 80mm
                "108x2.5": {"unutarnji_promjer": 103.0}   # Nominal 100mm
            },
            "PE-RT/Al/PE-RT cijev": {
                "16x2.0": {"unutarnji_promjer": 12},     # 16mm vanjski
                "20x2.3": {"unutarnji_promjer": 15.4},   # 20mm vanjski
                "25x2.5": {"unutarnji_promjer": 20},     # 25mm vanjski
                "32x3.0": {"unutarnji_promjer": 26}      # 32mm vanjski
            }
        }

    def _calculate_pipe_volume(self, diameter_mm, length_m):
        """
        Izračunava volumen vode u cijevi
        """
        return math.pi * ((diameter_mm/1000)/2)**2 * length_m * 1000  # rezultat u litrama

    def _get_standard_vessel_size(self, calculated_volume):
        """
        Vraća standardnu veličinu ekspanzijske posude
        """
        standard_sizes = [8, 12, 18, 24, 35, 50, 80, 100, 150, 200, 250, 300, 400, 
                         500, 600, 800, 1000, 1500, 2000, 3000, 5000]
        
        for size in standard_sizes:
            if size >= calculated_volume:
                return size
        
        return standard_sizes[-1]  # Vraća najveću dostupnu ako je izračun veći
    
    def export_to_word(self, doc):
        """
        Izvoz proračuna u Word dokument
        
        Args:
            doc: Word dokument (python-docx Document objekt)
        """
        # Dodavanje naslova i opisa
        doc.add_heading("Proračun ekspanzijske posude", level=1)
        doc.add_paragraph("Proračun volumena zatvorene membranske ekspanzijske posude za sustave grijanja.")
        
        # 1. Temperatura sustava
        doc.add_heading("1. Temperatura sustava", level=2)
        table = doc.add_table(rows=3, cols=2)
        table.style = 'Table Grid'
        
        # Zaglavlje
        table.cell(0, 0).text = "Parametar"
        table.cell(0, 1).text = "Vrijednost"
        
        # Podaci temperature
        table.cell(1, 0).text = "Temperatura polaza"
        table.cell(1, 1).text = f"{self.t_v:.1f} °C"
        
        table.cell(2, 0).text = "Temperatura povrata"
        table.cell(2, 1).text = f"{self.t_r:.1f} °C"
        
        # Rezultati temperature
        doc.add_paragraph(f"Srednja temperatura sustava: {self.results['t_m']:.2f} °C")
        doc.add_paragraph(f"Zaokružena temperatura: {self.results['t_m_rounded']} °C")
        doc.add_paragraph(f"Gustoća vode: {self.results['density']:.2f} kg/m³")
        doc.add_paragraph(f"Koeficijent širenja: {self.results['n']:.6f} %")
        
        # 2. Volumen sustava
        doc.add_heading("2. Volumen sustava", level=2)
        
        # Cijevi
        if self.volumes["Cijevi"]:
            doc.add_heading("Cijevi", level=3)
            table = doc.add_table(rows=len(self.volumes["Cijevi"])+1, cols=4)
            table.style = 'Table Grid'
            
            # Zaglavlje
            table.cell(0, 0).text = "Vrsta"
            table.cell(0, 1).text = "Dimenzija"
            table.cell(0, 2).text = "Duljina (m)"
            table.cell(0, 3).text = "Volumen (l)"
            
            # Podaci
            for i, pipe in enumerate(self.volumes["Cijevi"]):
                table.cell(i+1, 0).text = pipe["tip"]
                table.cell(i+1, 1).text = pipe["dimenzija"]
                table.cell(i+1, 2).text = f"{pipe['duljina']:.2f}"
                table.cell(i+1, 3).text = f"{pipe['volumen']:.2f}"
        
        # Uređaji
        if self.volumes["Uređaji"]:
            doc.add_heading("Uređaji", level=3)
            table = doc.add_table(rows=len(self.volumes["Uređaji"])+1, cols=2)
            table.style = 'Table Grid'
            
            # Zaglavlje
            table.cell(0, 0).text = "Naziv"
            table.cell(0, 1).text = "Volumen (l)"
            
            # Podaci
            for i, device in enumerate(self.volumes["Uređaji"]):
                device_name = device["tip"]
                if "broj_članaka" in device:
                    device_name += f" ({int(device['broj_članaka'])} članaka)"
                elif "duljina" in device:
                    device_name += f" (L={device['duljina']:.2f}m)"
                
                table.cell(i+1, 0).text = device_name
                table.cell(i+1, 1).text = f"{device['volumen']:.2f}"
        
        # Spremnici
        if self.volumes["Spremnici"]:
            doc.add_heading("Spremnici", level=3)
            table = doc.add_table(rows=len(self.volumes["Spremnici"])+1, cols=2)
            table.style = 'Table Grid'
            
            # Zaglavlje
            table.cell(0, 0).text = "Naziv"
            table.cell(0, 1).text = "Volumen (l)"
            
            # Podaci
            for i, container in enumerate(self.volumes["Spremnici"]):
                table.cell(i+1, 0).text = container["tip"]
                table.cell(i+1, 1).text = f"{container['volumen']:.2f}"
        
        # Ukupni volumen
        doc.add_paragraph(f"UKUPNI VOLUMEN VODE U SUSTAVU: {self.total_system_volume:.2f} l")
        
        # 3. Tlakovi i rezultati
        doc.add_heading("3. Tlakovi i rezultati", level=2)
        table = doc.add_table(rows=6, cols=2)
        table.style = 'Table Grid'
        
        # Zaglavlje
        table.cell(0, 0).text = "Parametar"
        table.cell(0, 1).text = "Vrijednost"
        
        # Podaci tlakova i rezultata
        table.cell(1, 0).text = "Visinska razlika"
        table.cell(1, 1).text = f"{self.h:.2f} m"
        
        table.cell(2, 0).text = "Statički tlak Pst"
        table.cell(2, 1).text = f"{self.results['p_st']:.2f} bar"
        
        table.cell(3, 0).text = "Minimalni radni tlak Po"
        table.cell(3, 1).text = f"{self.results['p_o']:.2f} bar"
        
        table.cell(4, 0).text = "Tlak sigurnosnog ventila Pe"
        table.cell(4, 1).text = f"{self.p_e:.2f} bar"
        
        table.cell(5, 0).text = "Izračunati volumen Vn"
        table.cell(5, 1).text = f"{self.results['v_n']:.2f} l"
        
        # 4. Konačan rezultat
        doc.add_heading("4. Konačan rezultat", level=2)
        doc.add_paragraph(f"Potrebna ekspanzijska posuda: {self.results['standard_size']} l")
