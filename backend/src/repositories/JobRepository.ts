import { query, queryOne } from "../config/db";
import {
  JobWithCompany,
  JobFilters,
  PaginatedResponse,
  JobTrend,
} from "../types";

export class JobRepository {
  async findAll(
    filters: JobFilters,
  ): Promise<PaginatedResponse<JobWithCompany>> {
    const page = Math.max(1, filters.page ?? 1);
    const limit = Math.min(50, Math.max(1, filters.limit ?? 20));
    const offset = (page - 1) * limit;

    const conditions: string[] = ["j.is_active = TRUE"];
    const params: unknown[] = [];
    let p = 1;

    if (filters.district) {
      conditions.push(`j.district ILIKE $${p++}`);
      params.push(`%${filters.district}%`);
    }
    if (filters.job_type) {
      conditions.push(`j.job_type = $${p++}`);
      params.push(filters.job_type);
    }
    if (filters.experience_level) {
      conditions.push(`j.experience_level = $${p++}`);
      params.push(filters.experience_level);
    }
    if (filters.salary_min !== undefined) {
      conditions.push(`j.salary_min >= $${p++}`);
      params.push(filters.salary_min);
    }
    if (filters.salary_max !== undefined) {
      conditions.push(`j.salary_max <= $${p++}`);
      params.push(filters.salary_max);
    }
    if (filters.search) {
      conditions.push(`(j.title ILIKE $${p} OR j.description ILIKE $${p})`);
      params.push(`%${filters.search}%`);
      p++;
    }
    if (filters.skill) {
      conditions.push(`
        EXISTS (
          SELECT 1 FROM job_skills js2
          JOIN skills s2 ON js2.skill_id = s2.id
          WHERE js2.job_id = j.id
          AND s2.name ILIKE $${p++}
        )
      `);
      params.push(`%${filters.skill}%`);
    }

    const where = conditions.length ? `WHERE ${conditions.join(" AND ")}` : "";

    const countResult = await queryOne<{ count: string }>(
      `SELECT COUNT(*) as count FROM jobs j ${where}`,
      params,
    );
    const total = parseInt(countResult?.count ?? "0", 10);

    const rows = await query<JobWithCompany>(
      `SELECT
        j.*,
        c.name        AS company_name,
        c.industry    AS company_industry,
        COALESCE(
          ARRAY_AGG(s.name ORDER BY s.name) FILTER (WHERE s.name IS NOT NULL),
          '{}'
        ) AS skills
      FROM jobs j
      JOIN companies c ON j.company_id = c.id
      LEFT JOIN job_skills js ON j.id = js.job_id
      LEFT JOIN skills s     ON js.skill_id = s.id
      ${where}
      GROUP BY j.id, c.name, c.industry
      ORDER BY j.posted_at DESC
      LIMIT $${p} OFFSET $${p + 1}`,
      [...params, limit, offset],
    );

    return {
      data: rows,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
        hasNext: page * limit < total,
        hasPrev: page > 1,
      },
    };
  }

  async findById(id: string): Promise<JobWithCompany | null> {
    const rows = await query<JobWithCompany>(
      `SELECT
        j.*,
        c.name     AS company_name,
        c.industry AS company_industry,
        COALESCE(
          ARRAY_AGG(s.name ORDER BY s.name) FILTER (WHERE s.name IS NOT NULL),
          '{}'
        ) AS skills
      FROM jobs j
      JOIN companies c ON j.company_id = c.id
      LEFT JOIN job_skills js ON j.id = js.job_id
      LEFT JOIN skills s     ON js.skill_id = s.id
      WHERE j.id = $1 AND j.is_active = TRUE
      GROUP BY j.id, c.name, c.industry`,
      [id],
    );

    return rows[0] ?? null;
  }
  async getTrends(months: number = 6): Promise<JobTrend[]> {
    return query<JobTrend>(
      `SELECT
        TO_CHAR(DATE_TRUNC('month', posted_at), 'Mon')  AS month,
        EXTRACT(YEAR  FROM posted_at)::int               AS year,
        COUNT(*)::int                                    AS job_count,
        ROUND(AVG(salary_min)::numeric, 0)               AS avg_salary_min
      FROM jobs
      WHERE posted_at >= NOW() - INTERVAL '1 month' * $1
        AND is_active = TRUE
      GROUP BY DATE_TRUNC('month', posted_at),
               EXTRACT(YEAR FROM posted_at)
      ORDER BY DATE_TRUNC('month', posted_at) ASC`,
      [months],
    );
  }
  async getStats(): Promise<{
    total_jobs: number;
    total_companies: number;
    avg_salary: number;
    districts: { district: string; count: number }[];
  }> {
    const [totals] = await query<{
      total_jobs: number;
      total_companies: number;
      avg_salary: number;
    }>(`SELECT
        COUNT(DISTINCT j.id)::int         AS total_jobs,
        COUNT(DISTINCT j.company_id)::int AS total_companies,
        ROUND(AVG(j.salary_min)::numeric, 0) AS avg_salary
      FROM jobs j
      WHERE j.is_active = TRUE`);

    const districts = await query<{ district: string; count: number }>(
      `SELECT district, COUNT(*)::int AS count
       FROM jobs WHERE is_active = TRUE
       GROUP BY district ORDER BY count DESC`,
    );
    return { ...totals, districts };
  }
}
