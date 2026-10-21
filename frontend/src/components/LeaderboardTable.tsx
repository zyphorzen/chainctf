"use client";

import { Trophy, Medal, Award, User, RefreshCw } from "lucide-react";

export interface LeaderboardPlayer {
  rank: number;
  wallet_address: string;
  username: string | null;
  score: number;
  solved_count: number;
}

interface LeaderboardTableProps {
  entries: LeaderboardPlayer[];
  isLoading: boolean;
  onRefresh: () => void;
}

export function LeaderboardTable({
  entries,
  isLoading,
  onRefresh,
}: LeaderboardTableProps) {
  const formatAddress = (addr: string) => {
    if (!addr) return "";
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`;
  };

  const getRankBadge = (rank: number) => {
    if (rank === 1) {
      return (
        <span className="flex items-center gap-1 font-bold text-amber-400">
          <Trophy className="h-4 w-4" /> #1
        </span>
      );
    }
    if (rank === 2) {
      return (
        <span className="flex items-center gap-1 font-bold text-slate-300">
          <Medal className="h-4 w-4" /> #2
        </span>
      );
    }
    if (rank === 3) {
      return (
        <span className="flex items-center gap-1 font-bold text-amber-600">
          <Award className="h-4 w-4" /> #3
        </span>
      );
    }
    return <span className="font-mono text-slate-400">#{rank}</span>;
  };

  return (
    <div className="rounded-xl border border-slate-800 bg-[#0d131f]/90 p-6 backdrop-blur-md">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-wide text-white">
            Global Leaderboard
          </h2>
          <p className="mt-1 text-xs text-slate-400">
            Real-time rankings synced from smart contract events
          </p>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-1.5 text-xs font-semibold text-slate-300 hover:border-slate-600 hover:text-white transition-all disabled:opacity-50"
        >
          <RefreshCw
            className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`}
          />
          <span>Refresh</span>
        </button>
      </div>

      {entries.length === 0 && !isLoading ? (
        <div className="py-12 text-center">
          <Trophy className="mx-auto h-10 w-10 text-slate-600" />
          <p className="mt-3 text-sm text-slate-400">No solves recorded yet.</p>
          <p className="text-xs text-slate-500">
            Be the first to claim a challenge on-chain!
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-800 text-xs font-mono text-slate-400">
                <th className="pb-3 pl-3">RANK</th>
                <th className="pb-3">PLAYER</th>
                <th className="pb-3 text-center">SOLVED</th>
                <th className="pb-3 pr-3 text-right">TOTAL SCORE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {entries.map((entry) => (
                <tr
                  key={entry.wallet_address}
                  className="hover:bg-slate-800/20 transition-colors"
                >
                  <td className="py-3.5 pl-3">{getRankBadge(entry.rank)}</td>
                  <td className="py-3.5">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-800 border border-slate-700">
                        <User className="h-3.5 w-3.5 text-slate-400" />
                      </div>
                      <div>
                        <div className="font-medium text-slate-200">
                          {entry.username ||
                            formatAddress(entry.wallet_address)}
                        </div>
                        {entry.username && (
                          <div className="font-mono text-xs text-slate-500">
                            {formatAddress(entry.wallet_address)}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 text-center font-mono text-slate-300">
                    {entry.solved_count}
                  </td>
                  <td className="py-3.5 pr-3 text-right font-mono font-bold text-emerald-400">
                    {entry.score} PTS
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
