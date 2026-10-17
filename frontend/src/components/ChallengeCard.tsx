"use client";

import { useState } from "react";
import { useWriteContract, useWaitForTransactionReceipt } from "wagmi";
import { CONTRACT_ADDRESS, CONTRACT_ABI } from "@/lib/contract";
import { submitFlag } from "@/lib/api";
import { Shield, Flag, CheckCircle2, Loader2, AlertCircle } from "lucide-react";

export interface ChallengeItem {
  id: number;
  title: string;
  description: string;
  category: string;
  reward: number;
  is_solved?: boolean;
}

interface ChallengeCardProps {
  challenge: ChallengeItem;
  token: string | null;
  onSuccess?: () => void;
}

export function ChallengeCard({ challenge, token, onSuccess }: ChallengeCardProps) {
  const [flagInput, setFlagInput] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [authPayload, setAuthPayload] = useState<any | null>(null);

  const { data: txHash, writeContractAsync, isPending: isTxPending } = useWriteContract();

  const { isLoading: isTxConfirming, isSuccess: isTxSuccess } = useWaitForTransactionReceipt({
    hash: txHash,
  });

  const handleFlagSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setErrorMessage("Please connect your wallet and sign in first.");
      return;
    }

    setErrorMessage(null);
    setIsVerifying(true);

    try {
      const response = await submitFlag(challenge.id, flagInput.trim(), token);
      setAuthPayload(response);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to verify flag");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleClaimOnChain = async () => {
    if (!authPayload) return;

    setErrorMessage(null);
    try {
      await writeContractAsync({
        address: CONTRACT_ADDRESS,
        abi: CONTRACT_ABI,
        functionName: "submitAchievement",
        args: [
          {
            player: authPayload.achievement.player as `0x${string}`,
            challengeId: BigInt(authPayload.achievement.challengeId),
            nonce: BigInt(authPayload.achievement.nonce),
            deadline: BigInt(authPayload.achievement.deadline),
          },
          authPayload.signature as `0x${string}`,
        ],
      });
      if (onSuccess) onSuccess();
    } catch (err: any) {
      setErrorMessage(err.message || "On-chain claim transaction failed");
    }
  };

  const isCompleted = challenge.is_solved || isTxSuccess;

  return (
    <div
      className={`rounded-xl border p-6 transition-all duration-300 ${
        isCompleted
          ? "border-emerald-500/40 bg-emerald-950/10 shadow-[0_0_20px_rgba(16,185,129,0.1)]"
          : "border-slate-800 bg-[#0d131f]/90 hover:border-slate-700"
      }`}
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded bg-emerald-500/10 px-2 py-0.5 text-xs font-mono font-medium text-emerald-400 border border-emerald-500/20">
              {challenge.category.toUpperCase()}
            </span>
            <span className="text-xs font-mono text-slate-400">ID #{challenge.id}</span>
          </div>
          <h3 className="mt-2 text-xl font-bold text-white tracking-wide">{challenge.title}</h3>
        </div>

        <div className="flex flex-col items-end">
          <div className="flex items-center gap-1 font-mono text-base font-bold text-emerald-400">
            <Shield className="h-4 w-4" />
            <span>+{challenge.reward} PTS</span>
          </div>
          {isCompleted && (
            <span className="mt-1 flex items-center gap-1 text-xs font-semibold text-emerald-400">
              <CheckCircle2 className="h-3.5 w-3.5" /> Solved
            </span>
          )}
        </div>
      </div>

      <p className="mt-4 text-sm leading-relaxed text-slate-300">{challenge.description}</p>

      {errorMessage && (
        <div className="mt-4 flex items-center gap-2 rounded-lg border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {isCompleted ? (
        <div className="mt-6 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-center text-xs font-mono text-emerald-300">
          Challenge verified and claimed on-chain!
        </div>
      ) : authPayload ? (
        <div className="mt-6 space-y-3">
          <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/10 p-3 text-xs text-cyan-200">
            Flag correct! EIP-712 cryptographic signature received from backend.
          </div>
          <button
            onClick={handleClaimOnChain}
            disabled={isTxPending || isTxConfirming}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 px-4 py-2.5 text-sm font-semibold text-black transition-all disabled:opacity-50"
          >
            {isTxPending || isTxConfirming ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Confirming on-chain...</span>
              </>
            ) : (
              <>
                <Shield className="h-4 w-4" />
                <span>Submit Achievement to Smart Contract</span>
              </>
            )}
          </button>
        </div>
      ) : (
        <form onSubmit={handleFlagSubmit} className="mt-6 space-y-3">
          <div className="relative">
            <input
              type="text"
              placeholder="CTF{flag_goes_here}"
              value={flagInput}
              onChange={(e) => setFlagInput(e.target.value)}
              disabled={isVerifying || !token}
              className="w-full rounded-lg border border-slate-700 bg-slate-950/70 px-4 py-2.5 pr-10 text-sm font-mono text-slate-100 placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:opacity-50"
            />
            <Flag className="absolute right-3 top-3 h-4 w-4 text-slate-500" />
          </div>

          <button
            type="submit"
            disabled={isVerifying || !flagInput.trim() || !token}
            className="w-full flex items-center justify-center gap-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 px-4 py-2.5 text-sm font-semibold text-black transition-all disabled:opacity-50"
          >
            {isVerifying ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Verifying flag...</span>
              </>
            ) : (
              <span>Verify Flag</span>
            )}
          </button>
        </form>
      )}
    </div>
  );
}
