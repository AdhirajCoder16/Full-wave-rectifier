# Full Wave Rectifier – simulation and report figures

Applied Physics (UPH004) project, Thapar Institute of Engineering and Technology.

Python code that simulates the bridge rectifier built for the project (4 × 1N4007, 1000 µF / 25 V filter capacitor,
green LED with 1 kΩ series resistor, 230 V / 12 V transformer) and produces the figures and table values used in the report.

## Files
| File | Purpose |
|---|---|
| `rectifier_figures.ipynb` | Colab / Jupyter notebook (same code as the script, split into cells) |
| `rectifier_figures.py` | Same code as a plain script |
| `photos/` | Photos of the built circuit (used for Figs. 8 and 9) |
| `figures/` | Generated figures (created when you run the code) |

## Run it
**Google Colab:** upload the notebook (File → Upload notebook), upload the three photos into a `photos/` folder, then Runtime → Run all.

**Locally:**
```
pip install -r requirements.txt
python rectifier_figures.py
```

## Model and assumptions
- Ideal transformer, 12 V rms secondary, 50 Hz.
- Constant 0.7 V drop per diode (two conduct at a time), LED drop 2 V, series resistor 1 kΩ.
- All values are **calculated / simulated**, not measured. Change the parameters at the top of the code to match your board.
