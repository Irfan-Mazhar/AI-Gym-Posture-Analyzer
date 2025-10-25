import "./App.css";
import {  Route, Routes } from "react-router-dom";
import Landing from "./pages/Landing";
import Analyze from "./pages/Analyze";
import HowItWorks from "./components/ui/HowItWorks";
import LoginPage from "./pages/Login";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <main className="min-h-screen text-center flex flex-col gap-10 items-center">
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </main>
  );
}
export default App;
