import random
import tkinter as tk


WIDTH = 900
HEIGHT = 700
FPS = 60


class SpaceShooter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Space Shooter")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#090d22", highlightthickness=0)
        self.canvas.pack()

        self.keys = set()
        self.running = True

        self.player_speed = 8
        self.player_w = 54
        self.player_h = 36
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 70
        self.player_lives = 3
        self.shoot_cooldown = 0

        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.enemy_spawn_timer = 0
        self.score = 0
        self.frame = 0

        self.stars = []
        for _ in range(120):
            self.stars.append([
                random.randint(0, WIDTH),
                random.randint(0, HEIGHT),
                random.randint(1, 3),
            ])

        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.focus_force()

    def on_key_press(self, event):
        self.keys.add(event.keysym)
        if event.keysym == "Escape":
            self.root.destroy()
            return
        if self.running and event.keysym == "space" and self.shoot_cooldown == 0:
            self.bullets.append({"x": self.player_x, "y": self.player_y - 18, "speed": -14})
            self.shoot_cooldown = 8
        if not self.running and event.keysym.lower() == "r":
            self.reset()

    def on_key_release(self, event):
        if event.keysym in self.keys:
            self.keys.remove(event.keysym)

    def rects_collide(self, a, b):
        return (
            a[0] < b[0] + b[2]
            and a[0] + a[2] > b[0]
            and a[1] < b[1] + b[3]
            and a[1] + a[3] > b[1]
        )

    def reset(self):
        self.running = True
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT - 70
        self.player_lives = 3
        self.shoot_cooldown = 0
        self.bullets.clear()
        self.enemies.clear()
        self.enemy_bullets.clear()
        self.enemy_spawn_timer = 0
        self.score = 0
        self.frame = 0

    def update_player(self):
        if "Left" in self.keys or "a" in self.keys or "A" in self.keys:
            self.player_x -= self.player_speed
        if "Right" in self.keys or "d" in self.keys or "D" in self.keys:
            self.player_x += self.player_speed
        if "Up" in self.keys or "w" in self.keys or "W" in self.keys:
            self.player_y -= self.player_speed
        if "Down" in self.keys or "s" in self.keys or "S" in self.keys:
            self.player_y += self.player_speed

        self.player_x = max(20, min(WIDTH - 20, self.player_x))
        self.player_y = max(HEIGHT - 240, min(HEIGHT - 24, self.player_y))

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def spawn_enemy(self):
        x = random.randint(30, WIDTH - 30)
        y = random.randint(-200, -40)
        speed = random.uniform(2.0, 3.8 + (self.score * 0.005))
        sway = random.uniform(0.5, 1.8)
        self.enemies.append(
            {
                "x": float(x),
                "y": float(y),
                "speed": speed,
                "phase": random.random() * 6.28,
                "amp": random.randint(15, 45),
                "sway": sway,
                "shoot": random.randint(35, 120),
            }
        )

    def update_enemies(self):
        self.enemy_spawn_timer -= 1
        spawn_interval = max(15, 60 - self.score // 10)
        if self.enemy_spawn_timer <= 0:
            self.spawn_enemy()
            self.enemy_spawn_timer = spawn_interval

        for enemy in self.enemies:
            enemy["y"] += enemy["speed"]
            enemy["x"] += random.uniform(-enemy["sway"], enemy["sway"])
            enemy["x"] += (random.random() - 0.5) * 0.8
            enemy["x"] = max(24, min(WIDTH - 24, enemy["x"]))

            enemy["shoot"] -= 1
            if enemy["shoot"] <= 0 and random.random() < 0.35:
                self.enemy_bullets.append({"x": enemy["x"], "y": enemy["y"] + 14, "speed": 7})
                enemy["shoot"] = random.randint(50, 140)

    def update_projectiles(self):
        for bullet in self.bullets:
            bullet["y"] += bullet["speed"]
        for bullet in self.enemy_bullets:
            bullet["y"] += bullet["speed"]

        self.bullets = [b for b in self.bullets if -30 <= b["y"] <= HEIGHT + 30]
        self.enemy_bullets = [b for b in self.enemy_bullets if -30 <= b["y"] <= HEIGHT + 30]

    def handle_collisions(self):
        player_rect = (
            self.player_x - self.player_w // 2,
            self.player_y - self.player_h // 2,
            self.player_w,
            self.player_h,
        )

        alive_enemies = []
        for enemy in self.enemies:
            enemy_rect = (enemy["x"] - 22, enemy["y"] - 16, 44, 32)
            enemy_hit = False

            new_bullets = []
            for bullet in self.bullets:
                bullet_rect = (bullet["x"] - 3, bullet["y"] - 10, 6, 20)
                if self.rects_collide(bullet_rect, enemy_rect):
                    enemy_hit = True
                    self.score += 10
                else:
                    new_bullets.append(bullet)
            self.bullets = new_bullets

            if enemy_hit:
                continue

            if self.rects_collide(player_rect, enemy_rect):
                self.player_lives -= 1
                continue

            if enemy["y"] > HEIGHT + 30:
                self.player_lives -= 1
                continue

            alive_enemies.append(enemy)

        self.enemies = alive_enemies

        new_enemy_bullets = []
        for bullet in self.enemy_bullets:
            bullet_rect = (bullet["x"] - 3, bullet["y"] - 10, 6, 20)
            if self.rects_collide(bullet_rect, player_rect):
                self.player_lives -= 1
            else:
                new_enemy_bullets.append(bullet)
        self.enemy_bullets = new_enemy_bullets

        if self.player_lives <= 0:
            self.running = False

    def draw_background(self):
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#090d22", outline="")
        for star in self.stars:
            star[1] += star[2]
            if star[1] > HEIGHT:
                star[0] = random.randint(0, WIDTH)
                star[1] = -5
                star[2] = random.randint(1, 3)
            color = "#9ab0ff" if star[2] == 1 else "#c9d7ff" if star[2] == 2 else "#ffffff"
            self.canvas.create_oval(star[0], star[1], star[0] + star[2], star[1] + star[2], fill=color, outline=color)

    def draw_player(self):
        x = self.player_x
        y = self.player_y
        points = [
            x,
            y - self.player_h // 2,
            x + self.player_w // 2,
            y + self.player_h // 2,
            x,
            y + self.player_h // 4,
            x - self.player_w // 2,
            y + self.player_h // 2,
        ]
        self.canvas.create_polygon(points, fill="#48e1ff", outline="#8ef0ff", width=2)
        self.canvas.create_oval(x - 7, y - 8, x + 7, y + 6, fill="#ecf7ff", outline="")

    def draw_enemies(self):
        for enemy in self.enemies:
            x = enemy["x"]
            y = enemy["y"]
            self.canvas.create_rectangle(x - 22, y - 16, x + 22, y + 16, fill="#ff5f76", outline="#ff9db0", width=2)
            self.canvas.create_rectangle(x - 10, y - 6, x + 10, y + 6, fill="#ffd3da", outline="")

    def draw_bullets(self):
        for bullet in self.bullets:
            self.canvas.create_rectangle(
                bullet["x"] - 3,
                bullet["y"] - 10,
                bullet["x"] + 3,
                bullet["y"] + 10,
                fill="#7cffb8",
                outline="",
            )
        for bullet in self.enemy_bullets:
            self.canvas.create_rectangle(
                bullet["x"] - 3,
                bullet["y"] - 10,
                bullet["x"] + 3,
                bullet["y"] + 10,
                fill="#ffd86a",
                outline="",
            )

    def draw_hud(self):
        self.canvas.create_text(18, 16, anchor="nw", fill="#e7efff", font=("Consolas", 18, "bold"), text=f"Score: {self.score}")
        self.canvas.create_text(
            WIDTH - 18,
            16,
            anchor="ne",
            fill="#e7efff",
            font=("Consolas", 18, "bold"),
            text=f"Lives: {self.player_lives}",
        )
        if self.running:
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT - 18,
                fill="#aebcf0",
                font=("Consolas", 14),
                text="Move: WASD / Arrows    Shoot: Space    Quit: Esc",
            )
        else:
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 - 20,
                fill="#ffffff",
                font=("Consolas", 52, "bold"),
                text="GAME OVER",
            )
            self.canvas.create_text(
                WIDTH // 2,
                HEIGHT // 2 + 30,
                fill="#cfd9ff",
                font=("Consolas", 20),
                text="Press R to restart or Esc to quit",
            )

    def tick(self):
        self.frame += 1
        if self.running:
            self.update_player()
            self.update_enemies()
            self.update_projectiles()
            self.handle_collisions()

        self.canvas.delete("all")
        self.draw_background()
        self.draw_bullets()
        self.draw_enemies()
        self.draw_player()
        self.draw_hud()

        delay = int(1000 / FPS)
        self.root.after(delay, self.tick)

    def run(self):
        self.tick()
        self.root.mainloop()


def main():
    game = SpaceShooter()
    game.run()


if __name__ == "__main__":
    main()
