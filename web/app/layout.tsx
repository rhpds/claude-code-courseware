import type { Metadata } from "next";
import "./globals.css";
import { AppShell } from "@/components/AppShell";
import { getAllModules } from "@/lib/modules";

export const metadata: Metadata = {
  title: {
    default: "Claude Code Courseware",
    template: "%s · Claude Code Courseware",
  },
  description:
    "Hands-on learning modules for the RHDP operations team, delivered as Claude Code skills.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const modules = getAllModules().map((m) => ({
    slug: m.slug,
    num: m.num,
    title: m.title,
    category: m.category,
    categoryColor: m.categoryColor,
    difficulty: m.difficulty,
    isNew: m.isNew,
  }));

  return (
    <html lang="en">
      <body>
        <AppShell modules={modules}>{children}</AppShell>
      </body>
    </html>
  );
}
