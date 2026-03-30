"use client";

import { useTopCompanies, useCompaniesByIndustry } from "@/lib/hooks";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const COLORS = [
  "#111827",
  "#374151",
  "#6b7280",
  "#9ca3af",
  "#d1d5db",
  "#e5e7eb",
];

const sizeLabel: Record<string, string> = {
  "1-10": "Startup",
  "11-50": "Small",
  "51-200": "Mid-size",
  "201-500": "Large",
  "500+": "Enterprise",
};

export default function CompaniesPage() {
  const { data: companies, isLoading } = useTopCompanies(20);
  const { data: byIndustry } = useCompaniesByIndustry();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          Top hiring companies
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Most active employers in Nepal IT market
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Company list */}
        <div className="lg:col-span-2 space-y-3">
          {isLoading
            ? Array.from({ length: 6 }).map((_, i) => (
                <div
                  key={i}
                  className="border border-gray-100 rounded-xl p-4 bg-white animate-pulse h-20"
                />
              ))
            : (companies ?? []).map((company, i) => (
                <div
                  key={company.id}
                  className="border border-gray-200 rounded-xl p-4 bg-white flex items-center gap-4"
                >
                  <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center text-xs font-semibold text-gray-500 shrink-0">
                    {i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {company.name}
                      </p>
                      <span className="text-xs text-gray-400 shrink-0">
                        {sizeLabel[company.size] ?? company.size}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <p className="text-xs text-gray-500">
                        {company.industry}
                      </p>
                      <span className="text-gray-300">·</span>
                      <p className="text-xs text-gray-500">
                        {company.district}
                      </p>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-lg font-semibold text-gray-900">
                      {company.job_count}
                    </p>
                    <p className="text-xs text-gray-400">jobs</p>
                  </div>
                </div>
              ))}
        </div>

        {/* Industry pie chart */}
        {byIndustry && (
          <div className="bg-white border border-gray-200 rounded-xl p-5">
            <h2 className="text-sm font-medium text-gray-900 mb-4">
              Jobs by industry
            </h2>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={byIndustry}
                  dataKey="job_count"
                  nameKey="industry"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  stroke="none"
                >
                  {byIndustry.map((_: unknown, index: number) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                    fontSize: "11px",
                    boxShadow: "none",
                  }}
                  formatter={(v: number, name: string) => [`${v} jobs`, name]}
                />
                <Legend
                  iconType="square"
                  iconSize={8}
                  wrapperStyle={{ fontSize: "10px" }}
                  formatter={(value: string) =>
                    value.length > 20 ? value.slice(0, 20) + "…" : value
                  }
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}
