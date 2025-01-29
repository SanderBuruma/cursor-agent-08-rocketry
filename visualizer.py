import pygame
import sys
from decimal import Decimal
from main import CelestialBody, main, PI
import math

from rocket import Rocket

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (1200, 800)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT_SIZE = 16
ROCKET_COLOR = (255, 100, 100)
ROCKET_SIZE = 10  # Base size in pixels

class Visualizer:
    def __init__(self, bodies):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Solar System Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        
        self.bodies = bodies
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_level = 0  # Base zoom level
        self.zoom = Decimal('2e-10') * Decimal('1.2') ** self.zoom_level  # Initial zoom
        self.dragging = False
        self.last_mouse_pos = None
        self.hovered_body = None
        
        # Time control
        self.time_scale = Decimal('1')  # 1 second real time = 1 second simulation time
        self.paused = False
        
        # Create rocket in circular orbit around Earth
        earth = next(b for b in bodies if b.name == "Earth")
        self.rocket = Rocket.in_circular_orbit(
            parent_body=earth,
            altitude_km=Decimal('1000'),  # 1000km orbit
            dry_mass=1000,  # 1000 kg dry mass
            fuel_mass=9000,  # 9000 kg fuel mass
            thrust=150000,   # 150 kN thrust
            fuel_consumption=40,  # 40 kg/s fuel consumption
        )
        self.track_rocket = False
        self.rotation_speed = Decimal('0.5')  # Radians per key press
    
    def world_to_screen(self, x: Decimal, y: Decimal) -> tuple[int, int]:
        """Convert world coordinates (meters) to screen coordinates (pixels)"""
        screen_x = int(float(x * self.zoom)) + WINDOW_SIZE[0]//2 + self.camera_x
        screen_y = int(float(y * self.zoom)) + WINDOW_SIZE[1]//2 + self.camera_y
        return (screen_x, screen_y)
        
    def screen_to_world(self, screen_x: int, screen_y: int) -> tuple[Decimal, Decimal]:
        """Convert screen coordinates (pixels) to world coordinates (meters)"""
        world_x = (Decimal(str(screen_x - WINDOW_SIZE[0]//2 - self.camera_x)) / self.zoom)
        world_y = (Decimal(str(screen_y - WINDOW_SIZE[1]//2 - self.camera_y)) / self.zoom)
        return (world_x, world_y)
    
    def get_absolute_position(self, body: CelestialBody) -> tuple[Decimal, Decimal]:
        """Get position relative to the sun (0,0) by accumulating parent positions"""
        x, y = body.get_position()
        current = body.parent_body
        while current:
            parent_x, parent_y = current.get_position()
            x += parent_x
            y += parent_y
            current = current.parent_body
        return (x, y)
    
    def get_rocket_absolute_position(self) -> tuple[Decimal, Decimal]:
        """Get rocket position relative to the sun (0,0) by accumulating parent positions"""
        rx, ry = self.rocket.x, self.rocket.y  # Get position relative to parent
        current = self.rocket.parent_body
        while current:
            parent_x, parent_y = current.get_position()
            rx += parent_x
            ry += parent_y
            current = current.parent_body
        return (rx, ry)
    
    def draw_controls(self):
        """Draw control instructions"""
        controls = [
            "Controls:",
            "Mouse Wheel: Zoom in/out",
            "Left Click + Drag: Pan view",
            "Hover: Show body info",
            "Space: Pause/Resume",
            "+ / -: Speed up/slow down time (10x)",
            "W: Thrust on",
            "S: Thrust off",
            "A/D: Rotate rocket",
            "1: Toggle rocket tracking",
            f"Time scale: {float(self.time_scale):.1e}x",
            f"Thrust: {float(self.rocket.thrust_fraction*100):.0f}%",
            f"Speed: {float(self.rocket.speed/Decimal('1000')):.1f} km/s",
            f"Orbital speed needed: {float(self.rocket.orbital_speed/Decimal('1000')):.1f} km/s",
            f"Altitude: {float(self.rocket.distance_from_parent_km - self.rocket.parent_body.radius):.1f} km",
            f"Rotation: {float(self.rocket.rotation * Decimal('180') / PI):.0f}°",
            "ESC: Quit"
        ]
        y = 10
        for line in controls:
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (10, y))
            y += FONT_SIZE + 2
    
    def draw_body(self, body: CelestialBody):
        """Draw a celestial body and its orbit"""
        # Get absolute position
        x, y = self.get_absolute_position(body)
        screen_x, screen_y = self.world_to_screen(x, y)
        
        # Calculate radius in pixels (minimum 2 pixels, no maximum)
        radius_m = body.radius * Decimal('1000')
        radius_px = max(2, int(float(radius_m * self.zoom)))
        
        # Draw orbit circle/arc if body has a parent
        if body.parent_body:
            parent_x, parent_y = self.get_absolute_position(body.parent_body)
            parent_screen_x, parent_screen_y = self.world_to_screen(parent_x, parent_y)
            orbit_radius = int(float(body.distance_from_parent_km * 1000 * self.zoom))
            
            # Only draw orbit if parent is near screen and orbit is visible
            if (0 < orbit_radius and
                -orbit_radius <= parent_screen_x <= WINDOW_SIZE[0] + orbit_radius and
                -orbit_radius <= parent_screen_y <= WINDOW_SIZE[1] + orbit_radius):
                
                if orbit_radius < 20000:
                    # Draw full circle for smaller orbits
                    pygame.draw.circle(self.screen, (50, 50, 50), 
                                     (parent_screen_x, parent_screen_y), 
                                     orbit_radius, 1)
                else:
                    # For large orbits, draw a line segment tangent to the orbit
                    # Calculate angle to current position relative to parent
                    dx = screen_x - parent_screen_x
                    dy = screen_y - parent_screen_y
                    current_angle = math.atan2(dy, dx)
                    
                    # Calculate points for line segment perpendicular to radius
                    # Use a fixed length of 1200 pixels for the line
                    line_length = 1200
                    tangent_angle = current_angle + math.pi/2  # 90 degrees offset for tangent
                    start_x = screen_x - math.cos(tangent_angle) * line_length/2
                    start_y = screen_y - math.sin(tangent_angle) * line_length/2
                    end_x = screen_x + math.cos(tangent_angle) * line_length/2
                    end_y = screen_y + math.sin(tangent_angle) * line_length/2
                    
                    pygame.draw.line(self.screen, (100, 150, 255),
                                   (int(start_x), int(start_y)),
                                   (int(end_x), int(end_y)), 1)
        
        # Draw the body if any part of it is visible on screen
        if (-radius_px <= screen_x <= WINDOW_SIZE[0] + radius_px and 
            -radius_px <= screen_y <= WINDOW_SIZE[1] + radius_px):
            pygame.draw.circle(self.screen, body.color, (screen_x, screen_y), radius_px)
            
            # Draw name if zoomed in enough or if body is hovered
            if radius_px > 5 or body == self.hovered_body:
                name_text = self.font.render(body.name, True, WHITE)
                self.screen.blit(name_text, (screen_x + radius_px + 5, screen_y - 8))
            
            # Draw info box if body is hovered
            if body == self.hovered_body:
                info = [
                    f"Mass: {body.mass:.2e} kg",
                    f"Radius: {body.radius:.1f} km",
                    f"Surface Gravity: {body.surface_gravity:.1f} m/s²",
                    f"Escape Velocity: {body.escape_velocity/Decimal('1000'):.1f} km/s"
                ]
                if body.parent_body:
                    info.append(f"Distance from {body.parent_body.name}: {body.distance_from_parent_km:,.0f} km")
                    info.append(f"Orbital Velocity: {body.current_orbital_velocity/Decimal('1000'):.1f} km/s")
                
                y_offset = screen_y + radius_px + 5
                for line in info:
                    text = self.font.render(line, True, WHITE)
                    self.screen.blit(text, (screen_x + radius_px + 5, y_offset))
                    y_offset += FONT_SIZE + 2
    
    def find_hovered_body(self, mouse_pos):
        """Find body that the mouse is hovering over.
        Shows info if mouse is within 5 pixels of center or within the body's radius."""
        mouse_x, mouse_y = mouse_pos
        closest_body = None
        closest_distance_px = float('inf')
        
        for body in self.bodies:
            # Get screen position of body
            body_x, body_y = self.get_absolute_position(body)
            screen_x, screen_y = self.world_to_screen(body_x, body_y)
            
            # Calculate radius in pixels
            radius_m = body.radius * Decimal('1000')
            radius_px = max(2, int(float(radius_m * self.zoom)))
            
            # Calculate distance in pixels
            dx = screen_x - mouse_x
            dy = screen_y - mouse_y
            distance_px = (dx * dx + dy * dy) ** 0.5
            
            # Update closest body if this one is closer
            if distance_px < closest_distance_px:
                closest_distance_px = distance_px
                closest_body = body
        
        # Return closest body if within 5 pixels of center or within body's radius
        if closest_body:
            radius_m = closest_body.radius * Decimal('1000')
            radius_px = max(2, int(float(radius_m * self.zoom)))
            return closest_body if closest_distance_px <= max(5, radius_px) else None
        return None
    
    def adjust_zoom(self, steps: int):
        """Adjust zoom by a number of steps (positive = zoom in, negative = zoom out)
        Each step is a 20% change"""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
        
        self.zoom_level += steps
        self.zoom = Decimal('2e-10') * Decimal('1.2') ** self.zoom_level
        
        # Adjust camera to keep mouse position fixed
        new_screen_x = int(float(world_x * self.zoom)) + WINDOW_SIZE[0]//2 + self.camera_x
        new_screen_y = int(float(world_y * self.zoom)) + WINDOW_SIZE[1]//2 + self.camera_y
        self.camera_x += mouse_x - new_screen_x
        self.camera_y += mouse_y - new_screen_y
    
    def update_orbits(self, dt_seconds: float):
        """Update orbital positions based on time elapsed"""
        if self.paused:
            return
            
        dt = Decimal(str(dt_seconds)) * self.time_scale
        
        for body in self.bodies:
            if body.parent_body:  # Only update bodies that orbit something
                # Calculate angular velocity (radians per second)
                mu = body.parent_body.G * body.parent_body.mass
                r = body.distance_from_parent_km * Decimal('1000')  # Convert to meters
                angular_velocity = (mu / (r * r * r)).sqrt()
                
                # Update orbit angle
                angle_change = angular_velocity * dt
                new_angle = body._orbit_angle + angle_change
                body.update_position(new_angle)
    
    def draw_rocket(self):
        """Draw the rocket as an elongated triangle pointing in its direction of motion"""
        # Get rocket absolute position in screen coordinates
        x, y = self.get_rocket_absolute_position()
        screen_x, screen_y = self.world_to_screen(x, y)
        
        # Draw orbit path if in bound orbit (not hyperbolic)
        # Calculate specific orbital energy
        v = self.rocket.speed
        r = self.rocket.distance_from_parent_km * Decimal('1000')  # Convert to meters
        mu = self.rocket.parent_body.G * self.rocket.parent_body.mass
        specific_energy = (v * v / Decimal('2')) - mu / r
        
        if specific_energy < 0:  # Negative energy means bound orbit (elliptical or circular)
            # Calculate orbital elements
            rx, ry = self.rocket.x, self.rocket.y
            vx, vy = self.rocket.dx, self.rocket.dy
            h = rx * vy - ry * vx  # Specific angular momentum
            
            # Calculate eccentricity
            ex = ((v * v - mu / r) * rx - (rx * vx + ry * vy) * vx) / mu
            ey = ((v * v - mu / r) * ry - (rx * vx + ry * vy) * vy) / mu
            e = (ex * ex + ey * ey).sqrt()
            
            # Calculate semi-major axis
            a = -mu / (Decimal('2') * specific_energy)
            
            # Draw orbit path
            if e < 1:  # Double check it's not hyperbolic
                points = []
                # Get parent body position for orbit centering
                parent_x, parent_y = self.get_absolute_position(self.rocket.parent_body)
                
                # Calculate orbit orientation angle from eccentricity vector
                orbit_angle = Decimal(str(math.atan2(float(ey), float(ex))))
                if h < 0:  # If angular momentum is negative, flip the orbit
                    orbit_angle += PI
                
                # Calculate points along the orbit
                for theta in range(0, 360, 1):  # Every 5 degrees
                    theta_rad = math.radians(theta)
                    # Convert e to float for math.cos
                    e_float = float(e)
                    # Orbit equation in polar form
                    r_factor = float(a * (1 - e * e))
                    orbit_r = r_factor / (1 + e_float * math.cos(theta_rad))
                    
                    # Convert polar to cartesian coordinates, then rotate by orbit_angle
                    base_x = orbit_r * math.cos(theta_rad)
                    base_y = orbit_r * math.sin(theta_rad)
                    
                    # Rotate point by orbit_angle
                    orbit_angle_float = float(orbit_angle)
                    rotated_x = base_x * math.cos(orbit_angle_float) - base_y * math.sin(orbit_angle_float)
                    rotated_y = base_x * math.sin(orbit_angle_float) + base_y * math.cos(orbit_angle_float)
                    
                    # Add parent body's position to center the orbit correctly
                    world_x = Decimal(str(rotated_x)) + parent_x
                    world_y = Decimal(str(rotated_y)) + parent_y
                    
                    # Convert to screen coordinates
                    screen_point = self.world_to_screen(world_x, world_y)
                    points.append(screen_point)
                
                # Draw the orbit path
                if len(points) > 2:
                    pygame.draw.lines(self.screen, (100, 150, 255), True, points, 1)
        
        # Calculate rocket orientation from rotation angle
        angle = float(self.rocket.rotation)
        
        # Calculate triangle points
        size = max(5, int(ROCKET_SIZE * self.zoom))  # Scale with zoom but maintain minimum size
        points = [
            (screen_x + size * 2 * math.cos(angle),
             screen_y + size * 2 * math.sin(angle)),  # Nose
            (screen_x + size * math.cos(angle + 2.6),
             screen_y + size * math.sin(angle + 2.6)),  # Left wing
            (screen_x + size * math.cos(angle - 2.6),
             screen_y + size * math.sin(angle - 2.6))   # Right wing
        ]
        
        # Draw rocket
        pygame.draw.polygon(self.screen, ROCKET_COLOR, points)
        
        # Draw thrust indicator if engines are firing
        if self.rocket.thrust_fraction > 0:
            thrust_points = [
                points[1],  # Left wing
                (screen_x - size * math.cos(angle),
                 screen_y - size * math.sin(angle)),  # Back
                points[2]   # Right wing
            ]
            pygame.draw.polygon(self.screen, (255, 165, 0), thrust_points)
    
    def run(self):
        """Main game loop"""
        running = True
        last_time = pygame.time.get_ticks() / 1000.0
        
        while running:
            # Handle time step
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            # Handle events
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a]:
                self.rocket.rotate(-self.rotation_speed * Decimal(str(dt)))
            if keys[pygame.K_d]:
                self.rocket.rotate(self.rotation_speed * Decimal(str(dt)))
            if keys[pygame.K_w]:
                self.rocket.set_thrust(Decimal('1'))
            if keys[pygame.K_s]:
                self.rocket.set_thrust(Decimal('0'))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.dragging = True
                        self.last_mouse_pos = event.pos
                    elif event.button == 4:  # Mouse wheel up
                        self.adjust_zoom(1)
                    elif event.button == 5:  # Mouse wheel down
                        self.adjust_zoom(-1)
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click release
                        self.dragging = False
                        
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        dx = event.pos[0] - self.last_mouse_pos[0]
                        dy = event.pos[1] - self.last_mouse_pos[1]
                        self.camera_x += dx
                        self.camera_y += dy
                        self.last_mouse_pos = event.pos
                    self.hovered_body = self.find_hovered_body(event.pos)
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_EQUALS:  # Plus key
                        self.time_scale *= Decimal('10')
                    elif event.key == pygame.K_MINUS:
                        self.time_scale /= Decimal('10')
                    elif event.key == pygame.K_1:
                        self.track_rocket = not self.track_rocket
            
            # Update
            if not self.paused:
                self.update_orbits(dt)
                self.rocket.update(Decimal(str(dt)) * self.time_scale)
                
                # Update camera if tracking rocket
                if self.track_rocket:
                    rx, ry = self.get_rocket_absolute_position()
                    screen_x, screen_y = self.world_to_screen(rx, ry)
                    self.camera_x = WINDOW_SIZE[0]//2 - screen_x
                    self.camera_y = WINDOW_SIZE[1]//2 - screen_y
            
            # Draw
            self.screen.fill(BLACK)
            for body in self.bodies:
                self.draw_body(body)
            self.draw_rocket()
            self.draw_controls()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    # Get bodies from main
    bodies = main()
    
    # Create and run visualizer
    visualizer = Visualizer(bodies)
    visualizer.run() 