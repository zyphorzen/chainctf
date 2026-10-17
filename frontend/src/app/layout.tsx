import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "ChainCTF — Blockchain Cybersecurity Challenges",
  description: "Capture The Flag platform with on-chain EIP-712 achievement verification",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#080c14] text-gray-100 antialiased">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
