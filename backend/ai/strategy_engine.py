import random

class StrategyEngine:
    def analyze_loadout(self, shield, ability):
        """
        Structural Intelligence:
        Pre-combat analysis of player equipment to set MIRAI's initial strategy.
        """
        analysis = []
        
        if shield.name == "Greatshield":
            analysis.append("Target is prioritizing defense. Recommend high-frequency GRAB maneuvers.")
        elif shield.name == "Buckler":
            analysis.append("Target is prioritizing parries. Recommend FEINT-heavy sequence to bait and punish.")
        elif shield.name == "Vanguard Plate":
            analysis.append("Target has high HP pool. Prioritize POSTURE damage to force a stagger.")

        if ability.name == "Focus Pulse":
            analysis.append("Target can restore stamina. Avoid long endurance trades.")
        elif ability.name == "Overdrive":
            analysis.append("High burst threat detected. Maintain CAUTION when player HP is low.")

        return " | ".join(analysis)

    def choose_strategy(
        self,
        player_type,
        summary,
        player_state,
        boss_state,
        predicted_move,
        trap_engine,
        similar_fights=[]
    ):
        """
        Autonomous Decision Logic v3:
        - Trap Proactivity (Baiting sequences)
        - Resource Aware (Stamina/Posture)
        - Prediction Reactive (Parry logic)
        - Gear Aware (Counters shields/abilities)
        """
        
        # 1. EMERGENCY: STAGGER CHECK
        if boss_state['is_staggered']:
            return "wait"

        # 2. PROACTIVE TRAPPING (Pattern Induction)
        # Consult TrapEngine to see if we should continue seeding or trigger a trap
        trap_move = trap_engine.get_trap_move()
        if trap_move:
            # Check if we have stamina for the trap move
            from engine.actions import ACTIONS
            if boss_state['stamina'] >= ACTIONS[trap_move].get('st_cost', 0):
                return trap_move

        # 3. THE PARRY TRAP (Reactive Prediction)
        # If we are very sure player will attack, and we have stamina, PARRY.
        if predicted_move in ["attack", "heavy"] and boss_state['stamina'] >= 25:
            # Only parry if confidence is high (simulated for now, summary could have it)
            if summary.get('predictability', 0) > 0.7:
                return "parry"

        # 3. KINETIC EXPLOITATION (Low Player Stamina)
        if player_state['stamina'] < 20:
            # Pursuit Mode: Player can't defend well
            if boss_state['stamina'] >= 40:
                return "heavy"
            return "attack"

        # 4. POSTURE PRESSURE (High Player Posture)
        if player_state['posture'] > 70:
            # Try to break them
            if boss_state['stamina'] >= 30:
                return "grab" # Grabs deal high posture damage

        # 5. VECTOR MEMORY INFLUENCE
        if similar_fights and similar_fights[0]["distance"] < 0.4:
            past_result = similar_fights[0]["fight"].get("predicted_move")
            if past_result in ["attack", "heavy"]:
                return "parry" if boss_state['stamina'] >= 25 else "defend"

        # 6. GEAR-AWARE COUNTERS
        if player_state.get('shield_type') == "Greatshield":
            # Greatshields are weak to grabs
            if boss_state['stamina'] >= 30:
                return "grab"

        # 7. EMOTIONAL WEIGHTING (Placeholder for Phase 3)
        # ... logic for Irritated/Dominant ...

        # 8. DEFAULT BEHAVIORAL COUNTERS
        if player_type == "Aggressive":
            return random.choice(["defend", "parry", "attack"]) if boss_state['stamina'] > 30 else "wait"
        
        if player_type == "Defensive":
            return random.choice(["grab", "heavy", "feint"])

        # 9. SURVIVAL
        if boss_state['hp'] < 30 and boss_state['stamina'] >= 20:
            return "heal"

        # 10. RANDOMIZED FALLBACK (With Stamina Check)
        options = ["attack", "wait"]
        if boss_state['stamina'] >= 40: options.append("heavy")
        if boss_state['stamina'] >= 30: options.append("grab")
        if boss_state['stamina'] >= 25: options.append("parry")
        if boss_state['stamina'] >= 20: 
            options.append("feint")
            options.append("heal")
        
        return random.choice(options)
