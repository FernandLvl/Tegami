from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QTimer, QUrl
from utils.i18n import tr  # función para traducir
from PySide6.QtGui import QFont, QPainter, QLinearGradient, QColor
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl
from config.config import get_setting, save_setting

import random
import os
import math
import time

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("menu_about"))
        self.setMinimumWidth(300)

        self.click_count = 0
        self.close_timer = QTimer()
        self.close_timer.setInterval(200)  # 1.5 segundos para resetear
        self.close_timer.setSingleShot(True)
        self.close_timer.timeout.connect(self.reset_clicks)

        layout = QVBoxLayout(self)

        # título de la app
        title_label = QLabel("<b>Tegami - Tag Gallery App</b>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # información del desarrollador
        dev_label = QLabel(tr("about_dev_info"))
        dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_label)

        # versión o estado actual
        version_label = QLabel(tr("about_version"))
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # botón para cerrar
        close_btn = QPushButton(tr("about_button_close"))
        close_btn.clicked.connect(self.handle_close_click)
        layout.addWidget(close_btn)

    def handle_close_click(self):
        self.click_count += 1
        self.close_timer.start()  # reinicia el tiempo cada clic

        if self.click_count >= 5:
            self.close_timer.stop()
            self.launch_mini_game()
            self.click_count = 0
        else:
            # si no llega a 5 clics, cerrar después del tiempo
            if not self.close_timer.isActive():
                self.close()

    def reset_clicks(self):
        # si después de 1.5 segundos no se siguió haciendo clic, cerrar
        if self.click_count < 5:
            self.close()
        self.click_count = 0

    def launch_mini_game(self):
        game = MiniGameDialog(self)
        game.exec()

class MiniGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("mini_game_title"))
        self.setFixedSize(300, 400)
        # QSS solo para los widgets, el fondo lo pintaremos nosotros

        self.score = 0
        self.lives = 10
        self.level = 1
        self.high_score = int(get_setting("game_high_score") or 0)

        # --- NUEVO: Etiquetas de puntaje y vidas ---
        self.score_label = QLabel(f"Puntaje: {self.score}", self)
        self.score_label.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        self.score_label.move(10, 10)

        self.lives_label = QLabel(f"Vidas: {self.lives}", self)
        self.lives_label.setStyleSheet("color: white; font-size: 14px; background: transparent;")
        self.lives_label.move(200, 10)
        # ------------------------------------------

        # --- NUEVO: Etiqueta para el estado de power-ups ---
        self.slowdown_label = QLabel("", self)
        self.slowdown_label.setStyleSheet("color: #aef; font-size: 14px; background: transparent;")
        self.slowdown_label.move(120, 10)  # Ajusta la posición según tu diseño
        self.slowdown_label.hide()
        # ------------------------------------------

        self.fish_emojis = [
                "🐟",  # pez común
                "🐠",  # pez tropical
                "🐡",  # pez globo
                "🦐",  # camarón
                "🦑",  # calamar
                "🦞",  # langosta
                "🦀",  # cangrejo
                "🐙",  # pulpo
                "🪼",  # medusa
            ]
        self.bad_emojis = [
                "💣",  # bomba
                "🪸",  # coral venenoso
                "🧊",  # hielo
                "🪨",  # roca
                "☠️",  # veneno/muerte
                "🦴",  # hueso
                "🪝",  # anzuelo metálico
            ]

        self.powerup_emojis = ["❤️", "🕑"]
        self.powerup_chance = 0.08    # 8% de probabilidad de powerup por item generado

        self.dolphin = QLabel("🐬", self)
        self.dolphin.setFont(QFont("Arial", 24))
        self.dolphin.setAlignment(Qt.AlignCenter)
        self.dolphin.setStyleSheet("background: transparent;")  # <-- Fondo transparente
        self.dolphin.move(130, 350)
        self.dolphin_pos = 1  # 0 izquierda, 1 centro, 2 derecha

        self.falling_items = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(100)

        self.spawn_timer = QTimer(self)
        self.spawn_timer.timeout.connect(self.spawn_item)
        self.spawn_timer.start(1000)

        self.level_timer = QTimer(self)
        self.level_timer.timeout.connect(self.increase_difficulty)
        self.level_timer.start(5000)  # Cada 5 segundos sube la dificultad

        # Ruta base de sonidos
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        SOUND_PATH = os.path.join(CURRENT_DIR, "..", "resources", "sounds")

        # Listas de sonidos
        self.death_sounds = [os.path.join(SOUND_PATH, f"dd{i}.wav") for i in (1, 2)]
        self.eat_sounds = [os.path.join(SOUND_PATH, f"de{i}.wav") for i in range(1, 4)]
        self.hurt_sounds = [os.path.join(SOUND_PATH, f"dh{i}.wav") for i in range(1, 4)]
        self.idle_sounds = [os.path.join(SOUND_PATH, f"di{i}.wav") for i in range(1, 7)]
        self.bubble_sounds = [os.path.join(SOUND_PATH, f"bbbl{i}.wav") for i in range(1, 7)]

        self.sound_effect = QSoundEffect(self)
        self.sound_effect.setVolume(0.5)

        # Timer para sonidos idle
        self.idle_timer = QTimer(self)
        self.idle_timer.timeout.connect(self.play_idle_sound)
        self.idle_timer.start(random.randint(3000, 5000))  # 3-5 segundos

        # Timer para sonidos de burbujas
        self.bubble_sound_timer = QTimer(self)
        self.bubble_sound_timer.timeout.connect(self.play_bubble_sound)
        self.bubble_sound_timer.start(random.randint(1200, 2500))  # 1.2 - 2.5 segundos

        # Variables para animar el gradiente
        self.gradient_phase = 0
        self.gradient_timer = QTimer(self)
        self.gradient_timer.timeout.connect(self.update_gradient)
        self.gradient_timer.start(40)  # ~25 FPS

        # --- Burbujas animadas ---
        self.bubbles = []
        self.last_bubble_time = time.time()
        self.max_bubbles = 15  # Puedes ajustar la cantidad máxima de burbujas

        self.setFocusPolicy(Qt.StrongFocus)

    def increase_difficulty(self):
        """Aumenta la dificultad del juego reduciendo los intervalos de los temporizadores."""
        self.level += 1
        # Reduce el intervalo de caída (mínimo 30 ms)
        new_update_interval = max(30, 100 - self.level * 10)
        self.timer.setInterval(new_update_interval)
        # Reduce el intervalo de aparición de items (mínimo 300 ms)
        new_spawn_interval = max(300, 1000 - self.level * 80)
        self.spawn_timer.setInterval(new_spawn_interval)

    def spawn_item(self):
        # Decide si aparece un powerup (probabilidad baja)
        if random.random() < self.powerup_chance:
            emoji = random.choice(self.powerup_emojis)
            is_powerup = True
        else:
            emoji = random.choice(self.fish_emojis + self.bad_emojis * 1)
            is_powerup = False

        item = QLabel(emoji, self)
        item.setFont(QFont("Arial", 24))
        item.setAlignment(Qt.AlignCenter)
        item.setStyleSheet("background: transparent;")
        pos = random.randint(0, 2)
        x = [50, 130, 210][pos]
        item.move(x, 0)
        item.pos_index = pos
        item.is_powerup = is_powerup
        self.falling_items.append(item)
        item.show()

    def play_sound(self, sound_list):
        """Reproduce un sonido aleatorio de la lista dada, permitiendo superposición."""
        sound_file = random.choice(sound_list)
        effect = QSoundEffect(self)
        effect.setSource(QUrl.fromLocalFile(sound_file))
        effect.setVolume(0.5)
        effect.play()
        # Mantener referencia para evitar que se destruya antes de tiempo
        if not hasattr(self, "_active_sounds"):
            self._active_sounds = []
        self._active_sounds.append(effect)
        # Limpiar referencia cuando termine, sin error si ya no está
        def cleanup():
            try:
                self._active_sounds.remove(effect)
            except ValueError:
                pass
        effect.playingChanged.connect(lambda: cleanup() if not effect.isPlaying() else None)

    def play_idle_sound(self):
        self.play_sound(self.idle_sounds)
        # Reinicia el timer con un nuevo intervalo aleatorio
        self.idle_timer.start(random.randint(3000, 5000))

    def play_bubble_sound(self):
        self.play_sound(self.bubble_sounds)
        # Reinicia el timer con un nuevo intervalo aleatorio
        self.bubble_sound_timer.start(random.randint(1200, 2500))

    def update_game(self):
        for item in self.falling_items[:]:
            item.move(item.x(), item.y() + 20)

            if item.y() >= 340:
                if item.pos_index == self.dolphin_pos:
                    if getattr(item, "is_powerup", False):
                        self.apply_powerup(item.text())
                    elif item.text() in self.fish_emojis:
                        self.score += 1
                        self.play_sound(self.eat_sounds)
                    else:
                        self.lives -= 1
                        self.play_sound(self.hurt_sounds)
                else:
                    if item.text() in self.fish_emojis:
                        self.lives -= 1
                        self.play_sound(self.hurt_sounds)
                item.deleteLater()
                self.falling_items.remove(item)

        # Actualiza los labels
        self.score_label.setText(tr("game_score_label").format(score=self.score))
        self.score_label.adjustSize()
        self.lives_label.setText(tr("game_lives_label").format(lives=self.lives))
        self.lives_label.adjustSize()

        if self.lives <= 0:
            self.timer.stop()
            self.spawn_timer.stop()
            self.idle_timer.stop()
            self.show_game_over()

    def show_game_over(self):
        # Actualiza el high score si es necesario
        if self.score > self.high_score:
            self.high_score = self.score
            save_setting("game_high_score", self.high_score)
            new_record = True
        else:
            new_record = False

        self.play_sound(self.death_sounds)
        msg = QDialog(self)
        msg.setWindowTitle(tr("game_over"))
        msg.setFixedSize(220, 160)
        layout = QVBoxLayout(msg)
        label = QLabel(tr("game_over_message").format(score=self.score), msg)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Mostrar el puntaje máximo
        high_score_label = QLabel(
            tr("game_high_score_label").format(high_score=self.high_score), msg
        )
        high_score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(high_score_label)

        # Mensaje de nuevo récord (opcional)
        if new_record:
            record_label = QLabel(tr("game_new_record"), msg)
            record_label.setAlignment(Qt.AlignCenter)
            record_label.setStyleSheet("color: gold; font-weight: bold;")
            layout.addWidget(record_label)

        retry_btn = QPushButton(tr("game_button_retry"), msg)
        retry_btn.setStyleSheet("margin-top: 10px;")
        layout.addWidget(retry_btn)
        retry_btn.clicked.connect(lambda: (msg.accept(), self.restart_game()))

        close_btn = QPushButton(tr("game_button_close"), msg)
        layout.addWidget(close_btn)
        close_btn.clicked.connect(lambda: (msg.accept(), self.close()))

        msg.exec()

    def restart_game(self):
        # Elimina todos los labels de los objetos en caída
        for item in getattr(self, "falling_items", []):
            item.deleteLater()
        self.falling_items.clear()
        # Elimina todas las burbujas visuales si usas labels para ellas (opcional)
        self.bubbles.clear()
        # Reinicia los valores y timers del minijuego
        self.score = 0
        self.lives = 10
        self.level = 1
        self.score_label.setText(tr("game_score_label").format(score=self.score))
        self.score_label.adjustSize()
        self.lives_label.setText(tr("game_lives_label").format(lives=self.lives))
        self.lives_label.adjustSize()
        self.falling_items.clear()
        self.bubbles.clear()
        self.dolphin_pos = 1
        self.dolphin.move(130, 350)
        self.timer.start(100)
        self.spawn_timer.start(1000)
        self.level_timer.start(5000)
        self.idle_timer.start(random.randint(3000, 5000))
        self.bubble_sound_timer.start(random.randint(1200, 2500))

    def keyPressEvent(self, event):
        # Permite mover con flechas o con las teclas 'a' (izquierda) y 'd' (derecha)
        if event.key() in (Qt.Key_Left, Qt.Key_A) and self.dolphin_pos > 0:
            self.dolphin_pos -= 1
        elif event.key() in (Qt.Key_Right, Qt.Key_D) and self.dolphin_pos < 2:
            self.dolphin_pos += 1

        x = [50, 130, 210][self.dolphin_pos]
        self.dolphin.move(x, 350)

    def update_gradient(self):
        """Actualiza la fase del gradiente, burbujas y repinta el fondo."""
        self.gradient_phase = (self.gradient_phase + 1) % 360
        self.update_bubbles()
        self.update()

    def update_bubbles(self):
        """Actualiza la posición de las burbujas y genera nuevas si es necesario."""
        now = time.time()
        # Añadir nuevas burbujas aleatoriamente
        if len(self.bubbles) < self.max_bubbles and now - self.last_bubble_time > random.uniform(0.8, 2.5):
            self.bubbles.append({
                "x0": random.randint(20, self.width() - 20),
                "y": self.height() + random.randint(0, 40),
                "size": random.randint(18, 48),
                "speed": random.uniform(1.5, 2.0),
                "opacity": random.uniform(0.15, 0.35),
                "zigzag_phase": random.uniform(0, 2 * math.pi),
                "zigzag_amp": random.randint(8, 24),
                "zigzag_freq": random.uniform(0.8, 1.5),
            })
            self.last_bubble_time = now

        # Actualizar posición de burbujas
        for bubble in self.bubbles:
            bubble["y"] -= bubble["speed"]
            # Zigzag horizontal
            t = bubble["y"] / 30.0
            bubble["x"] = bubble["x0"] + math.sin(t * bubble["zigzag_freq"] + bubble["zigzag_phase"]) * bubble["zigzag_amp"]

        # Eliminar burbujas que ya salieron de la pantalla
        self.bubbles = [b for b in self.bubbles if b["y"] + b["size"] > 0]

    def paintEvent(self, event):
        """Dibuja un gradiente animado como fondo y burbujas."""
        painter = QPainter(self)
        rect = self.rect()
        # Gradiente marino animado
        phase = self.gradient_phase
        color1 = QColor.fromHsv((180 + int(60 * math.sin(math.radians(phase)))) % 360, 180, 180)
        color2 = QColor.fromHsv((200 + int(60 * math.cos(math.radians(phase)))) % 360, 255, 120)
        grad = QLinearGradient(0, 0, 0, rect.height())
        grad.setColorAt(0, color1)
        grad.setColorAt(1, color2)
        painter.fillRect(rect, grad)

        # --- Dibuja burbujas ---
        for bubble in self.bubbles:
            painter.save()
            painter.setOpacity(bubble["opacity"])
            font = QFont("Segoe UI Emoji", bubble["size"])
            painter.setFont(font)
            painter.drawText(int(bubble["x"]), int(bubble["y"]), "🫧")
            painter.restore()

        super().paintEvent(event)

    def closeEvent(self, event):
        # Detén todos los timers y sonidos aquí
        if hasattr(self, "timer"):
            self.timer.stop()
        if hasattr(self, "spawn_timer"):
            self.spawn_timer.stop()
        if hasattr(self, "idle_timer"):
            self.idle_timer.stop()
        if hasattr(self, "gradient_timer"):
            self.gradient_timer.stop()
        if hasattr(self, "bubble_sound_timer"):
            self.bubble_sound_timer.stop()
        # Limpia referencias a sonidos activos
        if hasattr(self, "_active_sounds"):
            self._active_sounds.clear()
        event.accept()

    def apply_powerup(self, emoji):
        if emoji == "❤️":
            self.lives += 1
            self.lives_label.setText(tr("game_lives_label").format(lives=self.lives))
            self.lives_label.adjustSize()
        elif emoji == "🕑":
            self.activate_slowdown()

    def activate_slowdown(self):
        self._old_timer_interval = self.timer.interval()
        self.timer.setInterval(self._old_timer_interval * 2)
        duration = random.randint(3000, 5000)
        self._slowdown_remaining = duration // 1000  # segundos

        # Mostrar el label y actualizarlo
        self.slowdown_label.setText(f"🕑x{self._slowdown_remaining}s")
        self.slowdown_label.show()

        # Timer para el efecto
        if hasattr(self, "_slowdown_timer") and self._slowdown_timer.isActive():
            self._slowdown_timer.stop()
        else:
            self._slowdown_timer = QTimer(self)
            self._slowdown_timer.setSingleShot(True)
            self._slowdown_timer.timeout.connect(self.deactivate_slowdown)
        self._slowdown_timer.start(duration)

        # Timer para el contador visual
        if hasattr(self, "_slowdown_counter_timer") and self._slowdown_counter_timer.isActive():
            self._slowdown_counter_timer.stop()
        else:
            self._slowdown_counter_timer = QTimer(self)
            self._slowdown_counter_timer.timeout.connect(self.update_slowdown_counter)
        self._slowdown_counter_timer.start(1000)

    def update_slowdown_counter(self):
        self._slowdown_remaining -= 1
        if self._slowdown_remaining > 0:
            self.slowdown_label.setText(f"🕑x{self._slowdown_remaining}s")
        else:
            self._slowdown_counter_timer.stop()
            self.slowdown_label.hide()

    def deactivate_slowdown(self):
        if hasattr(self, "_old_timer_interval"):
            self.timer.setInterval(self._old_timer_interval)
        self.slowdown_label.hide()
        if hasattr(self, "_slowdown_counter_timer"):
            self._slowdown_counter_timer.stop()
