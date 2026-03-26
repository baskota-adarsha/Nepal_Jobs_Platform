import { query, queryOne } from "../config/db";
import { User } from "../types";
export class UserRepository {
  async findByEmail(email: string): Promise<User | null> {
    return queryOne<User>("SELECT * FROM users WHERE email =$1", [email]);
  }
  async findById(id: string): Promise<User | null> {
    return queryOne<User>(`SELECT * FROM users WHERE id = $1`, [id]);
  }
  async create(
    email: string,
    passwordHash: string,
    name: string,
  ): Promise<User> {
    const rows = await query<User>(
      `INSERT INTO users (email, password_hash, name)
       VALUES ($1, $2, $3)
       RETURNING *`,
      [email, passwordHash, name],
    );
    return rows[0];
  }
  async emailExists(email: string): Promise<boolean> {
    const result = await queryOne<{ count: string }>(
      `SELECT COUNT(*)::text AS count FROM users WHERE email = $1`,
      [email],
    );
    return parseInt(result?.count ?? "0", 10) > 0;
  }
}
