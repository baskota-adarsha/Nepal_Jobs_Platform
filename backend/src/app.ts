import "dotenv/config";
import express from "express";
import cors from "cors";
import helmet from "helmet";
import { apiLimiter } from "./middleware/ratelimiter";
import authRoutes from "./routes/auth";
import { errorHandler, notFound } from "./middleware/errorHandler";
import companyRoutes from "./routes/companies";
const app = express();
app.use(helmet());
app.use(
  cors({
    origin: process.env.CORS_ORIGIN ?? "*",
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  }),
);
app.use(express.json({ limit: "10kb" }));
app.use(express.urlencoded({ extended: true }));
app.use("/api", apiLimiter);
app.use("/api/auth", authRoutes);
app.use("/api/companies", companyRoutes);
app.use(notFound);
app.use(errorHandler);
export default app;
