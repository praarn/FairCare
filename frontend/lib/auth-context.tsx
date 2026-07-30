"use client";

import { createContext, useContext, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { User } from "./types";
import * as api from "./api";

const TOKEN_COOKIE = "sahaj_auth_token";

type AuthContextValue = {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

function setTokenCookie(token: string) {
  document.cookie = `${TOKEN_COOKIE}=${token}; path=/; max-age=${60 * 60 * 24 * 7}`;
}

function clearTokenCookie() {
  document.cookie = `${TOKEN_COOKIE}=; path=/; max-age=0`;
}

export function AuthProvider({
  initialUser,
  children,
}: {
  initialUser: User | null;
  children: React.ReactNode;
}) {
  const [user, setUser] = useState<User | null>(initialUser);
  const router = useRouter();

  const login = useCallback(
    async (email: string, password: string) => {
      const { token, user: loggedInUser } = await api.login({ email, password });
      setTokenCookie(token);
      setUser(loggedInUser);
      router.push("/");
      router.refresh();
    },
    [router]
  );

  const signup = useCallback(
    async (name: string, email: string, password: string) => {
      const { token, user: newUser } = await api.signup({ name, email, password });
      setTokenCookie(token);
      setUser(newUser);
      router.push("/");
      router.refresh();
    },
    [router]
  );

  const logout = useCallback(async () => {
    const match = document.cookie.match(new RegExp(`${TOKEN_COOKIE}=([^;]+)`));
    if (match) {
      try {
        await api.logout(match[1]);
      } catch {
        // ignore network errors on logout — clear locally regardless
      }
    }
    clearTokenCookie();
    setUser(null);
    router.push("/login");
    router.refresh();
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
