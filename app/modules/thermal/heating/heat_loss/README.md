# Heat Loss Calculator - Code Structure Documentation

## Overview
This document provides information about the code structure of the Heat Loss Calculator module, which has been refactored to improve maintainability by dividing it into smaller files and grouping related functionality.

## Directory Structure

```
app/modules/thermal/heating/heat_loss/
├── __init__.py                   # Module initialization
├── heat_loss_calc.py             # Main calculator entry point
├── constants.py                  # Global constants
├── calculations/                 # Calculation logic
│   ├── __init__.py
│   └── heat_loss_calculation.py  # Core heat loss calculation functions
├── controllers/                  # Controllers for MVC pattern
│   ├── __init__.py
│   ├── etaza_controller.py       # Controller for floor management
│   ├── prostorija_controller.py  # Controller for room management
│   └── zid_controller.py         # Controller for wall management
├── models/                       # Data models
│   ├── __init__.py
│   ├── etaza.py                  # Floor model
│   ├── model.py                  # Main MultiRoomModel
│   ├── prostorija.py             # Room model
│   └── elementi/                 # Building element models
│       ├── __init__.py
│       ├── building_elements_model.py  # Model for building elements
│       ├── constants.py          # Constants for building elements
│       ├── segment_zida.py       # Wall segment model
│       ├── wall_elements.py      # Wall elements model (windows, doors)
│       └── zid.py                # Wall model
└── ui/                           # User interface components
    ├── __init__.py
    ├── etaza_ui.py               # Floor UI components
    ├── prostorija_ui.py          # Room UI components
    ├── results_ui.py             # Results UI components
    └── zid_ui.py                 # Wall UI components
```

## Key Components

### Models
- **MultiRoomModel** (`models/model.py`): The main model that contains all floors, rooms, and walls.
- **Etaza** (`models/etaza.py`): Represents a floor in the building.
- **Prostorija** (`models/prostorija.py`): Represents a room in a floor.
- **BuildingElementsModel** (`models/elementi/building_elements_model.py`): Manages building elements like walls, floors, ceilings, windows, and doors.

### Controllers
- **EtazaController**: Manages the creation, editing, and deletion of floors.
- **ProstorijaController**: Manages the creation, editing, and deletion of rooms.
- **ZidController**: Manages the creation, editing, and deletion of walls.

### UI Components
- **etaza_ui.py**: UI components for managing floors.
- **prostorija_ui.py**: UI components for managing rooms.
- **zid_ui.py**: UI components for managing walls.
- **results_ui.py**: UI components for displaying calculation results.

### Calculations
- **heat_loss_calculation.py**: Contains functions for calculating heat loss for rooms, floors, and the entire building.

## Main Workflows
1. The user creates one or more floors (etaže).
2. For each floor, the user creates rooms (prostorije).
3. For each room, the user defines walls, floor, and ceiling properties.
4. For each wall, the user may add windows and doors.
5. The application calculates the heat loss based on room dimensions, building elements, and temperature differences.
6. Results are displayed for each room, floor, and the entire building.

## Session State Management
The application uses Streamlit's session state to persist data between user interactions. Key session state items include:
- `heat_loss_model`: Stores the current MultiRoomModel instance.
- `building_elements_data`: Stores the current BuildingElementsModel data.

## Development Guidelines
1. Follow the MVC pattern with clear separation of models, views, and controllers.
2. Place new models in the `models/` directory.
3. Place UI components in the `ui/` directory.
4. Place controllers in the `controllers/` directory.
5. Place calculation logic in the `calculations/` directory.
6. Use session state for data persistence.
7. Document all functions and classes with docstrings.
