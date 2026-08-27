import { CheckInput } from "@/components/CheckInput";
import { CheckAnalysis } from "@/components/checkoutput/CheckAnalysis";
import { FilePath } from "@/components/checkoutput/FilePath";
import { FixCode } from "@/components/checkoutput/FixCode";
import { IssueList } from "@/components/IssueList";
import { useAuth } from "@/context/AuthContext";
import { getIssues, getFix } from "@/service/checkService";
import type { DisplayCheck, HistoryData, Issue } from "@/types/types";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { useOutletContext } from "react-router-dom";

interface LayoutContext {
  selectedHistoryItem: HistoryData | null;
  clearSelectedHistoryItem: () => void;
}

export const Home = () => {
  const { user } = useAuth();
  const [selectedIssue, setSelectedIssue] = useState<Issue | null>(null);
  const [lastSubmited, setLastSubmitted] = useState<{
    repoUrl: string;
    task: string;
  } | null>(null);
  const { selectedHistoryItem, clearSelectedHistoryItem } =
    useOutletContext<LayoutContext>();

  const issueMutation = useMutation({
    mutationFn: getIssues,
    onError: (err) => console.log("CHECK ERROR:", err),
  });

  const fixMutation = useMutation({
    mutationFn: getFix,
  });

  const handleCheck = (repoUrl: string, task: string) => {
    clearSelectedHistoryItem();
    setSelectedIssue(null);
    fixMutation.reset();
    setLastSubmitted({ repoUrl, task });
    issueMutation.mutate({ repo_url: repoUrl, task });
  };

  const handleSelectIssue = (issue: Issue) => {
    if (!lastSubmited) return;
    setSelectedIssue(issue);
    fixMutation.mutate({
      repo_url: lastSubmited.repoUrl,
      task: lastSubmited.task,
      issue,
    });
  };

  const display: DisplayCheck | undefined = selectedHistoryItem
    ? {
        success: true,
        bug_summary: selectedHistoryItem.bug_summary,
        fix_code: selectedHistoryItem.fix_code,
        file_path: selectedHistoryItem.file_path,
        reason: null,
        sandbox_status: selectedHistoryItem.status,
        sandbox_output: null,
        sandbox_detail: null,
        requires_user_confirmation: false,
        detected_lang: selectedHistoryItem.detected_lang,
        error: null,
      }
    : fixMutation.data
      ? {
          success: true,
          bug_summary: selectedIssue?.bug_summary ?? null,
          fix_code: fixMutation.data.coder.fix_code,
          file_path: fixMutation.data.coder.file_path,
          reason: fixMutation.data.coder.reason,
          sandbox_status: fixMutation.data.verify.status,
          sandbox_output: fixMutation.data.verify.output,
          sandbox_detail: fixMutation.data.verify.detail,
          requires_user_confirmation:
            fixMutation.data.verify.requires_user_confirmation,
          detected_lang: fixMutation.data.verify.detected_lang,
          error: null,
        }
      : undefined;

  console.log(fixMutation.data);

  //like a condition if this is true then display the issue list
  const displayIssueList =
    !selectedHistoryItem &&
    issueMutation.data &&
    !fixMutation.data &&
    !fixMutation.isPending;

  return (
    <div className="min-h-[calc(100vh-64px)] bg-background">
      {user ? (
        <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr_700px] h-[calc(100vh-64px)]">
          {/* column one*/}
          <div className="border-r border-border overflow-y-auto">
            <FilePath filePath={display?.file_path ?? ""} />
          </div>
          {/*column 2 */}
          <div className="overflow-y-auto p-6">
            {!display && !issueMutation.isPending && !fixMutation.isPending && (
              <div className="flex h-full items-center justify-center">
                <p className="font-mono text-sm text-text-muted">
                  Fix code will appear here
                </p>
              </div>
            )}
            {issueMutation.isPending && (
              <div className="flex h-full items-center justify-center">
                <p className="font-mono text-sm text-primary animate-pulse">
                  Cloning repo and finding issues...
                </p>
              </div>
            )}
            {fixMutation.isPending && (
              <div className="flex h-full items-center justify-center">
                <p className="font-mono text-sm text-primary animate-pulse">
                  applying fix and verifying the fix...
                </p>
              </div>
            )}
            {display && (
              <FixCode
                filePath={display.file_path}
                fixCode={display.fix_code}
              />
            )}
          </div>
          <div className="flex flex-col border-l border-border p-6 gap-10">
            <h1 className="mb-1 font-mono text-lg">gitChecker</h1>
            <p className="font-mono text-sm text-text-muted">
              Paste a public repo url and describe the bug - we'll find it, fix
              it, and verify it.
            </p>
            {selectedHistoryItem ? selectedHistoryItem.task_description : ""}
            {display && (
              <CheckAnalysis
                result={display}
                repoUrl={
                  selectedHistoryItem
                    ? selectedHistoryItem.repo_url
                    : (lastSubmited?.repoUrl ?? "")
                }
                task={
                  selectedHistoryItem
                    ? selectedHistoryItem.task_description
                    : (lastSubmited?.task ?? "")
                }
              />
            )}
            {displayIssueList && (
              <IssueList
                issues={issueMutation.data.issues}
                onSelect={handleSelectIssue}
                isPending={fixMutation.isPending}
              />
            )}
            <CheckInput
              check={handleCheck}
              isPending={issueMutation.isPending}
            />
          </div>
        </div>
      ) : (
        <div className="flex h-[calc(100hv-64px)] flex-col items-center justify-center">
          <p className="font-mono">Sign in to check your repos</p>
        </div>
      )}
    </div>
  );
};
