// Client-side helper to read the auth token cookie set by auth-context.
// Kept separate so server-agnostic client islands (Save button, admin page)
// can authenticate their own fetches without pulling in the whole context.
const TOKEN_COOKIE = "faircare_auth_token";

export function getAuthToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`${TOKEN_COOKIE}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : null;
}
