import { getSections } from "@/lib/modules";
import { Catalog } from "@/components/Catalog";

export default function HomePage() {
  const sections = getSections().map((s) => ({
    name: s.name,
    modules: s.modules.map((m) => ({
      slug: m.slug,
      num: m.num,
      title: m.title,
      time: m.time,
      description: m.description,
      isNew: m.isNew,
      section: m.section,
      category: m.category,
      categoryColor: m.categoryColor,
    })),
  }));

  return <Catalog sections={sections} />;
}
