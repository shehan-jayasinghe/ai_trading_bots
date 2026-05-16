import { auth } from "@/auth";
import { getToken } from "next-auth/jwt";
import { SignJWT } from "jose";
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const secret = process.env.AUTH_SECRET;
  if (!secret) {
    return NextResponse.json(
      { error: "Server auth is not configured" },
      { status: 500 },
    );
  }

  const decoded = await getToken({ req: request, secret });
  if (!decoded?.sub) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const key = new TextEncoder().encode(secret);
  const token = await new SignJWT({
    sub: String(decoded.sub),
    email: decoded.email ?? undefined,
    name: decoded.name ?? undefined,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("30d")
    .sign(key);

  return NextResponse.json({
    token,
    user: {
      id: session.user.id,
      email: session.user.email,
      name: session.user.name,
    },
  });
}
