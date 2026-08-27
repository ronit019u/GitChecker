export const languageHighlighter = (filePath: string | null): string => {
  const ext = filePath?.split(".").pop()?.toLocaleLowerCase();
  const map: Record<string, string> = {
    py: "python",
    ts: "typescript",
    tsx: "tsx",
    js: "javascript",
    jsx: "jsx",
  };
  return map[ext ?? ""] ?? "text";
};
