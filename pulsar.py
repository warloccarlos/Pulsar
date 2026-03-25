import os
import numpy as np
import pygame
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label
from textual.containers import Container, Vertical
from textual.binding import Binding
from textual import events

BARS = " ▂▃▄▅▆▇█"

class Visualizer(Static):
    def on_mount(self) -> None:
        self.num_rows = 8
        self.bar_spacing = 3 
        self.prev_heights = [] # Store heights to create the "gravity" effect
        # Increased interval to 0.1 for a more relaxed pace
        self.set_interval(0.1, self.update_bars)

    def update_bars(self) -> None:
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            width = self.size.width
            if width > 0:
                num_bars = width // self.bar_spacing
                max_h = self.num_rows * 8
                
                # If window resized, reset previous heights
                if len(self.prev_heights) != num_bars:
                    self.prev_heights = np.zeros(num_bars)

                # 1. Target Heights: Bass (left) is heavier, Treble (right) is lighter
                weights = np.linspace(1.0, 0.3, num_bars)
                target_heights = np.random.rand(num_bars) * weights * max_h
                
                # 2. Smoothing Logic (The "Slow" part): 
                # We interpolate between old height and new target
                # 0.3 means it moves 30% toward the target each frame (Fluid motion)
                self.prev_heights = self.prev_heights * 0.7 + target_heights * 0.3
                heights = self.prev_heights.astype(int)

                lines = []
                for r in range(self.num_rows - 1, -1, -1):
                    row_str = ""
                    threshold = r * 8
                    for h in heights:
                        local_h = h - threshold
                        char = BARS[7] if local_h >= 8 else (BARS[local_h] if local_h > 0 else " ")
                        row_str += char + "  " # Horizontal spacing
                    lines.append(row_str)
                
                self.update(f"[bold cyan]{chr(10).join(lines)}[/bold cyan]")
        else:
            self.update("\n" * (self.num_rows - 1) + "[dim]" + "— " * (self.size.width // 3) + "[/dim]")

class Pulsar(App):
    TITLE = "Pulsar Chill Edition"
    CSS = """
    #app-body { height: 1fr; }
    #sidebar { width: 35; background: $panel; border-right: tall $primary; dock: left; }
    #sidebar.-hidden { display: none; }
    #main-view { width: 1fr; align: center middle; text-align: center; }
    #now-playing { text-style: bold; color: $accent; margin-bottom: 2; height: 3; }
    Visualizer { width: 100%; height: 8; content-align: center bottom; }
    #controls { height: 5; dock: bottom; background: $surface; border-top: double $secondary; align: center middle; }
    """

    BINDINGS = [
        Binding("b", "toggle_sidebar", "Sidebar"),
        Binding("space", "toggle_play", "Play/Pause"),
        Binding("n", "next_track", "Next"),
        Binding("z", "prev_track", "Prev"),
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        pygame.mixer.init()
        self.playlist = []
        self.current_index = -1

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="app-body"):
            with Vertical(id="sidebar"):
                yield Label(" [Playlist - Drag Files Here]")
                yield ListView(id="playlist-view")
            with Vertical(id="main-view"):
                yield Static("Drop an audio file to start", id="now-playing")
                yield Visualizer()
        with Vertical(id="controls"):
            yield Static(" [Z] Prev | [Space] Play/Pause | [N] Next | [B] Sidebar ")
            yield Static("--:-- / --:--", id="timer")
        yield Footer()

    def on_paste(self, event: events.Paste) -> None:
        path = event.text.strip().strip("'\"")
        if os.path.isfile(path) and path.lower().endswith(('.mp3', '.wav', '.ogg')):
            self.playlist.append(path)
            self.query_one("#playlist-view", ListView).append(ListItem(Label(f" {os.path.basename(path)} ")))
            if self.current_index == -1: self.play_track(0)

    def play_track(self, index: int):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            pygame.mixer.music.load(self.playlist[index])
            pygame.mixer.music.play()
            self.query_one("#now-playing").update(f"🎵 NOW PLAYING\n[b]{os.path.basename(self.playlist[index])}[/b]")
            self.query_one("#playlist-view", ListView).index = index

    def action_next_track(self):
        if self.playlist: self.play_track((self.current_index + 1) % len(self.playlist))

    def action_prev_track(self):
        if self.playlist: self.play_track((self.current_index - 1) % len(self.playlist))

    def action_toggle_play(self):
        if pygame.mixer.music.get_busy(): pygame.mixer.music.pause()
        else: pygame.mixer.music.unpause()

    def action_toggle_sidebar(self):
        self.query_one("#sidebar").toggle_class("-hidden")

    def on_list_view_selected(self, event: ListView.Selected):
        self.play_track(event.index)

if __name__ == "__main__":
    Pulsar().run()