from engine.actions import ACTIONS

def resolve_turn(player, p_action, boss, b_action, p_mods=None, b_mods=None):
    if p_mods is None: p_mods = {"dmg_dealt": 1.0, "dmg_taken": 1.0, "ps_dealt": 1.0, "st_regen": 1.0}
    if b_mods is None: b_mods = {"dmg_dealt": 1.0, "dmg_taken": 1.0, "ps_dealt": 1.0, "st_regen": 1.0}

    results = {"player": "", "boss": ""}

    # 1. HANDLE STAGGER (Entities skip turns)
    p_can_act = not player.is_staggered
    b_can_act = not boss.is_staggered

    if not p_can_act:
        results["player"] = f"{player.name} is staggered and cannot act!"
        p_action = "wait"
    if not b_can_act:
        results["boss"] = f"{boss.name} is staggered and cannot act!"
        b_action = "wait"

    # 2. STAMINA VALIDATION
    if p_can_act and not player.use_stamina(ACTIONS[p_action]["st_cost"]):
        results["player"] = f"{player.name} is too exhausted for {p_action}! Forced to wait."
        p_action = "wait"
    
    if b_can_act and not boss.use_stamina(ACTIONS[b_action]["st_cost"]):
        results["boss"] = f"{boss.name} is too exhausted for {b_action}! Forced to wait."
        b_action = "wait"

    # 3. SET DEFENSIVE STATES
    player.is_defending = (p_action == "defend")
    boss.is_defending = (b_action == "defend")

    # 4. RESOLVE PARRY (High Priority)
    if p_action == "parry" and b_action in ["attack", "heavy"]:
        # Player parries boss
        boss.take_damage(0, ACTIONS["parry"]["ps_damage"] * p_mods["ps_dealt"], multiplier=b_mods["dmg_taken"])
        results["player"] = f"{player.name} perfectly PARRIES {boss.name}'s attack!"
        results["boss"] = f"{boss.name}'s balance is shattered by the parry!"
        b_action = "wait" 

    if b_action == "parry" and p_action in ["attack", "heavy"]:
        # Boss parries player
        player.take_damage(0, ACTIONS["parry"]["ps_damage"] * b_mods["ps_dealt"], multiplier=p_mods["dmg_taken"])
        results["boss"] = f"{boss.name} perfectly PARRIES {player.name}'s attack!"
        results["player"] = f"{player.name}'s balance is shattered by the parry!"
        p_action = "wait"

    # 5. RESOLVE ACTIONS
    results["player"] += " " + process_single_action(player, boss, p_action, b_action, p_mods, b_mods)
    results["boss"] += " " + process_single_action(boss, player, b_action, p_action, b_mods, p_mods)

    # 6. RESOURCE RECOVERY
    player.recover_resources(st_amount=15 * p_mods["st_regen"])
    boss.recover_resources(st_amount=15 * b_mods["st_regen"])

    return results

def process_single_action(attacker, defender, act_name, def_act_name, attacker_mods, defender_mods):
    action = ACTIONS[act_name]
    res = ""
    
    # Apply Active Buffs (Abilities)
    dmg_mult = attacker_mods["dmg_dealt"]
    ps_mult = attacker_mods["ps_dealt"]
    if "titan_wrath" in attacker.active_buffs:
        ps_mult *= 2.0
    if "overdrive" in attacker.active_buffs:
        dmg_mult *= 1.5
        ps_mult *= 1.5

    # Target takes more/less damage based on their emotional state
    taken_mult = defender_mods["dmg_taken"]

    if act_name == "attack":
        dmg = int(action["damage"] * dmg_mult)
        ps_dmg = int(action["ps_damage"] * ps_mult)
        if defender.is_defending:
            dmg = int(dmg * 0.4)
            ps_dmg = int(ps_dmg * 0.5)
            res = f"{attacker.name} attacks! {defender.name} blocks, taking minor damage."
        else:
            res = f"{attacker.name} lands a solid hit."
        defender.take_damage(dmg, ps_dmg, multiplier=taken_mult)

    elif act_name == "heavy":
        dmg = int(action["damage"] * dmg_mult)
        ps_dmg = int(action["ps_damage"] * ps_mult)
        if defender.is_defending:
            dmg = int(dmg * 0.7)
            ps_dmg = int(ps_dmg * 0.8)
            res = f"{attacker.name} crushes through {defender.name}'s guard!"
        else:
            res = f"{attacker.name} delivers a devastating heavy strike."
        defender.take_damage(dmg, ps_dmg, multiplier=taken_mult)

    elif act_name == "grab":
        dmg = int(action["damage"] * dmg_mult)
        ps_dmg = int(action["ps_damage"] * ps_mult)
        if defender.is_defending:
            dmg = int(dmg * 1.5)
            ps_dmg = int(ps_dmg * 1.5)
            res = f"{attacker.name} catches {defender.name} off-guard while blocking! CRITICAL GRAB!"
        else:
            res = f"{attacker.name} throws {defender.name}."
        defender.take_damage(dmg, ps_dmg, multiplier=taken_mult)

    elif act_name == "heal":
        attacker.heal(action["heal"])
        res = f"{attacker.name} uses a quick repair, restoring HP."

    elif act_name == "defend":
        res = f"{attacker.name} assumes a defensive stance."

    elif act_name == "feint":
        if def_act_name in ["defend", "parry"]:
            defender.take_damage(0, 20 * ps_mult, multiplier=taken_mult)
            res = f"{attacker.name} feints! {defender.name} falls for the bait and loses balance."
        else:
            res = f"{attacker.name} performs a confusing feint."

    elif act_name == "ability":
        if attacker.ability and attacker.ability_cooldown <= 0:
            ability = attacker.ability
            res = f"{attacker.name} activates {ability.name}!"
            
            if ability.name == "Focus Pulse":
                attacker.stamina = min(attacker.max_stamina, attacker.stamina + ability.st_restore)
                res += f" Stamina surged."
            elif ability.name == "Titan's Wrath":
                attacker.active_buffs.append("titan_wrath")
                attacker.ability_duration = ability.duration
                res += " Posture pressure doubled."
            elif ability.name == "Overdrive":
                attacker.active_buffs.append("overdrive")
                attacker.ability_duration = ability.duration
                res += " Redlining systems!"

            attacker.ability_cooldown = ability.cooldown
        else:
            res = f"{attacker.name} ability is on cooldown."

    elif act_name == "bluff":
        res = f"{attacker.name} attempts to mask their movements."

    elif act_name == "wait":
        res = f"{attacker.name} focuses on recovery."

    return res.strip()
