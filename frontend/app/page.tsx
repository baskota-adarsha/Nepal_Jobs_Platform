"use client";

import { useJobStats, useJobTrends, useSkillsDemand } from "@/lib/hooks";
import StatCard from "@/components/StatCard";
import SkillBadge from "@/components/SkillBadge";
import Link from "next/link";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function HomePage() {
  const { data: stats, isLoading: statsLoading } = useJobStats();
  const { data: trends, isLoading: trendsLoading } = useJobTrends(6);
  const { data: skills } = useSkillsDemand(8);

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          Nepal IT Job Market Analytics
        </h1>
        <p className="text-gray-500 mt-1 text-sm">
          Real-time insights from merojob.com — updated weekly
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <StatCard
          label="Total jobs"
          value={statsLoading ? "—" : (stats?.total_jobs ?? 0).toLocaleString()}
          sub="Active listings"
          accent
        />
        <StatCard
          label="Companies hiring"
          value={
            statsLoading ? "—" : (stats?.total_companies ?? 0).toLocaleString()
          }
          sub="Across Nepal"
        />
        <StatCard
          label="Avg salary"
          value={
            statsLoading || !stats?.avg_salary
              ? "—"
              : `NRs ${Math.round(stats.avg_salary / 1000)}k`
          }
          sub="Monthly, NPR"
        />
        <StatCard
          label="Top district"
          value={
            statsLoading || !stats?.districts?.[0]
              ? "—"
              : stats.districts[0].district
          }
          sub={
            stats?.districts?.[0]
              ? `${stats.districts[0].count} jobs`
              : undefined
          }
        />
      </div>

      {/* Trends chart */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="text-sm font-medium text-gray-900 mb-4">
          Jobs posted per month
        </h2>
        {trendsLoading ? (
          <div className="h-48 flex items-center justify-center text-sm text-gray-400">
            Loading...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={trends ?? []}
              margin={{ top: 0, right: 0, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 11, fill: "#9ca3af" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#9ca3af" }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "12px",
                  boxShadow: "none",
                }}
              />
              <Bar
                dataKey="job_count"
                fill="#111827"
                radius={[4, 4, 0, 0]}
                name="Jobs posted"
              />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Top skills */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-medium text-gray-900">
            Top skills in demand
          </h2>
          <Link
            href="/skills"
            className="text-xs text-gray-500 hover:text-gray-900"
          >
            View all →
          </Link>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {(skills ?? []).map((skill) => (
            <SkillBadge key={skill.id} skill={skill} />
          ))}
        </div>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          {
            href: "/jobs",
            label: "Browse jobs",
            sub: "Filter by skill, district, salary",
          },
          {
            href: "/skills",
            label: "Skill trends",
            sub: "Rising & falling demand",
          },
          {
            href: "/salaries",
            label: "Salary explorer",
            sub: "By role and district",
          },
          {
            href: "/companies",
            label: "Top companies",
            sub: "Most active hirers",
          },
        ].map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className="border border-gray-200 rounded-xl p-4 bg-white hover:border-gray-400 transition-colors group"
          >
            <p className="text-sm font-medium text-gray-900 group-hover:text-gray-700">
              {item.label}
            </p>
            <p className="text-xs text-gray-400 mt-1">{item.sub}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
