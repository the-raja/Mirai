from collections import defaultdict

class BehaviorTracker:
    def __init__(self):
        self.move_counts = defaultdict(int)
        self.move_history = []
        self.first_move = None
        self.heal_when_low = 0
        self.total_turns = 0
        self.bluff_modifier = 0.0

    def track_move(self, move, player_hp):
        self.total_turns += 1
        self.move_counts[move] += 1
        self.move_history.append(move)
        
        if self.first_move is None:
            self.first_move = move

        # Panic heal detection
        if move == "heal" and player_hp <= 35:
            self.heal_when_low += 1
            
        # Psychological Warfare Logic
        if move == "bluff":
            # Bluffing reduces the perceived predictability of the player
            self.bluff_modifier += 0.1
        if move == "wait":
            # Waiting reduces aggression and panic scores
            if self.heal_when_low > 0: self.heal_when_low -= 0.5
            if self.move_counts["attack"] > 0: self.move_counts["attack"] -= 0.2

    def get_aggression_score(self):
        attacks = self.move_counts["attack"] + self.move_counts["heavy"]
        if self.total_turns == 0: return 0
        score = (attacks / self.total_turns)
        return round(max(0, score), 2)

    def get_defense_score(self):
        defenses = self.move_counts["defend"]
        if self.total_turns == 0: return 0
        return round(defenses / self.total_turns, 2)

    def get_panic_score(self):
        if self.total_turns == 0: return 0
        score = (self.heal_when_low / self.total_turns)
        return round(max(0, score), 2)

    def get_behavior_summary(self):
        move_counts = dict(self.move_counts)
        total_moves = sum(move_counts.values())
        
        predictability = 0
        if total_moves > 0:
            most_used = max(move_counts.values())
            # Bluffs actively mask predictability
            predictability = (most_used / total_moves) - self.bluff_modifier

        return {
            "aggression": self.get_aggression_score(),
            "defense": self.get_defense_score(),
            "panic": self.get_panic_score(),
            "predictability": round(max(0, predictability), 2),
            "first_move": self.first_move,
            "last_sequence": self.move_history[-3:],
            "move_counts": move_counts
        }

    def reset(self):
        self.move_counts = defaultdict(int)
        self.move_history = []
        self.first_move = None
        self.heal_when_low = 0
        self.total_turns = 0
        self.bluff_modifier = 0.0
