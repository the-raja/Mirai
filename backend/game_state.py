from engine.entities import Entity
from ai.behavior_tracker import BehaviorTracker
from ai.player_model import PlayerModel
from ai.strategy_engine import StrategyEngine
from ai.prediction_engine import PredictionEngine
from ai.memory_engine import MemoryEngine
from ai.embedding_engine import EmbeddingEngine
from ai.vector_memory import VectorMemory
from ai.emotional_engine import EmotionalEngine
from llm.dialogue_engine import DialogueEngine

memory_engine = MemoryEngine()
player = Entity("Player")
boss = Entity("MIRAI")
dialogue_engine = DialogueEngine()
tracker = BehaviorTracker()
model = PlayerModel()
emotion = EmotionalEngine()

strategy_engine = StrategyEngine()
prediction_engine = PredictionEngine()

embedding_engine = EmbeddingEngine()
vector_memory = VectorMemory()