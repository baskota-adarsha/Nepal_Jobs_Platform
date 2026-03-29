import { NextFunction, Router, Request, Response } from "express";
import { SkillRepository } from "../repositories/SkillRepository";
import { success, z } from "zod";
const router = Router();

const repo = new SkillRepository();
router.get("/", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const skills = await repo.findAll();
    res.json({ success: true, message: "Skills fetched", data: skills });
  } catch (error) {
    next(error);
  }
});
router.get(
  "/demand",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { limit } = z
        .object({
          limit: z.coerce.number().int().positive().max(50).default(20),
        })
        .parse(req.query);
      const demand = await repo.getDemand(limit);
      res.json({
        success: true,
        message: "Skill demand fetched",
        data: demand,
      });
    } catch (error) {
      next(error);
    }
  },
);

router.get(
  "/by-category",
  async (_req: Request, res: Response, next: NextFunction) => {
    try {
      const categories = await repo.getByCategory();
      res.json({
        success: true,
        message: "Skills by category fetched",
        data: categories,
      });
    } catch (err) {
      next(err);
    }
  },
);

export default router;
