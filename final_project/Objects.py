from abc import ABC, abstractmethod
import pygame
import random
import numpy as np


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
        size = display.game_engine.sprite_size
        sprite = self.sprite
        coord = self.position
        x = coord[0]
        y = coord[1]
        k = 5
        min_x = k * (x // k)
        min_y = k * (y // k)

        display.blit(sprite, ((coord[0] -min_x)* size, (coord[1] - min_y) * size))


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
            yield "level up!"
            self.level += 1
            self.stats["strength"] += 2
            self.stats["endurance"] += 2
            self.calc_max_HP()
            self.hp = self.max_hp


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
            intl_factor = np.log(1 + enemy_stats['intelligence'] / hero_stats['intelligence'])
            base_factor = enemy_stats['strength'] * enemy_stats['endurance']
            armr_factor = hero_stats['strength'] * hero_stats['endurance']
            damage = crit_factor * intl_factor * base_factor / armr_factor
            return damage

        def new_exp(self, hero):
            ''' Calulates exp for kill Enemy.'''
            return hero.exp + 2 ** (self.exp / (hero.exp + self.exp))

        def score(self, hero):
            return 0.1 * hero.level * self.exp / hero.exp

        hero.exp = new_exp(self, hero)
        hero.hp -= damage(self, hero)
        if hero.hp <= 0.0:
            engine.notify('Game Over')
            engine.working = False
        else:
            hero.level_up()
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


class Berserk(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["Strength"] += 3
        stats["Endurance"] += 3
        stats["Luck"] += 3
        stats["Intelligence"] -= 3
        self.stats = stats
        self.calc_max_HP()
        self.hp = self.max_hp


class Blessing(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["Strength"] += 1
        stats["Endurance"] += 1
        stats["Luck"] += 1
        stats["Intelligence"] += 1
        self.stats = stats
        self.calc_max_HP()
        self.hp = self.max_hp


class Fortunate(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["Luck"] += 5
        self.stats = stats


class Weakness(Effect):
    """ Class of negative effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["Strength"] -= 1
        stats["Endurance"] -= 1
        stats["Luck"] -= 1
        stats["Intelligence"] -= 1
        self.stats = stats
        self.calc_max_HP()
        self.hp = self.max_hp


class Luckless(Effect):
    """ Class of positive effect."""

    def apply_effect(self):
        stats = self.base.stats
        stats["Luck"] -= 2
        self.stats = stats