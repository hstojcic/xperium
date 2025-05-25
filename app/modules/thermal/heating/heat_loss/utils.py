"""
Pomoćne funkcije za proračun toplinskih gubitaka
"""

import pandas as pd
import plotly.graph_objects as go

def prikazuje_upozorenje_o_povrsinama(zid_info, visina):
    """
    Provjerava treba li prikazati upozorenje o površinama otvora na zidu
    
    Parameters:
    -----------
    zid_info : dict
        Informacije o zidu
    visina : float
        Visina zida
        
    Returns:
    --------
    bool
        True ako je površina prozora + vrata veća od površine zida
    """
    ukupna_povrsina = zid_info["duzina"] * visina
    povrsina_otvora = zid_info["povrsina_prozora"] + zid_info["povrsina_vrata"]
    
    return povrsina_otvora > ukupna_povrsina

def create_transmission_losses_table(rezultati):
    """
    Kreira DataFrame s pregledom transmisijskih gubitaka
    
    Parameters:
    -----------
    rezultati : dict
        Rezultati izračuna toplinskih gubitaka
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame s pregledom transmisijskih gubitaka
    """
    table_data = {
        "Element": ["Vanjski zidovi", "Prozori", "Vrata", "Pod", "Strop", "Toplinski mostovi", "UKUPNO"],
        "Toplinski gubici [W]": [
            f"{rezultati['gubitak_zidovi']:.1f}",
            f"{rezultati['gubitak_prozori']:.1f}",
            f"{rezultati['gubitak_vrata']:.1f}",
            f"{rezultati['gubitak_pod']:.1f}",
            f"{rezultati['gubitak_strop']:.1f}",
            f"{rezultati['gubitak_mostovi']:.1f}",
            f"{rezultati['gubici_transmisijski']:.1f}"
        ],
        "Udio [%]": [
            f"{rezultati['gubitak_zidovi'] / rezultati['gubici_transmisijski'] * 100:.1f}%",
            f"{rezultati['gubitak_prozori'] / rezultati['gubici_transmisijski'] * 100:.1f}%",
            f"{rezultati['gubitak_vrata'] / rezultati['gubici_transmisijski'] * 100:.1f}%",
            f"{rezultati['gubitak_pod'] / rezultati['gubici_transmisijski'] * 100:.1f}%",
            f"{rezultati['gubitak_strop'] / rezultati['gubici_transmisijski'] * 100:.1f}%",
            f"{rezultati['gubitak_mostovi'] / rezultati['gubici_transmisijski'] * 100:.1f}%",
            "100.0%"
        ]
    }
    
    return pd.DataFrame(table_data)

def create_ventilation_losses_table(rezultati, izmjene_zraka):
    """
    Kreira DataFrame s pregledom ventilacijskih gubitaka
    
    Parameters:
    -----------
    rezultati : dict
        Rezultati izračuna toplinskih gubitaka
    izmjene_zraka : float
        Broj izmjena zraka u satu
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame s pregledom ventilacijskih gubitaka
    """
    table_data = {
        "Parametar": ["Volumen prostorije", "Broj izmjena zraka", "Temperaturna razlika", "Ventilacijski gubici"],
        "Vrijednost": [
            f"{rezultati['volumen_prostorije']:.1f} m³",
            f"{izmjene_zraka:.1f} h⁻¹",
            f"{rezultati['delta_t']:.0f} °C",
            f"{rezultati['gubici_ventilacijski']:.1f} W"
        ]
    }
    
    return pd.DataFrame(table_data)

def create_losses_pie_chart(rezultati):
    """
    Kreira pie chart za vizualizaciju raspodjele gubitaka
    
    Parameters:
    -----------
    rezultati : dict
        Rezultati izračuna toplinskih gubitaka
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Figure objekt s pie chartom
    """
    labels = ['Vanjski zidovi', 'Prozori', 'Vrata', 'Pod', 'Strop', 'Toplinski mostovi', 'Ventilacijski gubici']
    values = [
        rezultati['gubitak_zidovi'],
        rezultati['gubitak_prozori'],
        rezultati['gubitak_vrata'],
        rezultati['gubitak_pod'],
        rezultati['gubitak_strop'],
        rezultati['gubitak_mostovi'],
        rezultati['gubici_ventilacijski']
    ]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=['#1E88E5', '#42A5F5', '#90CAF9', '#4CAF50', '#8BC34A', '#CDDC39', '#FF9800']
    )])
    
    fig.update_layout(
        title_text='Raspodjela toplinskih gubitaka',
        # Dodajemo legendu na desnu stranu
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="right",
            x=1.1
        )
    )
    
    return fig