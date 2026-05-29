"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
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
  difficulty?: string;
};

export function AppShell({
  modules,
  children,
}: {
  modules: NavModule[];
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const navRef = useRef<HTMLDivElement>(null);

  // Scroll the active NavItem into view within the sidebar whenever the route
  // changes. With 29 modules the active item is often below the fold. Querying
  // by data attribute keeps this robust when no item matches (e.g. the catalog
  // home page), where querySelector simply returns null and we do nothing.
  useEffect(() => {
    const active = navRef.current?.querySelector<HTMLElement>(
      '[data-active-nav-item="true"]'
    );
    active?.scrollIntoView({ block: "nearest" });
  }, [pathname]);

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
        <div ref={navRef}>
        <Nav aria-label="Module navigation">
          <NavList>
            <NavItem
              component={Link}
              href="/"
              isActive={pathname === "/"}
              itemId="home"
              {...(pathname === "/" ? { "data-active-nav-item": "true" } : {})}
            >
              Catalog
            </NavItem>
            {modules.map((m) => {
              const href = `/learn/${m.slug}`;
              const isActive = pathname === href;
              return (
                <NavItem
                  key={m.slug}
                  component={Link}
                  href={href}
                  isActive={isActive}
                  itemId={m.slug}
                  {...(isActive ? { "data-active-nav-item": "true" } : {})}
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
        </div>
      </PageSidebarBody>
    </PageSidebar>
  );

  return (
    <Page
      masthead={masthead}
      sidebar={sidebar}
      isManagedSidebar
      defaultManagedSidebarIsOpen
    >
      {children}
    </Page>
  );
}
