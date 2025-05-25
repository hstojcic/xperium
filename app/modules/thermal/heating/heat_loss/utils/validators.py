"""
Modul s funkcijama za validaciju podataka.

Ovaj modul sadrži skup funkcija za validaciju različitih tipova podataka
koji se koriste u aplikaciji za proračun toplinskih gubitaka.
"""

def validate_number(value, min_value=None, max_value=None, default=None):
    """
    Validira numeričku vrijednost.
    
    Parameters:
    -----------
    value : any
        Vrijednost koja se validira
    min_value : number
        Minimalna dozvoljena vrijednost
    max_value : number
        Maksimalna dozvoljena vrijednost
    default : number
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    number
        Validirana vrijednost ili zadana vrijednost ako validacija ne uspije
    """
    try:
        number = float(value)
        
        if min_value is not None and number < min_value:
            return default
        
        if max_value is not None and number > max_value:
            return default
            
        return number
    except (ValueError, TypeError):
        return default
    
def validate_int(value, min_value=None, max_value=None, default=None):
    """
    Validira cjelobrojnu vrijednost.
    
    Parameters:
    -----------
    value : any
        Vrijednost koja se validira
    min_value : int
        Minimalna dozvoljena vrijednost
    max_value : int
        Maksimalna dozvoljena vrijednost
    default : int
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    int
        Validirana vrijednost ili zadana vrijednost ako validacija ne uspije
    """
    try:
        # Prvo konvertiramo u float pa u int da bismo podržali i "5.0" i "5"
        number = int(float(value))
        
        if min_value is not None and number < min_value:
            return default
        
        if max_value is not None and number > max_value:
            return default
            
        return number
    except (ValueError, TypeError):
        return default
    
def validate_string(value, allowed_values=None, default=None):
    """
    Validira string vrijednost.
    
    Parameters:
    -----------
    value : any
        Vrijednost koja se validira
    allowed_values : list
        Lista dozvoljenih vrijednosti
    default : str
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    str
        Validirana vrijednost ili zadana vrijednost ako validacija ne uspije
    """
    if not isinstance(value, str):
        return default
    
    if allowed_values is not None and value not in allowed_values:
        return default
        
    return value

def validate_bool(value, default=False):
    """
    Validira boolean vrijednost.
    
    Parameters:
    -----------
    value : any
        Vrijednost koja se validira
    default : bool
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    bool
        Validirana vrijednost ili zadana vrijednost ako validacija ne uspije
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        value = value.lower()
        if value in ['true', 't', 'yes', 'y', '1']:
            return True
        elif value in ['false', 'f', 'no', 'n', '0']:
            return False
            
    return default

def validate_list(value, item_validator=None, min_length=None, max_length=None, default=None):
    """
    Validira listu vrijednosti.
    
    Parameters:
    -----------
    value : any
        Vrijednost koja se validira
    item_validator : function
        Funkcija koja validira pojedine elemente liste
    min_length : int
        Minimalna dozvoljena duljina liste
    max_length : int
        Maksimalna dozvoljena duljina liste
    default : list
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    list
        Validirana lista ili zadana vrijednost ako validacija ne uspije
    """
    if default is None:
        default = []
        
    if not isinstance(value, list):
        return default
    
    if min_length is not None and len(value) < min_length:
        return default
    
    if max_length is not None and len(value) > max_length:
        return default
    
    if item_validator is not None:
        validated_list = []
        for item in value:
            validated_item = item_validator(item)
            if validated_item is not None:
                validated_list.append(validated_item)
        return validated_list
    
    return value

def validate_dict(value, key_validator=None, value_validator=None, required_keys=None, default=None):
    """
    Validira rječnik vrijednosti.
    
    Parameters:
    -----------
    value : any
        Vrijednost koja se validira
    key_validator : function
        Funkcija koja validira ključeve rječnika
    value_validator : function
        Funkcija koja validira vrijednosti rječnika
    required_keys : list
        Lista obaveznih ključeva
    default : dict
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    dict
        Validirani rječnik ili zadana vrijednost ako validacija ne uspije
    """
    if default is None:
        default = {}
        
    if not isinstance(value, dict):
        return default
    
    if required_keys is not None:
        for key in required_keys:
            if key not in value:
                return default
    
    if key_validator is not None or value_validator is not None:
        validated_dict = {}
        for k, v in value.items():
            validated_key = k if key_validator is None else key_validator(k)
            validated_value = v if value_validator is None else value_validator(v)
            
            if validated_key is not None and validated_value is not None:
                validated_dict[validated_key] = validated_value
        
        return validated_dict
    
    return value

def prikazuje_upozorenje_o_povrsinama(prostorije, min_povrsina=1.0, max_povrsina=500.0):
    """
    Provjerava je li potrebno prikazati upozorenje o površinama prostorija.
    
    Parameters:
    -----------
    prostorije : list
        Lista prostorija koje se provjeravaju
    min_povrsina : float
        Minimalna dozvoljena površina prostorije
    max_povrsina : float
        Maksimalna dozvoljena površina prostorije
        
    Returns:
    --------
    tuple
        (bool, list) - Treba li prikazati upozorenje i lista problematičnih prostorija
    """
    problematicne = []
    
    for prostorija in prostorije:
        if not hasattr(prostorija, "povrsina"):
            continue
            
        if prostorija.povrsina < min_povrsina or prostorija.povrsina > max_povrsina:
            problematicne.append(prostorija)
    
    return len(problematicne) > 0, problematicne

def validiraj_temperaturu(temperatura, min_temp=-30.0, max_temp=50.0, default=20.0):
    """
    Validira temperaturnu vrijednost.
    
    Parameters:
    -----------
    temperatura : any
        Temperatura koja se validira
    min_temp : float
        Minimalna dozvoljena temperatura
    max_temp : float
        Maksimalna dozvoljena temperatura
    default : float
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    float
        Validirana temperatura ili zadana vrijednost ako validacija ne uspije
    """
    return validate_number(temperatura, min_temp, max_temp, default)

def validiraj_u_vrijednost(u_vrijednost, min_u=0.01, max_u=10.0, default=1.0):
    """
    Validira U-vrijednost (koeficijent prolaska topline).
    
    Parameters:
    -----------
    u_vrijednost : any
        U-vrijednost koja se validira
    min_u : float
        Minimalna dozvoljena U-vrijednost
    max_u : float
        Maksimalna dozvoljena U-vrijednost
    default : float
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    float
        Validirana U-vrijednost ili zadana vrijednost ako validacija ne uspije
    """
    return validate_number(u_vrijednost, min_u, max_u, default)

def validiraj_postotak(postotak, default=0.0):
    """
    Validira postotnu vrijednost.
    
    Parameters:
    -----------
    postotak : any
        Postotak koji se validira
    default : float
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    float
        Validirani postotak ili zadana vrijednost ako validacija ne uspije
    """
    return validate_number(postotak, 0.0, 100.0, default)

def validiraj_dimenzije_prostorije(sirina, duzina, visina):
    """
    Validira dimenzije prostorije.
    
    Parameters:
    -----------
    sirina : any
        Širina prostorije
    duzina : any
        Dužina prostorije
    visina : any
        Visina prostorije
        
    Returns:
    --------
    tuple
        (sirina, duzina, visina) - Validirane dimenzije prostorije
    """
    validirano_sirina = validate_number(sirina, 0.1, 50.0, 4.0)
    validirano_duzina = validate_number(duzina, 0.1, 50.0, 5.0)
    validirano_visina = validate_number(visina, 0.1, 10.0, 2.6)
    
    return validirano_sirina, validirano_duzina, validirano_visina

def validiraj_broj_osoba(broj_osoba, default=2):
    """
    Validira broj osoba u prostoriji.
    
    Parameters:
    -----------
    broj_osoba : any
        Broj osoba koji se validira
    default : int
        Zadana vrijednost koja se vraća ako validacija ne uspije
        
    Returns:
    --------
    int
        Validirani broj osoba ili zadana vrijednost ako validacija ne uspije
    """
    return validate_int(broj_osoba, 0, 100, default)
