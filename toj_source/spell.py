from toj_source.math_operations import percentage


class Spell:

    def __init__(self, sk_type, name, classes, level, owner, control=1):
        self.sk_type = sk_type
        self.name = name
        self.owner = owner
        if 'Control' in self.sk_type:
            pass
        if 'Buff' in self.sk_type:
            pass
        if 'Damage' in self.sk_type:
            pass
        self.spell_class = classes
        self.level = level


if __name__ == '__main__':
    pass
