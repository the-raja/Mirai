from fastapi import APIRouter
from pydantic import BaseModel

from engine.combat import resolve_turn
from engine.entities import SHIELDS, ABILITIES

from game_state import (
    player,
    boss,
    tracker,
    model,
    strategy_engine,
    prediction_engine,
    memory_engine,
    embedding_engine,
    vector_memory,
    dialogue_engine,
    emotion,
    trap_engine
)

router = APIRouter()

class SetupRequest(BaseModel):
    shield_name: str
    ability_name: str

# =========================================================
# TACTICAL SETUP ENDPOINT (Phase 2)
# =========================================================

@router.post("/setup")
def setup_combat(req: SetupRequest):
    # Reset entities
    player.reset()
    boss.reset()
    tracker.reset()
    trap_engine.reset_trap()

    # Assign Player Loadout
    if req.shield_name in SHIELDS:
        player.shield = SHIELDS[req.shield_name]
    if req.ability_name in ABILITIES:
        player.ability = ABILITIES[req.ability_name]

    # AI Boss Selection (Dynamic counter-pick logic)
    if req.shield_name == "greatshield":
        boss.shield = SHIELDS["buckler"]
        boss.ability = ABILITIES["titan_wrath"]
    else:
        boss.shield = SHIELDS["greatshield"]
        boss.ability = ABILITIES["overdrive"]

    analysis = strategy_engine.analyze_loadout(player.shield, player.ability)
    
    dialogue = dialogue_engine.generate_dialogue(
        "Initial Contact",
        tracker.get_behavior_summary(),
        0,
        f"ANALYZING {player.shield.name.upper()}"
    )

    return {
        "message": "Tactical Link Established.",
        "analysis": analysis,
        "boss_dialogue": dialogue,
        "boss_shield": boss.shield.name,
        "boss_ability": boss.ability.name
    }

# =========================================================
# PLAYER MODEL ENDPOINT
# =========================================================

@router.get("/player-model")
def get_player_model():

    summary = tracker.get_behavior_summary()

    classification = model.classify(summary)

    return {

        "player_type": classification,

        "behavior_summary": summary
    }


# =========================================================
# BEHAVIOR SUMMARY ENDPOINT
# =========================================================

@router.get("/behavior")
def get_behavior():

    return tracker.get_behavior_summary()


# =========================================================
# GAME STATE ENDPOINT
# =========================================================

@router.get("/state")
def get_state():

    return {

        "player_hp": player.hp,

        "boss_hp": boss.hp,
        "player_stamina": player.stamina,
        "boss_stamina": boss.stamina,
        "player_posture": player.posture,
        "boss_posture": boss.posture,

        "behavior_summary":
            tracker.get_behavior_summary()
    }


# =========================================================
# MEMORY ENDPOINT
# =========================================================

@router.get("/memory")
def get_memory():

    memory = memory_engine.get_player_memory(
        "player_1"
    )

    return memory


# =========================================================
# RESET ENDPOINT
# =========================================================

@router.post("/reset")
def reset_game():
    player.reset()
    boss.reset()
    tracker.reset()
    trap_engine.reset_trap()
    return {"message": "Game Reset"}


# =========================================================
# MAIN ACTION ENDPOINT
# =========================================================

@router.post("/action/{action_name}")
def player_action(action_name: str):

    # =====================================================
    # GAME OVER CHECK
    # =====================================================

    if not player.is_alive() or not boss.is_alive():
        return {"message": "Game Over"}

    # =====================================================
    # 1. AI OBSERVATION (BEFORE DAMAGE)
    # =====================================================

    summary = tracker.get_behavior_summary()
    player_type = model.classify(summary)
    
    # Update Trap State based on player's reaction
    trap_engine.update_trap_state(action_name)
    
    behavior_vector = embedding_engine.create_behavior_vector(summary)
    similar_fights = vector_memory.find_similar_fights(behavior_vector)
    predicted_move = prediction_engine.predict_next_move(tracker.move_history)

    # =====================================================
    # 2. DECISION PHASE (BOTH SIDES CHOOSE)
    # =====================================================

    # Build state snapshots for the AI
    player_state = {
        "hp": player.hp,
        "stamina": player.stamina,
        "posture": player.posture,
        "is_staggered": player.is_staggered,
        "shield_type": player.shield.name if player.shield else None
    }
    boss_state = {
        "hp": boss.hp,
        "stamina": boss.stamina,
        "posture": boss.posture,
        "is_staggered": boss.is_staggered
    }

    # Get emotional state and modifiers BEFORE resolution
    current_emotion, boss_mods = emotion.get_state()

    boss_action = strategy_engine.choose_strategy(
        player_type,
        summary,
        player_state,
        boss_state,
        predicted_move,
        trap_engine,
        similar_fights
    )

    # =====================================================
    # 3. RESOLUTION
    # =====================================================

    combat_results = resolve_turn(player, action_name, boss, boss_action, b_mods=boss_mods)

    # =====================================================
    # 4. EMOTION UPDATE (Update state for the NEXT turn)
    # =====================================================
    
    # Was our prediction correct? 
    prediction_hit = (predicted_move == action_name)
    player_bluffed = (action_name == "bluff")
    
    emotion.update(boss.hp, player.hp, prediction_hit, player_bluffed)
    new_emotion, _ = emotion.get_state()

    # =====================================================
    # 5. POST-ACTION UPDATES
    # =====================================================

    tracker.track_move(action_name, player.hp)
    new_summary = tracker.get_behavior_summary()

    # Memory
    memory = memory_engine.get_player_memory("player_1")
    familiarity = memory.get("matches", 0) if memory else 0

    memory_data = {
        "player_type": player_type,
        "behavior_summary": new_summary,
        "predicted_move": predicted_move,
        "matches": familiarity + 1,
        "vector": behavior_vector
    }

    # Save to short-term/meta memory
    memory_engine.save_memory("player_1", memory_data)
    
    # Save to long-term HNSW vector memory
    vector_memory.save_vector(memory_data)

    # Dialogue with Emotion
    dialogue = dialogue_engine.generate_dialogue(
        player_type,
        new_summary,
        familiarity,
        f"{predicted_move} (MIRAI IS {new_emotion})"
    )
    
    # Response
    return {
        "player_result": combat_results["player"],
        "boss_result": combat_results["boss"],
        "player_hp": player.hp,
        "boss_hp": boss.hp,
        "player_stamina": player.stamina,
        "boss_stamina": boss.stamina,
        "player_posture": player.posture,
        "boss_posture": boss.posture,
        "player_is_staggered": player.is_staggered,
        "boss_is_staggered": boss.is_staggered,
        "player_type": player_type,
        "predicted_move": predicted_move,
        "boss_action": boss_action,
        "trap_status": trap_engine.get_status(),
        "familiarity": familiarity,
        "behavior_vector": behavior_vector,
        "dialogue": dialogue,
        "emotion": new_emotion,
        "game_over": (not player.is_alive() or not boss.is_alive()),
        "winner": ("player" if boss.hp <= 0 else "boss" if player.hp <= 0 else None)
    }
