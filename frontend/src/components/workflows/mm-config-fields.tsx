"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import {
  ACCOUNT_CURRENCIES,
  CONTRACT_STRATEGIES,
  DURATION_TICKS_OPTIONS,
} from "@/constants/account-currencies";
import type { WorkflowCreate } from "@/types/workflow";

type MmFields = Pick<
  WorkflowCreate,
  | "risk_capital"
  | "mm_cycle_trades"
  | "mm_target_wins"
  | "mm_payout"
  | "account_currency"
  | "contract_strategy"
  | "duration_ticks"
>;

type Props<T extends MmFields> = {
  form: T;
  setForm: React.Dispatch<React.SetStateAction<T>>;
  idPrefix?: string;
};

export function MmConfigFields<T extends MmFields>({
  form,
  setForm,
  idPrefix = "wf",
}: Props<T>) {
  return (
    <>
      <p className="text-sm font-medium text-foreground">Money management (Masaniello)</p>
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <Label htmlFor={`${idPrefix}-risk-capital`}>Risk capital</Label>
          <Input
            id={`${idPrefix}-risk-capital`}
            type="number"
            min={0.35}
            step={0.01}
            required
            value={form.risk_capital ?? 5}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                risk_capital: parseFloat(e.target.value) || 5,
              }))
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor={`${idPrefix}-currency`}>Account currency</Label>
          <Select
            id={`${idPrefix}-currency`}
            value={form.account_currency ?? "USD"}
            onChange={(e) =>
              setForm((f) => ({ ...f, account_currency: e.target.value }))
            }
          >
            {ACCOUNT_CURRENCIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor={`${idPrefix}-cycle-trades`}>Trades per cycle</Label>
          <Input
            id={`${idPrefix}-cycle-trades`}
            type="number"
            min={1}
            required
            value={form.mm_cycle_trades ?? 10}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                mm_cycle_trades: parseInt(e.target.value, 10) || 10,
              }))
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor={`${idPrefix}-target-wins`}>Target wins (cycle)</Label>
          <Input
            id={`${idPrefix}-target-wins`}
            type="number"
            min={1}
            required
            value={form.mm_target_wins ?? 6}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                mm_target_wins: parseInt(e.target.value, 10) || 6,
              }))
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor={`${idPrefix}-payout`}>Payout (per $1)</Label>
          <Input
            id={`${idPrefix}-payout`}
            type="number"
            min={1.01}
            step={0.01}
            required
            value={form.mm_payout ?? 1.95}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                mm_payout: parseFloat(e.target.value) || 1.95,
              }))
            }
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor={`${idPrefix}-duration`}>Contract duration</Label>
          <Select
            id={`${idPrefix}-duration`}
            value={String(form.duration_ticks ?? 2)}
            onChange={(e) =>
              setForm((f) => ({
                ...f,
                duration_ticks: parseInt(e.target.value, 10) || 2,
              }))
            }
          >
            {DURATION_TICKS_OPTIONS.map((d) => (
              <option key={d.value} value={d.value}>
                {d.label}
              </option>
            ))}
          </Select>
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor={`${idPrefix}-contract`}>Contract strategy</Label>
        <Select
          id={`${idPrefix}-contract`}
          value={form.contract_strategy ?? "rise_fall"}
          onChange={(e) =>
            setForm((f) => ({ ...f, contract_strategy: e.target.value }))
          }
        >
          {CONTRACT_STRATEGIES.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </Select>
      </div>
    </>
  );
}
