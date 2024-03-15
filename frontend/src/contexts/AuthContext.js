import React, { createContext, useContext, useEffect, useState } from "react";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = sessionStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (phone) => {
    try {
      setUser({ phone });
      sessionStorage.setItem("user", JSON.stringify({ phone }));
      return true;
    } catch (error) {
      console.error("Login failed:", error);
      return false;
    }
  };

  return (
    <AuthContext.Provider value={{ user, login }}>
      {loading ? (
        <div>Loading...</div> // Display loading indicator until user data is retrieved
      ) : (
        children
      )}
    </AuthContext.Provider>
  );
};
