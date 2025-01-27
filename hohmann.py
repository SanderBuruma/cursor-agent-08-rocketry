from decimal import Decimal, getcontext
import math
from main import main, PI

# Set precision to 50 decimal places
getcontext().prec = 50

def calculate_hohmann_phase_angle(body1, body2):
    """Calculate the phase angle needed for a Hohmann transfer between two bodies.
    Both bodies must orbit the same parent body.
    
    Returns:
        phase_angle: The angle in radians that body2 should be ahead of body1
                    when starting the transfer
    """
    if body1.parent_body != body2.parent_body:
        raise ValueError("Bodies must share the same parent body")
    
    # Get orbital radii in meters
    r1 = body1.distance_from_parent_km * Decimal('1000')
    r2 = body2.distance_from_parent_km * Decimal('1000')
    
    # Ensure r1 is the smaller orbit
    if r1 > r2:
        r1, r2 = r2, r1
    
    # Calculate transfer time (half orbit of transfer ellipse)
    mu = body1.parent_body.G * body1.parent_body.mass  # gravitational parameter
    a = (r1 + r2) / Decimal('2')  # semi-major axis of transfer orbit
    transfer_time = PI * (a * a * a / mu).sqrt()
    
    # Calculate angular velocities (radians per second)
    w1 = (mu / (r1 * r1 * r1)).sqrt()  # angular velocity of inner orbit
    w2 = (mu / (r2 * r2 * r2)).sqrt()  # angular velocity of outer orbit
    
    # Calculate phase angle
    # During transfer time, outer body moves: w2 * transfer_time radians
    # We want inner body to move exactly 180° (π radians) more than this
    phase_angle = float(PI - w2 * transfer_time)
    
    return phase_angle

def main_hohmann():
    bodies = main()
    
    # Find Phobos and Deimos
    cb1 = next(b for b in bodies if b.name == "Mars")
    cb2 = next(b for b in bodies if b.name == "Earth")
    
    # Calculate phase angle for transfer
    phase_angle = calculate_hohmann_phase_angle(cb1, cb2)
    
    # Convert to degrees for easier understanding
    phase_degrees = math.degrees(phase_angle)
    
    print(f"For a Hohmann transfer from {cb1.name} to {cb2.name}:")
    print(f"Phase angle needed: {phase_degrees:.2f}°")
    print(f"This means {cb2.name} should be {phase_degrees:.2f}° ahead of {cb1.name}")
    print(f"when starting the transfer.")

if __name__ == "__main__":
    main_hohmann()