import { SkillDemand } from "@/lib/api";

const trendIcon = {
  rising: "↑",
  falling: "↓",
  stable: "→",
};

const trendColor = {
  rising: "text-green-600",
  falling: "text-red-500",
  stable: "text-gray-400",
};

const categoryColor: Record<string, string> = {
  frontend: "border-blue-200 bg-blue-50",
  backend: "border-purple-200 bg-purple-50",
  database: "border-amber-200 bg-amber-50",
  data: "border-teal-200 bg-teal-50",
  devops: "border-orange-200 bg-orange-50",
  mobile: "border-pink-200 bg-pink-50",
  design: "border-rose-200 bg-rose-50",
  other: "border-gray-200 bg-gray-50",
};

export default function SkillBadge({ skill }: { skill: SkillDemand }) {
  return (
    <div
      className={`border rounded-lg p-3 ${categoryColor[skill.category] ?? categoryColor.other}`}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="text-sm font-medium text-gray-900">{skill.name}</span>
        <span className={`text-xs font-medium ${trendColor[skill.trend]}`}>
          {trendIcon[skill.trend]}
          {skill.trend_pct !== 0 && ` ${Math.abs(skill.trend_pct)}%`}
        </span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">{skill.total_demand} jobs</span>
        <span className="text-xs text-gray-400 capitalize">
          {skill.category}
        </span>
      </div>
    </div>
  );
}
