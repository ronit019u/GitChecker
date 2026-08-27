import { Folder, FileCode } from "lucide-react";

interface FilePathProps {
  filePath: string | null;
}

export const FilePath = ({ filePath }: FilePathProps) => {
  if (!filePath) {
    return (
      <p className="p-4 font-mono text-xs text-text-muted">
        Fixed file path will appear here
      </p>
    );
  }

  const segments = filePath.split("/").filter(Boolean);
  const fileName = segments[segments.length - 1];
  const folders = segments.slice(0, -1);

  return (
    <div className="p-3">
      {folders.map((folder, i) => (
        <div
          key={i}
          className="flex items-center gap-1.5 py-1 font-mono text-xs text-text-muted"
          style={{ paddingLeft: `${i * 14}px` }}
        >
          <Folder className="h-3.5 w-3.5 shrink-0 text-primary/70" />
          <span className="truncate">{folder}</span>
        </div>
      ))}

      <div
        className="flex items-center gap-1.5 rounded-md bg-surface py-1.5 font-mono text-xs text-text"
        style={{ paddingLeft: `${folders.length * 14 + 4}px` }}
      >
        <FileCode className="h-3.5 w-3.5 shrink-0 text-primary" />
        <span className="truncate">{fileName}</span>
      </div>
    </div>
  );
};
