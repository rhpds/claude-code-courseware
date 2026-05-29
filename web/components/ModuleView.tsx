"use client";

import {
  PageSection,
  Content,
  Label,
  LabelGroup,
  Flex,
  FlexItem,
  Divider,
} from "@patternfly/react-core";
import { ProgressButton } from "@/components/ProgressButton";

type Meta = {
  slug: string;
  num: string;
  title: string;
  time: string;
  prerequisites: string;
  isNew: boolean;
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
      <Divider />
      <PageSection>{children}</PageSection>
    </>
  );
}
