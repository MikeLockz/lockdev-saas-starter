import type { NextApiRequest, NextApiResponse } from "next";
import { prisma } from "@/lib/prisma";
import type { UiPatient } from "@/types/patient";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<UiPatient[] | { message: string }>,
) {
  if (req.method === "GET") {
    try {
      const patients = await prisma.patient.findMany();

      const uiPatients: UiPatient[] = patients.map((patient) => {
        return {
          id: patient.id,
          organizationId: patient.organizationId,
          fullName: `${patient.firstName} ${patient.lastName}`,
          dateOfBirth: patient.dateOfBirth
            ? new Date(patient.dateOfBirth).toLocaleDateString("en-US")
            : "",
          mrn: patient.mrn || "",
          email: patient.email || "",
          phone: patient.phone || "",
          address: patient.address || "",
          city: patient.city || "",
          state: patient.state || "",
          zipCode: patient.zipCode || "",
        };
      });

      res.status(200).json(uiPatients);
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: "Failed to fetch patients" });
    }
  } else {
    res.status(405).json({ message: "Method Not Allowed" });
  }
}
