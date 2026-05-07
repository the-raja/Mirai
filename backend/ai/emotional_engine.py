class EmotionalEngine:
    def __init__(self):
        self.frustration = 0.0  # Increases on failed predictions or bluffs
        self.confidence = 0.5   # Increases on successful hits/predictions
        self.caution = 0.0      # Increases as HP drops

    def update(self, boss_hp, player_hp, prediction_hit, player_bluffed):
        # Update Caution
        self.caution = (100 - boss_hp) / 100.0
        
        # Update Frustration
        if player_bluffed:
            self.frustration += 0.2
        if not prediction_hit and not player_bluffed:
            self.frustration += 0.05
        
        # Update Confidence
        if prediction_hit:
            self.confidence += 0.1
            self.frustration -= 0.1
        if player_hp < boss_hp:
            self.confidence += 0.05
            
        # Clamp values
        self.frustration = max(0, min(1, self.frustration))
        self.confidence = max(0, min(1, self.confidence))
        self.caution = max(0, min(1, self.caution))

    def get_state(self):
        if self.caution > 0.7: return "DESPERATE"
        if self.frustration > 0.6: return "IRRITATED"
        if self.confidence > 0.8: return "DOMINANT"
        if self.caution > 0.4: return "CAUTIOUS"
        return "CALCULATING"
