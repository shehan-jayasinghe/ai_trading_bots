import bcrypt from "bcryptjs";
import { apiError, apiSuccess } from "@/lib/api-response";
import { prisma } from "@/lib/prisma";
import { signupBodySchema, zodIssuesToFieldErrors } from "@/lib/validation";
import { API_MESSAGES } from "@/types";

function isPrismaError(e: unknown): e is { code: string; message?: string } {
  return (
    typeof e === "object" &&
    e !== null &&
    "code" in e &&
    typeof (e as { code: unknown }).code === "string"
  );
}

export async function POST(request: Request) {
  let parsedJson = false;
  let insideBcryptHash = false;

  try {
    const rawBody = await request.json();
    parsedJson = true;

    const parsed = signupBodySchema.safeParse(rawBody);
    if (!parsed.success) {
      return apiError(
        API_MESSAGES.VALIDATION_FAILED,
        zodIssuesToFieldErrors(parsed.error),
        400
      );
    }

    const { email, password } = parsed.data;

    const existing = await prisma.user.findUnique({
      where: { email },
    });

    if (existing) {
      return apiError(
        API_MESSAGES.EMAIL_IN_USE,
        { email: API_MESSAGES.EMAIL_IN_USE_FIELD },
        409
      );
    }

    insideBcryptHash = true;
    const passwordHash = await bcrypt.hash(password, 10);
    insideBcryptHash = false;

    await prisma.user.create({
      data: { email, passwordHash },
    });

    return apiSuccess(API_MESSAGES.USER_CREATED, 201);
  } catch (err) {
    if (!parsedJson) {
      return apiError(API_MESSAGES.INVALID_JSON, {}, 400);
    }

    if (insideBcryptHash) {
      console.error("[signup] bcrypt", err);
      return apiError(
        API_MESSAGES.PASSWORD_HASH_FAILED,
        {},
        500,
        err instanceof Error ? err.message : String(err)
      );
    }

    if (isPrismaError(err) && err.code === "P2002") {
      return apiError(
        API_MESSAGES.EMAIL_IN_USE,
        { email: API_MESSAGES.EMAIL_IN_USE_FIELD },
        409
      );
    }

    if (isPrismaError(err) && err.code.startsWith("P100")) {
      console.error("[signup] database unavailable", err);
      return apiError(API_MESSAGES.DB_UNAVAILABLE, {}, 503, err.message);
    }

    console.error("[signup]", err);
    return apiError(
      API_MESSAGES.REGISTRATION_FAILED,
      {},
      500,
      err instanceof Error ? err.message : String(err)
    );
  }
}
