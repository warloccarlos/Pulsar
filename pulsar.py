import os
import random
import pygame
import numpy as np
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label
from textual.containers import Container, Vertical
from textual.binding import Binding
from textual import events

# Headless audio for terminal compatibility
os.environ['SDL_VIDEODRIVER'] = 'dummy'

BARS = " ▂▃▄▅▆▇█"

class Visualizer(Static):
    def on_mount(self) -> None:
        self.num_rows = 8
        self.bar_spacing = 3 
        self.prev_heights = []
        # Increase refresh rate for Tabby/Modern terminals
        self.set_interval(0.05, self.update_bars)

    def update_bars(self) -> None:
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            width = self.size.width
            if width > 0:
                num_bars = max(1, width // self.bar_spacing)
                max_h = self.num_rows * 8
                if len(self.prev_heights) != num_bars:
                    self.prev_heights = np.zeros(num_bars)
                
                target_heights = np.random.rand(num_bars) * max_h
                self.prev_heights = self.prev_heights * 0.5 + target_heights * 0.5
                heights = self.prev_heights.astype(int)

                lines = []
                for r in range(self.num_rows - 1, -1, -1):
                    row_str = ""
                    threshold = r * 8
                    for h in heights:
                        local_h = h - threshold
                        char = BARS[7] if local_h >= 8 else (BARS[local_h] if local_h > 0 else " ")
                        row_str += char + "  "
                    lines.append(row_str)
                self.update(f"[bold cyan]{chr(10).join(lines)}[/bold cyan]")
        else:
            # Show a "pulse" line when idle
            self.update("\n" * (self.num_rows - 1) + "[dim]— " * (self.size.width // 3) + "[/dim]")

class Pulsar(App):
    TITLE = "Pulsar Pro"
    # Added explicit focus settings to CSS
    CSS = """
    #app-body { height: 1fr; }
    #sidebar { width: 30; background: $panel; border-right: tall $primary; dock: left; }
    #main-view { width: 1fr; align: center middle; text-align: center; }
    #now-playing { text-style: bold; color: $accent; margin-bottom: 2; height: 3; }
    Visualizer { width: 100%; height: 10; content-align: center bottom; }
    #controls { height: 7; dock: bottom; background: $surface; border-top: double $secondary; align: center middle; }
    ListView:focus { border: none; } 
    """

    BINDINGS = [
        Binding("space", "toggle_play", "Play/Pause", show=True, priority=True),
        Binding("n", "next_track", "Next", show=True),
        Binding("z", "prev_track", "Prev", show=True),
        Binding("s", "toggle_shuffle", "Shuffle", show=True),
        Binding("r", "toggle_repeat", "Repeat", show=True),
        Binding("x", "remove_track", "Remove", show=True, priority=True),
        Binding("q", "quit_app", "Quit", show=True),
    ]

    def __init__(self):
        super().__init__()
        self.playlist = []
        self.current_index = -1
        self.repeat_mode = False
        self.shuffle_mode = False
        self.is_paused = True

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-body"):
            with Vertical(id="sidebar"):
                yield Label(" [Playlist]")
                yield ListView(id="playlist-view")
            with Vertical(id="main-view"):
                yield Static("Pulsar: Active", id="now-playing")
                yield Visualizer()
        with Vertical(id="controls"):
            yield Static(id="status-line")
            yield Static(" [Z] Prev | [Space] Play | [N] Next | [X] Remove | [Q] Quit ")
        yield Footer()

    def on_mount(self) -> None:
        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            self.scan_directories()
            self.update_status_display()
            self.set_interval(1.0, self.check_end_of_track)
        except Exception as e:
            self.notify(f"Mixer Error: {e}", severity="error")

    def scan_directories(self):
        home = Path.home()
        for p in [home, home / "Downloads", home / "Music"]:
            if p.exists():
                for f in p.glob("*.mp3"):
                    self.add_to_playlist(str(f))

    def add_to_playlist(self, path: str):
        if path not in self.playlist:
            self.playlist.append(path)
            self.query_one("#playlist-view", ListView).append(ListItem(Label(f" {os.path.basename(path)} ")))

    def play_track(self, index: int):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self.is_paused = False
            pygame.mixer.music.load(self.playlist[index])
            pygame.mixer.music.play()
            self.query_one("#now-playing").update(f"🎵 {os.path.basename(self.playlist[index])}")
            self.query_one("#playlist-view", ListView).index = index

    def action_toggle_play(self):
        if self.current_index == -1 and self.playlist:
            self.play_track(0)
        elif pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True
        else:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def action_remove_track(self):
        lv = self.query_one("#playlist-view", ListView)
        idx = lv.index
        if idx is not None and 0 <= idx < len(self.playlist):
            if idx == self.current_index:
                pygame.mixer.music.stop()
                self.is_paused = True
                self.current_index = -1
            self.playlist.pop(idx)
            lv.query("ListItem")[idx].remove()
            self.notify("Track Removed")

    def action_next_track(self):
        if self.playlist:
            idx = random.randint(0, len(self.playlist)-1) if self.shuffle_mode else (self.current_index + 1) % len(self.playlist)
            self.play_track(idx)

    def action_prev_track(self):
        if self.playlist:
            self.play_track((self.current_index - 1) % len(self.playlist))

    def action_toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode
        self.update_status_display()

    def action_toggle_repeat(self):
        self.repeat_mode = not self.repeat_mode
        self.update_status_display()

    def action_quit_app(self):
        pygame.mixer.quit()
        self.exit()

    def update_status_display(self):
        s = "ON" if self.shuffle_mode else "OFF"
        r = "ON" if self.repeat_mode else "OFF"
        self.query_one("#status-line").update(f"Shuffle: {s} | Repeat: {r}")

    def check_end_of_track(self):
        if not pygame.mixer.music.get_busy() and not self.is_paused and self.current_index != -1:
            if self.repeat_mode: self.play_track(self.current_index)
            else: self.action_next_track()

    def on_list_view_selected(self, event: ListView.Selected):
        self.play_track(event.index)

if __name__ == "__main__":
    Pulsar().run()