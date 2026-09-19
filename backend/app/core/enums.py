from enum import Enum


class UserRoleEnum(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    HOSPITAL_STAFF = "hospital_staff"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    
class DoctorPrefaceEnum(str, Enum):
    MR_DOCTOR = "mr_doctor"
    FEMALE_DOCTOR = "female_doctor"
    
class DoctorStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    RESIGNED = "resigned"
    RETIRED = "retired"
    
class DepartmentStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class SpecializationStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    
class AppointmentStatusEnum(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    IN_PROGRESS = "in_progress"
    NO_SHOW = "no_show"
    
class WeekdayEnum(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"
    
class NotificationTypeEnum(str, Enum):
    APPOINTMENT_CONFIRMED = "appointment_confirmed"
    REMINDER_3_DAYS = "reminder_3_days"
    REMINDER_1_DAY = "reminder_1_day"
    REMINDER_30_MINUTES = "reminder_30_minutes"
    READY_FOR_CONSULTATION = "ready_for_consultation"
    CONSULTATION_DELAYED = "consultation_delayed"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    APPOINTMENT_RESCHEDULED = "appointment_rescheduled"
    
class NotificationStatusEnum(str, Enum):
    SENT = "sent"
    FAILED = "failed"
    READ = "read"
    
class DevicePlatformEnum(str, Enum):
    ANDROID = "android"
    IOS = "ios"