// FILENAME: src/types/patient.ts

export interface DbPatient {
  id: string;
  organizationId: string;
  firstName: string;
  lastName: string;
  dateOfBirth: Date | null;
  mrn: string | null; // Medical Record Number
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  zipCode: string | null;
  createdAt: Date;
  updatedAt: Date;
  deletedAt: Date | null;
}

export interface UiPatient {
  id: string;
  organizationId: string;
  fullName: string;
  dateOfBirth: string; // Format: MM/DD/YYYY
  mrn: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
}
