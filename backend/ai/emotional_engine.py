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
        state = "CALCULATING"
        modifiers = {"dmg_dealt": 1.0, "dmg_taken": 1.0, "ps_dealt": 1.0, "st_regen": 1.0}

        if self.caution > 0.7:
            state = "DESPERATE"
            modifiers = {"dmg_dealt": 0.8, "dmg_taken": 1.0, "ps_dealt": 0.8, "st_regen": 1.3}
        elif self.frustration > 0.6:
            state = "IRRITATED"
            modifiers = {"dmg_dealt": 1.3, "dmg_taken": 1.2, "ps_dealt": 1.1, "st_regen": 1.0}
        elif self.confidence > 0.8:
            state = "DOMINANT"
            modifiers = {"dmg_dealt": 1.1, "dmg_taken": 0.8, "ps_dealt": 1.5, "st_regen": 1.0}
        elif self.caution > 0.4:
            state = "CAUTIOUS"
            modifiers = {"dmg_dealt": 0.9, "dmg_taken": 0.9, "ps_dealt": 1.0, "st_regen": 1.1}
        
        return state, modifiers
