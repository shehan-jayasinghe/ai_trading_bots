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
import { MmConfigFields } from "@/components/workflows/mm-config-fields";
import { TRADING_PAIRS } from "@/constants/trading-pairs";
import { TRADING_TYPES } from "@/constants/trading-types";
import { ApiError } from "@/services/api-client";
import { useWorkflowStore } from "@/stores/workflow-store";
import type { Workflow, WorkflowUpdate } from "@/types/workflow";
import { useEffect, useState } from "react";
import { toast } from "sonner";

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
    deriv_app_id: workflow.deriv_app_id ?? "1089",
    deriv_api_token: "",
    risk_capital: workflow.risk_capital ?? 5,
    mm_cycle_trades: workflow.mm_cycle_trades ?? 10,
    mm_target_wins: workflow.mm_target_wins ?? 6,
    mm_payout: workflow.mm_payout ?? 1.95,
    account_currency: workflow.account_currency ?? "USD",
    contract_strategy: workflow.contract_strategy ?? "rise_fall",
    duration_ticks: workflow.duration_ticks ?? 2,
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
      const message =
        err instanceof ApiError ? err.message : "Failed to enter edit mode";
      setError(message);
      toast.error(message);
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
      toast.success("Workflow saved");
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Failed to save workflow";
      setError(message);
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  }

  if (!workflow) return null;

  const startingTime = form.starting_time ?? "";

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="p-0">
        <SheetHeader className="mb-0 shrink-0 border-b border-slate-200 px-6 py-5">
          <SheetTitle>Edit workflow</SheetTitle>
        </SheetHeader>
        <form
          onSubmit={(e) => void handleSubmit(e)}
          className="flex min-h-0 flex-1 flex-col"
        >
          <div className="min-h-0 flex-1 space-y-4 overflow-y-auto px-6 py-4">
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
          <MmConfigFields form={form} setForm={setForm} idPrefix="edit-wf" />
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
            <Label htmlFor="edit-wf-app-id">Deriv app ID</Label>
            <Input
              id="edit-wf-app-id"
              required
              placeholder="1089"
              value={form.deriv_app_id ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, deriv_app_id: e.target.value }))
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="edit-wf-api-token">Deriv API token</Label>
            <Input
              id="edit-wf-api-token"
              type="password"
              autoComplete="off"
              placeholder={
                workflow.has_deriv_api_token
                  ? "Leave blank to keep current token"
                  : "From Deriv → API token"
              }
              value={form.deriv_api_token ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, deriv_api_token: e.target.value }))
              }
            />
            {workflow.has_deriv_api_token && (
              <p className="text-xs text-muted-foreground">
                API token is saved. Enter a new value only to replace it.
              </p>
            )}
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
          </div>
          <div className="flex shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
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
