import { useState } from "react";

import {
  loginUser,
  registerUser,
  getCurrentUser,
  clearToken,
} from "../lib/api";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [authStatus, setAuthStatus] = useState("");

  async function login(email, password) {
    setAuthStatus("");

    try {
      await loginUser(email, password);

      const currentUser = await getCurrentUser();

      setUser(currentUser);

      return currentUser;
    } catch (err) {
      setAuthStatus(err.message);
      throw err;
    }
  }

  async function register(email, password) {
    await registerUser(email, password);

    return await login(email, password);
  }

  function logout() {
    clearToken();
    setUser(null);
    setAuthStatus("");
  }

  return {
    user,
    setUser,

    authStatus,
    setAuthStatus,

    login,
    register,
    logout,
  };
}