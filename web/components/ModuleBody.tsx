import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeSanitize from "rehype-sanitize";

// Server-rendered markdown. rehype-sanitize strips any unsafe HTML embedded in
// module markdown before it reaches the DOM (defense against injected content).
export function ModuleBody({ body }: { body: string }) {
  return (
    <div className="pf-v6-c-content module-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]}>
        {body}
      </ReactMarkdown>
    </div>
  );
}
