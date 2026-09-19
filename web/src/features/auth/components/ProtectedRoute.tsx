import { useEffect, useState, type ReactNode } from "react";
import { Navigate } from "react-router-dom";

import {
  getCurrentUser,
  isAuthenticated,
} from "../authService";
import type { UserRole } from "../api/profileApi";

interface ProtectedRouteProps {
  allowedRole: UserRole;
  children: ReactNode;
}

function ProtectedRoute({
  allowedRole,
  children,
}: ProtectedRouteProps) {
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthorized, setIsAuthorized] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const checkAuthentication = async () => {
      if (!isAuthenticated()) {
        if (isMounted) {
          setIsChecking(false);
        }
        return;
      }

      try {
        const profile = await getCurrentUser();

        if (isMounted) {
          setIsAuthorized(profile.role === allowedRole);
        }
      } catch {
        sessionStorage.removeItem("access_token");

        if (isMounted) {
          setIsAuthorized(false);
        }
      } finally {
        if (isMounted) {
          setIsChecking(false);
        }
      }
    };

    void checkAuthentication();

    return () => {
      isMounted = false;
    };
  }, [allowedRole]);

  if (isChecking) {
    return null;
  }

  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (!isAuthorized) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default ProtectedRoute;