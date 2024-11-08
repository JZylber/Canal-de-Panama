import pygame
from canal import minute, initial_canal_state, CanalState, StateObserver

def draw_arrow(screen, dimensions, center, direction):
    arrow_image = pygame.image.load(f"assets/arrow.png").convert_alpha()
    arrow_image = pygame.transform.scale(arrow_image, dimensions)
    if direction == "down":
        arrow_image = pygame.transform.rotate(arrow_image, 90)
    elif direction == "up":
        arrow_image = pygame.transform.rotate(arrow_image, -90)
    elif direction == "right":
        arrow_image = pygame.transform.rotate(arrow_image, 180)
    arrow = arrow_image.get_rect()
    arrow.center = center
    screen.blit(arrow_image, arrow)

def draw_ship(screen, dimensions, center, direction, name):
    ship_image = pygame.image.load(f"assets/ship.png").convert_alpha()
    ship_image = pygame.transform.scale(ship_image, dimensions)
    if direction == "upstream":
        ship_image = pygame.transform.flip(ship_image, True, False)
    ship = ship_image.get_rect()
    ship.center = center
    screen.blit(ship_image, ship)
    font = pygame.font.SysFont("montserrat", 24)
    ship_name = font.render(name, 1, (0,0,0))
    ship_name_rect = ship_name.get_rect()
    screen.blit(ship_name, (center[0] - ship_name_rect.width/2, center[1] - dimensions[1]/2 - ship_name_rect.height))

def draw_lock(screen, dimensions, start_position, gates, level, boat, direction):
    initial_x, initial_y = start_position
    # Draw lock walls
    pygame.draw.lines(screen, (0,0,0), False, [(initial_x,initial_y), (initial_x,initial_y + dimensions["LOCK_HEIGHT"]),(initial_x + dimensions["LOCK_WIDTH"],initial_y + dimensions["LOCK_HEIGHT"]),(initial_x + dimensions["LOCK_WIDTH"],initial_y)], dimensions["LOCK_BORDER_WIDTH"])
    # Clear interior
    pygame.draw.rect(screen, (255,255,255), [initial_x + dimensions["LOCK_BORDER_WIDTH"]/2,initial_y - dimensions["BOAT_HEIGHT"], dimensions["LOCK_WIDTH"] - dimensions["LOCK_BORDER_WIDTH"] + 1, dimensions["BOAT_HEIGHT"] + dimensions["LOCK_HEIGHT"] - dimensions["LOCK_BORDER_WIDTH"]/2])
    # Draw lock water
    water_level = dimensions["LOCK_WATER_LEVELS"][1]
    if level == "high":
        water_level = dimensions["LOCK_WATER_LEVELS"][2]
    elif level == "low":
        water_level = dimensions["LOCK_WATER_LEVELS"][0]
    pygame.draw.rect(screen, (146,237,249), [initial_x + dimensions["LOCK_BORDER_WIDTH"]/2,initial_y + dimensions["LOCK_HEIGHT"] - water_level - dimensions["LOCK_BORDER_WIDTH"]/2 + 1, dimensions["LOCK_WIDTH"] - dimensions["LOCK_BORDER_WIDTH"] + 1, water_level])
    # Draw arrows
    if level == "draining":
        draw_arrow(screen, (40,30), (initial_x + dimensions["LOCK_WIDTH"]/2,initial_y + dimensions["LOCK_HEIGHT"] - dimensions["LOCK_BORDER_WIDTH"]/2 - water_level/2), "down")
    elif level == "filling":
        draw_arrow(screen, (40,30), (initial_x + dimensions["LOCK_WIDTH"]/2,initial_y + dimensions["LOCK_HEIGHT"] - dimensions["LOCK_BORDER_WIDTH"]/2 - water_level/2), "up")
    # Draw gates
    left_gate,right_gate = gates
    if left_gate:
        pygame.draw.line(screen, (255,255,255), (initial_x,initial_y), (initial_x,initial_y + dimensions["LOCK_HEIGHT"] - dimensions["LOCK_BORDER_WIDTH"]/2 - water_level), dimensions["LOCK_BORDER_WIDTH"])
        pygame.draw.line(screen, (146,237,249), (initial_x,initial_y + dimensions["LOCK_HEIGHT"] - dimensions["LOCK_BORDER_WIDTH"]/2 + 1 - water_level), (initial_x,initial_y + dimensions["LOCK_HEIGHT"] - dimensions["LOCK_BORDER_WIDTH"]/2), dimensions["LOCK_BORDER_WIDTH"])
    water_level_difference = dimensions["LOCK_WATER_LEVELS"][0] + dimensions["LOCK_HEIGHT"] - dimensions["LOCK_WATER_LEVELS"][2]
    if right_gate:
        pygame.draw.line(screen, (255,255,255), (initial_x + dimensions["LOCK_WIDTH"],initial_y), (initial_x + dimensions["LOCK_WIDTH"],initial_y + water_level_difference - dimensions["LOCK_BORDER_WIDTH"]/2), dimensions["LOCK_BORDER_WIDTH"])
        if level == "high":
            pygame.draw.line(screen, (146,237,249), (initial_x + dimensions["LOCK_WIDTH"],initial_y + water_level_difference - dimensions["LOCK_BORDER_WIDTH"]/2), (initial_x + dimensions["LOCK_WIDTH"],initial_y + water_level_difference - dimensions["LOCK_BORDER_WIDTH"]/2 + 1 - dimensions["LOCK_WATER_LEVELS"][0]), dimensions["LOCK_BORDER_WIDTH"])
    # Draw boat
    if boat == "":
        pygame.draw.rect(screen, (255,255,255), [initial_x + dimensions["LOCK_WIDTH"]/2 - dimensions["BOAT_WIDTH"]/2,initial_y + dimensions["LOCK_HEIGHT"] - water_level - dimensions["LOCK_BORDER_WIDTH"]/2 + 1 - dimensions["BOAT_HEIGHT"], dimensions["BOAT_WIDTH"], dimensions["BOAT_HEIGHT"]])
    else:
        draw_ship(screen, (dimensions["BOAT_WIDTH"],dimensions["BOAT_HEIGHT"]), (initial_x + dimensions["LOCK_WIDTH"]/2,initial_y + dimensions["LOCK_HEIGHT"] - water_level - dimensions["LOCK_BORDER_WIDTH"]/2 + 1 - dimensions["BOAT_HEIGHT"]/2), direction, boat)

def draw_locks(screen, dimensions, state):
    water_level_difference = dimensions["LOCK_WATER_LEVELS"][0]
    draw_lock(screen, dimensions, (dimensions["SCREEN_WIDTH"]/2 - dimensions["LOCK_WIDTH"] * 1.5 - dimensions["LOCK_BORDER_WIDTH"] , dimensions["SCREEN_HEIGHT"]/2 + dimensions["LOCK_HEIGHT"] * 0.5 - dimensions["LOCK_WATER_LEVELS"][0] - dimensions["LOCK_BORDER_WIDTH"] - water_level_difference), (state["gates"][0],state["gates"][1]), state["locks_water_level"][0], state["locks"][0], state["direction"])
    draw_lock(screen, dimensions, ((dimensions["SCREEN_WIDTH"] - dimensions["LOCK_WIDTH"])/2,(dimensions["SCREEN_HEIGHT"] - dimensions["LOCK_HEIGHT"])/2), (state["gates"][1],state["gates"][2]), state["locks_water_level"][1], state["locks"][1], state["direction"])
    draw_lock(screen, dimensions, (dimensions["SCREEN_WIDTH"]/2 + dimensions["LOCK_WIDTH"] * 0.5 + dimensions["LOCK_BORDER_WIDTH"],dimensions["SCREEN_HEIGHT"]/2 - dimensions["LOCK_HEIGHT"] * 1.5 + dimensions["LOCK_WATER_LEVELS"][0] + dimensions["LOCK_BORDER_WIDTH"] + water_level_difference), (state["gates"][2],state["gates"][3]), state["locks_water_level"][2], state["locks"][2], state["direction"])

def draw_lock_open(screen, dimensions, state, direction):
    closed_image = pygame.image.load(f"assets/closed.png").convert_alpha()
    open_image = pygame.image.load(f"assets/open.png").convert_alpha()
    closed_image = pygame.transform.scale(closed_image, (100, 100))
    open_image = pygame.transform.scale(open_image, (100, 100))
    if not state:
        image = closed_image
    else:
        image = open_image
    lock_state = image.get_rect()
    lock_state.center = (dimensions["SCREEN_WIDTH"]/2, 100)
    screen.blit(image, lock_state)
    if direction == "upstream":
        pygame.draw.rect(screen, (255,255,255), [dimensions["SCREEN_WIDTH"]/2 - 175, 62.5, 100, 75])
        draw_arrow(screen, (100,75), (dimensions["SCREEN_WIDTH"]/2 + 125, 100), "right")
    elif direction == "downstream":
        pygame.draw.rect(screen, (255,255,255), [dimensions["SCREEN_WIDTH"]/2 + 75, 62.5, 100, 75])
        draw_arrow(screen, (100,75), (dimensions["SCREEN_WIDTH"]/2 - 125, 100), "left")

def display_time(screen, time):
    font = pygame.font.SysFont("montserrat", 60)
    time_text = font.render(f"Minuto: {time}", 1, (0,0,0))
    time_text_rect = time_text.get_rect()
    pygame.draw.rect(screen, (255,255,255), [15, 15, time_text_rect.width + 5, time_text_rect.height + 5])
    screen.blit(time_text, (15, 15))
        
def update_downstream_queue(screen, dimensions, state):
    queue_font = pygame.font.SysFont("montserrat", 60)
    downstream_queue = queue_font.render(f"{len(state['queue_downstream'])}", 1, (0,0,0))
    downstream_queue_position = (dimensions["SCREEN_WIDTH"]/6 - 60 - downstream_queue.get_width() / 2, 620 - downstream_queue.get_height()/2)
    downstream_queue_rect = downstream_queue.get_rect()
    pygame.draw.rect(screen, (255,255,255), [downstream_queue_position[0] - 5, downstream_queue_position[1] - 5, downstream_queue_rect.width + 10, downstream_queue_rect.height + 10])
    screen.blit(downstream_queue, downstream_queue_position)

def update_upstream_queue(screen, dimensions, state):
    queue_font = pygame.font.SysFont("montserrat", 60)
    upstream_queue = queue_font.render(f"{len(state['queue_upstream'])}", 1, (0,0,0))
    upstream_queue_position = (dimensions["SCREEN_WIDTH"]*5/6 + 60 - upstream_queue.get_width() / 2, 620 - upstream_queue.get_height()/2)
    upstream_queue_rect = upstream_queue.get_rect()
    pygame.draw.rect(screen, (255,255,255), [upstream_queue_position[0] - 5, upstream_queue_position[1] - 5, upstream_queue_rect.width + 10, upstream_queue_rect.height + 10])
    screen.blit(upstream_queue, upstream_queue_position)

def draw_state(screen, dimensions, initial_height, state : CanalState):
    debug_font = pygame.font.SysFont("montserrat", 24)
    line_height = 2
    text_height = initial_height
    locks_text = debug_font.render(f"{'Locks': <10}: {state['locks']}", 1, (0,0,0))
    locks_text_rect = locks_text.get_rect()
    screen.blit(locks_text, (dimensions["SCREEN_WIDTH"], text_height))
    text_height += locks_text_rect.height + line_height
    levels_text = debug_font.render(f"{'Levels': <10}: {state['locks_water_level']}", 1, (0,0,0))
    levels_text_rect = levels_text.get_rect()
    screen.blit(levels_text, (dimensions["SCREEN_WIDTH"], text_height))
    text_height += levels_text_rect.height + line_height
    gates_text = debug_font.render(f"{'Gates': <10}: {state['gates']}", 1, (0,0,0))
    gates_text_rect = gates_text.get_rect()
    screen.blit(gates_text, (dimensions["SCREEN_WIDTH"], text_height))
    text_height += gates_text_rect.height + line_height
    control_text = debug_font.render(f"Control:", 1, (0,0,0))
    control_text_rect = control_text.get_rect()
    screen.blit(control_text, (dimensions["SCREEN_WIDTH"], text_height))
    text_height += control_text_rect.height + line_height
    for action in state["control"]:
        action_text = debug_font.render(f"{action}", 1, (0,0,0))
        action_text_rect = action_text.get_rect()
        screen.blit(action_text, (dimensions["SCREEN_WIDTH"], text_height))
        text_height += action_text_rect.height + line_height
    return text_height

def draw_phase_change(screen, dimensions, initial_height, phase):
    text_height = initial_height
    label_font = pygame.font.SysFont("montserrat", 30)
    phase_text = label_font.render(phase, 1, (0,0,0))
    phase_text_rect = phase_text.get_rect()
    screen.blit(phase_text, (dimensions["SCREEN_WIDTH"] + dimensions["DEBUG_WIDTH"]/4 - phase_text_rect.width/2, text_height + 20 - phase_text_rect.height/2))
    draw_arrow(screen, (40,30), (dimensions["SCREEN_WIDTH"] + dimensions["DEBUG_WIDTH"]/2, text_height + 20), "down")
    return text_height + 40

def draw_debug(screen, dimensions, state_observer : StateObserver):
    clear_debug(screen, dimensions)
    height = draw_state(screen, dimensions, 20, state_observer.get_state("Initial"))
    height = draw_phase_change(screen, dimensions, height, "FASE 1")
    height = draw_state(screen, dimensions, height + 5, state_observer.get_state("Phase 1"))
    height = draw_phase_change(screen, dimensions, height, "FASE 2")
    height = draw_state(screen, dimensions, height + 5, state_observer.get_state("Phase 2"))
    height = draw_phase_change(screen, dimensions, height, "FASE 3")
    height = draw_state(screen, dimensions, height + 5, state_observer.get_state("Final"))


def clear_debug(screen, dimensions):
    pygame.draw.rect(screen, (255,255,255), [dimensions["SCREEN_WIDTH"], 0, dimensions["DEBUG_WIDTH"], dimensions["SCREEN_HEIGHT"]])


def main(): 
    pygame.init()
    dimensions = {
        "SCREEN_WIDTH": 1024,
        "DEBUG_WIDTH": 342,
        "SCREEN_HEIGHT": 704,
        "LOCK_WIDTH": 200,
        "LOCK_HEIGHT": 100,
        "LOCK_BORDER_WIDTH": 5,
        "BOAT_WIDTH": 100,
        "BOAT_HEIGHT": 35,
        "LOCK_WATER_LEVELS": [15,50,80]
    }
    screen = pygame.display.set_mode((dimensions["SCREEN_WIDTH"] + dimensions["DEBUG_WIDTH"], dimensions["SCREEN_HEIGHT"])) 
    
    # TITLE OF CANVAS 
    pygame_icon = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(pygame_icon)
    pygame.display.set_caption("Esclusas de Gatún") 
    screen.fill((255, 255, 255))

    #Clock
    clock_image = pygame.image.load(f"assets/clock.png").convert_alpha()
    clock_image = pygame.transform.scale(clock_image, (100, 100))
    clock = clock_image.get_rect()
    clock.center = (dimensions["SCREEN_WIDTH"]/2, 550)
    screen.blit(clock_image, clock)
    
    #Switch Direction
    switch_image = pygame.image.load(f"assets/swap.png").convert_alpha()
    switch_image = pygame.transform.scale(switch_image, (75, 75))
    switch = switch_image.get_rect()
    switch.center = (dimensions["SCREEN_WIDTH"]/2, dimensions["SCREEN_HEIGHT"] - 50)
    screen.blit(switch_image, switch)

    plus_image = pygame.image.load(f"assets/plus.png").convert_alpha()
    plus_image = pygame.transform.scale(plus_image, (60, 60))
    #Add Downstream
    downstream = plus_image.get_rect()
    downstream.center = (dimensions["SCREEN_WIDTH"]/6, 620)
    screen.blit(plus_image, downstream)
    #Add Upstream
    upstream = plus_image.get_rect()
    upstream.center = (dimensions["SCREEN_WIDTH"]/6*5, 620)
    screen.blit(plus_image, upstream)

    #Debug Button
    font = pygame.font.SysFont("montserrat", 60)
    debug_text = font.render("DEBUG", 1, (255,255,255))
    debug_text_rect = debug_text.get_rect()
    debug_button = pygame.draw.rect(screen, (0,0,0), [dimensions["SCREEN_WIDTH"] - debug_text_rect.width - 25, 20, debug_text_rect.width, debug_text_rect.height])
    screen.blit(debug_text, (dimensions["SCREEN_WIDTH"] - debug_text_rect.width - 25, 20))


    exit = False
    debug = False
    state = initial_canal_state()
    state_observer = StateObserver()
    time = 0
    boat_number = 1
    display_time(screen, time)
    update_downstream_queue(screen, dimensions, state)
    update_upstream_queue(screen, dimensions, state)
    while not exit:
        draw_locks(screen, dimensions, state)
        draw_lock_open(screen, dimensions, state["open"], state["direction"])
        events = pygame.event.get()
        for event in events: 
            if event.type == pygame.QUIT: 
                exit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                position = pygame.mouse.get_pos()
                if clock.collidepoint(position):
                    minute(state, state_observer)
                    time += 1
                    display_time(screen, time)
                    update_downstream_queue(screen, dimensions, state)
                    update_upstream_queue(screen, dimensions, state)
                    if debug:
                        draw_debug(screen, dimensions, state_observer)
                if downstream.collidepoint(position):
                    state["queue_downstream"].append(f"ARA {boat_number}")
                    boat_number += 1
                    update_downstream_queue(screen, dimensions, state)
                if upstream.collidepoint(position):
                    state["queue_upstream"].append(f"`ARA {boat_number}")
                    boat_number += 1
                    update_upstream_queue(screen, dimensions, state)
                if switch.collidepoint(position) and state["open"]:
                    state["control"].append((1,f"direction open {'downstream' if state['direction'] == 'upstream' else 'upstream'}"))
                if debug_button.collidepoint(position):
                    debug = not debug
                    if debug:
                        draw_debug(screen, dimensions, state_observer)
                    else:
                        clear_debug(screen, dimensions)
        pygame.display.update()
    pygame.quit()

if __name__ == "__main__":
    main()
