import { Outlet } from "react-router-dom";
import StaffSidebar from "../component/StaffSidebar";

function StaffLayout() {
  return (
    <div className="staff-page">
      <StaffSidebar />

      <Outlet />
    </div>
  );
}

export default StaffLayout;