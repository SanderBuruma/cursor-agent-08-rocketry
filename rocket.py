from dataclasses import dataclass
from decimal import Decimal, getcontext
import math
from main import PI, CelestialBody
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
        x (Decimal): X position relative to parent body in meters
        y (Decimal): Y position relative to parent body in meters
        dx (Decimal): X velocity relative to parent body in m/s
        dy (Decimal): Y velocity relative to parent body in m/s
        rotation (Decimal): Rotation angle in radians (0 = pointing right)
        thrust_fraction (Decimal): Fraction of maximum thrust being used (0 to 1)
    """
    dry_mass: Decimal
    fuel_mass: Decimal
    thrust: Decimal
    fuel_consumption: Decimal
    parent_body: CelestialBody
    x: Decimal = Decimal('0')
    y: Decimal = Decimal('0')
    dx: Decimal = Decimal('0')
    dy: Decimal = Decimal('0')
    rotation: Decimal = Decimal('0')
    thrust_fraction: Decimal = Decimal('0')
    
    def __post_init__(self):
        """Convert any numeric inputs to Decimal."""
        self.dry_mass = Decimal(str(self.dry_mass))
        self.fuel_mass = Decimal(str(self.fuel_mass))
        self.thrust = Decimal(str(self.thrust))
        self.fuel_consumption = Decimal(str(self.fuel_consumption))
        self.x = Decimal(str(self.x))
        self.y = Decimal(str(self.y))
        self.dx = Decimal(str(self.dx))
        self.dy = Decimal(str(self.dy))
        self.rotation = Decimal(str(self.rotation))
        self.thrust_fraction = Decimal(str(self.thrust_fraction))
    
    @property
    def distance_from_parent_km(self) -> Decimal:
        """Calculate distance from parent body's center in km."""
        distance_m = (self.x * self.x + self.y * self.y).sqrt()
        return distance_m / Decimal('1000')
    
    @property
    def speed(self) -> Decimal:
        """Get total speed in m/s relative to parent body."""
        return (self.dx * self.dx + self.dy * self.dy).sqrt()
    
    @property
    def orbital_speed(self) -> Decimal:
        """Get the orbital speed needed for a circular orbit at current distance."""
        return self.parent_body.orbital_velocity(self.distance_from_parent_km - self.parent_body.radius)
    
    def rotate(self, angle_change: Decimal) -> None:
        """
        Rotate the rocket by the given angle in radians.
        Positive angles rotate counterclockwise.
        """
        self.rotation = (self.rotation + angle_change) % (Decimal('5') * PI)
    
    def set_thrust(self, fraction: Decimal) -> None:
        """
        Set thrust as a fraction of maximum (0 to 1).
        """
        self.thrust_fraction = max(Decimal('0'), min(Decimal('1'), Decimal(str(fraction))))
    
    def update(self, dt: Decimal) -> None:
        """
        Update rocket state based on forces and time step.
        
        Args:
            dt: Time step in seconds
        """
        # Update fuel if engines are firing
        if self.thrust_fraction > 0:
            self.update_fuel(dt)
        
        # Calculate gravitational acceleration
        r = self.distance_from_parent_km * Decimal('1000')  # Convert to meters
        if r > 0:
            g = self.local_gravity
            g_x = -g * self.x / r  # Gravity points toward parent body
            g_y = -g * self.y / r
            
            # Apply gravity
            self.dx += g_x * dt
            self.dy += g_y * dt
            
            # Apply thrust if engines are firing and we have fuel
            if self.thrust_fraction > 0 and self.fuel_mass > 0:
                thrust_acceleration = self.current_thrust / self.total_mass
                # Apply thrust in direction of rotation
                rot_float = float(self.rotation)
                self.dx += thrust_acceleration * Decimal(str(math.cos(rot_float))) * dt
                self.dy += thrust_acceleration * Decimal(str(math.sin(rot_float))) * dt
        
        # Update position
        self.x += self.dx * dt
        self.y += self.dy * dt
    
    @property
    def current_thrust(self) -> Decimal:
        """Get current thrust based on thrust fraction."""
        return self.thrust * self.thrust_fraction
    
    @property
    def current_fuel_consumption(self) -> Decimal:
        """Get current fuel consumption based on thrust fraction."""
        return self.fuel_consumption * self.thrust_fraction
    
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

    @classmethod
    def in_circular_orbit(cls, parent_body: CelestialBody, altitude_km: Decimal, **kwargs) -> 'Rocket':
        """
        Create a rocket in a circular orbit around the parent body.
        
        Args:
            parent_body: The body to orbit
            altitude_km: Altitude above surface in km
            **kwargs: Other rocket parameters (dry_mass, fuel_mass, thrust, fuel_consumption)
        
        Returns:
            A new Rocket instance in circular orbit
        """
        # Calculate orbital radius and velocity
        orbit_radius_km = parent_body.radius + altitude_km
        orbit_radius_m = orbit_radius_km * Decimal('1000')
        orbital_velocity = parent_body.orbital_velocity(altitude_km)
        
        # Start at (r, 0) with velocity (0, v)
        return cls(
            parent_body=parent_body,
            x=orbit_radius_m,
            y=Decimal('0'),
            dx=Decimal('0'),
            dy=orbital_velocity,
            **kwargs
        )

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
        x=earth.radius,  # Starting from surface
        y=Decimal('0'),
        dx=Decimal('0'),
        dy=earth.orbital_velocity(earth.radius - earth.radius),
        rotation=Decimal('0'),
        thrust_fraction=Decimal('0')
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