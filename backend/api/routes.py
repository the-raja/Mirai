from fastapi import APIRouter

from engine.combat import process_action

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
    emotion
)

router = APIRouter()


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
    behavior_vector = embedding_engine.create_behavior_vector(summary)
    similar_fights = vector_memory.find_similar_fights(behavior_vector)
    predicted_move = prediction_engine.predict_next_move(tracker.move_history)

    # =====================================================
    # 2. DECISION PHASE (BOTH SIDES CHOOSE)
    # =====================================================

    if action_name == "heavy" and player.heavy_uses <= 0:
        action_name = "attack"
        
    boss_action = strategy_engine.choose_strategy(
        player_type,
        summary,
        boss.heavy_uses,
        player.hp,
        boss.hp,
        similar_fights
    )

    # Set defense states
    player.is_defending = (action_name == "defend")
    boss.is_defending = (boss_action == "defend")
    
    # Decrement uses
    if action_name == "heavy":
        player.heavy_uses -= 1
    if boss_action == "heavy":
        boss.heavy_uses -= 1

    # =====================================================
    # 3. RESOLUTION
    # =====================================================

    player_result = process_action(player, boss, action_name)
    boss_result = process_action(boss, player, boss_action)

    # =====================================================
    # 4. EMOTION UPDATE
    # =====================================================
    
    # Was our prediction correct? 
    prediction_hit = (predicted_move == action_name)
    player_bluffed = (action_name == "bluff")
    
    emotion.update(boss.hp, player.hp, prediction_hit, player_bluffed)
    current_emotion = emotion.get_state()

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
        f"{predicted_move} (MIRAI IS {current_emotion})"
    )
    
    # Response
    return {
        "player_result": player_result,
        "boss_result": boss_result,
        "player_hp": player.hp,
        "boss_hp": boss.hp,
        "player_heavy_uses": player.heavy_uses,
        "boss_heavy_uses": boss.heavy_uses,
        "player_type": player_type,
        "predicted_move": predicted_move,
        "boss_action": boss_action,
        "familiarity": familiarity,
        "behavior_vector": behavior_vector,
        "dialogue": dialogue,
        "emotion": current_emotion,
        "game_over": (not player.is_alive() or not boss.is_alive()),
        "winner": ("player" if boss.hp <= 0 else "boss" if player.hp <= 0 else None)
    }
