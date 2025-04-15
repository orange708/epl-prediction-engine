import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";
import TeamView from "./components/TeamView";

const logoMap = {
  "Arsenal": "t3",
  "Aston Villa": "t7",
  "Bournemouth": "t91",
  "Brentford": "t94",
  "Brighton": "t36",
  "Burnley": "t90",
  "Chelsea": "t8",
  "Crystal Palace": "t31",
  "Everton": "t11",
  "Fulham": "t54",
  "Leicester": "t13",
  "Liverpool": "t14",
  "Luton": "t102",
  "Man City": "t43",
  "Man United": "t1",
  "Newcastle": "t4",
  "Nott'm Forest": "t17",
  "Sheffield United": "t49",
  "Tottenham": "t6",
  "West Ham": "t21",
  "Wolves": "t39"
};

const getTeamLogo = (teamName) => {
  const code = logoMap[teamName];
  return code ? `https://resources.premierleague.com/premierleague/badges/${code}.png` : "/placeholder-logo.png";
};

// Define the API base URL - update this if your backend is on a different port/host
const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [season, setSeason] = useState("2027/2028");
  const [standings, setStandings] = useState([]);
  const [team, setTeam] = useState("Arsenal");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [availableSeasons, setAvailableSeasons] = useState([]);
  
  // Fetch available seasons on initial load
  useEffect(() => {
    console.log("Fetching available seasons...");
    axios
      .get(`${API_BASE_URL}/seasons`)
      .then((res) => {
        console.log("Seasons response:", res.data);
        if (res.data && res.data.seasons && res.data.seasons.length > 0) {
          setAvailableSeasons(res.data.seasons);
          // Set initial season to latest available
          setSeason(res.data.seasons[res.data.seasons.length - 1]);
        } else {
          console.warn("No seasons found in response");
          setAvailableSeasons([
            "2025/2026", "2026/2027", "2027/2028", 
            "2028/2029", "2029/2030", "2030/2031"
          ]);
        }
      })
      .catch((err) => {
        console.error(`Error fetching seasons: ${err.message}`);
        // Fallback seasons if API fails
        setAvailableSeasons([
          "2025/2026", "2026/2027", "2027/2028", 
          "2028/2029", "2029/2030", "2030/2031"
        ]);
      });
  }, []);

  // Fetch standings when season changes
  useEffect(() => {
    if (!season) return;
    
    console.log(`Fetching standings for season ${season}...`);
    setLoading(true);
    
    axios
      .get(`${API_BASE_URL}/standings?season=${season}`)
      .then((res) => {
        console.log("Standings response:", res.data);
        if (Array.isArray(res.data)) {
          setStandings(res.data);
          setLoading(false);
          setError(null);
          
          // If no team is selected or current team not in new season,
          // select the top team from standings
          if (res.data.length > 0 && (!team || !res.data.some(t => t.Team === team))) {
            setTeam(res.data[0].Team);
          }
        } else {
          console.warn("Invalid standings response format:", res.data);
          setError("Received invalid data format from server.");
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(`Error fetching standings: ${err.message}`);
        setError("Could not load standings data. Please check if the backend is running.");
        setLoading(false);
      });
  }, [season]);

  const checkServerHealth = () => {
    axios
      .get(`${API_BASE_URL}/health`)
      .then((res) => {
        console.log("Server health:", res.data);
        if (res.data.status === "ok") {
          // If server is healthy but we had an error, retry loading standings
          if (error) {
            setSeason(prevSeason => prevSeason); // Trigger a refetch
          }
        }
      })
      .catch((err) => {
        console.error(`Server health check failed: ${err.message}`);
        setError("Backend server not responding. Please ensure it's running at " + API_BASE_URL);
      });
  };

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
          <div style={{ marginTop: "0.5rem" }}>
            <button 
              onClick={checkServerHealth} 
              style={{ 
                background: "rgba(255, 255, 255, 0.2)",
                border: "none",
                padding: "0.25rem 0.75rem",
                borderRadius: "4px",
                cursor: "pointer",
                color: "white"
              }}
            >
              Check Connection
            </button>
          </div>
        </div>
      )}

      <div className="controls">
        <div className="control-group">
          <span className="control-label">Select Season:</span>
          <select
            id="season-select"
            value={season}
            onChange={(e) => setSeason(e.target.value)}
            disabled={loading || availableSeasons.length === 0}
          >
            {availableSeasons.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
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
                          src={getTeamLogo(t.Team)}
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

        <TeamView team={team} season={season} apiBaseUrl={API_BASE_URL} />
      </div>
      
      <footer>
        <p>© 2025 Premier League Prediction Engine | Data powered by ML model</p>
      </footer>
    </div>
  );
}

export default App;