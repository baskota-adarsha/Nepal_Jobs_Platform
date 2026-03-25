import { testConnection } from "./config/db";
import { env } from "./config/env";

const PORT = parseInt(env.PORT, 10);
const start = async () => {
  try {
    await testConnection();
    app.listen(PORT, () => {
      console.log(`\n Nepal Jobs API running on http://localhost:${PORT}`);
      console.log(` Swagger docs:  http://localhost:${PORT}/api/docs`);
      console.log(` Health check:  http://localhost:${PORT}/health`);
      console.log(` Environment:   ${env.NODE_ENV}\n`);
    });
  } catch (error) {
    console.error("Failed to start server:", err);
    process.exit(1);
  }
};
