import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getAllModules, getModule } from "@/lib/modules";
import { ModuleBody } from "@/components/ModuleBody";
import { ModuleView } from "@/components/ModuleView";

// All module pages are known at build time; reject unknown slugs with a 404
// instead of attempting a runtime render (the runtime image has no module files).
export const dynamicParams = false;

export function generateStaticParams() {
  return getAllModules().map((m) => ({ slug: m.slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const mod = getModule(slug);
  if (!mod) return { title: "Module not found" };
  return {
    title: `${mod.meta.num} · ${mod.meta.title}`,
    description: mod.meta.description,
  };
}

export default async function ModulePage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const mod = getModule(slug);
  if (!mod) notFound();

  const { meta, body } = mod;

  return (
    <ModuleView
      meta={{
        slug: meta.slug,
        num: meta.num,
        title: meta.title,
        time: meta.time,
        prerequisites: meta.prerequisites,
        isNew: meta.isNew,
      }}
    >
      <ModuleBody body={body} />
    </ModuleView>
  );
}
