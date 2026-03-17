export type StudentStatus = "normal" | "warning" | "suspicious";

export interface Student {
  id: string;
  name: string;
  exam: string;
  status: StudentStatus;
  connection: "Excellent" | "Good" | "Fair" | "Poor";
}

export interface Alert {
  id: string;
  studentId: string;
  type: "multiple_faces" | "phone_detected" | "left_screen" | "background_voice";
  message: string;
  severity: "low" | "medium" | "high";
  timestamp: string;
}

export interface ExamReport {
  id: string;
  studentName: string;
  exam: string;
  alertsCount: number;
  uploadStatus: "Pending" | "Processing" | "Completed" | "Failed";
}

