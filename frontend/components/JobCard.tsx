import { Job } from "@/lib/api";

const levelColors: Record<string, string> = {
  entry: "bg-green-50 text-green-700",
  mid: "bg-blue-50 text-blue-700",
  senior: "bg-purple-50 text-purple-700",
  lead: "bg-orange-50 text-orange-700",
  manager: "bg-red-50 text-red-700",
};

export default function JobCard({ job }: { job: Job }) {
  const salary =
    job.salary_min && job.salary_max
      ? `NRs ${(job.salary_min / 1000).toFixed(0)}k – ${(job.salary_max / 1000).toFixed(0)}k`
      : job.salary_min
        ? `NRs ${(job.salary_min / 1000).toFixed(0)}k+`
        : "Negotiable";

  const posted = new Date(job.posted_at).toLocaleDateString("en-NP", {
    month: "short",
    day: "numeric",
  });

  return (
    <div className="border border-gray-200 rounded-xl p-4 bg-white hover:border-gray-400 transition-colors">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div>
          <h3 className="font-medium text-gray-900 text-sm">{job.title}</h3>
          <p className="text-xs text-gray-500 mt-0.5">{job.company_name}</p>
        </div>
        <span
          className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${levelColors[job.experience_level] ?? "bg-gray-100 text-gray-600"}`}
        >
          {job.experience_level}
        </span>
      </div>

      <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
        <span>{job.district}</span>
        <span>·</span>
        <span>{job.job_type}</span>
        <span>·</span>
        <span className="font-medium text-gray-700">{salary}</span>
      </div>

      {job.skills.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {job.skills.slice(0, 4).map((skill) => (
            <span
              key={skill}
              className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-md"
            >
              {skill}
            </span>
          ))}
          {job.skills.length > 4 && (
            <span className="text-xs text-gray-400">
              +{job.skills.length - 4}
            </span>
          )}
        </div>
      )}

      <p className="text-xs text-gray-400 mt-3">{posted}</p>
    </div>
  );
}
