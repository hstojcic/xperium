"""
Pomoćne funkcije za aplikaciju
"""

import os
import datetime
import streamlit as st

def sanitize_filename(filename):
    """
    Čisti ime datoteke od nedozvoljenih znakova
    
    Args:
        filename (str): Izvorno ime datoteke
        
    Returns:
        str: Očišćeno ime datoteke
    """
    # Zamjena nedozvoljenih znakova
    forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in forbidden_chars:
        filename = filename.replace(char, '_')
    
    return filename

def get_timestamp():
    """
    Vraća trenutni timestamp u formatiranom obliku
    
    Returns:
        str: Formatirani timestamp (YYYYMMDD_HHMMSS)
    """
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S")

def format_file_size(size_in_bytes):
    """
    Formatira veličinu datoteke u čitljiv oblik
    
    Args:
        size_in_bytes (int): Veličina u bajtovima
        
    Returns:
        str: Formatirana veličina (npr. '2.5 KB')
    """
    # Konverzija u odgovarajuće jedinice
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"

def create_empty_directories():
    """
    Stvara potrebne direktorije ako ne postoje
    """
    # Lista direktorija koje želimo stvoriti
    directories = ["saved_calculations", "exports"]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)