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
  player_heavy_uses: number;
  boss_heavy_uses: number;
  player_type: string;
  predicted_move: string | null;
  boss_action: string;
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
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showThoughtProcess, setShowThoughtProcess] = useState(false);
  const [battleLog, setBattleLog] = useState<LogEntry[]>([]);
  const [isDamaged, setIsDamaged] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  const API_URL = "http://127.0.0.1:8000";

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [battleLog]);

  const getTime = () => {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
  };

  const handleAction = async (action: string) => {
    if (gameState?.game_over) return;
    setLoading(true);
    setIsDamaged(false);
    
    try {
      const response = await fetch(`${API_URL}/action/${action}`, { method: "POST" });
      if (!response.ok) throw new Error("Link Lost.");
      const data: GameState = await response.json();
      
      if (gameState && data.player_hp < gameState.player_hp) {
          setIsDamaged(true);
          setTimeout(() => setIsDamaged(false), 500);
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
    } catch (err: any) {
      setError("Reset Failed.");
    } finally {
      setLoading(false);
    }
  };

  const similarity = gameState?.similar_fights?.[0] 
    ? Math.round((1 - gameState.similar_fights[0].distance) * 100) 
    : 0;

  return (
    <main className={`min-h-screen bg-[#020202] text-white p-4 md:p-8 font-mono relative overflow-hidden transition-colors duration-150 ${isDamaged ? "damage-flash" : ""}`}>
      
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
                  <div className="w-3 h-3 bg-red-600 animate-pulse"></div>
                  <h1 className="text-4xl md:text-6xl font-black tracking-tighter text-white italic leading-none">MIRAI</h1>
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
                    <p className="text-2xl md:text-4xl leading-tight font-bold text-white uppercase tracking-tight italic">
                        "{gameState ? gameState.dialogue : "You Again, Show me what changed"}"
                    </p>
                    <div className="absolute bottom-2 right-2 flex gap-1">
                        <div className="w-10 h-1 bg-red-600/20"></div>
                        <div className="w-4 h-1 bg-red-600"></div>
                    </div>
                </div>

                {/* HUD: POWER CORES */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* PLAYER STATUS */}
                    <div className="p-6 tactical-corner bg-black/60">
                        <div className="flex justify-between items-center mb-4">
                            <span className="text-xs font-black text-white/60 tracking-widest uppercase flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-cyan-500"></span>
                                YOU
                            </span>
                            <span className="text-4xl font-black text-white tabular-nums tracking-tighter">
                                {gameState?.player_hp ?? 100}%
                            </span>
                        </div>
                        <div className="h-6 hp-bar-container">
                            <div 
                                className={`hp-bar-fill bg-gradient-to-r from-cyan-600 to-cyan-400 ${gameState?.player_hp && gameState.player_hp < 30 ? "animate-pulse" : ""}`}
                                style={{ width: `${gameState?.player_hp ?? 100}%` }}
                            />
                        </div>
                        <div className="mt-4 flex justify-between">
                            <div className="flex gap-1.5">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className={`h-1.5 w-8 ${i < (gameState?.player_heavy_uses ?? 3) ? "bg-cyan-500 shadow-[0_0_10px_rgba(0,212,255,0.5)]" : "bg-white/5"}`} />
                                ))}
                            </div>
                            <span className="text-[9px] font-bold text-cyan-500/60 uppercase tracking-widest">AUX_POWER_STABLE</span>
                        </div>
                    </div>

                    {/* BOSS STATUS */}
                    <div className="p-6 tactical-corner bg-black/60">
                        <div className="flex justify-between items-center mb-4">
                            <span className="text-xs font-black text-red-500 tracking-widest uppercase flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-red-600 animate-ping"></span>
                                MIRAI
                            </span>
                            <span className="text-4xl font-black text-red-500 tabular-nums tracking-tighter">
                                {gameState?.boss_hp ?? 100}%
                            </span>
                        </div>
                        <div className="h-6 hp-bar-container">
                            <div 
                                className="hp-bar-fill bg-gradient-to-l from-red-600 to-red-900 float-right shadow-[0_0_20px_rgba(255,0,0,0.3)]"
                                style={{ width: `${gameState?.boss_hp ?? 100}%` }}
                            />
                        </div>
                        <div className="mt-4 flex justify-between flex-row-reverse">
                            <div className="flex gap-1.5">
                                {[...Array(3)].map((_, i) => (
                                    <div key={i} className={`h-1.5 w-8 ${i < (gameState?.boss_heavy_uses ?? 3) ? "bg-red-600 shadow-[0_0_10px_rgba(255,0,0,0.5)]" : "bg-white/5"}`} />
                                ))}
                            </div>
                            <span className="text-[9px] font-bold text-red-500 uppercase tracking-widest">THREAT_LEVEL:MAXIMUM</span>
                        </div>
                    </div>
                </div>

                {/* COMBAT ACTIONS */}
                <div className="grid grid-cols-2 md:grid-cols-6 gap-3">
                    {["attack", "heavy", "defend", "heal", "bluff", "wait"].map((action) => (
                    <button
                        key={action}
                        onClick={() => handleAction(action)}
                        disabled={loading || gameState?.game_over || (action === "heavy" && (gameState?.player_heavy_uses ?? 3) <= 0)}
                        className={`
                        py-5 battle-btn text-[11px] font-black uppercase tracking-[0.3em] tactical-corner
                        ${loading || (action === "heavy" && (gameState?.player_heavy_uses ?? 3) <= 0) ? "opacity-20 cursor-not-allowed" : "text-white"}
                        `}
                    >
                        <span className="relative z-10">{action}</span>
                        <div className="absolute top-0 right-0 w-1 h-1 bg-white/20"></div>
                    </button>
                    ))}
                </div>

                {/* TACTICAL DATA FEED */}
                <div className="tactical-corner bg-black/80 backdrop-blur-md p-6 h-64 overflow-y-auto custom-scrollbar">
                    <div className="space-y-3 font-mono text-[11px]">
                        {battleLog.length > 0 ? (
                            battleLog.filter(log => log.source !== "DIALOGUE").map((log, i) => (
                                <div key={i} className="flex gap-6 tracking-wider uppercase border-l-2 border-transparent hover:border-red-600/50 pl-4 py-1 transition-all bg-white/[0.02]">
                                    <span className="text-white/20 font-bold tabular-nums">[{log.time}]</span>
                                    <span className={`font-black w-12 ${log.source === "MIR" ? "text-red-500" : "text-cyan-500"}`}>{log.source}:</span>
                                    <span className={`font-bold ${log.source === "MIR" ? "text-red-500" : "text-white"}`}>{log.text}</span>
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
                    <div className="tactical-corner bg-black/90 p-8 space-y-10">
                        <h2 className="text-xs font-black tracking-[0.4em] text-cyan-400 border-b border-white/10 pb-4 uppercase flex items-center justify-between">
                            COGNITIVE_TRACE
                            <span className="text-[8px] text-white/20">SEQ_8842</span>
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
                                <p className="text-xs font-black text-white uppercase tracking-tighter">{gameState?.emotion ?? "N/A"}</p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            <p className="text-[9px] text-white/30 uppercase font-black tracking-widest">Vector_Distribution</p>
                            <div className="flex gap-1.5 h-20 items-end bg-black p-4 border border-white/10">
                                {gameState?.behavior_vector?.map((v, i) => (
                                    <div key={i} className="flex-1 bg-white/5 relative group">
                                        <div className="absolute bottom-0 left-0 w-full bg-cyan-500/40 transition-all duration-700 group-hover:bg-cyan-400" style={{ height: `${v * 100}%` }}></div>
                                    </div>
                                )) ?? <div className="w-full h-full bg-white/5 animate-pulse" />}
                            </div>
                        </div>

                        <div className="pt-8 border-t border-white/10 space-y-4">
                            <div className="flex justify-between items-center bg-cyan-500/10 p-3 tactical-corner">
                                <span className="text-[9px] text-cyan-400 uppercase font-black">Next_Prediction:</span>
                                <span className="text-xs font-black text-white uppercase tracking-widest">{gameState?.predicted_move ?? "PENDING"}</span>
                            </div>
                            <div className="bg-black p-5 border-l-2 border-cyan-500 text-[10px] text-white/60 leading-relaxed italic uppercase font-medium">
                                "Pattern_{similarity} match confirmed. Target exhibiting {gameState?.player_type} behavior. Deploying {gameState?.boss_action} counter-measure."
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
