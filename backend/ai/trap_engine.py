import random

class TrapEngine:
    def __init__(self):
        self.active_trap = None
        self.trap_progress = 0
        self.trap_target_length = 3
        self.is_trigger_ready = False
        
        # Define available traps
        self.TRAPS = {
            "bait_and_parry": {
                "seed_sequence": ["attack", "attack"],
                "trigger_on": ["attack", "heavy"], # If player tries to counter-attack
                "counter_move": "parry",
                "description": "Inducing aggression to land a perfect parry."
            },
            "false_opening": {
                "seed_sequence": ["wait", "wait"],
                "trigger_on": ["heavy", "grab"], # If player tries to punish the 'opening'
                "counter_move": "attack",
                "description": "Feigning exhaustion to lure a heavy commitment."
            },
            "shield_breaker_trap": {
                "seed_sequence": ["attack", "defend"],
                "trigger_on": ["defend", "parry"], # If player plays safe
                "counter_move": "grab",
                "description": "Conditioning a defensive response to land a grab."
            }
        }

    def update_trap_state(self, player_last_move):
        """
        Logic to decide if a trap should be sprung or if we are still 'seeding'.
        """
        if not self.active_trap:
            return None

        trap = self.TRAPS[self.active_trap]
        
        # Check if the player fell for the bait (reacted to the pattern)
        if self.trap_progress >= self.trap_target_length - 1:
            if player_last_move in trap["trigger_on"]:
                self.is_trigger_ready = True
                return trap["counter_move"]

        return None

    def get_trap_move(self):
        """
        Returns the next move in the seeding sequence or the trigger move.
        """
        if not self.active_trap:
            # Chance to start a new trap if none is active
            if random.random() < 0.2: # 20% chance to start a trap
                self.active_trap = random.choice(list(self.TRAPS.keys()))
                self.trap_progress = 0
                self.is_trigger_ready = False
            else:
                return None

        trap = self.TRAPS[self.active_trap]
        
        # If trigger is ready, spring it!
        if self.is_trigger_ready:
            move = trap["counter_move"]
            self.reset_trap()
            return move

        # Otherwise, continue seeding the pattern
        move = trap["seed_sequence"][self.trap_progress % len(trap["seed_sequence"])]
        self.trap_progress += 1
        
        # If we've seeded too long without a bite, reset
        if self.trap_progress > 5:
            self.reset_trap()
            
        return move

    def reset_trap(self):
        self.active_trap = None
        self.trap_progress = 0
        self.is_trigger_ready = False

    def get_status(self):
        if not self.active_trap:
            return "IDLE"
        return f"EXECUTING_{self.active_trap.upper()} (Progress: {self.trap_progress})"
