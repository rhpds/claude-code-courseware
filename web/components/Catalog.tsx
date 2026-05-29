"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
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
  Toolbar,
  ToolbarContent,
  ToolbarItem,
  ToolbarGroup,
  SearchInput,
  Select,
  SelectList,
  SelectOption,
  MenuToggle,
  EmptyState,
  EmptyStateBody,
  EmptyStateFooter,
  EmptyStateActions,
  Button,
} from "@patternfly/react-core";
import type { MenuToggleElement } from "@patternfly/react-core";
import { loadProgress } from "@/lib/progress";
import type { LabelColor, Difficulty } from "@/lib/modules";

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
  difficulty: Difficulty;
};

const ALL = "All";

export function Catalog({
  sections,
}: {
  sections: { name: string; modules: CatalogModule[] }[];
}) {
  const [done, setDone] = useState<Record<string, boolean>>({});
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string>(ALL);
  const [difficulty, setDifficulty] = useState<string>(ALL);
  const [categoryOpen, setCategoryOpen] = useState(false);
  const [difficultyOpen, setDifficultyOpen] = useState(false);

  useEffect(() => {
    setDone(loadProgress());
  }, []);

  const all = useMemo(
    () => sections.flatMap((s) => s.modules),
    [sections],
  );
  const completed = all.filter((m) => done[m.slug]).length;

  const categoryOptions = useMemo(() => {
    const set = new Set(all.map((m) => m.category));
    return [ALL, ...Array.from(set).sort()];
  }, [all]);

  const difficultyOptions = useMemo(() => {
    const set = new Set(all.map((m) => m.difficulty));
    return [ALL, ...Array.from(set)];
  }, [all]);

  const query = search.trim().toLowerCase();

  const matches = (m: CatalogModule): boolean => {
    const matchesSearch =
      query === "" ||
      m.title.toLowerCase().includes(query) ||
      m.description.toLowerCase().includes(query) ||
      m.num.toLowerCase().includes(query);
    const matchesCategory = category === ALL || m.category === category;
    const matchesDifficulty = difficulty === ALL || m.difficulty === difficulty;
    return matchesSearch && matchesCategory && matchesDifficulty;
  };

  const filteredSections = sections
    .map((section) => ({
      name: section.name,
      modules: section.modules.filter(matches),
    }))
    .filter((section) => section.modules.length > 0);

  const clearFilters = () => {
    setSearch("");
    setCategory(ALL);
    setDifficulty(ALL);
  };

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

        <Toolbar
          id="catalog-filter-toolbar"
          clearAllFilters={clearFilters}
          collapseListedFiltersBreakpoint="md"
          style={{ marginTop: "1rem" }}
        >
          <ToolbarContent>
            <ToolbarItem>
              <SearchInput
                aria-label="Search modules"
                placeholder="Search modules"
                value={search}
                onChange={(_event, value) => setSearch(value)}
                onClear={() => setSearch("")}
              />
            </ToolbarItem>
            <ToolbarGroup variant="filter-group">
              <ToolbarItem>
                <Select
                  id="category-filter"
                  aria-label="Filter by category"
                  isOpen={categoryOpen}
                  selected={category}
                  onSelect={(_event, value) => {
                    setCategory(String(value));
                    setCategoryOpen(false);
                  }}
                  onOpenChange={(isOpen) => setCategoryOpen(isOpen)}
                  toggle={(toggleRef: React.Ref<MenuToggleElement>) => (
                    <MenuToggle
                      ref={toggleRef}
                      aria-label="Filter by category"
                      onClick={() => setCategoryOpen((prev) => !prev)}
                      isExpanded={categoryOpen}
                    >
                      {category === ALL ? "Category" : category}
                    </MenuToggle>
                  )}
                >
                  <SelectList>
                    {categoryOptions.map((option) => (
                      <SelectOption key={option} value={option}>
                        {option}
                      </SelectOption>
                    ))}
                  </SelectList>
                </Select>
              </ToolbarItem>
              <ToolbarItem>
                <Select
                  id="difficulty-filter"
                  aria-label="Filter by difficulty"
                  isOpen={difficultyOpen}
                  selected={difficulty}
                  onSelect={(_event, value) => {
                    setDifficulty(String(value));
                    setDifficultyOpen(false);
                  }}
                  onOpenChange={(isOpen) => setDifficultyOpen(isOpen)}
                  toggle={(toggleRef: React.Ref<MenuToggleElement>) => (
                    <MenuToggle
                      ref={toggleRef}
                      aria-label="Filter by difficulty"
                      onClick={() => setDifficultyOpen((prev) => !prev)}
                      isExpanded={difficultyOpen}
                    >
                      {difficulty === ALL ? "Difficulty" : difficulty}
                    </MenuToggle>
                  )}
                >
                  <SelectList>
                    {difficultyOptions.map((option) => (
                      <SelectOption key={option} value={option}>
                        {option}
                      </SelectOption>
                    ))}
                  </SelectList>
                </Select>
              </ToolbarItem>
            </ToolbarGroup>
          </ToolbarContent>
        </Toolbar>
      </PageSection>

      {filteredSections.length === 0 ? (
        <PageSection>
          <EmptyState
            titleText="No modules match"
            headingLevel="h2"
            icon={undefined}
          >
            <EmptyStateBody>
              No modules match your current search and filters.
            </EmptyStateBody>
            <EmptyStateFooter>
              <EmptyStateActions>
                <Button variant="link" onClick={clearFilters}>
                  Clear filters
                </Button>
              </EmptyStateActions>
            </EmptyStateFooter>
          </EmptyState>
        </PageSection>
      ) : (
        filteredSections.map((section) => (
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
                        <LabelGroup numLabels={4}>
                          <Label color={m.categoryColor} isCompact>
                            {m.category}
                          </Label>
                          <Label variant="outline" isCompact>
                            {m.difficulty}
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
        ))
      )}
    </>
  );
}
