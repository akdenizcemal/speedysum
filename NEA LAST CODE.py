# Import necessary libraries
import tkinter as tk  # GUI library
from tkinter import messagebox  # For pop-up messages
import json  # For storing user data
import os  # For file handling
import pygame  # Game framework
import sys  # For system exit
import random  # For generating random questions and answers
import time  # For time tracking

# ---------- Credentials Management ----------

# File to store user data
CREDENTIALS_FILE = 'users.json'
current_user = None  # To keep track of the logged-in user

# Load existing user credentials from JSON file
def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            return json.load(file)
    return {}

# Save updated credentials back to JSON file
def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file)


# ---------- Highway Background Animation ----------

class Highway:
    def __init__(self, width, height, speed=300):
        self.width = width
        self.height = height
        self.speed = speed
        self.dash_width = 40
        self.dash_height = 10
        self.dash_gap = 60
        self.num_dashes = width // (self.dash_width + self.dash_gap) + 2
        center_y = height // 2 - self.dash_height // 2
        # Initial positions for dashes on the road
        self.dashes = [
            [i * (self.dash_width + self.dash_gap) - self.dash_width, center_y]
            for i in range(self.num_dashes)
        ]

    def update(self, dt):
        # Move dashes to the left and reset when off screen
        for dash in self.dashes:
            dash[0] -= self.speed * dt / 1000
            if dash[0] < -self.dash_width:
                dash[0] = self.width

    def draw(self, screen):
        # Draw background road and dashes
        screen.fill((50, 50, 50))
        b_h = 20
        pygame.draw.rect(screen, (255, 255, 255), (0, self.height//4 - b_h//2, self.width, b_h))
        pygame.draw.rect(screen, (255, 255, 255), (0, 3*self.height//4 - b_h//2, self.width, b_h))
        for x, y in self.dashes:
            pygame.draw.rect(screen, (255, 255, 255), (x, y, self.dash_width, self.dash_height))


# ---------- Player (Car) Class ----------

class Player:
    def __init__(self, x, y, speed=10):
        self.x = x
        self.y = y
        self.speed = speed  # Controls how fast the car moves up/down
        self.body_width = 60
        self.body_height = 20
        self.roof_height = 15
        self.wheel_radius = 6
        self.rect = pygame.Rect(self.x, self.y, self.body_width, self.roof_height + self.body_height)

    def update(self, move_y=0):
        # Move vertically and keep within screen bounds
        self.y += move_y
        if self.y < 0:
            self.y = 0
        elif self.y > 600 - (self.roof_height + self.body_height):
            self.y = 600 - (self.roof_height + self.body_height)
        self.rect.y = self.y

    def draw(self, screen):
        # Draw the car with a body, roof, window, and wheels
        body_rect = pygame.Rect(self.x, self.y + self.roof_height, self.body_width, self.body_height)
        pygame.draw.rect(screen, (220, 10, 60), body_rect)
        roof_points = [
            (self.x + self.body_width * 0.2, self.y + self.roof_height),
            (self.x + self.body_width * 0.35, self.y),
            (self.x + self.body_width * 0.65, self.y),
            (self.x + self.body_width * 0.8, self.y + self.roof_height)
        ]
        pygame.draw.polygon(screen, (178, 34, 34), roof_points)
        window_rect = pygame.Rect(self.x + self.body_width * 0.4, self.y + 2, self.body_width * 0.2, self.roof_height - 4)
        pygame.draw.rect(screen, (5, 206, 235), window_rect)
        # Wheels
        left_center = (int(self.x + self.body_width * 0.25), int(self.y + self.roof_height + self.body_height))
        right_center = (int(self.x + self.body_width * 0.75), int(self.y + self.roof_height + self.body_height))
        pygame.draw.circle(screen, (0, 0, 0), left_center, self.wheel_radius + 3)
        pygame.draw.circle(screen, (0, 0, 0), right_center, self.wheel_radius + 3)
        pygame.draw.circle(screen, (192, 192, 192), left_center, self.wheel_radius)
        pygame.draw.circle(screen, (192, 192, 192), right_center, self.wheel_radius)


# ---------- Math Question Generator ----------

class Question:
    def __init__(self, difficulty=1):
        self.num1 = random.randint(1, 10 * difficulty)
        self.num2 = random.randint(1, 10 * difficulty)
        self.operator = random.choice(['+', '-', '*', '/'])
        if self.operator == '/':
            # Ensure division results in integer
            self.num2 = random.randint(1, 10 * difficulty)
            self.num1 = self.num2 * random.randint(1, 10)
        expr = f"{self.num1} {self.operator} {self.num2}"
        self.answer = round(eval(expr))
        self.text = f"{expr} = ?"
        # Generate 3 options (1 correct + 2 random)
        opts = {self.answer}
        while len(opts) < 3:
            opts.add(random.randint(self.answer - 10 * difficulty, self.answer + 10 * difficulty))
        self.options = list(opts)
        random.shuffle(self.options)


# ---------- Main Game Function ----------

def maind():
    pygame.init()
    screen_width, screen_height = 1200, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("speedy sums")
    clock = pygame.time.Clock()

    # Initialize game elements
    highway = Highway(screen_width, screen_height)
    player = Player(100, screen_height // 2, speed=10)
    lives, score = 3, 0
    difficulty = 1
    current_question = Question(difficulty)
    column_width = 200
    box_x = screen_width
    font = pygame.font.SysFont(None, 36)

    # Feedback variables
    show_wrong = False
    show_correct = False
    feedback_start = 0
    feedback_duration = 1000  # ms

    box_gap = 10
    BOX_COLOR = (100, 200, 255)

    running = True
    paused = False
    start_time = time.time()

    # Main game loop
    while running:
        dt = clock.tick(60)  # Cap to 60 FPS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused

        # Pause screen
        if paused:
            screen.fill((0, 0, 0))
            screen.blit(font.render("Paused - Press 'P' to Resume", True, (255, 255, 0)), (screen_width//2 - 200, screen_height//2))
            pygame.display.flip()
            continue

        elapsed_time = time.time() - start_time
        game_speed = 5 + elapsed_time / 10  # Increase speed over time

        # Handle input
        keys = pygame.key.get_pressed()
        move_y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * player.speed
        player.update(move_y)

        # Move boxes leftward
        box_x -= game_speed
        if box_x + column_width < 0:
            box_x = screen_width
            difficulty = 1 + int(elapsed_time // 20)
            current_question = Question(difficulty)

        # Check collisions with answer boxes
        correct_index = current_question.options.index(current_question.answer)
        for i, option in enumerate(current_question.options):
            box_top = i * ((screen_height - 2 * box_gap) // 3 + box_gap)
            box_height = (screen_height - 2 * box_gap) // 3
            box_rect = pygame.Rect(box_x, box_top + box_gap, column_width, box_height)
            if player.rect.colliderect(box_rect):
                if i == correct_index:
                    score += 1
                    show_correct = True
                else:
                    lives -= 1
                    show_wrong = True
                feedback_start = pygame.time.get_ticks()
                box_x = screen_width
                current_question = Question(difficulty)
                break

        # Draw everything
        highway.update(dt)
        highway.draw(screen)
        screen.blit(font.render("Press P to Pause", True, (200, 200, 200)), (screen_width - 180, 10))
        player.draw(screen)

        # Draw answer boxes
        for i, option in enumerate(current_question.options):
            box_top = i * ((screen_height - 2 * box_gap) // 3 + box_gap)
            box_height = (screen_height - 2 * box_gap) // 3
            box_rect = pygame.Rect(box_x, box_top + box_gap, column_width, box_height)
            pygame.draw.rect(screen, BOX_COLOR, box_rect)
            text_surf = font.render(str(option), True, (0, 0, 0))
            screen.blit(text_surf, (box_x + 50, box_top + box_gap + box_height // 2 - 18))

        # Show feedback icons
        now = pygame.time.get_ticks()
        if show_wrong and now - feedback_start < feedback_duration:
            pygame.draw.circle(screen, (255, 0, 0), (screen_width // 2, 50), 30)
        else:
            show_wrong = False
        if show_correct and now - feedback_start < feedback_duration:
            pygame.draw.circle(screen, (0, 255, 0), (screen_width // 2, 50), 30)
        else:
            show_correct = False

        # Display score, lives, and question
        screen.blit(font.render(f"Lives: {lives}", True, (255, 255, 255)), (20, 20))
        screen.blit(font.render(f"Score: {score}", True, (255, 255, 255)), (20, 60))
        screen.blit(font.render(current_question.text, True, (255, 255, 255)), (300, 20))

        pygame.display.flip()
        if lives <= 0:
            running = False

    # Save high score if it's a new record
    creds = load_credentials()
    if current_user in creds and score > creds[current_user].get("max_score", 0):
        creds[current_user]["max_score"] = score
        save_credentials(creds)

    # Game Over screen
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    maind()
                elif event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
        screen.fill((0, 0, 0))
        screen.blit(font.render(f"Game Over! Final Score: {score}", True, (255, 0, 0)), (200, 150))
        screen.blit(font.render("Press R to Replay or Q to Quit", True, (255, 255, 255)), (200, 200))
        pygame.display.flip()


# ---------- Tkinter GUI Functions ----------

def signup():
    username = entry_username.get()
    password = entry_password.get()
    creds = load_credentials()
    if username in creds:
        messagebox.showerror("error", "username already exists")
    elif len(password) < 4:
        messagebox.showerror("error", "password must be at least 4 characters long")
    else:
        creds[username] = {"password": password, "max_score": 0}
        save_credentials(creds)
        messagebox.showinfo("success", "signup successful")

def login():
    global current_user
    username = entry_username.get()
    password = entry_password.get()
    creds = load_credentials()
    if username in creds and creds[username]["password"] == password:
        current_user = username
        messagebox.showinfo("success", "login successful")
        root.destroy()
        show_start_game_screen()
    else:
        messagebox.showerror("error", "invalid username or password")

def show_start_game_screen():
    start_root = tk.Tk()
    start_root.title("Speedy Sums - Start Game")
    start_root.geometry("500x400")
    tk.Label(start_root, text="Speedy Sums", font=("Comic Sans MS", 32, "bold"), fg="magenta").pack(pady=20)
    creds = load_credentials()
    max_score = creds.get(current_user, {}).get("max_score", 0)
    tk.Label(start_root, text=f"Max Score: {max_score}", font=("Arial", 18)).pack(pady=20)
    tk.Button(start_root, text="Start Game", font=("Arial", 14), command=lambda: [start_root.destroy(), maind()]).pack(pady=20)
    start_root.mainloop()


# ---------- Launch Login GUI ----------

root = tk.Tk()
root.title("Speedy Sums Login")
root.geometry("500x400")

tk.Label(root, text="Speedy Sums", font=("Comic Sans MS", 32, "bold"), fg="magenta").pack(pady=20)
tk.Label(root, text="Username:").pack()
entry_username = tk.Entry(root)
entry_username.pack(pady=5)
tk.Label(root, text="Password:").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack(pady=5)

tk.Button(root, text="Login", command=login).pack(pady=5)
tk.Button(root, text="Signup", command=signup).pack(pady=5)
root.mainloop()

