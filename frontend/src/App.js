
import './App.css';
import Patientprofiles from "./components/Patientprofiles";
import Otp from './components/Otp';
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PatientCard from "./components/PatientCard";
import Records from "./components/Records";


function App() {
  return (
    <BrowserRouter>
        <Routes>
          <Route path="/otp" element={<Otp />} />
          <Route path="/patientprofile" element={<Patientprofiles />} />
          <Route path="/patientCard" element={<PatientCard />} />
          <Route path="/patientReports/:patientId" element={<Records />} />
        </Routes>
      </BrowserRouter>
  );
}

export default App;
