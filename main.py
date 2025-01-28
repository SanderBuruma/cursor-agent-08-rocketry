import math
from decimal import Decimal, getcontext
from rich.console import Console
from rich.table import Table

# Set precision to 50 decimal places
getcontext().prec = 50

# Define pi with high precision
PI = Decimal('3.14159265358979323846264338327950288419716939937510')

class CelestialBody:
    G = Decimal('6.67430e-11')  # Gravitational constant in m³/kg·s²
    
    def __init__(self, name: str, mass: Decimal, radius: Decimal, color: tuple[int, int, int], 
                 parent_body: 'CelestialBody' = None, distance_from_parent_km: Decimal = Decimal('0')):
        self.name = name
        self.mass = Decimal(str(mass))
        self.radius = Decimal(str(radius))
        self.color = color
        self.parent_body = parent_body
        self.distance_from_parent_km = Decimal(str(distance_from_parent_km))
        self._orbit_angle = Decimal('0.0')  # Angle in radians
      
    def get_position(self) -> tuple[Decimal, Decimal]:
        """Calculate x,y coordinates in meters relative to parent body.
        Assumes parent is at (0,0) and uses current orbit angle.
        
        Returns:
            Tuple of (x, y) coordinates in meters
        """
        if not self.parent_body:
            return (Decimal('0'), Decimal('0'))
            
        distance_m = self.distance_from_parent_km * Decimal('1000')
        # Convert to float for trig functions, then back to Decimal
        angle_float = float(self._orbit_angle)
        x = distance_m * Decimal(str(math.cos(angle_float)))
        y = distance_m * Decimal(str(math.sin(angle_float)))
        return (x, y)
        
    def update_position(self, angle_radians: Decimal):
        """Update the orbital position angle.
        
        Args:
            angle_radians: New angle in radians (0 = along x-axis)
        """
        self._orbit_angle = angle_radians % (Decimal('2') * PI)
      
    @property
    def surface_gravity(self) -> Decimal:
        radius_meters = self.radius * Decimal('1000')  # Convert km to m
        return self.G * self.mass / (radius_meters ** Decimal('2'))
      
    def gravity_at_distance(self, distance_km: Decimal) -> Decimal:
        """Calculate gravitational acceleration at a given distance from the body's center.
        
        Args:
            distance_km: Distance from center in kilometers
            
        Returns:
            Gravitational acceleration in m/s²
        """
        distance_meters = distance_km * Decimal('1000')  # Convert km to m
        return self.G * self.mass / (distance_meters ** Decimal('2'))
    
    def orbital_velocity(self, altitude_km: Decimal) -> Decimal:
        """Calculate velocity needed for circular orbit at given altitude above surface.
        
        Args:
            altitude_km: Altitude above surface in kilometers
            
        Returns:
            Orbital velocity in m/s
        """
        orbit_radius_km = self.radius + Decimal(str(altitude_km))
        orbit_radius_m = orbit_radius_km * Decimal('1000')
        return (self.G * self.mass / orbit_radius_m).sqrt()
      
    @property
    def escape_velocity(self) -> Decimal:
        radius_meters = self.radius * Decimal('1000')  # Convert km to m
        return (Decimal('2') * self.G * self.mass / radius_meters).sqrt()
        
    @property
    def current_orbital_velocity(self) -> Decimal:
        """Calculate the orbital velocity at the current distance from parent body.
        Returns velocity in m/s, or 0 if this is the sun (no parent)."""
        if not self.parent_body:
            return Decimal('0')
        return (self.G * self.parent_body.mass / (self.distance_from_parent_km * Decimal('1000'))).sqrt()
        
    @property
    def sphere_of_influence(self) -> Decimal:
        """
        Calculate the radius of the body's sphere of influence in kilometers.
        Uses the formula: r_soi = a * (m/M)^(2/5), where:
        - a is the semi-major axis (distance from parent)
        - m is the body's mass
        - M is the parent body's mass
        
        Returns:
            Radius of sphere of influence in km, or None if body has no parent
        """
        if not self.parent_body:
            return None
            
        mass_ratio = self.mass / self.parent_body.mass
        # Convert mass ratio to float for power operation, then back to Decimal
        mass_ratio_pow = Decimal(str(float(mass_ratio) ** 0.4))  # 2/5 = 0.4
        return self.distance_from_parent_km * mass_ratio_pow
    
    def __str__(self):
        parent_info = f", orbiting {self.parent_body.name}" if self.parent_body else ""
        soi_info = f", SOI: {self.sphere_of_influence:.0f} km" if self.sphere_of_influence else ""
        return f"{self.name} ({self.mass:.2e} kg, {self.radius} km{parent_info}{soi_info})"
    
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
    table.add_column("SOI (km)", justify="right", style="magenta")
    
    # Create bodies
    sun = CelestialBody("Sun", Decimal('1.989e30'), Decimal('696340.0'), (255, 255, 0))
    
    # Mercury and Venus have no moons
    mercury = CelestialBody("Mercury", Decimal('3.285e23'), Decimal('2439.7'), (169, 169, 169), sun, Decimal('57.9e6'))
    mercury._orbit_angle = Decimal('4.16')  # ~238 degrees
    
    venus = CelestialBody("Venus", Decimal('4.867e24'), Decimal('6051.8'), (255, 198, 73), sun, Decimal('108.2e6'))
    venus._orbit_angle = Decimal('5.67')  # ~325 degrees
    
    # Earth and Moon
    earth = CelestialBody("Earth", Decimal('5.972e24'), Decimal('6371.0'), (0, 0, 255), sun, Decimal('149.6e6'))
    earth._orbit_angle = Decimal('1.57')  # ~90 degrees
    
    moon = CelestialBody("Moon", Decimal('7.348e22'), Decimal('1737.4'), (128, 128, 128), earth, Decimal('384400'))
    moon._orbit_angle = Decimal('2.09')  # ~120 degrees relative to Earth
    
    # Mars and its moons
    mars = CelestialBody("Mars", Decimal('6.39e23'), Decimal('3389.5'), (255, 0, 0), sun, Decimal('227.9e6'))
    mars._orbit_angle = Decimal('3.49')  # ~200 degrees
    
    phobos = CelestialBody("Phobos", Decimal('1.06e16'), Decimal('11.267'), (169, 169, 169), mars, Decimal('9377'))
    phobos._orbit_angle = Decimal('1.05')  # ~60 degrees relative to Mars
    
    deimos = CelestialBody("Deimos", Decimal('1.48e15'), Decimal('6.2'), (169, 169, 169), mars, Decimal('23460'))
    deimos._orbit_angle = Decimal('4.19')  # ~240 degrees relative to Mars
    
    # Asteroid Belt Objects
    ceres = CelestialBody("Ceres", Decimal('9.393e20'), Decimal('469.7'), (190, 190, 190), sun, Decimal('413.7e6'))
    ceres._orbit_angle = Decimal('2.1')
    
    vesta = CelestialBody("Vesta", Decimal('2.59e20'), Decimal('262.7'), (180, 180, 170), sun, Decimal('353.3e6'))
    vesta._orbit_angle = Decimal('3.3')
    
    pallas = CelestialBody("Pallas", Decimal('2.11e20'), Decimal('256'), (180, 180, 170), sun, Decimal('414.7e6'))
    pallas._orbit_angle = Decimal('4.5')
    
    hygiea = CelestialBody("Hygiea", Decimal('8.32e19'), Decimal('217'), (170, 170, 170), sun, Decimal('470.3e6'))
    hygiea._orbit_angle = Decimal('5.7')
    
    # Jupiter and its major moons
    jupiter = CelestialBody("Jupiter", Decimal('1.898e27'), Decimal('69911.0'), (255, 165, 0), sun, Decimal('778.5e6'))
    jupiter._orbit_angle = Decimal('2.79')  # ~160 degrees
    
    io = CelestialBody("Io", Decimal('8.932e22'), Decimal('1821.6'), (255, 255, 150), jupiter, Decimal('421700'))
    io._orbit_angle = Decimal('0.52')  # ~30 degrees relative to Jupiter
    
    europa = CelestialBody("Europa", Decimal('4.800e22'), Decimal('1560.8'), (255, 220, 200), jupiter, Decimal('671100'))
    europa._orbit_angle = Decimal('2.09')  # ~120 degrees relative to Jupiter
    
    ganymede = CelestialBody("Ganymede", Decimal('1.482e23'), Decimal('2634.1'), (169, 169, 169), jupiter, Decimal('1070400'))
    ganymede._orbit_angle = Decimal('3.66')  # ~210 degrees relative to Jupiter
    
    callisto = CelestialBody("Callisto", Decimal('1.076e23'), Decimal('2410.3'), (128, 128, 128), jupiter, Decimal('1882700'))
    callisto._orbit_angle = Decimal('5.24')  # ~300 degrees relative to Jupiter
    
    amalthea = CelestialBody("Amalthea", Decimal('2.08e18'), Decimal('83.5'), (255, 100, 100), jupiter, Decimal('181366'))
    amalthea._orbit_angle = Decimal('1.3')
    
    thebe = CelestialBody("Thebe", Decimal('4.3e17'), Decimal('49.3'), (200, 150, 150), jupiter, Decimal('221889'))
    thebe._orbit_angle = Decimal('2.8')
    
    # Saturn and its major moons
    saturn = CelestialBody("Saturn", Decimal('5.683e26'), Decimal('58232.0'), (238, 232, 205), sun, Decimal('1.434e9'))
    saturn._orbit_angle = Decimal('4.54')  # ~260 degrees
    
    titan = CelestialBody("Titan", Decimal('1.345e23'), Decimal('2574.73'), (255, 200, 100), saturn, Decimal('1221870'))
    titan._orbit_angle = Decimal('1.57')  # ~90 degrees relative to Saturn
    
    rhea = CelestialBody("Rhea", Decimal('2.307e21'), Decimal('763.8'), (200, 200, 200), saturn, Decimal('527108'))
    rhea._orbit_angle = Decimal('3.14')  # ~180 degrees relative to Saturn
    
    iapetus = CelestialBody("Iapetus", Decimal('1.806e21'), Decimal('734.5'), (200, 200, 200), saturn, Decimal('3560820'))
    iapetus._orbit_angle = Decimal('4.71')  # ~270 degrees relative to Saturn
    
    enceladus = CelestialBody("Enceladus", Decimal('1.080e20'), Decimal('252.1'), (255, 255, 255), saturn, Decimal('237948'))
    enceladus._orbit_angle = Decimal('0.79')  # ~45 degrees relative to Saturn
    
    mimas = CelestialBody("Mimas", Decimal('3.7e19'), Decimal('198.2'), (200, 200, 200), saturn, Decimal('185539'))
    mimas._orbit_angle = Decimal('2.4')
    
    tethys = CelestialBody("Tethys", Decimal('6.17e20'), Decimal('531.1'), (200, 200, 200), saturn, Decimal('294619'))
    tethys._orbit_angle = Decimal('3.9')
    
    dione = CelestialBody("Dione", Decimal('1.095e21'), Decimal('561.4'), (200, 200, 200), saturn, Decimal('377396'))
    dione._orbit_angle = Decimal('5.2')
    
    # Uranus and its major moons
    uranus = CelestialBody("Uranus", Decimal('8.681e25'), Decimal('25362.0'), (173, 216, 230), sun, Decimal('2.871e9'))
    uranus._orbit_angle = Decimal('5.93')  # ~340 degrees
    
    titania = CelestialBody("Titania", Decimal('3.527e21'), Decimal('788.9'), (169, 169, 169), uranus, Decimal('435910'))
    titania._orbit_angle = Decimal('2.36')  # ~135 degrees relative to Uranus
    
    oberon = CelestialBody("Oberon", Decimal('3.014e21'), Decimal('761.4'), (169, 169, 169), uranus, Decimal('583520'))
    oberon._orbit_angle = Decimal('3.93')  # ~225 degrees relative to Uranus
    
    miranda = CelestialBody("Miranda", Decimal('6.59e19'), Decimal('235.8'), (169, 169, 169), uranus, Decimal('129390'))
    miranda._orbit_angle = Decimal('5.50')  # ~315 degrees relative to Uranus
    
    ariel = CelestialBody("Ariel", Decimal('1.251e21'), Decimal('578.9'), (169, 169, 169), uranus, Decimal('190900'))
    ariel._orbit_angle = Decimal('1.8')
    
    umbriel = CelestialBody("Umbriel", Decimal('1.275e21'), Decimal('584.7'), (169, 169, 169), uranus, Decimal('266000'))
    umbriel._orbit_angle = Decimal('4.1')
    
    # Neptune and its major moons
    neptune = CelestialBody("Neptune", Decimal('1.024e26'), Decimal('24622.0'), (0, 0, 139), sun, Decimal('4.495e9'))
    neptune._orbit_angle = Decimal('1.05')  # ~60 degrees
    
    triton = CelestialBody("Triton", Decimal('2.139e22'), Decimal('1353.4'), (200, 200, 200), neptune, Decimal('354759'))
    triton._orbit_angle = Decimal('1.83')  # ~105 degrees relative to Neptune
    
    naiad = CelestialBody("Naiad", Decimal('1.9e17'), Decimal('33.0'), (169, 169, 169), neptune, Decimal('48227'))
    naiad._orbit_angle = Decimal('4.45')  # ~255 degrees relative to Neptune
    
    nereid = CelestialBody("Nereid", Decimal('2.7e19'), Decimal('170'), (169, 169, 169), neptune, Decimal('5513400'))
    nereid._orbit_angle = Decimal('2.7')
    
    # Dwarf Planets and Kuiper Belt Objects
    pluto = CelestialBody("Pluto", Decimal('1.303e22'), Decimal('1188.3'), (230, 230, 230), sun, Decimal('5.9e9'))
    pluto._orbit_angle = Decimal('2.3')
    
    charon = CelestialBody("Charon", Decimal('1.586e21'), Decimal('606'), (200, 200, 200), pluto, Decimal('19571'))
    charon._orbit_angle = Decimal('1.1')
    
    haumea = CelestialBody("Haumea", Decimal('4.006e21'), Decimal('816'), (230, 230, 230), sun, Decimal('6.452e9'))
    haumea._orbit_angle = Decimal('3.7')
    
    makemake = CelestialBody("Makemake", Decimal('3.1e21'), Decimal('715'), (230, 230, 230), sun, Decimal('6.850e9'))
    makemake._orbit_angle = Decimal('4.9')
    
    eris = CelestialBody("Eris", Decimal('1.67e22'), Decimal('1163'), (230, 230, 230), sun, Decimal('10.125e9'))
    eris._orbit_angle = Decimal('5.5')
    
    bodies = [
        sun,
        mercury, venus,
        earth, moon,
        mars, phobos, deimos,
        ceres, vesta, pallas, hygiea,
        jupiter, io, europa, ganymede, callisto, amalthea, thebe,
        saturn, titan, rhea, iapetus, enceladus, mimas, tethys, dione,
        uranus, titania, oberon, miranda, ariel, umbriel,
        neptune, triton, naiad, nereid,
        pluto, charon, haumea, makemake, eris
    ]
    
    for body in bodies:
        table.add_row(
            body.name,
            f"{body.mass:.2e}",
            f"{body.radius:,.0f}",
            f"{body.surface_gravity:.1f}",
            f"{body.escape_velocity/Decimal('1000'):.1f}",  # Convert to km/s
            f"{body.orbital_velocity(Decimal('200'))/Decimal('1000'):.1f}",  # Convert to km/s
            body.parent_body.name if body.parent_body else "-",
            f"{body.distance_from_parent_km:,.0f}" if body.parent_body else "-",
            f"{body.sphere_of_influence:,.0f}" if body.sphere_of_influence else "-"
        )
    
    console.print(table)
    return bodies
    
    
if __name__ == "__main__":
    main()
