# Implementacija unaprijeđenog kalkulatora toplinskih gubitaka - Upute za dovršetak

## Što je implementirano

1. **FizickiZid klasa**
   - Implementirana je klasa FizickiZid koja omogućuje centralizirano upravljanje zidovima
   - Dodana je podrška za povezivanje više prostorija s jednim fizičkim zidom
   - Implementirani su potrebni mmehanizmi za održavanje konzistentnosti modela

2. **Konverzija i analiziranje zidova**
   - Implementiran modul za konverziju postojećih zidova u sustav fizičkih zidova
   - Implementiran modul za analizu i povezivanje zajedničkih zidova
   - Implementiran modul za obnavljanje referenci između zidova i prostorija

3. **UI komponente**
   - Implementirano sučelje za analizu i povezivanje zidova
   - Dodana kontrola za upravljanje fizičkim zidovima

4. **Testovi**
   - Dodani su testovi za klasu FizickiZid

## Što još treba dovršiti

1. **Ažuriranje prostorija i zidova**
   - Dovršiti nadogradnju `dodaj_zid` metode u `Prostorija` klasi
   - Osigurati da sve prostorije s povezanim zidovima dijele istu referencu na fizički zid

2. **UI integracija**
   - Dodati tab "Povezivanje zidova" u glavni UI
   - Integrirati analizu zidova u glavno sučelje

3. **Inicijalizacija modela**
   - Osigurati da se poziva metoda za konverziju starih zidova u fizičke zidove pri učitavanju modela

4. **Testiranje i otklanjanje grešaka**
   - Provjeriti sve funkcionalnosti kroz korisničko sučelje
   - Osigurati da su proračuni konzistentni i točni

## Kako dovršiti implementaciju

### 1. Ažuriranje `model.py`
Dodajte i nadogradite sljedeće metode u klasi `MultiRoomModel`:

```python
def konvertiraj_u_fizicke_zidove(self):
    """
    Konvertira sve postojeće zidove u sustav fizičkih zidova.
    
    Returns:
    --------
    int
        Broj konvertiranih zidova
    """
    from .zid_konverzija import konvertiraj_u_fizicke_zidove
    return konvertiraj_u_fizicke_zidove(self)
    
def obnovi_reference_zidova(self):
    """
    Obnavlja reference između fizičkih zidova i zidova prostorija.
    
    Returns:
    --------
    int
        Broj obnovljenih referenci
    """
    from .zid_reference import restore_wall_references
    return restore_wall_references(self)
    
def create_physical_wall_from_wall(self, wall_dict):
    """
    Stvara novi fizički zid na temelju rječnika zida iz prostorije.
    
    Parameters:
    -----------
    wall_dict : dict
        Rječnik s podacima o zidu
        
    Returns:
    --------
    FizickiZid
        Novostvoreni fizički zid
    """
    # Izvlačimo elemente zida
    elementi = wall_dict.get("elementi")
    if not isinstance(elementi, WallElements):
        elementi = WallElements()
        
    # Izvlačimo segmente zida
    segmenti = wall_dict.get("segmenti", [])
        
    # Stvaramo novi fizički zid
    fizicki_zid = FizickiZid(
        tip=wall_dict.get("tip", "vanjski"),
        orijentacija=wall_dict.get("orijentacija"),
        duzina=float(wall_dict.get("duzina", 5.0)),
        visina=float(wall_dict.get("visina")) if wall_dict.get("visina") is not None else None,
        je_segmentiran=wall_dict.get("je_segmentiran", False),
        segmenti=segmenti,
        elementi=elementi
    )
        
    return fizicki_zid

def analiziraj_povezanost_zidova(self):
    """
    Analizira prostorije i identificira potencijalno povezane zidove.
    
    Returns:
    --------
    list
        Lista potencijalnih povezivanja zidova
    """
    from .zid_povezivanje import analiziraj_povezanost_zidova
    return analiziraj_povezanost_zidova(self)
    
def povezi_zidove(self, prostorija1_id, zid1_id, prostorija2_id, zid2_id):
    """
    Povezuje dva zida u različitim prostorijama kao isti fizički zid.
    
    Parameters:
    -----------
    prostorija1_id, prostorija2_id : str
        ID prostorija čiji se zidovi povezuju
    zid1_id, zid2_id : str
        ID zidova koji se povezuju
        
    Returns:
    --------
    bool
        True ako je povezivanje uspjelo, False inače
    """
    from .zid_povezivanje import povezi_zidove
    return povezi_zidove(self, prostorija1_id, zid1_id, prostorija2_id, zid2_id)
```

### 2. Ažuriranje `heat_loss_calc.py`
Osigurajte inicijalizaciju modela i konverziju zidova:

```python
def _inicijaliziraj_model(self):
    """
    Inicijalizira model i kontrolere za proračun toplinskih gubitaka.
    
    Ova metoda stvara novu instancu MultiRoomModel-a i kontrolera za upravljanje
    modelom, te vrši konverziju modela u sustav fizičkih zidova ako je potrebno.
    """
    # 1. Inicijalizacija modela građevinskih elemenata
    if "elements_model" not in st.session_state:
        st.session_state.elements_model = inicijaliziraj_elemente()
    elements_model = st.session_state.elements_model

    # 2. Inicijalizacija MultiRoomModel-a
    # Konstruktor MultiRoomModel-a interno upravlja učitavanjem stanja
    # iz session_state (ako postoji) ili inicijalizacijom novog modela
    self.multi_room_model = MultiRoomModel(self.session_key)
    
    # 3. Konvertiramo postojeće zidove u sustav fizičkih zidova
    if "konvertiran_u_fizicke_zidove" not in st.session_state or not st.session_state["konvertiran_u_fizicke_zidove"]:
        broj_konvertiranih = self.multi_room_model.konvertiraj_u_fizicke_zidove()
        if broj_konvertiranih > 0:
            st.info(f"Uspješno ažuriran model zidova: {broj_konvertiranih} zidova konvertirano u centralizirani sustav.")
        st.session_state["konvertiran_u_fizicke_zidove"] = True
    
    # 4. Obnavljamo reference između zidova
    broj_obnovljenih = self.multi_room_model.obnovi_reference_zidova()
    
    # 5. Inicijalizacija kontrolera
    self.inicijaliziraj_kontrolere(self.multi_room_model, elements_model)
    
    # 6. Učitavanje rezultata iz session state-a
    if self.results_session_key in st.session_state:
        self.rezultati = st.session_state[self.results_session_key]
    else:
        self.rezultati = {}
```

I ažurirajte `render` metodu:

```python
def render(self):
    st.title(self.name)
    
    # Inicijalizacija modela i kontrolera
    self._inicijaliziraj_model()

    # Definiranje tabova
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Osnovni podaci", 
        "Prostorije i zidovi", 
        "Povezivanje zidova",
        "Građevinski elementi",
        "Rezultati"
    ])
    
    with tab1:
        # Osnovni podaci
        self._prikazi_opce_postavke(st.session_state.elements_model)
        
    with tab2:
        # Prostorije i zidovi
        st.header("Postavke zgrade")
        prikazi_manager_etaza(self.multi_room_model, self.etaza_controller, self.prostorija_controller, self.zid_controller)
        
    with tab3:
        # Povezivanje zidova
        from .ui.zid_povezivanje_ui import prikazi_analizator_povezanosti_zidova
        prikazi_analizator_povezanosti_zidova(self.multi_room_model, self.zid_controller)
        
    with tab4:
        # Građevinski elementi
        st.header("Građevinski elementi")
        prikazi_manager_gradevinski_elementi(self.multi_room_model, self.elementi_controller)
        
    with tab5:
        # Rezultati
        self._prikazi_rezultate()
```

### 3. Testiranje i otklanjanje grešaka
Nakon što sve implementirate, temeljito testirajte:
- Dodavanje novih prostorija i zidova
- Povezivanje zidova
- Izračune toplinskih gubitaka i provjeru konzistentnosti rezultata

## Zaključak

Ova implementacija omogućuje centralizirani sustav upravljanja fizičkim zidovima, gdje više prostorija dijeli referencu na isti fizički objekt zida. Time se eliminiraju problemi nekonzistentnosti koji su postojali u prethodnoj implementaciji.

Ključne prednosti:
- Jedan objekt za svaki fizički zid
- Prostorije dijele reference na iste objekte zidova
- Promjene na zidu automatski se reflektiraju kroz cijeli model
- Poboljšana konzistentnost izračuna
