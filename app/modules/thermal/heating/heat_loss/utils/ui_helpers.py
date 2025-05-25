"""
UI helper funkcije za prikaz rezultata proračuna toplinskih gubitaka
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def create_transmission_losses_table(gubici_po_elementima):
    """
    Kreira tablicu transmisijskih gubitaka za prikaz.
    
    Parameters:
    -----------
    gubici_po_elementima : dict
        Rječnik s gubicima po elementima
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame s formatiranim podacima za prikaz
    """
    rows = []
    
    for element_type, elements in gubici_po_elementima.items():
        if element_type == "ukupno":
            continue
            
        for element_name, element_info in elements.items():
            if isinstance(element_info, dict) and "snaga" in element_info:
                rows.append({
                    "Tip elementa": element_type.capitalize(),
                    "Naziv": element_name,
                    "Površina [m²]": element_info.get("povrsina", 0),
                    "U-vrijednost [W/m²K]": element_info.get("u_vrijednost", 0),
                    "Razlika temp. [°C]": element_info.get("delta_t", 0),
                    "Gubitak [W]": element_info.get("snaga", 0)
                })
    
    if not rows:
        return None
        
    # Kreiranje DataFrame-a
    df = pd.DataFrame(rows)
    
    # Formatiranje numeričkih stupaca
    if "Površina [m²]" in df.columns:
        df["Površina [m²]"] = df["Površina [m²]"].map(lambda x: f"{x:.2f}" if pd.notnull(x) else "")
    if "U-vrijednost [W/m²K]" in df.columns:
        df["U-vrijednost [W/m²K]"] = df["U-vrijednost [W/m²K]"].map(lambda x: f"{x:.3f}" if pd.notnull(x) else "")
    if "Razlika temp. [°C]" in df.columns:
        df["Razlika temp. [°C]"] = df["Razlika temp. [°C]"].map(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
    if "Gubitak [W]" in df.columns:
        df["Gubitak [W]"] = df["Gubitak [W]"].map(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
    
    return df

def create_ventilation_losses_table(ventilacijski, infiltracija=None):
    """
    Kreira tablicu ventilacijskih gubitaka za prikaz.
    
    Parameters:
    -----------
    ventilacijski : dict
        Rječnik s ventilacijskim gubicima
    infiltracija : dict, optional
        Rječnik s gubicima infiltracije
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame s formatiranim podacima za prikaz
    """
    data = {
        "Parametar": [
            "Volumen prostorije [m³]",
            "Izmjena zraka [1/h]",
            "Protok zraka",
            "Razlika temperatura [°C]",
            "Specifični toplinski kapacitet [Wh/m³K]",
            "Ventilacijski toplinski gubici [W]"
        ],
        "Vrijednost": [
            f"{ventilacijski['volumen']:.2f}",
            f"{ventilacijski['izmjena_zraka']:.2f}",
            f"{ventilacijski['protok_zraka']:.2f} m³/h",
            f"{ventilacijski['delta_t']:.1f}",
            f"{ventilacijski['cp_rho']:.3f}",
            f"{ventilacijski['snaga_gubitaka']:.1f}"
        ]
    }
    
    if infiltracija:
        data["Parametar"].extend([
            "Infiltracijski protok zraka [m³/h]",
            "Infiltracijski toplinski gubici [W]"
        ])
        data["Vrijednost"].extend([
            f"{infiltracija['protok_zraka']:.2f}",
            f"{infiltracija['snaga_gubitaka']:.1f}"
        ])
    
    return pd.DataFrame(data)

def create_losses_pie_chart(transmisijski, ventilacijski, toplinski_mostovi, infiltracija=None):
    """
    Kreira pie chart za prikaz udjela pojedinih gubitaka.
    
    Parameters:
    -----------
    transmisijski : float
        Iznos transmisijskih gubitaka u W
    ventilacijski : float
        Iznos ventilacijskih gubitaka u W
    toplinski_mostovi : float
        Iznos gubitaka kroz toplinske mostove u W
    infiltracija : float, optional
        Iznos gubitaka zbog infiltracije u W
        
    Returns:
    --------
    plotly.graph_objects.Figure
        Pie chart s udjelima gubitaka
    """
    labels = ["Transmisijski", "Ventilacijski", "Toplinski mostovi"]
    values = [transmisijski, ventilacijski, toplinski_mostovi]
    
    if infiltracija:
        labels.append("Infiltracija")
        values.append(infiltracija)
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.4,
        marker_colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    )])
    
    fig.update_layout(
        title={
            'text': "Udio pojedinih toplinskih gubitaka",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        height=400
    )
    
    return fig
