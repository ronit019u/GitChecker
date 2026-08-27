export interface User {
  logged_in_user_id: string;
  username: string;
  avatar_url: string;
}

export interface AuthContextType {
  user: User | null;
  login: (userData: User) => void;
  logout: () => Promise<void>;
}

export interface CheckRequest {
  repo_url: string;
  task: string;
}

export interface Issue {
  id: number;
  bug_summary: string;
  suggested_fix_direction: string;
  files_checked: string[];
}

export interface StartResponse {
  issues: Issue[];
}

export interface CoderResult {
  file_path: string;
  fix_code: string;
  reason: string;
}

export interface SandboxResult {
  status: string;
  output: string;
  detail: string;
  requires_user_confirmation: boolean;
  detected_lang: string;
}

export interface FixRequest {
  repo_url: string;
  task: string;
  issue: Issue;
}

export interface FixResponse {
  coder: CoderResult;
  verify: SandboxResult;
}

export interface DisplayCheck {
  success: boolean;
  bug_summary: string | null;
  fix_code: string | null;
  file_path: string | null;
  reason: string | null;
  sandbox_status: string | null;
  sandbox_output: string | null;
  sandbox_detail: string | null;
  requires_user_confirmation: boolean;
  detected_lang: string | null;
  error: string | null;
}

export interface CheckFormData {
  repoUrl: string;
  task: string;
}

export interface checkOutputData {
  result: DisplayCheck;
  repoUrl: string;
  task: string;
}

export interface SaveCheck {
  repo_url: string;
  task: string;
  bug_summary: string;
  fix_code: string;
  file_path: string;
  detected_lang: string;
}

export interface HistoryData {
  id: string;
  repo_url: string;
  task_description: string;
  reason: string;
  bug_summary: string;
  fix_code: string;
  file_path: string;
  detected_lang: string | null;
  status: string;
  created_at: string;
}
