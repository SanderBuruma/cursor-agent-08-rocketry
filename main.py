import math
from rich.console import Console
from rich.table import Table


class CelestialBody:
    def __init__(self, name: str, mass: float, radius: float, color: tuple[int, int, int]):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.color = color
      
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
        return f"{self.name} ({self.mass} kg, {self.radius} m, {self.color})"
    
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
    
    planets: list[CelestialBody] = []
    planets.append(CelestialBody("Sun", 1.989e30, 696340.0, (255, 255, 0)))
    planets.append(CelestialBody("Mercury", 3.285e23, 2439.7, (169, 169, 169)))
    planets.append(CelestialBody("Venus", 4.867e24, 6051.8, (255, 198, 73)))
    planets.append(CelestialBody("Earth", 5.972e24, 6371.0, (0, 0, 255)))
    planets.append(CelestialBody("Mars", 6.39e23, 3389.5, (255, 0, 0)))
    planets.append(CelestialBody("Jupiter", 1.898e27, 69911.0, (255, 165, 0)))
    planets.append(CelestialBody("Saturn", 5.683e26, 58232.0, (238, 232, 205)))
    planets.append(CelestialBody("Uranus", 8.681e25, 25362.0, (173, 216, 230)))
    planets.append(CelestialBody("Neptune", 1.024e26, 24622.0, (0, 0, 139)))
    planets.append(CelestialBody("Moon", 7.348e22, 1737.4, (128, 128, 128)))
    
    for planet in planets:
        table.add_row(
            planet.name,
            f"{planet.mass:.2e}",
            f"{planet.radius:.1f}",
            f"{planet.surface_gravity:.1f}",
            f"{planet.escape_velocity/1000:.1f}",  # Convert to km/s
            f"{planet.orbital_velocity(200):.1f}"
        )
    
    console.print(table)
    
    
if __name__ == "__main__":
    main()
