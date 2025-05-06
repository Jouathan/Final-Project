import pygame
import time

# === Paths for images ===
PLAYER1_IMG_PATH    = "player1.png"    # Red (WASD)
PLAYER2_IMG_PATH    = "player2.png"    # Blue (Arrows)
BALL_IMG_PATH       = "ball.png"
BACKGROUND_IMG_PATH = "background.png"
ENDSCREEN_IMG_PATH  = "endscreen.png"
STARTSCREEN_IMG_PATH= "startscreen.jpg"

# === Initialize Pygame ===
pygame.init()
width, height = 800, 600
screen  = pygame.display.set_mode((width, height))
pygame.display.set_caption("2-Player Soccer Game")
clock   = pygame.time.Clock()

# === Colors ===
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
LIGHT_GRAY = (200, 200, 200)

# === Load & scale images ===
red_img         = pygame.image.load(PLAYER1_IMG_PATH).convert_alpha()
blue_img        = pygame.image.load(PLAYER2_IMG_PATH).convert_alpha()
ball_img        = pygame.image.load(BALL_IMG_PATH).convert_alpha()
background_img  = pygame.image.load(BACKGROUND_IMG_PATH).convert()
background_img  = pygame.transform.scale(background_img, (width, height))
endscreen_img   = pygame.image.load(ENDSCREEN_IMG_PATH).convert()
endscreen_img   = pygame.transform.scale(endscreen_img, (width, height))
startscreen_img = pygame.image.load(STARTSCREEN_IMG_PATH).convert()
startscreen_img = pygame.transform.scale(startscreen_img, (width, height))

# === Scale player sprites proportionally ===
scale = 0.07
red_w  = int(red_img.get_width()  * scale)
red_h  = int(red_img.get_height() * scale)
blue_w = int(blue_img.get_width() * scale)
blue_h = int(blue_img.get_height() * scale)
red_img  = pygame.transform.scale(red_img,  (red_w,  red_h))
blue_img = pygame.transform.scale(blue_img, (blue_w, blue_h))
player_size = (red_w, red_h)

# === Scale ball ===
ball_img = pygame.transform.scale(ball_img, (30, 30))

# === Spawn points ===
red_spawn  = (100, height//2 - red_h//2)
blue_spawn = (width - 150, height//2 - blue_h//2)

# === Game state ===
red_x, red_y     = red_spawn
blue_x, blue_y   = blue_spawn
player_speed     = 5
goalie1          = pygame.Rect(30, height//2 - 25, 20, 50)
goalie2          = pygame.Rect(width - 50, height//2 - 25, 20, 50)
goalie_speed     = 2
ball             = pygame.Rect(width//2 - 15, height//2 - 15, 30, 30)
ball_speed       = [0, 0]
ball_max_speed   = 6

score1, score2   = 0, 0
win_score        = 5
font_large       = pygame.font.SysFont(None, 72)
font_hud         = pygame.font.SysFont(None, 48)
game_duration    = 120
game_started     = False
start_time       = 0
game_over        = False
winner_text      = ""

# === Name-entry state (boxes now farther apart) ===
name1 = ""
name2 = ""
active_input = None  # 1 or 2
max_name_len = 12
input_box1 = pygame.Rect(width//2 - 150, height//2 - 200, 300, 50)
input_box2 = pygame.Rect(width//2 - 150, height//2 -  70, 300, 50)

# === Pause state ===
pause_duration      = 3
pause_start_time    = 0
is_paused_for_score = False

# === Buttons ===
btn_w, btn_h = 180, 60
start_btn    = pygame.Rect(width//2 - btn_w//2, height//2 +  20, btn_w, btn_h)
restart_btn  = pygame.Rect(width//2 - btn_w//2, height//2 + 100, btn_w, btn_h)

# === Start screen flag ===
show_start_screen = True

def draw_text_outline(surface, text, font, cx, cy, color):
    txt = font.render(text, True, color)
    ox, oy = txt.get_width()//2, txt.get_height()//2
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
        outline = font.render(text, True, BLACK)
        surface.blit(outline, (cx - ox + dx, cy - oy + dy))
    surface.blit(txt, (cx - ox, cy - oy))

def reset_ball():
    ball.center    = (width//2, height//2)
    ball_speed[0]  = ball_speed[1] = 0

def reset_after_score(scorer):
    global red_x, red_y, blue_x, blue_y
    global is_paused_for_score, pause_start_time, game_over, winner_text
    reset_ball()
    if scorer == "red":
        red_x, red_y = red_spawn
        blue_x = ball.centerx + 40
        blue_y = ball.centery - red_h//2
    else:
        blue_x, blue_y = blue_spawn
        red_x = ball.centerx - red_w - 40
        red_y = ball.centery - red_h//2
    if score1 >= win_score:
        game_over   = True
        winner_text = f"{name1} Wins!"
    elif score2 >= win_score:
        game_over   = True
        winner_text = f"{name2} Wins!"
    else:
        is_paused_for_score = True
        pause_start_time    = time.time()

# === Main loop ===
running = True
while running:
    dt     = clock.tick(60) / 1000.0
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            running = False

    # --- Start Screen ---
    if show_start_screen:
        screen.blit(startscreen_img, (0, 0))
        draw_text_outline(screen, "CLICK OR PRESS ANY KEY",
                          font_hud, width//2, height - 80, WHITE)
        pygame.display.flip()
        if any(e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN) for e in events):
            show_start_screen = False
        continue

    # --- Handle input & buttons ---
    for e in events:
        if e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            if not game_started:
                if input_box1.collidepoint(mx,my):
                    active_input = 1
                elif input_box2.collidepoint(mx,my):
                    active_input = 2
                elif start_btn.collidepoint(mx,my) and name1 and name2:
                    game_started = True
                    start_time   = time.time()
            if game_over and restart_btn.collidepoint(mx,my):
                score1 = score2 = 0
                game_over = False
                game_started = False
                is_paused_for_score = False
                name1 = name2 = ""
                active_input = None
                red_x, red_y   = red_spawn
                blue_x, blue_y = blue_spawn
        elif e.type == pygame.KEYDOWN and not game_started:
            if active_input == 1:
                if e.key == pygame.K_BACKSPACE:
                    name1 = name1[:-1]
                elif e.key == pygame.K_RETURN:
                    active_input = 2
                elif len(name1) < max_name_len and e.unicode.isprintable():
                    name1 += e.unicode
            elif active_input == 2:
                if e.key == pygame.K_BACKSPACE:
                    name2 = name2[:-1]
                elif e.key == pygame.K_RETURN:
                    active_input = None
                elif len(name2) < max_name_len and e.unicode.isprintable():
                    name2 += e.unicode

    keys = pygame.key.get_pressed()

    # Timer
    if game_started and not game_over:
        elapsed   = time.time() - start_time
        time_left = max(0, int(game_duration - elapsed))
        if time_left <= 0:
            game_over   = True
            winner_text = "Time Up!"
    else:
        time_left = game_duration

    # Gameplay
    if game_started and not game_over and not is_paused_for_score:
        # Red (WASD)
        if keys[pygame.K_a]: red_x -= player_speed
        if keys[pygame.K_d]: red_x += player_speed
        if keys[pygame.K_w]: red_y -= player_speed
        if keys[pygame.K_s]: red_y += player_speed
        # Blue (Arrows)
        if keys[pygame.K_LEFT]:  blue_x -= player_speed
        if keys[pygame.K_RIGHT]: blue_x += player_speed
        if keys[pygame.K_UP]:    blue_y -= player_speed
        if keys[pygame.K_DOWN]:  blue_y += player_speed

        # Clamp
        red_x = max(0, min(width-red_w,   red_x))
        red_y = max(0, min(height-red_h,  red_y))
        blue_x= max(0, min(width-blue_w,  blue_x))
        blue_y= max(0, min(height-blue_h, blue_y))

        r_rect = pygame.Rect(red_x,  red_y,  red_w,  red_h)
        b_rect = pygame.Rect(blue_x, blue_y, blue_w, blue_h)

        for g in (goalie1, goalie2):
            if g.centery < ball.centery: g.y += goalie_speed
            elif g.centery > ball.centery: g.y -= goalie_speed
            g.clamp_ip(screen.get_rect())

        ball.x += ball_speed[0]
        ball.y += ball_speed[1]
        if r_rect.colliderect(ball):
            ball_speed[0] = ball_max_speed
            ball_speed[1] = (ball.centery - r_rect.centery)//4
        if b_rect.colliderect(ball):
            ball_speed[0] = -ball_max_speed
            ball_speed[1] = (ball.centery - b_rect.centery)//4
        for g in (goalie1, goalie2):
            if g.colliderect(ball):
                ball_speed[0] *= -1
                ball_speed[1] = (ball.centery - g.centery)//4
        if ball.top <= 0 or ball.bottom >= height:
            ball_speed[1] *= -1

        if ball.left <= 0:
            score2 += 1
            reset_after_score("blue")
        if ball.right >= width:
            score1 += 1
            reset_after_score("red")

    if is_paused_for_score and (time.time() - pause_start_time >= pause_duration):
        is_paused_for_score = False

    # --- Drawing ---
    if game_over:
        screen.blit(endscreen_img, (0,0))
        draw_text_outline(screen, winner_text, font_large, width//2, height//2 - 80, WHITE)
        pygame.draw.rect(screen, LIGHT_GRAY, restart_btn)
        draw_text_outline(screen, "RESTART", font_hud, restart_btn.centerx, restart_btn.centery, WHITE)
    elif not game_started:
        screen.blit(background_img, (0,0))
        # name entry with more vertical separation
        draw_text_outline(screen, "Enter Player 1 Name:", font_hud, width//2, input_box1.y - 20, WHITE)
        pygame.draw.rect(screen, WHITE if active_input==1 else LIGHT_GRAY, input_box1, 2)
        draw_text_outline(screen, name1 or "Player1", font_hud, input_box1.centerx, input_box1.centery, WHITE)
        draw_text_outline(screen, "Enter Player 2 Name:", font_hud, width//2, input_box2.y - 20, WHITE)
        pygame.draw.rect(screen, WHITE if active_input==2 else LIGHT_GRAY, input_box2, 2)
        draw_text_outline(screen, name2 or "Player2", font_hud, input_box2.centerx, input_box2.centery, WHITE)
        # START button
        pygame.draw.rect(screen, LIGHT_GRAY if not (name1 and name2) else WHITE, start_btn)
        draw_text_outline(screen, "START", font_hud, start_btn.centerx, start_btn.centery,
                          BLACK if name1 and name2 else WHITE)
    else:
        screen.blit(background_img, (0,0))
        pygame.draw.line(screen, WHITE, (width//2,0), (width//2,height), 5)
        screen.blit(red_img,  (red_x,  red_y))
        screen.blit(blue_img, (blue_x, blue_y))
        pygame.draw.rect(screen, WHITE, goalie1)
        pygame.draw.rect(screen, WHITE, goalie2)
        screen.blit(ball_img, ball)

        draw_text_outline(screen, str(score1), font_hud, width//4, 20, WHITE)
        draw_text_outline(screen, str(score2), font_hud, 3*width//4, 20, WHITE)
        draw_text_outline(screen, str(time_left), font_hud, width//2, 20, WHITE)

        if is_paused_for_score:
            cnt = int(pause_duration - (time.time() - pause_start_time)) + 1
            draw_text_outline(screen, str(cnt), font_large, width//2, height//2, WHITE)

    pygame.display.flip()

pygame.quit()
