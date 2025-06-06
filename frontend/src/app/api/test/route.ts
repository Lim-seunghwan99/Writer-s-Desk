import { NextResponse } from 'next/server';
import pool from '@/lib/db';

export async function GET() {
  try {
    const res = await pool.query('SELECT NOW()');
    return NextResponse.json({ time: res.rows[0].now });
  } catch (err) {
    console.error('DB 연결 오류:', err);
    return NextResponse.json({ error: 'DB 연결 실패' }, { status: 500 });
  }
}
