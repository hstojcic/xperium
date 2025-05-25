# modules/thermal/ventilation/ventilation_recovery/ui/__init__.py

"""
UI components for the ventilation recovery calculator.

This module centralizes all UI components for rendering different tabs
of the ventilation recovery calculator.
"""

from modules.thermal.ventilation.ventilation_recovery.ui.basic_info_ui import render_basic_info_tab
from modules.thermal.ventilation.ventilation_recovery.ui.airflow_ui import render_airflow_tab
from modules.thermal.ventilation.ventilation_recovery.ui.ducts_ui import render_ducts_tab
from modules.thermal.ventilation.ventilation_recovery.ui.recuperator_ui import render_recuperator_tab, calculate_heater_power
from modules.thermal.ventilation.ventilation_recovery.ui.energy_ui import render_energy_tab

# Export all UI components
__all__ = [
    'render_basic_info_tab',
    'render_airflow_tab',
    'render_ducts_tab',
    'render_recuperator_tab',
    'render_energy_tab',
    'calculate_heater_power'
]