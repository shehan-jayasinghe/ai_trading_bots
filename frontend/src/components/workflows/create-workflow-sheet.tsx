"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { TRADING_PAIRS } from "@/constants/trading-pairs";
import { TRADING_TYPES } from "@/constants/trading-types";
import { ApiError } from "@/services/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { useWorkflowStore } from "@/stores/workflow-store";
import type { WorkflowCreate } from "@/types/workflow";
import { useState } from "react";
import { toast } from "sonner";

const defaultForm = (): WorkflowCreate => ({
  name: "",
  trading_pair: TRADING_PAIRS[0].value,
  trading_type: TRADING_TYPES[0].value,
  starting_time: new Date().toISOString(),
  one_day_minimum_trade: "1",
});

export function CreateWorkflowSheet() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const createWorkflow = useWorkflowStore((s) => s.createWorkflow);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState<WorkflowCreate>(defaultForm);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await createWorkflow(form);
      setForm(defaultForm());
      setOpen(false);
      toast.success("Workflow created");
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to create workflow";
      setError(message);
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button disabled={!accessToken}>Create workflow</Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>New workflow</SheetTitle>
        </SheetHeader>
        <form
          onSubmit={(e) => void handleSubmit(e)}
          className="flex flex-1 flex-col gap-4"
        >
          {error && (
            <p className="text-sm text-red-600" role="alert">
              {error}
            </p>
          )}
          <div className="space-y-2">
            <Label htmlFor="wf-name">Name</Label>
            <Input
              id="wf-name"
              required
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="wf-pair">Trading pair</Label>
            <Select
              id="wf-pair"
              value={form.trading_pair}
              onChange={(e) =>
                setForm((f) => ({ ...f, trading_pair: e.target.value }))
              }
            >
              {TRADING_PAIRS.map((p) => (
                <option key={p.value} value={p.value}>
                  {p.label}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="wf-type">Trading type</Label>
            <Select
              id="wf-type"
              value={form.trading_type}
              onChange={(e) =>
                setForm((f) => ({ ...f, trading_type: e.target.value }))
              }
            >
              {TRADING_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                </option>
              ))}
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="wf-min">Min trades per day</Label>
            <Input
              id="wf-min"
              required
              value={form.one_day_minimum_trade}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  one_day_minimum_trade: e.target.value,
                }))
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="wf-time">Starting time</Label>
            <Input
              id="wf-time"
              type="datetime-local"
              required
              value={form.starting_time.slice(0, 16)}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  starting_time: new Date(e.target.value).toISOString(),
                }))
              }
            />
          </div>
          <div className="mt-auto flex gap-3 pt-4">
            <Button type="submit" disabled={submitting} className="flex-1">
              {submitting ? "Creating…" : "Create"}
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="flex-1"
              onClick={() => setOpen(false)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </SheetContent>
    </Sheet>
  );
}