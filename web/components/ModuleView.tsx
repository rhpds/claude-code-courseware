"use client";

import {
  PageSection,
  Content,
  Label,
  LabelGroup,
  Flex,
  FlexItem,
  Divider,
  Card,
  CardBody,
  ClipboardCopy,
} from "@patternfly/react-core";
import { ProgressButton } from "@/components/ProgressButton";
import type { LabelColor, Difficulty } from "@/lib/modules";

type Meta = {
  slug: string;
  num: string;
  title: string;
  time: string;
  prerequisites: string;
  isNew: boolean;
  category: string;
  categoryColor: LabelColor;
  difficulty: Difficulty;
};

export function ModuleView({
  meta,
  children,
}: {
  meta: Meta;
  children: React.ReactNode;
}) {
  return (
    <>
      <PageSection>
        <Flex
          justifyContent={{ default: "justifyContentSpaceBetween" }}
          alignItems={{ default: "alignItemsFlexStart" }}
        >
          <FlexItem>
            <Content component="h1">
              Module {meta.num} — {meta.title}
            </Content>
            <LabelGroup>
              <Label color={meta.categoryColor}>{meta.category}</Label>
              <Label variant="outline">{meta.difficulty}</Label>
              {meta.time && <Label color="blue">{meta.time}</Label>}
              <Label variant="outline">
                Prerequisites: {meta.prerequisites}
              </Label>
              {meta.isNew && <Label color="green">New</Label>}
            </LabelGroup>
          </FlexItem>
          <FlexItem>
            <ProgressButton slug={meta.slug} />
          </FlexItem>
        </Flex>
      </PageSection>
      <PageSection>
        <Card isCompact>
          <CardBody>
            <Content component="p">
              <strong>How to run this module.</strong> This is a hands-on Claude
              Code module — the steps below execute inside the Claude Code CLI,
              not in the browser. Open Claude Code in the courseware repo and run:
            </Content>
            <ClipboardCopy
              isReadOnly
              hoverTip="Copy"
              clickTip="Copied"
              variant="inline-compact"
            >
              {`/learn-${meta.slug}`}
            </ClipboardCopy>
          </CardBody>
        </Card>
      </PageSection>
      <Divider />
      <PageSection>{children}</PageSection>
    </>
  );
}
