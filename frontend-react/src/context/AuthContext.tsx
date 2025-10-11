import React, { createContext, useState, useContext } from 'react';

// Define the shape of the context data
interface AuthContextType {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

// FIX #1: Use the name "AuthContext" consistently
const AuthContext = createContext<AuthContextType | null>(null);

// Create the Provider component
// FIX #2: Add the type for the 'children' prop
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('authToken'));

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('authToken', newToken);
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem('authToken');
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// Create a custom hook to use the context easily
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}