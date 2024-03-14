
import './App.css';
import Patientprofiles from "./components/Patientprofiles";
import Otp from './components/Otp';
import { BrowserRouter, Routes, Route } from "react-router-dom";


function App() {
  return (
    <BrowserRouter>
        <Routes>
          <Route path="/otp" element={<Otp />} />
          <Route path="/patientprofile" element={<Patientprofiles />} />
        </Routes>
      </BrowserRouter>
  );
}

export default App;
