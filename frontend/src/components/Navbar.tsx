"use client";

import { useAccount, useConnect, useDisconnect } from "wagmi";
import { Shield, Wallet, LogOut, Terminal } from "lucide-react";

interface NavbarProps {
  activeTab: "challenges" | "leaderboard" | "profile";
  setActiveTab: (tab: "challenges" | "leaderboard" | "profile") => void;
  token: string | null;
  onLogin: () => void;
}

export function Navbar({ activeTab, setActiveTab, token, onLogin }: NavbarProps) {
  const { address, isConnected } = useAccount();
  const { connect, connectors } = useConnect();
  const { disconnect } = useDisconnect();

  return (
    <header className="border-b border-gray-800 bg-[#0d131f]/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-2 cursor-pointer" onClick={() => setActiveTab("challenges")}>
            <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Shield className="w-5 h-5" />
            </div>
            <span className="font-bold text-lg tracking-wider text-white">
              Chain<span className="text-emerald-400">CTF</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center gap-1">
            <button
              onClick={() => setActiveTab("challenges")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
                activeTab === "challenges" ? "bg-gray-800 text-emerald-400" : "text-gray-400 hover:text-white"
              }`}
            >
              Challenges
            </button>
            <button
              onClick={() => setActiveTab("leaderboard")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
                activeTab === "leaderboard" ? "bg-gray-800 text-emerald-400" : "text-gray-400 hover:text-white"
              }`}
            >
              Leaderboard
            </button>
            <button
              onClick={() => setActiveTab("profile")}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition ${
                activeTab === "profile" ? "bg-gray-800 text-emerald-400" : "text-gray-400 hover:text-white"
              }`}
            >
              Profile
            </button>
          </nav>
        </div>

        <div className="flex items-center gap-3">
          {!isConnected ? (
            <button
              onClick={() => connect({ connector: connectors[0] })}
              className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
            >
              <Wallet className="w-4 h-4" />
              Connect Wallet
            </button>
          ) : (
            <div className="flex items-center gap-2">
              {!token && (
                <button
                  onClick={onLogin}
                  className="flex items-center gap-1.5 bg-yellow-500/10 border border-yellow-500/30 hover:bg-yellow-500/20 text-yellow-400 px-3 py-1.5 rounded-lg text-xs font-medium transition"
                >
                  <Terminal className="w-3.5 h-3.5" />
                  Sign In
                </button>
              )}
              <div className="px-3 py-1.5 rounded-lg bg-gray-900 border border-gray-800 text-xs text-gray-300 font-mono">
                {address?.slice(0, 6)}...{address?.slice(-4)}
              </div>
              <button
                onClick={() => disconnect()}
                className="p-2 rounded-lg bg-gray-900 border border-gray-800 hover:bg-gray-800 text-gray-400 hover:text-red-400 transition"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
