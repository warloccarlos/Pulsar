import os
import random
import pygame
import numpy as np
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, ListItem, ListView, Label
from textual.containers import Container, Vertical
from textual.binding import Binding

# Headless audio for terminal compatibility
os.environ['SDL_VIDEODRIVER'] = 'dummy'

BARS = " ▂▃▄▅▆▇█"

class Visualizer(Static):
    def on_mount(self) -> None:
        self.num_rows = 6 # Rows above and below the center
        self.bar_spacing = 3 
        self.prev_heights = []
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

                # Generate Upper Half (Growing Up)
                upper_lines = []
                for r in range(self.num_rows - 1, -1, -1):
                    row_str = ""
                    threshold = r * 8
                    for h in heights:
                        local_h = h - threshold
                        char = BARS[7] if local_h >= 8 else (BARS[local_h] if local_h > 0 else " ")
                        row_str += char + "  "
                    upper_lines.append(row_str)

                # Generate Lower Half (Flipped, Growing Down)
                # We use the same 'heights' but reversed characters to simulate downward growth
                lower_lines = []
                for r in range(self.num_rows):
                    row_str = ""
                    threshold = r * 8
                    for h in heights:
                        local_h = h - threshold
                        # Use dots or smaller bars for the downward pulse
                        char = "█" if local_h >= 8 else (BARS[local_h] if local_h > 0 else " ")
                        row_str += char + "  "
                    lower_lines.append(row_str)

                # Combine with a center divider
                divider = "[dim]" + "—" * (width) + "[/dim]"
                full_viz = f"[bold cyan]{os.linesep.join(upper_lines)}[/]\n{divider}\n[bold blue]{os.linesep.join(lower_lines)}[/]"
                self.update(full_viz)
        else:
            self.update("\n" * self.num_rows + "[dim]P U L S A R   I D L E[/dim]" + "\n" * self.num_rows)

class Pulsar(App):
    TITLE = "Pulsar Audio Engine"
    CSS = """
    #app-body { height: 1fr; }
    #sidebar { 
        width: 35; 
        background: $panel; 
        border-right: tall $primary; 
        dock: left; 
        transition: width 300ms;
    }
    #sidebar.-hidden { 
        display: none; 
    }
    #main-view { width: 1fr; align: center middle; text-align: center; }
    #now-playing { text-style: bold; color: $accent; margin-bottom: 1; height: 3; }
    Visualizer { width: 100%; height: 1fr; content-align: center middle; }
    #controls { height: 7; dock: bottom; background: $surface; border-top: double $secondary; align: center middle; }
    """

    BINDINGS = [
        Binding("b", "toggle_sidebar", "Playlist", priority=True),
        Binding("space", "toggle_play", "Play/Pause", priority=True),
        Binding("n", "next_track", "Next"),
        Binding("z", "prev_track", "Prev"),
        Binding("s", "toggle_shuffle", "Shuffle"),
        Binding("r", "toggle_repeat", "Repeat"),
        Binding("x", "remove_track", "Remove", priority=True),
        Binding("q", "quit_app", "Quit"),
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
                yield Label(" [Playlist - 'X' to Remove]")
                yield ListView(id="playlist-view")
            with Vertical(id="main-view"):
                yield Static("Select a track to begin", id="now-playing")
                yield Visualizer()
        with Vertical(id="controls"):
            yield Static(id="status-line")
            yield Static(" [B] Sidebar | [Z] Prev | [Space] Play | [N] Next | [X] Del ")
        yield Footer()

    def on_mount(self) -> None:
        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            self.scan_directories()
            self.update_status_display()
            self.set_interval(1.0, self.check_end_of_track)
        except Exception as e:
            self.notify(f"Hardware Error: {e}", severity="error")

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one("#sidebar")
        sidebar.toggle_class("-hidden")

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

    def update_status_display(self):
        s = "ON" if self.shuffle_mode else "OFF"
        r = "ON" if self.repeat_mode else "OFF"
        self.query_one("#status-line").update(f"Shuffle: {s} | Repeat: {r}")

    def check_end_of_track(self):
        if not pygame.mixer.music.get_busy() and not self.is_paused and self.current_index != -1:
            if self.repeat_mode: self.play_track(self.current_index)
            else: self.action_next_track()

    def action_quit_app(self):
        pygame.mixer.quit()
        self.exit()

    def on_list_view_selected(self, event: ListView.Selected):
        self.play_track(event.index)

if __name__ == "__main__":
    Pulsar().run()