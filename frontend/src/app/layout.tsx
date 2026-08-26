import type { Metadata } from "next";
import "./globals.css";
import { Sidebar, TopHeader } from "@/components/Navigation";

export const metadata: Metadata = {
  title: "RevivePay — Autonomous AI Revenue Recovery Platform",
  description: "Autonomous Revenue Recovery Platform detecting payment at risk, predicting recovery probability, and executing policy-guarded actions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-slate-900 antialiased">
        <div className="flex min-h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col min-w-0">
            <TopHeader />
            <main className="flex-1 p-8 overflow-y-auto">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
