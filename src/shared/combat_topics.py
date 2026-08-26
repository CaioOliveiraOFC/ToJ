"""Tópicos do EventBus para combate (importáveis por `mechanics/` sem acoplar `engine/`)."""

# Eventos de combate
COMBAT_PHYSICAL_STRIKE = "combat.physical_strike"
COMBAT_SKILL_OUTCOME = "combat.skill_outcome"
COMBAT_SKILL_CAST = "combat.skill_cast"
COMBAT_TURN_EFFECT = "combat.turn_effect"
COMBAT_FLEE_RESULT = "combat.flee_result"

# Eventos de sistema/log (para notificações da UI)
SYSTEM_LOG_MESSAGE = "system.log_message"
SYSTEM_SAVE_SUCCESS = "system.save_success"
SYSTEM_SAVE_ERROR = "system.save_error"

# Eventos de UI (engine → ui via EventBus)
UI_OPEN_INVENTORY = "ui.open_inventory"
UI_OPEN_SHOP = "ui.open_shop"
UI_OPEN_PASSIVES = "ui.open_passives"
UI_OPEN_SKILLS = "ui.open_skills"
UI_EXTRACTION_PROMPT = "ui.extraction_prompt"
UI_RANDOM_EVENT = "ui.random_event"
UI_GAME_OVER = "ui.game_over"
UI_SAVE_SUCCESS = "ui.save_success"
UI_MAIN_MENU = "ui.main_menu"
UI_CHARACTER_CREATION = "ui.character_creation"
