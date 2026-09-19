import { useState, type FormEvent } from "react";
import {
  changePassword,
  type ChangePasswordRequest,
} from "../api/changePasswordApi";

function ChangePasswordPage() {
  const [formData, setFormData] =
    useState<ChangePasswordRequest>({
      current_password: "",
      new_password: "",
      confirm_password: "",
    });

  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleChange = (
    field: keyof ChangePasswordRequest,
    value: string,
  ) => {
    setFormData((current) => ({
      ...current,
      [field]: value,
    }));
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setErrorMessage("");
    setSuccessMessage("");

    if (
      !formData.current_password ||
      !formData.new_password ||
      !formData.confirm_password
    ) {
      setErrorMessage("กรุณากรอกข้อมูลให้ครบทุกช่อง");
      return;
    }

    if (
      formData.current_password.length < 8 ||
      formData.current_password.length > 20
    ) {
      setErrorMessage(
        "รหัสผ่านปัจจุบันต้องมีความยาว 8–20 ตัวอักษร",
      );
      return;
    }

    if (
      formData.new_password.length < 8 ||
      formData.new_password.length > 20
    ) {
      setErrorMessage(
        "รหัสผ่านใหม่ต้องมีความยาว 8–20 ตัวอักษร",
      );
      return;
    }

    if (
      formData.confirm_password.length < 8 ||
      formData.confirm_password.length > 20
    ) {
      setErrorMessage(
        "การยืนยันรหัสผ่านต้องมีความยาว 8–20 ตัวอักษร",
      );
      return;
    }

    if (formData.new_password !== formData.confirm_password) {
      setErrorMessage("รหัสผ่านใหม่ไม่ตรงกัน");
      return;
    }

    setIsSaving(true);

    try {
      await changePassword(formData);

      setSuccessMessage("เปลี่ยนรหัสผ่านสำเร็จ");

      setFormData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      });
    } catch (error: unknown) {
      if (
        typeof error === "object" &&
        error !== null &&
        "response" in error
      ) {
        const response = (
          error as {
            response?: {
              data?: {
                detail?: string;
              };
            };
          }
        ).response;

        setErrorMessage(
          response?.data?.detail ??
            "ไม่สามารถเปลี่ยนรหัสผ่านได้",
        );
      } else {
        setErrorMessage("ไม่สามารถเปลี่ยนรหัสผ่านได้");
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <main>
      <h1>เปลี่ยนรหัสผ่าน</h1>

      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="current-password">
            รหัสผ่านปัจจุบัน
          </label>

          <input
            id="current-password"
            type="password"
            value={formData.current_password}
            onChange={(event) =>
              handleChange(
                "current_password",
                event.target.value,
              )
            }
            disabled={isSaving}
          />
        </div>

        <div>
          <label htmlFor="new-password">
            รหัสผ่านใหม่
          </label>

          <input
            id="new-password"
            type="password"
            value={formData.new_password}
            onChange={(event) =>
              handleChange(
                "new_password",
                event.target.value,
              )
            }
            disabled={isSaving}
          />
        </div>

        <div>
          <label htmlFor="confirm-password">
            ยืนยันรหัสผ่านใหม่
          </label>

          <input
            id="confirm-password"
            type="password"
            value={formData.confirm_password}
            onChange={(event) =>
              handleChange(
                "confirm_password",
                event.target.value,
              )
            }
            disabled={isSaving}
          />
        </div>

        {errorMessage && (
          <p role="alert">{errorMessage}</p>
        )}

        {successMessage && (
          <p role="status">{successMessage}</p>
        )}

        <button type="submit" disabled={isSaving}>
          {isSaving
            ? "กำลังเปลี่ยนรหัสผ่าน..."
            : "เปลี่ยนรหัสผ่าน"}
        </button>
      </form>
    </main>
  );
}

export default ChangePasswordPage;