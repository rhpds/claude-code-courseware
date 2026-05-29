"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  PageSection,
  Content,
  Gallery,
  Card,
  CardTitle,
  CardBody,
  CardFooter,
  Label,
  LabelGroup,
  Flex,
  FlexItem,
  Progress,
  ProgressMeasureLocation,
} from "@patternfly/react-core";
import { loadProgress } from "@/lib/progress";
import type { LabelColor } from "@/lib/modules";

type CatalogModule = {
  slug: string;
  num: string;
  title: string;
  time: string;
  description: string;
  isNew: boolean;
  section: string;
  category: string;
  categoryColor: LabelColor;
};

export function Catalog({
  sections,
}: {
  sections: { name: string; modules: CatalogModule[] }[];
}) {
  const [done, setDone] = useState<Record<string, boolean>>({});

  useEffect(() => {
    setDone(loadProgress());
  }, []);

  const all = sections.flatMap((s) => s.modules);
  const completed = all.filter((m) => done[m.slug]).length;

  return (
    <>
      <PageSection>
        <Content component="h1">Claude Code Courseware</Content>
        <Content component="p">
          Interactive, hands-on modules for the RHDP operations team. Pick any
          module to start a guided walkthrough.
        </Content>
        <div style={{ maxWidth: "30rem", marginTop: "1rem" }}>
          <Progress
            value={all.length ? (completed / all.length) * 100 : 0}
            title={`${completed} of ${all.length} modules complete`}
            measureLocation={ProgressMeasureLocation.outside}
            aria-label="Overall progress"
          />
        </div>
      </PageSection>

      {sections.map((section) => (
        <PageSection key={section.name}>
          <Content component="h2">{section.name}</Content>
          <Gallery hasGutter minWidths={{ default: "300px" }}>
            {section.modules.map((m) => (
              <Card key={m.slug} isClickable isCompact>
                <CardTitle>
                  <Flex
                    justifyContent={{ default: "justifyContentSpaceBetween" }}
                    alignItems={{ default: "alignItemsCenter" }}
                  >
                    <FlexItem>
                      <Link
                        href={`/learn/${m.slug}`}
                        style={{ textDecoration: "none", color: "inherit" }}
                      >
                        {m.num} · {m.title}
                      </Link>
                    </FlexItem>
                    <FlexItem>
                      <LabelGroup numLabels={3}>
                        <Label color={m.categoryColor} isCompact>
                          {m.category}
                        </Label>
                        {done[m.slug] && (
                          <Label color="green" isCompact>
                            Done
                          </Label>
                        )}
                        {m.isNew && (
                          <Label color="blue" isCompact>
                            New
                          </Label>
                        )}
                      </LabelGroup>
                    </FlexItem>
                  </Flex>
                </CardTitle>
                <CardBody>
                  <Content component="small">{m.description}</Content>
                </CardBody>
                <CardFooter>
                  <Label variant="outline" isCompact>
                    {m.time}
                  </Label>
                </CardFooter>
              </Card>
            ))}
          </Gallery>
        </PageSection>
      ))}
    </>
  );
}
