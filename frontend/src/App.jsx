import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [season, setSeason] = useState("2027/2028");
  const [standings, setStandings] = useState([]);
  const [team, setTeam] = useState("Arsenal");
  const [teamData, setTeamData] = useState(null);

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/standings?season=${season}`)
      .then((res) => setStandings(res.data))
      .catch((err) => console.error(err));
  }, [season]);

  useEffect(() => {
    axios
      .get(`http://127.0.0.1:8000/team?season=${season}&team=${team}`)
      .then((res) => setTeamData(res.data))
      .catch((err) => console.error(err));
  }, [season, team]);

  return (
    <div className="app-container">
      <h1 className="app-title">Premier League Predictor</h1>

      <div className="controls">
        <label htmlFor="season-select">Select Season:</label>
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

      <div className="main-content">
        <div className="table-section">
          <h2>League Standings</h2>
          <table className="standings-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>Team</th>
                <th>Points</th>
              </tr>
            </thead>
            <tbody>
              {standings.map((t, idx) => (
                <tr
                  key={`${t.Team}-${idx}`}
                  onClick={() => setTeam(t.Team)}
                  className={t.Team === team ? "highlight" : ""}
                >
                  <td>{idx + 1}</td>
                  <td>{t.Team}</td>
                  <td>{t.Points ? t.Points.toFixed(1) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {teamData && (
          <div className="team-details">
            <h3>{teamData.Team} — {season}</h3>
            <ul>
              <li><strong>Points:</strong> {teamData.Points?.toFixed(1) ?? "—"}</li>
              <li><strong>Goal Difference:</strong> {teamData.GD ?? "—"}</li>
              <li><strong>Manager Rating:</strong> {teamData.ManagerRating ?? "—"}</li>
              <li><strong>Promoted:</strong> {teamData.PromotedTeam ? "Yes" : "No"}</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
