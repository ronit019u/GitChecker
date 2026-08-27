import type { DisplayCheck } from "@/types/types";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { unverifiedCheck } from "@/service/checkService";
import { Button } from "../ui/button";

interface StatusInfo {
  label: string;
  variant: string;
  explanation: string;
}

const getStatusInfo = (
  status: string | null,
  language: string | null
): StatusInfo => {
  switch (status) {
    case "successful":
      return {
        label: "Verified — passed",
        variant: "bg-success/15 text-success border-success/30",
        explanation:
          "The fix was tested and all checks passed. You can trust this result.",
      };
    case "failed":
      return {
        label: "Verified — failed",
        variant: "bg-error/15 text-error border-error/30",
        explanation:
          "The proposed fix was tested, but it did not pass. This means the fix is likely incorrect or incomplete — check the verification output below, and try rerunning with a more specific task description.",
      };
    case "unsupported":
      return {
        label: `${language ?? "This language"} not verifiable`,
        variant: "bg-warning/15 text-warning border-warning/30",
        explanation: `We can't automatically test fixes for ${language ?? "this language"} yet. The fix below is a proposal only — review it carefully before using it, since it hasn't been run or tested.`,
      };
    case "not_runnable":
      return {
        label: "No tests or entry point found",
        variant: "bg-warning/15 text-warning border-warning/30",
        explanation: `This ${language ?? ""} project doesn't have a test suite or a runnable entry point we could detect, so we couldn't verify the fix. Review it manually, or add tests to the repo for future checks.`,
      };
    case "error":
      return {
        label: "Verification error",
        variant: "bg-error/15 text-error border-error/30",
        explanation:
          "Something went wrong while trying to verify this fix (not related to the fix itself). Try running the check again — if it keeps failing, the repo might be too large or have an unusual setup.",
      };
    default:
      return {
        label: "Unknown status",
        variant: "outline",
        explanation:
          "We couldn't determine the verification status for this check.",
      };
  }
};

interface CheckAnalysis {
  result: DisplayCheck;
  repoUrl: string;
  task: string;
}

export const CheckAnalysis = ({ result, repoUrl, task }: CheckAnalysis) => {
  const [decision, setDecision] = useState<"saved" | "discarded" | null>(null);
  const statusInfo = getStatusInfo(result.sandbox_status, result.detected_lang);

  const saveMutation = useMutation({
    mutationFn: unverifiedCheck,
    onSuccess: () => setDecision("saved"),
  });

  return (
    <div className="flex flex-col gap-4">
      {statusInfo && (
        <div>
          <span
            className={`inline-block rounded-full border px-3 py-1 font-mono text-xs ${statusInfo.variant}`}
          >
            {statusInfo.label}
          </span>
          <p className="mt-3 text-sm  text-text-muted">
            {statusInfo.explanation}
          </p>
        </div>
      )}
      <div>
        <p className="mb-2 uppercase text-sm text-text-muted">Bug Summary</p>
        <p className="leading-relaxed text-sm">{result.bug_summary}</p>
      </div>
      {result.reason && (
        <div>
          <p className="mb-1 font-mono text-sm uppercase tracking-wide text-text-muted">
            Reasoning
          </p>
          <p className="text-sm leading-relaxed">{result.reason}</p>
        </div>
      )}
      {result.sandbox_output && (
        <div>
          <p className="mb-1 font-mono text-xs uppercase tracking-wide text-text-muted">
            Sandbox output
          </p>
          <div className="rounded-lg border border-border bg-black/40 p-3">
            <div className="mb-2 flex gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-error/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning/60" />
              <span className="h-2.5 w-2.5 rounded-full bg-success/60" />
            </div>
            <pre className="max-h-64 overflow-auto whitespace-pre-wrap font-mono text-xs text-text-muted">
              {result.sandbox_output}
            </pre>
          </div>
        </div>
      )}
      {result.requires_user_confirmation && !decision && (
        <div className="flex flex-col gap-2 rounded-lg border border-warning/30 bg-warning/10 p-3">
          <p className="text-mono text-sm text-warning">
            The gitchecker sandbox cannot verify fixes for{" "}
            {result.detected_lang ?? "this language"}. Save this proposed fix to
            your history anyway?
          </p>
          <div className="flex gap-2">
            <Button
              size="sm"
              disabled={saveMutation.isPending}
              onClick={() =>
                saveMutation.mutate({
                  repo_url: repoUrl,
                  task,
                  bug_summary: result.bug_summary ?? "",
                  fix_code: result.fix_code ?? "",
                  file_path: result.file_path ?? "",
                  detected_lang: result.detected_lang ?? "",
                })
              }
            >
              Yes, Save it
            </Button>
            <Button size="sm" onClick={() => setDecision("discarded")}>
              Donot save
            </Button>
          </div>
        </div>
      )}
      {decision == "saved" && (
        <p className="text-mono text-sm text-text-muted">Saved to history.</p>
      )}
      {decision == "discarded" && (
        <p className="text-mono text-sm text-text-muted">Discarded</p>
      )}
    </div>
  );
};
