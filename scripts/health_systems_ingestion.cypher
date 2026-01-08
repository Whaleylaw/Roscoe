// Health Systems Ingestion - Generated Cypher
// Source: health_systems.json
// Generated: 2026-01-02T14:18:29.918340
// Total entities: 5

// 1. Norton Healthcare
MERGE (h:HealthSystem {name: "Norton Healthcare", group_id: "roscoe_graph"})
ON CREATE SET
  h.medical_records_endpoint = "Norton Healthcare Medical Records",
  h.billing_endpoint = "Norton Healthcare Patient Financial Services",
  h.phone = "(502) 629-1234",
  h.fax = "",
  h.email = "",
  h.address = "Louisville, KY",
  h.website = "nortonhealthcare.com",
  h.created_at = "2026-01-02T14:18:29.918346"
ON MATCH SET
  h.updated_at = "2026-01-02T14:18:29.918346"
RETURN h.name, id(h)

// 2. UofL Health
MERGE (h:HealthSystem {name: "UofL Health", group_id: "roscoe_graph"})
ON CREATE SET
  h.medical_records_endpoint = "UofL Health Medical Records - Central",
  h.billing_endpoint = "UofL Health Patient Accounts",
  h.phone = "(502) 562-3000",
  h.fax = "",
  h.email = "",
  h.address = "530 South Jackson Street, Louisville, KY 40202",
  h.website = "uoflhealth.org",
  h.created_at = "2026-01-02T14:18:29.918350"
ON MATCH SET
  h.updated_at = "2026-01-02T14:18:29.918350"
RETURN h.name, id(h)

// 3. Baptist Health
MERGE (h:HealthSystem {name: "Baptist Health", group_id: "roscoe_graph"})
ON CREATE SET
  h.medical_records_endpoint = "Baptist Health Medical Records",
  h.billing_endpoint = "Baptist Health Patient Financial Services",
  h.phone = "(502) 896-5000",
  h.fax = "",
  h.email = "",
  h.address = "Louisville, KY",
  h.website = "baptisthealth.com",
  h.created_at = "2026-01-02T14:18:29.918352"
ON MATCH SET
  h.updated_at = "2026-01-02T14:18:29.918352"
RETURN h.name, id(h)

// 4. CHI Saint Joseph Health
MERGE (h:HealthSystem {name: "CHI Saint Joseph Health", group_id: "roscoe_graph"})
ON CREATE SET
  h.medical_records_endpoint = "CHI Saint Joseph Medical Records",
  h.billing_endpoint = "CHI Saint Joseph Patient Accounts",
  h.phone = "",
  h.fax = "",
  h.email = "",
  h.address = "Lexington, KY",
  h.website = "chisaintjosephhealth.org",
  h.created_at = "2026-01-02T14:18:29.918354"
ON MATCH SET
  h.updated_at = "2026-01-02T14:18:29.918354"
RETURN h.name, id(h)

// 5. St. Elizabeth Healthcare
MERGE (h:HealthSystem {name: "St. Elizabeth Healthcare", group_id: "roscoe_graph"})
ON CREATE SET
  h.medical_records_endpoint = "St. Elizabeth Medical Records",
  h.billing_endpoint = "St. Elizabeth Patient Financial Services",
  h.phone = "(859) 344-2000",
  h.fax = "",
  h.email = "",
  h.address = "Northern Kentucky",
  h.website = "stelizabeth.com",
  h.created_at = "2026-01-02T14:18:29.918356"
ON MATCH SET
  h.updated_at = "2026-01-02T14:18:29.918356"
RETURN h.name, id(h)
