import { languageHighlighter } from "@/utility/highlighter";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
interface FixCodeProps {
  filePath: string | null;
  fixCode: string | null;
}

const cleanCode = (code: string | null): string => {
  if (!code) return "";
  return code
    .replace(/^```[\w]*\n?/, "")
    .replace(/```$/, "")
    .trim();
};

export const FixCode = ({ filePath, fixCode }: FixCodeProps) => {
  return (
    <div className="max-h-[600px] overflow-y-auto rounded-lg border border-border">
      <SyntaxHighlighter
        language={languageHighlighter(filePath)}
        style={vscDarkPlus}
        showLineNumbers
      >
        {cleanCode(fixCode)}
      </SyntaxHighlighter>
    </div>
  );
};
