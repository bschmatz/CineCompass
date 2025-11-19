const SESSION_KEY = 'cinecompass_session_id';

export const getSessionId = (): string => {
  let sessionId = localStorage.getItem(SESSION_KEY);

  if (!sessionId) {
    // Generate a new UUID for the session
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sessionId);
  }

  return sessionId;
};

export const clearSession = (): void => {
  localStorage.removeItem(SESSION_KEY);
};
