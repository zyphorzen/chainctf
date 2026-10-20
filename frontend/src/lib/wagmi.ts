import { http, createConfig } from "wagmi";
import { sepolia } from "wagmi/chains";
import { injected } from "wagmi/connectors";

export const anvilChain = {
  id: 31337,
  name: "Anvil Local",
  nativeCurrency: { name: "Ether", symbol: "ETH", decimals: 18 },
  rpcUrls: {
    default: { http: ["http://localhost:8545"] },
  },
} as const;

export const config = createConfig({
  chains: [anvilChain, sepolia],
  connectors: [injected()],
  transports: {
    [anvilChain.id]: http("http://localhost:8545"),
    [sepolia.id]: http("https://rpc.sepolia.org"),
  },
});
