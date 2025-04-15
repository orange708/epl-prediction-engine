import React from 'react';
import './SquadView.css';

const SquadView = ({ team, squad, cleanSheets, possession, goalsScored, goalsConceded }) => {
  return (
    <div className="squad-view">
      <div className="team-info">
        <h2 className="team-name">{team} Squad</h2>
        <div className="info-box">
          <p><strong>Clean Sheets:</strong> {cleanSheets}</p>
          <p><strong>Possession:</strong> {possession}</p>
          <p><strong>Goals Scored:</strong> {goalsScored}</p>
          <p><strong>Goals Conceded:</strong> {goalsConceded}</p>
        </div>
      </div>

      {squad.length > 0 ? (
        <div className="player-grid">
          {squad.map((player) => (
            <div className="player-card" key={player.id}>
              <img src={player.photo} alt={`${player.name}'s photo`} className="player-photo" />
              <div className="player-details">
                <h3 className="player-name">{player.name}</h3>
                <p className="player-age">Age: {player.age}</p>
                <p className="player-position">Position: {player.position}</p>
                <p className="player-nationality">Nationality: {player.nationality}</p>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="no-squad-message">
          <p>No players found in the squad.</p>
        </div>
      )}
    </div>
  );
};

export default SquadView;