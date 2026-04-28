# this module is dedicated to the creation of math functions
def percentage(percent, whole, remainder=True):
    # Calculate the percentage of a whole number
    if remainder:
        operation = (percent * whole) / 100
    else:
        operation = (percent * whole) // 100
    return operation

def calculate_monster_hp(monster_level):
    base_hp = 70 # Slightly reduced base HP
    scaling_per_level = 20 # Slightly reduced scaling
    return base_hp + (monster_level - 1) * scaling_per_level

def calculate_monster_strength(monster_level):
    base_strength = 25 # Further reduced base strength
    scaling_per_level = 15 # Further reduced scaling
    return base_strength + (monster_level - 1) * scaling_per_level

def calculate_monster_defense(monster_level):
    base_defense = 20 # Slightly reduced base defense
    scaling_per_level = 8 # Slightly reduced scaling
    return base_defense + (monster_level - 1) * scaling_per_level

def calculate_monster_magic(monster_level):
    base_magic = 40 # Slightly reduced base magic
    scaling_per_level = 12 # Slightly reduced scaling
    return base_magic + (monster_level - 1) * scaling_per_level

def calculate_xp_for_next_level(current_level):
    # XP needed to reach the next level
    # Formula: initial_xp_cost + (current_level - 1) * xp_growth_per_level
    initial_xp_cost = 3000 # Significantly increased to slow down XP gain
    xp_growth_per_level = 750 # Significantly increased to slow down XP gain
    return initial_xp_cost + (current_level - 1) * xp_growth_per_level

def calculate_monster_xp_reward(monster_level):
    # XP awarded for defeating a monster
    base_xp_reward = 50 # Slightly reduced base XP reward
    xp_scaling_per_level = 20 # Slightly reduced XP scaling
    return base_xp_reward + (monster_level - 1) * xp_scaling_per_level

def calculate_mini_boss_hp(dungeon_level):
    # Mini-bosses are tougher, let's make their effective level higher than regular monsters
    mini_boss_effective_level = dungeon_level + 2 # Mini-boss is effectively 2 levels higher than regular monsters at this floor
    base_hp = 150 # Higher base HP for mini-boss, adjusted
    scaling_per_level = 40 # More aggressive HP scaling, adjusted
    return base_hp + (mini_boss_effective_level - 1) * scaling_per_level

def calculate_mini_boss_strength(dungeon_level):
    mini_boss_effective_level = dungeon_level + 2
    base_strength = 80 # Higher base strength for mini-boss, adjusted
    scaling_per_level = 30 # More aggressive strength scaling, adjusted
    return base_strength + (mini_boss_effective_level - 1) * scaling_per_level

def calculate_mini_boss_defense(dungeon_level):
    mini_boss_effective_level = dungeon_level + 2
    base_defense = 45 # Higher base defense for mini-boss, adjusted
    scaling_per_level = 10 # More aggressive defense scaling, adjusted
    return base_defense + (mini_boss_effective_level - 1) * scaling_per_level

def calculate_mini_boss_magic(dungeon_level):
    mini_boss_effective_level = dungeon_level + 2
    base_magic = 75 # Higher base magic for mini-boss, adjusted
    scaling_per_level = 18 # More aggressive magic scaling, adjusted
    return base_magic + (mini_boss_effective_level - 1) * scaling_per_level

def calculate_mini_boss_xp_reward(dungeon_level):
    mini_boss_effective_level = dungeon_level + 2
    base_xp_reward = 120 # Much higher XP reward for mini-boss, adjusted
    xp_scaling_per_level = 25 # More aggressive XP scaling, adjusted
    return base_xp_reward + (mini_boss_effective_level - 1) * xp_scaling_per_level

if __name__ == "__main__":
    # Test monster scaling
    print("--- Monster Scaling Tests ---")
    for level in range(1, 10):
        print(f"Level {level}: HP={calculate_monster_hp(level)}, Str={calculate_monster_strength(level)}, Def={calculate_monster_defense(level)}, Mag={calculate_monster_magic(level)}")

    # Test mini-boss scaling
    print("\n--- Mini-Boss Scaling Tests (for dungeon_level) ---")
    for d_level in range(5, 16, 5): # Test at dungeon levels 5, 10, 15
        print(f"Dungeon Level {d_level} (Mini-Boss Effective Level {d_level+2}): HP={calculate_mini_boss_hp(d_level)}, Str={calculate_mini_boss_strength(d_level)}, Def={calculate_mini_boss_defense(d_level)}, Mag={calculate_mini_boss_magic(d_level)}, XP={calculate_mini_boss_xp_reward(d_level)}")

    # Test XP Curve
    print("\n--- XP Curve Tests ---")
    for level in range(1, 10):
        print(f"To reach Level {level+1}: {calculate_xp_for_next_level(level)} XP")

    # Test Monster XP Reward
    print("\n--- Monster XP Reward Tests ---")
    for level in range(1, 10):
        print(f"Level {level} Monster XP Reward: {calculate_monster_xp_reward(level)} XP")
