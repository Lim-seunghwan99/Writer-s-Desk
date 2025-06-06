import { NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';

const secret = process.env.JWT_SECRET!;

function generateGuestId() {
  return 'guest_' + Math.random().toString(36).substring(2, 10);
}

export async function POST() {
  const guestId = generateGuestId();

  const token = jwt.sign(
    { user_id: guestId, guest: true },
    secret,
    { expiresIn: '1h' }
  );

  return NextResponse.json({ token, user_id: guestId });
}
