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
  NavExpandable,
  NavItem,
  Content,
} from "@patternfly/react-core";
import { BarsIcon } from "@patternfly/react-icons";

export type NavSection = {
  name: string;
  modules: { slug: string; num: string; title: string }[];
};

export function AppShell({
  sections,
  children,
}: {
  sections: NavSection[];
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
            {sections.map((section) => (
              <NavExpandable
                key={section.name}
                title={section.name}
                isExpanded
                groupId={section.name}
              >
                {section.modules.map((m) => {
                  const href = `/learn/${m.slug}`;
                  return (
                    <NavItem
                      key={m.slug}
                      component={Link}
                      href={href}
                      isActive={pathname === href}
                      itemId={m.slug}
                    >
                      {m.num} · {m.title}
                    </NavItem>
                  );
                })}
              </NavExpandable>
            ))}
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
