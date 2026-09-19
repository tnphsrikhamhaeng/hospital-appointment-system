import {
  Navigate,
  Route,
  Routes,
  useLocation,
} from "react-router-dom";
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

function AppRoutes({
  location,
}: {
  location: ReturnType<typeof useLocation>;
}) {
  return (
    <Routes location={location}>
      <Route
        path="/"
        element={<Navigate to="/login" replace />}
      />

      <Route
        path="/login"
        element={<LoginPage />}
      />

      <Route
        path="/doctor"
        element={
          <ProtectedRoute allowedRole="doctor">
            <DoctorPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/doctor/history"
        element={
          <ProtectedRoute allowedRole="doctor">
            <DoctorHistoryPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/doctor/history/detail"
        element={
          <ProtectedRoute allowedRole="doctor">
            <DoctorMedicalRecordDetailPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/doctor/schedule"
        element={
          <ProtectedRoute allowedRole="doctor">
            <DoctorSchedulePage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/doctor/change-password"
        element={
          <ProtectedRoute allowedRole="doctor">
            <ChangePasswordPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/medical-record"
        element={
          <ProtectedRoute allowedRole="doctor">
            <MedicalRecordPage />
          </ProtectedRoute>
        }
      />

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
            <StaffCheckInPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/staff/check-in"
        element={
          <Navigate to="/staff" replace />
        }
      />

      <Route
        path="/staff/create"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <CreateStaffPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/staff/doctors/create"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <CreateDoctorPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/staff/doctors"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <DoctorListPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/staff/doctors/edit"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <EditDoctorPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/staff/doctors/schedule"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <StaffDoctorSchedulePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/staff/departments"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <DepartmentManagementPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/staff/specializations"
        element={
          <Navigate to="/staff/departments" replace />
        }
      />

      <Route
        path="/staff/change-password"
        element={
          <ProtectedRoute allowedRole="hospital_staff">
            <ChangePasswordPage />
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function PageTransition() {
  const location = useLocation();

  const [displayLocation, setDisplayLocation] =
    useState(location);

  const [isTransitioning, setIsTransitioning] =
    useState(false);

  useEffect(() => {
    const currentKey =
      `${displayLocation.pathname}${displayLocation.search}`;

    const nextKey =
      `${location.pathname}${location.search}`;

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
  }, [
    location,
    displayLocation.pathname,
    displayLocation.search,
  ]);

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