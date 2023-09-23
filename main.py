# Import required modules
import sys
import os
import pygame
from random import randint, choice
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    KEYUP,
    K_RETURN,
    K_SPACE,
    QUIT,
)


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller.
    URL: https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS2  # Adjust to MEIPASS2 if not working
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# Initialize pygame and pygame mixer
pygame.init()
pygame.mixer.init()


# Set the screen
WIDTH = 800
HEIGHT = 580
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Markanov Tipkobrz")


# Fonts - font, size, bold, italic
LETTER_FONT = pygame.font.SysFont("Times New Roman", 25, True, False)
TITLE_FONT = pygame.font.SysFont("Calibri", 25, True, True)
END_GAME_FONT = pygame.font.SysFont("Calibri", 30, True, True)
GAME_STATUS_FONT = pygame.font.SysFont("Calibri", 20, True, False)
SCORE_FONT = pygame.font.SysFont("Calibri", 25, True, False)


# Balloon class
class Balloon(pygame.sprite.Sprite):
    def __init__(self):
        super(Balloon, self).__init__()
        self.balloon_icons = choice(letters)
        # Balloon radius and speed
        self.radius = 25
        self.speed = 2
        # Draw Balloon as circles
        self.surf = pygame.Surface((2 * self.radius, 2 * self.radius))
        self.surf.set_colorkey(BLACK)
        pygame.draw.circle(self.surf, YELLOW,
                           (self.radius, self.radius), self.radius)
        # Render the font for letters on to the balloon surface, anti-aliasing, black color
        text = LETTER_FONT.render(self.balloon_icons, 1, BLACK)
        # Draw the font on the balloon surface
        self.surf.blit(text, (self.radius - text.get_width() // 2,
                              self.radius - text.get_height() // 2))
        self.rect = self.surf.get_rect()

    def update(self):
        global score
        self.rect.move_ip(0, self.speed)
        if self.rect.top > HEIGHT:
            self.kill()
            score -= 1
        # Update the x-coordinate based on lane
        self.rect.centerx = self.distance * balloon_distance + balloon_distance // 2

    def generate_new_balloon(self):
        # Set a random lane for the balloon
        self.distance = randint(0, x_distance - 1)
        # Set the position of the balloon based on the lane
        self.rect.centerx = self.distance * balloon_distance + balloon_distance // 2
        
        # Add an offset to the vertical position to increase the spacing between balloons
        offset_y = randint(150, 350)
        self.rect.bottom = 0 - offset_y


# Load music and sound files
music = pygame.mixer.music.load(resource_path("music\\Mama_ŠČ.ogg"))
balloon_pop_sound = pygame.mixer.Sound(resource_path("music\\pop.ogg"))
# Ensure that the song keeps playing
pygame.mixer.music.play(-1)

# Set the base volume for balloon popping sound
balloon_pop_sound.set_volume(1.0)

# Set the background music volume
pygame.mixer.music.set_volume(0.5)


# Creating a custom event for adding a new enemy
ADDBALLOON = pygame.USEREVENT + 1
pygame.time.set_timer(ADDBALLOON, 150)
# Limit the maximum number of balloons on the screen
MAX_BALLOONS = 10

# Create groups to hold balloon sprites
balloons = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

# Letters
letters = ["a", "b", "c", "č", "ć", "d", "dž", "đ", "e", "f", "g", "h", "i", "j", "k",
           "l", "lj", "m", "n", "nj", "o", "p", "r", "s", "š", "t", "u", "v", "z", "ž"]

# Game variables
score = 0
level = 1
max_level = 10
balloon_distance = 50  # Distance between each balloon
x_distance = WIDTH // balloon_distance  # Calculate the x distance
paused = False
won = False
lost = False


def add_balloon(balloons, all_sprites):
    global paused
    if not paused:
        # Check if the maximum number of balloons is reached
        if len(balloons) <= MAX_BALLOONS:
            new_balloon = Balloon()
            new_balloon.generate_new_balloon()
            while pygame.sprite.spritecollideany(new_balloon, balloons):
                new_balloon.generate_new_balloon()
            balloons.add(new_balloon)
            all_sprites.add(new_balloon)


# Function to check if the pressed key matches the balloon's letter
def pop_balloon(pressed_key):
    global score
    for balloon in balloons:
        if balloon.balloon_icons.lower() == pressed_key:
            balloon.kill()
            score += 1
            balloon_pop_sound.play()


def clear_balloons():
    balloons.empty()  # Clear the balloons group
    all_sprites.empty()  # Clear the all_sprites group


def advance_level():
    global level, score, MAX_BALLOONS
    level = next_level
    MAX_BALLOONS += 1
    score = 0  # Reset the score
    for balloon in balloons:
        balloon.speed += balloon.speed * 0.5
    clear_balloons()
    game()


def reset_game():
    global level, score, MAX_BALLOONS
    level = 1
    score = 0  # Reset the score
    MAX_BALLOONS = 10
    clear_balloons()
    game()


def display_score():
    # Render the text. "True" for anti-aliasing text. Yellow color
    text = SCORE_FONT.render(f"Score: {score}", True, YELLOW)
    # Put the image of the text on the screen at 10x10
    screen.blit(text, (0, 5))


def draw():
    screen.fill(BLACK)

    # Draw title
    # Render the title font on to the screen, anti-aliasing, red color
    text = TITLE_FONT.render("Markanov Tipkobrz", 1, RED)
    # Draw font onto the screen
    # x-centered, y-5
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 5))

    # Draw balloons on the screen
    for balloon in balloons:
        screen.blit(balloon.surf, balloon.rect)

    # Display the score
    display_score()

    # Draw the message about current level
    # Render the font for word on to the screen, anti-aliasing, blue color
    text = GAME_STATUS_FONT.render(
        f"Level: {level}", 1, BLUE)
    # Draw font onto the screen
    screen.blit(text, (WIDTH - text.get_width() - 5, 5))

    pygame.display.update()


def display_welcome_message(message):
    screen.fill(BLACK)
    lines = [line.strip() for line in message.split("\n")]
    line_height = END_GAME_FONT.get_height()
    y_position = (HEIGHT - line_height * len(lines)) // 2

    for line in lines:
        line_text = END_GAME_FONT.render(line, 1, YELLOW)
        x_position = (WIDTH - line_text.get_width()) // 2
        screen.blit(line_text, (x_position, y_position))
        y_position += line_height

    pygame.display.update()

    # Shorter time delay for the welcome message
    pygame.time.delay(100)


def display_end_message(message):
    pygame.time.delay(2500)
    screen.fill(BLACK)
    lines = [line.strip() for line in message.split("\n")]
    line_height = END_GAME_FONT.get_height()
    y_position = (HEIGHT - line_height * len(lines)) // 2

    for line in lines:
        line_text = END_GAME_FONT.render(line, 1, YELLOW)
        x_position = (WIDTH - line_text.get_width()) // 2
        screen.blit(line_text, (x_position, y_position))
        y_position += line_height

    pygame.display.update()


def game():
    global running, paused, level, next_level, won, lost
    FPS = 60
    clock = pygame.time.Clock()
    running = True

    # Reset game flags when starting a new game
    won = False
    lost = False

    prev_keys_pressed = {} # Define pressed_keys

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            # Also quit if user presses the ESCAPE key
            keys = pygame.key.get_pressed()
            if keys[K_ESCAPE]:
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                        for balloon in balloons:
                            balloon.speed = 0
                    else:
                        pygame.mixer.music.unpause()
                        for balloon in balloons:
                            balloon.speed = 2  # Restore original speed

                # Get the pressed keys
                if not paused:
                    pressed_key = event.unicode.lower()
                    # Check if the pressed key is a valid letter
                    if pressed_key in letters:
                        # Handle "lj", "nj" and "dž"
                        if pressed_key == "l":
                            prev_keys_pressed["l"] = True
                        elif pressed_key == "j" and prev_keys_pressed.get("l"):
                            pressed_key = "lj"
                        elif pressed_key == "n":
                            prev_keys_pressed["n"] = True
                        elif pressed_key == "j" and prev_keys_pressed.get("n"):
                            pressed_key = "nj"
                        elif pressed_key == "d":
                            prev_keys_pressed["d"] = True
                        elif pressed_key == "ž" and prev_keys_pressed.get("d"):
                            pressed_key = "dž"
                        else:
                            prev_keys_pressed.clear()  # Clear any previous combinations

                        # Remove the balloon for which the key had been pressed
                        pop_balloon(pressed_key)

            # Clear any previous combinations if a single key is pressed
            elif event.type == KEYUP:
                prev_keys_pressed.clear()

        if not paused:
            add_balloon(balloons, all_sprites)
            balloons.update()

        draw()

        # Check if the user had won or lost
        if score >= 10:
            won = True
        elif score <= - 10:
            lost = True

        if won or lost:
            if won:
                if level < max_level:
                    next_level = level + 1
                    message = f"""You have reached level: {next_level}!
                          Press ENTER if you want to continue playing,
                          or press \"ESCAPE\" if you want to quit."""
                elif level == max_level:
                    message = f"""You have WON the game!
                            Congratulations! You are a true typing master!
                            Press ENTER if you want to play again,
                            or press \"ESCAPE\" if you want to quit."""
            if lost:
                message = f"""You have LOST!
                          Press ENTER if you want to play again,
                          or press \"ESCAPE\" if you want to quit."""

            display_end_message(message)

            # Wait for player to click or press ESCAPE
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == KEYDOWN and event.key == K_RETURN:
                        waiting = False
                        if won:
                            if level < max_level:
                                advance_level()
                            elif level == max_level:
                                reset_game()
                        if lost:
                            reset_game()
                    elif event.type == KEYDOWN and event.key == K_ESCAPE:
                            running = False
                            waiting = False

    pygame.mixer.quit()
    pygame.quit()


def main():
    global running
    running = True

    # Display the welcome message
    message = """Welcome to the Markanov Tipkobrz game.
                The goal is to type the incoming letters.
                For every typed letter, you get 1 score
                and for every letter passing the screen,
                1 score is being deducted.
                Press "ENTER" to start the game."""
    display_welcome_message(message)
    
    while running:
        # Wait for the player to press ENTER
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_RETURN:
                    waiting = False
                elif event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    running = False
                    waiting = False       
        
        if running:
            game()

    pygame.quit()
    pygame.mixer.quit()


if __name__ == "__main__":
    main()