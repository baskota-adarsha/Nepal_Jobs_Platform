import { Router, Request, Response, NextFunction } from "express";
import { CompanyRepository } from "../repositories/CompanyRepository";
import { z } from "zod";

const router = Router();
const repo = new CompanyRepository();
router.get("/", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const companies = await repo.findAll();
    res.json({
      success: true,
      message: "Companies fetched",
      data: companies,
    });
  } catch (error) {
    next(error);
  }
});
router.get("/top", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { limit } = z
      .object({
        limit: z.coerce.number().int().positive().max(30).default(10),
      })
      .parse(req.query);
    const companies = await repo.getTopHirers(limit);
    res.json({
      success: true,
      message: "Top Companies fetched",
      data: companies,
    });
  } catch (error) {
    next(error);
  }
});

router.get(
  "/by-industry",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const data = await repo.getByIndustry();
      res.json({
        success: true,
        message: "Companies by industry fetched",
        data: data,
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
        id: z.string().uuid("Invalid company ID"),
      })
      .parse(req.params);
    const company = await repo.findById(id);
    if (!company) {
      res.status(404).json({ success: false, message: "Company not found" });
      return;
    }
    res.json({
      success: true,
      message: "Company fetched",
      data: company,
    });
  } catch (error) {
    next(error);
  }
});
export default router;
