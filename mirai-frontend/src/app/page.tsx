"use client";

import { useState, useEffect, useRef } from "react";

interface LogEntry {
  time: string;
  source: "SYS" | "MIR" | "DIALOGUE";
  text: string;
}

interface GameState {
  player_hp: number;
  boss_hp: number;
  player_stamina: number;
  boss_stamina: number;
  player_posture: number;
  boss_posture: number;
  player_is_staggered: boolean;
  boss_is_staggered: boolean;
  player_type: string;
  predicted_move: string | null;
  boss_action: string;
  trap_status: string;
  familiarity: number;
  dialogue: string;
  emotion: string;
  player_result: string;
  boss_result: string;
  game_over: boolean;
  winner: string | null;
  behavior_vector: number[];
  similar_fights: any[];
}

export default function MiraiGame() {
  const [phase, setPhase] = useState<"setup" | "combat">("setup");
  const [selectedShield, setSelectedShield] = useState("buckler");
  const [selectedAbility, setSelectedAbility] = useState("focus_pulse");
  const [setupData, setSetupData] = useState<any>(null);

  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showThoughtProcess, setShowThoughtProcess] = useState(false);
  const [battleLog, setBattleLog] = useState<LogEntry[]>([]);
  const [isDamaged, setIsDamaged] = useState(false);
  const [isShake, setIsShake] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [battleLog]);

  const getTime = () => {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
  };

  const triggerShake = () => {
    setIsShake(true);
    setTimeout(() => setIsShake(false), 300);
  };

  const handleSetup = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/setup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ shield_name: selectedShield, ability_name: selectedAbility }),
      });
      const data = await response.json();
      setSetupData(data);
      setPhase("combat");
      
      const introLog: LogEntry[] = [
        { time: getTime(), source: "SYS", text: `LINK ESTABLISHED. BOSS_SHIELD: ${data.boss_shield} | BOSS_ABILITY: ${data.boss_ability}` },
        { time: getTime(), source: "DIALOGUE", text: `MIRAI: "${data.boss_dialogue}"` }
      ];
      setBattleLog(introLog);
    } catch (err: any) {
      setError("Setup Link Failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: string) => {
    if (gameState?.game_over) return;
    setLoading(true);
    setIsDamaged(false);
    
    try {
      const response = await fetch(`${API_URL}/action/${action}`, { method: "POST" });
      if (!response.ok) throw new Error("Link Lost.");
      const data: GameState = await response.json();
      
      // Visual Feedback Triggers
      if (gameState && data.player_hp < gameState.player_hp) {
          setIsDamaged(true);
          setTimeout(() => setIsDamaged(false), 500);
          if (gameState.player_hp - data.player_hp > 15 || data.player_is_staggered) triggerShake();
      }

      if (gameState && data.boss_hp < gameState.boss_hp) {
          if (gameState.boss_hp - data.boss_hp > 15 || data.boss_is_staggered) triggerShake();
      }

      if (data.player_result.includes("PARRIES") || data.boss_result.includes("PARRIES")) {
          triggerShake();
      }

      setGameState(data);
      
      const newEntries: LogEntry[] = [
          { time: getTime(), source: "SYS", text: data.player_result },
          { time: getTime(), source: "MIR", text: data.boss_result },
          { time: getTime(), source: "DIALOGUE", text: `MIRAI: "${data.dialogue}"` }
      ];
      setBattleLog(prev => [...prev, ...newEntries]);

    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    setLoading(true);
    try {
      await fetch(`${API_URL}/reset`, { method: "POST" });
      setGameState(null);
      setBattleLog([]);
      setError(null);
      setPhase("setup");
    } catch (err: any) {
      setError("Reset Failed.");
    } finally {
      setLoading(false);
    }
  };

  const similarity = gameState?.similar_fights?.[0] 
    ? Math.round((1 - gameState.similar_fights[0].distance) * 100) 
    : 0;

  const isIrritated = gameState?.emotion === "IRRITATED";

  if (phase === "setup") {
    return (
      <main className="min-h-screen bg-[#020202] text-white p-8 font-mono flex items-center justify-center">
        <div className="w-full max-w-4xl tactical-corner bg-black/80 backdrop-blur-xl p-12 space-y-12 shadow-[0_0_50px_rgba(255,0,0,0.1)]">
          <div className="space-y-2 border-b border-red-600/30 pb-6">
            <h1 className="text-5xl font-black italic tracking-tighter uppercase">Tactical_Briefing</h1>
            <p className="text-[10px] font-bold text-red-500 tracking-[0.5em]">PHASE_01: STRUCTURAL_INDEXING</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div className="space-y-6">
              <label className="text-[11px] font-black tracking-widest text-cyan-500 uppercase">Defensive_Matrix (Shield)</label>
              <div className="grid grid-cols-1 gap-3">
                {[
                  { id: "buckler", name: "Buckler", desc: "+Parry Window | -Block Efficiency" },
                  { id: "greatshield", name: "Greatshield", desc: "+Posture Resistance | +Stamina Cost" },
                  { id: "vanguard", name: "Vanguard Plate", desc: "+Defense | -Stamina Regen" }
                ].map((s) => (
                  <button 
                    key={s.id}
                    onClick={() => setSelectedShield(s.id)}
                    className={`p-4 text-left tactical-corner border transition-all ${selectedShield === s.id ? "border-cyan-500 bg-cyan-500/10 shadow-[0_0_20px_rgba(0,212,255,0.1)]" : "border-white/10 hover:border-white/30"}`}
                  >
                    <p className="text-sm font-black uppercase">{s.name}</p>
                    <p className="text-[9px] text-white/40 font-bold">{s.desc}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-6">
              <label className="text-[11px] font-black tracking-widest text-red-500 uppercase">Special_Ability (Trump)</label>
              <div className="grid grid-cols-1 gap-3">
                {[
                  { id: "focus_pulse", name: "Focus Pulse", desc: "Instant +40 Stamina" },
                  { id: "titan_wrath", name: "Titan's Wrath", desc: "2x Posture Damage (2 turns)" },
                  { id: "overdrive", name: "Overdrive", desc: "Act multiple times per turn" }
                ].map((a) => (
                  <button 
                    key={a.id}
                    onClick={() => setSelectedAbility(a.id)}
                    className={`p-4 text-left tactical-corner border transition-all ${selectedAbility === a.id ? "border-red-600 bg-red-600/10 shadow-[0_0_20px_rgba(255,0,0,0.1)]" : "border-white/10 hover:border-white/30"}`}
                  >
                    <p className="text-sm font-black uppercase">{a.name}</p>
                    <p className="text-[9px] text-white/40 font-bold">{a.desc}</p>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button 
            onClick={handleSetup}
            disabled={loading}
            className="w-full py-6 bg-white text-black font-black uppercase tracking-[0.8em] text-sm hover:bg-cyan-500 transition-all shadow-[0_0_40px_rgba(255,255,255,0.2)]"
          >
            {loading ? "INITIALIZING_LINK..." : "CONFIRM_TACTICAL_LOADOUT"}
          </button>
        </div>
      </main>
    );
  }

  return (
    <main className={`min-h-screen bg-[#020202] text-white p-4 md:p-8 font-mono relative overflow-hidden transition-all duration-150 ${isDamaged ? "damage-flash" : ""} ${isShake ? "screen-shake" : ""}`}>
      
      {/* IMMERSIVE LAYER: SCANLINES & GRID */}
      <div className="fixed inset-0 pointer-events-none z-50">
          <div className="scanline"></div>
          <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.01),rgba(0,255,0,0.01),rgba(0,0,255,0.01))] bg-[length:100%_4px,3px_100%]"></div>
          <div className="absolute inset-0 opacity-[0.03]" style={{ backgroundImage: "radial-gradient(#fff 1px, transparent 0)", backgroundSize: "40px 40px" }}></div>
      </div>

      <div className="w-full max-w-7xl mx-auto space-y-10 relative z-10">
        
        {/* TACTICAL HEADER */}
        <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 p-6 tactical-corner bg-black/40 backdrop-blur-sm">
          <div className="space-y-1">
              <div className="flex items-center gap-3">
                  <div className={`w-3 h-3 bg-red-600 ${isIrritated ? "animate-ping" : "animate-pulse"}`}></div>
                  <h1 className={`text-4xl md:text-6xl font-black tracking-tighter text-white italic leading-none ${isIrritated ? "glitch-text" : ""}`} data-text="MIRAI">MIRAI</h1>
              </div>
              <p className="text-[10px] font-bold text-red-500/80 tracking-[0.4em] uppercase">Memory-Integrated Relational Adaptive Intelligence</p>
          </div>
          <div className="flex flex-col items-end gap-2">
              <div className="flex gap-1">
                  {[...Array(5)].map((_, i) => <div key={i} className="w-1 h-4 bg-red-600/30"></div>)}
                  <div className="w-1 h-4 bg-red-600 animate-bounce"></div>
              </div>
              <button 
                  onClick={() => setShowThoughtProcess(!showThoughtProcess)}
                  className={`text-[9px] font-black tracking-[0.3em] px-6 py-2 border-2 transition-all ${showThoughtProcess ? "bg-cyan-500 border-cyan-400 text-black shadow-[0_0_20px_rgba(0,212,255,0.4)]" : "border-white/10 text-white/40 hover:border-white/40 hover:text-white"}`}
              >
                  {showThoughtProcess ? "TERMINATE_TRACE" : "INITIALIZE_TRACE"}
              </button>
          </div>
        </header>

        <div className="flex flex-col lg:flex-row gap-8">
            
            {/* PRIMARY COMBAT ZONE */}
            <div className={`flex-1 space-y-8 transition-all duration-500 ${showThoughtProcess ? "lg:w-2/3" : "w-full"}`}>
                
                {/* DIALOGUE FEED */}
                <div className="dialogue-box tactical-corner">
                    <div className="absolute top-2 left-2 text-[8px] text-red-500 font-bold tracking-widest opacity-50">ORIGIN:MIRAI_CORE</div>
                    <p className={`text-2xl md:text-4xl leading-tight font-bold text-white uppercase tracking-tight italic ${isIrritated ? "glitch-text" : ""}`} data-text={gameState ? gameState.dialogue : (setupData?.boss_dialogue || "Analyzing Profile...")}>
                        "{gameState ? gameState.dialogue : (setupData?.boss_dialogue || "Analyzing Profile...")}"
                    </p>
                    <div className="absolute bottom-2 right-2 flex gap-1">
                        <div className="w-10 h-1 bg-red-600/20"></div>
                        <div className="w-4 h-1 bg-red-600"></div>
                    </div>
                </div>

                {/* HUD: POWER CORES */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* PLAYER STATUS */}
                    <div className="p-6 tactical-corner bg-black/60 space-y-4 border-l-4 border-l-cyan-500">
                        <div className="flex justify-between items-center">
                            <span className="text-xs font-black text-white/60 tracking-widest uppercase flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-cyan-500"></span>
                                YOU {gameState?.player_is_staggered && <span className="text-red-500 animate-ping">[STAGGERED_LOCK]</span>}
                            </span>
                            <span className="text-4xl font-black text-white tabular-nums tracking-tighter">
                                {gameState?.player_hp ?? 100}%
                            </span>
                        </div>
                        
                        {/* HP BAR */}
                        <div className="h-4 hp-bar-container">
                            <div 
                                className={`hp-bar-fill bg-gradient-to-r from-cyan-600 to-cyan-400 ${gameState?.player_hp && gameState.player_hp < 30 ? "animate-pulse" : ""}`}
                                style={{ width: `${gameState?.player_hp ?? 100}%` }}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          {/* STAMINA BAR */}
                          <div className="space-y-1">
                              <div className="flex justify-between text-[8px] font-black text-cyan-400/60 tracking-widest uppercase">
                                  <span>STAMINA</span>
                                  <span>{gameState?.player_stamina ?? 100}%</span>
                              </div>
                              <div className="h-1.5 bg-black/40 border border-white/5">
                                  <div 
                                      className={`h-full bg-cyan-500/60 shadow-[0_0_10px_rgba(0,212,255,0.2)] transition-all ${gameState?.player_stamina && gameState.player_stamina < 20 ? "animate-pulse bg-red-500" : ""}`}
                                      style={{ width: `${gameState?.player_stamina ?? 100}%` }}
                                  />
                              </div>
                          </div>

                          {/* POSTURE BAR */}
                          <div className="space-y-1">
                              <div className="flex justify-between text-[8px] font-black text-white/40 tracking-widest uppercase">
                                  <span>POSTURE</span>
                                  <span>{gameState?.player_posture ?? 0}%</span>
                              </div>
                              <div className="h-1.5 bg-black/40 border border-white/5">
                                  <div 
                                      className={`h-full bg-white/40 transition-all ${gameState?.player_posture && gameState.player_posture > 70 ? "bg-red-500 shadow-[0_0_10px_rgba(255,0,0,0.4)]" : ""}`}
                                      style={{ width: `${gameState?.player_posture ?? 0}%` }}
                                  />
                              </div>
                          </div>
                        </div>
                    </div>

                    {/* BOSS STATUS */}
                    <div className={`p-6 tactical-corner bg-black/60 space-y-4 border-r-4 border-r-red-600 ${isIrritated ? "shadow-[inset_0_0_30px_rgba(255,0,0,0.2)]" : ""}`}>
                        <div className="flex justify-between items-center">
                            <span className="text-xs font-black text-red-500 tracking-widest uppercase flex items-center gap-2">
                                <span className={`w-2 h-2 rounded-full bg-red-600 ${isIrritated ? "animate-ping" : "animate-pulse"}`}></span>
                                MIRAI {gameState?.boss_is_staggered && <span className="text-cyan-400 animate-ping">[NEURAL_COLLAPSE]</span>}
                            </span>
                            <span className={`text-4xl font-black text-red-500 tabular-nums tracking-tighter ${isIrritated ? "glitch-text" : ""}`} data-text={gameState?.boss_hp ?? 100}>
                                {gameState?.boss_hp ?? 100}%
                            </span>
                        </div>

                        {/* HP BAR */}
                        <div className="h-4 hp-bar-container">
                            <div 
                                className="hp-bar-fill bg-gradient-to-l from-red-600 to-red-900 float-right shadow-[0_0_20px_rgba(255,0,0,0.3)]"
                                style={{ width: `${gameState?.boss_hp ?? 100}%` }}
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                          {/* STAMINA BAR */}
                          <div className="space-y-1">
                              <div className="flex justify-between text-[8px] font-black text-red-500/60 tracking-widest uppercase">
                                  <span>STAMINA</span>
                                  <span>{gameState?.boss_stamina ?? 100}%</span>
                              </div>
                              <div className="h-1.5 bg-black/40 border border-white/5">
                                  <div 
                                      className="h-full bg-red-600/60 shadow-[0_0_10px_rgba(255,0,0,0.2)] float-right transition-all"
                                      style={{ width: `${gameState?.boss_stamina ?? 100}%` }}
                                  />
                              </div>
                          </div>

                          {/* POSTURE BAR */}
                          <div className="space-y-1">
                              <div className="flex justify-between text-[8px] font-black text-white/40 tracking-widest uppercase">
                                  <span>POSTURE</span>
                                  <span>{gameState?.boss_posture ?? 0}%</span>
                              </div>
                              <div className="h-1.5 bg-black/40 border border-white/5">
                                  <div 
                                      className={`h-full bg-white/40 float-right transition-all ${gameState?.boss_posture && gameState.boss_posture > 70 ? "bg-cyan-400 shadow-[0_0_10px_rgba(0,212,255,0.4)]" : ""}`}
                                      style={{ width: `${gameState?.boss_posture ?? 0}%` }}
                                  />
                              </div>
                          </div>
                        </div>
                    </div>
                </div>

                {/* COMBAT ACTIONS */}
                <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
                    {["attack", "heavy", "parry", "grab", "feint", "defend", "heal", "bluff", "wait", "ability"].map((action) => (
                    <button
                        key={action}
                        onClick={() => handleAction(action)}
                        disabled={loading || gameState?.game_over || (gameState?.player_is_staggered)}
                        className={`
                        py-4 battle-btn text-[10px] font-black uppercase tracking-[0.2em] tactical-corner
                        ${loading || gameState?.player_is_staggered ? "opacity-20 cursor-not-allowed" : "text-white"}
                        ${action === "ability" ? "border-red-600/40 text-red-400 bg-red-950/10" : ""}
                        `}
                    >
                        <span className="relative z-10">{action}</span>
                        <div className="absolute top-0 right-0 w-1 h-1 bg-white/20"></div>
                    </button>
                    ))}
                </div>

                {/* TACTICAL DATA FEED */}
                <div className="tactical-corner bg-black/80 backdrop-blur-md p-6 h-64 overflow-y-auto custom-scrollbar border-t-2 border-t-red-600/20">
                    <div className="space-y-3 font-mono text-[11px]">
                        {battleLog.length > 0 ? (
                            battleLog.filter(log => log.source !== "DIALOGUE").map((log, i) => (
                                <div key={i} className={`flex gap-6 tracking-wider uppercase border-l-2 border-transparent hover:border-red-600/50 pl-4 py-1 transition-all bg-white/[0.02] ${log.text.includes("PARRIES") ? "bg-cyan-500/10 border-l-cyan-500" : ""}`}>
                                    <span className="text-white/20 font-bold tabular-nums">[{log.time}]</span>
                                    <span className={`font-black w-12 ${log.source === "MIR" ? "text-red-500" : "text-cyan-500"}`}>{log.source}:</span>
                                    <span className={`font-bold ${log.source === "MIR" ? "text-red-500" : log.source === "SYS" ? "text-cyan-400" : "text-white"}`}>{log.text}</span>
                                </div>
                            ))
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full space-y-4 opacity-20">
                                <div className="w-12 h-12 border-2 border-white/20 border-t-white animate-spin"></div>
                                <p className="text-[10px] tracking-[0.8em] font-black uppercase">LINK_IDLE</p>
                            </div>
                        )}
                        <div ref={logEndRef} />
                    </div>
                </div>
            </div>

            {/* COGNITIVE TRACE ASIDE */}
            {showThoughtProcess && (
                <aside className="lg:w-1/3 space-y-6 animate-in slide-in-from-right duration-500">
                    <div className="tactical-corner bg-black/90 p-8 space-y-10 border-l-2 border-cyan-500/30">
                        <h2 className="text-xs font-black tracking-[0.4em] text-cyan-400 border-b border-white/10 pb-4 uppercase flex items-center justify-between">
                            NEURAL_ARCHITECTURE
                            <span className="text-[8px] text-white/20">VER_4.2.0</span>
                        </h2>
                        
                        <div className="space-y-4">
                            <div className="flex justify-between text-[9px] font-black tracking-widest text-white/40 uppercase">
                                <span>Neural_Similarity</span>
                                <span>{similarity}%</span>
                            </div>
                            <div className="relative h-3 hp-bar-container bg-black">
                                <div className="h-full bg-cyan-500 transition-all duration-1000 shadow-[0_0_15px_rgba(0,212,255,0.4)]" style={{ width: `${similarity}%` }}></div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-4 bg-white/[0.03] border border-white/10 tactical-corner">
                                <p className="text-[8px] text-white/30 uppercase font-bold mb-1">Archetype</p>
                                <p className="text-xs font-black text-cyan-400 uppercase tracking-tighter">{gameState?.player_type ?? "N/A"}</p>
                            </div>
                            <div className="p-4 bg-white/[0.03] border border-white/10 tactical-corner">
                                <p className="text-[8px] text-white/30 uppercase font-bold mb-1">Internal_State</p>
                                <p className={`text-xs font-black uppercase tracking-tighter ${isIrritated ? "text-red-500 animate-pulse" : "text-white"}`}>{gameState?.emotion ?? "N/A"}</p>
                            </div>
                        </div>

                        <div className="space-y-6 bg-cyan-500/5 p-6 border border-cyan-500/10 tactical-corner">
                            <p className="text-[9px] text-cyan-400 uppercase font-black tracking-widest mb-4">Tactical_Heuristics</p>
                            <div className="space-y-4">
                              <div className="space-y-1">
                                <div className="flex justify-between text-[7px] text-white/40 font-black">
                                  <span>STAMINA_EFFICIENCY</span>
                                  <span>{gameState ? Math.round((gameState.player_stamina / 100) * 100) : 100}%</span>
                                </div>
                                <div className="h-1 bg-white/5"><div className="h-full bg-cyan-500/40" style={{ width: `${gameState?.player_stamina ?? 100}%` }}></div></div>
                              </div>
                              <div className="space-y-1">
                                <div className="flex justify-between text-[7px] text-white/40 font-black">
                                  <span>POSTURE_PRESSURE</span>
                                  <span>{gameState ? gameState.player_posture : 0}%</span>
                                </div>
                                <div className="h-1 bg-white/5"><div className="h-full bg-red-600/40" style={{ width: `${gameState?.player_posture ?? 0}%` }}></div></div>
                              </div>
                            </div>
                        </div>

                        <div className="pt-8 border-t border-white/10 space-y-4">
                            <div className="flex justify-between items-center bg-cyan-500/10 p-3 tactical-corner">
                                <span className="text-[9px] text-cyan-400 uppercase font-black">Trap_Protocol:</span>
                                <span className="text-xs font-black text-white uppercase tracking-widest">{gameState?.trap_status ?? "IDLE"}</span>
                            </div>
                            <div className="flex justify-between items-center bg-cyan-500/10 p-3 tactical-corner">
                                <span className="text-[9px] text-cyan-400 uppercase font-black">Next_Prediction:</span>
                                <span className="text-xs font-black text-white uppercase tracking-widest">{gameState?.predicted_move ?? "PENDING"}</span>
                            </div>
                            <div className="bg-black p-5 border-l-2 border-cyan-500 text-[10px] text-white/60 leading-relaxed italic uppercase font-medium">
                                "Analysis: {setupData?.analysis || "Awaiting Data..."}"
                            </div>
                        </div>
                    </div>
                </aside>
            )}
        </div>

        {/* TERMINAL MODAL */}
        {gameState?.game_over && (
            <div className="fixed inset-0 bg-red-950/90 flex items-center justify-center z-[200] p-4 backdrop-blur-md">
                <div className="max-w-xl w-full tactical-corner bg-black p-16 text-center space-y-12">
                    <div className="space-y-4">
                        <div className="inline-block px-4 py-1 bg-red-600 text-[10px] font-black tracking-[0.5em] uppercase mb-4">
                            {gameState.winner === "player" ? "COMBAT_LOG_ARCHIVED" : "COMBAT_LOG_TERMINATED"}
                        </div>
                        <h2 className={`text-5xl md:text-7xl font-black italic uppercase tracking-tighter leading-none ${gameState.winner === "player" ? "text-cyan-400" : "text-red-600"}`}>
                            {gameState.winner === "player" ? "YOU WON" : "MIRAI WON"}
                        </h2>
                        <div className="w-full h-px bg-white/10 mt-8"></div>
                        <div className="space-y-2">
                            <p className="text-white text-xl font-black tracking-[0.3em] uppercase animate-pulse">Mirai remembers you.</p>
                            <p className="text-white/40 text-[10px] tracking-[0.6em] font-black uppercase">Connection Severed. Data Persistence Established.</p>
                        </div>
                    </div>
                    <button 
                        onClick={handleReset}
                        className="w-full border-2 border-white/10 text-white/40 p-6 text-xs font-black uppercase tracking-[0.5em] hover:bg-white hover:text-black hover:border-white transition-all shadow-2xl"
                    >
                        RE_INITIALIZE_SYSTEM
                    </button>
                </div>
            </div>
        )}
      </div>
    </main>
  );
}
