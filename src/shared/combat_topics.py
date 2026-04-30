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
