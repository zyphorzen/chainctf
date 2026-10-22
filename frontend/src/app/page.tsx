"use client";

import { useEffect, useState, useCallback } from "react";
import { useAccount, useSignMessage } from "wagmi";
import { Navbar } from "@/components/Navbar";
import { ChallengeCard, ChallengeItem } from "@/components/ChallengeCard";
import {
  LeaderboardTable,
  LeaderboardPlayer,
} from "@/components/LeaderboardTable";
import { ProfileView } from "@/components/ProfileView";
import {
  requestNonce,
  verifySignature,
  getChallenges,
  getLeaderboard,
} from "@/lib/api";
import {
  Shield,
  Trophy,
  User,
  Terminal,
  Loader2,
  Sparkles,
  Filter,
} from "lucide-react";

export default function Home() {
  const { address, isConnected } = useAccount();
  const { signMessageAsync } = useSignMessage();

  const [activeTab, setActiveTab] = useState<
    "challenges" | "leaderboard" | "profile"
  >("challenges");
  const [token, setToken] = useState<string | null>(null);
  const [challenges, setChallenges] = useState<ChallengeItem[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardPlayer[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSigningIn, setIsSigningIn] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("chainctf_token");
    if (saved) setToken(saved);
  }, []);

  useEffect(() => {
    if (!isConnected) {
      setToken(null);
      localStorage.removeItem("chainctf_token");
    }
  }, [isConnected]);

  const handleLogin = async () => {
    if (!address) return;
    setIsSigningIn(true);
    setAuthError(null);

    try {
      const nonceData = await requestNonce(address);
      const signature = await signMessageAsync({ message: nonceData.message });
      const authResult = await verifySignature(address, signature);

      setToken(authResult.access_token);
      localStorage.setItem("chainctf_token", authResult.access_token);
    } catch (err: any) {
      setAuthError(err.message || "Failed to sign in with wallet");
    } finally {
      setIsSigningIn(false);
    }
  };

  const loadChallenges = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getChallenges(token);
      setChallenges(data);
    } catch {
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const loadLeaderboard = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getLeaderboard();
      setLeaderboard(data);
    } catch {
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (activeTab === "challenges") loadChallenges();
    if (activeTab === "leaderboard") loadLeaderboard();
  }, [activeTab, loadChallenges, loadLeaderboard]);

  const categories = [
    "ALL",
    ...Array.from(new Set(challenges.map((c) => c.category.toUpperCase()))),
  ];

  const filteredChallenges =
    selectedCategory === "ALL"
      ? challenges
      : challenges.filter((c) => c.category.toUpperCase() === selectedCategory);

  return (
    <div className="min-h-screen bg-[#070a11] text-slate-100 flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        token={token}
        onLogin={handleLogin}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-8">
        {authError && (
          <div className="mb-6 rounded-lg border border-rose-500/30 bg-rose-500/10 p-4 text-xs font-mono text-rose-300">
            {authError}
          </div>
        )}

        {isConnected && !token && (
          <div className="mb-8 rounded-xl border border-yellow-500/30 bg-yellow-500/5 p-6 backdrop-blur-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 text-yellow-400 font-bold">
                <Terminal className="h-5 w-5" />
                <h3>Authentication Required</h3>
              </div>
              <p className="mt-1 text-xs text-slate-300">
                Wallet connected. Sign a cryptographic message to verify
                ownership and unlock flag submission.
              </p>
            </div>
            <button
              onClick={handleLogin}
              disabled={isSigningIn}
              className="flex items-center gap-2 rounded-lg bg-yellow-500 hover:bg-yellow-400 px-4 py-2 text-xs font-bold text-black transition-all disabled:opacity-50"
            >
              {isSigningIn ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="h-4 w-4" />
              )}
              <span>Sign In with Wallet</span>
            </button>
          </div>
        )}

        {activeTab === "challenges" && (
          <div>
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  <Shield className="h-6 w-6 text-emerald-400" />
                  Security Challenges
                </h1>
                <p className="mt-1 text-xs text-slate-400 font-mono">
                  Solve off-chain challenges, receive EIP-712 typed signatures,
                  and submit achievements on-chain.
                </p>
              </div>

              {categories.length > 1 && (
                <div className="flex items-center gap-1.5 overflow-x-auto pb-2 md:pb-0">
                  <Filter className="h-3.5 w-3.5 text-slate-500 shrink-0 ml-1 mr-1" />
                  {categories.map((cat) => (
                    <button
                      key={cat}
                      onClick={() => setSelectedCategory(cat)}
                      className={`px-3 py-1 rounded-lg text-xs font-mono font-semibold transition ${
                        selectedCategory === cat
                          ? "bg-emerald-500 text-black shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                          : "bg-slate-900/80 border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
                      }`}
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {isLoading ? (
              <div className="py-20 flex flex-col items-center justify-center text-slate-500">
                <Loader2 className="h-8 w-8 animate-spin text-emerald-400" />
                <span className="mt-3 text-xs font-mono">
                  Loading challenges...
                </span>
              </div>
            ) : filteredChallenges.length === 0 ? (
              <div className="py-16 text-center rounded-xl border border-slate-800 bg-[#0d131f]/60 p-8">
                <Shield className="mx-auto h-10 w-10 text-slate-600" />
                <p className="mt-3 text-sm text-slate-400">
                  No challenges found.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredChallenges.map((challenge) => (
                  <ChallengeCard
                    key={challenge.id}
                    challenge={challenge}
                    token={token}
                    onSuccess={loadChallenges}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "leaderboard" && (
          <LeaderboardTable
            entries={leaderboard}
            isLoading={isLoading}
            onRefresh={loadLeaderboard}
          />
        )}

        {activeTab === "profile" && (
          <ProfileView token={token} walletAddress={address} />
        )}
      </main>
    </div>
  );
}
