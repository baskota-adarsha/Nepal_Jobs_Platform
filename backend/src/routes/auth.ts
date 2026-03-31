import { Router, Request, Response, NextFunction } from "express";
import { UserRepository } from "../repositories/UserRepository";
import z, { success } from "zod";
import { AppError } from "../middleware/errorHandler";
import bcrypt from "bcryptjs";
import { generateTokens, verifyRefreshToken } from "../middleware/auth";
import { ApiResponse, AuthTokens } from "../types";
import { authLimiter } from "../middleware/ratelimiter";
const router = Router();
const repo = new UserRepository();
const COOKIE_OPTIONS = {
  httpOnly: true,
  secure: process.env.NODE_ENV === "production",
  sameSite: "strict" as const,
};
const ACCESS_MAX_AGE = 15 * 60 * 1000; // 15 minutes
const REFRESH_MAX_AGE = 7 * 24 * 60 * 60 * 1000; // 7 days
const loginSchema = z.object({
  email: z.string().email("Invalid Email Format"),
  password: z.string(),
});
const registerSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Invalid Email Format"),
  password: z.string().min(6, "Password must at least be 6 characters"),
});

function setAuthCookies(
  res: Response,
  accessToken: string,
  refreshToken: string,
) {
  res.cookie("access_token", accessToken, {
    ...COOKIE_OPTIONS,
    maxAge: ACCESS_MAX_AGE,
  });
  res.cookie("refresh_token", refreshToken, {
    ...COOKIE_OPTIONS,
    maxAge: REFRESH_MAX_AGE,
    path: "/api/auth/refresh",
  });
}
function clearAuthCookies(res: Response) {
  res.clearCookie("access_token");
  res.clearCookie("refresh_token", { path: "/api/auth/refresh" });
}
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
      setAuthCookies(res, tokens.accessToken, tokens.refreshToken);
      res.status(201).json({
        success: true,
        message: "Registration successful",
        data: {
          user: {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
          },
        },
      });
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
      setAuthCookies(res, tokens.accessToken, tokens.refreshToken);
      res.json({
        success: true,
        message: "Login successful",
        data: {
          user: {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
          },
        },
      });
    } catch (error) {
      next(error);
    }
  },
);
router.post(
  "/refresh",
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const refreshToken = req.cookies?.refresh_token;
      if (!refreshToken) throw new AppError(401, "No refresh token");

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
      setAuthCookies(res, tokens.accessToken, tokens.refreshToken);
      res.json({
        success: true,
        message: "Token refreshed",
      });
    } catch (error) {
      next(error);
    }
  },
);
router.post("/logout", (req: Request, res: Response) => {
  clearAuthCookies(res);
  res.json({ success: true, message: "Logged out" });
});

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
