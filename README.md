# Celestial Bodies Calculator

A Python program that calculates and displays key properties of celestial bodies.

## Units

- **Mass**: kilograms (kg)
- **Radius**: kilometers (km) for input/display, converted to meters (m) for calculations
- **Surface Gravity**: meters per second squared (m/s²)
- **Escape Velocity**: kilometers per second (km/s) for display, calculated in m/s internally

## Implementation Details

- Uses gravitational constant G = 6.67430e-11 m³/kg·s²
- Surface gravity calculated as g = GM/r²
- Escape velocity calculated as v = √(2GM/r)
- Rich library used for formatted table output

## Development Notes

### Setup
1. Use Python virtual environment in `venv/`
2. Install dependencies: `pip install rich`
3. Run with VS Code debugger using `.vscode/launch.json` config

### Important Considerations
- Always convert radius to meters (×1000) before calculations
- Escape velocity needs conversion back to km/s (÷1000) for display
- Keep G constant at 6.67430e-11 for precision
- Use scientific notation (:.2e) for mass display
- Update this file before every git commit