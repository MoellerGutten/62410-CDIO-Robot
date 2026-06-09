import os
from dotenv import load_dotenv
from presets.presets import PRESET_A, PRESET_B

load_dotenv()

PRESETS = {
    "A": PRESET_A,
    "B": PRESET_B,
}

#Gets the active preset from the env file, with a default to preset A
active_name = os.getenv("ACTIVE_PRESET", "A")
current_preset = PRESETS[active_name]