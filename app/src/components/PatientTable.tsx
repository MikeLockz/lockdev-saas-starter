// FILENAME: src/components/PatientCard.tsx
import type React from "react";
import type { UiPatient } from "@/types/patient";

interface PatientCardProps {
  patient: UiPatient;
}

const PatientCard: React.FC<PatientCardProps> = ({ patient }) => {
  return (
    <div className="rounded-md border p-4 shadow-sm">
      <h2 className="text-lg font-semibold">{patient.fullName}</h2>
      <p className="text-gray-500">MRN: {patient.mrn}</p>
      <div className="mt-2">
        <p>Date of Birth: {patient.dateOfBirth}</p>
        <p>Email: {patient.email}</p>
        <p>Phone: {patient.phone}</p>
        <p>
          Address: {patient.address}, {patient.city}, {patient.state}{" "}
          {patient.zipCode}
        </p>
      </div>
    </div>
  );
};

export default PatientCard;
