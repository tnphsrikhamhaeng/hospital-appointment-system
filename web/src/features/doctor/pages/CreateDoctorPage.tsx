import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { getValidationError } from "../../../utils/validation";
import { useValidationFocus } from "../../../hooks/useValidationFocus";
import { getValidationInputStyle } from "../../../utils/validationStyle";

import {
  createDoctor,
  uploadDoctorImage,
  type DoctorCreateRequest,
} from "../api/doctorApi";

import {
  getDepartments,
  type DepartmentResponse,
} from "../../department/api/departmentApi";

import {
  getSpecializations,
  type SpecializationResponse,
} from "../../department/api/specializationApi";

import "./DoctorPage.css";

const inputStyle: React.CSSProperties = {
  width: "100%",
  height: "42px",
  boxSizing: "border-box",
  padding: "0 12px",
  border: "1px solid var(--border)",
  borderRadius: "7px",
  outline: "none",
  background: "var(--surface)",
  color: "var(--text)",
  fontFamily: "var(--font)",
  fontSize: "14px",
};

const getInputValidationStyle = (field: string, errorField: string | null) =>
  getValidationInputStyle(field, errorField, inputStyle);

const fieldStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "7px",
};

const labelStyle: React.CSSProperties = {
  color: "var(--text)",
  fontSize: "13px",
  fontWeight: 500,
};

const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

const ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"];

function CreateDoctorPage() {
  const navigate = useNavigate();
  const { errorField, registerField, focusField, clearFieldError } =
    useValidationFocus();

  const [departments, setDepartments] = useState<DepartmentResponse[]>([]);

  const [specializations, setSpecializations] = useState<
    SpecializationResponse[]
  >([]);

  const [form, setForm] = useState<DoctorCreateRequest>({
    employee_id: "",
    password: "",
    profile_image_url: null,
    preface: "mr_doctor",
    first_name: "",
    last_name: "",
    license_number: "",
    phone_number: "",
    email: "",
    department_id: "",
    specialization_ids: [],
  });

  const [isLoading, setIsLoading] = useState(true);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [isUploadingImage, setIsUploadingImage] = useState(false);

  const [profileImagePreview, setProfileImagePreview] = useState<string | null>(
    null,
  );

  const [errorMessage, setErrorMessage] = useState("");

  const [isSaveSuccessOpen, setIsSaveSuccessOpen] = useState(false);

  useEffect(() => {
    const loadOptions = async () => {
      setIsLoading(true);
      setErrorMessage("");

      try {
        const [departmentData, specializationData] = await Promise.all([
          getDepartments(),
          getSpecializations(),
        ]);

        setDepartments(departmentData);
        setSpecializations(specializationData);
      } catch {
        setErrorMessage("ไม่สามารถโหลดข้อมูลแผนกหรือความเชี่ยวชาญได้");
      } finally {
        setIsLoading(false);
      }
    };

    void loadOptions();
  }, []);

  const handleChange = (
    field: keyof DoctorCreateRequest,
    value: string | null,
  ) => {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));

    clearFieldError(field);

    if (errorMessage) {
      setErrorMessage("");
    }
  };

  const handleSpecializationChange = (
    specializationId: string,
    checked: boolean,
  ) => {
    setForm((current) => ({
      ...current,
      specialization_ids: checked
        ? [...current.specialization_ids, specializationId]
        : current.specialization_ids.filter((id) => id !== specializationId),
    }));

    clearFieldError("specialization_ids");

    if (errorMessage) {
      setErrorMessage("");
    }
  };

  const handleProfileImageChange = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setErrorMessage("");

    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setErrorMessage("รองรับเฉพาะไฟล์ JPG, PNG และ WEBP");
      event.target.value = "";
      return;
    }

    if (file.size > MAX_IMAGE_SIZE) {
      setErrorMessage("ขนาดรูปภาพต้องไม่เกิน 5 MB");
      event.target.value = "";
      return;
    }

    const previewUrl = URL.createObjectURL(file);

    setProfileImagePreview(previewUrl);
    setIsUploadingImage(true);

    try {
      const result = await uploadDoctorImage(file);

      setForm((current) => ({
        ...current,
        profile_image_url: result.image_url,
      }));
    } catch (error: unknown) {
      URL.revokeObjectURL(previewUrl);
      setProfileImagePreview(null);
      setForm((current) => ({
        ...current,
        profile_image_url: null,
      }));

      const validation = getValidationError(
        error,
        "ไม่สามารถอัปโหลดรูปโปรไฟล์ได้",
      );

      setErrorMessage(validation.message);

      if (validation.field) {
        focusField(validation.field);
      }
    } finally {
      setIsUploadingImage(false);
      event.target.value = "";
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setErrorMessage("");

    if (isUploadingImage) {
      setErrorMessage("กรุณารอให้การอัปโหลดรูปโปรไฟล์เสร็จสิ้น");
      return;
    }

    if (!form.employee_id.trim()) {
      setErrorMessage("กรุณากรอก Employee ID");
      focusField("employee_id");
      return;
    }

    if (!form.password) {
      setErrorMessage("กรุณากรอกรหัสผ่าน");
      focusField("password");
      return;
    }

    if (form.password.length < 8) {
      setErrorMessage("รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร");
      focusField("password");
      return;
    }

    if (!form.first_name.trim()) {
      setErrorMessage("กรุณากรอกชื่อ");
      focusField("first_name");
      return;
    }

    if (!form.last_name.trim()) {
      setErrorMessage("กรุณากรอกนามสกุล");
      focusField("last_name");
      return;
    }

    if (!form.license_number.trim()) {
      setErrorMessage("กรุณากรอกเลขใบประกอบวิชาชีพ");
      focusField("license_number");
      return;
    }

    if (!form.phone_number.trim()) {
      setErrorMessage("กรุณากรอกเบอร์โทรศัพท์");
      focusField("phone_number");
      return;
    }

    if (!form.email.trim()) {
      setErrorMessage("กรุณากรอก Email");
      focusField("email");
      return;
    }

    if (!form.department_id) {
      setErrorMessage("กรุณาเลือกแผนก");
      focusField("department_id");
      return;
    }

    if (form.specialization_ids.length === 0) {
      setErrorMessage("กรุณาเลือกความเชี่ยวชาญอย่างน้อย 1 รายการ");
      focusField("specialization_ids");
      return;
    }

    setIsSubmitting(true);

    try {
      await createDoctor({
        ...form,
        employee_id: form.employee_id.trim(),
        first_name: form.first_name.trim(),
        last_name: form.last_name.trim(),
        license_number: form.license_number.trim(),
        phone_number: form.phone_number.trim(),
        email: form.email.trim(),
        profile_image_url: form.profile_image_url?.trim() || null,
      });

      setIsSaveSuccessOpen(true);

      if (profileImagePreview) {
        URL.revokeObjectURL(profileImagePreview);
      }

      setProfileImagePreview(null);

      setForm({
        employee_id: "",
        password: "",
        profile_image_url: null,
        preface: "mr_doctor",
        first_name: "",
        last_name: "",
        license_number: "",
        phone_number: "",
        email: "",
        department_id: "",
        specialization_ids: [],
      });
    } catch (error: unknown) {
      const validation = getValidationError(error, "ไม่สามารถเพิ่มแพทย์ได้");

      setErrorMessage(validation.message);

      if (validation.field) {
        focusField(validation.field);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <section className="doctor-content">
        <div
          style={{
            padding: "32px",
            color: "var(--muted)",
            fontSize: "14px",
          }}
        >
          กำลังโหลดข้อมูล...
        </div>
      </section>
    );
  }

  const activeSpecializations = specializations.filter(
    (specialization) =>
      specialization.status === "active" &&
      (!form.department_id ||
        specialization.department_id === form.department_id),
  );

  return (
    <section className="doctor-content">
      <header className="doctor-header">
        <div>
          <span className="page-eyebrow">CareFlow Hospital System</span>

          <h1>เพิ่มแพทย์</h1>

          <p>เพิ่มข้อมูลแพทย์เข้าสู่ระบบโรงพยาบาล</p>
        </div>
      </header>

      {errorMessage && (
        <div className="doctor-alert" role="alert">
          {errorMessage}
        </div>
      )}

      <section className="current-patient-section">
        <div className="current-patient-card">
          <div className="current-patient-header">
            <div>
              <span className="section-eyebrow">Doctor Management</span>

              <h2>ข้อมูลแพทย์</h2>

              <p>กรุณากรอกข้อมูลแพทย์ให้ครบถ้วน</p>
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            style={{
              padding: "24px",
            }}
          >
            {/* =========================
                  1. Account Information
              ========================== */}
            <section
              style={{
                marginBottom: "28px",
              }}
            >
              <div
                style={{
                  marginBottom: "16px",
                }}
              >
                <h3
                  style={{
                    margin: "0 0 4px",
                    color: "var(--text)",
                    fontSize: "15px",
                    fontWeight: 600,
                  }}
                >
                  ข้อมูลบัญชี
                </h3>

                <p
                  style={{
                    margin: 0,
                    color: "var(--muted)",
                    fontSize: "13px",
                  }}
                >
                  กำหนดข้อมูลสำหรับเข้าสู่ระบบของแพทย์
                </p>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: "20px 28px",
                }}
              >
                <div style={fieldStyle}>
                  <label htmlFor="employee-id" style={labelStyle}>
                    Employee ID
                  </label>

                  <input
                    ref={(element) => registerField("employee_id", element)}
                    id="employee-id"
                    type="text"
                    value={form.employee_id}
                    onChange={(event) =>
                      handleChange("employee_id", event.target.value)
                    }
                    disabled={isSubmitting || isUploadingImage}
                    style={getInputValidationStyle("employee_id", errorField)}
                  />
                </div>

                <div style={fieldStyle}>
                  <label htmlFor="password" style={labelStyle}>
                    Password
                  </label>

                  <input
                    ref={(element) => registerField("password", element)}
                    id="password"
                    type="password"
                    value={form.password}
                    onChange={(event) =>
                      handleChange("password", event.target.value)
                    }
                    disabled={isSubmitting || isUploadingImage}
                    style={getInputValidationStyle("password", errorField)}
                  />
                </div>
              </div>
            </section>

            {/* =========================
                  2. Personal Information
              ========================== */}
            <section
              style={{
                marginBottom: "28px",
              }}
            >
              <div
                style={{
                  marginBottom: "16px",
                }}
              >
                <h3
                  style={{
                    margin: "0 0 4px",
                    color: "var(--text)",
                    fontSize: "15px",
                    fontWeight: 600,
                  }}
                >
                  ข้อมูลส่วนตัว
                </h3>

                <p
                  style={{
                    margin: 0,
                    color: "var(--muted)",
                    fontSize: "13px",
                  }}
                >
                  ข้อมูลชื่อและคำนำหน้าของแพทย์
                </p>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: "20px 28px",
                }}
              >
                <div style={fieldStyle}>
                  <label htmlFor="preface" style={labelStyle}>
                    คำนำหน้า
                  </label>

                  <select
                    ref={(element) => registerField("preface", element)}
                    id="preface"
                    value={form.preface}
                    onChange={(event) =>
                      handleChange("preface", event.target.value)
                    }
                    disabled={isSubmitting || isUploadingImage}
                    style={getInputValidationStyle("preface", errorField)}
                  >
                    <option value="mr_doctor">นายแพทย์</option>

                    <option value="female_doctor">แพทย์หญิง</option>
                  </select>
                </div>

                <div style={fieldStyle}>
                  <label htmlFor="first-name" style={labelStyle}>
                    ชื่อ
                  </label>

                  <input
                    ref={(element) => registerField("first_name", element)}
                    id="first-name"
                    type="text"
                    value={form.first_name}
                    onChange={(event) =>
                      handleChange("first_name", event.target.value)
                    }
                    disabled={isSubmitting || isUploadingImage}
                    style={getInputValidationStyle("first_name", errorField)}
                  />
                </div>

                <div
                  style={{
                    ...fieldStyle,
                    gridColumn: "1 / -1",
                  }}
                >
                  <label htmlFor="last-name" style={labelStyle}>
                    นามสกุล
                  </label>

                  <input
                    ref={(element) => registerField("last_name", element)}
                    id="last-name"
                    type="text"
                    value={form.last_name}
                    onChange={(event) =>
                      handleChange("last_name", event.target.value)
                    }
                    disabled={isSubmitting || isUploadingImage}
                    style={getInputValidationStyle("last_name", errorField)}
                  />
                </div>
              </div>
            </section>

            {/* =========================
                  3. Professional Information
              ========================== */}
            <section
              style={{
                marginBottom: "28px",
              }}
            >
              <div
                style={{
                  marginBottom: "16px",
                }}
              >
                <h3
                  style={{
                    margin: "0 0 4px",
                    color: "var(--text)",
                    fontSize: "15px",
                    fontWeight: 600,
                  }}
                >
                  ข้อมูลวิชาชีพ
                </h3>

                <p
                  style={{
                    margin: 0,
                    color: "var(--muted)",
                    fontSize: "13px",
                  }}
                >
                  ข้อมูลใบประกอบวิชาชีพของแพทย์
                </p>
              </div>

              <div style={fieldStyle}>
                <label htmlFor="license-number" style={labelStyle}>
                  เลขใบประกอบวิชาชีพ
                </label>

                <input
                  ref={(element) => registerField("license_number", element)}
                  id="license-number"
                  type="text"
                  value={form.license_number}
                  onChange={(event) =>
                    handleChange("license_number", event.target.value)
                  }
                  disabled={isSubmitting || isUploadingImage}
                  style={getInputValidationStyle("license_number", errorField)}
                />
              </div>
            </section>

            {/* =========================
                  4. Contact Information
              ========================== */}
            <section
              style={{
                marginBottom: "28px",
              }}
            >
              <div
                style={{
                  marginBottom: "16px",
                }}
              >
                <h3
                  style={{
                    margin: "0 0 4px",
                    color: "var(--text)",
                    fontSize: "15px",
                    fontWeight: 600,
                  }}
                >
                  ข้อมูลติดต่อ
                </h3>

                <p
                  style={{
                    margin: 0,
                    color: "var(--muted)",
                    fontSize: "13px",
                  }}
                >
                  ข้อมูลสำหรับติดต่อแพทย์
                </p>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
                  gap: "20px 28px",
                }}
              >
                <div style={fieldStyle}>
                  <label htmlFor="phone-number" style={labelStyle}>
                    เบอร์โทรศัพท์
                  </label>

                  <input
                    ref={(element) => registerField("phone_number", element)}
                    id="phone-number"
                    type="text"
                    value={form.phone_number}
                    onChange={(event) =>
                      handleChange("phone_number", event.target.value)
                    }
                    disabled={isSubmitting || isUploadingImage}
                    style={getInputValidationStyle("phone_number", errorField)}
                  />
                </div>

                <div style={fieldStyle}>
                  <label htmlFor="email" style={labelStyle}>
                    Email
                  </label>

                  <input
                    ref={(element) => registerField("email", element)}
                    id="email"
                    type="email"
                    value={form.email}
                    onChange={(event) =>
                      handleChange("email", event.target.value)
                    }
                    disabled={isSubmitting || isUploadingImage}
                    style={getInputValidationStyle("email", errorField)}
                  />
                </div>
              </div>
            </section>

            {/* =========================
                  5. Work Information
              ========================== */}
            <section
              style={{
                marginBottom: "28px",
              }}
            >
              <div
                style={{
                  marginBottom: "16px",
                }}
              >
                <h3
                  style={{
                    margin: "0 0 4px",
                    color: "var(--text)",
                    fontSize: "15px",
                    fontWeight: 600,
                  }}
                >
                  ข้อมูลการทำงาน
                </h3>

                <p
                  style={{
                    margin: 0,
                    color: "var(--muted)",
                    fontSize: "13px",
                  }}
                >
                  กำหนดแผนกและความเชี่ยวชาญของแพทย์
                </p>
              </div>

              <div style={fieldStyle}>
                <label htmlFor="department" style={labelStyle}>
                  แผนก
                </label>

                <select
                  ref={(element) => registerField("department_id", element)}
                  id="department"
                  value={form.department_id}
                  onChange={(event) =>
                    handleChange("department_id", event.target.value)
                  }
                  disabled={isSubmitting || isUploadingImage}
                  style={getInputValidationStyle("department_id", errorField)}
                >
                  <option value="">-- เลือกแผนก --</option>

                  {departments
                    .filter((department) => department.status === "active")
                    .map((department) => (
                      <option key={department.id} value={department.id}>
                        {department.name}
                      </option>
                    ))}
                </select>
              </div>

              <fieldset
                style={{
                  border:
                    errorField === "specialization_ids"
                      ? "2px solid #dc2626"
                      : "1px solid var(--border)",
                  borderRadius: "8px",
                  padding: "16px",
                  margin: "20px 0 0",
                  boxShadow:
                    errorField === "specialization_ids"
                      ? "0 0 0 3px rgba(220, 38, 38, 0.15)"
                      : "none",
                  transition: "border-color 0.15s ease, box-shadow 0.15s ease",
                }}
              >
                <legend
                  style={{
                    padding: "0 8px",
                    color: "var(--text)",
                    fontSize: "13px",
                    fontWeight: 600,
                  }}
                >
                  ความเชี่ยวชาญ
                </legend>

                {activeSpecializations.length === 0 ? (
                  <p
                    style={{
                      margin: "4px 0",
                      color: "var(--muted)",
                      fontSize: "13px",
                    }}
                  >
                    {form.department_id
                      ? "ไม่พบความเชี่ยวชาญในแผนกนี้"
                      : "กรุณาเลือกแผนกเพื่อแสดงความเชี่ยวชาญ"}
                  </p>
                ) : (
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(3, minmax(0, 1fr))",
                      gap: "10px",
                    }}
                  >
                    {activeSpecializations.map((specialization, index) => {
                      const isChecked = form.specialization_ids.includes(
                        specialization.id,
                      );

                      return (
                        <label
                          key={specialization.id}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "8px",
                            minHeight: "40px",
                            padding: "0 10px",
                            border: isChecked
                              ? "1px solid #176ed1"
                              : "1px solid var(--border)",
                            borderRadius: "7px",
                            background: isChecked
                              ? "rgba(23, 110, 209, 0.06)"
                              : "var(--surface)",
                            color: "var(--text)",
                            fontSize: "13px",
                            cursor: "pointer",
                            boxSizing: "border-box",
                          }}
                        >
                          <input
                            ref={(element) => {
                              if (index === 0) {
                                registerField("specialization_ids", element);
                              }
                            }}
                            type="checkbox"
                            checked={isChecked}
                            onChange={(event) =>
                              handleSpecializationChange(
                                specialization.id,
                                event.target.checked,
                              )
                            }
                            disabled={isSubmitting || isUploadingImage}
                          />

                          <span>{specialization.name}</span>
                        </label>
                      );
                    })}
                  </div>
                )}
              </fieldset>
            </section>

            {/* =========================
                  6. Profile Image
              ========================== */}
            <section
              style={{
                marginBottom: "24px",
              }}
            >
              <div
                style={{
                  marginBottom: "16px",
                }}
              >
                <h3
                  style={{
                    margin: "0 0 4px",
                    color: "var(--text)",
                    fontSize: "15px",
                    fontWeight: 600,
                  }}
                >
                  รูปโปรไฟล์
                </h3>

                <p
                  style={{
                    margin: 0,
                    color: "var(--muted)",
                    fontSize: "13px",
                  }}
                >
                  อัปโหลดรูปโปรไฟล์ของแพทย์
                </p>
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "20px",
                }}
              >
                <div
                  style={{
                    width: "96px",
                    height: "96px",
                    borderRadius: "50%",
                    overflow: "hidden",
                    border: "1px solid var(--border)",
                    background: "var(--surface)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {profileImagePreview ? (
                    <img
                      src={profileImagePreview}
                      alt="ตัวอย่างรูปโปรไฟล์"
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                      }}
                    />
                  ) : (
                    <span
                      style={{
                        color: "var(--muted)",
                        fontSize: "13px",
                      }}
                    >
                      ไม่มีรูป
                    </span>
                  )}
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "8px",
                  }}
                >
                  <label
                    htmlFor="profile-image"
                    className="action-button secondary"
                    style={{
                      width: "fit-content",
                      cursor:
                        isSubmitting || isUploadingImage
                          ? "not-allowed"
                          : "pointer",
                      opacity: isSubmitting || isUploadingImage ? 0.6 : 1,
                    }}
                  >
                    {isUploadingImage ? "กำลังอัปโหลด..." : "เลือกรูปโปรไฟล์"}
                  </label>

                  <input
                    id="profile-image"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={handleProfileImageChange}
                    disabled={isSubmitting || isUploadingImage}
                    style={{
                      display: "none",
                    }}
                  />

                  <span
                    style={{
                      color: "var(--muted)",
                      fontSize: "12px",
                    }}
                  >
                    JPG, PNG หรือ WEBP ขนาดไม่เกิน 5 MB
                  </span>
                </div>
              </div>
            </section>

            {/* =========================
                  Submit
              ========================== */}
            <div
              style={{
                display: "flex",
                justifyContent: "flex-end",
                alignItems: "center",
                gap: "10px",
                marginTop: "24px",
                paddingTop: "20px",
                borderTop: "1px solid var(--border)",
              }}
            >
              <button
                type="button"
                className="action-button secondary"
                disabled={isSubmitting || isUploadingImage}
                onClick={() => navigate("/staff/doctors")}
              >
                ยกเลิก
              </button>

              <button
                type="submit"
                className="action-button primary"
                disabled={isSubmitting || isUploadingImage}
                style={{
                  minWidth: "120px",
                  justifyContent: "center",
                }}
              >
                {isUploadingImage
                  ? "กำลังอัปโหลด..."
                  : isSubmitting
                    ? "กำลังบันทึก..."
                    : "ยืนยัน"}
              </button>
            </div>
          </form>
        </div>
      </section>

      {isSaveSuccessOpen && (
        <div className="doctor-modal-overlay" role="presentation">
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="create-doctor-success-title"
          >
            <div className="doctor-modal-header">
              <div>
                <span className="section-eyebrow">Doctor Management</span>

                <h2 id="create-doctor-success-title">เพิ่มแพทย์สำเร็จ</h2>
              </div>
            </div>

            <div className="doctor-modal-body">
              <p>เพิ่มข้อมูลแพทย์เข้าสู่ระบบเรียบร้อยแล้ว</p>
            </div>

            <div
              className="doctor-modal-actions"
              style={{
                display: "flex",
                flexDirection: "column",
                width: "100%",
              }}
            >
              <button
                type="button"
                className="action-button primary"
                onClick={() => {
                  setIsSaveSuccessOpen(false);
                  navigate("/staff/doctors");
                }}
                style={{
                  width: "100%",
                  justifyContent: "center",
                }}
              >
                ตกลง
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default CreateDoctorPage;
