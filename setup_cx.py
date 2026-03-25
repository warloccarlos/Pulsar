import sys
from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": [
        "os", 
        "pygame", 
        "numpy", 
        "textual", 
        "asyncio", 
        "_asyncio", 
        "_queue",
        "encodings"
    ],
    "include_msvcr": True, # Critical for Windows systems
}

base = None
# Optional: Change to "Win32GUI" ONLY if you don't want a terminal window, 
# but for a terminal player, 'None' is usually what you want.

setup(
    name="Pulsar",
    version="1.0",
    description="Terminal Audio Player",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "terminal_player.py", 
            base=base, 
            target_name="Pulsar.exe",
            shortcut_name="Pulsar",
            shortcut_dir="ProgramMenuFolder", # Creates a Start Menu shortcut
        )
    ],
)
