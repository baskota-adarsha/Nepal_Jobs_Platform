import { Router, Request, Response, NextFunction } from "express";
import { z } from "zod";
import { query } from "../config/db";
import { SalarySummary } from "../types";

const router = Router();

/**
 * @swagger
 * /api/salaries:
 *   get:
 *     summary: Average salary by role, district, experience
 *     tags: [Salaries]
 */
router.get("/", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { district, experience_level, limit } = z
      .object({
        district: z.string().optional(),
        experience_level: z
          .enum(["entry", "mid", "senior", "lead", "manager"])
          .optional(),
        limit: z.coerce.number().int().positive().max(100).default(30),
      })
      .parse(req.query);

    const conditions = ["j.is_active = TRUE", "j.salary_min IS NOT NULL"];
    const params: unknown[] = [];
    let p = 1;

    if (district) {
      conditions.push(`j.district ILIKE $${p++}`);
      params.push(`%${district}%`);
    }
    if (experience_level) {
      conditions.push(`j.experience_level = $${p++}`);
      params.push(experience_level);
    }

    const where = `WHERE ${conditions.join(" AND ")}`;

    const rows = await query<SalarySummary>(
      `SELECT
        j.title                            AS role,
        j.district,
        ROUND(AVG(j.salary_min)::numeric, 0) AS avg_salary_min,
        ROUND(AVG(j.salary_max)::numeric, 0) AS avg_salary_max,
        COUNT(*)::int                        AS job_count,
        j.experience_level
      FROM jobs j
      ${where}
      GROUP BY j.title, j.district, j.experience_level
      HAVING COUNT(*) >= 2
      ORDER BY avg_salary_min DESC
      LIMIT $${p}`,
      [...params, limit],
    );

    res.json({ success: true, message: "Salary data fetched", data: rows });
  } catch (err) {
    next(err);
  }
});

/**
 * @swagger
 * /api/salaries/by-district:
 *   get:
 *     summary: Average salary by district
 *     tags: [Salaries]
 */
router.get(
  "/by-district",
  async (_req: Request, res: Response, next: NextFunction) => {
    try {
      const rows = await query(
        `SELECT
        district,
        ROUND(AVG(salary_min)::numeric, 0) AS avg_salary_min,
        ROUND(AVG(salary_max)::numeric, 0) AS avg_salary_max,
        COUNT(*)::int                       AS job_count
      FROM jobs
      WHERE is_active = TRUE AND salary_min IS NOT NULL
      GROUP BY district
      ORDER BY avg_salary_min DESC`,
      );
      res.json({
        success: true,
        message: "Salary by district fetched",
        data: rows,
      });
    } catch (err) {
      next(err);
    }
  },
);

/**
 * @swagger
 * /api/salaries/percentiles:
 *   get:
 *     summary: Salary percentiles for the Nepal IT market
 *     tags: [Salaries]
 */
router.get(
  "/percentiles",
  async (_req: Request, res: Response, next: NextFunction) => {
    try {
      const rows = await query(
        `SELECT
        ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY salary_min)::numeric, 0) AS p25,
        ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY salary_min)::numeric, 0) AS p50,
        ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY salary_min)::numeric, 0) AS p75,
        ROUND(PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY salary_min)::numeric, 0) AS p90,
        ROUND(MIN(salary_min)::numeric, 0) AS min,
        ROUND(MAX(salary_min)::numeric, 0) AS max,
        ROUND(AVG(salary_min)::numeric, 0) AS mean
      FROM jobs
      WHERE is_active = TRUE AND salary_min IS NOT NULL`,
      );
      res.json({
        success: true,
        message: "Salary percentiles fetched",
        data: rows[0],
      });
    } catch (err) {
      next(err);
    }
  },
);

export default router;
