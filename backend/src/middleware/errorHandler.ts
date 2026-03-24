import { Request, Response, NextFunction } from "express";
import { ZodError } from "zod";
import { ApiResponse } from "../types";

export class AppError extends Error {
  constructor(
    public statusCode: number,
    message: string,
    public isOperational = true,
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

export const errorHandler = (
  err: Error,
  _req: Request,
  res: Response,
  _next: NextFunction,
): void => {
  if (err instanceof ZodError) {
    const response: ApiResponse = {
      success: false,
      message: "Validation error",
      error: err.issues
        .map((e) => `${e.path.join(".")}: ${e.message}`)
        .join(", "),
    };
    res.status(400).json(response);
    return;
  }
  if (err instanceof AppError) {
    const response: ApiResponse = {
      success: false,
      message: err.message,
    };

    res.status(err.statusCode).json(response);
    return;
  }

  console.error("Unhandled error:", err);
  const response: ApiResponse = {
    success: false,
    message: "Internal Server Error",
    error: process.env.NODE_ENV === "development" ? err.message : undefined,
  };
  res.status(500).json(response);
};
export const notFound = (_req: Request, res: Response): void => {
  res.status(404).json({
    success: false,
    message: `Route not found`,
  });
};
