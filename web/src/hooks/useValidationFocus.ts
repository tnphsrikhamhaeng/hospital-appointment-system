import {
  useRef,
  useState,
} from "react";

type FormElement =
  | HTMLInputElement
  | HTMLSelectElement
  | HTMLTextAreaElement;

export const useValidationFocus = () => {
  const fieldRefs = useRef<
    Record<string, FormElement | null>
  >({});

  const [errorField, setErrorField] =
    useState<string | null>(null);

  const registerField = (
    field: string,
    element: FormElement | null,
  ) => {
    fieldRefs.current[field] = element;
  };

  const focusField = (
    field: string,
  ) => {
    setErrorField(field);

    requestAnimationFrame(() => {
      const element =
        fieldRefs.current[field];

      if (!element) {
        return;
      }

      element.focus();

      element.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    });
  };

  const clearFieldError = (
    field: string,
  ) => {
    setErrorField((current) =>
      current === field
        ? null
        : current,
    );
  };

  const clearValidationError = () => {
    setErrorField(null);
  };

  return {
    errorField,
    registerField,
    focusField,
    clearFieldError,
    clearValidationError,
  };
};