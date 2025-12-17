"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Phone, Mail, DollarSign } from "lucide-react";
import { z } from "zod";
import { ArtifactComponent, ArtifactProps } from "./types";
import { artifactRegistry } from "./registry";

export const insuranceCardSchema = z.object({
  carrier: z.string().min(1),
  policyNumber: z.string().optional(),
  claimNumber: z.string().optional(),
  adjuster: z.string().optional(),
  adjusterPhone: z.string().optional(),
  adjusterEmail: z.string().email().optional(),
  policyLimits: z.string().optional(),
  status: z.enum(["active", "pending", "denied", "settled"]).optional(),
  coverage: z.array(z.string()).optional(),
});

export type InsuranceCardData = z.infer<typeof insuranceCardSchema>;

interface InsuranceCardProps extends ArtifactProps {
  data: InsuranceCardData;
}

const statusColors = {
  active: "bg-green-500",
  pending: "bg-yellow-500",
  denied: "bg-red-500",
  settled: "bg-blue-500",
};

export function InsuranceCard({ data, onAction }: InsuranceCardProps) {
  const validated = insuranceCardSchema.parse(data);

  return (
    <Card className="w-full max-w-md">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            {validated.carrier}
          </CardTitle>
          {validated.status && (
            <Badge variant="outline" className="capitalize">
              <div className={`w-2 h-2 rounded-full ${statusColors[validated.status]} mr-2`} />
              {validated.status}
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {validated.policyNumber && (
          <div>
            <p className="text-sm font-medium">Policy Number</p>
            <p className="text-sm text-muted-foreground font-mono">{validated.policyNumber}</p>
          </div>
        )}

        {validated.claimNumber && (
          <div>
            <p className="text-sm font-medium">Claim Number</p>
            <p className="text-sm text-muted-foreground font-mono">{validated.claimNumber}</p>
          </div>
        )}

        {validated.adjuster && (
          <div>
            <p className="text-sm font-medium">Adjuster</p>
            <p className="text-sm text-muted-foreground">{validated.adjuster}</p>
            <div className="mt-2 space-y-1">
              {validated.adjusterPhone && (
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <a
                    href={`tel:${validated.adjusterPhone}`}
                    className="text-sm hover:underline"
                    onClick={(e) => {
                      e.preventDefault();
                      onAction?.("call", { phone: validated.adjusterPhone });
                    }}
                  >
                    {validated.adjusterPhone}
                  </a>
                </div>
              )}
              {validated.adjusterEmail && (
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <a
                    href={`mailto:${validated.adjusterEmail}`}
                    className="text-sm hover:underline"
                  >
                    {validated.adjusterEmail}
                  </a>
                </div>
              )}
            </div>
          </div>
        )}

        {validated.policyLimits && (
          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm">
              <span className="font-medium">Policy Limits:</span> {validated.policyLimits}
            </span>
          </div>
        )}

        {validated.coverage && validated.coverage.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-2">Coverage</p>
            <div className="flex flex-wrap gap-2">
              {validated.coverage.map((item, i) => (
                <Badge key={i} variant="secondary">
                  {item}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

const insuranceCardArtifact: ArtifactComponent<InsuranceCardProps> = {
  id: "insurance-card",
  name: "Insurance Card",
  description: "Display insurance carrier, policy, claim, and adjuster information for a case",
  component: InsuranceCard,
  schema: insuranceCardSchema,
  category: "insurance",
};

artifactRegistry.register(insuranceCardArtifact);
