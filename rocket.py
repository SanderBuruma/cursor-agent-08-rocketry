from dataclasses import dataclass
from decimal import Decimal, getcontext
import math
from main import CelestialBody
from main import main as main_
from rich.console import Console
from rich.table import Table

getcontext().prec = 50


@dataclass
class Rocket:
    """
    Represents a rocket with physical properties and performance characteristics.
    
    Attributes:
        dry_mass (Decimal): Mass of the rocket without fuel in kg
        fuel_mass (Decimal): Mass of fuel in kg
        thrust (Decimal): Engine thrust in Newtons
        fuel_consumption (Decimal): Fuel consumption rate in kg/s
        parent_body (CelestialBody): The celestial body the rocket is orbiting/launching from
        distance_from_parent_km (Decimal): Distance from parent body's center in km
    """
    dry_mass: Decimal
    fuel_mass: Decimal
    thrust: Decimal
    fuel_consumption: Decimal
    parent_body: CelestialBody
    distance_from_parent_km: Decimal
    
    def __post_init__(self):
        """Convert any numeric inputs to Decimal and calculate Isp if not provided."""
        self.dry_mass = Decimal(str(self.dry_mass))
        self.fuel_mass = Decimal(str(self.fuel_mass))
        self.thrust = Decimal(str(self.thrust))
        self.fuel_consumption = Decimal(str(self.fuel_consumption))
        self.distance_from_parent_km = Decimal(str(self.distance_from_parent_km))
        
    
    @property
    def total_mass(self) -> Decimal:
        """Total mass of the rocket including fuel."""
        return self.dry_mass + self.fuel_mass
    
    @property
    def mass_ratio(self) -> Decimal:
        """Mass ratio (total mass / dry mass)."""
        return self.total_mass / self.dry_mass
    
    @property
    def exhaust_velocity(self) -> Decimal:
        """Effective exhaust velocity in m/s."""
        return self.thrust / self.fuel_consumption
    
    @property
    def delta_v(self) -> Decimal:
        """
        Calculate the ideal delta-v using the Tsiolkovsky rocket equation.
        Returns the result in m/s.
        """
        try:
            return self.exhaust_velocity * Decimal(str(math.log(float(self.mass_ratio))))
        except (ValueError, ZeroDivisionError):
            return Decimal('0')
    
    @property
    def burn_time(self) -> Decimal:
        """Calculate the total burn time in seconds based on fuel mass and consumption rate."""
        try:
            return self.fuel_mass / self.fuel_consumption
        except ZeroDivisionError:
            return Decimal('0')
    
    @property
    def local_gravity(self) -> Decimal:
        """Calculate the local gravitational acceleration at the rocket's current position."""
        return self.parent_body.gravity_at_distance(self.distance_from_parent_km)
    
    @property
    def thrust_to_weight(self) -> Decimal:
        """Calculate the thrust-to-weight ratio using local gravity."""
        return self.thrust / (self.total_mass * self.local_gravity)

    def update_fuel(self, elapsed_time: Decimal) -> None:
        """
        Update the fuel mass based on elapsed time and consumption rate.
        
        Args:
            elapsed_time (Decimal): Time elapsed in seconds
        """
        fuel_used = self.fuel_consumption * elapsed_time
        self.fuel_mass = max(Decimal('0'), self.fuel_mass - fuel_used)

    def update_distance(self, new_distance_km: Decimal) -> None:
        """
        Update the rocket's distance from its parent body.
        
        Args:
            new_distance_km (Decimal): New distance from parent body's center in km
        """
        self.distance_from_parent_km = max(Decimal('0'), new_distance_km)

# Example usage:
if __name__ == "__main__":
    # Get celestial bodies
    bodies = main_()
    earth = next(b for b in bodies if b.name == "Earth")
    
    # Example rocket with properties similar to a small orbital launcher
    # Starting from Earth's surface
    rocket = Rocket(
        dry_mass=1000,  # 1000 kg dry mass
        fuel_mass=9000,  # 9000 kg fuel mass
        thrust=150000,   # 100 kN thrust
        fuel_consumption=40,  # 40 kg/s fuel consumption
        parent_body=earth,
        distance_from_parent_km=earth.radius  # Starting from surface
    )
    
    # Create Rich table
    console = Console()
    table = Table(title="Rocket Performance Characteristics")
    
    # Add columns
    table.add_column("Property", style="cyan")
    table.add_column("Value", justify="right", style="yellow")
    table.add_column("Unit", style="green")
    
    # Add rows with rocket properties
    table.add_row("Dry Mass", f"{rocket.dry_mass:,.0f}", "kg")
    table.add_row("Fuel Mass", f"{rocket.fuel_mass:,.0f}", "kg")
    table.add_row("Total Mass", f"{rocket.total_mass:,.0f}", "kg")
    table.add_row("Mass Ratio", f"{rocket.mass_ratio:.2f}", "-")
    table.add_row("Thrust", f"{rocket.thrust/Decimal('1000'):,.0f}", "kN")
    table.add_row("Fuel Consumption", f"{rocket.fuel_consumption:.0f}", "kg/s")
    table.add_row("Exhaust Velocity", f"{rocket.exhaust_velocity:,.0f}", "m/s")
    table.add_row("Delta-v", f"{rocket.delta_v:,.0f}", "m/s")
    table.add_row("Burn Time", f"{rocket.burn_time:.0f}", "s")
    table.add_row("Local Gravity", f"{rocket.local_gravity:.2f}", "m/s²")
    table.add_row("Thrust-to-Weight Ratio", f"{rocket.thrust_to_weight:.2f}", "-")
    table.add_row("Parent Body", rocket.parent_body.name, "-")
    table.add_row("Distance from Parent", f"{rocket.distance_from_parent_km:,.0f}", "km")
    
    # Print the table
    console.print(table) 