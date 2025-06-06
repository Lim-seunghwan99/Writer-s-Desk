import { NextResponse } from 'next/server';
import pool from '@/lib/db';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';

const secret = process.env.JWT_SECRET!;

export async function POST(req: Request) {
  const { user_id, password } = await req.json();

  const result = await pool.query('SELECT * FROM users WHERE user_id = $1', [user_id]);
  const user = result.rows[0];

  if (!user) {
    return NextResponse.json({ error: 'User not found' }, { status: 404 });
  }

  const isValid = await bcrypt.compare(password, user.password);

  if (!isValid) {
    return NextResponse.json({ error: 'Invalid credentials' }, { status: 401 });
  }

  const token = jwt.sign({ user_id: user.user_id }, secret, { expiresIn: '1h' });

  return NextResponse.json({ token });
}
