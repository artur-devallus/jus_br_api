type JwtPayload = {
  jti: number;
  exp: number;
}

function getTokenFromLocalStorage(tokenKey: string): string | null {
  const token = localStorage.getItem(tokenKey);
  if (!token) return null;
  return token;
}

export function getTokenPayload(tokenKey: string): JwtPayload | null {
  const token = getTokenFromLocalStorage(tokenKey);
  if (!token) return null;
  try {
    const [, payload] = token.split(".");
    // console.log(JSON.parse(atob(payload)));
    return JSON.parse(atob(payload));
  } catch (error) {
    console.error(error);
    localStorage.removeItem(tokenKey);
    return null;
  }
}

export function getValidTokenFromStorage(tokenKey: string): string | null {
  const token = getTokenFromLocalStorage(tokenKey);
  const payload = getTokenPayload(tokenKey);
  if (!token || !payload) return null;
  try {
    const currentTime = Math.floor(Date.now() / 1000);
    if (payload.exp && payload.exp < currentTime) {
      localStorage.removeItem(tokenKey);
      return null;
    }
    return token;
  } catch (error) {
    console.error(error);
    localStorage.removeItem(tokenKey);
    return null;
  }
}