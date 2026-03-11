"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { login, me } from "@/lib/api";
import { AuthUser } from "@/lib/types";

type AuthContextValue = {
  token: string | null;
  user: AuthUser | null;
  booting: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signOut: () => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const STORAGE_TOKEN = "aacc_token";
const STORAGE_USER = "aacc_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [booting, setBooting] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem(STORAGE_TOKEN);
    const storedUser = localStorage.getItem(STORAGE_USER);

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser) as AuthUser);
    }
    setBooting(false);
  }, []);

  const signIn = async (email: string, password: string) => {
    const accessToken = await login(email, password);
    const profile = await me(accessToken);

    localStorage.setItem(STORAGE_TOKEN, accessToken);
    localStorage.setItem(STORAGE_USER, JSON.stringify(profile));

    setToken(accessToken);
    setUser(profile);
  };

  const signOut = () => {
    localStorage.removeItem(STORAGE_TOKEN);
    localStorage.removeItem(STORAGE_USER);
    setToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({ token, user, booting, signIn, signOut }),
    [token, user, booting],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
