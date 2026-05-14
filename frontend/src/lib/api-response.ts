import { NextResponse } from "next/server";
import type { ApiErrorResponse, ApiSuccessResponse, FieldErrors } from "@/types/api";
import { API_MESSAGES } from "@/types/api";

function stripDetail(body: ApiErrorResponse): ApiErrorResponse {
  if (process.env.NODE_ENV === "development") return body;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars -- omit `detail` in production
  const { detail, ...rest } = body;
  return rest;
}

export function apiError(
  error: string,
  fieldErrors: FieldErrors,
  status: number,
  detail?: string
): NextResponse<ApiErrorResponse> {
  const body: ApiErrorResponse = {
    ok: false,
    error,
    fieldErrors,
    ...(detail !== undefined ? { detail } : {}),
  };
  return NextResponse.json(stripDetail(body), { status });
}

export function apiSuccess(
  message: string = API_MESSAGES.USER_CREATED,
  status: number = 200
): NextResponse<ApiSuccessResponse> {
  return NextResponse.json({ ok: true, message }, { status });
}
