import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Roscoe Legal Workbench",
  description: "AI-powered legal workspace for case management and document drafting",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
