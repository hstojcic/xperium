import streamlit as st
import importlib
import os
from modules.base import BaseCalculation

class Navigation:
    """
    Klasa za upravljanje navigacijom u aplikaciji
    """
    
    def __init__(self):
        self.state_manager = st.session_state.state_manager
        
        # Inicijaliziramo zastavice za dijaloške prikaze
        if 'showing_unsaved_dialog' not in st.session_state:
            st.session_state.showing_unsaved_dialog = False
        
        if 'showing_save_dialog' not in st.session_state:
            st.session_state.showing_save_dialog = False
            
        if 'showing_save_as_dialog' not in st.session_state:
            st.session_state.showing_save_as_dialog = False
            
        if 'pending_action_type' not in st.session_state:
            st.session_state.pending_action_type = None
    
    def check_unsaved_changes(self, action_type=None):
        """
        Provjerava ima li nespremljenih promjena
        i pita korisnika za potvrdu ako ih ima.
        Vraća True ako je ok nastaviti, False ako treba prekinuti akciju.
        
        Args:
            action_type: Tip akcije koja se pokušava izvršiti ('new', 'open', 'close', itd.)
        """
        if self.state_manager.has_unsaved_changes():
            # Zapamti koji tip akcije je pokrenuo dijalog
            if action_type:
                st.session_state.pending_action_type = action_type
                
            # Postavi zastavicu za prikazivanje dijaloga
            st.session_state.showing_unsaved_dialog = True
            st.rerun()  # Ovo će osvježiti stranicu s aktivnim dijalogom
            return False  # Privremeno zaustavi akciju dok korisnik ne odluči
        
        return True  # Nema nespremljenih promjena, ok je nastaviti
    
    def render_unsaved_dialog(self):
        """
        Prikazuje dijalog za nespremljene promjene
        """
        # Prikazujemo upozorenje
        st.warning("Imate nespremljene promjene. Želite li spremiti prije nastavka?")
        
        # Gumbi u vertikalnom rasporedu - jedan ispod drugog
        if st.button("Spremi", key="dialog_save", use_container_width=True):
            # Spremi promjene
            success = st.session_state.file_manager.save_calculation()
            st.session_state.showing_unsaved_dialog = False
            
            # Nakon spremanja, nastavi s prethodno zahtijevanom akcijom
            self.continue_with_action()
            
        if st.button("Nastavi bez spremanja", key="dialog_continue", use_container_width=True):
            # Nastavi bez spremanja
            st.session_state.showing_unsaved_dialog = False
            
            # Nakon odabira, nastavi s prethodno zahtijevanom akcijom
            self.continue_with_action()
            
        if st.button("Odustani", key="dialog_cancel", use_container_width=True):
            # Odustani od akcije
            st.session_state.showing_unsaved_dialog = False
            
            # Resetiranje akcije
            if 'pending_action_type' in st.session_state:
                del st.session_state.pending_action_type
            
            st.rerun()
    
    def continue_with_action(self):
        """
        Nastavlja s prethodno zahtijevanom akcijom nakon odgovora u dijalozima
        """
        action_type = st.session_state.get('pending_action_type')
        
        # Resetiramo akciju prije izvršavanja
        if 'pending_action_type' in st.session_state:
            del st.session_state.pending_action_type
        
        # Izvršavanje odgovarajuće akcije
        if action_type == 'new':
            # Ako je akcija bila 'novi proračun', prikaži odabir kategorija
            st.session_state['show_category_selection'] = True
            
        elif action_type == 'open':
            # Ako je akcija bila 'otvori', pozovi open_calculation direktno
            st.session_state.file_manager.open_calculation()
                
        elif action_type == 'close':
            # Ako je akcija bila 'zatvori', zatvori proračun
            self.close_current_calculation()
        
        st.rerun()    
    
    def render_save_dialog(self):
        """
        Prikazuje dijalog za spremanje proračuna u Streamlit sučelju
        """
        # Pozivamo metodu za spremanje s novim Streamlit dijalogom
        file_manager = st.session_state.file_manager
        result = file_manager.save_calculation()
        
        # Ako je rezultat "waiting", to znači da korisnik još interagira s dijalogom
        if result != "waiting":
            # Resetiramo zastavicu dijaloga jer je postupak završen
            st.session_state.showing_save_dialog = False
            st.rerun()
        
    def render_save_as_dialog(self):
        """
        Prikazuje dijalog za spremanje proračuna pod novim imenom u Streamlit sučelju
        """
        # Pozivamo metodu za spremanje pod novim imenom s novim Streamlit dijalogom
        file_manager = st.session_state.file_manager
        result = file_manager.save_calculation_as()
        
        # Ako je rezultat "waiting", to znači da korisnik još interagira s dijalogom
        if result != "waiting":
            # Resetiramo zastavicu dijaloga jer je postupak završen
            st.session_state.showing_save_as_dialog = False
            st.rerun()
    
    def show_category_selection(self):
        """
        Prikazuje sučelje za odabir kategorije i podkategorije proračuna - 
        potpuno reorganizirano bez dodatnih stilova
        """
        st.title("Odabir proračuna")
        
        categories = self.state_manager.get_categories()
        available_calcs = st.session_state.available_calculations if hasattr(st.session_state, 'available_calculations') else {}
        
        # Definiranje tab-ova za glavne kategorije
        tabs = st.tabs(list(categories.keys()))
        
        # Popunjavanje sadržaja za svaku kategoriju
        for i, (main_category, subcategories) in enumerate(categories.items()):
            with tabs[i]:
                st.header(main_category)
                
                # Korištenje accordiona za podkategorije
                for subcategory in subcategories:
                    with st.expander(subcategory, expanded=False):
                        st.subheader(subcategory)
                        
                        # Provjera jesu li dostupni proračuni
                        if (main_category in available_calcs and 
                            subcategory in available_calcs[main_category] and
                            available_calcs[main_category][subcategory]):
                            
                            # Direktan prikaz dostupnih proračuna
                            st.write("Odaberite proračun:")
                              # Dobavljanje proračuna
                            calcs = available_calcs[main_category][subcategory]
                            
                            # Sortiraj proračune abecedno po imenu
                            calcs_sorted = sorted(calcs, key=lambda x: x['name'])
                            
                            # Stvaramo prilagođene kartice za proračune u 3 stupca
                            cols = st.columns(3)  # Tri stupca za prikaz
                            
                            for i, calc in enumerate(calcs_sorted):
                                col_index = i % 3  # Za raspored u 3 stupca
                                with cols[col_index]:
                                    if st.button(
                                        calc['name'], 
                                        key=f"calc_{main_category}_{subcategory}_{calc['name']}_{calc['module']}_{calc['class']}",
                                        use_container_width=True
                                    ):
                                        self._load_calculation(calc["module"], calc["class"])
                        else:
                            st.info("Trenutno nema dostupnih proračuna za ovu kategoriju.")
    
    def close_current_calculation(self):
        """
        Zatvara trenutni proračun i vraća na početni ekran
        """
        self.state_manager.set_current_calculation(None)
        self.state_manager.set_current_file_path(None)
        self.state_manager.set_calculation_changed(False)
        
        # Također resetiramo zastavice za dijaloge i prikaz kategorija
        if 'show_category_selection' in st.session_state:
            st.session_state.show_category_selection = False
    
    def render_home_screen(self):
        """
        Prikazuje početni ekran aplikacije - naslov centriran na stranici s poboljšanom stilizacijom
        """
        # Korištenje CSS-a za centriranje sadržaja i stilizaciju
        st.markdown("""
            <style>
            .center-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                height: 80vh;
                margin: auto;
            }
            
            .main-title {
                font-size: 3.2rem;
                font-weight: 600;
                margin-bottom: 1rem;
                color: var(--text-color);
                padding: 0.5rem 2rem;
                border-bottom: 3px solid var(--primary-color);
                border-top: 3px solid var(--primary-color);
                border-radius: 5px;
                letter-spacing: 0.5px;
            }
            
            .author-info {
                margin-top: 1rem;
                font-size: 18px;
                color: var(--text-color);
                font-weight: 500;
            }
            
            .copyright-info {
                margin-top: 0.5rem;
                font-size: 16px;
                color: var(--text-color);
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Prikaz centriranog sadržaja
        st.markdown("""
            <div class="center-content">
                <h1 class="main-title">Proračuni strojarskih instalacija</h1>
                <div class="author-info">
                    Autor: Hrvoje Stojčić, mag. ing. mech.
                </div>
                <div class="copyright-info">
                    © XPERIUM d.o.o. Sva prava pridržana.
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    def _load_calculation(self, module_path, class_name):
        """
        Dinamički učitava klasu proračuna iz modula
        
        Args:
            module_path: Putanja do modula (npr. 'hydraulic.water_supply.basic_calc')
            class_name: Ime klase koja se učitava
        """
        try:
            # Puni modul path
            full_module_path = f"modules.{module_path}"
            
            # Dinamičko učitavanje modula
            module = importlib.import_module(full_module_path)
            
            # Dohvaćanje klase
            calculation_class = getattr(module, class_name)
            
            # Instanciranje klase
            calculation = calculation_class()
            
            # Postavljanje kao trenutni proračun
            self.state_manager.set_current_calculation(calculation)
            self.state_manager.set_calculation_changed(False)
            
            # Resetiranje prikaza kategorija i drugih zastavica nakon uspješnog učitavanja proračuna
            if 'show_category_selection' in st.session_state:
                st.session_state.show_category_selection = False
                
            st.rerun()
            
        except Exception as e:
            st.error(f"Greška prilikom učitavanja proračuna: {str(e)}")
            # Dodajemo detaljnije informacije o grešci za lakše otklanjanje problema
            import traceback
            st.error(traceback.format_exc())