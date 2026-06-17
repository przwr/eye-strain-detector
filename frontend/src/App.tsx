import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";

export default function App() {
  const [tab, setTab] = useState<"live" | "history">("live");
  return (
    <div className="app">
      <div className="topbar">
        <div className="brand">
          <h1>Iris</h1>
          <span className="sub">Eye Strain Monitor</span>
        </div>
        <div className="nav">
          <a className={tab === "live" ? "active" : ""} onClick={() => setTab("live")} href="#">Live</a>
          <a className={tab === "history" ? "active" : ""} onClick={() => setTab("history")} href="#">History</a>
        </div>
      </div>
      {tab === "live" ? <Dashboard /> : <History />}
    </div>
  );
}
