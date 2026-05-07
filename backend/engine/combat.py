from engine.actions import ACTIONS

def process_action(attacker, defender, action_name):

    action = ACTIONS[action_name]

    # Note: attacker.is_defending is handled in routes.py 
    # for simultaneous resolution logic.

    result = ""

    if action_name == "attack":

        damage = action["damage"]
        
        # Attack deals HALF damage (5) if defending
        if defender.is_defending:
            damage = int(damage * 0.5)
            result = f"{attacker.name} attacks! {defender.name} guards, taking {damage} damage."
        else:
            result = f"{attacker.name} attacks for {damage} damage."

        defender.take_damage(damage)

    elif action_name == "heavy":

        damage = action["damage"]
        
        # Heavy attack deals 70% damage if defending
        if defender.is_defending:
            damage = int(damage * 0.7)
            result = f"{attacker.name} uses HEAVY ATTACK! {defender.name} guards, but the force pierces through for {damage} damage."
        else:
            result = f"{attacker.name} uses HEAVY ATTACK for {damage} damage!"

        defender.take_damage(damage)

    elif action_name == "defend":

        result = f"{attacker.name} is in a defensive stance."

    elif action_name == "heal":

        heal = action["heal"]

        attacker.heal(heal)

        result = f"{attacker.name} heals for {heal} HP."

    elif action_name == "bluff":

        result = f"{attacker.name} attempts to confuse {defender.name}."

    elif action_name == "wait":

        result = f"{attacker.name} waits for an opening."

    return result
