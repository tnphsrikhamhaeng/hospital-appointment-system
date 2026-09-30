import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { logout } from "../../auth/api/authApi";
import ChangePasswordModal from "../../profile/components/ChangePasswordModal";
import { getProfile, type ProfileResponse } from "../../auth/api/profileApi";

function DoctorSidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const [profile, setProfile] = useState<ProfileResponse | null>(null);

  const [isLogoutOpen, setIsLogoutOpen] = useState(false);

  const [isChangePasswordOpen, setIsChangePasswordOpen] = useState(false);

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await getProfile();
        setProfile(data);
      } catch (error) {
        console.error("Failed to load profile:", error);
      }
    };

    loadProfile();
  }, []);

  const handleConfirmLogout = () => {
    logout();
    setIsLogoutOpen(false);
    navigate("/login", { replace: true });
  };

  const isActive = (path: string) => {
    if (path === "/doctor" && location.pathname === "/medical-record") {
      return true;
    }

    if (path === "/doctor/history") {
      return (
        location.pathname === "/doctor/history" ||
        location.pathname.startsWith("/doctor/history/")
      );
    }

    return location.pathname === path;
  };

  return (
    <>
      <aside className="doctor-sidebar">
        <div className="sidebar-brand">
          <img
            src="/image/logo/LOGO.png"
            alt="CareFlow"
            className="sidebar-logo"
          />

          <div>
            <strong>CareFlow</strong>

            <span>ระบบบริหารจัดการโรงพยาบาล</span>
          </div>
        </div>

        {/* ชื่อผู้ใช้งาน */}
        {profile && (
          <div className="sidebar-user">
            {profile.first_name} {profile.last_name}
          </div>
        )}

        <div className="sidebar-role">
          <span>ระบบสำหรับแพทย์</span>
        </div>

        <nav className="sidebar-nav">
          <button
            type="button"
            className={`sidebar-nav-item ${
              isActive("/doctor") ? "active" : ""
            }`}
            onClick={() => navigate("/doctor")}
          >
            <span className="nav-icon">⌂</span>

            <span>หน้าหลัก</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${
              isActive("/doctor/history") ? "active" : ""
            }`}
            onClick={() => navigate("/doctor/history")}
          >
            <span className="nav-icon">▤</span>

            <span>ประวัติการรักษา</span>
          </button>

          <button
            type="button"
            className={`sidebar-nav-item ${
              isActive("/doctor/schedule") ? "active" : ""
            }`}
            onClick={() => navigate("/doctor/schedule")}
          >
            <span className="nav-icon">▦</span>

            <span>ตารางนัดหมาย</span>
          </button>
        </nav>

        <div className="sidebar-bottom">
          <button
            type="button"
            className="sidebar-bottom-item"
            onClick={() => setIsChangePasswordOpen(true)}
          >
            <span className="nav-icon">⚿</span>

            <span>เปลี่ยนรหัสผ่าน</span>
          </button>

          <button
            type="button"
            className="sidebar-bottom-item logout-item"
            onClick={() => setIsLogoutOpen(true)}
          >
            <span className="nav-icon">↪</span>

            <span>ออกจากระบบ</span>
          </button>
        </div>
      </aside>

      {/* Logout Confirmation Modal */}
      {isLogoutOpen && (
        <div
          className="doctor-modal-overlay"
          role="presentation"
          onClick={() => setIsLogoutOpen(false)}
        >
          <div
            className="doctor-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="logout-modal-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="doctor-modal-icon warning">↪</div>

            <h2 id="logout-modal-title">ยืนยันการออกจากระบบ</h2>

            <p>คุณต้องการออกจากระบบใช่หรือไม่?</p>

            <div className="doctor-modal-actions">
              <button
                type="button"
                className="action-button secondary"
                onClick={() => setIsLogoutOpen(false)}
              >
                ยกเลิก
              </button>

              <button
                type="button"
                className="action-button danger"
                onClick={handleConfirmLogout}
              >
                ยืนยัน
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Change Password Modal */}
      <ChangePasswordModal
        isOpen={isChangePasswordOpen}
        onClose={() => setIsChangePasswordOpen(false)}
      />
    </>
  );
}

export default DoctorSidebar;
