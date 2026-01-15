import { exec } from "node:child_process";
import util from "node:util";

const execAsync = util.promisify(exec);

async function globalSetup() {
  console.log("Seeding database...");
  try {
    // Assuming we are running from frontend directory, so backend is ../backend
    // Use uv run for better environment management
    await execAsync(
      'cd ../backend && DATABASE_URL="postgresql+asyncpg://app:app_password@localhost:5433/app_db" uv run scripts/seed_e2e.py',
    );
    console.log("Database seeded.");
  } catch (error) {
    console.error("Error seeding database:", error);
    throw error;
  }
}

export default globalSetup;
