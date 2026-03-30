"use client";

import { useState } from "react";
import { useJobs } from "@/lib/hooks";
import JobCard from "@/components/JobCard";
import { JobFilters } from "@/lib/api";

const DISTRICTS = ["Kathmandu", "Lalitpur", "Bhaktapur"];
const JOB_TYPES = [
  "full-time",
  "part-time",
  "contract",
  "internship",
  "remote",
];
const EXP_LEVELS = ["entry", "mid", "senior", "lead", "manager"];

export default function JobsPage() {
  const [filters, setFilters] = useState<JobFilters>({ page: 1, limit: 20 });
  const [search, setSearch] = useState("");

  const { data, isLoading } = useJobs(filters);

  const applyFilter = (
    key: keyof JobFilters,
    value: string | number | undefined,
  ) => {
    setFilters((f) => ({ ...f, [key]: value, page: 1 }));
  };

  const handleSearch = () => {
    setFilters((f) => ({ ...f, search: search || undefined, page: 1 }));
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Job listings</h1>
        <p className="text-gray-500 text-sm mt-1">
          {data?.pagination.total ?? "—"} active jobs in Nepal IT
        </p>
      </div>

      {/* Search + filters */}
      <div className="bg-white border border-gray-200 rounded-xl p-4 space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Search job title or keyword..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="flex-1 border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-gray-400"
          />
          <button
            onClick={handleSearch}
            className="px-4 py-2 bg-gray-900 text-white text-sm rounded-lg hover:bg-gray-700 transition-colors"
          >
            Search
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          <select
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-600 focus:outline-none focus:border-gray-400"
            onChange={(e) =>
              applyFilter("district", e.target.value || undefined)
            }
          >
            <option value="">All districts</option>
            {DISTRICTS.map((d) => (
              <option key={d}>{d}</option>
            ))}
          </select>

          <select
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-600 focus:outline-none focus:border-gray-400"
            onChange={(e) =>
              applyFilter("job_type", e.target.value || undefined)
            }
          >
            <option value="">All types</option>
            {JOB_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>

          <select
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm text-gray-600 focus:outline-none focus:border-gray-400"
            onChange={(e) =>
              applyFilter("experience_level", e.target.value || undefined)
            }
          >
            <option value="">All levels</option>
            {EXP_LEVELS.map((l) => (
              <option key={l} value={l}>
                {l}
              </option>
            ))}
          </select>

          <input
            type="number"
            placeholder="Min salary (NRs)"
            className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm w-40 focus:outline-none focus:border-gray-400"
            onChange={(e) =>
              applyFilter(
                "salary_min",
                e.target.value ? Number(e.target.value) : undefined,
              )
            }
          />

          <button
            onClick={() => {
              setFilters({ page: 1, limit: 20 });
              setSearch("");
            }}
            className="text-xs text-gray-400 hover:text-gray-700 px-2"
          >
            Clear filters
          </button>
        </div>
      </div>

      {/* Job grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div
              key={i}
              className="border border-gray-100 rounded-xl p-4 bg-white animate-pulse"
            >
              <div className="h-4 bg-gray-100 rounded w-3/4 mb-2" />
              <div className="h-3 bg-gray-100 rounded w-1/2 mb-4" />
              <div className="h-3 bg-gray-100 rounded w-full" />
            </div>
          ))}
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {(data?.data ?? []).map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>

          {/* Pagination */}
          {data && data.pagination.totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 pt-4">
              <button
                disabled={!data.pagination.hasPrev}
                onClick={() =>
                  setFilters((f) => ({ ...f, page: (f.page ?? 1) - 1 }))
                }
                className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg disabled:opacity-40 hover:border-gray-400 transition-colors"
              >
                ← Prev
              </button>
              <span className="text-sm text-gray-500">
                Page {data.pagination.page} of {data.pagination.totalPages}
              </span>
              <button
                disabled={!data.pagination.hasNext}
                onClick={() =>
                  setFilters((f) => ({ ...f, page: (f.page ?? 1) + 1 }))
                }
                className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg disabled:opacity-40 hover:border-gray-400 transition-colors"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
