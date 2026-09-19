import { useState, type FormEvent } from "react";
import { changePassword } from "../api/changePasswordApi";
import "../../doctor/pages/DoctorPage.css";
import "./ChangePasswordModal.css";

interface ChangePasswordModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface PasswordForm {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

function ChangePasswordModal({
  isOpen,
  onClose,
}: ChangePasswordModalProps) {
  const [passwordForm, setPasswordForm] =
    useState<PasswordForm>({
      current_password: "",
      new_password: "",
      confirm_password: "",
    });

  const [isChangingPassword, setIsChangingPassword] =
    useState(false);

  const [errorMessage, setErrorMessage] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  if (!isOpen) {
    return null;
  }

  const resetForm = () => {
    setPasswordForm({
      current_password: "",
      new_password: "",
      confirm_password: "",
    });

    setErrorMessage("");
    setSuccessMessage("");
  };

  const handleClose = () => {
    if (isChangingPassword) {
      return;
    }

    resetForm();
    onClose();
  };

  const handleChange = (
    field:
      | "current_password"
      | "new_password"
      | "confirm_password",
    value: string,
  ) => {
    setPasswordForm((current) => ({
      ...current,
      [field]: value,
    }));

    setErrorMessage("");
    setSuccessMessage("");
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setErrorMessage("");
    setSuccessMessage("");

    if (
      passwordForm.new_password.length < 8 ||
      passwordForm.new_password.length > 20
    ) {
      setErrorMessage(
        "รหัสผ่านใหม่ต้องมีความยาว 8–20 ตัวอักษร",
      );
      return;
    }

    if (
      passwordForm.new_password !==
      passwordForm.confirm_password
    ) {
      setErrorMessage(
        "รหัสผ่านใหม่และยืนยันรหัสผ่านไม่ตรงกัน",
      );
      return;
    }

    setIsChangingPassword(true);

    try {
      await changePassword(passwordForm);

      setSuccessMessage(
        "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว",
      );

      setPasswordForm({
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

        const detail = response?.data?.detail;

        if (typeof detail === "string") {
          setErrorMessage(detail);
          return;
        }
      }

      setErrorMessage(
        "ไม่สามารถเปลี่ยนรหัสผ่านได้",
      );
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <div
      className="doctor-modal-overlay"
      role="presentation"
      onClick={handleClose}
    >
      <div
        className="doctor-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="change-password-modal-title"
        onClick={(event) =>
          event.stopPropagation()
        }
      >
        <h2 id="change-password-modal-title">
          เปลี่ยนรหัสผ่าน
        </h2>

        <p>
          กรอกรหัสผ่านเดิมและกำหนดรหัสผ่านใหม่
        </p>

        <form onSubmit={handleSubmit}>
          <div className="change-password-field">
            <label htmlFor="current-password">
              รหัสผ่านเดิม
            </label>

            <input
              id="current-password"
              type="password"
              value={
                passwordForm.current_password
              }
              onChange={(event) =>
                handleChange(
                  "current_password",
                  event.target.value,
                )
              }
              disabled={isChangingPassword}
              autoComplete="current-password"
              required
            />
          </div>

          <div className="change-password-field">
            <label htmlFor="new-password">
              รหัสผ่านใหม่
            </label>

            <input
              id="new-password"
              type="password"
              value={
                passwordForm.new_password
              }
              onChange={(event) =>
                handleChange(
                  "new_password",
                  event.target.value,
                )
              }
              disabled={isChangingPassword}
              autoComplete="new-password"
              required
            />
          </div>

          <div className="change-password-field">
            <label htmlFor="confirm-password">
              ยืนยันรหัสผ่านใหม่
            </label>

            <input
              id="confirm-password"
              type="password"
              value={
                passwordForm.confirm_password
              }
              onChange={(event) =>
                handleChange(
                  "confirm_password",
                  event.target.value,
                )
              }
              disabled={isChangingPassword}
              autoComplete="new-password"
              required
            />
          </div>

          {errorMessage && (
            <p
              className="change-password-message error"
              role="alert"
            >
              {errorMessage}
            </p>
          )}

          {successMessage && (
            <p
              className="change-password-message success"
              role="status"
            >
              {successMessage}
            </p>
          )}

          <div
            className="doctor-modal-actions change-password-actions"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "stretch",
              gap: "8px",
              width: "100%",
            }}
          >
            <button
              type="submit"
              className="action-button primary"
              disabled={isChangingPassword}
              style={{
                width: "100%",
                justifyContent: "center",
                boxSizing: "border-box",
              }}
            >
              {isChangingPassword
                ? "กำลังบันทึก..."
                : "เปลี่ยนรหัสผ่าน"}
            </button>

            <button
              type="button"
              className="action-button secondary"
              onClick={handleClose}
              disabled={isChangingPassword}
              style={{
                width: "100%",
                justifyContent: "center",
                boxSizing: "border-box",
              }}
            >
              ยกเลิก
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default ChangePasswordModal;