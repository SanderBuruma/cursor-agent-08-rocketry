import pygame
import sys
from decimal import Decimal
from main import CelestialBody, main

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (1200, 800)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FONT_SIZE = 16

class Visualizer:
    def __init__(self, bodies):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Solar System Visualizer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        
        self.bodies = bodies
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = Decimal('2e-10')  # Initial zoom to see most of inner solar system
        self.dragging = False
        self.last_mouse_pos = None
        self.hovered_body = None
        
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
    
    def draw_controls(self):
        """Draw control instructions"""
        controls = [
            "Controls:",
            "Mouse Wheel: Zoom in/out",
            "Left Click + Drag: Pan view",
            "Hover: Show body info",
            "ESC: Quit"
        ]
        y = 10
        for line in controls:
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (10, y))
            y += FONT_SIZE + 2
    
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
    
    def draw_body(self, body: CelestialBody):
        """Draw a celestial body and its orbit"""
        # Get absolute position
        x, y = self.get_absolute_position(body)
        screen_x, screen_y = self.world_to_screen(x, y)
        
        # Calculate radius in pixels (minimum 2 pixels, maximum 50)
        radius_m = body.radius * Decimal('1000')
        radius_px = max(2, min(50, int(float(radius_m * self.zoom))))
        
        # Draw orbit circle if body has a parent
        if body.parent_body:
            parent_x, parent_y = self.get_absolute_position(body.parent_body)
            parent_screen_x, parent_screen_y = self.world_to_screen(parent_x, parent_y)
            orbit_radius = int(float(body.distance_from_parent_km * 1000 * self.zoom))
            if 0 < orbit_radius < max(WINDOW_SIZE):  # Only draw if visible and not too large
                pygame.draw.circle(self.screen, (50, 50, 50), 
                                 (parent_screen_x, parent_screen_y), 
                                 orbit_radius, 1)
        
        # Draw the body if it's on screen
        if 0 <= screen_x <= WINDOW_SIZE[0] and 0 <= screen_y <= WINDOW_SIZE[1]:
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
                
                y_offset = screen_y + radius_px + 5
                for line in info:
                    text = self.font.render(line, True, WHITE)
                    self.screen.blit(text, (screen_x + radius_px + 5, y_offset))
                    y_offset += FONT_SIZE + 2
    
    def find_hovered_body(self, mouse_pos):
        """Find body under mouse cursor"""
        mouse_x, mouse_y = mouse_pos
        world_x, world_y = self.screen_to_world(mouse_x, mouse_y)
        
        for body in self.bodies:
            body_x, body_y = self.get_absolute_position(body)
            dx = body_x - world_x
            dy = body_y - world_y
            distance = (dx * dx + dy * dy).sqrt()
            
            # Check if mouse is within body's radius (with some padding)
            radius_m = body.radius * Decimal('1000')
            if distance < radius_m * Decimal('2'):
                return body
        return None
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and 
                    event.key == pygame.K_ESCAPE
                ):
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.dragging = True
                        self.last_mouse_pos = event.pos
                    elif event.button == 4:  # Mouse wheel up
                        self.zoom *= Decimal('1.1')
                    elif event.button == 5:  # Mouse wheel down
                        self.zoom *= Decimal('0.9')
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:  # Left click
                        self.dragging = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        current_pos = event.pos
                        dx = current_pos[0] - self.last_mouse_pos[0]
                        dy = current_pos[1] - self.last_mouse_pos[1]
                        self.camera_x += dx
                        self.camera_y += dy
                        self.last_mouse_pos = current_pos
                    
                    # Update hovered body
                    self.hovered_body = self.find_hovered_body(event.pos)
            
            # Clear screen
            self.screen.fill(BLACK)
            
            # Draw all bodies
            for body in self.bodies:
                self.draw_body(body)
            
            # Draw controls
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