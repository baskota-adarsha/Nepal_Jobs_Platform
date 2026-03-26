import { queryOne } from "../config/db";

export class JobRepository {
  async findAll() {
    const countResult = await queryOne<{ count: string }>(
      "SELECT COUNT(*) as count FROM jobs ",
    );
    const total = parseInt(countResult?.count ?? "0", 10);
  }
}
