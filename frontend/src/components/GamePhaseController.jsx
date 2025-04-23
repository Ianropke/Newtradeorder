import React from "react";

const PHASES = [
  "Forberedelse",
  "Handelsvalg",
  "Simulering",
  "Resultater",
  "Afslutning"
];

export default function GamePhaseController({ currentPhase, onPhaseChange }) {
  return (
    <div className="game-phase-controller">
      <h3>Spilfaser</h3>
      <div style={{ display: "flex", gap: 8 }}>
        {PHASES.map((phase, idx) => (
          <button
            key={phase}
            onClick={() => onPhaseChange(idx)}
            style={{
              fontWeight: idx === currentPhase ? "bold" : "normal",
              background: idx === currentPhase ? "#d0f0c0" : "#f0f0f0",
              border: "1px solid #ccc",
              borderRadius: 4,
              padding: "4px 12px",
              cursor: "pointer"
            }}
          >
            {phase}
          </button>
        ))}
      </div>
    </div>
  );
}
