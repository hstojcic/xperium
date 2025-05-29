"""
Additional UI components for chimney sizing calculator.
Dodatne UI komponente za kalkulator dimnjaka.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any
from .constants import CONDENSING_BOILERS, CHIMNEY_SYSTEMS, CONNECTING_ELEMENTS, VALIDATION_LIMITS

def render_boiler_selector():
    """
    Renders a boiler selection widget with predefined boilers.
    Prikazuje widget za odabir kotla iz predefiniranih modela.
    """
    st.subheader("🔥 Odabir predefiniranog kotla")
    
    boiler_options = list(CONDENSING_BOILERS.keys())
    boiler_options.insert(0, "Vlastiti unos")
    
    selected_boiler = st.selectbox(
        "Odaberite model kotla:",
        boiler_options,
        key="boiler_selector"
    )
    
    if selected_boiler != "Vlastiti unos":
        boiler_data = CONDENSING_BOILERS[selected_boiler]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Gorivo:** {boiler_data['fuel']}")
            st.info(f"**Puno opterećenje:** {boiler_data['full_load']['nominal_heat_output']} kW")
            st.info(f"**CO2:** {boiler_data['full_load']['co2_percentage']}%")
        
        with col2:
            st.info(f"**Temp. dimnih plinova:** {boiler_data['full_load']['flue_gas_temperature']}°C")
            st.info(f"**Maseni protok:** {boiler_data['full_load']['flue_gas_mass_flow']} g/s")
            st.info(f"**Priključak:** Ø{boiler_data['connection']['diameter']} mm")
        
        if st.button("📋 Koristi ovaj kotao", key="use_selected_boiler"):
            return boiler_data
    
    return None

def render_chimney_selector():
    """
    Renders a chimney system selection widget.
    Prikazuje widget za odabir dimnjaka iz predefiniranih sustava.
    """
    st.subheader("🏗️ Odabir predefiniranog dimnjaka")
    
    chimney_options = list(CHIMNEY_SYSTEMS.keys())
    chimney_options.insert(0, "Vlastiti unos")
    
    selected_chimney = st.selectbox(
        "Odaberite sustav dimnjaka:",
        chimney_options,
        key="chimney_selector"
    )
    
    if selected_chimney != "Vlastiti unos":
        chimney_data = CHIMNEY_SYSTEMS[selected_chimney]
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Tip:** {chimney_data['type']}")
            st.info(f"**Proizvođač:** {chimney_data['manufacturer']}")
            st.info(f"**Promjer:** Ø{chimney_data['inner_diameter']} mm")
        
        with col2:
            st.info(f"**Materijal:** {chimney_data['material']}")
            st.info(f"**Debljina:** {chimney_data['thickness']} mm")
            st.info(f"**Hrapavost:** {chimney_data['roughness']} mm")
        
        if st.button("🔧 Koristi ovaj dimnjak", key="use_selected_chimney"):
            return chimney_data
    
    return None

def render_validation_summary(errors: List[str], warnings: List[str]):
    """
    Renders validation results in a formatted way.
    Prikazuje rezultate validacije u formatu.
    """
    if errors or warnings:
        st.subheader("⚠️ Validacija podataka")
        
        if errors:
            st.error("**Greške koje trebaju ispravak:**")
            for error in errors:
                st.error(f"• {error}")
        
        if warnings:
            st.warning("**Upozorenja:**")
            for warning in warnings:
                st.warning(f"• {warning}")
    else:
        st.success("✅ Svi podaci prošli validaciju!")

def render_calculation_summary(results: Dict[str, Any]):
    """
    Renders a compact calculation summary.
    Prikazuje sažetak rezultata proračuna.
    """
    if not results or not results.get("pressure_conditions"):
        return
    
    st.subheader("📊 Brzi pregled rezultata")
    
    # Kreiranje metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pressure_status = results["pressure_conditions"].get("status", "N/A")
        if "Zadovoljava" in pressure_status:
            st.metric("Tlačni uvjeti", "✅ OK", delta="Zadovoljava")
        else:
            st.metric("Tlačni uvjeti", "❌ NOK", delta="Ne zadovoljava")
    
    with col2:
        working_status = results["working_pressures"].get("status", "N/A")
        if "Zadovoljava" in working_status:
            st.metric("Radni tlakovi", "✅ OK", delta="Zadovoljava")
        else:
            st.metric("Radni tlakovi", "❌ NOK", delta="Ne zadovoljava")
    
    with col3:
        backflow_status = results["backflow"].get("status", "N/A")
        if "Ne dolazi" in backflow_status:
            st.metric("Povrat plinova", "✅ OK", delta="Nema povrata")
        else:
            st.metric("Povrat plinova", "❌ NOK", delta="Moguć povrat")
    
    with col4:
        temp_status = results["temperature_conditions"].get("status", "N/A")
        if "Zadovoljava" in temp_status:
            st.metric("Temp. uvjeti", "✅ OK", delta="Zadovoljava")
        else:
            st.metric("Temp. uvjeti", "❌ NOK", delta="Ne zadovoljava")

def render_technical_data_table(data: Dict[str, Any]):
    """
    Renders technical data in a formatted table.
    Prikazuje tehničke podatke u formatiranoj tablici.
    """
    st.subheader("📋 Tehnički podaci")
    
    # Kreiranje tablice s ključnim podacima
    table_data = []
    
    # Općeniti podaci
    general = data.get("general", {})
    table_data.append(["Lokacija", general.get("location", "N/A")])
    table_data.append(["Geodetska visina", f"{general.get('geodetic_height', 0)} m"])
    table_data.append(["Sigurnosni broj SE", general.get("safety_number_SE", 1.2)])
    
    # Dimnjak podaci
    chimney = data.get("chimney", {})
    chimney_height = sum(section.get("effective_height", 0) for section in chimney.get("sections", []))
    table_data.append(["Visina dimnjaka", f"{chimney_height:.1f} m"])
    table_data.append(["Promjer dimnjaka", f"Ø{chimney.get('inner_diameter', 0)} mm"])
    table_data.append(["Materijal dimnjaka", chimney.get("material", "N/A")])
    
    # Ložišta podaci
    appliances = data.get("appliances", [])
    if appliances:
        table_data.append(["Broj ložišta", len(appliances)])
        table_data.append(["Gorivo", appliances[0].get("fuel", "N/A")])
        table_data.append(["Snaga kotla", f"{appliances[0].get('full_load', {}).get('nominal_heat_output', 0)} kW"])
    
    # Prikazivanje tablice
    df = pd.DataFrame(table_data, columns=["Parametar", "Vrijednost"])
    st.dataframe(df, hide_index=True, width=600)

def render_help_section():
    """
    Renders help section with usage instructions.
    Prikazuje sekciju pomoći s uputama za korištenje.
    """
    with st.expander("❓ Pomoć i upute za korištenje"):
        st.markdown("""
        ## 🎯 Kako koristiti kalkulator
        
        ### 1. Opći parametri
        - Unesite lokaciju i geodetsku visinu
        - Postavite sigurnosne faktore (preporuča se SE = 1.2)
        - Definirajte temperature okolnog zraka
        
        ### 2. Ložišta
        - Dodajte ložišta (do 5 prema EN 13384-2)
        - Unesite podatke za puno i djelomično opterećenje
        - Provjerite da je CO2 udio u optimalnom rasponu
        
        ### 3. Spojni elementi
        - Definirajte spojne elemente između ložišta i dimnjaka
        - Unesite hrapavost i otpore
        
        ### 4. Dimovod
        - Unesite dimenzije i materijal dimnjaka
        - Dodajte sekcije dimnjaka
        - Definirajte otpore na ulazu i izlazu
        
        ### 5. Rezultati
        - Pokrenite izračun
        - Provjerite sva četiri uvjeta prema normi
        - Implementirajte preporuke ako je potrebno
        
        ## ⚠️ Važne napomene
        
        - Kalkulator slijedi EN 13384-2:2015+A1:2019
        - Svi uvjeti moraju biti zadovoljeni
        - Kondenzacijska ložišta zahtijevaju dimnjake otporne na kondenzat
        - Validacija će upozoriti na problematične vrijednosti
        
        ## 🔧 Česti problemi
        
        - **Nizak CO2**: Previše viška zraka - podestite ložište
        - **Slab uzgon**: Povećajte visinu ili promjer dimnjaka
        - **Kondenzacija**: Poboljšajte izolaciju dimnjaka
        - **Povrat plinova**: Smanjite broj ložišta ili povećajte dimnjak
        """)

def render_export_options(data: Dict[str, Any]):
    """
    Renders export options for calculation results.
    Prikazuje opcije izvoza rezultata proračuna.
    """
    st.subheader("📤 Izvoz rezultata")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Izvezi PDF", key="export_pdf"):
            st.info("PDF izvoz će biti implementiran u budućoj verziji")
    
    with col2:
        if st.button("📊 Izvezi Excel", key="export_excel"):
            st.info("Excel izvoz će biti implementiran u budućoj verziji")
    
    with col3:
        if st.button("💾 Spremi podatke", key="save_data"):
            # Kreiranje JSON izvoza
            import json
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="⬇️ Preuzmi JSON",
                data=json_data,
                file_name="chimney_calculation.json",
                mime="application/json"
            )

def render_comparison_tool():
    """
    Renders a tool for comparing different chimney configurations.
    Prikazuje alat za usporedbu različitih konfiguracija dimnjaka.
    """
    st.subheader("🔀 Usporedba konfiguracija")
    
    st.info("Alat za usporedbu različitih konfiguracija dimnjaka bit će implementiran u budućoj verziji")
    
    # Placeholder za budući razvoj
    with st.expander("Planirana funkcionalnost"):
        st.markdown("""
        - Usporedba različitih promjera dimnjaka
        - Analiza utjecaja visine dimnjaka
        - Optimizacija konfiguracije
        - Analiza troškova vs. performansi
        """)

def render_version_info():
    """
    Renders version and module information.
    Prikazuje informacije o verziji i modulu.
    """
    from . import MODULE_INFO
    
    with st.expander("ℹ️ Informacije o verziji"):
        st.markdown(f"""
        **{MODULE_INFO['name']}**  
        Verzija: {MODULE_INFO['version']}  
        Standard: {MODULE_INFO['standard']}  
        
        **Opis:** {MODULE_INFO['description']}
        
        **Ključna unaprijeđenja:**
        """)
        
        for feature in MODULE_INFO['features']:
            st.markdown(f"• {feature}")
        
        st.markdown("**Implementirane ispravke:**")
        for improvement in MODULE_INFO['improvements']:
            st.markdown(f"• {improvement}")

def create_status_badge(status: str) -> str:
    """
    Creates a colored status badge.
    Kreira obojeni status badge.
    """
    if "Zadovoljava" in status or "OK" in status:
        return f'<span style="background-color: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">✅ {status}</span>'
    elif "Ne zadovoljava" in status or "NOK" in status:
        return f'<span style="background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">❌ {status}</span>'
    else:
        return f'<span style="background-color: #ffc107; color: black; padding: 2px 8px; border-radius: 12px; font-size: 0.8em;">⚠️ {status}</span>'

def render_validation_limits_info():
    """
    Renders information about validation limits.
    Prikazuje informacije o granicama validacije.
    """
    with st.expander("📏 Granice validacije prema EN 13384-2"):
        limits_data = [
            ["Minimalna visina dimnjaka", f"{VALIDATION_LIMITS['min_chimney_height']} m"],
            ["Maksimalna visina dimnjaka", f"{VALIDATION_LIMITS['max_chimney_height']} m"],
            ["Minimalni promjer dimnjaka", f"{VALIDATION_LIMITS['min_chimney_diameter']} mm"],
            ["Maksimalni promjer dimnjaka", f"{VALIDATION_LIMITS['max_chimney_diameter']} mm"],
            ["Minimalna temperatura dimnih plinova", f"{VALIDATION_LIMITS['min_flue_gas_temp']} °C"],
            ["Maksimalna temperatura dimnih plinova", f"{VALIDATION_LIMITS['max_flue_gas_temp']} °C"],
            ["Minimalni CO2 udio", f"{VALIDATION_LIMITS['min_co2_percentage']} %"],
            ["Maksimalni CO2 udio", f"{VALIDATION_LIMITS['max_co2_percentage']} %"],
            ["Maksimalni broj ložišta", f"{VALIDATION_LIMITS['max_appliances']}"]
        ]
        
        df_limits = pd.DataFrame(limits_data, columns=["Parametar", "Granica"])
        st.dataframe(df_limits, hide_index=True)