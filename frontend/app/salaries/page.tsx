"use client";

import { useState } from "react";
import {
  useSalaries,
  useSalariesByDistrict,
  useSalaryPercentiles,
} from "@/lib/hooks";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const EXP_LEVELS = ["entry", "mid", "senior", "lead", "manager"];
const DISTRICTS = ["Kathmandu", "Lalitpur", "Bhaktapur"];

export default function SalariesPage() {
  const [expLevel, setExpLevel] = useState<string | undefined>();
  const [district, setDistrict] = useState<string | undefined>();

  const { data: salaries } = useSalaries({
    district,
    experience_level: expLevel,
  });
  const { data: byDistrict } = useSalariesByDistrict();
  const { data: percentiles } = useSalaryPercentiles();

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">
          Salary explorer
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          Average salaries in Nepal IT — in NPR per month
        </p>
      </div>

      {/* Percentile cards */}
      {percentiles && (
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-3">
          {[
            { label: "25th %ile", val: percentiles.p25 },
            { label: "Median", val: percentiles.p50 },
            { label: "75th %ile", val: percentiles.p75 },
            { label: "90th %ile", val: percentiles.p90 },
            { label: "Average", val: percentiles.mean },
            { label: "Max", val: percentiles.max },
          ].map((item) => (
            <div
              key={item.label}
              className="bg-white border border-gray-200 rounded-xl p-3 text-center"
            >
              <p className="text-xs text-gray-400 mb-1">{item.label}</p>
              <p className="text-sm font-semibold text-gray-900">
                NRs {Math.round(item.val / 1000)}k
              </p>
            </div>
          ))}
        </div>
      )}

      {/* District chart */}
      {byDistrict && (
        <div className="bg-white border border-gray-200 rounded-xl p-5">
          <h2 className="text-sm font-medium text-gray-900 mb-4">
            Average salary by district
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart
              data={byDistrict}
              margin={{ top: 0, right: 0, left: -10, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="district"
                tick={{ fontSize: 11, fill: "#9ca3af" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#9ca3af" }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => `${Math.round(v / 1000)}k`}
              />
              <Tooltip
                contentStyle={{
                  border: "1px solid #e5e7eb",
                  borderRadius: "8px",
                  fontSize: "12px",
                  boxShadow: "none",
                }}
                formatter={(v: number) => [`NRs ${Math.round(v / 1000)}k`, ""]}
              />
              <Legend
                iconType="square"
                iconSize={8}
                wrapperStyle={{ fontSize: "11px" }}
              />
              <Bar
                dataKey="avg_salary_min"
                fill="#111827"
                radius={[4, 4, 0, 0]}
                name="Min salary"
              />
              <Bar
                dataKey="avg_salary_max"
                fill="#d1d5db"
                radius={[4, 4, 0, 0]}
                name="Max salary"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Filters + table */}
      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-medium text-gray-900">Salary by role</h2>
          <div className="flex gap-2">
            <select
              className="border border-gray-200 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:border-gray-400"
              onChange={(e) => setDistrict(e.target.value || undefined)}
            >
              <option value="">All districts</option>
              {DISTRICTS.map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
            <select
              className="border border-gray-200 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:border-gray-400"
              onChange={(e) => setExpLevel(e.target.value || undefined)}
            >
              <option value="">All levels</option>
              {EXP_LEVELS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left text-xs font-medium text-gray-400 pb-2 pr-4">
                  Role
                </th>
                <th className="text-left text-xs font-medium text-gray-400 pb-2 pr-4">
                  District
                </th>
                <th className="text-left text-xs font-medium text-gray-400 pb-2 pr-4">
                  Level
                </th>
                <th className="text-right text-xs font-medium text-gray-400 pb-2 pr-4">
                  Min
                </th>
                <th className="text-right text-xs font-medium text-gray-400 pb-2">
                  Max
                </th>
              </tr>
            </thead>
            <tbody>
              {(salaries ?? []).slice(0, 30).map((row, i) => (
                <tr
                  key={i}
                  className="border-b border-gray-50 hover:bg-gray-50"
                >
                  <td className="py-2 pr-4 font-medium text-gray-900 text-xs">
                    {row.role}
                  </td>
                  <td className="py-2 pr-4 text-gray-500 text-xs">
                    {row.district}
                  </td>
                  <td className="py-2 pr-4">
                    <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded capitalize">
                      {row.experience_level}
                    </span>
                  </td>
                  <td className="py-2 pr-4 text-right text-xs text-gray-700">
                    NRs {Math.round(row.avg_salary_min / 1000)}k
                  </td>
                  <td className="py-2 text-right text-xs text-gray-700">
                    NRs {Math.round(row.avg_salary_max / 1000)}k
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {!salaries?.length && (
            <p className="text-center text-sm text-gray-400 py-8">
              No salary data found for these filters
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
