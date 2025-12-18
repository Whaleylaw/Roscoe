"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Building2, Phone, Mail, Calendar } from "lucide-react";
import { z } from "zod";
import { ArtifactComponent, ArtifactProps } from "./types";
import { artifactRegistry } from "./registry";

export const medicalProviderSchema = z.object({
  name: z.string().min(1),
  specialty: z.string().optional(),
  facility: z.string().optional(),
  phone: z.string().optional(),
  email: z.string().email().optional(),
  lastVisit: z.string().optional(), // ISO date string
  treatments: z.array(z.string()).optional(),
});

export type MedicalProviderData = z.infer<typeof medicalProviderSchema>;

interface MedicalProviderCardProps extends ArtifactProps {
  data: MedicalProviderData;
}

export function MedicalProviderCard({ data, onAction }: MedicalProviderCardProps) {
  const validated = medicalProviderSchema.parse(data);

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              {validated.name}
            </CardTitle>
            {validated.specialty && (
              <Badge variant="outline" className="mt-2">
                {validated.specialty}
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {validated.facility && (
          <div>
            <p className="text-sm font-medium">Facility</p>
            <p className="text-sm text-muted-foreground">{validated.facility}</p>
          </div>
        )}

        <div className="space-y-2">
          {validated.phone && (
            <div className="flex items-center gap-2">
              <Phone className="h-4 w-4 text-muted-foreground" />
              <a
                href={`tel:${validated.phone}`}
                className="text-sm hover:underline"
                onClick={(e) => {
                  e.preventDefault();
                  onAction?.("call", { phone: validated.phone });
                }}
              >
                {validated.phone}
              </a>
            </div>
          )}
          {validated.email && (
            <div className="flex items-center gap-2">
              <Mail className="h-4 w-4 text-muted-foreground" />
              <a
                href={`mailto:${validated.email}`}
                className="text-sm hover:underline"
              >
                {validated.email}
              </a>
            </div>
          )}
        </div>

        {validated.lastVisit && (
          <div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm">
                Last Visit: {new Date(validated.lastVisit).toLocaleDateString()}
              </span>
            </div>
          </div>
        )}

        {validated.treatments && validated.treatments.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-2">Treatments</p>
            <div className="flex flex-wrap gap-2">
              {validated.treatments.map((treatment, i) => (
                <Badge key={i} variant="secondary">
                  {treatment}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

const medicalProviderArtifact: ArtifactComponent<MedicalProviderCardProps> = {
  id: "medical-provider-card",
  name: "Medical Provider Card",
  description: "Display information about a medical provider, doctor, or healthcare facility involved in a case",
  component: MedicalProviderCard,
  schema: medicalProviderSchema,
  category: "medical",
};

artifactRegistry.register(medicalProviderArtifact);
