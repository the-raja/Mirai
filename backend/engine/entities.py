class Shield:
    def __init__(self, name, parry_bonus=0, block_efficiency=0.5, posture_resistance=1.0, stamina_mod=1.0):
        self.name = name
        self.parry_bonus = parry_bonus # Increases parry success chance/window
        self.block_efficiency = block_efficiency # Damage reduction when defending
        self.posture_resistance = posture_resistance # Multiplier for posture damage taken
        self.stamina_mod = stamina_mod # Multiplier for stamina costs

SHIELDS = {
    "buckler": Shield("Buckler", parry_bonus=0.2, block_efficiency=0.3, posture_resistance=1.2, stamina_mod=0.9),
    "greatshield": Shield("Greatshield", parry_bonus=-0.1, block_efficiency=0.8, posture_resistance=0.6, stamina_mod=1.2),
    "vanguard": Shield("Vanguard Plate", parry_bonus=0, block_efficiency=0.6, posture_resistance=0.8, stamina_mod=1.1)
}

class Ability:
    def __init__(self, name, st_restore=0, damage_mod=1.0, ps_dmg_mod=1.0, cooldown=3, duration=0):
        self.name = name
        self.st_restore = st_restore
        self.damage_mod = damage_mod
        self.ps_dmg_mod = ps_dmg_mod
        self.cooldown = cooldown
        self.duration = duration

ABILITIES = {
    "focus_pulse": Ability("Focus Pulse", st_restore=40, cooldown=4),
    "titan_wrath": Ability("Titan's Wrath", ps_dmg_mod=2.0, cooldown=5, duration=2),
    "overdrive": Ability("Overdrive", cooldown=6, duration=1) # Acting multiple times
}

class Entity:
    def __init__(self, name, hp=100, stamina=100):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.max_stamina = stamina
        self.stamina = stamina
        self.max_posture = 100
        self.posture = 0

        self.is_defending = False
        self.is_staggered = False
        self.stagger_turns = 0
        
        self.shield = None
        self.ability = None
        self.ability_cooldown = 0
        self.ability_duration = 0
        self.active_buffs = []

    def take_damage(self, damage, posture_damage=0, multiplier=1.0):
        # Apply shield posture resistance if applicable
        if self.shield:
            posture_damage *= self.shield.posture_resistance

        self.hp -= int(damage * multiplier)
        self.posture += int(posture_damage * multiplier)

        if self.hp < 0: self.hp = 0
        if self.posture >= self.max_posture:
            self.posture = self.max_posture
            self.trigger_stagger()

    def trigger_stagger(self):
        self.is_staggered = True
        self.stagger_turns = 1

    def recover_resources(self, st_amount=15, ps_amount=10):
        # 1. Handle Stagger
        if self.is_staggered:
            self.stagger_turns -= 1
            if self.stagger_turns <= 0:
                self.is_staggered = False
                self.posture = 0
            return

        # 2. Handle Buff Durations
        if self.ability_duration > 0:
            self.ability_duration -= 1
            if self.ability_duration == 0:
                self.active_buffs = [] # Clear buffs when duration ends

        # 3. Standard Recovery
        self.stamina += st_amount
        if self.stamina > self.max_stamina:
            self.stamina = self.max_stamina
            
        self.posture -= ps_amount
        if self.posture < 0:
            self.posture = 0
            
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1

    def use_stamina(self, amount):
        cost = amount
        if self.shield:
            cost *= self.shield.stamina_mod
        
        if self.stamina >= cost:
            self.stamina -= cost
            return True
        return False

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):
        return self.hp > 0

    def reset(self):
        self.hp = self.max_hp
        self.stamina = self.max_stamina
        self.posture = 0
        self.is_defending = False
        self.is_staggered = False
        self.stagger_turns = 0
        self.ability_cooldown = 0
        self.heavy_uses = 3
