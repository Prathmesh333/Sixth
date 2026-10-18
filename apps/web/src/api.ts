let csrfToken = '';
export function setCsrf(token: string) { csrfToken = token; }

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function api<T>(path: string, method = 'GET', body?: unknown): Promise<T> {
  const options: RequestInit = {
    method, credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      ...(method === 'GET' ? {} : { 'X-CSRF-Token': csrfToken, 'Idempotency-Key': crypto.randomUUID() }),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  };
  let response: Response | undefined;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      response = await fetch(path, options);
      if (![502, 503, 504].includes(response.status) || attempt === 1) break;
    } catch (error) {
      if (attempt === 1) throw new Error('The server could not be reached. Please check your connection and retry.');
    }
    // Reuse the same idempotency key after an upstream interruption.
    await new Promise(resolve => setTimeout(resolve, 800));
  }
  if (!response) throw new Error('The server could not be reached. Please try again.');
  if (!response.ok) {
    const error = await response.json().catch(() => ({})) as { message?: string; detail?: unknown };
    throw new ApiError(response.status, error.message || (typeof error.detail === 'string' ? error.detail : response.status >= 500 ? 'The server is temporarily unavailable. Please try again shortly.' : `Request failed (${response.status})`));
  }
  return response.json() as Promise<T>;
}
