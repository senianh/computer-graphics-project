import pygame
import sys
import random
import math

pygame.init()
WIDTH, HEIGHT = 1200, 750
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🌳 NeoTerra: A Sustainable Future City Simulation")
FONT = pygame.font.SysFont("Segoe UI Emoji", 15)
FONT_BOLD = pygame.font.SysFont("Segoe UI Emoji", 15, bold=True)
BIGFONT = pygame.font.SysFont("Segoe UI Emoji", 32, bold=True)
MEDFONT = pygame.font.SysFont("Segoe UI Emoji", 20)
CLOCK = pygame.time.Clock()
FPS = 60

class Particle:
    def __init__(self, x, y, color, vx=0, vy=0):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx + random.uniform(-0.5, 0.5)
        self.vy = vy + random.uniform(-2, -0.5)
        self.life = 30
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.life -= 1
        
    def draw(self, surf):
        alpha = int(255 * (self.life / 30))
        if alpha > 0:
            s = pygame.Surface((self.size*2, self.size*2))
            s.set_alpha(alpha)
            s.fill(self.color)
            surf.blit(s, (int(self.x), int(self.y)))

class Cloud:
    def __init__(self):
        self.x = random.randint(-100, WIDTH)
        self.y = 140 
        self.speed = random.uniform(0.2, 0.5)
        self.size = random.randint(50, 100)
        
    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 100:
            self.x = -100
            self.y = random.randint(30, 100)
    
    def draw(self, surf):
        color = (255, 255, 255, 180)
        pygame.draw.ellipse(surf, color, (self.x, self.y, self.size * 2, self.size//2))
        pygame.draw.ellipse(surf, color, (self.x+30, self.y-10, self.size*1.5, self.size//2))
        pygame.draw.ellipse(surf, color, (self.x+70, self.y, self.size*1.2, self.size//2))

class Button:
    def __init__(self, rect, text, callback=None, bg=(200,200,200), fg=(0,0,0), hover_bg=(220,220,220)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.bg = bg
        self.hover_bg = hover_bg
        self.fg = fg
        self.hovered = False
        
    def draw(self, surf):
        mx, my = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mx, my)
        color = self.hover_bg if self.hovered else self.bg
        
        shadow = self.rect.copy()
        shadow.x += 3
        shadow.y += 3
        pygame.draw.rect(surf, (0,0,0,30), shadow, border_radius=8)
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, (80,80,80), self.rect, 2, border_radius=8)
        
        r = FONT_BOLD.render(self.text, True, self.fg)
        surf.blit(r, (self.rect.centerx - r.get_width()//2, self.rect.centery - r.get_height()//2))
        
    def click(self):
        if self.callback:
            self.callback()

class TrafficLight:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.pole_height = 120
        self.state = "GREEN"
        self.timer = 0
        self.durations = {"GREEN": 5*FPS, "YELLOW": 2*FPS, "RED": 5*FPS}
        self.glow = 0
    
    @property
    def depth_y(self):
        return self.y + self.pole_height
        
    def update(self):
        self.timer += 1
        self.glow = (self.glow + 3) % 360
        if self.timer > self.durations[self.state]:
            self.timer = 0
            if self.state == "GREEN":
                self.state = "YELLOW"
            elif self.state == "YELLOW":
                self.state = "RED"
            else:
                self.state = "GREEN"
                
    def draw(self, surf):
        base_y = self.y + self.pole_height
        pygame.draw.rect(surf, (40,40,40), (self.x-8, base_y-5, 16, 10))
        pygame.draw.rect(surf, (50,50,50), (self.x-4, self.y, 8, self.pole_height), border_radius=3)
        pygame.draw.rect(surf, (30,30,30), (self.x-4, self.y, 8, self.pole_height), 1, border_radius=3)
        
        box_width, box_height = 40, 95
        box_x = self.x - box_width//2
        box_y = self.y - box_height
        
        pygame.draw.rect(surf, (0,0,0,60), (box_x+3, box_y+3, box_width, box_height), border_radius=8)
        pygame.draw.rect(surf, (40,40,40), (box_x, box_y, box_width, box_height), border_radius=8)
        pygame.draw.rect(surf, (30,30,30), (box_x, box_y, box_width, box_height), 2, border_radius=8)
        
        colors = {
            "RED": ((220,30,30), (100,0,0)),
            "YELLOW": ((255,200,30), (120,90,0)),
            "GREEN": ((30,220,60), (0,80,20))
        }
        
        for i, state in enumerate(["RED", "YELLOW", "GREEN"]):
            y_pos = box_y + 20 + i*25
            active = self.state == state
            color = colors[state][0] if active else colors[state][1]
            
            if active:
                glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                glow_alpha = int(100 + 50 * math.sin(math.radians(self.glow)))
                pygame.draw.circle(glow_surf, (*color, glow_alpha), (15, 15), 12)
                surf.blit(glow_surf, (self.x - glow_surf.get_width()//2, y_pos - glow_surf.get_height()//2))
            
            pygame.draw.circle(surf, color, (self.x, y_pos), 10)
            pygame.draw.circle(surf, (200,200,200), (self.x, y_pos), 10, 1)

class Vehicle:
    def __init__(self, kind="car", x=0, y=0, speed=2, scale=1.3, enable_exhaust=True):
        self.kind = kind
        self.x = x
        self.y = y
        self.speed = speed
        self.scale = scale
        self.enable_exhaust = enable_exhaust
        
        base_width = 30 if kind=="car" else 68 if kind=="bus" else 18
        base_height = 18 if kind!="bus" else 28
        self.width = int(base_width * scale)
        self.height = int(base_height * scale)

        if kind == "car":
            self.color = random.choice([(220,50,50), (50,120,220), (220,180,50), (50,200,80)])
        elif kind == "bus":
            self.color = (30,130,230)
        else:
            self.color = (40,180,40)

        self.passengers = random.randint(1,4) if kind=="bus" else 1
        self.exhaust_timer = 0
        self.exhaust_particles = []

    def update(self, traffic_light=None, vehicles=None):
        if traffic_light and traffic_light.state == "RED":
            if self.x < traffic_light.x and traffic_light.x - self.x < 140:
                return

        if vehicles and not self.can_move(vehicles):
            return

        self.x += self.speed

        if self.enable_exhaust and self.kind == "car":
            self.exhaust_timer += 1
            if self.exhaust_timer > 10:
                self.exhaust_timer = 0
                p = Particle(self.x - 5, self.y + 5, (80,80,80), vx=-0.5, vy=0)
                self.exhaust_particles.append(p)

        for p in self.exhaust_particles:
            p.update()
        self.exhaust_particles = [p for p in self.exhaust_particles if p.life > 0]

    def can_move(self, vehicles):
        SAFE_DISTANCE = self.width * 1.6
        for other in vehicles:
            if other is self:
                continue
            if other.y == self.y:
                if 0 < other.x - self.x < SAFE_DISTANCE:
                    return False
        return True

    def draw(self, surf):
        for p in self.exhaust_particles:
            p.draw(surf)

        shadow = pygame.Rect(self.x+2*self.scale, self.y - self.height//2 + 2*self.scale, self.width, self.height)
        pygame.draw.rect(surf, (0,0,0,60), shadow, border_radius=5)

        if self.kind == "bus":
            r = pygame.Rect(self.x, self.y - self.height//2, self.width, self.height)
            pygame.draw.rect(surf, self.color, r, border_radius=6)
            pygame.draw.rect(surf, (0,0,0), r, max(1,int(2*self.scale)), border_radius=6)
            
            window_width = int(12 * self.scale)
            window_height = int(8 * self.scale)
            for i in range(4):
                wx = self.x + int(8*self.scale) + i * (window_width + int(3*self.scale))
                pygame.draw.rect(surf, (185,230,255),
                    (wx, self.y - self.height//2 + int(6 * self.scale), window_width, window_height),
                    border_radius=3)
        else:
            body_y = self.y - int(self.height * 0.25)
            wheel_radius = int(self.width * 0.12)

            pygame.draw.ellipse(surf, self.color, (self.x, body_y, self.width, int(self.height * 0.6)))
            
            roof_width = int(self.width * 0.7)
            roof_height = int(self.height * 0.65)
            pygame.draw.arc(surf, self.color,
                (self.x + int(self.width * 0.10), body_y - int(roof_height * 0.55),
                 int(roof_width * 1.15), int(roof_height * 1.45)),
                math.radians(0), math.radians(180), 4)

            window_x = self.x + int(self.width * 0.18)
            window_y = body_y - int(roof_height * 0.38)
            window_w = int(roof_width * 0.75)
            window_h = int(roof_height * 0.85)
            pygame.draw.arc(surf, (185,230,255), (window_x, window_y, window_w, window_h),
                math.radians(0), math.radians(180), 4)

            pygame.draw.line(surf, self.color,
                (self.x + int(self.width * 0.47), self.y - int(self.height * 0.45)),
                (self.x + int(self.width * 0.47), self.y - int(self.height * 0.20)), 4)

            left_wheel_x = self.x + int(self.width * 0.18)
            right_wheel_x = self.x + int(self.width * 0.72)
            wheel_y = self.y + int(self.height * 0.15)
            for wx in [left_wheel_x, right_wheel_x]:
                pygame.draw.circle(surf, (25,25,25), (wx, wheel_y), wheel_radius)
                pygame.draw.circle(surf, (140,140,140), (wx, wheel_y), wheel_radius - 4)
                    
        wheel_radius = int(6 * self.scale)
        wheel_y = self.y + self.height//2 - int(wheel_radius * 0.5)

        if self.kind == "bus":
            left_wheel_x = self.x + int(15 * self.scale)
            right_wheel_x = self.x + self.width - int(15 * self.scale)
        else:
            left_wheel_x = self.x + int(7 * self.scale)
            right_wheel_x = self.x + self.width - int(7 * self.scale)

        for wx in [left_wheel_x, right_wheel_x]:
            pygame.draw.circle(surf, (30, 30, 30), (wx, wheel_y), wheel_radius)
            pygame.draw.circle(surf, (120,120,120), (wx, wheel_y), wheel_radius - 2)

        pygame.draw.circle(surf, (255,255,200), 
            (self.x + self.width - int(4 * self.scale), self.y - int(6 * self.scale)),
            int(3 * self.scale))

class Tree:
    def __init__(self, x, ground_y, stage=0):
        self.x = x
        self.ground_y = ground_y
        self.stage = stage
        self.watered = False
        self.growth_timer = 0
        self.sway = random.randint(0, 360)
        self.sparkles = []
        self.reward_given = False
        self.y = self.ground_y
        self.has_fruit = False
        self.fruit_respawn_timer = 0

    def water(self):
        self.watered = True
        for _ in range(10):
            p = Particle(self.x, self.ground_y-5, (100,150,255), 
                        vx=random.uniform(-2,2), vy=random.uniform(-3,-1))
            self.sparkles.append(p)

    def update(self):
        self.sway = (self.sway + 1) % 360
        
        if self.watered:
            self.growth_timer += 1
            if random.random() < 0.1:
                p = Particle(self.x + random.randint(-10,10), 
                        self.ground_y - 20 - self.stage*5,
                        (100,255,100), vx=0, vy=-1)
                self.sparkles.append(p)
                
            if self.growth_timer > 3*FPS:
                self.stage = min(3, self.stage + 1)
                self.growth_timer = 0
                self.watered = False
                self.reward_given = True  

                for _ in range(20):
                    p = Particle(self.x, self.ground_y - 20,
                            (50,255,50), vx=random.uniform(-3,3), vy=random.uniform(-5,-2))
                    self.sparkles.append(p)

        for p in self.sparkles:
            p.update()
        self.sparkles = [p for p in self.sparkles if p.life > 0]

        if self.stage == 3 and not self.has_fruit:
            self.fruit_respawn_timer += 1
            if self.fruit_respawn_timer > FPS * 5:
                self.fruit_respawn_timer = 0
                self.grow_fruit()

    def grow_fruit(self):
        self.has_fruit = True
        self.fruit_positions = []
        leaf_radius = 20 + self.stage * 20
        trunk_h = 20 + self.stage * 35
        foliage_y = self.ground_y - trunk_h - leaf_radius//2
        fruit_count = random.randint(3, 6)

        for _ in range(fruit_count):
            radius = random.randint(int(leaf_radius * 0.3), int(leaf_radius * 0.8))
            angle = random.uniform(0.5, 2.5)
            fx = self.x + math.cos(angle) * radius
            fy = foliage_y + math.sin(angle) * radius + random.randint(5, 15)
            self.fruit_positions.append((fx, fy))

    def draw(self, surf):
        for p in self.sparkles:
            p.draw(surf)
            
        y = self.ground_y
        
        if self.stage == 0:
            pygame.draw.circle(surf, (139,69,19), (int(self.x), y-3), 4)
            pygame.draw.circle(surf, (100,50,10), (int(self.x), y-3), 4, 1)
        else:
            trunk_h = 20 + self.stage*35
            sway_offset = math.sin(math.radians(self.sway)) * (self.stage * 0.5)
            trunk_width = 10 + self.stage * 8

            trunk_rect = pygame.Rect(self.x - trunk_width // 2, y - trunk_h, trunk_width, trunk_h)
            pygame.draw.rect(surf, (120,80,50), trunk_rect, border_radius=4)
            pygame.draw.rect(surf, (90,60,30), trunk_rect, 2, border_radius=4)

            for i in range(0, trunk_h, 8):
                pygame.draw.line(surf, (100,70,40), (self.x-4, y-trunk_h+i), (self.x+4, y-trunk_h+i), 1)
            
            leaf_radius = 20 + self.stage*20
            foliage_y = y - trunk_h - leaf_radius//2
            
            pygame.draw.circle(surf, (20,100,20), (int(self.x + sway_offset), foliage_y), leaf_radius)
            pygame.draw.circle(surf, (40,160,40), (int(self.x + sway_offset), foliage_y-3), leaf_radius-2)
            pygame.draw.circle(surf, (60,200,60), (int(self.x + sway_offset-3), foliage_y-5), leaf_radius//2)
            
            if self.stage >= 2:
                pygame.draw.circle(surf, (30,140,30), 
                    (int(self.x-leaf_radius//2 + sway_offset), foliage_y+5), leaf_radius//2)
                pygame.draw.circle(surf, (30,140,30), 
                    (int(self.x+leaf_radius//2 + sway_offset), foliage_y+5), leaf_radius//2)
                    
            if self.has_fruit:
                for i, (fx, fy) in enumerate(self.fruit_positions):
                    sway_offset = math.sin(math.radians(self.sway + i*30)) * 3
                    draw_x = fx + sway_offset
                    draw_y = fy + sway_offset/2
                    pygame.draw.circle(surf, (255, 60, 60), (int(draw_x), int(draw_y)), 10)
                    pygame.draw.circle(surf, (200, 30, 30), (int(draw_x), int(draw_y)), 10, 2)

class RewardEffect:
    def __init__(self, x, y, kind="star"):
        self.x = x
        self.y = y
        self.kind = kind
        self.life = 100
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-2, -0.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surf):
        if self.kind == "star":
            pygame.draw.circle(surf, (255,255,80), (int(self.x), int(self.y)), 6)
        elif self.kind == "butterfly":
            pygame.draw.circle(surf, (255,120,200), (int(self.x)-6, int(self.y)), 6)
            pygame.draw.circle(surf, (255,80,160), (int(self.x)+6, int(self.y)), 6)
        elif self.kind == "rainbow":
            pygame.draw.arc(surf, (255,100,100), (self.x-30, self.y-40, 60, 40), 0, 3.14)

class Building:
    def __init__(self, x, y, w, h, color):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.color = color
        self.window_lights = [[random.random() > 0.3 for _ in range(w//25)] 
                             for _ in range(h//30)]
        
    def draw(self, surf):
        shadow_surf = pygame.Surface((self.w+10, self.h+10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0,0,0,40), (0, 0, self.w+10, self.h+10))
        surf.blit(shadow_surf, (self.x+8, self.y+8))
        
        side_color = tuple(max(0, c-40) for c in self.color)
        side_points = [(self.x + self.w, self.y), (self.x + self.w + 15, self.y + 15),
                      (self.x + self.w + 15, self.y + self.h + 15), (self.x + self.w, self.y + self.h)]
        pygame.draw.polygon(surf, side_color, side_points)
        
        top_color = tuple(min(255, c+20) for c in self.color)
        top_points = [(self.x, self.y), (self.x + 15, self.y - 10),
                     (self.x + self.w + 15, self.y - 10), (self.x + self.w, self.y)]
        pygame.draw.polygon(surf, top_color, top_points)
        
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surf, (0,0,0), (self.x, self.y, self.w, self.h), 2)
        
        WINDOW_W, WINDOW_H = 18, 20
        SPACING_X, SPACING_Y = 25, 30
        MARGIN_X, MARGIN_Y = 10, 15

        for row, lights_row in enumerate(self.window_lights):
            for col, is_lit in enumerate(lights_row):
                wx = self.x + MARGIN_X + col * SPACING_X
                wy = self.y + MARGIN_Y + row * SPACING_Y

                if wx + WINDOW_W > self.x + self.w - MARGIN_X: 
                    break  
                if wy + WINDOW_H > self.y + self.h - MARGIN_Y: 
                    continue

                pygame.draw.rect(surf, (40,40,50), (wx-1, wy-1, WINDOW_W+2, WINDOW_H+2), border_radius=2)
                color = (255,250,200) if is_lit else (50,50,70)
                pygame.draw.rect(surf, color, (wx, wy, WINDOW_W, WINDOW_H), border_radius=2)

                if is_lit:
                    glow = pygame.Surface((SPACING_X, SPACING_Y), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (255,250,200,80), (3, 3, WINDOW_W, WINDOW_H), border_radius=2)
                    surf.blit(glow, (wx-3, wy-3))
                    pygame.draw.rect(surf, (200,190,140), (wx, wy, WINDOW_W, 6))

class SmartCitySim:
    def __init__(self):
        self.vehicles = []
        self.trees = []
        self.traffic_light = TrafficLight(950, 300)
        self.shadow_buildings = [] 
        self.buildings = []
        self.clouds = [Cloud() for _ in range(10)]
        self.road_y = 340
        self.spawn_timer = 0
        self.max_congestion = 18
        self.spawn_auto = True
        self.time_of_day = 0
        
        for i in range(20):
            w = random.randint(110, 160)
            h = random.randint(100, 200)
            x = 20 + i * random.randint(50, 80)
            y = self.road_y - h - random.randint(10, 30)
            self.shadow_buildings.append((x, y, w, h))
            
        for i in range(10):
            w = random.randint(90, 140)
            h = random.randint(120, 220)
            x = 20 + i*190
            y = self.road_y - h - 80
            color = random.choice([(120,130,140), (100,110,130), (140,120,110)])
            self.buildings.append(Building(x, y, w, h, color))

    def add_vehicle(self, kind="car"):
        y = self.road_y + random.choice([-15, 15])
        speed = random.uniform(1.5, 3.0) if kind=="car" else random.uniform(1.2, 2.0)
        self.vehicles.append(Vehicle(kind=kind, x=-100, y=y, speed=speed))

    def remove_vehicle(self, kind=None):
        for i in range(len(self.vehicles)-1,-1,-1):
            if kind is None or self.vehicles[i].kind==kind:
                self.vehicles.pop(i)
                return

    def add_tree(self):
        x = random.randint(50, WIDTH - 50)
        self.trees.append(Tree(x, self.road_y - 60, stage=random.choice([1,2])))

    def remove_tree(self):
        if self.trees:
            self.trees.pop()

    def update(self):
        self.time_of_day = (self.time_of_day + 0.2) % 360
        self.traffic_light.update()
        
        for cloud in self.clouds:
            cloud.update()
        
        if self.spawn_auto:
            self.spawn_timer += 1
            if self.spawn_timer > 50:
                self.spawn_timer = 0
                self.add_vehicle("car" if random.random() < 0.5 else "bus")
        
        for v in self.vehicles:
            v.update(self.traffic_light, self.vehicles)
        
        self.vehicles = [v for v in self.vehicles if -200 < v.x < WIDTH + 200 and v.kind != "bike"]

        for t in self.trees:
            t.update()

    def draw(self, surf):
        sky_color = int(180 + 40 * math.sin(math.radians(self.time_of_day)))
        for i in range(HEIGHT//2):
            c = sky_color - i//3
            pygame.draw.line(surf, (c, c+30, 255), (0, i), (WIDTH, i))
        
        car_count = sum(1 for v in self.vehicles if v.kind=="car")
        bus_count = sum(1 for v in self.vehicles if v.kind=="bus")
        total = len(self.vehicles)
        people_count = car_count * 2 + bus_count * 15
        
        tree_power = sum(1.0 + 0.5*t.stage for t in self.trees)
        air_score = max(0.0, (1.0 - min(1.0, (total*0.08) / (1 + tree_power*0.6))))
        
        if air_score < 0.5:
            pollution_alpha = int((1.0 - air_score) * 120)
            pollution_surf = pygame.Surface((WIDTH, HEIGHT//2), pygame.SRCALPHA)
            pollution_surf.fill((100, 80, 60, pollution_alpha))
            surf.blit(pollution_surf, (0, 0))
            
            for i in range(int((1.0 - air_score) * 30)):
                x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT//2)
                size = random.randint(3, 8)
                smog = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(smog, (80, 70, 60, random.randint(30, 80)), (size, size), size)
                surf.blit(smog, (x, y))
        
        for cloud in self.clouds:
            cloud.draw(surf)
            
        for x, y, w, h in self.shadow_buildings:
            pygame.draw.rect(surf, (45,45,70), (x, y, w, h), border_radius=6)

        for b in self.buildings:
            b.draw(surf)
        
        pygame.draw.rect(surf, (70,150,70), (0, self.road_y-100, WIDTH, 100))
        
        for i in range(100):
            shade = 60 + i//5
            pygame.draw.line(surf, (shade, shade, shade), (0, self.road_y-50+i), (WIDTH, self.road_y-50+i))
        
        for i in range(0, WIDTH, 70):
            pygame.draw.rect(surf, (255,240,120), (i+15, self.road_y-5, 35, 8), border_radius=2)
        
        pygame.draw.rect(surf, (160,160,160), (0, self.road_y-60, WIDTH, 10))
        pygame.draw.rect(surf, (160,160,160), (0, self.road_y+50, WIDTH, 10))
        pygame.draw.rect(surf, (60,140,60), (0, self.road_y+60, WIDTH, HEIGHT-self.road_y-60))
        
        drawables = [(self.traffic_light.depth_y, self.traffic_light)]
        drawables.extend((t.ground_y, t) for t in self.trees)
        drawables.extend((v.y, v) for v in self.vehicles)
        drawables.sort(key=lambda x: x[0])
        
        for _, obj in drawables:
            obj.draw(surf)

        panel_height = 200
        panel = pygame.Surface((WIDTH, panel_height), pygame.SRCALPHA)
        panel.fill((20, 20, 40, 240))
        surf.blit(panel, (0, HEIGHT - panel_height))
        
        title = BIGFONT.render("🏙️ SIMULASI KOTA CERDAS", True, (255,255,100))
        surf.blit(title, (20, HEIGHT - panel_height + 15))
        
        stats = [
            (f"🚗 Mobil: {car_count}", (255,100,100), 30),
            (f"🚌 Bus: {bus_count}", (100,150,255), 170),
            (f"🌳 Pohon: {len(self.trees)}", (100,255,150), 310),
            (f"📊 Total: {total}", (255,255,255), 450),
            (f"👥 Orang: {people_count}", (255,220,120), 590)
        ]
        
        for text, color, x_pos in stats:
            surf.blit(FONT_BOLD.render(text, True, color), (x_pos, HEIGHT - panel_height + 65))
        
        congestion_ratio = min(1.0, total/self.max_congestion)
        draw_stat_bar(surf, 30, HEIGHT - panel_height + 95, 280, 25, congestion_ratio, 
                     "Tingkat Kemacetan", (80,255,80), (255,80,80))
        draw_stat_bar(surf, 340, HEIGHT - panel_height + 95, 280, 25, air_score, 
                     "Kualitas Udara", (255,80,80), (80,255,80))
        
        if total > self.max_congestion:
            msg = MEDFONT.render("⚠️ MACET! Polusi bertambah! Tambahkan pohon!", True, (255,255,100))
            surf.blit(msg, (650, HEIGHT - panel_height + 20))
        
        controls_text = "🎮 Kontrol   |   A = + Mobil   |   Z = - Mobil   |   S = + Bus   |   X = - Bus   |   D = + Pohon   |   C = - Pohon   |   SPACE = Auto   |   ESC = Menu"
        rendered = FONT.render(controls_text, True, (220,220,220))
        
        box_width = rendered.get_width() + 40
        box_height = rendered.get_height() + 16
        box_x, box_y = 25, HEIGHT - panel_height + 140
        
        control_box = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        control_box.fill((30, 90, 50, 180))
        surf.blit(control_box, (box_x, box_y))
        pygame.draw.rect(surf, (120,200,140), (box_x, box_y, box_width, box_height), 2, border_radius=10)
        surf.blit(rendered, (box_x + 20, box_y + 8))


def draw_stat_bar(surf, x, y, w, h, ratio, label, good_color, bad_color):
    pygame.draw.rect(surf, (40,40,60), (x, y, w, h), border_radius=5)
    
    fill_w = int(w * ratio)
    color = blend_color(good_color, bad_color, ratio)
    pygame.draw.rect(surf, color, (x, y, fill_w, h), border_radius=5)
    pygame.draw.rect(surf, (200,200,200), (x, y, w, h), 2, border_radius=5)
    
    text = FONT.render(f"{label}: {int(ratio*100)}%", True, (255,255,255))
    surf.blit(text, (x + w//2 - text.get_width()//2, y + h//2 - text.get_height()//2))

def blend_color(c1, c2, ratio):
    return tuple(int(c1[i] * (1-ratio) + c2[i] * ratio) for i in range(3))


class PlantingSim:
    def __init__(self):
        self.slots = [None for _ in range(8)]
        self.ground_y = 520
        self.selected_slot = None
        self.clouds = [Cloud() for _ in range(3)]
        self.time = 0
        self.effects = []
        self.show_insight = False
        self.insight_timer = 0
        self.insight_duration = 5 * 60
        self.current_insight_stage = None
        
        self.insights = {
            0: {"tahap": "Bibit muncul", "pemicu": "Setelah bibit ditanam", 
                "insight": "Satu pohon dapat menyerap hingga 22 kg CO2 per tahun."},
            1: {"tahap": "Pohon muda", "pemicu": "Setelah beberapa interaksi (misalnya penyiraman)", 
                "insight": "Ruang hijau dapat menurunkan suhu kota hingga 2-4 C."},
            2: {"tahap": "Pohon besar", "pemicu": "Setelah tumbuh sepenuhnya", 
                "insight": "Satu pohon mampu menghasilkan oksigen untuk dua orang setiap harinya."},
            3: {"tahap": "Pohon berbuah", "pemicu": "Level akhir", 
                "insight": "Menanam pohon bukan hanya menjaga bumi, tetapi juga menjaga kehidupan generasi berikutnya."}
        }

    def plant_seed(self, slot_idx):
        if 0 <= slot_idx < len(self.slots) and self.slots[slot_idx] is None:
            self.slots[slot_idx] = Tree(140 + slot_idx * 120, self.ground_y, stage=0)
            self.show_insight = True
            self.insight_timer = 0
            self.current_insight_stage = 0

    def water_slot(self, slot_idx):
        t = self.slots[slot_idx]
        if t:
            t.water()
            self.show_insight = True
            self.insight_timer = 0
            self.current_insight_stage = t.stage

    def remove_tree(self, slot_idx):
        if 0 <= slot_idx < len(self.slots):
            self.slots[slot_idx] = None

    def update(self):
        self.time += 1
        
        if self.show_insight:
            self.insight_timer += 1
            if self.insight_timer > self.insight_duration:
                self.show_insight = False
                self.insight_timer = 0
        
        for cloud in self.clouds:
            cloud.update()
            
        for t in self.slots:
            if t:
                t.update()
                if t.reward_given:
                    self.effects.append(RewardEffect(t.x, t.ground_y - 80, random.choice(["star", "butterfly", "rainbow"])))
                    t.reward_given = False
                    self.show_insight = True
                    self.insight_timer = 0
                    self.current_insight_stage = t.stage
                    
        self.effects = [e for e in self.effects if e.life > 0]
        
        for e in self.effects:
            e.update()

    def draw(self, surf):
        for i in range(HEIGHT):
            c = 200 - i//4
            pygame.draw.line(surf, (c, c+35, 255), (0, i), (WIDTH, i))
        
        for cloud in self.clouds:
            cloud.draw(surf)
        
        pygame.draw.circle(surf, (255,255,100), (WIDTH-100, 150), 35)
        pygame.draw.circle(surf, (255,240,80), (WIDTH-100, 150), 32)
        
        pygame.draw.rect(surf, (90,170,90), (0, self.ground_y, WIDTH, HEIGHT-self.ground_y))
        pygame.draw.line(surf, (120,90,60), (0, self.ground_y), (WIDTH, self.ground_y), 5)
        
        for i in range(0, WIDTH, 15):
            pygame.draw.line(surf, (70,150,70), (i, self.ground_y), (i, self.ground_y+random.randint(5, 12)), 2)
        
        stage_names = ["🌱 Benih", "🌿 Tunas", "🌳 Kecil", "🌲 Dewasa"]
        for i in range(len(self.slots)):
            x = 140 + i*120
            slot_rect = pygame.Rect(x-50, self.ground_y, 100, 60)
            
            pygame.draw.rect(surf, (180,140,100,150), slot_rect, border_radius=10)
            pygame.draw.rect(surf, (100,70,40), slot_rect, 3, border_radius=10)
            
            if self.selected_slot == i:
                pygame.draw.rect(surf, (255,200,0), slot_rect, 5, border_radius=10)
                pygame.draw.polygon(surf, (255,200,0), [(x, self.ground_y - 75), (x-10, self.ground_y - 90), (x+10, self.ground_y - 90)])
            
            num = MEDFONT.render(f"#{i+1}", True, (60,40,20))
            surf.blit(num, (x - num.get_width()//2, self.ground_y - 52))
            
            t = self.slots[i]
            if t:
                t.draw(surf)
                stage_text = FONT.render(stage_names[t.stage], True, (40,100,40))
                surf.blit(stage_text, (x - stage_text.get_width()//2, self.ground_y + 20))
                
                if t.watered:
                    water_text = FONT_BOLD.render("💧 Disiram", True, (50,150,255))
                    surf.blit(water_text, (x - water_text.get_width()//2, self.ground_y + 40))
            else:
                empty_text = FONT.render("Kosong", True, (120,100,80))
                surf.blit(empty_text, (x - empty_text.get_width()//2, self.ground_y - 30))
        
        title_panel = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)
        title_panel.fill((40, 80, 40, 230))
        surf.blit(title_panel, (0, 0))
        
        title = BIGFONT.render("🌱 SIMULASI MENANAM POHON", True, (150,255,150))
        surf.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        subtitle = FONT.render("Tanam benih, siram secara teratur, dan saksikan pohon tumbuh!", True, (200,255,200))
        surf.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 65))
        
        instr_panel = pygame.Surface((WIDTH-40, 90), pygame.SRCALPHA)
        instr_panel.fill((60, 40, 20, 230))
        surf.blit(instr_panel, (20, HEIGHT-110))
        pygame.draw.rect(surf, (150,120,80), (20, HEIGHT-110, WIDTH-40, 90), 3, border_radius=8)
        
        instructions = [
            "🎮 Angka 1-8 = Pilih Slot | P = Tanam Benih | W = Siram Air | R = Cabut Pohon",
            "💡 Tips: Siram pohon secara teratur untuk membuatnya tumbuh lebih cepat!",
            "ESC = Kembali ke Menu"
        ]
        
        for i, text in enumerate(instructions):
            color = (255,230,180) if i < 2 else (255,200,100)
            surf.blit(FONT.render(text, True, color), (35, HEIGHT - 95 + i*25))

        for e in self.effects:
            e.draw(surf)
        
        if self.show_insight and self.current_insight_stage is not None:
            insight_data = self.insights[self.current_insight_stage]
            
            fade_duration = 30
            if self.insight_timer < fade_duration:
                alpha_factor = self.insight_timer / fade_duration
            elif self.insight_timer > self.insight_duration - fade_duration:
                alpha_factor = (self.insight_duration - self.insight_timer) / fade_duration
            else:
                alpha_factor = 1.0
            
            panel_width, panel_height = 750, 140
            panel_x = (WIDTH - panel_width) // 2
            panel_y = (HEIGHT - panel_height) // 2 - 50
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(100 * alpha_factor)))
            surf.blit(overlay, (0, 0))
            
            shadow_surf = pygame.Surface((panel_width + 8, panel_height + 8), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, int(150 * alpha_factor)))
            surf.blit(shadow_surf, (panel_x + 6, panel_y + 6))
            
            panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            for i in range(panel_height):
                pygame.draw.line(panel_surf, (20, 60, 40, int((240 - (i // 4)) * alpha_factor)), (0, i), (panel_width, i))
            surf.blit(panel_surf, (panel_x, panel_y))
            
            pygame.draw.rect(surf, (120, 220, 160, int(255 * alpha_factor)), (panel_x, panel_y, panel_width, panel_height), 5, border_radius=15)
            pygame.draw.rect(surf, (80, 180, 120, int(120 * alpha_factor)), (panel_x-3, panel_y-3, panel_width+6, panel_height+6), 3, border_radius=15)
            
            header = MEDFONT.render("✨🌿 Nature Speaks 🌿✨", True, (180, 255, 200))
            header.set_alpha(int(255 * alpha_factor))
            surf.blit(header, (panel_x + 25, panel_y + 20))
            
            tahap_label = FONT_BOLD.render("Tahap:", True, (200, 255, 220))
            tahap_value = FONT.render(insight_data["tahap"], True, (255, 255, 255))
            pemicu_label = FONT_BOLD.render("Pemicu:", True, (200, 255, 220))
            pemicu_value = FONT.render(insight_data["pemicu"], True, (255, 255, 255))
            
            for text_surf in [tahap_label, tahap_value, pemicu_label, pemicu_value]:
                text_surf.set_alpha(int(255 * alpha_factor))
            
            surf.blit(tahap_label, (panel_x + 25, panel_y + 58))
            surf.blit(tahap_value, (panel_x + 95, panel_y + 58))
            surf.blit(pemicu_label, (panel_x + 300, panel_y + 58))
            surf.blit(pemicu_value, (panel_x + 375, panel_y + 58))
            
            divider_surf = pygame.Surface((panel_width - 50, 2), pygame.SRCALPHA)
            divider_surf.fill((120, 220, 160, int(180 * alpha_factor)))
            surf.blit(divider_surf, (panel_x + 25, panel_y + 85))
            
            full_text = f"🌿 {insight_data['insight']}"
            words = full_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                if FONT_BOLD.size(test_line)[0] < panel_width - 60:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            
            for idx, line in enumerate(lines):
                text_surf = FONT_BOLD.render(line, True, (150, 255, 200))
                text_surf.set_alpha(int(255 * alpha_factor))
                surf.blit(text_surf, (panel_x + 25, panel_y + 95 + idx * 22))


class Pedestrian:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(0.8, 1.2)
        self.color = random.choice([(220, 80, 80), (80, 140, 220), (140, 200, 80), (220, 160, 80)])
        self.anim_frame = random.randint(0, 30)
        self.hair_color = (20, 20, 20)
        self.hair_style = random.choice(["short", "long"])
    
    def update(self):
        self.x += self.direction * self.speed
        self.anim_frame = (self.anim_frame + 1) % 30
        
        if self.x < -50:
            self.x = WIDTH + 50
            self.y = HEIGHT - 170 + random.randint(-8, 8)
        elif self.x > WIDTH + 50:
            self.x = -50
            self.y = HEIGHT - 170 + random.randint(-8, 8)
    
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        leg_swing = math.sin(self.anim_frame * 0.3) * 7
        arm_swing = math.sin(self.anim_frame * 0.3 + math.pi) * 5
        face_dir = self.direction

        pygame.draw.ellipse(surf, (0, 0, 0, 80), (x - 8, y + 20, 16, 6))

        leg_right_x = x + face_dir * 4 + leg_swing
        pygame.draw.line(surf, (50, 40, 30), (x, y + 8), (leg_right_x, y + 22), 4)
        pygame.draw.circle(surf, (40, 30, 20), (int(leg_right_x), y + 24), 4)
        
        leg_left_x = x + face_dir * -4 - leg_swing
        pygame.draw.line(surf, (50, 40, 30), (x, y + 8), (leg_left_x, y + 22), 4)
        pygame.draw.circle(surf, (40, 30, 20), (int(leg_left_x), y + 24), 4)

        body_rect = pygame.Rect(x - 6, y - 10, 12, 18)
        pygame.draw.ellipse(surf, self.color, body_rect)
        pygame.draw.ellipse(surf, tuple(max(0, c - 30) for c in self.color), body_rect, 2)

        arm_x = x + face_dir * 3 + arm_swing * 0.6
        pygame.draw.line(surf, (230, 200, 180), (x, y - 4), (int(arm_x), y + 8), 4)

        head_x, head_y = x, y - 18
        pygame.draw.circle(surf, (240, 210, 190), (head_x, head_y), 7)
        pygame.draw.circle(surf, (200, 170, 150), (head_x, head_y), 7, 1)
       
        if self.hair_style == "long":
            pygame.draw.ellipse(surf, self.hair_color, (head_x - 5, head_y - 6, 10, 18))
            pygame.draw.ellipse(surf, self.hair_color, (head_x - 9, head_y - 4, 6, 14))
            pygame.draw.ellipse(surf, self.hair_color, (head_x + 3, head_y - 4, 6, 14))

        hair_rect = pygame.Rect(head_x - 7, head_y - 10, 14, 10)
        pygame.draw.ellipse(surf, self.hair_color, hair_rect)
        pygame.draw.arc(surf, self.hair_color, (head_x - 7, head_y - 8, 14, 10), 0, math.pi, 2)
        
        eye_offset = 2 if face_dir > 0 else -2
        pygame.draw.circle(surf, (40, 30, 20), (head_x + eye_offset, head_y - 1), 2)


class Cyclist:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.direction = random.choice([-1, 1])
        self.speed = random.uniform(2.0, 3.0)
        self.color = random.choice([(220, 80, 80), (80, 140, 220), (140, 200, 80), (220, 160, 80)])
        self.anim_frame = random.randint(0, 20)
        
    def update(self):
        self.x += self.direction * self.speed
        self.anim_frame = (self.anim_frame + 1) % 20
        
        if self.x < -50:
            self.x = WIDTH + 50
            self.y = HEIGHT - 200 + random.randint(-8, 8)
        elif self.x > WIDTH + 50:
            self.x = -50
            self.y = HEIGHT - 200 + random.randint(-8, 8)
    
    def draw(self, surf):
        x, y = int(self.x), int(self.y)
        face_dir = self.direction
        pedal = math.sin(self.anim_frame * 0.5) * 6
        
        pygame.draw.ellipse(surf, (0, 0, 0, 80), (x - 12, y + 18, 24, 6))
        
        for wx in [x - 10, x + 10]:
            pygame.draw.circle(surf, (40, 40, 40), (wx, y + 12), 8)
            pygame.draw.circle(surf, (120, 120, 120), (wx, y + 12), 6)
        
        pygame.draw.line(surf, (200, 50, 50), (x - 10, y + 12), (x, y), 3)
        pygame.draw.line(surf, (200, 50, 50), (x, y), (x + 10, y + 12), 3)
        pygame.draw.line(surf, (200, 50, 50), (x, y), (x, y - 8), 3)
        pygame.draw.line(surf, (150, 150, 150), (x, y - 8), (x + face_dir * 6, y - 8), 3)
        
        body_y = y - 8
        pygame.draw.ellipse(surf, self.color, (x - 5, body_y - 10, 10, 12))
        pygame.draw.circle(surf, (240, 210, 190), (x, body_y - 16), 6)
        pygame.draw.circle(surf, (40, 25, 15), (x, body_y - 18), 6)
        pygame.draw.circle(surf, (240, 210, 190), (x, body_y - 14), 5)
        # Lengan ke stang
        pygame.draw.line(surf, (230, 200, 180), (x, body_y - 6), (x + face_dir * 6, y - 8), 3)
        
        # Kaki mengayuh pedal
        leg_x = x + pedal * face_dir
        leg_y = y + 6
        pygame.draw.line(surf, (50, 40, 30), (x, body_y), (leg_x, leg_y), 4)
        pygame.draw.circle(surf, (40, 30, 20), (leg_x, leg_y), 3)


class GreenCitySim:
    def __init__(self):
        self.buildings = []
        self.trees = []
        self.pedestrians = []
        self.cyclists = []
        self.cars = []
        self.buses = []
        self.clouds = [Cloud() for _ in range(4)]
        self.birds = []
        self.time = 0
        self.spawn_timer = 0
        self.init_scene()

    def init_scene(self):
        # Buildings with variety (base di posisi yang sama dengan pohon)
        building_base_y = HEIGHT - 240
        for i in range(6):
            w = random.randint(90,150)
            h = random.randint(150,320)
            x = 60 + i*185
            y = building_base_y - h
            color = random.choice([(110,120,135), (95,105,125), (125,115,105)])
            self.buildings.append(Building(x, y, w, h, color))
        
        # Initial trees (berjajar rapi, lebih kecil)
        tree_positions = [100, 230, 360, 490, 620, 750, 880, 1010]
        for x in tree_positions:
            t = Tree(x, HEIGHT-240, stage=1)
            self.trees.append(t)
        
        # Pedestrians
        for i in range(5):
            x = random.randint(0, WIDTH)
            y = HEIGHT-170 + random.randint(-10,10)
            self.pedestrians.append(Pedestrian(x, y))
        
        # Cyclists (pengendara sepeda)
        for i in range(4):
            x = random.randint(0, WIDTH)
            y = HEIGHT-200 + random.randint(-8, 8)
            self.cyclists.append(Cyclist(x, y))
        
        # Cars - POSISI DI TENGAH JALAN, spawn dengan jarak
        for i in range(2):  # Kurangi dari 3 ke 2
            self.cars.append(Vehicle(kind="car", 
                                    x=-100 - i * 350,  # spawn dengan jarak lebih jauh
                                    y=HEIGHT-215,  # POSISI DI TENGAH JALAN
                                    speed=random.uniform(1.5, 2.0),  # Kecepatan lebih lambat
                                    scale=1.0,
                                    enable_exhaust=False))
        
        # Initial buses - spawn dengan jarak
        for i in range(1):  # Kurangi dari 2 ke 1
            self.buses.append(Vehicle(kind="bus", 
                                     x=-500 - i * 400,  # spawn dengan jarak lebih jauh
                                     y=HEIGHT-215,  # POSISI DI TENGAH JALAN (sama dengan mobil)
                                     speed=random.uniform(1.0, 1.4),  # Kecepatan lebih lambat
                                     enable_exhaust=False))
                                    
        
        # Birds
        for i in range(5):
            self.birds.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(200, 300),
                "vx": random.uniform(-1, 1),
                "vy": random.uniform(-0.3, 0.3),
                "wing": 0
            })

    def can_spawn_vehicle(self, x_pos, vehicle_list, safe_distance=150):
        """Cek apakah aman untuk spawn kendaraan baru"""
        for v in vehicle_list:
            if abs(v.x - x_pos) < safe_distance:
                return False
        return True

    def update(self):
        self.time += 1
        self.spawn_timer += 1
        
        for cloud in self.clouds:
            cloud.update()
        
        for t in self.trees:
            t.update()
        
        # Cyclists
        for c in self.cyclists:
            c.update()
        
        # Pedestrians
        for p in self.pedestrians:
            p.update()
        
        # ===== UPDATE CARS (dengan collision detection) =====
        all_vehicles = self.cars + self.buses
        
        for car in self.cars:
            # Cek jarak dengan kendaraan lain
            can_move = True
            for other in all_vehicles:
                if other is car:
                    continue
                
                # Jika ada kendaraan di depan dalam jarak 80px, berhenti
                distance = other.x - car.x
                if 0 < distance < 80:
                    can_move = False
                    break
            
            if can_move:
                car.update()
        
        # Hapus mobil yang keluar layar
        self.cars = [c for c in self.cars if -300 < c.x < WIDTH + 300]
        
        # Spawn mobil baru (dengan jarak aman dan lebih jarang)
        if self.spawn_timer > 180 and random.random() < 0.3:  # Lebih jarang spawn
            if self.can_spawn_vehicle(-100, all_vehicles, safe_distance=250):  # Jarak lebih jauh
                self.cars.append(Vehicle(kind="car", x=-100, y=HEIGHT-215,  # Posisi tengah jalan
                                        speed=random.uniform(1.5, 2.0), scale=1.0,  # Kecepatan lebih lambat
                enable_exhaust=False))
                self.spawn_timer = 0
        
        # ===== UPDATE BUSES (dengan collision detection) =====
        for bus in self.buses:
            can_move = True
            for other in all_vehicles:
                if other is bus:
                    continue
                
                # Bus lebih panjang, butuh jarak lebih jauh (100px)
                distance = other.x - bus.x
                if 0 < distance < 100:
                    can_move = False
                    break
            
            if can_move:
                bus.update()
        
        # Hapus bus yang keluar layar
        self.buses = [b for b in self.buses if b.x < WIDTH + 200]
        
        # Spawn bus baru (dengan jarak aman dan lebih jarang lagi)
        if self.spawn_timer > 240 and random.random() < 0.25:  # Lebih jarang dari mobil
            if self.can_spawn_vehicle(-100, all_vehicles, safe_distance=300):  # Jarak lebih jauh
                self.buses.append(Vehicle(kind="bus", x=-100, y=HEIGHT-215,  # Posisi tengah jalan
                                         speed=random.uniform(1.0, 1.4),
                                         enable_exhaust=False)) # Kecepatan lebih lambat
                self.spawn_timer = 0
        
        # Birds
        for bird in self.birds:
            bird["x"] += bird["vx"]
            bird["y"] += bird["vy"]
            bird["wing"] = (bird["wing"] + 5) % 360
            
            if bird["x"] < -50 or bird["x"] > WIDTH + 50:
                bird["x"] = WIDTH + 50 if bird["vx"] < 0 else -50
                bird["y"] = random.randint(200, 300)

    def draw(self, surf):
        # ===== SKY GRADIENT (lebih halus) =====
        for i in range(HEIGHT):
            ratio = i / HEIGHT
            r = int(120 + (200 - 120) * ratio)
            g = int(180 + (240 - 180) * ratio)
            b = 255
            pygame.draw.line(surf, (r, g, b), (0, i), (WIDTH, i))

        # ===== SUN dengan GLOW (diturunkan posisinya) =====
        sun_x, sun_y = WIDTH - 120, 200
        
        # Glow layers
        for radius in [45, 38, 32]:
            alpha = 50 if radius == 45 else 90 if radius == 38 else 255
            sun_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(sun_surf, (255, 240, 100, alpha), (radius, radius), radius)
            surf.blit(sun_surf, (sun_x - radius, sun_y - radius))

        # ===== MOUNTAINS (posisi di tanah) =====
        mountain_color = (100,130,160)
        mountain_base_y = HEIGHT - 240
        
        # Gunung kiri
        pygame.draw.polygon(surf, mountain_color, [
            (0, mountain_base_y),
            (150, mountain_base_y - 80),
            (300, mountain_base_y - 40),
            (300, mountain_base_y),
            (0, mountain_base_y)
        ])
        
        # Gunung tengah (paling tinggi)
        pygame.draw.polygon(surf, (90, 120, 150), [
            (250, mountain_base_y),
            (450, mountain_base_y - 120),
            (650, mountain_base_y - 60),
            (650, mountain_base_y),
            (250, mountain_base_y)
        ])
        
        # Gunung kanan
        pygame.draw.polygon(surf, mountain_color, [
            (600, mountain_base_y),
            (800, mountain_base_y - 90),
            (1000, mountain_base_y - 50),
            (WIDTH, mountain_base_y - 70),
            (WIDTH, mountain_base_y),
            (600, mountain_base_y)
        ])
        
        # Mountain highlights (garis salju di puncak)
        pygame.draw.lines(surf, (140, 170, 200), False, 
                         [(150, mountain_base_y - 80),
                          (300, mountain_base_y - 40)], 2)
        
        pygame.draw.lines(surf, (140, 170, 200), False, 
                         [(450, mountain_base_y - 120),
                          (650, mountain_base_y - 60)], 2)
        
        pygame.draw.lines(surf, (140, 170, 200), False, 
                         [(800, mountain_base_y - 90),
                          (1000, mountain_base_y - 50)], 2)

        # ===== CLOUDS (diturunkan posisinya) =====
        for cloud in self.clouds:
            original_y = cloud.y
            cloud.y = 240
            cloud.draw(surf)
            cloud.y = original_y

        # ===== WIND TURBINES (posisi di tanah) =====
        turbine_base_y = HEIGHT - 240
        turbine_height = 130
        
        for x in [200, 450, 700, 950]:
            # Tower dengan shading
            pygame.draw.rect(surf, (240, 240, 240), (x, turbine_base_y - turbine_height, 7, turbine_height))
            pygame.draw.rect(surf, (200, 200, 200), (x + 5, turbine_base_y - turbine_height, 2, turbine_height))
            
            # Nacelle (rumah turbin)
            nacelle_y = turbine_base_y - turbine_height - 10
            pygame.draw.ellipse(surf, (255, 255, 255), (x - 8, nacelle_y, 23, 16))
            pygame.draw.ellipse(surf, (220, 220, 220), (x - 8, nacelle_y, 23, 16), 2)
            
            # Blades dengan motion
            angle_offset = (self.time * 2.5) % 360
            blade_length = 32
            blade_center_y = nacelle_y + 8
            
            for i in range(3):
                angle = math.radians(angle_offset + i * 120)
                end_x = (x + 3.5) + math.cos(angle) * blade_length
                end_y = blade_center_y + math.sin(angle) * blade_length
                
                # Blade shadow
                pygame.draw.line(surf, (200, 200, 200), 
                               (x + 5, blade_center_y + 2), (end_x + 2, end_y + 2), 4)
                
                # Blade
                pygame.draw.line(surf, (250, 250, 250), 
                               (x + 3.5, blade_center_y), (end_x, end_y), 4)
            
            # Center hub
            pygame.draw.circle(surf, (200, 200, 200), (int(x + 3.5), blade_center_y), 5)

        # ===== BUILDINGS =====
        for b in self.buildings:
            b.draw(surf)

        # ===== TREES =====
        for t in self.trees:
            t.draw(surf)

        # ===== ROAD =====
        road_y = HEIGHT - 240
        pygame.draw.rect(surf, (160, 160, 160), (0, road_y, WIDTH, 90))
        
        # Road texture (aspal)
        for i in range(0, WIDTH, 25):
            shade = random.randint(155, 165)
            pygame.draw.rect(surf, (shade, shade, shade), (i, road_y, 25, 90))

        # Center line (dashed yellow)
        for i in range(0, WIDTH, 65):
            pygame.draw.rect(surf, (255, 230, 100), (i + 12, road_y + 42, 40, 6), border_radius=2)

        # ===== SIDEWALK =====
        sidewalk_y = HEIGHT - 150
        pygame.draw.rect(surf, (200, 200, 200), (0, sidewalk_y, WIDTH, 30))
        
        # Sidewalk tiles
        for i in range(0, WIDTH, 35):
            pygame.draw.line(surf, (180, 180, 180), (i, sidewalk_y), (i, sidewalk_y + 30), 2)

        # ===== BIKE LANE =====
        bike_lane_y = HEIGHT - 165
        pygame.draw.line(surf, (80, 200, 80), (0, bike_lane_y), (WIDTH, bike_lane_y), 4)

        # ===== LAYERING SYSTEM (dari belakang ke depan) =====
        # Gabungkan semua kendaraan dan sort berdasarkan posisi X
        # Supaya yang di belakang digambar dulu, yang di depan digambar terakhir
        all_vehicles = [(v.x, v) for v in self.cars + self.buses]
        all_vehicles.sort(key=lambda item: item[0])
        
        # Gambar semua kendaraan dengan urutan yang benar
        for _, vehicle in all_vehicles:
            vehicle.draw(surf)
        
        # Layer 3: Cyclists (di depan kendaraan, di bike lane)
        for c in self.cyclists:
            c.draw(surf)
        
        # Layer 4: Pedestrians (paling depan, di sidewalk)
        for p in self.pedestrians:
            p.draw(surf)

        # ===== BIRDS =====
        for bird in self.birds:
            bx, by = int(bird["x"]), int(bird["y"])
            
            # Bird body
            pygame.draw.circle(surf, (60, 50, 40), (bx, by), 4)
            
            # Wings (animated)
            wing_angle = math.sin(math.radians(bird["wing"])) * 10
            wing_span = 10
            
            # Left wing
            pygame.draw.line(surf, (60, 50, 40),
                           (bx, by),
                           (bx - wing_span, by - abs(wing_angle)),
                           2)
            
            # Right wing
            pygame.draw.line(surf, (60, 50, 40),
                           (bx, by),
                           (bx + wing_span, by - abs(wing_angle)),
                           2)

        # ===== GRASS/GROUND =====
        ground_y = HEIGHT - 120
        pygame.draw.rect(surf, (75, 155, 75), (0, ground_y, WIDTH, 120))
        
        # Grass texture
        for i in range(0, WIDTH, 6):
            grass_h = random.randint(4, 9)
            grass_shade = random.randint(70, 90)
            pygame.draw.line(surf, (grass_shade, 150 + grass_shade//3, grass_shade),
                           (i, ground_y), (i, ground_y + grass_h), 2)

        # ===== UI PANEL (disederhanakan) =====
        panel_h = 100
        ui = pygame.Surface((WIDTH, panel_h), pygame.SRCALPHA)
        ui.fill((25, 75, 45, 240))
        surf.blit(ui, (0, 0))
        
        # Panel border
        pygame.draw.rect(surf, (80, 180, 120), (0, 0, WIDTH, panel_h), 3)

        # Title dengan shadow
        title_text = "🌿 Simulasi Kota Hijau"
        title_shadow = BIGFONT.render(title_text, True, (0, 0, 0))
        title = BIGFONT.render(title_text, True, (180, 255, 180))
        surf.blit(title_shadow, (22, 17))
        surf.blit(title, (20, 15))

        # Stats dengan icon (tambah mobil)
        stats_y = 62
        
        stat_items = [
            (f"🌳 Pohon: {len(self.trees)}", (150, 255, 150), 20),
            (f"🚗 Mobil: {len(self.cars)}", (255, 220, 150), 220),
            (f"🚌 Bus: {len(self.buses)}", (150, 200, 255), 420),
            (f"🚲 Sepeda: {len(self.cyclists)}", (255, 255, 150), 620),
            (f"🚶 Pejalan: {len(self.pedestrians)}", (255, 200, 150), 860)
        ]
        
        for text, color, x_pos in stat_items:
            surf.blit(FONT_BOLD.render(text, True, color), (x_pos, stats_y))
            
            
class App:
    def __init__(self):
        self.state = "menu"
        self.smart = SmartCitySim()
        self.plant = PlantingSim()
        self.green = GreenCitySim()
        self.buttons = []
        self.create_menu_buttons()
        self.particles = []
        self.menu_time = 0
        
        # Floating elements untuk animasi
        self.floating_elements = []
        for i in range(15):
            self.floating_elements.append({
                "x": random.randint(0, WIDTH),
                "y": random.randint(0, HEIGHT),
                "vx": random.uniform(-0.5, 0.5),
                "vy": random.uniform(-0.5, 0.5),
                "size": random.randint(20, 60),
                "color": random.choice([
                    (100, 255, 150, 30),
                    (100, 200, 255, 30),
                    (255, 200, 100, 30)
                ]),
                "phase": random.randint(0, 360)
            })

    def create_menu_buttons(self):
        self.buttons = [
            Button((WIDTH//2 - 225, 280, 450, 75), 
                   "🏙️ Simulasi Kota Cerdas", 
                   callback=lambda: self.set_state("smart"),
                   bg=(80,140,255), hover_bg=(100,160,255), fg=(255,255,255)),
            Button((WIDTH//2 - 225, 375, 450, 75), 
                   "🌱 Simulasi Menanam Pohon", 
                   callback=lambda: self.set_state("plant"),
                   bg=(60,200,100), hover_bg=(80,220,120), fg=(255,255,255)),
            Button((WIDTH//2 - 225, 470, 450, 75), 
                   "🌿 Simulasi Kota Hijau", 
                   callback=lambda: self.set_state("green"),
                   bg=(50,180,120), hover_bg=(70,200,140), fg=(255,255,255)),
            Button((WIDTH//2 - 225, 575, 450, 65), 
                   "❌ Keluar", 
                   callback=self.quit,
                   bg=(220,80,80), hover_bg=(240,100,100), fg=(255,255,255)),
        ]

    def set_state(self, s):
        self.state = s
        # Add transition particles
        for _ in range(50):
            self.particles.append(Particle(
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.choice([(100,255,150), (100,200,255), (255,200,100)]),
                vx=random.uniform(-3,3),
                vy=random.uniform(-3,3)
            ))

    def quit(self):
        pygame.quit()
        sys.exit()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if self.state == "menu":
                for b in self.buttons:
                    if b.rect.collidepoint((mx,my)):
                        b.click()
            elif self.state == "plant":
                for i in range(len(self.plant.slots)):
                    x = 140 + i*120
                    slot_rect = pygame.Rect(x-50, self.plant.ground_y-60, 100, 60)
                    if slot_rect.collidepoint((mx,my)):
                        self.plant.selected_slot = i
            elif self.state == "green":
                pass  # Tidak ada aksi klik di green city
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"
            
            if self.state == "smart":
                if event.key == pygame.K_a:
                    self.smart.add_vehicle("car")
                elif event.key == pygame.K_s:
                    self.smart.add_vehicle("bus")
                elif event.key == pygame.K_d:
                    self.smart.add_tree()
                elif event.key == pygame.K_z:
                    self.smart.remove_vehicle("car")
                elif event.key == pygame.K_x:
                    self.smart.remove_vehicle("bus")
                elif event.key == pygame.K_c:
                    self.smart.remove_tree()
                elif event.key == pygame.K_SPACE:
                    self.smart.spawn_auto = not self.smart.spawn_auto
            
            elif self.state == "plant":
                if pygame.K_1 <= event.key <= pygame.K_8:
                    idx = event.key - pygame.K_1
                    self.plant.selected_slot = idx
                elif event.key == pygame.K_p:
                    if self.plant.selected_slot is not None:
                        self.plant.plant_seed(self.plant.selected_slot)
                elif event.key == pygame.K_w:
                    if self.plant.selected_slot is not None:
                        self.plant.water_slot(self.plant.selected_slot)
                elif event.key == pygame.K_r:
                    if self.plant.selected_slot is not None:
                        self.plant.remove_tree(self.plant.selected_slot)
            
            elif self.state == "green":
                if event.key == pygame.K_t:
                    self.green.add_tree()
                elif event.key == pygame.K_y:
                    self.green.remove_tree()

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        if self.state == "menu":
            self.menu_time += 1
            # Update floating elements
            for elem in self.floating_elements:
                elem["x"] += elem["vx"]
                elem["y"] += elem["vy"]
                elem["phase"] = (elem["phase"] + 2) % 360
                
                # Bounce off edges
                if elem["x"] < -50 or elem["x"] > WIDTH + 50:
                    elem["vx"] *= -1
                if elem["y"] < -50 or elem["y"] > HEIGHT + 50:
                    elem["vy"] *= -1
        
        elif self.state == "smart":
            self.smart.update()
        elif self.state == "plant":
            self.plant.update()
        elif self.state == "green":
            self.green.update()

    def draw_menu(self):
        # ===== ANIMATED GRADIENT BACKGROUND =====
        for i in range(HEIGHT):
            # Wave effect on gradient
            wave = math.sin((i + self.menu_time) / 50) * 15
            ratio = (i + wave) / HEIGHT
            
            r = int(140 + (180 - 140) * ratio)
            g = int(180 + (220 - 180) * ratio)
            b = 255
            
            pygame.draw.line(SCREEN, (r, g, b), (0, i), (WIDTH, i))
        
        # ===== FLOATING ANIMATED ELEMENTS =====
        for elem in self.floating_elements:
            # Pulsing effect
            pulse = math.sin(math.radians(elem["phase"])) * 0.3 + 0.7
            size = int(elem["size"] * pulse)
            
            # Draw glowing circle
            glow_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            
            # Multiple glow layers
            for layer in range(3, 0, -1):
                alpha = elem["color"][3] // (layer * 2)
                radius = size * layer // 2
                pygame.draw.circle(glow_surf, (*elem["color"][:3], alpha), 
                                 (size * 3 // 2, size * 3 // 2), radius)
            
            SCREEN.blit(glow_surf, (int(elem["x"] - size * 1.5), int(elem["y"] - size * 1.5)))
        
        # ===== PARTICLES =====
        for p in self.particles:
            p.draw(SCREEN)
        
        # ===== LOGO/ICON (Earth) =====
        earth_x, earth_y = WIDTH // 2, 140
        
        # Rotating glow
        glow_angle = self.menu_time * 2
        for i in range(3):
            angle_offset = i * 120 + glow_angle
            glow_x = earth_x + math.cos(math.radians(angle_offset)) * 45
            glow_y = earth_y + math.sin(math.radians(angle_offset)) * 45
            
            glow_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (100, 255, 200, 80), (30, 30), 20)
            SCREEN.blit(glow_surf, (glow_x - 30, glow_y - 30))
        
        # Earth body (gradient circle)
        for r in range(50, 0, -2):
            color_factor = r / 50
            color = (
                int(50 + 150 * color_factor),
                int(150 + 100 * color_factor),
                int(50 + 200 * color_factor)
            )
            pygame.draw.circle(SCREEN, color, (earth_x, earth_y), r)
        
        # Earth continents (simple shapes)
        pygame.draw.ellipse(SCREEN, (80, 180, 100), (earth_x - 25, earth_y - 15, 30, 20))
        pygame.draw.ellipse(SCREEN, (80, 180, 100), (earth_x + 5, earth_y - 5, 25, 18))
        pygame.draw.circle(SCREEN, (80, 180, 100), (earth_x - 10, earth_y + 15), 8)
        
        # Shine effect
        pygame.draw.circle(SCREEN, (255, 255, 255, 150), (earth_x - 15, earth_y - 15), 12)
        pygame.draw.circle(SCREEN, (255, 255, 255, 80), (earth_x - 12, earth_y - 12), 8)
        
        # ===== TITLE WITH ANIMATED EFFECT =====
        title_y = 80
        
        # Shadow with multiple layers for depth
        for offset in range(5, 0, -1):
            shadow_alpha = 30 * offset
            title_shadow = BIGFONT.render("🌍 SIMULASI GRAFIKA", True, (0, 0, 0))
            title_shadow.set_alpha(shadow_alpha)
            SCREEN.blit(title_shadow, (WIDTH//2 - title_shadow.get_width()//2 + offset, 
                                      title_y + offset))
        
        # Main title with color wave
        title_text = "🌍 SIMULASI GRAFIKA"
        x_offset = 0
        base_x = WIDTH // 2 - BIGFONT.size(title_text)[0] // 2
        
        for i, char in enumerate(title_text):
            wave_y = math.sin(math.radians(self.menu_time * 3 + i * 20)) * 5
            
            # Rainbow-ish color effect
            color_shift = (self.menu_time + i * 10) % 360
            if color_shift < 120:
                color = (50, 255, 150)
            elif color_shift < 240:
                color = (100, 200, 255)
            else:
                color = (255, 200, 100)
            
            char_surf = BIGFONT.render(char, True, color)
            SCREEN.blit(char_surf, (base_x + x_offset, title_y + wave_y))
            x_offset += BIGFONT.size(char)[0]
        
        # ===== SUBTITLE =====
        subtitle = MEDFONT.render("Kota Cerdas • Menanam Pohon • Kota Hijau", True, (255, 255, 255))
        subtitle_shadow = MEDFONT.render("Kota Cerdas • Menanam Pohon • Kota Hijau", True, (0, 0, 0))
        
        subtitle_shadow.set_alpha(100)
        SCREEN.blit(subtitle_shadow, (WIDTH//2 - subtitle.get_width()//2 + 2, 202))
        SCREEN.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 200))
        
        # ===== DECORATIVE ELEMENTS =====
        # Animated rings around buttons area
        ring_time = self.menu_time * 2
        for i in range(3):
            ring_radius = 400 + i * 80 + (math.sin(math.radians(ring_time + i * 30)) * 20)
            ring_alpha = int(30 - i * 8)
            
            ring_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (100, 255, 200, ring_alpha), 
                             (WIDTH // 2, HEIGHT // 2), int(ring_radius), 2)
            SCREEN.blit(ring_surf, (0, 0))
        
        # ===== BUTTONS WITH ENHANCED STYLE =====
        for i, b in enumerate(self.buttons):
            # Animated entrance (stagger effect)
            if self.menu_time < 60:
                offset_y = max(0, (60 - self.menu_time - i * 10) * 5)
                temp_rect = b.rect.copy()
                temp_rect.y += offset_y
                
                # Temporarily modify button position for animation
                original_y = b.rect.y
                b.rect.y = temp_rect.y
            
            # Draw button with glow effect
            if b.hovered:
                glow_surf = pygame.Surface((b.rect.width + 20, b.rect.height + 20), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*b.hover_bg, 80), 
                               (0, 0, b.rect.width + 20, b.rect.height + 20), 
                               border_radius=12)
                SCREEN.blit(glow_surf, (b.rect.x - 10, b.rect.y - 10))
            
            b.draw(SCREEN)
            
            # Restore original position if animated
            if self.menu_time < 60:
                b.rect.y = original_y
        
        # ===== FOOTER WITH ANIMATED HINT =====
        footer_alpha = int((math.sin(math.radians(self.menu_time * 3)) * 0.3 + 0.7) * 255)
        footer = FONT.render("Gunakan mouse untuk memilih • Tekan ESC untuk kembali", True, (220, 240, 255))
        footer.set_alpha(footer_alpha)
        SCREEN.blit(footer, (WIDTH//2 - footer.get_width()//2, HEIGHT - 50))
        
        # Sparkle effect on footer
        if self.menu_time % 30 == 0:
            for _ in range(5):
                sparkle_x = random.randint(WIDTH//2 - 200, WIDTH//2 + 200)
                sparkle_y = HEIGHT - 50 + random.randint(-5, 5)
                self.particles.append(Particle(sparkle_x, sparkle_y, (255, 255, 200), 
                                              vx=random.uniform(-1, 1), vy=random.uniform(-2, -1)))

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "smart":
            self.smart.draw(SCREEN)
        elif self.state == "plant":
            self.plant.draw(SCREEN)
        elif self.state == "green":
            self.green.draw(SCREEN)
            
# ========== Main Loop ==========
def main():
    app = App()
    running = True
    
    while running:
        dt = CLOCK.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                app.handle_event(event)
        
        app.update()
        app.draw()
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()