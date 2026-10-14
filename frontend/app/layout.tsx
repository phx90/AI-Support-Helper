import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/app-shell";
const inter = Inter({ subsets: ["latin"] });
export const metadata: Metadata = {
  title: "AI Support Hub",
  description: "Intelligent RAG Helpdesk & AI Automation Platform",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
