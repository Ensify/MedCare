import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const ProtectedRoute = () => {
  const auth = useAuth();
  console.log(auth);
  return auth.user === null ? <Navigate to="/patientprofile" /> : <Outlet />;
};

export default ProtectedRoute;
