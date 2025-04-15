import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import TeamView from "./components/TeamView";

function App() {
  const [season, setSeason] = useState("2027/2028");
  const [standings, setStandings] = useState([]);
  const [team, setTeam] = useState("Arsenal");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Reset loading state when season changes
    setLoading(true);
    
    // Generate dummy data as fallback
    const dummyStandings = generateDummyStandings();
    
    axios
      .get(`http://127.0.0.1:8000/standings?season=${season}`)
      .then((res) => {
        setStandings(res.data);
        setLoading(false);
        setError(null);
      })
      .catch((err) => {
        console.error(`Error fetching standings: ${err.message}`);
        // Use dummy data when API fails
        setStandings(dummyStandings);
        setError("Could not connect to API. Using sample data instead.");
        setLoading(false);
      });
  }, [season]);

  return (
    <div className="app-container">
      <h1 className="app-title">Premier League Predictor</h1>
      
      {error && (
        <div style={{ 
          color: "#ff6b6b", 
          background: "rgba(255, 107, 107, 0.1)", 
          padding: "0.75rem 1rem", 
          borderRadius: "8px", 
          marginBottom: "1.5rem",
          textAlign: "center" 
        }}>
          {error}
        </div>
      )}

      <div className="controls">
        <div className="control-group">
          <span className="control-label">Select Season:</span>
          <select
            id="season-select"
            value={season}
            onChange={(e) => setSeason(e.target.value)}
          >
            <option value="2025/2026">2025/2026</option>
            <option value="2026/2027">2026/2027</option>
            <option value="2027/2028">2027/2028</option>
            <option value="2028/2029">2028/2029</option>
            <option value="2029/2030">2029/2030</option>
            <option value="2030/2031">2030/2031</option>
          </select>
        </div>
      </div>

      <div className="main-content">
        <div className="table-section">
          <h2 className="section-title">League Standings</h2>
          
          {loading ? (
            <div style={{ padding: "2rem 0", textAlign: "center", color: "var(--text-secondary)" }}>
              Loading standings data...
            </div>
          ) : (
            <table className="standings-table">
              <thead>
                <tr>
                  <th>Pos</th>
                  <th>Team</th>
                  <th>P</th>
                  <th>W</th>
                  <th>D</th>
                  <th>L</th>
                  <th>Points</th>
                </tr>
              </thead>
              <tbody>
                {standings.map((t, idx) => {
                  const rank = idx + 1;
                  let rankClass = "";
                  
                  if (rank <= 4) {
                    rankClass = "ucl";
                  } else if (rank === 5 || rank === 6) {
                    rankClass = "europa";
                  } else if (rank === 7) {
                    rankClass = "conf";
                  } else if (rank > standings.length - 3) {
                    rankClass = "relegation";
                  }

                  return (
                    <tr
                      key={`${t.Team}-${idx}`}
                      onClick={() => setTeam(t.Team)}
                      className={`${t.Team === team ? "highlight" : ""} ${rankClass}`}
                    >
                      <td><span className="position">{rank}</span></td>
                      <td className="team-cell">
                        <img
                          src={`https://logo.clearbit.com/${t.Team.replace(/\s+/g, "").toLowerCase()}.com`}
                          alt={`${t.Team} logo`}
                          className="club-logo"
                          onError={(e) => { e.target.src = "/placeholder-logo.png"; }}
                        />
                        <span className="team-name">{t.Team}</span>
                      </td>
                      <td>{t.Matches || "38"}</td>
                      <td>{t.Win || "—"}</td>
                      <td>{t.Draw || "—"}</td>
                      <td>{t.Loss || "—"}</td>
                      <td>{t.Points ? t.Points.toFixed(1) : "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
          
          <div className="league-position-indicator">
            <div className="position-marker marker-ucl">
              <span className="color-dot dot-ucl"></span>
              <span>Champions League</span>
            </div>
            <div className="position-marker marker-europa">
              <span className="color-dot dot-europa"></span>
              <span>Europa League</span>
            </div>
            <div className="position-marker marker-conf">
              <span className="color-dot dot-conf"></span>
              <span>Conference League</span>
            </div>
            <div className="position-marker marker-relegation">
              <span className="color-dot dot-relegation"></span>
              <span>Relegation</span>
            </div>
          </div>
        </div>

        <TeamView team={team} season={season} />
      </div>
    </div>
  );
}

// Function to generate dummy standings data when API fails
function generateDummyStandings() {
  const teams = [
    "Man City", "Arsenal", "Liverpool", "Chelsea", "Man United", 
    "Tottenham", "Aston Villa", "Newcastle", "West Ham", "Brighton",
    "Brentford", "Wolves", "Crystal Palace", "Everton", "Nottingham Forest",
    "Bournemouth", "Fulham", "Luton", "Burnley", "Sheffield United"
  ];
  
  // Sort teams roughly by expected strength
  const sortedTeams = [...teams].sort((a, b) => {
    const tierA = getTier(a);
    const tierB = getTier(b);
    return tierA - tierB;
  });
  
  // Add some randomness to points
  return sortedTeams.map(team => {
    const tier = getTier(team);
    const basePoints = tier === 1 ? 80 : tier === 2 ? 60 : 40;
    const randomFactor = Math.floor(Math.random() * 15) - 5; // -5 to +10 points of randomness
    const points = basePoints + randomFactor;
    
    const matches = 38;
    const winRate = tier === 1 ? 0.65 : tier === 2 ? 0.45 : 0.3;
    const wins = Math.round(matches * winRate);
    const drawRate = tier === 1 ? 0.2 : tier === 2 ? 0.25 : 0.25;
    const draws = Math.round(matches * drawRate);
    const losses = matches - wins - draws;
    
    return {
      Team: team,
      Points: points,
      Matches: matches,
      Win: wins,
      Draw: draws,
      Loss: losses
    };
  });
}

// Helper function to determine team tier
function getTier(team) {
  const topTeams = ["Man City", "Liverpool", "Arsenal", "Chelsea", "Man United", "Tottenham"];
  const midTeams = ["Aston Villa", "Newcastle", "West Ham", "Brighton", "Brentford", "Wolves", "Crystal Palace"];
  
  if (topTeams.includes(team)) return 1;
  if (midTeams.includes(team)) return 2;
  return 3;
}

export default App;