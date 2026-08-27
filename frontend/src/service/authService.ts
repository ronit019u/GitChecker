import api from "@/api/axios";
import type { User } from "@/types/types";

export const getMe = async (): Promise<User> => {
  const res = await api.get("/auth/me");
  return res.data;
};

export const logOut = async (): Promise<void> => {
  await api.post("/auth/logout");
};
