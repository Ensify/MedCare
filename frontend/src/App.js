import "./App.css";
import Patientprofiles from "./components/Patientprofiles";
import Otp from "./components/Otp";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import PatientCard from "./components/PatientCard";
import Records from "./components/Records";
import Summary from "./components/Summary";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./contexts/AuthContext";
function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route exact path="/" element={<ProtectedRoute />}>
            <Route exact path="/otp" element={<Otp />} />
            <Route exact path="/patientCard" element={<PatientCard />} />
            <Route
              exact
              path="/patientReports/:patientId"
              element={<Records />}
            />
            <Route exact path="/patientsum/:id" element={<Summary />} />
          </Route>
          <Route path="/patientprofile" element={<Patientprofiles />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
