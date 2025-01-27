import math
from rich.console import Console
from rich.table import Table


class CelestialBody:
    def __init__(self, name: str, mass: float, radius: float, color: tuple[int, int, int], parent_body: 'CelestialBody' = None, distance_from_parent_km: float = 0):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.color = color
        self.parent_body = parent_body
        self.distance_from_parent_km = distance_from_parent_km
      
    @property
    def surface_gravity(self):
        radius_meters = self.radius * 1000  # Convert km to m
        return 6.67430e-11 * self.mass / (radius_meters ** 2)
      
    def gravity_at_distance(self, distance_km: float) -> float:
        """Calculate gravitational acceleration at a given distance from the body's center.
        
        Args:
            distance_km: Distance from center in kilometers
            
        Returns:
            Gravitational acceleration in m/s²
        """
        distance_meters = distance_km * 1000  # Convert km to m
        return 6.67430e-11 * self.mass / (distance_meters ** 2)
    
    def orbital_velocity(self, altitude_km: float) -> float:
        """Calculate velocity needed for circular orbit at given altitude above surface.
        
        Args:
            altitude_km: Altitude above surface in kilometers
            
        Returns:
            Orbital velocity in m/s
        """
        orbit_radius_km = self.radius + altitude_km
        # v = sqrt(GM/r) for circular orbit
        orbit_radius_m = orbit_radius_km * 1000
        return math.sqrt(6.67430e-11 * self.mass / orbit_radius_m)
      
    @property
    def escape_velocity(self):
        radius_meters = self.radius * 1000  # Convert km to m
        return math.sqrt(2 * 6.67430e-11 * self.mass / radius_meters)
        
    def __str__(self):
        parent_info = f", orbiting {self.parent_body.name}" if self.parent_body else ""
        return f"{self.name} ({self.mass:.2e} kg, {self.radius} km{parent_info})"
    
    def __repr__(self):
        return f"CelestialBody(name={self.name}, mass={self.mass}, radius={self.radius}, color={self.color})"
        

def main():
    console = Console()
    table = Table(title="Celestial Bodies Information")
    
    # Add columns
    table.add_column("Name", style="cyan")
    table.add_column("M (kg)", justify="right", style="yellow")
    table.add_column("R (km)", justify="right", style="yellow")
    table.add_column("SG (m/s²)", justify="right", style="yellow")
    table.add_column("EV (km/s)", justify="right", style="yellow")
    table.add_column("Orbit(km/s) 200km", justify="right", style="yellow")
    table.add_column("Parent Body", style="cyan")
    table.add_column("Distance (km)", justify="right", style="yellow")
    
    # Create bodies
    sun = CelestialBody("Sun", 1.989e30, 696340.0, (255, 255, 0))
    mercury = CelestialBody("Mercury", 3.285e23, 2439.7, (169, 169, 169), sun, 57.9e6)
    venus = CelestialBody("Venus", 4.867e24, 6051.8, (255, 198, 73), sun, 108.2e6)
    earth = CelestialBody("Earth", 5.972e24, 6371.0, (0, 0, 255), sun, 149.6e6)
    mars = CelestialBody("Mars", 6.39e23, 3389.5, (255, 0, 0), sun, 227.9e6)
    jupiter = CelestialBody("Jupiter", 1.898e27, 69911.0, (255, 165, 0), sun, 778.5e6)
    saturn = CelestialBody("Saturn", 5.683e26, 58232.0, (238, 232, 205), sun, 1.434e9)
    uranus = CelestialBody("Uranus", 8.681e25, 25362.0, (173, 216, 230), sun, 2.871e9)
    neptune = CelestialBody("Neptune", 1.024e26, 24622.0, (0, 0, 139), sun, 4.495e9)
    moon = CelestialBody("Moon", 7.348e22, 1737.4, (128, 128, 128), earth, 384400)
    
    planets = [sun, mercury, venus, earth, mars, jupiter, saturn, uranus, neptune, moon]
    
    for planet in planets:
        table.add_row(
            planet.name,
            f"{planet.mass:.2e}",
            f"{planet.radius:.1f}",
            f"{planet.surface_gravity:.1f}",
            f"{planet.escape_velocity/1000:.1f}",  # Convert to km/s
            f"{planet.orbital_velocity(200)/1000:.1f}",  # Convert to km/s
            planet.parent_body.name if planet.parent_body else "-",
            f"{planet.distance_from_parent_km:,.0f}" if planet.parent_body else "-"
        )
    
    console.print(table)
    
    
if __name__ == "__main__":
    main()
