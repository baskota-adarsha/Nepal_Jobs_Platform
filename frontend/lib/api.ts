import axios from "axios";
const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:5000",
  timeout: 10000,
  headers: { "Content-Type": "application/json" },
});
export interface Job {
  id: string;
  title: string;
  company_name: string;
  company_industry: string;
  district: string;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string;
  job_type: string;
  experience_level: string;
  description: string | null;
  skills: string[];
  posted_at: string;
}

export interface JobFilters {
  page?: number;
  limit?: number;
  district?: string;
  skill?: string;
  salary_min?: number;
  salary_max?: number;
  job_type?: string;
  experience_level?: string;
  search?: string;
}

export interface PaginatedJobs {
  data: Job[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface JobTrend {
  month: string;
  year: number;
  job_count: number;
  avg_salary_min: number | null;
}

export interface JobStats {
  total_jobs: number;
  total_companies: number;
  avg_salary: number;
  districts: { district: string; count: number }[];
}

export interface SkillDemand {
  id: string;
  name: string;
  category: string;
  total_demand: number;
  this_month: number;
  last_month: number;
  trend: "rising" | "falling" | "stable";
  trend_pct: number;
}

export interface SalarySummary {
  role: string;
  district: string;
  avg_salary_min: number;
  avg_salary_max: number;
  job_count: number;
  experience_level: string;
}

export interface SalaryByDistrict {
  district: string;
  avg_salary_min: number;
  avg_salary_max: number;
  job_count: number;
}

export interface SalaryPercentiles {
  p25: number;
  p50: number;
  p75: number;
  p90: number;
  min: number;
  max: number;
  mean: number;
}

export interface Company {
  id: string;
  name: string;
  industry: string;
  size: string;
  district: string;
  website: string | null;
  job_count: number;
}

export const getJobs = async (filters?: JobFilters): Promise<PaginatedJobs> => {
  const { data } = await api.get("/api/jobs", { params: filters });
  return data.data;
};

export const getJobStats = async (): Promise<JobStats> => {
  const { data } = await api.get("/api/jobs/stats");
  return data.data;
};

export const getJobTrends = async (months = 6): Promise<JobTrend[]> => {
  const { data } = await api.get("/api/jobs/trends", { params: { months } });
  return data.data;
};

export const getSkillsDemand = async (limit = 20): Promise<SkillDemand[]> => {
  const { data } = await api.get("/api/skills/demand", { params: { limit } });
  return data.data;
};

export const getSkillsByCategory = async () => {
  const { data } = await api.get("/api/skills/by-category");
  return data.data;
};

export const getSalaries = async (filters?: {
  district?: string;
  experience_level?: string;
}): Promise<SalarySummary[]> => {
  const { data } = await api.get("/api/salaries", { params: filters });
  return data.data;
};

export const getSalariesByDistrict = async (): Promise<SalaryByDistrict[]> => {
  const { data } = await api.get("/api/salaries/by-district");
  return data.data;
};

export const getSalaryPercentiles = async (): Promise<SalaryPercentiles> => {
  const { data } = await api.get("/api/salaries/percentiles");
  return data.data;
};

export const getTopCompanies = async (limit = 10): Promise<Company[]> => {
  const { data } = await api.get("/api/companies/top", { params: { limit } });
  return data.data;
};

export const getCompaniesByIndustry = async () => {
  const { data } = await api.get("/api/companies/by-industry");
  return data.data;
};
