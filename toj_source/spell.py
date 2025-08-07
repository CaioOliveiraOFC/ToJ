from .math_operations import percentage

class Spell:
    """
    Classe para gerenciar feitiços e suas propriedades.
    """
    def __init__(self, sk_type, name, classes, level, owner, control=1):
        self.sk_type = sk_type # Pode ser 'Damage', 'Buff', 'Control', etc.
        self.name = name
        self.owner = owner
        self.spell_class = classes
        self.level = level

        # A lógica específica para cada tipo de feitiço pode ser adicionada aqui.
        if 'Control' in self.sk_type:
            # Ex: self.duration = 2 * level
            pass
        if 'Buff' in self.sk_type:
            # Ex: self.stat_increase = percentage(10 * level, owner.get_st())
            pass
        if 'Damage' in self.sk_type:
            # Ex: self.base_damage = 20 * level
            pass

if __name__ == '__main__':
    pass
