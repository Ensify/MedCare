
import './App.css';
import Patientprofiles from "./components/Patientprofiles";
import { BrowserRouter, Routes, Route } from "react-router-dom";

function App() {
  return (
    <BrowserRouter>
        <Routes>
          <Route path="/patientprofile" element={<Patientprofiles />} />
        </Routes>
      </BrowserRouter>
  );
}

export default App;
