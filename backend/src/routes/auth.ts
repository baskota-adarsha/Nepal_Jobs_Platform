import { Router, Request, Response, NextFunction } from "express";
import { UserRepository } from "../repositories/UserRepository";
import z from "zod";
import { AppError } from "../middleware/errorHandler";
import bcrypt from "bcryptjs";
import { generateTokens, verifyRefreshToken } from "../middleware/auth";
import { ApiResponse, AuthTokens } from "../types";
import { authLimiter } from "../middleware/ratelimiter";
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
  authLimiter,
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
router.post(
  "/login",
  authLimiter,
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { email, password } = loginSchema.parse(req.body);
      const user = await repo.findByEmail(email);
      if (!user) {
        throw new AppError(401, "Invalid email or password");
      }
      const passwordMatch = await bcrypt.compare(password, user.password_hash);
      if (!passwordMatch) {
        throw new AppError(401, "Invalid email or password");
      }
      const tokens = generateTokens({
        userId: user.id,
        email: user.email,
        role: user.role,
      });
      const response: ApiResponse<AuthTokens> = {
        success: true,
        message: "Login Successfull",
        data: tokens,
      };
      res.json(response);
    } catch (error) {
      next(error);
    }
  },
);
router.post(
  "/refresh",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { refreshToken } = z
        .object({
          refreshToken: z.string().min(1, "Refresh token required"),
        })
        .parse(req.body);

      const payload = verifyRefreshToken(refreshToken);
      const user = await repo.findById(payload.userId);
      if (!user) {
        throw new AppError(401, "User not found");
      }
      const tokens = generateTokens({
        userId: user.id,
        email: user.email,
        role: user.role,
      });
      res.json({
        success: true,
        message: "Token refreshed",
        data: tokens,
      });
    } catch (error) {
      next(error);
    }
  },
);
router.get("/me", async (req: Request, res: Response, next: NextFunction) => {
  try {
    const user = await repo.findById(req.user!.userId);
    if (!user) {
      throw new AppError(404, "User not found");
    }
    const { password_hash, ...safeUser } = user;
    res.json({
      success: true,
      message: "User Fetched",
      data: safeUser,
    });
  } catch (error) {
    next(error);
  }
});
export default router;
