import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { login } from "../authService";
import "./LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    setErrorMessage("");
    setIsLoading(true);

    try {
      const profile = await login({
        username,
        password,
      });

      if (profile.role === "doctor") {
        navigate("/doctor", { replace: true });
        return;
      }

      if (profile.role === "hospital_staff") {
        navigate("/staff", { replace: true });
        return;
      }

      setErrorMessage("บัญชีนี้ไม่มีสิทธิ์เข้าใช้งานระบบ");
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
            "เกิดข้อผิดพลาดในการเข้าสู่ระบบ",
        );
      } else {
        setErrorMessage("ไม่สามารถเชื่อมต่อกับระบบได้");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="login-page">
      <section className="login-card">
        <div className="login-brand-panel">
          <div className="login-brand-top">
            <img
              className="login-logo"
              src="/image/logo/LOGO.png"
              alt="CareFlow"
            />

            <span className="login-brand-name">
              CareFlow
            </span>
          </div>

          <div className="login-brand-content">
            <span className="login-brand-label">
              ระบบบริหารจัดการนัดหมายโรงพยาบาล
            </span>

            <h1>
              ดูแลผู้ป่วย
              <br />
              อย่างเป็นระบบ
            </h1>

            <p>
              ระบบสำหรับแพทย์และเจ้าหน้าที่
              <br />
              เพื่อช่วยจัดการการให้บริการ
              <br />
              ภายในโรงพยาบาล
            </p>
          </div>

          <div className="login-brand-footer">
            <span>CareFlow</span>
            <span>ระบบจัดการนัดหมายโรงพยาบาล</span>
          </div>
        </div>

        <div className="login-form-panel">
          <div className="login-form-header">
            <span className="login-form-eyebrow">
              CareFlow
            </span>

            <h2>เข้าสู่ระบบ</h2>

            <p>
              กรุณาเข้าสู่ระบบเพื่อใช้งาน
            </p>
          </div>

          <form
            className="login-form"
            onSubmit={handleSubmit}
          >
            <div className="login-field">
              <label htmlFor="username">
                ชื่อผู้ใช้หรืออีเมล
              </label>

              <input
                id="username"
                type="text"
                value={username}
                onChange={(event) =>
                  setUsername(event.target.value)
                }
                placeholder="กรอกชื่อผู้ใช้หรืออีเมล"
                autoComplete="username"
                disabled={isLoading}
                required
              />
            </div>

            <div className="login-field">
              <label htmlFor="password">
                รหัสผ่าน
              </label>

              <div className="password-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  placeholder="กรอกรหัสผ่าน"
                  autoComplete="current-password"
                  disabled={isLoading}
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword((previous) => !previous)
                  }
                  disabled={isLoading}
                  aria-label={
                    showPassword
                      ? "ซ่อนรหัสผ่าน"
                      : "แสดงรหัสผ่าน"
                  }
                >
                  {showPassword ? "ซ่อน" : "แสดง"}
                </button>
              </div>
            </div>

            {errorMessage && (
              <div
                className="login-error"
                role="alert"
              >
                {errorMessage}
              </div>
            )}

            <button
              className="login-submit"
              type="submit"
              disabled={isLoading}
            >
              {isLoading
                ? "กำลังเข้าสู่ระบบ..."
                : "เข้าสู่ระบบ"}
            </button>
          </form>

          <div className="login-security-note">
            <span className="login-security-icon">
              ✓
            </span>

            <p>
              ระบบสำหรับบุคลากรที่ได้รับอนุญาตกรุณาเก็บข้อมูลบัญชีผู้ใช้เป็นความลับ
            </p>
          </div>
        </div>
      </section>

      <footer className="login-footer">
        © CareFlow Hospital Appointment Management System
      </footer>
    </main>
  );
}

export default LoginPage;