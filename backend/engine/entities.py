class Entity:

    def __init__(self, name, hp=100):

        self.name = name
        self.max_hp = hp
        self.hp = hp

        self.is_defending = False
        self.heavy_uses = 3

    def take_damage(self, damage):

        self.hp -= damage

        if self.hp < 0:
            self.hp = 0

    def heal(self, amount):

        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def is_alive(self):

        return self.hp > 0

    def reset(self):
        self.hp = self.max_hp
        self.is_defending = False
        self.heavy_uses = 3