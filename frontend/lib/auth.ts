import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000",
  timeout: 10000,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
});
export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: string;
}

export const login = async (
  email: string,
  password: string,
): Promise<AuthUser> => {
  const { data } = await api.post("/api/auth/login", { email, password });
  return data.data.user;
};
export const register = async (
  email: string,
  name: string,
  password: string,
): Promise<AuthUser> => {
  const { data } = await api.post("/api/auth/register", {
    email,
    password,
    name,
  });
  return data.data.user;
};
export const getMe = async (): Promise<AuthUser> => {
  const { data } = await api.get("/api/auth/me");
  return data.data;
};
export const refreshToken = async (): Promise<void> => {
  await api.post("/api/auth/refresh");
};
export const logout = async (): Promise<void> => {
  await api.post("/api/auth/logout");
};
