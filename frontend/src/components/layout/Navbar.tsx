import { useAuth } from "@/context/AuthContext";
import { useNavigate } from "react-router-dom";
import { Login } from "../Login";
import { Button } from "../ui/button";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { deleteHistory, getHistory } from "@/service/checkService";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { HistoryIcon, LogOut, Trash2 } from "lucide-react";
import type { HistoryData } from "@/types/types";

interface NavbarProps {
  onSelectedHistory: (item: HistoryData) => void;
}

export const Navbar = ({ onSelectedHistory }: NavbarProps) => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const { data: history } = useQuery({
    queryKey: ["history"],
    queryFn: getHistory,
    enabled: !!user,
  });

  const removeHistory = useMutation({
    mutationFn: deleteHistory,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["history"] }),
  });

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <nav className="flex h-16 items-center justify-between border-b border-border bg-surface px-5">
      <span className="font-mono text-lg">GitChecker</span>
      {user ? (
        <div className="flex items-center gap-3">
          <Popover>
            <PopoverTrigger
              render={
                <Button
                  variant="ghost"
                  className="font-mono text-sm text-text-muted"
                >
                  <HistoryIcon />
                  History
                </Button>
              }
            />
            <PopoverContent className="max-h-[500px] overflow-y-auto w-80 bg-surface">
              {!history || history.length == 0 ? (
                <p className="text-mono">No past checks yet</p>
              ) : (
                history.map((check: HistoryData) => (
                  <div className="flex item-center border border-border rounded-lg gap-2 px-3 py-2.5 last:border-b-0">
                    <button
                      key={check.id}
                      onClick={() => onSelectedHistory(check)}
                      className="min-w-0 flex-1 truncate font-mono text-text hover:text-primary"
                    >
                      {check.task_description}
                    </button>
                    <button
                      onClick={() => removeHistory.mutate(check.id)}
                      className="text-white hover:text-error"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                ))
              )}
            </PopoverContent>
          </Popover>
          <div className="flex items-center gap-3">
            <Avatar className="h-7 w-7">
              <AvatarImage src={user.avatar_url} alt={user.username} />
              <AvatarFallback>
                {user.username?.[0]?.toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <span className="font-mono text-sm">{user.username}</span>
          </div>
          <Button
            className="text-text-muted hover:text-error"
            variant="ghost"
            onClick={handleLogout}
          >
            <LogOut className="h-3.5 w-3.5" />
          </Button>
        </div>
      ) : (
        <Login />
      )}
    </nav>
  );
};
