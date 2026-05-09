# MIRAI v2: The Autonomous Adversary Technical Specification
**Project Vision**: To elevate MIRAI from a turn-based boss to a "Cognitive Combatant" inspired by the **NVIDIA ACE / MIR5** architecture—continuously learning, resource-aware, and gear-adaptive.

---

## 1. Core Philosophy: The Autonomous Adversary
Unlike traditional scripted bosses, MIRAI v2 does not follow a decision tree. It operates as an **Autonomous Adversary** that utilizes its high-fidelity memory and **Structural Intelligence** to "Level Up" alongside the player.

---

## 2. The Neural Pipeline (Enhanced)
1.  **Pre-Combat Heuristics**: Analysis of player **Loadout** (Shields, Abilities, Artifacts).
2.  **Behavior Observation**: Real-time tracking of player inputs (Aggression, Defense, Panic, Bluff).
3.  **Kinetic Perception**: Analysis of current **Stamina (ST)** and **Posture (PS)** levels.
4.  **HNSW Vector Retrieval**: Querying the FAISS index for similar historical behavior + gear vectors.
5.  **Markovian Prediction**: N-Gram analysis (N=3) to predict actions with a confidence score.
6.  **Strategic Synthesis**: Combining memory, emotion, and gear-counters to output a tactical action.

---

## 3. The Loadout & Gear System (Structural Intelligence)
The player (and MIRAI) now possesses a "Setup" that dictates their combat style.

### A. Protective Gear (Shields)
*   **Buckler**: +20% Parry Window, -50% Block Efficiency.
*   **Greatshield**: +40% Posture Resistance, +15% Stamina Cost for attacks.
*   **Vanguard Plate**: Reduces damage taken but slows Stamina regeneration.

### B. Special Abilities (The "Trumps")
*   **Focus Pulse**: (Active) Instantly restores 40 ST. (Cooldown: 4 turns).
*   **Overdrive**: (Active) Act 3 times in one turn, but lose 50% current HP.
*   **Counter-Link**: (Passive) Successfully parrying restores 10 HP.

### C. AI Perception of Gear
*   **Loadout Countering**: If a player brings a `Greatshield`, MIRAI’s `StrategyEngine` increases the weight of the `Grab` action (which bypasses shields).
*   **Ability Prediction**: MIRAI tracks the "Cooldown State" of player abilities. If `Focus Pulse` is ready and player ST is low, MIRAI predicts a "Heal/Pulse" action.

---

## 4. Kinetic Resource Engine (The "Body")
### A. Stamina (ST) - 100 Units
*   **Regeneration**: +15 ST/turn (Wait/Defend).
*   **Consumption**: All actions (Attack, Dodge, Ability) cost ST.
### B. Posture (PS) - 100 Units
*   **Stagger State**: At 100 PS, the entity is "Staggered"—skipping 1 turn and taking **1.5x damage**.

---

## 5. Tactical Action Suite (The "Moveset")
| Action | ST Cost | PS Damage | Mechanic |
| :--- | :--- | :--- | :--- |
| **Quick Attack** | 15 | 10 | Low cost poke. |
| **Heavy Strike** | 40 | 35 | Pierces `Defend`. |
| **Parry** | 25 | 50 (Inflicted) | High-reward counter. |
| **Feint** | 20 | 0 | Baits defensive responses. |
| **Grab** | 30 | 45 | Bypasses Shields/Defend. |
| **Use Ability** | Var. | - | Triggers the selected Loadout Trump. |

---

## 6. The Laws of Adaptive Fairness (Anti-Bias)
1.  **Law of Shared Physicality**: MIRAI uses the same ST/PS systems as the player.
2.  **Law of the Transparent HUD**: MIRAI's **Confidence** and **Intent** (e.g., "Countering Shield") are visible.
3.  **Law of Emotional Fallibility**: Frustration (> 0.7) reduces prediction accuracy.
4.  **Law of Loadout Transparency**: MIRAI cannot "hide" its gear; the player can see MIRAI's selected abilities.

---

## 7. Technical Implementation Roadmap

### Phase 1: Structural Refactor (Loadouts)
*   Define `Loadout` and `Ability` classes in `entities.py`.
*   Implement `PreCombatAnalyzer` to set initial AI weights based on gear.

### Phase 2: Kinetic Refactor (Resources)
*   Add `stamina` and `posture` logic to `combat.py`.

### Phase 3: AI Cognitive Expansion
*   **StrategyEngine**: Integrate "Gear-Aware" decision making.
*   **PredictionEngine**: Track player ability cooldowns.

### Phase 4: HUD v2 (Tactical Interface)
*   Add Loadout Selection screen.
*   Display ST/PS bars and Ability Cooldown icons.

---

## 8. Technical Stack
*   **Backend**: FastAPI, Python 3.13, NumPy, FAISS.
*   **AI**: Ollama (Llama 3.2), Markov Chain, Gear-Weighting Heuristics.
*   **Frontend**: Next.js 15, Tailwind 4, Framer Motion.
