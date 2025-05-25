import streamlit as st
from datetime import datetime
from modules.thermal.heating.floor_heating.constants import *
from modules.thermal.heating.floor_heating.utils import *


class FloorHeatingDataManager:
    """Klasa za upravljanje podacima kalkulatora podnog grijanja."""
    
    def __init__(self, calculation_handler):
        """Inicijalizacija upravitelja podataka s handlerom za kalkulacije."""
        self.calculation_handler = calculation_handler
    
    def initialize_data_structure(self):
        """Inicijalizira strukturu podataka za proračun podnog grijanja."""
        return {
            "meta": {
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "version": "2.0",
                "calculation_type": "Proračun podnog grijanja"
            },
            "building": {
                "name": "Nova zgrada",
                "floors": [
                    {
                        "id": 1,
                        "name": "Prizemlje",
                        "screed_thickness": 45,
                        "manifolds": [
                            {
                                "id": 1,
                                "name": "Razdjelnik 1",
                                "flow_temperature": 35,
                                "ΔT": 5,
                                "pipe_diameter": "16×2,0",
                                "supply_pipe_length": 5.0,
                                "return_pipe_length": 5.0,
                                "supply_pipe_diameter": "20×2,0",
                                "num_circuits": 2,  # Promijenjeno s 4 na 2 kruga
                                "rooms": [
                                    {
                                        "id": 1,
                                        "name": "Blagovaonica",
                                        "position": 1  # Pozicija na razdjelniku (1 = lijevo)
                                    },
                                    {
                                        "id": 2,
                                        "name": "Blagovaonica",
                                        "position": 2  # Pozicija na razdjelniku (2 = desno od prvog)
                                    }
                                ],
                                "loops": [
                                    {
                                        "id": 1,
                                        "room_name": "Blagovaonica",
                                        "room_temperature": 22,
                                        "r_lambda": 0.00,
                                        "pipe_spacing": 15,
                                        "area": None,
                                        "manifold_distance": None,
                                        "results": {}
                                    },
                                    {
                                        "id": 2,
                                        "room_name": "Blagovaonica",
                                        "room_temperature": 22,
                                        "r_lambda": 0.00,
                                        "pipe_spacing": 15,
                                        "area": None,
                                        "manifold_distance": None,
                                        "results": {}
                                    }
                                ]
                            }
                        ]
                    }
                ]
            },
            "common_params": {
                # Zajednički parametri za kompatibilnost s postojećim kodom
                "flow_temperature": 35,
                "ΔT": 5,
                "pipe_diameter": "16×2,0",
                "screed_thickness": 45
            },
            "loops": []  # Prazno za migraciju
        }
    
    def migrate_data_if_needed(self, data):
        """Migrira podatke iz stare strukture u novu ako je potrebno."""
        # Provjeri je li potrebna migracija
        if "building" not in data or not data["building"]["floors"]:
            st.info("Migracija podataka u novu strukturu...")
            
            # Inicijaliziraj novu strukturu ako ne postoji
            if "building" not in data:
                data["building"] = {
                    "name": "Nova zgrada",
                    "floors": []
                }
            
            # Kreiraj prvu etažu ako ne postoji
            if not data["building"]["floors"]:
                data["building"]["floors"] = [{
                    "id": 1,
                    "name": "Prizemlje",
                    "screed_thickness": data["common_params"].get("screed_thickness", 45),
                    "manifolds": []
                }]
            
            # Kreiraj prvi razdjelnik ako ne postoji
            first_floor = data["building"]["floors"][0]
            if not first_floor.get("manifolds"):
                first_floor["manifolds"] = [{
                    "id": 1,
                    "name": "Razdjelnik 1",
                    "flow_temperature": data["common_params"].get("flow_temperature", 35),
                    "ΔT": data["common_params"].get("ΔT", 5),
                    "pipe_diameter": data["common_params"].get("pipe_diameter", "16×2,0"),
                    "supply_pipe_length": 5.0,
                    "return_pipe_length": 5.0,
                    "supply_pipe_diameter": "20×2,0",
                    "num_circuits": 4,
                    "rooms": [],
                    "loops": []
                }]
            
            # Migriraj postojeće petlje u novi razdjelnik
            first_manifold = first_floor["manifolds"][0]
            
            # Kopiraj postojeće petlje
            if "loops" in data and data["loops"]:
                # Dohvati imena svih prostorija
                room_names = {}
                for i, loop in enumerate(data["loops"]):
                    room_name = loop.get("room_name", f"Prostorija {i+1}")
                    room_names[loop["id"]] = room_name
                    
                    # Dodaj sobu u razdjelnik
                    first_manifold["rooms"].append({
                        "id": loop["id"],
                        "name": room_name,
                        "position": loop["id"]  # Pozicija prema ID-u
                    })
                    
                    # Kopiraj petlju u razdjelnik
                    first_manifold["loops"].append(loop.copy())
                
                # Zadrži stare podatke za kompatibilnost
                # data["loops"] = []
            
            st.success("Migracija podataka uspješno završena!")
            
        # Ažuriraj common_params prema prvom razdjelniku za kompatibilnost sa starim kodom
        if "building" in data and data["building"]["floors"]:
            first_floor = data["building"]["floors"][0]
            if first_floor.get("manifolds"):
                first_manifold = first_floor["manifolds"][0]
                data["common_params"]["screed_thickness"] = first_floor.get("screed_thickness", 45)
                data["common_params"]["flow_temperature"] = first_manifold.get("flow_temperature", 35)
                data["common_params"]["ΔT"] = first_manifold.get("ΔT", 5)
                data["common_params"]["pipe_diameter"] = first_manifold.get("pipe_diameter", "16×2,0")
    
    def add_floor(self, data):
        """Dodaje novu etažu u zgradu."""
        floors = data["building"]["floors"]
        
        # Generiraj novi ID
        new_id = 1
        if floors:
            new_id = max(floor.get("id", 0) for floor in floors) + 1
        
        # Kreiraj novu etažu
        new_floor = {
            "id": new_id,
            "name": f"Etaža {new_id}",
            "screed_thickness": 45,
            "manifolds": [{
                "id": 1,
                "name": "Razdjelnik 1",
                "flow_temperature": 35,
                "ΔT": 5,
                "pipe_diameter": "16×2,0",
                "supply_pipe_length": 5.0,
                "return_pipe_length": 5.0,
                "supply_pipe_diameter": "20×2,3",
                "num_circuits": 2,  # Defaultno 2 kruga
                "rooms": [],
                "loops": []
            }]
        }
        
        # Dodaj etažu u podatke
        floors.append(new_floor)
        
        # Označi da ima promjena
        self.calculation_handler.mark_as_changed()
        
        # Automatski dodaj prostorije prema broju krugova
        floor_id = new_floor.get("id")
        manifold_id = 1  # Novi razdjelnik ima ID=1
        self.sync_rooms_with_circuits(floor_id, manifold_id, data)
        
        return new_floor
    
    def delete_floor(self, floor_id, data):
        """Briše etažu po ID-u."""
        floors = data["building"]["floors"]
        
        # Pronađi indeks etaže
        floor_index = None
        for i, floor in enumerate(floors):
            if floor.get("id") == floor_id:
                floor_index = i
                break
        
        # Ukloni etažu ako je pronađena
        if floor_index is not None:
            floors.pop(floor_index)
            self.calculation_handler.mark_as_changed()
            return True
        
        return False
    
    def add_manifold(self, floor, data):
        """Dodaje novi razdjelnik na etažu."""
        manifolds = floor.get("manifolds", [])
        if "manifolds" not in floor:
            floor["manifolds"] = manifolds
        
        # Generiraj novi ID
        new_id = 1
        if manifolds:
            new_id = max(manifold.get("id", 0) for manifold in manifolds) + 1
        
        # Kreiraj novi razdjelnik
        new_manifold = {
            "id": new_id,
            "name": f"Razdjelnik {new_id}",
            "flow_temperature": 35,
            "ΔT": 5,
            "pipe_diameter": "16×2,0",
            "supply_pipe_length": 5.0,
            "return_pipe_length": 5.0,
            "supply_pipe_diameter": "20×2,0",
            "num_circuits": 2,  # Promijenjeno s 4 na 2 kruga
            "rooms": [],
            "loops": []
        }
        
        # Dodaj razdjelnik na etažu
        manifolds.append(new_manifold)
        
        # Označi da ima promjena
        self.calculation_handler.mark_as_changed()
        
        # Automatski dodaj prostorije prema broju krugova
        floor_id = floor.get("id")
        if floor_id is not None:
            self.sync_rooms_with_circuits(floor_id, new_id, data)
        
        return new_manifold
    
    def delete_manifold(self, floor_id, manifold_id, data):
        """Briše razdjelnik po ID-u."""
        # Pronađi etažu
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                # Pronađi indeks razdjelnika
                manifold_index = None
                for i, manifold in enumerate(floor.get("manifolds", [])):
                    if manifold.get("id") == manifold_id:
                        manifold_index = i
                        break
                
                # Ukloni razdjelnik ako je pronađen
                if manifold_index is not None:
                    floor["manifolds"].pop(manifold_index)
                    self.calculation_handler.mark_as_changed()
                    return True
                
                break
        
        return False
    
    def add_room_to_manifold(self, floor_id, manifold_id, data):
        """Dodaje novu prostoriju na razdjelnik."""
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        rooms = manifold.get("rooms", [])
                        if "rooms" not in manifold:
                            manifold["rooms"] = rooms
                        
                        # Provjeri ograničenje broja prostorija
                        num_circuits = manifold.get("num_circuits", 4)
                        if len(rooms) >= num_circuits:
                            st.warning(f"Nije moguće dodati više prostorija. Razdjelnik ima {num_circuits} krugova.")
                            return None
                        
                        # Generiraj novi ID
                        new_id = 1
                        if rooms:
                            new_id = max(room.get("id", 0) for room in rooms) + 1
                        
                        # Odredi poziciju nove prostorije (dodaj na kraj)
                        new_position = 1
                        if rooms:
                            new_position = max(room.get("position", 0) for room in rooms) + 1
                        
                        # Dohvati prvu prostoriju s popisa (po defaultu "Blagovaonica")
                        first_room_type = "Blagovaonica"
                        if len(ROOM_TYPES) > 0 and 22 in ROOM_TYPES and len(ROOM_TYPES[22]) > 0:
                            # Ako postoje definirani tipovi prostorija, pronađi "Blagovaonicu" ili uzmi drugu po redu
                            if "Blagovaonica" in ROOM_TYPES[22]:
                                first_room_type = "Blagovaonica"
                            elif len(ROOM_TYPES[22]) > 1:
                                first_room_type = ROOM_TYPES[22][1]  # Uzmi drugu prostoriju s popisa
                            else:
                                first_room_type = ROOM_TYPES[22][0]  # Ako nema druge, uzmi prvu
                        
                        # Kreiraj novu prostoriju
                        new_room = {
                            "id": new_id,
                            "name": first_room_type,  # Uvijek prva prostorija s popisa
                            "position": new_position
                        }
                        
                        # Dodaj prostoriju na razdjelnik
                        rooms.append(new_room)
                        
                        # Dodaj i odgovarajuću petlju
                        loops = manifold.get("loops", [])
                        if "loops" not in manifold:
                            manifold["loops"] = loops
                        
                        # Dohvat preporučene temperature prema tipu prostorije
                        room_temp = get_room_temperature_for_name(first_room_type)
                        
                        # Odabir preporučenog razmaka cijevi prema tipu prostorije
                        pipe_spacing = 15  # Default
                        if room_temp >= 24:  # Za kupaonicu i slične (viša temperatura)
                            pipe_spacing = 10
                        elif room_temp >= 22:  # Za dnevni boravak i sl.
                            pipe_spacing = 15
                        else:  # Za ostale prostorije
                            pipe_spacing = 20

                        # Odabir preporučene podne obloge prema tipu prostorije
                        r_lambda = 0.00  # Default - keramička obloga
                        floor_covering_name = "Keramička obloga"
                        
                        if "Kupao" in first_room_type:
                            # Keramičke pločice (prva opcija)
                            r_lambda = 0.00
                            floor_covering_name = "Keramička obloga"
                        elif "Dnevni" in first_room_type or "Spava" in first_room_type:
                            # Drvena podloga (zadnja opcija)
                            r_lambda = 0.15
                            floor_covering_name = "Drvena obloga"
                        else:
                            # Plastična obloga (druga opcija)
                            r_lambda = 0.05
                            floor_covering_name = "Plastična obloga (tanka)"
                        
                        # Kreiraj novu petlju
                        new_loop = {
                            "id": new_id,
                            "room_name": new_room["name"],
                            "room_temperature": room_temp,
                            "r_lambda": r_lambda,
                            "floor_covering_name": floor_covering_name,
                            "pipe_spacing": pipe_spacing,
                            "area": None,
                            "manifold_distance": None,
                            "results": {}
                        }
                        
                        # Dodaj petlju u razdjelnik
                        loops.append(new_loop)
                        
                        # Označi da ima promjena
                        self.calculation_handler.mark_as_changed()
                        
                        return new_room, new_loop
                        
                        break
                break
        
        return None
    
    def update_room_numbers(self, floor_id, manifold_id, data):
        """Ažurira brojeve prostorija prema stvarnoj poziciji na listi."""
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        rooms = manifold.get("rooms", [])
                        
                        # Sortiraj prostorije prema poziciji
                        sorted_rooms = sorted(rooms, key=lambda x: x.get("position", 0))
                        
                        # Ažuriraj brojeve prostorija prema njihovoj stvarnoj poziciji
                        for i, room in enumerate(sorted_rooms):
                            # Označava broj prostorije kao poziciju + 1 (da počnu od 1, a ne od 0)
                            room_position = i + 1
                            room["position"] = room_position
                        
                        # Označi da ima promjena
                        self.calculation_handler.mark_as_changed()
                        return True
                        
                break
        
        return False
    
    def delete_room_from_manifold(self, floor_id, manifold_id, room_id, data):
        """Briše prostoriju s razdjelnika."""
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        # Pronađi indeks prostorije
                        room_index = None
                        for i, room in enumerate(manifold.get("rooms", [])):
                            if room.get("id") == room_id:
                                room_index = i
                                break
                        
                        # Ukloni prostoriju ako je pronađena
                        if room_index is not None:
                            manifold["rooms"].pop(room_index)
                            
                            # Pronađi i ukloni odgovarajuću petlju
                            loop_index = None
                            for i, loop in enumerate(manifold.get("loops", [])):
                                if loop.get("id") == room_id:
                                    loop_index = i
                                    break
                            
                            if loop_index is not None:
                                manifold["loops"].pop(loop_index)
                            
                            # Označi da ima promjena
                            self.calculation_handler.mark_as_changed()
                            return True
                        
                        break
                break
        
        return False
    
    def move_room_up(self, floor_id, manifold_id, room_id, data):
        """Pomiče prostoriju jedno mjesto gore (prema manjem indeksu)."""
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        rooms = manifold.get("rooms", [])
                        
                        # Sortiraj prostorije prema poziciji
                        sorted_rooms = sorted(rooms, key=lambda x: x.get("position", 0))
                        
                        # Pronađi prostoriju i njezin prethodnik
                        current_room = None
                        prev_room = None
                        for i, room in enumerate(sorted_rooms):
                            if room.get("id") == room_id:
                                if i > 0:  # Nije prva prostorija
                                    current_room = room
                                    prev_room = sorted_rooms[i-1]
                                break
                        
                        # Zamijeni pozicije ako su pronađene obje prostorije
                        if current_room and prev_room:
                            current_pos = current_room.get("position", 0)
                            prev_pos = prev_room.get("position", 0)
                            
                            current_room["position"] = prev_pos
                            prev_room["position"] = current_pos
                            
                            # Označi da ima promjena
                            self.calculation_handler.mark_as_changed()
                            return True
                        
                        break
                break
        
        return False
    
    def move_room_down(self, floor_id, manifold_id, room_id, data):
        """Pomiče prostoriju jedno mjesto dolje (prema većem indeksu)."""
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        rooms = manifold.get("rooms", [])
                        
                        # Sortiraj prostorije prema poziciji
                        sorted_rooms = sorted(rooms, key=lambda x: x.get("position", 0))
                        
                        # Pronađi prostoriju i njezin sljedbenik
                        current_room = None
                        next_room = None
                        for i, room in enumerate(sorted_rooms):
                            if room.get("id") == room_id:
                                if i < len(sorted_rooms) - 1:  # Nije zadnja prostorija
                                    current_room = room
                                    next_room = sorted_rooms[i+1]
                                break
                        
                        # Zamijeni pozicije ako su pronađene obje prostorije
                        if current_room and next_room:
                            current_pos = current_room.get("position", 0)
                            next_pos = next_room.get("position", 0)
                            
                            current_room["position"] = next_pos
                            next_room["position"] = current_pos
                            
                            # Označi da ima promjena
                            self.calculation_handler.mark_as_changed()
                            return True
                        
                        break
                break
        
        return False
        
    def get_custom_params_for_loop(self, loop, floor, manifold):
        """Dohvaća prilagođene parametre za petlju iz odgovarajućeg razdjelnika."""
        delta_t_value = manifold.get("ΔT", 5)
        return {
            "screed_thickness": floor.get("screed_thickness", 45),
            "flow_temperature": manifold.get("flow_temperature", 35),
            "ΔT": delta_t_value,
            "delta_t": delta_t_value,  # Dodano za kompatibilnost - ista vrijednost ali drugačiji ključ
            "pipe_diameter": manifold.get("pipe_diameter", "16×2,0")
        }
        
    def get_room_temperature_for_name(self, room_name):
        """Dohvaća preporučenu temperaturu za prostoriju prema imenu."""
        return get_room_temperature_for_name(room_name)
        
    def sync_rooms_with_circuits(self, floor_id, manifold_id, data):
        """Sinkronizira broj prostorija s brojem krugova razdjelnika."""
        # Pronađi razdjelnik
        for floor in data["building"]["floors"]:
            if floor.get("id") == floor_id:
                for manifold in floor.get("manifolds", []):
                    if manifold.get("id") == manifold_id:
                        num_circuits = manifold.get("num_circuits", 4)
                        rooms = manifold.get("rooms", [])
                        
                        # Ako ima previše prostorija, ukloni višak s kraja
                        if len(rooms) > num_circuits:
                            # Sortiramo prema poziciji prije uklanjanja
                            sorted_rooms = sorted(rooms, key=lambda x: x.get("position", 0))
                            rooms_to_remove = sorted_rooms[num_circuits:]
                            
                            for room in rooms_to_remove:
                                self.delete_room_from_manifold(floor_id, manifold_id, room.get("id"), data)
                            
                            # Nakon brisanja prostorija, potrebno je ažurirati brojeve preostalih prostorija
                            self.update_room_numbers(floor_id, manifold_id, data)
                        
                        # Ako ima premalo prostorija, dodaj nove do broja krugova
                        while len(rooms) < num_circuits:
                            self.add_room_to_manifold(floor_id, manifold_id, data)
                        
                        return True
        
        return False