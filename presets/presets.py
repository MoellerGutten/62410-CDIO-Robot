class RobotPreset(object):
    def __init__(self, reverse_motor=False, speed_modifier=1, reverse_direction=False):
        if speed_modifier <= 0:
            raise ValueError("speed_modifier must be positive")

        self.reverse_motor = reverse_motor
        self.speed_modifier = speed_modifier
        self.reverse_direction = reverse_direction


PRESET_A = RobotPreset(reverse_motor=True, speed_modifier=1, reverse_direction=True)
PRESET_B = RobotPreset(reverse_motor=False, speed_modifier=1, reverse_direction=True)
# More presets here...