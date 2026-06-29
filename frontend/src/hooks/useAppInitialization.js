import { useEffect } from "react";
import { getCurrentUser, getToken } from "../lib/api";

export function useAppInitialization({
  setUser,
  restoreThread,
}) {
  useEffect(() => {
    async function restoreLogin() {
      if (!getToken()) return;

      try {
        const currentUser = await getCurrentUser();

        setUser(currentUser);

        restoreThread(currentUser.email);
      } catch (err) {
        console.error(err);
      }
    }

    restoreLogin();
  }, []);
}