import machine
import ssd1306
import time
import random

# --- Hardware Configuration ---
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))
display = ssd1306.SSD1306_I2C(128, 64, i2c)

trig = machine.Pin(5, machine.Pin.OUT)
echo = machine.Pin(18, machine.Pin.IN)

# --- Game Constants ---
WIDTH = 128
HEIGHT = 64
PLAYER_X = 20
PLAYER_SIZE = 6
MIN_DIST = 5    
MAX_DIST = 25   
GAP_SIZE = 24   
PIPE_WIDTH = 8
BASE_SPEED = 2.0
SMOOTHING = 0.2  # Value between 0 and 1. Smaller = smoother.

# --- State Variables ---
score = 0
high_score = 0
prev_high_score = 0 # To calculate diff correctly when record is broken
speed_mult = 1.0
pipes = [] 
game_state = "START" 
player_y = float(HEIGHT // 2)
filtered_d = 15.0

def get_distance():
    """Get raw distance from HC-SR04 sensor."""
    trig.value(0)
    time.sleep_us(5)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    duration = machine.time_pulse_us(echo, 1, 30000)
    if duration < 0: return 500.0 # Return large value on timeout
    return (duration * 0.0343) / 2

def spawn_pipe(x_pos):
    """Create a pipe with a random gap."""
    gap_y = random.randint(10, HEIGHT - 10 - GAP_SIZE)
    return [float(x_pos), gap_y]

def reset_game():
    global score, speed_mult, pipes, player_y, game_state, filtered_d
    score = 0
    speed_mult = 1.0
    player_y = float(HEIGHT // 2)
    pipes = [spawn_pipe(128), spawn_pipe(128 + 70)]
    game_state = "PLAYING"

def draw_ui():
    """Draw top status bar."""
    display.text(str(score), 0, 0)
    display.text("HI:{}".format(high_score), 45, 0)
    display.text("{:.1f}x".format(speed_mult), 95, 0)
    display.hline(0, 9, WIDTH, 1)

# --- Main Game Loop with Cleanup ---
try:
    while True:
        raw_d = get_distance()
        
        # Logic for updating the filtered distance
        diff_d = abs(raw_d - filtered_d)
        
        # If in Menu or Paused, allow faster convergence to "catch" the hand
        if game_state in ["START", "PAUSED", "GAMEOVER"]:
            if MIN_DIST <= raw_d <= MAX_DIST:
                filtered_d = raw_d # Instant snap to hand in menus/pause
            else:
                filtered_d = filtered_d + 0.5 * (raw_d - filtered_d)
        else:
            # Standard gameplay smoothing with outlier rejection
            if diff_d < 15 or raw_d > 100:
                filtered_d = filtered_d + SMOOTHING * (raw_d - filtered_d)
        
        hand_in_range = MIN_DIST <= filtered_d <= MAX_DIST
        
        display.fill(0)
        
        if game_state == "START":
            display.text("^^ MicroFly ^^", 8, 15)
            display.text("PLACE HAND", 24, 35)
            display.text("IN ZONE", 36, 45)
            if hand_in_range:
                reset_game()

        elif game_state == "PLAYING":
            # Increased threshold for pause to prevent accidental triggers
            if raw_d > 45:
                game_state = "PAUSED"
            else:
                # Map filtered distance to Y position
                target_y = float(HEIGHT - ((filtered_d - MIN_DIST) / (MAX_DIST - MIN_DIST) * (HEIGHT - 12)))
                player_y = max(10.0, min(float(HEIGHT - PLAYER_SIZE), target_y))
                
                move_speed = BASE_SPEED * speed_mult
                for pipe in pipes:
                    pipe[0] -= move_speed
                
                if pipes[0][0] < -PIPE_WIDTH:
                    pipes.pop(0)
                    pipes.append(spawn_pipe(WIDTH))
                    score += 1
                    if score > 0 and score % 5 == 0:
                        speed_mult += 0.1
                
                # Collision Detection
                for pipe in pipes:
                    if pipe[0] < PLAYER_X + PLAYER_SIZE and pipe[0] + PIPE_WIDTH > PLAYER_X:
                        if player_y < pipe[1] or player_y + PLAYER_SIZE > pipe[1] + GAP_SIZE:
                            game_state = "GAMEOVER"
                            prev_high_score = high_score # Save old record for display
                            if score > high_score:
                                high_score = score

            # Drawing
            draw_ui()
            display.fill_rect(PLAYER_X, int(player_y), PLAYER_SIZE, PLAYER_SIZE, 1)
            for pipe in pipes:
                display.fill_rect(int(pipe[0]), 10, PIPE_WIDTH, int(pipe[1] - 10), 1)
                display.fill_rect(int(pipe[0]), int(pipe[1] + GAP_SIZE), PIPE_WIDTH, int(HEIGHT - (pipe[1] + GAP_SIZE)), 1)

        elif game_state == "PAUSED":
            display.text("- PAUSED -", 24, 25)
            display.text("RETURN HAND", 20, 40)
            # Check raw distance to resume immediately
            if MIN_DIST <= raw_d <= MAX_DIST:
                game_state = "PLAYING"

        elif game_state == "GAMEOVER":
            display.text("^^ MicroFly ^^", 8, 5)
            display.text("GAME OVER", 28, 18)
            display.text("SC:{}".format(score), 10, 30)
            display.text("HI:{}".format(prev_high_score), 70, 30)
            display.text("DIFF: {:+}".format(score - prev_high_score), 25, 42)
            display.text("RE-HOLD TO TRY", 8, 54)
            
            # Restart logic: hand must go away then come back
            if raw_d > 45:
                while True:
                    rd = get_distance()
                    if MIN_DIST <= rd <= MAX_DIST:
                        reset_game()
                        break
                    time.sleep(0.1)

        display.show()
        time.sleep(0.01)

finally:
    # Final screen before turning off
    print('Game will be ended soon, you can see your high score on the display.\nThanks for playing!')
    display.fill(0)
    display.text("^^ MicroFly ^^", 8, 10)
    display.text("HIGH SCORE: {}".format(high_score), 8, 30)
    display.text("Thanks4Playing!", 0, 50)
    display.show()
    
    # Wait for 3 seconds
    time.sleep(3.0)
    
    # Turn off the display (clear and show empty)
    display.fill(0)
    display.show()
