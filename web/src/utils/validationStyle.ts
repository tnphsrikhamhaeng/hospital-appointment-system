import type { CSSProperties } from "react";

export const getValidationInputStyle = (
  field: string,
  errorField: string | null,
  baseStyle: CSSProperties,
): CSSProperties => {
  const isError = field === errorField;

  return {
    ...baseStyle,
    border: isError
      ? "2px solid #dc2626"
      : baseStyle.border,
    boxShadow: isError
      ? "0 0 0 3px rgba(220, 38, 38, 0.15)"
      : baseStyle.boxShadow,
    transition:
      "border-color 0.15s ease, box-shadow 0.15s ease",
  };
};