/** Field-level validation errors returned by APIs */
export type FieldErrors = Record<string, string>;

/** Standard error JSON for Route Handlers */
export type ApiErrorResponse = {
  ok: false;
  error: string;
  fieldErrors: FieldErrors;
  detail?: string;
};

/** Standard success JSON for mutating routes */
export type ApiSuccessResponse = {
  ok: true;
  message: string;
};

/** User-facing strings — single source of truth */
export const API_MESSAGES = {
  INVALID_JSON: "Invalid JSON body.",
  VALIDATION_FAILED: "Validation failed.",
  EMAIL_IN_USE: "Email already registered.",
  EMAIL_IN_USE_FIELD: "An account with this email already exists.",
  DB_UNAVAILABLE: "Database temporarily unavailable. Please try again later.",
  PASSWORD_HASH_FAILED: "Could not process password. Please try again.",
  REGISTRATION_FAILED: "Registration failed. Please try again later.",
  USER_CREATED: "Account created successfully.",
} as const;
