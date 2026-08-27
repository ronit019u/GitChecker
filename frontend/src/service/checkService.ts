import api from "@/api/axios";
import type {
  CheckRequest,
  FixRequest,
  FixResponse,
  SaveCheck,
  StartResponse,
} from "@/types/types";

export const getIssues = async (data: CheckRequest): Promise<StartResponse> => {
  const res = await api.post("/check/start", data);
  return res.data;
};

export const getFix = async (data: FixRequest): Promise<FixResponse> => {
  const res = await api.post("/check/fix", data);
  return res.data;
};

export const unverifiedCheck = async (data: SaveCheck) => {
  const res = await api.post("/check/save", data);
  return res.data;
};

export const getHistory = async () => {
  const res = await api.get("/check/history");
  return res.data;
};

export const deleteHistory = async (historyId: string) => {
  const res = await api.delete(`/check/history/${historyId}`);
  return res;
};
