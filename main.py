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
    
    # Mercury and Venus have no moons
    mercury = CelestialBody("Mercury", 3.285e23, 2439.7, (169, 169, 169), sun, 57.9e6)
    venus = CelestialBody("Venus", 4.867e24, 6051.8, (255, 198, 73), sun, 108.2e6)
    
    # Earth and Moon
    earth = CelestialBody("Earth", 5.972e24, 6371.0, (0, 0, 255), sun, 149.6e6)
    moon = CelestialBody("Moon", 7.348e22, 1737.4, (128, 128, 128), earth, 384400)
    
    # Mars and its moons
    mars = CelestialBody("Mars", 6.39e23, 3389.5, (255, 0, 0), sun, 227.9e6)
    phobos = CelestialBody("Phobos", 1.06e16, 11.267, (169, 169, 169), mars, 9377)
    deimos = CelestialBody("Deimos", 1.48e15, 6.2, (169, 169, 169), mars, 23460)
    
    # Jupiter and its major moons
    jupiter = CelestialBody("Jupiter", 1.898e27, 69911.0, (255, 165, 0), sun, 778.5e6)
    io = CelestialBody("Io", 8.932e22, 1821.6, (255, 255, 150), jupiter, 421700)
    europa = CelestialBody("Europa", 4.800e22, 1560.8, (255, 220, 200), jupiter, 671100)
    ganymede = CelestialBody("Ganymede", 1.482e23, 2634.1, (169, 169, 169), jupiter, 1070400)
    callisto = CelestialBody("Callisto", 1.076e23, 2410.3, (128, 128, 128), jupiter, 1882700)
    
    # Saturn and its major moons
    saturn = CelestialBody("Saturn", 5.683e26, 58232.0, (238, 232, 205), sun, 1.434e9)
    titan = CelestialBody("Titan", 1.345e23, 2574.73, (255, 200, 100), saturn, 1221870)
    rhea = CelestialBody("Rhea", 2.307e21, 763.8, (200, 200, 200), saturn, 527108)
    iapetus = CelestialBody("Iapetus", 1.806e21, 734.5, (200, 200, 200), saturn, 3560820)
    enceladus = CelestialBody("Enceladus", 1.080e20, 252.1, (255, 255, 255), saturn, 237948)
    
    # Uranus and its major moons
    uranus = CelestialBody("Uranus", 8.681e25, 25362.0, (173, 216, 230), sun, 2.871e9)
    titania = CelestialBody("Titania", 3.527e21, 788.9, (169, 169, 169), uranus, 435910)
    oberon = CelestialBody("Oberon", 3.014e21, 761.4, (169, 169, 169), uranus, 583520)
    miranda = CelestialBody("Miranda", 6.59e19, 235.8, (169, 169, 169), uranus, 129390)
    
    # Neptune and its major moons
    neptune = CelestialBody("Neptune", 1.024e26, 24622.0, (0, 0, 139), sun, 4.495e9)
    triton = CelestialBody("Triton", 2.139e22, 1353.4, (200, 200, 200), neptune, 354759)
    naiad = CelestialBody("Naiad", 1.9e17, 33.0, (169, 169, 169), neptune, 48227)
    
    bodies = [
        sun,
        mercury, venus,
        earth, moon,
        mars, phobos, deimos,
        jupiter, io, europa, ganymede, callisto,
        saturn, titan, rhea, iapetus, enceladus,
        uranus, titania, oberon, miranda,
        neptune, triton, naiad
    ]
    
    for body in bodies:
        table.add_row(
            body.name,
            f"{body.mass:.2e}",
            f"{body.radius:.1f}",
            f"{body.surface_gravity:.1f}",
            f"{body.escape_velocity/1000:.1f}",  # Convert to km/s
            f"{body.orbital_velocity(200)/1000:.1f}",  # Convert to km/s
            body.parent_body.name if body.parent_body else "-",
            f"{body.distance_from_parent_km:,.0f}" if body.parent_body else "-"
        )
    
    console.print(table)
    
    
if __name__ == "__main__":
    main()
