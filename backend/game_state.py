from engine.entities import Entity, SHIELDS, ABILITIES
from ai.behavior_tracker import BehaviorTracker
from ai.player_model import PlayerModel
from ai.strategy_engine import StrategyEngine
from ai.prediction_engine import PredictionEngine
from ai.memory_engine import MemoryEngine
from ai.embedding_engine import EmbeddingEngine
from ai.vector_memory import VectorMemory
from ai.emotional_engine import EmotionalEngine
from ai.trap_engine import TrapEngine
from llm.dialogue_engine import DialogueEngine

memory_engine = MemoryEngine()
player = Entity("Player")
player.shield = SHIELDS["buckler"]
player.ability = ABILITIES["focus_pulse"]

boss = Entity("MIRAI")
boss.shield = SHIELDS["greatshield"]
boss.ability = ABILITIES["overdrive"]

dialogue_engine = DialogueEngine()
tracker = BehaviorTracker()
model = PlayerModel()
emotion = EmotionalEngine()
trap_engine = TrapEngine()

strategy_engine = StrategyEngine()
prediction_engine = PredictionEngine()

embedding_engine = EmbeddingEngine()
vector_memory = VectorMemory()