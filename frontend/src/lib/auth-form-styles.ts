/** Shared auth form field styles (light ash inputs). */
export const authLabelClass = "text-sm font-medium text-slate-700";

export function authInputClass(hasError: boolean) {
  return [
    "w-full rounded-xl border px-4 py-3 text-sm text-slate-900 outline-none transition",
    "bg-slate-100 placeholder:text-slate-500 focus:ring-2",
    hasError
      ? "border-red-400 focus:border-red-400 focus:ring-red-200"
      : "border-slate-200 focus:border-slate-400 focus:ring-slate-200",
  ].join(" ");
}
