from abc import ABC, abstractmethod
import pygame
import random
import numpy as np

def calculate_left_corner(hero, display):
    sprite_size = display.game_engine.sprite_size
    hero_position = hero.position
    x = hero_position[0]
    y = hero_position[1]

    game_screen_size = display.get_size()
    width, length = game_screen_size

    shape_x = width // sprite_size
    shape_y = length // sprite_size
    map_size = 41
    if shape_x//2 <= x <= map_size - shape_x//2:
        min_x = x - shape_x//2
    elif x < shape_x//2:
        min_x = 0
    elif x > map_size - shape_x//2:
        min_x = map_size - shape_x

    if shape_y//2 <= y <= map_size - shape_y//2:
        min_y = y - shape_y//2
    elif y < shape_y//2:
        min_y = 0
    elif y > map_size - shape_y//2:
        min_y = map_size - shape_y

    return (min_x, min_y)

def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class AbstractObject(ABC):

    @abstractmethod
    def __init__(self):
        pass

    def draw(self, display):
        min_x, min_y = calculate_left_corner(self, display)
        size = display.game_engine.sprite_size
        sprite = self.sprite
        coord = self.position
        display.blit(sprite, ((coord[0] - min_x)* size, (coord[1] - min_y) * size))


def create_sprite(img, sprite_size):
    icon = pygame.image.load(img).convert_alpha()
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    return sprite


class Interactive(ABC):

    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):

    def __init__(self, icon, action, position):
        self.sprite = icon
        self.action = action
        self.position = position

    def interact(self, engine, hero):
        self.action(engine, hero)


class Creature(AbstractObject):

    def __init__(self, icon, stats, position):
        self.sprite = icon
        self.stats = stats
        self.position = position
        self.calc_max_HP()
        self.hp = self.max_hp

    def calc_max_HP(self):
        self.max_hp = 5 + self.stats["endurance"] * 2


class Hero(Creature):

    def __init__(self, stats, icon):
        pos = [1, 1]
        self.level = 1
        self.exp = 0
        self.gold = 0
        super().__init__(icon, stats, pos)

    def level_up(self):
        while self.exp >= 100 * (2 ** (self.level - 1)):
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp
            return "level up!"


class Enemy(Creature, Interactive):

    def __init__(self, icon, stats, xp, position):
        # Init from Creature
        super().__init__(icon, stats, position)
        self.exp = xp

    def interact(self, engine, hero):
        def damage(self, hero):
            ''' Calulates damage of Enemy.'''
            hero_stats = hero.stats
            enemy_stats = self.stats
            # Calculation factor of hit
            crit_factor = (1 + random.random() * enemy_stats['luck'] ** 0.5)
            intl_factor = np.log(1 + enemy_stats['intelligence'] / max(1, hero_stats['intelligence']))
            base_factor = enemy_stats['strength'] * enemy_stats['endurance']
            armr_factor = hero_stats['strength'] * hero_stats['endurance']
            damage = crit_factor * intl_factor * base_factor / max(1,armr_factor)
            return max(1, damage)

        def new_exp(self, hero):
            ''' Calulates exp for kill Enemy.'''
            return hero.exp + (self.exp // 2)

        def score(self, hero):
            return round(10*hero.level*self.exp / max(1,hero.exp), 2)

        hero.exp = new_exp(self, hero)
        hero.hp -= int(damage(self, hero))
        if hero.hp <= 0.0:
            engine.notify('Game Over')
            engine.working = False

        if hero.level_up():
            engine.notify('Enemy killed!')
            engine.notify('Level Up!')
        else:
            engine.notify('Enemy killed!')
            engine.notify('Damage recieved {}'.format(int(damage(self, hero))))
        engine.score += score(self, hero)

class Effect(Hero):

    def __init__(self, base):
        self.base = base
        self.stats = self.base.stats.copy()
        self.apply_effect()

    @property
    def position(self):
        return self.base.position

    @position.setter
    def position(self, value):
        self.base.position = value

    @property
    def level(self):
        return self.base.level

    @level.setter
    def level(self, value):
        self.base.level = value

    @property
    def gold(self):
        return self.base.gold

    @gold.setter
    def gold(self, value):
        self.base.gold = value

    @property
    def hp(self):
        return self.base.hp

    @hp.setter
    def hp(self, value):
        self.base.hp = value

    @property
    def max_hp(self):
        return self.base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self.base.max_hp = value

    @property
    def exp(self):
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self.base.exp = value

    @property
    def sprite(self):
        return self.base.sprite

    @abstractmethod
    def apply_effect(self):
        pass

    @abstractmethod
    def notify_effect(self):
        pass


class Berserk(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["strength"] += 3
        stats["endurance"] += 3
        stats["luck"] += 3
        stats["intelligence"] -= 3
        self.stats = stats
        self.calc_max_HP()
        self.hp = self.max_hp

    def notify_effect(self):
        return 'Berserk Effect !'


class Blessing(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["strength"] += 1
        stats["endurance"] += 1
        stats["luck"] += 1
        stats["intelligence"] += 1
        self.stats = stats
        self.calc_max_HP()
        self.hp = self.max_hp

    def notify_effect(self):
        return 'Blessing Effect !'


class Fortunate(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["luck"] += 5
        self.stats = stats

    def notify_effect(self):
        return 'Fortunate Effect !'

class Weakness(Effect):
    """ Class of negative effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["strength"] -= 1
        stats["endurance"] -= 1
        stats["luck"] -= 1
        stats["intelligence"] -= 1
        self.stats = stats
        self.calc_max_HP()
        self.hp = self.max_hp

    def notify_effect(self):
        return 'Weakness Effect !'

class Luckless(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["Luck"] -= 2
        self.stats = stats

    def notify_effect(self):
        return 'Luckless Effect !'