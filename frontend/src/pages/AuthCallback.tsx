import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import { getMe } from "@/service/authService";

export function AuthCallback() {
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    async function finish() {
      try {
        const user = await getMe();
        login(user);
        //catch just to prevent the gitchecker from breaking when error occurs
      } catch {
        // login failed — just bounce home, ProtectedRoute will show login button
      }
      navigate("/", { replace: true });
    }
    finish();
  }, []);

  return <div>Signing you in…</div>;
}
