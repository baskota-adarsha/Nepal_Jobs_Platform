import { query, queryOne } from "../config/db";
import { JobWithCompany } from "../types";
export class JobRepository {
  async findAll() {
    const countResult = await queryOne<{ count: string }>(
      "SELECT COUNT(*) as count FROM jobs ",
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
    
      GROUP BY j.id, c.name, c.industry
      ORDER BY j.posted_at DESC
     
      
      `,
    );
  }
}
