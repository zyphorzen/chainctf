const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function requestNonce(walletAddress: string) {
  const res = await fetch(`${API_BASE}/auth/nonce`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wallet_address: walletAddress }),
  });
  if (!res.ok) throw new Error("Failed to request login nonce");
  return res.json();
}

export async function verifySignature(
  walletAddress: string,
  signature: string,
) {
  const res = await fetch(`${API_BASE}/auth/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wallet_address: walletAddress, signature }),
  });
  if (!res.ok) throw new Error("Wallet signature verification failed");
  return res.json();
}

export async function getChallenges(token?: string | null) {
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/challenges`, { headers });
  if (!res.ok) throw new Error("Failed to fetch challenges");
  return res.json();
}

export async function submitFlag(
  challengeId: number,
  flag: string,
  token: string,
) {
  const res = await fetch(`${API_BASE}/challenges/${challengeId}/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ challenge_id: challengeId, flag }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Flag submission failed");
  return data;
}

export async function getLeaderboard() {
  const res = await fetch(`${API_BASE}/leaderboard`);
  if (!res.ok) throw new Error("Failed to fetch leaderboard");
  return res.json();
}

export async function getMyProfile(token: string) {
  const res = await fetch(`${API_BASE}/player/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch profile");
  return res.json();
}

export async function getMyAuthorizations(token: string) {
  const res = await fetch(`${API_BASE}/player/me/authorizations`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to fetch pending authorizations");
  return res.json();
}
