import type { Issue } from "@/types/types";

interface IssueProps {
  issues: Issue[];
  onSelect: (issue: Issue) => void;
  isPending: boolean;
}

export const IssueList = ({ issues, onSelect, isPending }: IssueProps) => {
  if (issues.length == 0) {
    return <p>No Issues found for the task</p>;
  }

  return (
    <div className="flex flex-col gap-2">
      <p className="text-mono text-sm uppercase text-text-muted">
        {issues.length} issue
        {issues.length > 1
          ? "s found - select any one to fix"
          : "select the issue"}
      </p>
      {issues.map((issue) => (
        <button
          key={issue.id}
          disabled={isPending}
          onClick={() => onSelect(issue)}
          className="rounded-lg border border-border p-3 text-left font-mono text-sm leading-relaxed transition-colors hover:border-primary hover:bg-surface disabled:opacity-50"
        >
          {issue.bug_summary}
        </button>
      ))}
    </div>
  );
};
