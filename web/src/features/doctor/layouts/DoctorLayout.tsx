import { Outlet } from "react-router-dom";
import DoctorSidebar from "../component/DoctorSidebar";
import "./DoctorLayout.css";



function DoctorLayout() {
  return (
    <div className="doctor-page">
      <DoctorSidebar />
      <Outlet />
    </div>
  );
}

export default DoctorLayout;