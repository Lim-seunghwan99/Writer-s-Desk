import { NextResponse } from 'next/server';
import pool from '@/lib/db';
import bcrypt from 'bcrypt';

export async function POST(req: Request) {
  const { user_id, password } = await req.json();

  try {
    const existing = await pool.query('SELECT * FROM users WHERE user_id = $1', [user_id]);
    if (existing.rows.length > 0) {
      return NextResponse.json({ error: 'User already exists' }, { status: 400 });
    }

    const hashedPassword = await bcrypt.hash(password, 10);

    const result = await pool.query(
      'INSERT INTO users (user_id, password) VALUES ($1, $2) RETURNING user_id',
      [user_id, hashedPassword]
    );

    return NextResponse.json({ success: true, user_id: result.rows[0].user_id });
  } catch (err) {
    console.error(err);
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}
