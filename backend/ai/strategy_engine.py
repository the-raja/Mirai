import random


class StrategyEngine:

    def choose_strategy(
        self,
        player_type,
        summary,
        boss_heavy_uses=0,
        player_hp=100,
        boss_hp=100,
        similar_fights=[]
    ):

        last_sequence = summary["last_sequence"]

        # 1. VECTOR MEMORY INFLUENCE (RELAXED THRESHOLD)
        if similar_fights and similar_fights[0]["distance"] < 0.5:
            
            past_predicted = similar_fights[0]["fight"].get("predicted_move")
            confidence = 1.0 - similar_fights[0]["distance"] # Higher confidence for closer matches

            if random.random() < confidence:
                if past_predicted in ["attack", "heavy"]:
                    return "defend"
                if past_predicted == "defend":
                    return "heavy" if boss_heavy_uses > 0 else "attack"
                if past_predicted == "heal":
                    return "heavy" if boss_heavy_uses > 0 else "attack"

        # 2. IMMEDIATE HP-BASED LOGIC (SURVIVAL & KILL PRESSURE)
        
        # Kill Pressure: If player is weak, finish them.
        if player_hp <= 20:
            return "heavy" if boss_heavy_uses > 0 else "attack"
            
        # Survival: If boss is weak, heal or defend.
        if boss_hp <= 30:
            if random.random() < 0.7:
                return "heal" if boss_hp < 20 else "defend"

        # 3. BEHAVIORAL COUNTERS
        
        # Counter Aggressive
        if player_type == "Aggressive":
            return random.choice(["defend", "heavy" if boss_heavy_uses > 0 else "attack", "attack"])

        # Counter Defensive
        elif player_type == "Defensive":
            return random.choice(["heavy" if boss_heavy_uses > 0 else "attack", "attack", "bluff"])

        # Counter Panic
        elif player_type == "Panic":
            return "attack" # Don't give them room to breathe

        # 4. SEQUENCE PUNISHMENT
        if len(last_sequence) >= 2 and last_sequence[-1] == "heal":
            return "heavy" if boss_heavy_uses > 0 else "attack"

        # 5. CHARGE-AWARE DEFAULT (No more wasted turns)
        options = ["attack", "defend", "heal", "bluff", "wait"]
        if boss_heavy_uses > 0:
            options.append("heavy")
            
        return random.choice(options)
