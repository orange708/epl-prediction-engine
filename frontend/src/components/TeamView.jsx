import { useEffect, useState } from "react";
import axios from "axios";

function TeamView({ team, season }) {
  const [teamData, setTeamData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    // Using dummy data as fallback if API fails
    const dummyData = generateDummyData(team);
    
    axios
      .get(`http://127.0.0.1:8000/team?season=${season}&team=${team}`)
      .then((res) => {
        setTeamData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error(`Error fetching team data: ${err.message}`);
        // Use dummy data when API fails
        setTeamData(dummyData);
        setError("Could not connect to API. Using sample data instead.");
        setLoading(false);
      });
  }, [team, season]);

  if (loading) {
    return (
      <div className="team-details">
        <div className="team-header">
          <div className="team-header-info">
            <h3>Loading {team}...</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="team-details">
      {error && (
        <div style={{ color: "#ff6b6b", marginBottom: "1rem", fontSize: "0.9rem" }}>
          {error}
        </div>
      )}
      
      <div className="team-header">
        <img
          src={`https://logo.clearbit.com/${team.replace(/\s+/g, "").toLowerCase()}.com`}
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
          {teamData?.predictedRank || "—"}
          {teamData?.predictedRank ? getOrdinalSuffix(teamData.predictedRank) : ""}
        </div>
      </div>

      <div className="stat-section">
        <h4>Team Statistics</h4>
        <div className="stats-grid">
          <div className="stat-item">
            <div className="stat-label">Points</div>
            <div className="stat-value">{teamData?.points || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Win Rate</div>
            <div className="stat-value">{teamData?.winRate || "—"}%</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Goals Scored</div>
            <div className="stat-value">{teamData?.goalsScored || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Goals Conceded</div>
            <div className="stat-value">{teamData?.goalsConceded || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Clean Sheets</div>
            <div className="stat-value">{teamData?.cleanSheets || "—"}</div>
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
            <div className="stat-value">{teamData?.managerRating?.toFixed(2) || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Tier Score</div>
            <div className="stat-value">{teamData?.tierScore?.toFixed(1) || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">3 Year Avg. Points</div>
            <div className="stat-value">{teamData?.avgPoints?.toFixed(1) || "—"}</div>
          </div>
          <div className="stat-item">
            <div className="stat-label">Relegation Risk</div>
            <div className="stat-value">{teamData?.relegationRisk || "—"}</div>
          </div>
        </div>
      </div>

      <div className="chart-section">
        <div className="chart-placeholder">Position trend data will appear here</div>
      </div>
    </div>
  );
}

// Helper function to generate ordinal suffix (1st, 2nd, 3rd, etc.)
function getOrdinalSuffix(num) {
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

// Generate dummy data to use when API fails
function generateDummyData(team) {
  const topTeams = ["Man City", "Liverpool", "Arsenal", "Chelsea", "Man United", "Tottenham"];
  const isTopTeam = topTeams.includes(team);
  
  return {
    team: team,
    predictedRank: isTopTeam ? Math.floor(Math.random() * 6) + 1 : Math.floor(Math.random() * 14) + 7,
    points: isTopTeam ? Math.floor(Math.random() * 20) + 70 : Math.floor(Math.random() * 30) + 40,
    winRate: isTopTeam ? Math.floor(Math.random() * 20) + 60 : Math.floor(Math.random() * 30) + 30,
    goalsScored: isTopTeam ? Math.floor(Math.random() * 30) + 70 : Math.floor(Math.random() * 40) + 30,
    goalsConceded: isTopTeam ? Math.floor(Math.random() * 20) + 30 : Math.floor(Math.random() * 30) + 40,
    cleanSheets: isTopTeam ? Math.floor(Math.random() * 5) + 15 : Math.floor(Math.random() * 10) + 5,
    possession: isTopTeam ? Math.floor(Math.random() * 10) + 55 : Math.floor(Math.random() * 15) + 40,
    managerRating: isTopTeam ? 0.8 + (Math.random() * 0.15) : 0.6 + (Math.random() * 0.2),
    tierScore: isTopTeam ? 3.0 : Math.random() < 0.3 ? 1.0 : 2.0,
    avgPoints: isTopTeam ? Math.floor(Math.random() * 10) + 70 : Math.floor(Math.random() * 20) + 40,
    relegationRisk: isTopTeam ? "None" : Math.random() < 0.3 ? "High" : "Medium"
  };
}

export default TeamView;