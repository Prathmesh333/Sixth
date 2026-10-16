let csrfToken = '';
export function setCsrf(token: string) { csrfToken = token; }

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const response = await fetch(path, {
    method, credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      ...(method === 'GET' ? {} : { 'X-CSRF-Token': csrfToken, 'Idempotency-Key': crypto.randomUUID() }),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({})) as { message?: string; detail?: unknown };
    throw new ApiError(response.status, error.message || (typeof error.detail === 'string' ? error.detail : `Request failed (${response.status})`));
  }
  return response.json() as Promise<T>;
}
