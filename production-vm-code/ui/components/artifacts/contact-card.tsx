"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Phone, Mail, MapPin } from "lucide-react";
import { z } from "zod";
import { ArtifactComponent, ArtifactProps } from "./types";
import { artifactRegistry } from "./registry";

// Zod schema for validation
export const contactCardSchema = z.object({
  name: z.string().min(1, "Name is required"),
  role: z.string().optional(),
  email: z.string().email().optional(),
  phone: z.string().optional(),
  address: z.string().optional(),
  avatarUrl: z.string().url().optional(),
  initials: z.string().length(2).optional(),
});

export type ContactCardData = z.infer<typeof contactCardSchema>;

interface ContactCardProps extends ArtifactProps {
  data: ContactCardData;
}

export function ContactCard({ data, onAction }: ContactCardProps) {
  const validated = contactCardSchema.parse(data);
  const initials = validated.initials || validated.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <div className="flex items-center gap-4">
          <Avatar className="h-16 w-16">
            <AvatarImage src={validated.avatarUrl} alt={validated.name} />
            <AvatarFallback>{initials}</AvatarFallback>
          </Avatar>
          <div>
            <CardTitle>{validated.name}</CardTitle>
            {validated.role && (
              <p className="text-sm text-muted-foreground">{validated.role}</p>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        {validated.email && (
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4 text-muted-foreground" />
            <a
              href={`mailto:${validated.email}`}
              className="text-sm hover:underline"
              onClick={(e) => {
                e.preventDefault();
                onAction?.("email", { email: validated.email });
              }}
            >
              {validated.email}
            </a>
          </div>
        )}
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
        {validated.address && (
          <div className="flex items-center gap-2">
            <MapPin className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">{validated.address}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Register component in artifact registry
const contactCardArtifact: ArtifactComponent<ContactCardProps> = {
  id: "contact-card",
  name: "Contact Card",
  description: "Display contact information for a person (attorney, client, witness, etc)",
  component: ContactCard,
  schema: contactCardSchema,
  category: "contact",
};

artifactRegistry.register(contactCardArtifact);
