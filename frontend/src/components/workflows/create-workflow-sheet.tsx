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
import { MmConfigFields } from "@/components/workflows/mm-config-fields";
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
  deriv_app_id: "1089",
  deriv_api_token: "",
  risk_capital: 5,
  mm_cycle_trades: 10,
  mm_target_wins: 6,
  mm_payout: 1.95,
  account_currency: "USD",
  contract_strategy: "rise_fall",
  duration_ticks: 2,
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
      <SheetContent className="p-0">
        <SheetHeader className="mb-0 shrink-0 border-b border-slate-200 px-6 py-5">
          <SheetTitle>New workflow</SheetTitle>
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
          <MmConfigFields form={form} setForm={setForm} idPrefix="wf" />
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
            <Label htmlFor="wf-app-id">Deriv app ID</Label>
            <Input
              id="wf-app-id"
              required
              placeholder="1089"
              value={form.deriv_app_id ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, deriv_app_id: e.target.value }))
              }
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="wf-api-token">Deriv API token</Label>
            <Input
              id="wf-api-token"
              type="password"
              required
              autoComplete="off"
              placeholder="From Deriv → API token"
              value={form.deriv_api_token ?? ""}
              onChange={(e) =>
                setForm((f) => ({ ...f, deriv_api_token: e.target.value }))
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
          </div>
          <div className="flex shrink-0 gap-3 border-t border-slate-200 bg-white px-6 py-4">
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