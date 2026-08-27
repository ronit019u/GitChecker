import { getMe, logOut } from "@/service/authService";
import type { AuthContextType, User } from "@/types/types";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useContext } from "react";

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const queryClient = useQueryClient();

  const { data: user, isLoading } = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
    retry: false,
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  });

  console.log("Query state:", { user, isLoading });

  const login = (userData: User) => {
    queryClient.setQueryData(["me"], userData);
    queryClient.invalidateQueries({ queryKey: ["me"] });
  };
  const logoutUser = async () => {
    await logOut();
    queryClient.setQueryData(["me"], null);
    queryClient.invalidateQueries({ queryKey: ["me"] });
  };
  if (isLoading) return <div>Loading...</div>;

  return (
    <AuthContext.Provider
      value={{ user: user ?? null, login, logout: logoutUser }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be inside AuthProvider");
  return context;
};
