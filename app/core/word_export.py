import streamlit as st
import os
import sys

# Provjera jesmo li u streamlit cloud okruženju
is_streamlit_cloud = (
    os.environ.get("IS_STREAMLIT_CLOUD", "0") == "1" or
    "STREAMLIT_SHARING" in os.environ or
    os.environ.get("HOSTNAME", "").startswith("stcloud")
)

# Debugiranje
print(f"Word_export.py: is_streamlit_cloud = {is_streamlit_cloud}")

# Global varijabla za Document
Document = None

# Pokušaj importiranja docx biblioteke
if not is_streamlit_cloud:
    try:
        print("Pokušaj importa python-docx...")
        from docx import Document
        print("Uspješno importan python-docx")
    except ImportError as e:
        # Ako biblioteka nije dostupna, Document ostaje None
        print(f"Neuspješno importan python-docx: {str(e)}")
        pass
else:
    print("Streamlit Cloud detektiran - preskačem import python-docx")

class WordExport:
    """
    Klasa za izvoz proračuna u Microsoft Word
    """
    
    def __init__(self):
        self.state_manager = st.session_state.state_manager
        
        # Provjera i stvaranje mape za izvoz
        os.makedirs("exports", exist_ok=True)
        
        # Provjera dostupnosti Word funkcionalnosti
        self.word_available = Document is not None
    
    def export_current_calculation(self):
        """
        Izvozi trenutni proračun u Word dokument
        """
        # Provjera je li docx modul dostupan
        if not self.word_available:
            st.error("Funkcionalnost izvoza u Word nije dostupna u ovom okruženju.")
            st.info("Ova funkcionalnost je dostupna samo u desktop verziji aplikacije.")
            return
            
        calculation = self.state_manager.get_current_calculation()
        if not calculation:
            st.error("Nema otvorenog proračuna za izvoz.")
            return
        
        st.subheader("Izvoz u Word")
        
        # Opcije za izvoz
        filename = st.text_input("Ime datoteke:", 
                               value=calculation.get_default_filename().replace('.calc', '.docx'))
        
        if st.button("Izvezi"):
            if not filename:
                st.error("Unesite ime datoteke.")
                return
                
            # Dodajemo ekstenziju ako nema
            if not filename.endswith('.docx'):
                filename += '.docx'
                
            file_path = os.path.join("exports", filename)
            
            # Izvoz
            try:
                self._export_to_word(calculation, file_path)
                st.success(f"Proračun izvezen u {filename}")
                
                # Dodajemo link za preuzimanje
                with open(file_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Preuzmi Word dokument",
                        data=file,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
            except Exception as e:
                st.error(f"Greška prilikom izvoza: {str(e)}")
    
    def _export_to_word(self, calculation, file_path):
        """
        Izvozi proračun u Word datoteku
        
        Args:
            calculation: Proračun za izvoz
            file_path: Putanja za spremanje Word datoteke
        """
        # Dodatna provjera dostupnosti Word funkcionalnosti
        if not self.word_available or Document is None:
            raise ImportError("Modul za Word export nije dostupan")
            
        # Stvaranje novog dokumenta
        doc = Document()
        
        # Dodavanje naslova
        doc.add_heading(calculation.name, level=1)
        
        # Pozivanje metode proračuna za izvoz
        calculation.export_to_word(doc)
        
        # Spremanje dokumenta
        doc.save(file_path)