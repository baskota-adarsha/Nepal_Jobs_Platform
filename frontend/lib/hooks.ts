import { useQuery } from "@tanstack/react-query";
import {
  getJobs,
  getJobStats,
  getJobTrends,
  getSkillsDemand,
  getSkillsByCategory,
  getSalaries,
  getSalariesByDistrict,
  getSalaryPercentiles,
  getTopCompanies,
  getCompaniesByIndustry,
  JobFilters,
} from "./api";

export const useJobStats = () =>
  useQuery({
    queryKey: ["job-stats"],
    queryFn: getJobStats,
    staleTime: 5 * 60 * 1000,
  });

export const useJobs = (filters?: JobFilters) =>
  useQuery({
    queryKey: ["jobs", filters],
    queryFn: () => getJobs(filters),
    staleTime: 2 * 60 * 1000,
  });

export const useJobTrends = (months = 6) =>
  useQuery({
    queryKey: ["job-trends", months],
    queryFn: () => getJobTrends(months),
    staleTime: 10 * 60 * 1000,
  });

export const useSkillsDemand = (limit = 20) =>
  useQuery({
    queryKey: ["skills-demand", limit],
    queryFn: () => getSkillsDemand(limit),
    staleTime: 10 * 60 * 1000,
  });

export const useSkillsByCategory = () =>
  useQuery({
    queryKey: ["skills-category"],
    queryFn: getSkillsByCategory,
    staleTime: 10 * 60 * 1000,
  });

export const useSalaries = (filters?: {
  district?: string;
  experience_level?: string;
}) =>
  useQuery({
    queryKey: ["salaries", filters],
    queryFn: () => getSalaries(filters),
    staleTime: 10 * 60 * 1000,
  });

export const useSalariesByDistrict = () =>
  useQuery({
    queryKey: ["salaries-district"],
    queryFn: getSalariesByDistrict,
    staleTime: 10 * 60 * 1000,
  });

export const useSalaryPercentiles = () =>
  useQuery({
    queryKey: ["salary-percentiles"],
    queryFn: getSalaryPercentiles,
    staleTime: 10 * 60 * 1000,
  });

export const useTopCompanies = (limit = 10) =>
  useQuery({
    queryKey: ["top-companies", limit],
    queryFn: () => getTopCompanies(limit),
    staleTime: 5 * 60 * 1000,
  });

export const useCompaniesByIndustry = () =>
  useQuery({
    queryKey: ["companies-industry"],
    queryFn: getCompaniesByIndustry,
    staleTime: 10 * 60 * 1000,
  });
