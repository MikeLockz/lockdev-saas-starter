import { useState } from "react";
import { Button } from "@/components/ui/button";
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
import { Textarea } from "@/components/ui/textarea";
import { useCreateThread } from "@/hooks/api/useMessaging";

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
  const [participantId, setParticipantId] = useState(""); // Single participant for now

  const createThread = useCreateThread();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!defaultOrganizationId && !createThread.isPending) return; // Must have org context

    createThread.mutate(
      {
        organization_id: defaultOrganizationId!,
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>New Message</DialogTitle>
          <DialogDescription>Start a new conversation.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="recipient">Recipient (User ID)</Label>
            <Input
              id="recipient"
              placeholder="UUID of recipient"
              value={participantId}
              onChange={(e) => setParticipantId(e.target.value)}
              required
            />
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
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createThread.isPending}>
              {createThread.isPending ? "Sending..." : "Send Message"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
