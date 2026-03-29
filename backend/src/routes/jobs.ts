import { Request, Response, NextFunction, Router } from "express";
import { ApiResponse, JobFilters } from "../types";
import { success, z } from "zod";
import { JobRepository } from "../repositories/JobRepository";
const router = Router();
const repo = new JobRepository();
const JobFiltersSchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(50).default(20),
  district: z.string().optional(),
  skill: z.string().optional(),
  salary_min: z.coerce.number().int().positive().optional(),
  salary_max: z.coerce.number().int().positive().optional(),
  job_type: z
    .enum(["full-time", "part-time", "contract", "internship", "remote"])
    .optional(),
  experience_level: z
    .enum(["entry", "mid", "senior", "lead", "manager"])
    .optional(),
  search: z.string().optional(),
});
router.get("/", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const filters = JobFiltersSchema.parse(req.query);
    const result = await repo.findAll(filters);
    const response: ApiResponse<typeof result> = {
      data: result,
      success: true,
      message: "Jobs fetched successfully",
    };
    res.json(response);
  } catch (error) {
    next(error);
  }
});

router.get(
  "/stats",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const stats = await repo.getStats();
      res.json({
        success: true,
        message: "Stats Fetched",
        data: stats,
      });
    } catch (error) {
      next(error);
    }
  },
);

router.get(
  "/trends",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { months } = z
        .object({
          months: z.coerce.number().int().positive().max(24).default(6),
        })
        .parse(req.query);
      const trends = await repo.getTrends(months);
      res.json({
        success: true,
        message: "Trends Fetched",
        data: trends,
      });
    } catch (error) {
      next(error);
    }
  },
);
router.get("/:id", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { id } = z
      .object({
        id: z.string().uuid("Invalid job ID format"),
      })
      .parse(req.params);
    const job = await repo.findById(id);
    if (!job) {
      res.status(404).json({ success: false, message: "Job not found" });
    }
    res.json({
      success: true,
      message: "Job Fetched",
      data: job,
    });
  } catch (error) {
    next(error);
  }
});

export default router;
