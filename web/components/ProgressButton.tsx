"use client";

import { useEffect, useState } from "react";
import { Button } from "@patternfly/react-core";
import { CheckCircleIcon, OutlinedCircleIcon } from "@patternfly/react-icons";
import { loadProgress, setComplete } from "@/lib/progress";

export function ProgressButton({ slug }: { slug: string }) {
  const [done, setDone] = useState(false);

  useEffect(() => {
    setDone(Boolean(loadProgress()[slug]));
  }, [slug]);

  return (
    <Button
      variant={done ? "secondary" : "primary"}
      icon={done ? <CheckCircleIcon /> : <OutlinedCircleIcon />}
      onClick={() => {
        const next = !done;
        setComplete(slug, next);
        setDone(next);
      }}
    >
      {done ? "Completed — mark incomplete" : "Mark module complete"}
    </Button>
  );
}
