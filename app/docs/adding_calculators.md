# Upute za dodavanje novih kalkulatora

## Automatsko otkrivanje kalkulatora

Sustav sada automatski otkriva sve dostupne kalkulatore koji nasljeđuju `BaseCalculation` klasu.
Nije potrebno ručno registrirati nove kalkulatore - oni će biti automatski otkriveni i prikazani
u odgovarajućim kategorijama i podkategorijama.

## Struktura direktorija

Da bi kalkulator bio ispravno kategoriziran, mora se nalaziti u odgovarajućoj strukturi direktorija:

```
modules/
  ├── hydraulic/             # Hidrotehničke instalacije
  │   ├── water_supply/      # Instalacije vodovoda
  │   ├── sanitary_drainage/ # Instalacije sanitarne kanalizacije
  │   ├── rainwater_drainage/ # Instalacije oborinske kanalizacije
  │   ├── fire_protection/   # Instalacije zaštite od požara
  │   └── pool_systems/      # Instalacije bazenske tehnike
  │
  └── thermal/               # Termotehničke instalacije
      ├── gas/               # Instalacije plina
      ├── heating/           # Instalacije grijanja
      ├── cooling/           # Instalacije hlađenja
      ├── hvac/              # Instalacije grijanja i hlađenja
      └── ventilation/       # Instalacije ventilacije
```

## Koraci za dodavanje novog kalkulatora

1. Stvorite novu Python datoteku u odgovarajućem direktoriju (npr. `modules/hydraulic/water_supply/new_calc.py`)
2. Implementirajte klasu koja nasljeđuje `BaseCalculation`:

```python
from modules.base import BaseCalculation

class MyNewCalculator(BaseCalculation):
    def __init__(self):
        super().__init__(name="Moj novi kalkulator")
        
    def render(self):
        # Implementacija sučelja kalkulatora
        pass
        
    # Ostale metode...
```

3. Nakon dodavanja novog kalkulatora, ako je aplikacija već pokrenuta, kliknite na gumb "Osvježi popis kalkulatora"
   na ekranu za odabir proračuna.

## Rješavanje problema

Ako kalkulator nije automatski otkriven:

1. Provjerite je li u ispravnom direktoriju prema strukturi kategorija
2. Provjerite nasljeđuje li ispravno `BaseCalculation` klasu
3. Provjerite je li ime klase jedinstveno
4. Ručno osvježite popis kalkulatora klikom na gumb "Osvježi popis kalkulatora"
