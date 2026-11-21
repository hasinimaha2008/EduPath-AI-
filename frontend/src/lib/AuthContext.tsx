"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { User } from "./types";
import { api } from "./api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  logout: () => void;
  refreshUser: () => Promise<User | null>;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  logout: () => {},
  refreshUser: async () => null,
  setUser: () => {},
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const refreshUser = async (): Promise<User | null> => {
    try {
      const u = await api.getMe();
      setUser(u);
      api.setUser(u);
      return u;
    } catch (err) {
      console.warn("Could not fetch current user profile:", err);
      api.clearAuth();
      setUser(null);
      return null;
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 1. Initial cached profile for instantaneous render
    const cachedUser = api.getUser();
    if (cachedUser) {
      setUser(cachedUser);
    }

    // 2. Authoritative profile validation from backend database
    const token = typeof window !== "undefined" ? localStorage.getItem("edupath_token") : null;
    if (token) {
      refreshUser();
    } else {
      setLoading(false);
    }
  }, []);

  const logout = () => {
    api.clearAuth();
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout, refreshUser, setUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
