"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Masthead,
  MastheadMain,
  MastheadToggle,
  MastheadBrand,
  MastheadLogo,
  MastheadContent,
  Page,
  PageSidebar,
  PageSidebarBody,
  PageToggleButton,
  Nav,
  NavList,
  NavItem,
  Label,
  Content,
  Flex,
  FlexItem,
} from "@patternfly/react-core";
import { BarsIcon } from "@patternfly/react-icons";
import type { LabelColor } from "@/lib/modules";

export type NavModule = {
  slug: string;
  num: string;
  title: string;
  category: string;
  categoryColor: LabelColor;
  isNew: boolean;
};

export function AppShell({
  modules,
  children,
}: {
  modules: NavModule[];
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  const masthead = (
    <Masthead>
      <MastheadMain>
        <MastheadToggle>
          <PageToggleButton variant="plain" aria-label="Global navigation">
            <BarsIcon />
          </PageToggleButton>
        </MastheadToggle>
        <MastheadBrand>
          <MastheadLogo component={Link} href="/">
            <span style={{ fontWeight: 700 }}>Claude Code Courseware</span>
          </MastheadLogo>
        </MastheadBrand>
      </MastheadMain>
      <MastheadContent>
        <Content component="small">RHDP operations team</Content>
      </MastheadContent>
    </Masthead>
  );

  const sidebar = (
    <PageSidebar>
      <PageSidebarBody>
        <Nav aria-label="Module navigation">
          <NavList>
            <NavItem
              component={Link}
              href="/"
              isActive={pathname === "/"}
              itemId="home"
            >
              Catalog
            </NavItem>
            {modules.map((m) => {
              const href = `/learn/${m.slug}`;
              return (
                <NavItem
                  key={m.slug}
                  component={Link}
                  href={href}
                  isActive={pathname === href}
                  itemId={m.slug}
                >
                  <Flex
                    alignItems={{ default: "alignItemsCenter" }}
                    spaceItems={{ default: "spaceItemsSm" }}
                    flexWrap={{ default: "nowrap" }}
                  >
                    <FlexItem flex={{ default: "flex_1" }}>
                      {m.num} · {m.title}
                    </FlexItem>
                    <FlexItem>
                      <Label color={m.categoryColor} isCompact>
                        {m.category}
                      </Label>
                    </FlexItem>
                  </Flex>
                </NavItem>
              );
            })}
          </NavList>
        </Nav>
      </PageSidebarBody>
    </PageSidebar>
  );

  return (
    <Page masthead={masthead} sidebar={sidebar} isManagedSidebar>
      {children}
    </Page>
  );
}
