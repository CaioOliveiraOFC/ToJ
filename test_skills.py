"""Teste rápido do sistema de skills."""
import sys
sys.path.insert(0, "src")

from src.content.skills_loader import load_skills, get_initial_skills, generate_skill_choices
from src.entities.heroes import Warrior, Mage, Rogue

def test_load_skills():
    print("=== Teste 1: Carregar skills ===")
    skills = load_skills()
    print(f"Total de skills: {len(skills)}")
    
    # Verifica skills por classe
    for cls in ["Warrior", "Mage", "Rogue"]:
        class_skills = [s for s in skills if s.skill_class == cls]
        initial = [s for s in class_skills if s.is_initial]
        print(f"{cls}: {len(class_skills)} total, {len(initial)} iniciais")
    print()

def test_initial_skills():
    print("=== Teste 2: Skills iniciais ===")
    for cls_name, cls in [("Warrior", Warrior), ("Mage", Mage), ("Rogue", Rogue)]:
        player = cls("Teste")
        initial = get_initial_skills(cls_name)
        print(f"{cls_name}: {len(initial)} skills iniciais")
        for s in initial:
            print(f"  - {s.name} (id: {s.id}, level: {s.level_required})")
    print()

def test_skill_choices():
    print("=== Teste 3: Geração de escolhas ===")
    for cls in ["Warrior", "Mage", "Rogue"]:
        choices = generate_skill_choices(cls, 5, [], count=3)
        print(f"{cls} nível 5: {len(choices)} escolhas")
        for c in choices:
            print(f"  - {c.name} (raridade: {c.rarity}, nível: {c.level_required})")
    print()

def test_player_flow():
    print("=== Teste 4: Fluxo do Player ===")
    player = Warrior("Teste")
    print(f"Criado: {player.get_nick_name()} (Classe: {player.get_classname()})")
    print(f"Skills iniciais: {len(player.skills)}")
    for k, v in player.skills.items():
        print(f"  Slot {k}: {v.name}")
    
    # Simula level up
    print("\nSimulando level up para 2...")
    player.level = 2
    msgs = player.learn_new_skills(show=True)
    for m in msgs:
        print(f"  {m}")
    print(f"Skills agora: {len(player.skills)}")
    print()

if __name__ == "__main__":
    test_load_skills()
    test_initial_skills()
    test_skill_choices()
    test_player_flow()
    print("=== Todos os testes passaram! ===")
