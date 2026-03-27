//Pagination

export interface PaginationQuery {
  page?: number;
  limit?: number;
}
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}
//Company

export interface Company {
  id: string;
  name: string;
  industry: string;
  size: string;
  district: string;
  website: string | null;
  description: string | null;
  is_active: boolean;
  created_at: Date;
  updated_at: Date;
}
export interface CompanyWithJobCount extends Company {
  job_count: number;
}

//Skill

export interface Skill {
  id: string;
  name: string;
  category: string;
  descripton: string | null;
  is_active: boolean;
  created_at: Date;
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

//Job

export interface Job {
  id: string;
  title: string;
  company_id: string;
  district: string;
  location_detail: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string;
  job_type: "full-time" | "part-time" | "contract" | "internship" | "remote";
  experience_level: "entry" | "mid" | "senior" | "lead" | "manager";
  description: string | null;
  is_active: boolean;
  posted_at: Date;
  expires_at: Date | null;
  created_at: Date;
  updated_at: Date;
}

export interface JobWithCompany extends Job {
  company_name: string;
  company_industry: string;
  skills: string[];
}

export interface JobFilters extends PaginationQuery {
  district?: string;
  skill?: string;
  salary_min?: number;
  salary_max?: number;
  job_type?: string;
  experience_level?: string;
  search?: string;
}

export interface JobTrend {
  month: string;
  year: number;
  job_count: number;
  avg_salary_min: number | null;
}

// ─── Salary ───────────────────────────────────────────────────────────────────
export interface SalaryStats {
  role: string;
  district: string;
  avg_salary: number;
  min_salary: number;
  max_salary: number;
  sample_size: number;
  month: number;
  year: number;
}

export interface SalarySummary {
  role: string;
  district: string;
  avg_salary_min: number;
  avg_salary_max: number;
  job_count: number;
  experience_level: string;
}
//Auth

export interface User {
  id: string;
  email: string;
  password_hash: string;
  name: string;
  role: "admin" | "user";
  created_at: Date;
  updated_at: Date;
}

export interface TokenPayload {
  userId: string;
  email: string;
  role: string;
}
export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  expiresIn: string;
}

export interface LoginBody {
  email: string;
  password: string;
}

export interface RegisterBody {
  email: string;
  password: string;
  name: string;
}

//API Response Wrapper

export interface ApiResponse<T = unknown> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
}

// ─── Express augmentation ─────────────────────────────────────────────────────
declare global {
  namespace Express {
    interface Request {
      user?: TokenPayload;
    }
  }
}
