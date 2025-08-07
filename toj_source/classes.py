#!/usr/bin/env python3
from math_operations import percentage

class Player:
    """
    Classe base para todos os jogadores.
    Contém atributos e métodos comuns a todas as classes de personagens.
    """
    def __init__(self, nick_name):
        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        # avg_damage será definido nas subclasses onde _st e _mg existem
        self.avg_damage = 0
        self.kill_streak = 0
        self.wins = 0
        self.coins = 0
        self.skill_points = 0
        # Corrigido o erro de digitação "sdfaBody" para "Body"
        self.inventory = {"Weapon": None, "Helmet": None,
                          "Body": None, "Legs": None,
                          "Shoes": None}
        self.skills = {1: None, 2: None, 3: None, 4: None}

    def get_coins(self):
        return self.coins

    def set_coins(self, amount):
        self.coins = amount

    def receive_coins(self, amount):
        self.coins += amount

    def win(self):
        self.wins += 1

    def get_kill_streak(self):
        return self.kill_streak

    def add_kill_streak(self):
        self.kill_streak += 1

    def reset_kill_streak(self):
        self.kill_streak = 0
    
    def get_avg_damage(self):
        return self.avg_damage

    def get_isalive(self):
        return self.isalive

    def set_isalive(self, state=True):
        if not isinstance(state, bool):
            raise ValueError("Expected True or False")
        self.isalive = state

    def reduce_hp(self, quantty):
        self._hp -= quantty

    @staticmethod
    def my_type():
        return 'Human'

    def set_xp_points(self, amount):
        self.xp_points = amount

    def add_xp_points(self, amount):
        self.xp_points += amount

    def get_xp_points(self):
        return self.xp_points

    def get_nick_name(self):
        return self.nick_name

    def get_level(self):
        return self.level

    def set_level(self, new_level):
        self.level = new_level

    def need_to_up(self):
        # Fórmula simplificada e mais comum para XP em RPGs
        return int(100 * (self.level ** 1.5))

    def level_up(self, show=True):
        needed_xp = self.need_to_up()
        while self.get_xp_points() >= needed_xp:
            self.set_xp_points(self.xp_points - needed_xp)
            self.level += 1
            self.skill_points += 3
            
            if show:
                print(f"Level up! Agora você está no nível: {self.level}".center(100))

            # Atualiza os atributos base com base na classe
            self._update_stats_on_level_up()
            needed_xp = self.need_to_up() # Recalcula o XP necessário para o próximo nível
        
        if show and self.get_xp_points() < needed_xp:
            print(f"Você precisa de mais {needed_xp - self.get_xp_points()} XP para o próximo nível.".center(100))

    def _update_stats_on_level_up(self):
        """
        Método auxiliar para atualizar os status ao subir de nível.
        Deve ser implementado nas subclasses.
        """
        # Lógica de aumento de status
        class_name = self.get_classname()
        if class_name == 'Warrior':
            self._hp += percentage(17, self._hp, False)
            self._mp += percentage(14, self._mp, False)
            self._st += percentage(13, self._st, False)
            self._ag = min(self._ag + 1, 90)
            self._mg += percentage(12, self._mg, False)
            self._df += percentage(13, self._df, False)
        elif class_name == 'Mage':
            self._hp += percentage(17, self._hp, False)
            self._mp += percentage(15, self._mp, False)
            self._st += percentage(11, self._st, False)
            self._ag = min(self._ag + 1, 90)
            self._mg += percentage(15, self._mg, False)
            self._df += percentage(11, self._df, False)
        elif class_name == 'Rogue':
            # Ajustado para tornar o Rogue mais viável
            self._hp += percentage(15, self._hp, False)
            self._mp += percentage(14, self._mp, False)
            self._st += percentage(16, self._st, False)
            self._ag = min(self._ag + 2, 95) # Aumento maior de agilidade
            self._mg += percentage(12, self._mg, False)
            self._df += percentage(13, self._df, False)
        
        # Atualiza os atributos base e o dano médio
        self.base_hp, self.base_mp, self.base_st = self._hp, self._mp, self._st
        self.base_ag, self.base_mg, self.base_df = self._ag, self._mg, self._df
        self.avg_damage = (self._st + self._mg) // 3

    def need_to_next(self):
        operation = self.need_to_up() - self.get_xp_points()
        return operation if operation > 0 else 0

    def get_level_bar(self):
        needed_xp = self.need_to_up()
        if needed_xp == 0: # Evita divisão por zero se o cálculo de XP for 0
            percent_of_bar = 10 if self.get_xp_points() > 0 else 0
        else:
            percent_of_bar = int((self.get_xp_points() / needed_xp) * 10)

        level_bar = ['[x]' * percent_of_bar, '[ ]' * (10 - percent_of_bar)]
        printable = ''.join(level_bar)
        return f"|{printable}|"
            
    def rest(self):
        self._hp, self._mp = self.base_hp, self.base_mp
        self.set_isalive(True)
        #TODO: resetar o cooldown das habilidades

    def equip_a_gun(self, gun):
        if gun.is_equipped():
            print('Alguém já está usando esta arma'.center(100))
            return
        if gun.get_wp_level() > self.get_level():
            print(f'Você precisa de nível -> {gun.get_wp_level()} para usar esta arma'.center(100))
            return
        if self.get_classname() not in gun.classes:
            print(f'Você precisa ser {" ou ".join(gun.get_lst_class())}'.center(100))
            return

        self._mg += gun.get_mg()
        self._st += gun.get_st()
        self._ag += gun.get_ag()
        self.avg_damage += gun.avg_dmg
        gun.set_equipped()
        self.inventory["Weapon"] = gun.name
        print(f'Parabéns {self.get_nick_name()}, agora você tem {gun.name}'.center(100))

    def equip_a_armor(self, ar):
        if ar.is_equipped():
            print(f'Alguém já está usando esta armadura'.center(100))
            return
        if ar.get_ar_level() > self.get_level():
            print(f'Você precisa de nível -> {ar.get_ar_level()} para usar esta armadura'.center(100))
            return
        if self.get_classname() not in ar.classes:
            print(f'Você precisa ser {" ou ".join(ar.get_lst_class())}'.center(100))
            return
            
        self._df += ar.get_df()
        ar.set_equipped()
        self.inventory[ar.in_space()] = ar.name
        print(f'Parabéns {self.get_nick_name()}, agora você tem: {ar.name}'.center(100))

class Warrior(Player):
    base_hp, base_mp, base_st = 104, 89, 104
    base_ag, base_mg, base_df = 3, 30, 30

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = self.base_hp, self.base_mp, self.base_st
        self._ag, self._mg, self._df = self.base_ag, self.base_mg, self.base_df
        super().__init__(nick_name)
        self.avg_damage = (self._st + self._mg) // 3

    @staticmethod
    def get_classname():
        return 'Warrior'
    # Getters e Setters ...
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self._st
    def get_ag(self): return self._ag
    def get_mg(self): return self._mg
    def get_df(self): return self._df
    def set_hp(self, new_hp): self._hp = new_hp
    def set_mp(self, new_mp): self._mp = new_mp
    def set_st(self, new_st): self._st = new_st
    def set_ag(self, new_ag): self._ag = new_ag
    def set_mg(self, new_mg): self._mg = new_mg
    def set_df(self, new_df): self._df = new_df

class Mage(Player):
    base_hp, base_mp, base_st = 96, 100, 32
    base_ag, base_mg, base_df = 3, 100, 23

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = self.base_hp, self.base_mp, self.base_st
        self._ag, self._mg, self._df = self.base_ag, self.base_mg, self.base_df
        super().__init__(nick_name)
        self.avg_damage = (self._st + self._mg) // 3

    @staticmethod
    def get_classname():
        return 'Mage'
    # Getters e Setters ...
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self._st
    def get_ag(self): return self._ag
    def get_mg(self): return self._mg
    def get_df(self): return self._df
    def set_hp(self, new_hp): self._hp = new_hp
    def set_mp(self, new_mp): self._mp = new_mp
    def set_st(self, new_st): self._st = new_st
    def set_ag(self, new_ag): self._ag = new_ag
    def set_mg(self, new_mg): self._mg = new_mg
    def set_df(self, new_df): self._df = new_df

class Rogue(Player):
    base_hp, base_mp, base_st = 99, 30, 67
    base_ag, base_mg, base_df = 10, 66, 20

    def __init__(self, nick_name):
        self._hp, self._mp, self._st = self.base_hp, self.base_mp, self.base_st
        self._ag, self._mg, self._df = self.base_ag, self.base_mg, self.base_df
        super().__init__(nick_name)
        self.avg_damage = (self._st + self._mg) // 3

    @staticmethod
    def get_classname():
        return 'Rogue'
    # Getters e Setters ...
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self._st
    def get_ag(self): return self._ag
    def get_mg(self): return self._mg
    def get_df(self): return self._df
    def set_hp(self, new_hp): self._hp = new_hp
    def set_mp(self, new_mp): self._mp = new_mp
    def set_st(self, new_st): self._st = new_st
    def set_ag(self, new_ag): self._ag = new_ag
    def set_mg(self, new_mg): self._mg = new_mg
    def set_df(self, new_df): self._df = new_df

class Monster:
    base_hp, base_mp, base_st = 100, 40, 55
    base_ag, base_mg, base_df = 3, 50, 30

    def __init__(self, nick_name, mob_level=1):
        self.nick_name = nick_name
        self.level = max(1, mob_level) # Garante que o nível mínimo é 1
        self.isalive = True
        
        # Inicializa os atributos base
        self._hp = self.base_hp
        self._mp = self.base_mp
        self._st = self.base_st
        self._ag = self.base_ag
        self._mg = self.base_mg
        self._df = self.base_df

        # Aumenta os atributos com base no nível
        for _ in range(self.level):
            if 1 <= self.level < 10:
                self._hp += percentage(10, self._hp, False)
                self._st += percentage(8, self._st, False)
                self._df += percentage(10, self._df, False)
            elif 10 <= self.level < 20:
                self._hp += percentage(11, self._hp, False)
                self._st += percentage(11, self._st, False)
                self._df += percentage(13, self._df, False)
            else: # Nível 20+
                self._hp += percentage(15, self._hp, False)
                self._st += percentage(15, self._st, False)
                self._df += percentage(15, self._df, False)
                self._ag = min(self._ag + 1, 60)

        self.base_hp = self._hp # Define o HP base após os cálculos
        self.avg_damage = (self._st + self._mg) // 3

    def get_avg_damage(self):
        return self.avg_damage

    def reduce_hp(self, quantty):
        self._hp -= quantty

    @staticmethod
    def my_type():
        return 'COM'

    @staticmethod
    def get_classname():
        return 'Monster'
    # Getters e Setters ...
    def get_level(self): return self.level
    def set_isalive(self, state=True): self.isalive = state
    def get_isalive(self): return self.isalive
    def set_level(self, new_level): self.level = new_level
    def get_hp(self): return self._hp
    def get_mp(self): return self._mp
    def get_st(self): return self._st
    def get_ag(self): return self._ag
    def get_mg(self): return self._mg
    def get_df(self): return self._df
    def set_hp(self, new_hp): self._hp = new_hp
    def set_mp(self, new_mp): self._mp = new_mp
    def set_st(self, new_st): self._st = new_st
    def set_ag(self, new_ag): self._ag = new_ag
    def set_mg(self, new_mg): self._mg = new_mg
    def set_df(self, new_df): self._df = new_df

    def restart(self):
        self._hp = self.base_hp
        self.set_isalive(True)

def get_hp_bar(entt):
    if entt.base_hp == 0:
        percent_of_bar = 0
    else:
        # Garante que o HP não seja negativo para o cálculo
        current_hp = max(0, entt.get_hp())
        percent_of_bar = int((current_hp / entt.base_hp) * 10)
    
    # Previne IndexError garantindo que o percentual não exceda 10
    percent_of_bar = min(percent_of_bar, 10)

    hp_bar_fill = "[#]" * percent_of_bar
    hp_bar_empty = "[ ]" * (10 - percent_of_bar)
    printable = hp_bar_fill + hp_bar_empty
    
    return f'|{printable}| {entt.get_hp()}/{entt.base_hp} HP'

def compare(ennt1, ennt2):
    print(f'Classe |{ennt1.get_classname():<7} X {ennt2.get_classname():>7}| Classe'.center(102))
    print(f'Nível  |{ennt1.get_level():<7} X {ennt2.get_level():>7}| Nível'.center(100))
    print(f"Dano Médio |{ennt1.avg_damage:<7} X {ennt2.avg_damage:>7}| Dano Médio".center(100))
    print(f"HP     |{ennt1.get_hp():<7} X {ennt2.get_hp():>7}| HP".center(100))
    print(f'MP     |{ennt1.get_mp():<7} X {ennt2.get_mp():>7}| MP'.center(100))
    print(f'Força  |{ennt1.get_st():<7} X {ennt2.get_st():>7}| Força'.center(100))
    print(f'Agil.  |{ennt1.get_ag():<7} X {ennt2.get_ag():>7}| Agil.'.center(100))
    print(f'Magia  |{ennt1.get_mg():<7} X {ennt2.get_mg():>7}| Magia'.center(100))
    print(f'Defesa |{ennt1.get_df():<7} X {ennt2.get_df():>7}| Defesa'.center(100))

def show_status(ennt1):
    print(f'--- Status de {ennt1.get_nick_name()} ---')
    print (f'Classe: {ennt1.get_classname()}')
    print(f'Nível: {ennt1.get_level()}')
    print(f"Dano Médio: {ennt1.avg_damage}")
    print(f"HP: {ennt1.get_hp()}/{ennt1.base_hp}")
    print(f'MP: {ennt1.get_mp()}/{ennt1.base_mp}')
    print(f'Força: {ennt1.get_st()}')
    print(f'Agilidade: {ennt1.get_ag()}')
    print(f'Magia: {ennt1.get_mg()}')
    print(f'Defesa: {ennt1.get_df()}')
    print(f'XP: {ennt1.get_xp_points()}/{ennt1.need_to_up()}')
    print(f'Barra de XP: {ennt1.get_level_bar()}')
    print('--------------------')
