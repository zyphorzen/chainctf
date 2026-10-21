"use client";

import { useEffect, useState } from "react";
import { useWriteContract, useWaitForTransactionReceipt } from "wagmi";
import { getMyProfile, getMyAuthorizations } from "@/lib/api";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "@/lib/contract";
import {
  User,
  Shield,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Award,
  Copy,
  Check,
} from "lucide-react";

interface ProfileViewProps {
  token: string | null;
  walletAddress: string | undefined;
}

export function ProfileView({ token, walletAddress }: ProfileViewProps) {
  const [profile, setProfile] = useState<any | null>(null);
  const [pendingAuths, setPendingAuths] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [activeClaimId, setActiveClaimId] = useState<number | null>(null);
  const [claimError, setClaimError] = useState<string | null>(null);

  const {
    data: txHash,
    writeContractAsync,
    isPending: isTxPending,
  } = useWriteContract();

  const { isLoading: isTxConfirming, isSuccess: isTxSuccess } =
    useWaitForTransactionReceipt({
      hash: txHash,
    });

  const fetchData = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const [profileData, authsData] = await Promise.all([
        getMyProfile(token),
        getMyAuthorizations(token),
      ]);
      setProfile(profileData);
      setPendingAuths(authsData);
    } catch {
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token, isTxSuccess]);

  const handleCopy = () => {
    if (!walletAddress) return;
    navigator.clipboard.writeText(walletAddress);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleClaim = async (auth: any) => {
    setClaimError(null);
    setActiveClaimId(auth.achievement.challengeId);

    try {
      await writeContractAsync({
        address: CONTRACT_ADDRESS,
        abi: CONTRACT_ABI,
        functionName: "submitAchievement",
        args: [
          {
            player: auth.achievement.player as `0x${string}`,
            challengeId: BigInt(auth.achievement.challengeId),
            nonce: BigInt(auth.achievement.nonce),
            deadline: BigInt(auth.achievement.deadline),
          },
          auth.signature as `0x${string}`,
        ],
      });
    } catch (err: any) {
      setClaimError(err.message || "Claim transaction failed");
    } finally {
      setActiveClaimId(null);
    }
  };

  if (!token || !walletAddress) {
    return (
      <div className="rounded-xl border border-slate-800 bg-[#0d131f]/90 p-8 text-center backdrop-blur-md">
        <User className="mx-auto h-12 w-12 text-slate-600" />
        <h3 className="mt-3 text-lg font-bold text-white">
          Wallet Not Connected
        </h3>
        <p className="mt-1 text-sm text-slate-400">
          Please connect your Web3 wallet and authenticate to view your hacker
          profile.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-800 bg-[#0d131f]/90 p-6 backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <User className="h-7 w-7" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">
                {profile?.username || "Anonymous Hacker"}
              </h2>
              <div className="mt-1 flex items-center gap-2">
                <span className="font-mono text-xs text-slate-400">
                  {walletAddress}
                </span>
                <button
                  onClick={handleCopy}
                  className="text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {copied ? (
                    <Check className="h-3.5 w-3.5 text-emerald-400" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                </button>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-2.5 text-center">
              <div className="text-xs font-mono text-slate-400">SCORE</div>
              <div className="mt-0.5 font-mono text-lg font-bold text-emerald-400">
                {profile?.score ?? 0} PTS
              </div>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-2.5 text-center">
              <div className="text-xs font-mono text-slate-400">SOLVED</div>
              <div className="mt-0.5 font-mono text-lg font-bold text-cyan-400">
                {profile?.solved_count ?? 0}
              </div>
            </div>
          </div>
        </div>
      </div>

      {pendingAuths.length > 0 && (
        <div className="rounded-xl border border-amber-500/30 bg-amber-500/5 p-6 backdrop-blur-md">
          <div className="flex items-center gap-2 text-amber-400">
            <AlertTriangle className="h-5 w-5" />
            <h3 className="font-bold">Pending On-Chain Authorizations</h3>
          </div>
          <p className="mt-1 text-xs text-slate-300">
            You solved these challenges off-chain! Submit the cryptographic
            signatures to the smart contract to register points on the
            leaderboard.
          </p>

          {claimError && (
            <div className="mt-3 rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
              {claimError}
            </div>
          )}

          <div className="mt-4 space-y-3">
            {pendingAuths.map((auth) => (
              <div
                key={auth.achievement.challengeId}
                className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-950/70 p-4"
              >
                <div>
                  <div className="font-mono text-sm font-semibold text-slate-200">
                    Challenge #{auth.achievement.challengeId}
                  </div>
                  <div className="mt-0.5 font-mono text-xs text-slate-500">
                    Nonce: {auth.achievement.nonce} | Deadline:{" "}
                    {auth.achievement.deadline}
                  </div>
                </div>

                <button
                  onClick={() => handleClaim(auth)}
                  disabled={isTxPending || isTxConfirming}
                  className="flex items-center gap-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 px-3.5 py-1.5 text-xs font-semibold text-black transition-all disabled:opacity-50"
                >
                  {(isTxPending || isTxConfirming) &&
                  activeClaimId === auth.achievement.challengeId ? (
                    <>
                      <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      <span>Submitting...</span>
                    </>
                  ) : (
                    <>
                      <Shield className="h-3.5 w-3.5" />
                      <span>Claim On-Chain</span>
                    </>
                  )}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
