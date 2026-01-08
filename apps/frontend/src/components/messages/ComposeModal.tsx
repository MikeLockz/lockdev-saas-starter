import { Check, ChevronsUpDown, Loader2, User } from "lucide-react";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Textarea } from "@/components/ui/textarea";
import { useCreateThread } from "@/hooks/api/useMessaging";
import { useCurrentOrg } from "@/hooks/useCurrentOrg";
import { useOrgMembers } from "@/hooks/useOrgMembers";
import { cn } from "@/lib/utils";

interface ComposeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultOrganizationId?: string;
  onSuccess?: (threadId: string) => void;
}

export function ComposeModal({
  open,
  onOpenChange,
  defaultOrganizationId,
  onSuccess,
}: ComposeModalProps) {
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [participantId, setParticipantId] = useState("");
  const [recipientOpen, setRecipientOpen] = useState(false);

  const { orgId } = useCurrentOrg();
  const { data: members, isLoading: isMembersLoading } = useOrgMembers(
    orgId || defaultOrganizationId,
  );
  const createThread = useCreateThread();

  // Get the selected recipient for display
  const selectedRecipient = useMemo(() => {
    if (!participantId || !members) return null;
    return members.find((m) => m.user_id === participantId);
  }, [participantId, members]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const orgIdToUse = defaultOrganizationId || orgId;
    if (!orgIdToUse || createThread.isPending || !participantId) return;

    createThread.mutate(
      {
        organization_id: orgIdToUse,
        subject,
        initial_message: message,
        participant_ids: [participantId],
      },
      {
        onSuccess: (data) => {
          onOpenChange(false);
          setSubject("");
          setMessage("");
          setParticipantId("");
          onSuccess?.(data.id);
        },
      },
    );
  };

  const handleClose = () => {
    onOpenChange(false);
    setSubject("");
    setMessage("");
    setParticipantId("");
    setRecipientOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>New Message</DialogTitle>
          <DialogDescription>Start a new conversation.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="recipient">Recipient</Label>
            <Popover open={recipientOpen} onOpenChange={setRecipientOpen}>
              <PopoverTrigger asChild>
                <Button
                  variant="outline"
                  role="combobox"
                  aria-expanded={recipientOpen}
                  className="w-full justify-between"
                >
                  {selectedRecipient ? (
                    <span className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      {selectedRecipient.display_name ||
                        selectedRecipient.email}
                    </span>
                  ) : (
                    <span className="text-muted-foreground">
                      Search recipients...
                    </span>
                  )}
                  <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
              </PopoverTrigger>
              <PopoverContent className="w-[400px] p-0">
                <Command>
                  <CommandInput placeholder="Search by name or email..." />
                  <CommandList>
                    <CommandEmpty>
                      {isMembersLoading ? (
                        <div className="flex items-center justify-center py-4">
                          <Loader2 className="h-4 w-4 animate-spin" />
                        </div>
                      ) : (
                        "No users found."
                      )}
                    </CommandEmpty>
                    <CommandGroup>
                      {members?.map((member) => (
                        <CommandItem
                          key={member.user_id}
                          value={`${member.display_name || ""} ${member.email || ""}`}
                          onSelect={() => {
                            setParticipantId(member.user_id);
                            setRecipientOpen(false);
                          }}
                        >
                          <Check
                            className={cn(
                              "mr-2 h-4 w-4",
                              participantId === member.user_id
                                ? "opacity-100"
                                : "opacity-0",
                            )}
                          />
                          <div className="flex flex-col">
                            <span className="font-medium">
                              {member.display_name || "No name"}
                            </span>
                            <span className="text-sm text-muted-foreground">
                              {member.email}
                            </span>
                          </div>
                        </CommandItem>
                      ))}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>
          </div>
          <div className="space-y-2">
            <Label htmlFor="subject">Subject</Label>
            <Input
              id="subject"
              placeholder="Thread subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="message">Message</Label>
            <Textarea
              id="message"
              placeholder="Type your message..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="h-32"
              required
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={createThread.isPending || !participantId}
            >
              {createThread.isPending ? "Sending..." : "Send Message"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
