from dataclasses import dataclass

@dataclass
class RobotPreset:
    reverse_motor = False
    speed_modifier = 1
    reverse_direction = False

    # Protect against negative speed modifier values
    def __post_init__(self):
        if self.speed_modifier <= 0:
            raise ValueError("speed_modifier must be positive")


PRESET_A = RobotPreset(reverse_motor=True, speed_modifier=1, reverse_direction=False)
PRESET_B = RobotPreset(reverse_motor=False, speed_modifier=0.5, reverse_direction=True)
# More presets here...