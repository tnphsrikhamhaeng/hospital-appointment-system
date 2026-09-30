export interface ValidationResult {
  field: string | null;
  message: string;
}

const fieldLabels: Record<string, string> = {
  employee_id: "Employee ID",
  password: "รหัสผ่าน",
  preface: "คำนำหน้า",
  first_name: "ชื่อ",
  last_name: "นามสกุล",
  license_number: "เลขใบประกอบวิชาชีพ",
  phone_number: "เบอร์โทรศัพท์",
  email: "Email",
  department_id: "แผนก",
  specialization_ids: "ความเชี่ยวชาญ",
  profile_image_url: "รูปโปรไฟล์",
};

export const getValidationError = (
  error: unknown,
  fallback = "ข้อมูลไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง",
): ValidationResult => {
  if (
    typeof error !== "object" ||
    error === null ||
    !("response" in error)
  ) {
    return {
      field: null,
      message: fallback,
    };
  }

  const response = (
    error as {
      response?: {
        data?: {
          detail?: unknown;
        };
      };
    }
  ).response;

  const detail = response?.data?.detail;

  // Backend ส่ง detail เป็นข้อความ
  if (typeof detail === "string") {
    return {
      field: null,
      message: detail,
    };
  }

  // Backend ส่ง FastAPI/Pydantic validation errors
  if (Array.isArray(detail)) {
    const firstError = detail[0];

    if (
      typeof firstError !== "object" ||
      firstError === null
    ) {
      return {
        field: null,
        message: fallback,
      };
    }

    const validationError = firstError as {
      loc?: unknown;
      msg?: unknown;
      type?: unknown;
    };

    const loc = Array.isArray(validationError.loc)
      ? validationError.loc
      : [];

    const field =
      typeof loc[loc.length - 1] === "string"
        ? loc[loc.length - 1]
        : null;

    const type =
      typeof validationError.type === "string"
        ? validationError.type
        : "";

    const msg =
      typeof validationError.msg === "string"
        ? validationError.msg
        : "";

    // Pattern
    if (
      type === "string_pattern_mismatch" &&
      field === "license_number"
    ) {
      return {
        field,
        message:
          "เลขใบประกอบวิชาชีพไม่ถูกต้อง กรุณากรอกในรูปแบบ ว.12345",
      };
    }

    // Required
    if (
      type === "missing" ||
      type === "value_error.missing"
    ) {
      return {
        field,
        message: `กรุณากรอก${
          fieldLabels[field ?? ""] ?? "ข้อมูล"
        }ให้ครบถ้วน`,
      };
    }

    // String too short
    if (type === "string_too_short") {
      return {
        field,
        message: `${
          fieldLabels[field ?? ""] ?? "ข้อมูล"
        }สั้นเกินไป`,
      };
    }

    // String too long
    if (type === "string_too_long") {
      return {
        field,
        message: `${
          fieldLabels[field ?? ""] ?? "ข้อมูล"
        }ยาวเกินไป`,
      };
    }

    // Phone
    if (
      field === "phone_number" ||
      type.includes("email")
    ) {
      return {
        field,
        message: "กรุณารูปแบบเบอร์โทรศัพท์ให้ถูกต้อง",
      };
    }


    // Email
    if (
      field === "email" ||
      type.includes("email")
    ) {
      return {
        field,
        message: "กรุณากรอก Email ให้ถูกต้อง",
      };
    }

    // Fallback จาก Backend
    return {
      field,
      message:
        msg ||
        `ข้อมูล${
          fieldLabels[field ?? ""] ?? ""
        }ไม่ถูกต้อง`,
    };
  }

  return {
    field: null,
    message: fallback,
  };
};