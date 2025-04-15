import React from "react";
import "./SquadView.css";

const SquadView = ({ team, squad }) => {
  if (!team || squad.length === 0) {
    return (
      <div className="squad-view">
        <h2>Select a team to view squad</h2>
      </div>
    );
  }

  return (
    <div className="squad-view">
      <h2>{team} Squad</h2>
      <div className="squad-grid">
        {squad.map((player, index) => (
          <div className="player-card" key={index}>
            <img
              src={player.photo || "https://via.placeholder.com/100"}
              alt={player.name}
              className="player-photo"
            />
            <div className="player-info">
              <h3>{player.name}</h3>
              <p><strong>Age:</strong> {player.age}</p>
              <p><strong>Number:</strong> {player.number || "-"}</p>
              <p><strong>Position:</strong> {player.position}</p>
              <p><strong>Nationality:</strong> {player.nationality}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SquadView;
