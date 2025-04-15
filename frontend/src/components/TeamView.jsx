import PropTypes from "prop-types";

function TeamView({ team, season, teamData }) {
  if (!teamData) {
    return (
      <div className="team-details">
        <div style={{ color: "#ff6b6b", padding: "2rem", textAlign: "center" }}>
          No data found for {team} in the {season} season.
        </div>
      </div>
    );
  }

  return (
    <div className="team-details">
      <div className="team-header">
        <img
          src={`https://crests.football-data.org/${getTeamId(team)}.svg`}
          alt={`${team} logo`}
          onError={(e) => { e.target.src = "/placeholder-logo.png"; }}
        />
        <div className="team-header-info">
          <h3>{team}</h3>
          <p>Season: <strong>{season}</strong></p>
        </div>
      </div>

      <div className="prediction-section">
        <div className="prediction-label">Predicted Final Position</div>
        <div className="prediction-value">
          {teamData?.predictedRank || teamData?.PredictedRank || "—"}
          {getOrdinalSuffix(teamData?.predictedRank || teamData?.PredictedRank)}
        </div>
      </div>

      <div className="stat-section">
        <h4>Team Statistics</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">Points</div>
            <div className="stat-value">
              {teamData?.Points !== undefined 
                ? Number(teamData.Points).toFixed(1) 
                : "—"}
            </div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Win Rate</div>
            <div className="stat-value">
              {teamData?.winRate !== undefined 
                ? teamData.winRate 
                : (teamData?.Win !== undefined && teamData?.Matches !== undefined
                  ? Math.round((teamData.Win / teamData.Matches) * 100) 
                  : "—")}%
            </div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Goals Scored</div>
            <div className="stat-value">{teamData?.goalsScored || teamData?.GF || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Goals Conceded</div>
            <div className="stat-value">{teamData?.goalsConceded || teamData?.GA || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Clean Sheets</div>
            <div className="stat-value">{teamData?.cleanSheets || 
              (teamData?.GA !== undefined ? Math.max(1, Math.round(38 - (teamData.GA / 2))) : "—")}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Avg. Possession</div>
            <div className="stat-value">{teamData?.possession || "—"}%</div>
          </div>
        </div>
      </div>

      <div className="stat-section">
        <h4>Prediction Metrics</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">Manager Rating</div>
            <div className="stat-value">
              {teamData?.managerRating !== undefined || teamData?.ManagerRating !== undefined
                ? Number(teamData.managerRating || teamData.ManagerRating).toFixed(2) 
                : "—"}
            </div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Tier Score</div>
            <div className="stat-value">
              {teamData?.tierScore !== undefined || teamData?.TierScore !== undefined
                ? Number(teamData.tierScore || teamData.TierScore).toFixed(1)
                : "—"}
            </div>
          </div>
          <div className="stat-item">
            <div className="stat-label">3 Year Avg. Points</div>
            <div className="stat-value">
              {teamData?.avgPoints !== undefined || teamData?.AvgPoints3Yrs !== undefined
                ? Number(teamData.avgPoints || teamData.AvgPoints3Yrs).toFixed(1)
                : "—"}
            </div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Relegation Risk</div>
            <div className="stat-value">
              {teamData?.relegationRisk !== undefined 
                ? teamData.relegationRisk
                : (teamData?.RelegationRisk !== undefined
                  ? getRelegationRiskText(teamData.RelegationRisk)
                  : "—")}
            </div>
          </div>
        </div>
      </div>

      <div className="stat-section">
        <h4>Top Scorer</h4>
        {teamData?.TopScorer ? (
          <p>{teamData.TopScorer.name} ({teamData.TopScorer.goals} goals)</p>
        ) : (
          <p>No data available</p>
        )}

        <h4>Key Players</h4>
        {teamData?.KeyPlayers?.length > 0 ? (
          <ul>
            {teamData.KeyPlayers.map((player, idx) => (
              <li key={idx}>{player.name} - {player.position}</li>
            ))}
          </ul>
        ) : (
          <p>No data available</p>
        )}

        <h4>Transfers In</h4>
        {teamData?.TransfersIn?.length > 0 ? (
          <ul>
            {teamData.TransfersIn.map((t, idx) => (
              <li key={idx}>{t.name} from {t.from} ({t.fee})</li>
            ))}
          </ul>
        ) : (
          <p>No data available</p>
        )}

        <h4>Transfers Out</h4>
        {teamData?.TransfersOut?.length > 0 ? (
          <ul>
            {teamData.TransfersOut.map((t, idx) => (
              <li key={idx}>{t.name} to {t.to} ({t.fee})</li>
            ))}
          </ul>
        ) : (
          <p>No data available</p>
        )}
      </div>

      <div className="chart-section">
        <div className="chart-placeholder">Position trend data will appear here</div>
      </div>
    </div>
  );
}

// Helper function to generate ordinal suffix (1st, 2nd, 3rd, etc.)
function getOrdinalSuffix(num) {
  if (num === undefined || num === null) return "";
  
  const j = num % 10;
  const k = num % 100;
  if (j === 1 && k !== 11) {
    return "st";
  }
  if (j === 2 && k !== 12) {
    return "nd";
  }
  if (j === 3 && k !== 13) {
    return "rd";
  }
  return "th";
}

// Helper function to convert relegation risk number to text
function getRelegationRiskText(risk) {
  if (risk < 20) return "None";
  if (risk < 40) return "Low";
  if (risk < 60) return "Medium";
  return "High";
}

// Helper function to map team names to football-data.org IDs
function getTeamId(teamName) {
  const teamIds = {
    "Arsenal": 57,
    "Aston Villa": 58,
    "Bournemouth": 1044,
    "Brentford": 402,
    "Brighton": 397,
    "Burnley": 328,
    "Chelsea": 61,
    "Crystal Palace": 354,
    "Everton": 62,
    "Fulham": 63,
    "Leicester": 338,
    "Liverpool": 64,
    "Luton": 389,
    "Man City": 65,
    "Man United": 66,
    "Newcastle": 67,
    "Nott'm Forest": 351,
    "Sheffield United": 356,
    "Tottenham": 73,
    "West Ham": 563,
    "Wolves": 76
  };
  return teamIds[teamName] || 0;
}

TeamView.propTypes = {
  team: PropTypes.string.isRequired,
  season: PropTypes.string.isRequired,
  teamData: PropTypes.object
};

export default TeamView;