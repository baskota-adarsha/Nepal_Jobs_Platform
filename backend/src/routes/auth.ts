import { Router, Request, Response, NextFunction } from "express";
import { UserRepository } from "../repositories/UserRepository";
import z from "zod";
import { AppError } from "../middleware/errorHandler";
import bcrypt from "bcryptjs";
import { generateTokens } from "../middleware/auth";
import { ApiResponse, AuthTokens } from "../types";
const router = Router();
const repo = new UserRepository();
const loginSchema = z.object({
  email: z.string().email("Invalid Email Format"),
  password: z.string(),
});
const registerSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid Email Format"),
  password: z.string().min(6, "Password must at least be 6 characters"),
});
router.post(
  "/register",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { email, name, password } = registerSchema.parse(req.body);
      const exists = await repo.emailExists(email);
      if (exists) {
        throw new AppError(409, "Email already registered");
      }

      const passwordHash = await bcrypt.hash(password, 12);
      const user = await repo.create(email, passwordHash, name);
      const tokens = generateTokens({
        userId: user.id,
        email: user.email,
        role: user.role,
      });
      const response: ApiResponse<AuthTokens> = {
        success: true,
        message: "Registration successful",
        data: tokens,
      };
      res.status(201).json(response);
    } catch (error) {
      next(error);
    }
  },
);
