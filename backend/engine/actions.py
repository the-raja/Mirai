ACTIONS = {
    "attack": {
        "damage": 10,
        "st_cost": 15,
        "ps_damage": 10,
        "priority": 1
    },
    "heavy": {
        "damage": 18,
        "st_cost": 40,
        "ps_damage": 35,
        "priority": 1
    },
    "parry": {
        "damage": 0,
        "st_cost": 25,
        "ps_damage": 50, # Damage dealt to attacker if successful
        "priority": 2
    },
    "feint": {
        "damage": 0,
        "st_cost": 20,
        "ps_damage": 0,
        "priority": 1
    },
    "grab": {
        "damage": 12,
        "st_cost": 30,
        "ps_damage": 45,
        "priority": 1
    },
    "defend": {
        "damage": 0,
        "st_cost": 0,
        "priority": 0
    },
    "heal": {
        "heal": 15,
        "st_cost": 20,
        "priority": 0
    },
    "bluff": {
        "damage": 0,
        "st_cost": 0,
        "priority": 0
    },
    "wait": {
        "damage": 0,
        "st_cost": 0,
        "priority": 0
    },
    "ability": {
        "damage": 0,
        "st_cost": 0,
        "priority": 2
    }
}
