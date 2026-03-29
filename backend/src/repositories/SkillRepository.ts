import { query } from "../config/db";
import { Skill, SkillDemand } from "../types";

export class SkillRepository {
  async findAll(): Promise<Skill[]> {
    return query<Skill>(
      `SELECT * FROM skills where is_active= TRUE ORDER BY name ASC`,
    );
  }
  async getDemand(limit: number = 20): Promise<SkillDemand[]> {
    const now = new Date();
    const thisMonth = now.getMonth() + 1;
    const thisYear = now.getFullYear();
    const lastMonth = thisMonth === 1 ? 12 : thisMonth - 1;
    const lastYear = thisMonth === 1 ? thisYear - 1 : thisYear;

    return query<SkillDemand>(
      `WITH skill_totals AS (
        SELECT
          s.id,
          s.name,
          s.category,
          COUNT(js.job_id)::int AS total_demand
        FROM skills s
        LEFT JOIN job_skills js ON s.id = js.skill_id
        LEFT JOIN jobs j        ON js.job_id = j.id AND j.is_active = TRUE
        WHERE s.is_active = TRUE
        GROUP BY s.id, s.name, s.category
      ),
      this_month AS (
        SELECT s.id, COUNT(js.job_id)::int AS cnt
        FROM skills s
        LEFT JOIN job_skills js ON s.id = js.skill_id
        LEFT JOIN jobs j ON js.job_id = j.id
          AND EXTRACT(MONTH FROM j.posted_at) = $1
          AND EXTRACT(YEAR  FROM j.posted_at) = $2
          AND j.is_active = TRUE
        GROUP BY s.id
      ),
      last_month AS (
        SELECT s.id, COUNT(js.job_id)::int AS cnt
        FROM skills s
        LEFT JOIN job_skills js ON s.id = js.skill_id
        LEFT JOIN jobs j ON js.job_id = j.id
          AND EXTRACT(MONTH FROM j.posted_at) = $3
          AND EXTRACT(YEAR  FROM j.posted_at) = $4
          AND j.is_active = TRUE
        GROUP BY s.id
      )
      SELECT
        st.id,
        st.name,
        st.category,
        st.total_demand,
        COALESCE(tm.cnt, 0) AS this_month,
        COALESCE(lm.cnt, 0) AS last_month,
        CASE
          WHEN COALESCE(lm.cnt, 0) = 0 AND COALESCE(tm.cnt, 0) > 0 THEN 'rising'
          WHEN COALESCE(lm.cnt, 0) = 0 THEN 'stable'
          WHEN COALESCE(tm.cnt, 0) > COALESCE(lm.cnt, 0) THEN 'rising'
          WHEN COALESCE(tm.cnt, 0) < COALESCE(lm.cnt, 0) THEN 'falling'
          ELSE 'stable'
        END AS trend,
        CASE
          WHEN COALESCE(lm.cnt, 0) = 0 THEN 0
          ELSE ROUND(
            ((COALESCE(tm.cnt, 0)::float - lm.cnt::float) / lm.cnt::float) * 100
          )::int
        END AS trend_pct
      FROM skill_totals st
      LEFT JOIN this_month tm ON st.id = tm.id
      LEFT JOIN last_month lm ON st.id = lm.id
      WHERE st.total_demand > 0
      ORDER BY st.total_demand DESC
      LIMIT $5`,
      [thisMonth, thisYear, lastMonth, lastYear, limit],
    );
  }
  async getByCategory(): Promise<
    { category: string; skills: Skill[]; total_jobs: number }[]
  > {
    const rows = await query<Skill & { total_jobs: number }>(
      `SELECT
        s.*,
        COUNT(js.job_id)::int AS total_jobs
      FROM skills s
      LEFT JOIN job_skills js ON s.id = js.skill_id
      LEFT JOIN jobs j        ON js.job_id = j.id AND j.is_active = TRUE
      WHERE s.is_active = TRUE
      GROUP BY s.id
      ORDER BY s.category, total_jobs DESC`,
    );

    const grouped = rows.reduce<Record<string, typeof rows>>((acc, row) => {
      if (!acc[row.category]) acc[row.category] = [];
      acc[row.category].push(row);
      return acc;
    }, {});

    return Object.entries(grouped).map(([category, skills]) => ({
      category,
      skills,
      total_jobs: skills.reduce((sum, s) => sum + s.total_jobs, 0),
    }));
  }
}
