import {
  useEffect,
  useMemo,
  useState,
  type ChangeEvent,
  type CSSProperties,
  type FormEvent,
} from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import {
  getDoctorById,
  updateDoctor,
  uploadDoctorImage,
  type DoctorResponse,
  type DoctorStatus,
  type DoctorUpdateRequest,
} from "../api/doctorApi";

import {
  getDepartments,
  type DepartmentResponse,
} from "../../department/api/departmentApi";

import {
  getSpecializations,
  type SpecializationResponse,
} from "../../department/api/specializationApi";

import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";

import "../pages/DoctorPage.css";

const inputStyle: CSSProperties = {
  width: "100%",
  padding: "11px 13px",
  border: "1px solid var(--border)",
  borderRadius: "8px",
  background: "var(--surface)",
  color: "var(--text)",
  fontSize: "14px",
  outline: "none",
  boxSizing: "border-box",
};

const fieldStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "7px",
};

const labelStyle: CSSProperties = {
  fontSize: "14px",
  fontWeight: 500,
  color: "var(--text)",
};

const sectionStyle: CSSProperties = {
  border: "1px solid var(--border)",
  borderRadius: "12px",
  padding: "22px",
  background: "var(--surface)",
};

const sectionTitleStyle: CSSProperties = {
  margin: "0 0 18px",
  fontSize: "18px",
  fontWeight: 600,
  color: "var(--text)",
};

const rowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
  gap: "18px",
};

const fullRowStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "1fr",
  gap: "18px",
};

const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

const ALLOWED_IMAGE_TYPES = [
  "image/jpeg",
  "image/png",
  "image/webp",
];

const getPrefaceLabel = (
  preface: DoctorResponse["preface"],
) => {
  switch (preface) {
    case "mr_doctor":
      return "นายแพทย์";

    case "female_doctor":
      return "แพทย์หญิง";

    default:
      return "แพทย์";
  }
};

const getStatusLabel = (status: DoctorStatus) => {
  switch (status) {
    case "active":
      return "ปฏิบัติงาน";

    case "on_leave":
      return "ลา";

    case "resigned":
      return "ลาออก";

    case "retired":
      return "เกษียณ";

    case "inactive":
      return "ปิดใช้งาน";

    default:
      return status;
  }
};

const EditDoctorPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const doctorId = searchParams.get("doctor_id");

  const [doctor, setDoctor] =
    useState<DoctorResponse | null>(null);

  const [departments, setDepartments] = useState<
    DepartmentResponse[]
  >([]);

  const [specializations, setSpecializations] =
    useState<SpecializationResponse[]>([]);

  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] =
    useState<DoctorStatus>("active");

  const [departmentId, setDepartmentId] =
    useState("");

  const [specializationIds, setSpecializationIds] =
    useState<string[]>([]);

  const [profileImageUrl, setProfileImageUrl] =
    useState("");

  const [profileImagePreview, setProfileImagePreview] =
    useState<string | null>(null);

  const [isUploadingImage, setIsUploadingImage] =
    useState(false);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [error, setError] = useState("");

  const [isLogoutOpen, setIsLogoutOpen] =
    useState(false);

  const [isChangePasswordOpen, setIsChangePasswordOpen] =
    useState(false);

  const [isSaveSuccessOpen, setIsSaveSuccessOpen] =
    useState(false);

  useEffect(() => {
    const loadData = async () => {
      if (!doctorId) {
        setError("ไม่พบ doctor_id");
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError("");

        const [
          doctorData,
          departmentData,
          specializationData,
        ] = await Promise.all([
          getDoctorById(doctorId),
          getDepartments(),
          getSpecializations(),
        ]);

        setDoctor(doctorData);
        setDepartments(departmentData);
        setSpecializations(specializationData);

        setFirstName(doctorData.first_name);
        setLastName(doctorData.last_name);
        setPhoneNumber(doctorData.phone_number);
        setEmail(doctorData.email);
        setStatus(doctorData.status);
        setDepartmentId(doctorData.department.id);

        setSpecializationIds(
          doctorData.specializations.map(
            (item) => item.id,
          ),
        );

        const imageUrl =
          doctorData.profile_image_url ?? "";

        setProfileImageUrl(imageUrl);
        setProfileImagePreview(
          imageUrl || null,
        );
      } catch (err: any) {
        setError(
          err?.response?.data?.detail ||
            err?.message ||
            "ไม่สามารถโหลดข้อมูล Doctor ได้",
        );
      } finally {
        setLoading(false);
      }
    };

    void loadData();
  }, [doctorId]);

  const filteredSpecializations = useMemo(() => {
    if (!departmentId) {
      return [];
    }

    return specializations.filter(
      (item) =>
        item.department_id === departmentId &&
        item.status === "active",
    );
  }, [departmentId, specializations]);

  const handleDepartmentChange = (
    value: string,
  ) => {
    setDepartmentId(value);

    setSpecializationIds((current) =>
      current.filter((id) => {
        const specialization =
          specializations.find(
            (item) => item.id === id,
          );

        return (
          specialization?.department_id === value
        );
      }),
    );
  };

  const handleSpecializationChange = (
    id: string,
  ) => {
    setSpecializationIds((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    );
  };

  const handleProfileImageChange = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setError("");

    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
      setError(
        "รองรับเฉพาะไฟล์ JPG, PNG และ WEBP",
      );
      event.target.value = "";
      return;
    }

    if (file.size > MAX_IMAGE_SIZE) {
      setError(
        "ขนาดรูปภาพต้องไม่เกิน 5 MB",
      );
      event.target.value = "";
      return;
    }

    const previousPreview =
      profileImagePreview;

    const previewUrl =
      URL.createObjectURL(file);

    setProfileImagePreview(previewUrl);
    setIsUploadingImage(true);

    try {
      const result =
        await uploadDoctorImage(file);

      setProfileImageUrl(
        result.image_url,
      );

      if (
        previousPreview &&
        previousPreview.startsWith("blob:")
      ) {
        URL.revokeObjectURL(
          previousPreview,
        );
      }
    } catch (error: unknown) {
      URL.revokeObjectURL(previewUrl);

      setProfileImagePreview(
        profileImageUrl || null,
      );

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

        setError(
          response?.data?.detail ??
            "ไม่สามารถอัปโหลดรูปโปรไฟล์ได้",
        );
      } else {
        setError(
          "ไม่สามารถอัปโหลดรูปโปรไฟล์ได้",
        );
      }
    } finally {
      setIsUploadingImage(false);
      event.target.value = "";
    }
  };

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault();

    if (!doctorId) {
      setError("ไม่พบ doctor_id");
      return;
    }

    if (isUploadingImage) {
      setError(
        "กรุณารอให้การอัปโหลดรูปโปรไฟล์เสร็จสิ้น",
      );
      return;
    }

    if (
      !firstName.trim() ||
      !lastName.trim()
    ) {
      setError("กรุณากรอกชื่อและนามสกุล");
      return;
    }

    if (!departmentId) {
      setError("กรุณาเลือกแผนก");
      return;
    }

    if (specializationIds.length === 0) {
      setError(
        "กรุณาเลือกความเชี่ยวชาญอย่างน้อย 1 รายการ",
      );
      return;
    }

    try {
      setSaving(true);
      setError("");

      const data: DoctorUpdateRequest = {
        profile_image_url: profileImageUrl.trim()
          ? profileImageUrl.trim()
          : null,
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        phone_number: phoneNumber.trim(),
        email: email.trim(),
        status,
        department_id: departmentId,
        specialization_ids: specializationIds,
      };

      const updatedDoctor =
        await updateDoctor(doctorId, data);

      setDoctor(updatedDoctor);

      setFirstName(updatedDoctor.first_name);
      setLastName(updatedDoctor.last_name);
      setPhoneNumber(updatedDoctor.phone_number);
      setEmail(updatedDoctor.email);
      setStatus(updatedDoctor.status);

      setDepartmentId(
        updatedDoctor.department.id,
      );

      setSpecializationIds(
        updatedDoctor.specializations.map(
          (item) => item.id,
        ),
      );

      const updatedImageUrl =
        updatedDoctor.profile_image_url ?? "";

      setProfileImageUrl(
        updatedImageUrl,
      );

      if (
        profileImagePreview &&
        profileImagePreview.startsWith("blob:")
      ) {
        URL.revokeObjectURL(
          profileImagePreview,
        );
      }

      setProfileImagePreview(
        updatedImageUrl || null,
      );

      setIsSaveSuccessOpen(true);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "ไม่สามารถแก้ไขข้อมูล Doctor ได้",
      );
    } finally {
      setSaving(false);
    }
  };

  const handleOpenLogout = () => {
    setIsLogoutOpen(true);
  };

  const handleCloseLogout = () => {
    setIsLogoutOpen(false);
  };

  const handleConfirmLogout = () => {
    logout();
    setIsLogoutOpen(false);

    navigate("/login", {
      replace: true,
    });
  };

  const handleOpenChangePassword = () => {
    setIsChangePasswordOpen(true);
  };

  const handleCloseChangePassword = () => {
    setIsChangePasswordOpen(false);
  };

  const handleCloseSaveSuccess = () => {
    setIsSaveSuccessOpen(false);

    navigate("/staff/doctors", {
      replace: true,
    });
  };

  if (loading) {
    return (
      <main className="doctor-page">
        <aside className="doctor-sidebar">
          <div className="sidebar-brand">
            <img
              src="/image/logo/LOGO.png"
              alt="CareFlow"
              className="sidebar-logo"
            />

            <div>
              <strong>CareFlow</strong>

              <span>
                ระบบบริหารจัดการโรงพยาบาล
              </span>
            </div>
          </div>

          <div className="sidebar-role">
            <span>ระบบสำหรับ Staff</span>
          </div>

          <nav className="sidebar-nav">
            <button
              type="button"
              className="sidebar-nav-item"
              onClick={() =>
                navigate("/staff")
              }
            >
              <span className="nav-icon">
                ⌂
              </span>

              <span>เช็คอินผู้ป่วย</span>
            </button>

            <button
              type="button"
              className="sidebar-nav-item active"
              onClick={() =>
                navigate("/staff/doctors")
              }
            >
              <span className="nav-icon">
                ♙
              </span>

              <span>จัดการแพทย์</span>
            </button>

            <button
              type="button"
              className="sidebar-nav-item"
            >
              <span className="nav-icon">
                ▤
              </span>

              <span>จัดการ Staff</span>
            </button>

            <button
              type="button"
              className="sidebar-nav-item"
              onClick={() =>
                navigate("/staff/departments")
              }
            >
              <span className="nav-icon">
                ▦
              </span>

              <span>จัดการแผนก</span>
            </button>
          </nav>

          <div className="sidebar-bottom">
            <button
              type="button"
              className="sidebar-bottom-item"
              onClick={
                handleOpenChangePassword
              }
            >
              <span className="nav-icon">
                ⚿
              </span>

              <span>เปลี่ยนรหัสผ่าน</span>
            </button>

            <button
              type="button"
              className="sidebar-bottom-item logout-item"
              onClick={handleOpenLogout}
            >
              <span className="nav-icon">
                ↪
              </span>

              <span>ออกจากระบบ</span>
            </button>
          </div>
        </aside>

        <section className="doctor-content">
          <div className="doctor-card">
            <p>
              กำลังโหลดข้อมูล Doctor...
            </p>
          </div>
        </section>
      </main>
    );
  }

  if (!doctor) {
    return (
      <main className="doctor-page">
        <aside className="doctor-sidebar">
          <div className="sidebar-brand">
            <img
              src="/image/logo/LOGO.png"
              alt="CareFlow"
              className="sidebar-logo"
            />

            <div>
              <strong>CareFlow</strong>

              <span>
                ระบบบริหารจัดการโรงพยาบาล
              </span>
            </div>
          </div>

          <div className="sidebar-role">
            <span>ระบบสำหรับ Staff</span>
          </div>

          <nav className="sidebar-nav">
            <button
              type="button"
              className="sidebar-nav-item"
              onClick={() =>
                navigate("/staff")
              }
            >
              <span className="nav-icon">
                ⌂
              </span>

              <span>เช็คอินผู้ป่วย</span>
            </button>

            <button
              type="button"
              className="sidebar-nav-item active"
              onClick={() =>
                navigate("/staff/doctors")
              }
            >
              <span className="nav-icon">
                ♙
              </span>

              <span>จัดการแพทย์</span>
            </button>

            <button
              type="button"
              className="sidebar-nav-item"
            >
              <span className="nav-icon">
                ▤
              </span>

              <span>จัดการ Staff</span>
            </button>

            <button
              type="button"
              className="sidebar-nav-item"
              onClick={() =>
                navigate("/staff/departments")
              }
            >
              <span className="nav-icon">
                ▦
              </span>

              <span>จัดการแผนก</span>
            </button>
          </nav>

          <div className="sidebar-bottom">
            <button
              type="button"
              className="sidebar-bottom-item"
              onClick={
                handleOpenChangePassword
              }
            >
              <span className="nav-icon">
                ⚿
              </span>

              <span>เปลี่ยนรหัสผ่าน</span>
            </button>

            <button
              type="button"
              className="sidebar-bottom-item logout-item"
              onClick={handleOpenLogout}
            >
              <span className="nav-icon">
                ↪
              </span>

              <span>ออกจากระบบ</span>
            </button>
          </div>
        </aside>

        <section className="doctor-content">
          <div className="doctor-card">
            <p>
              {error ||
                "ไม่พบข้อมูล Doctor"}
            </p>

            <button
              type="button"
              className="action-button secondary"
              onClick={() =>
                navigate("/staff/doctors")
              }
            >
              กลับรายการ Doctor
            </button>
          </div>
        </section>

        <ChangePasswordModal
          isOpen={
            isChangePasswordOpen
          }
          onClose={
            handleCloseChangePassword
          }
        />
      </main>
    );
  }

  return (
    <main className="doctor-page">
      {/* =========================
          Sidebar
      ========================== */}
      <aside className="doctor-sidebar">
        <div className="sidebar-brand">
          <img
            src="/image/logo/LOGO.png"
            alt="CareFlow"
            className="sidebar-logo"
          />

          <div>
            <strong>CareFlow</strong>

            <span>
              ระบบบริหารจัดการโรงพยาบาล
            </span>
          </div>
        </div>

        <div className="sidebar-role">
          <span>ระบบสำหรับ Staff</span>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/staff")
            }
          >
            <span className="nav-icon">
              ⌂
            </span>

            <span>เช็คอินผู้ป่วย</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item active"
            onClick={() =>
              navigate("/staff/doctors")
            }
          >
            <span className="nav-icon">
              ♙
            </span>

            <span>จัดการแพทย์</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
          >
            <span className="nav-icon">
              ▤
            </span>

            <span>จัดการเจ้าหน้าที่</span>
          </button>

          <button
            type="button"
            className="sidebar-nav-item"
            onClick={() =>
              navigate("/staff/departments")
            }
          >
            <span className="nav-icon">
              ▦
            </span>

            <span>จัดการแผนก</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button
            type="button"
            className="sidebar-bottom-item"
            onClick={
              handleOpenChangePassword
            }
          >
            <span className="nav-icon">
              ⚿
            </span>

            <span>เปลี่ยนรหัสผ่าน</span>
          </button>

          <button
            type="button"
            className="sidebar-bottom-item logout-item"
            onClick={handleOpenLogout}
          >
            <span className="nav-icon">
              ↪
            </span>

            <span>ออกจากระบบ</span>
          </button>
        </div>
      </aside>

      {/* =========================
          Main Content
      ========================== */}
      <section className="doctor-content">
        <header className="doctor-header">
          <div>
            <span className="page-eyebrow">
              CareFlow Hospital System
            </span>

            <h1>แก้ไข Doctor</h1>

            <p>
              แก้ไขข้อมูลของแพทย์
            </p>
          </div>
        </header>

        {error && (
          <div
            className="doctor-alert"
            role="alert"
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "18px",
            }}
          >
            {/* ข้อมูลบัญชี */}
            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>
                ข้อมูลบัญชี
              </h2>

              <div style={rowStyle}>
                <div style={fieldStyle}>
                  <label
                    htmlFor="doctor-id"
                    style={labelStyle}
                  >
                    Doctor ID
                  </label>

                  <input
                    id="doctor-id"
                    value={doctor.id}
                    readOnly
                    style={{
                      ...inputStyle,
                      background:
                        "var(--bg)",
                      color:
                        "var(--muted)",
                      cursor: "default",
                    }}
                  />
                </div>

                <div style={fieldStyle}>
                  <label
                    htmlFor="doctor-preface"
                    style={labelStyle}
                  >
                    คำนำหน้า
                  </label>

                  <input
                    id="doctor-preface"
                    value={getPrefaceLabel(
                      doctor.preface,
                    )}
                    readOnly
                    style={{
                      ...inputStyle,
                      background:
                        "var(--bg)",
                      color:
                        "var(--muted)",
                      cursor: "default",
                    }}
                  />
                </div>
              </div>
            </section>

            {/* ข้อมูลส่วนตัว */}
            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>
                ข้อมูลส่วนตัว
              </h2>

              <div style={rowStyle}>
                <div style={fieldStyle}>
                  <label
                    htmlFor="first-name"
                    style={labelStyle}
                  >
                    ชื่อ
                  </label>

                  <input
                    id="first-name"
                    type="text"
                    value={firstName}
                    onChange={(event) =>
                      setFirstName(
                        event.target.value,
                      )
                    }
                    disabled={
                      saving ||
                      isUploadingImage
                    }
                    style={inputStyle}
                  />
                </div>

                <div style={fieldStyle}>
                  <label
                    htmlFor="last-name"
                    style={labelStyle}
                  >
                    นามสกุล
                  </label>

                  <input
                    id="last-name"
                    type="text"
                    value={lastName}
                    onChange={(event) =>
                      setLastName(
                        event.target.value,
                      )
                    }
                    disabled={
                      saving ||
                      isUploadingImage
                    }
                    style={inputStyle}
                  />
                </div>
              </div>
            </section>

            {/* ข้อมูลวิชาชีพ */}
            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>
                ข้อมูลวิชาชีพ
              </h2>

              <div style={fullRowStyle}>
                <div style={fieldStyle}>
                  <label
                    htmlFor="license-number"
                    style={labelStyle}
                  >
                    เลขใบประกอบวิชาชีพ
                  </label>

                  <input
                    id="license-number"
                    value={
                      doctor.license_number
                    }
                    readOnly
                    style={{
                      ...inputStyle,
                      background:
                        "var(--bg)",
                      color:
                        "var(--muted)",
                      cursor: "default",
                    }}
                  />
                </div>
              </div>
            </section>

            {/* ข้อมูลติดต่อ */}
            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>
                ข้อมูลติดต่อ
              </h2>

              <div style={rowStyle}>
                <div style={fieldStyle}>
                  <label
                    htmlFor="phone-number"
                    style={labelStyle}
                  >
                    เบอร์โทรศัพท์
                  </label>

                  <input
                    id="phone-number"
                    type="tel"
                    value={phoneNumber}
                    onChange={(event) =>
                      setPhoneNumber(
                        event.target.value,
                      )
                    }
                    disabled={
                      saving ||
                      isUploadingImage
                    }
                    style={inputStyle}
                  />
                </div>

                <div style={fieldStyle}>
                  <label
                    htmlFor="email"
                    style={labelStyle}
                  >
                    Email
                  </label>

                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(event) =>
                      setEmail(
                        event.target.value,
                      )
                    }
                    disabled={
                      saving ||
                      isUploadingImage
                    }
                    style={inputStyle}
                  />
                </div>
              </div>
            </section>

            {/* ข้อมูลการทำงาน */}
            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>
                ข้อมูลการทำงาน
              </h2>

              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "18px",
                }}
              >
                <div style={fieldStyle}>
                  <label
                    htmlFor="department"
                    style={labelStyle}
                  >
                    แผนก
                  </label>

                  <select
                    id="department"
                    value={departmentId}
                    onChange={(event) =>
                      handleDepartmentChange(
                        event.target.value,
                      )
                    }
                    disabled={
                      saving ||
                      isUploadingImage
                    }
                    style={inputStyle}
                  >
                    <option value="">
                      เลือกแผนก
                    </option>

                    {departments
                      .filter(
                        (department) =>
                          department.status ===
                          "active",
                      )
                      .map((department) => (
                        <option
                          key={
                            department.id
                          }
                          value={
                            department.id
                          }
                        >
                          {department.name}
                        </option>
                      ))}
                  </select>
                </div>

                <div style={fieldStyle}>
                  <label style={labelStyle}>
                    ความเชี่ยวชาญ
                  </label>

                  {filteredSpecializations.length ===
                  0 ? (
                    <div
                      style={{
                        padding:
                          "12px 13px",
                        border:
                          "1px solid var(--border)",
                        borderRadius:
                          "8px",
                        color:
                          "var(--muted)",
                        fontSize: "14px",
                        background:
                          "var(--bg)",
                      }}
                    >
                      กรุณาเลือกแผนกก่อน
                    </div>
                  ) : (
                    <div
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "repeat(2, minmax(0, 1fr))",
                        gap: "10px",
                      }}
                    >
                      {filteredSpecializations.map(
                        (specialization) => (
                          <label
                            key={
                              specialization.id
                            }
                            style={{
                              display:
                                "flex",
                              alignItems:
                                "center",
                              gap: "9px",
                              padding:
                                "11px 12px",
                              border:
                                "1px solid var(--border)",
                              borderRadius:
                                "8px",
                              cursor:
                                saving ||
                                isUploadingImage
                                  ? "default"
                                  : "pointer",
                              fontSize:
                                "14px",
                              color:
                                "var(--text)",
                              background:
                                specializationIds.includes(
                                  specialization.id,
                                )
                                  ? "var(--bg)"
                                  : "var(--surface)",
                            }}
                          >
                            <input
                              type="checkbox"
                              checked={specializationIds.includes(
                                specialization.id,
                              )}
                              onChange={() =>
                                handleSpecializationChange(
                                  specialization.id,
                                )
                              }
                              disabled={
                                saving ||
                                isUploadingImage
                              }
                            />

                            <span>
                              {
                                specialization.name
                              }
                            </span>
                          </label>
                        ),
                      )}
                    </div>
                  )}
                </div>

                <div style={fieldStyle}>
                  <label
                    htmlFor="status"
                    style={labelStyle}
                  >
                    สถานะ
                  </label>

                  <select
                    id="status"
                    value={status}
                    onChange={(event) =>
                      setStatus(
                        event.target
                          .value as DoctorStatus,
                      )
                    }
                    disabled={
                      saving ||
                      isUploadingImage
                    }
                    style={inputStyle}
                  >
                    <option value="active">
                      ปฏิบัติงาน
                    </option>

                    <option value="on_leave">
                      ลา
                    </option>

                    <option value="resigned">
                      ลาออก
                    </option>

                    <option value="retired">
                      เกษียณ
                    </option>
                  </select>

                  <span
                    style={{
                      fontSize: "12px",
                      color:
                        "var(--muted)",
                    }}
                  >
                    สถานะปัจจุบัน:{" "}
                    {getStatusLabel(
                      doctor.status,
                    )}
                  </span>
                </div>
              </div>
            </section>

            {/* รูปโปรไฟล์ */}
            <section style={sectionStyle}>
              <h2 style={sectionTitleStyle}>
                รูปโปรไฟล์
              </h2>

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
                    border:
                      "1px solid var(--border)",
                    background:
                      "var(--bg)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  {profileImagePreview ? (
                    <img
                      src={
                        profileImagePreview
                      }
                      alt="รูปโปรไฟล์ Doctor"
                      style={{
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                      }}
                      onError={() => {
                        setProfileImagePreview(
                          null,
                        );
                      }}
                    />
                  ) : (
                    <span
                      style={{
                        color:
                          "var(--muted)",
                        fontSize:
                          "13px",
                      }}
                    >
                      ไม่มีรูป
                    </span>
                  )}
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection:
                      "column",
                    gap: "8px",
                  }}
                >
                  <label
                    htmlFor="profile-image"
                    className="action-button secondary"
                    style={{
                      width:
                        "fit-content",
                      cursor:
                        saving ||
                        isUploadingImage
                          ? "not-allowed"
                          : "pointer",
                      opacity:
                        saving ||
                        isUploadingImage
                          ? 0.6
                          : 1,
                    }}
                  >
                    {isUploadingImage
                      ? "กำลังอัปโหลด..."
                      : "เปลี่ยนรูปโปรไฟล์"}
                  </label>

                  <input
                    id="profile-image"
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={
                      handleProfileImageChange
                    }
                    disabled={
                      saving ||
                      isUploadingImage
                    }
                    style={{
                      display: "none",
                    }}
                  />

                  <span
                    style={{
                      color:
                        "var(--muted)",
                      fontSize: "12px",
                    }}
                  >
                    JPG, PNG หรือ WEBP ขนาดไม่เกิน 5 MB
                  </span>
                </div>
              </div>
            </section>

            {/* ปุ่ม */}
            <div
              style={{
                display: "flex",
                justifyContent:
                  "flex-end",
                gap: "10px",
                paddingTop: "4px",
              }}
            >
              <button
                type="button"
                className="action-button secondary"
                onClick={() =>
                  navigate(
                    "/staff/doctors",
                  )
                }
                disabled={
                  saving ||
                  isUploadingImage
                }
              >
                ยกเลิก
              </button>

              <button
                type="submit"
                className="action-button primary"
                disabled={
                  saving ||
                  isUploadingImage
                }
              >
                {isUploadingImage
                  ? "กำลังอัปโหลด..."
                  : saving
                    ? "กำลังบันทึก..."
                    : "ยืนยัน"}
              </button>
            </div>
          </div>
        </form>
      </section>

      {/* =========================
          Save Success Modal
      ========================== */}
      {isSaveSuccessOpen && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="save-success-modal-title"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="doctor-modal-icon success">
              ✓
            </div>

            <h2 id="save-success-modal-title">
              บันทึกการแก้ไขสำเร็จ
            </h2>

            <p>
              ข้อมูล Doctor ถูกแก้ไขและบันทึกเรียบร้อยแล้ว
            </p>

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
                onClick={
                  handleCloseSaveSuccess
                }
                style={{
                  width: "100%",
                  justifyContent:
                    "center",
                }}
              >
                ตกลง
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================
          Logout Modal
      ========================== */}
      {isLogoutOpen && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={handleCloseLogout}
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-modal-title"
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <div className="doctor-modal-icon warning">
              ↪
            </div>

            <h2 id="logout-modal-title">
              ยืนยันการออกจากระบบ
            </h2>

            <p>
              คุณต้องการออกจากระบบใช่หรือไม่?
            </p>

            <div className="doctor-modal-actions">
              <button
                type="button"
                className="action-button secondary"
                onClick={
                  handleCloseLogout
                }
              >
                ยกเลิก
              </button>

              <button
                type="button"
                className="action-button danger"
                onClick={
                  handleConfirmLogout
                }
              >
                ยืนยัน
              </button>
            </div>
          </div>
        </div>
      )}

      {/* =========================
          Change Password Modal
      ========================== */}
      <ChangePasswordModal
        isOpen={
          isChangePasswordOpen
        }
        onClose={
          handleCloseChangePassword
        }
      />
    </main>
  );
};

export default EditDoctorPage;