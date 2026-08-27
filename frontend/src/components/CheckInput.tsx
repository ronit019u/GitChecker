import { useState } from "react";
import { Button } from "./ui/button";
import type { CheckFormData } from "@/types/types";

interface CheckInputProps {
  check: (repoUrl: string, task: string) => void;
  isPending: boolean;
}

export const CheckInput = ({ check, isPending }: CheckInputProps) => {
  const [form, setForm] = useState<CheckFormData>({
    repoUrl: "",
    task: "",
  });
  //const queryClient = useQueryClient()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.repoUrl.trim() || !form.task.trim()) return;
    check(form.repoUrl.trim(), form.task.trim());
  };

  return (
    <div>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <div className="flex flex-col gap-1.5">
          <label className="font-mono text-xs uppercase tracking-wide">
            Repository URL
          </label>
          <input
            className="rounded-lg border border-border px-3 py-2 font-mono text-sm outline-none focus:border-primary disabled:opacity-50"
            placeholder="https://github.com/user/repo"
            value={form.repoUrl}
            onChange={(e) => setForm({ ...form, repoUrl: e.target.value })}
          />
        </div>
        <div className="flex flex-col gap-1.5">
          <label className="font-mono text-xs uppercase tracking-wide">
            Task
          </label>
          <textarea
            className="resize-none rounded-lg border  border-border bg-surface px-3 py-2 font-mono text-sm outline-none transition-colors focus:border-primary disabled:opacity-50"
            placeholder="task"
            value={form.task}
            rows={5}
            onChange={(e) => setForm({ ...form, task: e.target.value })}
          />
        </div>
        <Button
          className="mt-1 bg-primary font-mono text-sm  hover:bg-primary disabled:opacity-50"
          type="submit"
          disabled={isPending}
        >
          {isPending ? "Checking..." : "Run check"}
        </Button>
      </form>
    </div>
  );
};
