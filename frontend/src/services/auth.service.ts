export type TokenResponse = {
  token: string;
  user: {
    id: string;
    email?: string | null;
    name?: string | null;
  };
};

export async function fetchAccessToken(): Promise<TokenResponse> {
  const res = await fetch("/api/auth/token");
  if (!res.ok) {
    throw new Error("Failed to get access token");
  }
  return res.json() as Promise<TokenResponse>;
}
