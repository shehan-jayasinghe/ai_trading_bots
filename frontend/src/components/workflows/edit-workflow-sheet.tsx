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
} from "@/components/ui/sheet";
import { TRADING_PAIRS } from "@/constants/trading-pairs";
import { TRADING_TYPES } from "@/constants/trading-types";
import { ApiError } from "@/services/api-client";
import { useWorkflowStore } from "@/stores/workflow-store";
import type { Workflow, WorkflowUpdate } from "@/types/workflow";
import { useEffect, useState } from "react";

type Props = {
  workflow: Workflow | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

function toForm(workflow: Workflow): WorkflowUpdate {
  return {
    name: workflow.name,
    trading_pair: workflow.trading_pair,
    trading_type: workflow.trading_type,
    starting_time: workflow.starting_time ?? new Date().toISOString(),
    one_day_minimum_trade: workflow.one_day_minimum_trade ?? "1",
  };
}

export function EditWorkflowSheet({ workflow, open, onOpenChange }: Props) {
  const beginEditWorkflow = useWorkflowStore((s) => s.beginEditWorkflow);
  const updateWorkflow = useWorkflowStore((s) => s.updateWorkflow);
  const [form, setForm] = useState<WorkflowUpdate>({});
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!open || !workflow) return;
    setForm(toForm(workflow));
    setError(null);
    void beginEditWorkflow(workflow.id).catch((err) => {
      setError(
        err instanceof ApiError ? err.message : "Failed to enter edit mode",
      );
    });
  }, [open, workflow, beginEditWorkflow]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!workflow) return;
    setError(null);
    setSubmitting(true);
    try {
      await updateWorkflow(workflow.id, form);
      onOpenChange(false);
    } catch (err) {
      setError(
        err instanceof ApiError ? err.message : "Failed to save workflow",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (!workflow) return null;

  const startingTime = form.starting_time ?? "";

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Edit workflow</SheetTitle>
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
            <Label htmlFor="edit-wf-name">Name</Label>
            <Input
              id="edit-wf-name"
              required
              value={form.name ?? ""}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="edit-wf-pair">Trading pair</Label>
            <Select
              id="edit-wf-pair"
              value={form.trading_pair ?? ""}
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
            <Label htmlFor="edit-wf-type">Trading type</Label>
            <Select
              id="edit-wf-type"
              value={form.trading_type ?? ""}
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
            <Label htmlFor="edit-wf-min">Min trades per day</Label>
            <Input
              id="edit-wf-min"
              required
              value={form.one_day_minimum_trade ?? ""}
              onChange={(e) =>
                setForm((f) => ({
                  ...f,
                  one_day_minimum_trade: e.target.value,
                }))
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="edit-wf-time">Starting time</Label>
            <Input
              id="edit-wf-time"
              type="datetime-local"
              required
              value={startingTime.slice(0, 16)}
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
              {submitting ? "Saving…" : "Save"}
            </Button>
            <Button
              type="button"
              variant="destructive"
              className="flex-1"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </SheetContent>
    </Sheet>
  );
}
