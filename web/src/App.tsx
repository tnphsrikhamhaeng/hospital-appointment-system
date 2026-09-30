import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";

import LoginPage from "./features/auth/pages/LoginPage";
import ProtectedRoute from "./features/auth/components/ProtectedRoute";
import DoctorPage from "./features/doctor/pages/DoctorPage";
import MedicalRecordPage from "./features/medical-record/pages/MedicalRecordPage";
import AppointmentPatientPage from "./features/appointment/pages/AppointmentPatientPage";
import DoctorSchedulePage from "./features/doctor/pages/DoctorSchedulePage";
import StaffCheckInPage from "./features/staff/pages/StaffCheckInPage";
import CreateStaffPage from "./features/staff/pages/CreateStaffPage";
import CreateDoctorPage from "./features/doctor/pages/CreateDoctorPage";
import DoctorListPage from "./features/doctor/pages/DoctorListPage";
import EditDoctorPage from "./features/doctor/pages/EditDoctorPage";
import DepartmentManagementPage from "./features/department/pages/DepartmentManagementPage";
import ChangePasswordPage from "./features/profile/pages/ChangePasswordPage";
import DoctorHistoryPage from "./features/medical-record/pages/DoctorHistoryPage";
import DoctorMedicalRecordDetailPage from "./features/medical-record/pages/DoctorMedicalRecordDetailPage";
import StaffDoctorSchedulePage from "./features/staff/pages/StaffDoctorSchedulePage";
import StaffLayout from "./features/staff/layouts/StaffLayout";
import DoctorLayout from "./features/doctor/layouts/DoctorLayout";

function AppRoutes({ location }: { location: ReturnType<typeof useLocation> }) {
  return (
    <Routes location={location}>
      <Route path="/" element={<Navigate to="/login" replace />} />

      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/doctor"
        element={
          <ProtectedRoute allowedRole="doctor">
            <DoctorLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DoctorPage />} />

        <Route path="history" element={<DoctorHistoryPage />} />

        <Route
          path="history/detail"
          element={<DoctorMedicalRecordDetailPage />}
        />

        <Route path="schedule" element={<DoctorSchedulePage />} />

        <Route path="change-password" element={<ChangePasswordPage />} />
      </Route>

      <Route
        path="/medical-record"
        element={
          <ProtectedRoute allowedRole="doctor">
            <DoctorLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<MedicalRecordPage />} />
      </Route>

      <Route
        path="/appointment-patient"
        element={
          <ProtectedRoute allowedRole="doctor">
            <AppointmentPatientPage />
          </ProtectedRoute>
        }
      />

      {/* =========================
          Staff
      ========================== */}

      <Route
        path="/staff"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <StaffLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<StaffCheckInPage />} />

        <Route path="create" element={<CreateStaffPage />} />

        <Route path="doctors" element={<DoctorListPage />} />

        <Route path="doctors/create" element={<CreateDoctorPage />} />

        <Route path="doctors/edit" element={<EditDoctorPage />} />

        <Route path="doctors/schedule" element={<StaffDoctorSchedulePage />} />

        <Route path="departments" element={<DepartmentManagementPage />} />

        <Route
          path="specializations"
          element={<Navigate to="/staff/departments" replace />}
        />

        <Route path="change-password" element={<ChangePasswordPage />} />
      </Route>

      <Route
        path="/staff/check-in"
        element={<Navigate to="/staff" replace />}
      />
    </Routes>
  );
}

function PageTransition() {
  const location = useLocation();

  const [displayLocation, setDisplayLocation] = useState(location);

  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    const currentKey = `${displayLocation.pathname}${displayLocation.search}`;

    const nextKey = `${location.pathname}${location.search}`;

    if (currentKey === nextKey) {
      return;
    }

    setIsTransitioning(true);

    const timer = window.setTimeout(() => {
      setDisplayLocation(location);
      setIsTransitioning(false);
    }, 150);

    return () => {
      window.clearTimeout(timer);
    };
  }, [location, displayLocation.pathname, displayLocation.search]);

  return (
    <div
      className={
        isTransitioning
          ? "page-transition page-transition-changing"
          : "page-transition"
      }
    >
      <AppRoutes location={displayLocation} />
    </div>
  );
}

function App() {
  return <PageTransition />;
}

export default App;
