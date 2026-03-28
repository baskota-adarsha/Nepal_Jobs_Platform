import { query } from "../config/db";
import { Company, CompanyWithJobCount } from "../types";
export class CompanyRepository {
  async getTopHirers(limit: number = 10): Promise<CompanyWithJobCount[]> {
    return query<CompanyWithJobCount>(
      `SELECT
        c.*,
        COUNT(j.id)::int AS job_count
      FROM companies c
      JOIN jobs j ON c.id = j.company_id AND j.is_active = TRUE
      WHERE c.is_active = TRUE
      GROUP BY c.id
      ORDER BY job_count DESC
      LIMIT $1`,
      [limit],
    );
  }
  async findAll(): Promise<CompanyWithJobCount[]> {
    return query<CompanyWithJobCount>(
      `SELECT
        c.*,
        COUNT(j.id)::int AS job_count
      FROM companies c
      LEFT JOIN jobs j ON c.id = j.company_id AND j.is_active = TRUE
      WHERE c.is_active = TRUE
      GROUP BY c.id
      ORDER BY c.name ASC
      `,
    );
  }

  async findById(id: string): Promise<CompanyWithJobCount | null> {
    const rows = await query<CompanyWithJobCount>(
      `SELECT
        c.*,
        COUNT(j.id)::int AS job_count
      FROM companies c
      LEFT JOIN jobs j ON c.id = j.company_id AND j.is_active = TRUE
      WHERE c.id = $1
      GROUP BY c.id`,
      [id],
    );
    return rows[0] ?? null;
  }

  async getByIndustry(): Promise<
    {
      industry: string;
      company_count: number;
      job_count: number;
    }[]
  > {
    return query(
      `
        SELECT c.industry,
        COUNT(DISTINCT c.id)::int AS company_count,
        COUNT(j.id)::int as job_count

        from 
        companies c 
        left join 
        jobs j on c.id=j.company_id and j.is_active=true
        where c.is_active=true
        GROUP BY c.industry
        ORDER BY job_count DESC
        
        `,
    );
  }
}
