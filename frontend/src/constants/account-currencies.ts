/** Common Deriv account / proposal currencies (extend via API later). */
export const ACCOUNT_CURRENCIES = [
  { value: "USD", label: "USD" },
  { value: "USDT", label: "USDT" },
  { value: "EUR", label: "EUR" },
  { value: "GBP", label: "GBP" },
  { value: "AUD", label: "AUD" },
] as const;

export const CONTRACT_STRATEGIES = [
  { value: "rise_fall", label: "Rise / Fall (binary)" },
] as const;

export const DURATION_TICKS_OPTIONS = [
  { value: "1", label: "1 tick" },
  { value: "2", label: "2 ticks" },
] as const;
