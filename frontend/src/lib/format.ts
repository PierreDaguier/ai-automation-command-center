export function currency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 4,
  }).format(value);
}

export function percent(value: number): string {
  return `${value.toFixed(2)}%`;
}

export function ms(value: number): string {
  return `${Math.round(value)} ms`;
}

export function stamp(value: string): string {
  return new Date(value).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
