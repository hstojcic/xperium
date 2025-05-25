# modules/thermal/ventilation/ventilation_recovery/ui_components.py
"""
This module provides backwards compatibility by re-exporting all
UI components from the ui/ package. This ensures existing code that
imports from ui_components still works without modification.

For new code, it's recommended to import directly from the ui package:
from modules.thermal.ventilation.ventilation_recovery.ui import (
    render_basic_info_tab,
    render_airflow_tab,
    render_ducts_tab,
    render_recuperator_tab,
    render_energy_tab,
    calculate_heater_power
)
"""

from modules.thermal.ventilation.ventilation_recovery.ui import (
    render_basic_info_tab,
    render_airflow_tab,
    render_ducts_tab,
    render_recuperator_tab,
    render_energy_tab,
    calculate_heater_power
)

# Re-export all components for backwards compatibility
__all__ = [
    'render_basic_info_tab',
    'render_airflow_tab',
    'render_ducts_tab',
    'render_recuperator_tab',
    'render_energy_tab',
    'calculate_heater_power'
]