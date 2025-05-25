"""
Modul s pomoćnim funkcijama za rad sa Streamlit session state.
"""

import streamlit as st
import json
import base64

def spremi_u_session_state(session_key, data):
    """
    Sprema podatke u Streamlit session state.
    
    Parameters:
    -----------
    session_key : str
        Ključ pod kojim se podaci spremaju u session state
    data : any
        Podaci koji se spremaju
    """
    st.session_state[session_key] = data
    
def ucitaj_iz_session_state(session_key, default=None):
    """
    Učitava podatke iz Streamlit session state.
    
    Parameters:
    -----------
    session_key : str
        Ključ pod kojim su podaci spremljeni u session state
    default : any
        Zadana vrijednost koja se vraća ako ključ ne postoji
        
    Returns:
    --------
    any
        Podaci iz session state-a ili zadana vrijednost ako ključ ne postoji
    """
    return st.session_state.get(session_key, default)

def obrisi_iz_session_state(session_key):
    """
    Briše podatke iz Streamlit session state.
    
    Parameters:
    -----------
    session_key : str
        Ključ pod kojim su podaci spremljeni u session state
        
    Returns:
    --------
    bool
        True ako je ključ postojao i obrisan, False inače
    """
    if session_key in st.session_state:
        del st.session_state[session_key]
        return True
    return False

def provjeri_ispravnost_tipa(session_key, ocekivani_tip):
    """
    Provjerava je li objekt u session state-u određenog tipa.
    Ako nije, briše ga iz session state-a.
    
    Parameters:
    -----------
    session_key : str
        Ključ pod kojim su podaci spremljeni u session state
    ocekivani_tip : type
        Očekivani tip podataka
        
    Returns:
    --------
    bool
        True ako je objekt ispravnog tipa, False inače
    """
    if session_key in st.session_state:
        if not isinstance(st.session_state[session_key], ocekivani_tip):
            del st.session_state[session_key]
            return False
        return True
    return False

def is_valid_session_data(data, data_type=dict):
    """
    Provjerava je li podatak iz session statea validan za korištenje.
    
    Parameters:
    -----------
    data : any
        Podatak iz session statea
    data_type : type
        Očekivani tip podatka
        
    Returns:
    --------
    bool
        True ako je podatak validan, False inače
    """
    if data is None:
        return False
    
    # Provjera je li podatak očekivanog tipa
    if not isinstance(data, data_type):
        return False
    
    return True

def initialize_session_data(session_key, default_value=None):
    """
    Inicijalizira podatke u session stateu ako ne postoje.
    
    Parameters:
    -----------
    session_key : str
        Ključ pod kojim se podaci spremaju u session state
    default_value : any
        Zadana vrijednost koja se postavlja ako ključ ne postoji
        
    Returns:
    --------
    any
        Vrijednost iz session statea (postojeća ili nova)
    """
    if session_key not in st.session_state:
        st.session_state[session_key] = default_value if default_value is not None else {}
    elif default_value is not None and not isinstance(st.session_state[session_key], type(default_value)):
        # Ako je već postoji vrijednost ali nije očekivanog tipa, reset na default
        st.session_state[session_key] = default_value
    
    return st.session_state[session_key]

def generate_download_json(data, filename="session_data.json"):
    """
    Generira JSON datoteku za preuzimanje podataka iz session statea.
    
    Parameters:
    -----------
    data : dict
        Podaci koji se spremaju u JSON
    filename : str
        Naziv datoteke za preuzimanje
        
    Returns:
    --------
    str
        HTML kod za preuzimanje podataka
    """
    # Konvertiramo podatke u JSON string
    json_str = json.dumps(data, indent=2)
    
    # Kodiramo kao base64
    b64 = base64.b64encode(json_str.encode()).decode()
    
    # Generiramo HTML za preuzimanje
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}" target="_blank">Preuzmi podatke</a>'
    
    return href

def upload_session_data(session_key, uploaded_file):
    """
    Učitava podatke iz uploadane datoteke u session state.
    
    Parameters:
    -----------
    session_key : str
        Ključ pod kojim se podaci spremaju u session state
    uploaded_file : UploadedFile
        Uploadana datoteka iz Streamlit file_uploader-a
        
    Returns:
    --------
    bool
        True ako je učitavanje uspjelo, False inače
    """
    if uploaded_file is None:
        return False
    
    try:
        # Učitavamo JSON podatke
        content = uploaded_file.read()
        data = json.loads(content)
        
        # Spremamo u session state
        st.session_state[session_key] = data
        return True
    except Exception as e:
        st.error(f"Greška prilikom učitavanja podataka: {e}")
        return False
