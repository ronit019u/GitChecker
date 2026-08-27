import { Button } from "./ui/button";

export const Login = () => {
  const handleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_BASE_URL}/auth/login`;
  };
  return <Button onClick={handleLogin}>Login</Button>;
};
