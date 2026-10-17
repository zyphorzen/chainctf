export const CONTRACT_ADDRESS = (process.env.NEXT_PUBLIC_CONTRACT_ADDRESS ||
  "0x5FbDB2315678afecb367f032d93F642f64180aa3") as `0x${string}`;

export const CONTRACT_ABI = [
  {
    type: "function",
    name: "submitAchievement",
    inputs: [
      {
        name: "achievement",
        type: "tuple",
        internalType: "struct CTFPlatform.Achievement",
        components: [
          { name: "player", type: "address", internalType: "address" },
          { name: "challengeId", type: "uint256", internalType: "uint256" },
          { name: "nonce", type: "uint256", internalType: "uint256" },
          { name: "deadline", type: "uint256", internalType: "uint256" },
        ],
      },
      { name: "signature", type: "bytes", internalType: "bytes" },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "scores",
    inputs: [{ name: "player", type: "address", internalType: "address" }],
    outputs: [{ name: "", type: "uint256", internalType: "uint256" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "solved",
    inputs: [
      { name: "player", type: "address", internalType: "address" },
      { name: "challengeId", type: "uint256", internalType: "uint256" },
    ],
    outputs: [{ name: "", type: "bool", internalType: "bool" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "challengeCount",
    inputs: [],
    outputs: [{ name: "", type: "uint256", internalType: "uint256" }],
    stateMutability: "view",
  },
] as const;
