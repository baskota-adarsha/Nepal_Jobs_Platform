"use client";

import { useSkillsDemand, useSkillsByCategory } from "@/lib/hooks";
import SkillBadge from "@/components/SkillBadge";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

const trendFill = {
  rising: "#16a34a",
  falling: "#dc2626",
  stable: "#6b7280",
};

export default function SkillsPage() {
  const { data: skills, isLoading } = useSkillsDemand(30);
  const { data: byCategory } = useSkillsByCategory();

  const top10 = (skills ?? []).slice(0, 10);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Skills demand</h1>
        <p className="text-gray-500 text-sm mt-1">
          Most in-demand skills in Nepal IT — with month-over-month trend
        </p>
      </div>

      {/* Bar chart */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="text-sm font-medium text-gray-900 mb-4">
          Top 10 skills by job count
        </h2>
        {isLoading ? (
          <div className="h-48 flex items-center justify-center text-sm text-gray-400">
            Loading...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart
              data={top10}
              layout="vertical"
              margin={{ top: 0, right: 20, left: 60, bottom: 0 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#f0f0f0"
                horizontal={false}
              />
              <XAxis
                type="number"
                tick={{ fontSize: 11, fill: "#9ca3af" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 11, fill: "#374151" }}
                axisLine={false}
                tickLine={false}
                width={55}
              />
              <Tooltip
                contentStyle={{
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "12px",
                  boxShadow: "none",
                }}
                formatter={(val: number) => [`${val} jobs`, "Demand"]}
              />
              <Bar dataKey="total_demand" radius={[0, 4, 4, 0]} name="Jobs">
                {top10.map((skill) => (
                  <Cell key={skill.id} fill={trendFill[skill.trend]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
        <div className="flex items-center gap-4 mt-3">
          {Object.entries(trendFill).map(([trend, color]) => (
            <div key={trend} className="flex items-center gap-1.5">
              <div
                className="w-2.5 h-2.5 rounded-sm"
                style={{ background: color }}
              />
              <span className="text-xs text-gray-500 capitalize">{trend}</span>
            </div>
          ))}
        </div>
      </div>

      {/* All skills grid */}
      <div>
        <h2 className="text-sm font-medium text-gray-900 mb-4">All skills</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {(skills ?? []).map((skill) => (
            <SkillBadge key={skill.id} skill={skill} />
          ))}
        </div>
      </div>

      {/* By category */}
      {byCategory && (
        <div>
          <h2 className="text-sm font-medium text-gray-900 mb-4">
            Skills by category
          </h2>
          <div className="space-y-4">
            {byCategory.map(
              (cat: {
                category: string;
                total_jobs: number;
                skills: { id: string; name: string }[];
              }) => (
                <div
                  key={cat.category}
                  className="bg-white border border-gray-200 rounded-xl p-4"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-medium text-gray-900 capitalize">
                      {cat.category}
                    </span>
                    <span className="text-xs text-gray-400">
                      {cat.total_jobs} jobs
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {cat.skills.map((s: { id: string; name: string }) => (
                      <span
                        key={s.id}
                        className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-md"
                      >
                        {s.name}
                      </span>
                    ))}
                  </div>
                </div>
              ),
            )}
          </div>
        </div>
      )}
    </div>
  );
}
