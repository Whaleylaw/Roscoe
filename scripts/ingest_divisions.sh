#!/bin/bash
# Court Divisions Ingestion Script
# Generated: generate_division_ingestion_script.py
# Execute on VM: bash /tmp/ingest_divisions.sh

set -e

echo "======================================================================="
echo "COURT DIVISIONS INGESTION - PHASE 1b"
echo "======================================================================="
echo ""

# Verify graph connection
echo "Verifying FalkorDB connection..."
docker exec roscoe-graphdb redis-cli -p 6379 PING > /dev/null 2>&1 || { echo "❌ Cannot connect to FalkorDB"; exit 1; }
echo "✓ Connected to FalkorDB"
echo ""

# Pre-ingestion count
BEFORE=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (n) RETURN count(n)" --raw | grep -E "^[0-9]+$" | head -1)
echo "Nodes before: $BEFORE"
echo ""

echo "Ingesting CircuitDivision: 86 entities..."
CREATED_COUNT=0
MATCHED_COUNT=0

# 1. Barren County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Barren County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "43", h.court_name = "Barren County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Barren County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Barren County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Barren County Circuit Court, Division I"
else
  echo "  ❌ Error: Barren County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 2. Hardin County Circuit Court, Division III
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Hardin County Circuit Court, Division III", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.circuit_number = "09", h.court_name = "Hardin County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hardin County Circuit Court, Division III"
elif echo "$RESULT" | grep -q "Hardin County Circuit Court, Division III"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hardin County Circuit Court, Division III"
else
  echo "  ❌ Error: Hardin County Circuit Court, Division III"
  echo "$RESULT" | head -3
fi

# 3. Hart County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Hart County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "10", h.court_name = "Hart County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hart County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Hart County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hart County Circuit Court, Division II"
else
  echo "  ❌ Error: Hart County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 4. McCreary County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "McCreary County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "34", h.court_name = "McCreary County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McCreary County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "McCreary County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McCreary County Circuit Court, Division I"
else
  echo "  ❌ Error: McCreary County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 5. Bath County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Bath County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "21", h.court_name = "Bath County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bath County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Bath County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bath County Circuit Court, Division II"
else
  echo "  ❌ Error: Bath County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 6. Jefferson County Circuit Court, Division VII
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division VII", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "07", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division VII"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division VII"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division VII"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division VII"
  echo "$RESULT" | head -3
fi

# 7. Boone County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Boone County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "54", h.court_name = "Boone County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boone County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Boone County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boone County Circuit Court, Division I"
else
  echo "  ❌ Error: Boone County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 8. Anderson County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Anderson County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "53", h.court_name = "Anderson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Anderson County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Anderson County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Anderson County Circuit Court, Division I"
else
  echo "  ❌ Error: Anderson County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 9. Fayette County Circuit Court, Division IX
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Fayette County Circuit Court, Division IX", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "09", h.circuit_number = "22", h.court_name = "Fayette County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County Circuit Court, Division IX"
elif echo "$RESULT" | grep -q "Fayette County Circuit Court, Division IX"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County Circuit Court, Division IX"
else
  echo "  ❌ Error: Fayette County Circuit Court, Division IX"
  echo "$RESULT" | head -3
fi

# 10. Bullitt County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Bullitt County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "55", h.court_name = "Bullitt County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bullitt County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Bullitt County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bullitt County Circuit Court, Division I"
else
  echo "  ❌ Error: Bullitt County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 11. Breckinridge County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Breckinridge County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "46", h.court_name = "Breckinridge County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Breckinridge County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Breckinridge County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Breckinridge County Circuit Court, Division I"
else
  echo "  ❌ Error: Breckinridge County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 12. Daviess County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Daviess County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "06", h.court_name = "Daviess County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Daviess County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Daviess County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Daviess County Circuit Court, Division I"
else
  echo "  ❌ Error: Daviess County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 13. Knox County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Knox County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "27", h.court_name = "Knox County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Knox County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Knox County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Knox County Circuit Court, Division II"
else
  echo "  ❌ Error: Knox County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 14. Jefferson County Circuit Court, Division IX
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division IX", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "09", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division IX"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division IX"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division IX"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division IX"
  echo "$RESULT" | head -3
fi

# 15. Clark County Circuit Court, Division V
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Clark County Circuit Court, Division V", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "05", h.circuit_number = "25", h.court_name = "Clark County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clark County Circuit Court, Division V"
elif echo "$RESULT" | grep -q "Clark County Circuit Court, Division V"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clark County Circuit Court, Division V"
else
  echo "  ❌ Error: Clark County Circuit Court, Division V"
  echo "$RESULT" | head -3
fi

# 16. Edmonson County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Edmonson County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "08", h.court_name = "Edmonson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Edmonson County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Edmonson County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Edmonson County Circuit Court, Division I"
else
  echo "  ❌ Error: Edmonson County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 17. Pike County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Pike County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "35", h.court_name = "Pike County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Pike County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Pike County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Pike County Circuit Court, Division I"
else
  echo "  ❌ Error: Pike County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 18. Butler County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Butler County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "38", h.court_name = "Butler County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Butler County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Butler County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Butler County Circuit Court, Division I"
else
  echo "  ❌ Error: Butler County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 19. Oldham County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Oldham County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "12", h.court_name = "Oldham County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Oldham County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Oldham County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Oldham County Circuit Court, Division I"
else
  echo "  ❌ Error: Oldham County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 20. Garrard County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Garrard County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "13", h.court_name = "Garrard County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Garrard County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Garrard County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Garrard County Circuit Court, Division I"
else
  echo "  ❌ Error: Garrard County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 21. Bath County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Bath County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "21", h.court_name = "Bath County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bath County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Bath County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bath County Circuit Court, Division I"
else
  echo "  ❌ Error: Bath County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 22. Boyd County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Boyd County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "32", h.court_name = "Boyd County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boyd County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Boyd County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boyd County Circuit Court, Division I"
else
  echo "  ❌ Error: Boyd County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 23. Jefferson County Circuit Court, Division V
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division V", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "05", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division V"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division V"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division V"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division V"
  echo "$RESULT" | head -3
fi

# 24. Christian County Circuit Court, Division IV
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Christian County Circuit Court, Division IV", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.circuit_number = "03", h.court_name = "Christian County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Christian County Circuit Court, Division IV"
elif echo "$RESULT" | grep -q "Christian County Circuit Court, Division IV"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Christian County Circuit Court, Division IV"
else
  echo "  ❌ Error: Christian County Circuit Court, Division IV"
  echo "$RESULT" | head -3
fi

# 25. Jefferson County Circuit Court, Division XI
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division XI", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "11", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division XI"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division XI"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division XI"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division XI"
  echo "$RESULT" | head -3
fi

# 26. Russell County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Russell County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "57", h.court_name = "Russell County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Russell County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Russell County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Russell County Circuit Court, Division II"
else
  echo "  ❌ Error: Russell County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 27. Bourbon County Circuit Court, Division IV
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Bourbon County Circuit Court, Division IV", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.circuit_number = "14", h.court_name = "Bourbon County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bourbon County Circuit Court, Division IV"
elif echo "$RESULT" | grep -q "Bourbon County Circuit Court, Division IV"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bourbon County Circuit Court, Division IV"
else
  echo "  ❌ Error: Bourbon County Circuit Court, Division IV"
  echo "$RESULT" | head -3
fi

# 28. Bourbon County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Bourbon County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "14", h.court_name = "Bourbon County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bourbon County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Bourbon County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bourbon County Circuit Court, Division II"
else
  echo "  ❌ Error: Bourbon County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 29. Jefferson County Circuit Court, Division XII
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division XII", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "12", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division XII"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division XII"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division XII"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division XII"
  echo "$RESULT" | head -3
fi

# 30. Fayette County Circuit Court, Division IV
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Fayette County Circuit Court, Division IV", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.circuit_number = "22", h.court_name = "Fayette County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County Circuit Court, Division IV"
elif echo "$RESULT" | grep -q "Fayette County Circuit Court, Division IV"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County Circuit Court, Division IV"
else
  echo "  ❌ Error: Fayette County Circuit Court, Division IV"
  echo "$RESULT" | head -3
fi

# 31. Jefferson County Circuit Court, Division VI
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division VI", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "06", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division VI"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division VI"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division VI"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division VI"
  echo "$RESULT" | head -3
fi

# 32. Russell County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Russell County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "57", h.court_name = "Russell County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Russell County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Russell County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Russell County Circuit Court, Division I"
else
  echo "  ❌ Error: Russell County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 33. Edmonson County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Edmonson County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "08", h.court_name = "Edmonson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Edmonson County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Edmonson County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Edmonson County Circuit Court, Division II"
else
  echo "  ❌ Error: Edmonson County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 34. Pike County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Pike County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "35", h.court_name = "Pike County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Pike County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Pike County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Pike County Circuit Court, Division II"
else
  echo "  ❌ Error: Pike County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 35. Jefferson County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division I"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 36. Floyd County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Floyd County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "31", h.court_name = "Floyd County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Floyd County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Floyd County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Floyd County Circuit Court, Division I"
else
  echo "  ❌ Error: Floyd County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 37. Crittenden County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Crittenden County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "05", h.court_name = "Crittenden County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Crittenden County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Crittenden County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Crittenden County Circuit Court, Division I"
else
  echo "  ❌ Error: Crittenden County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 38. Edmonson County Circuit Court, Division V
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Edmonson County Circuit Court, Division V", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "05", h.circuit_number = "08", h.court_name = "Edmonson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Edmonson County Circuit Court, Division V"
elif echo "$RESULT" | grep -q "Edmonson County Circuit Court, Division V"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Edmonson County Circuit Court, Division V"
else
  echo "  ❌ Error: Edmonson County Circuit Court, Division V"
  echo "$RESULT" | head -3
fi

# 39. Johnson County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Johnson County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "24", h.court_name = "Johnson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Johnson County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Johnson County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Johnson County Circuit Court, Division II"
else
  echo "  ❌ Error: Johnson County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 40. Clay County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Clay County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "41", h.court_name = "Clay County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clay County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Clay County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clay County Circuit Court, Division I"
else
  echo "  ❌ Error: Clay County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 41. Boyle County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Boyle County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "50", h.court_name = "Boyle County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boyle County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Boyle County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boyle County Circuit Court, Division I"
else
  echo "  ❌ Error: Boyle County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 42. Jefferson County Circuit Court, Division IV
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division IV", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division IV"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division IV"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division IV"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division IV"
  echo "$RESULT" | head -3
fi

# 43. McCracken County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "McCracken County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "02", h.court_name = "McCracken County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McCracken County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "McCracken County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McCracken County Circuit Court, Division II"
else
  echo "  ❌ Error: McCracken County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 44. Kenton County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Kenton County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "16", h.court_name = "Kenton County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kenton County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Kenton County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kenton County Circuit Court, Division I"
else
  echo "  ❌ Error: Kenton County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 45. Knox County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Knox County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "27", h.court_name = "Knox County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Knox County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Knox County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Knox County Circuit Court, Division I"
else
  echo "  ❌ Error: Knox County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 46. Clark County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Clark County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "25", h.court_name = "Clark County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clark County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Clark County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clark County Circuit Court, Division II"
else
  echo "  ❌ Error: Clark County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 47. Bourbon County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Bourbon County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "14", h.court_name = "Bourbon County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bourbon County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Bourbon County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bourbon County Circuit Court, Division I"
else
  echo "  ❌ Error: Bourbon County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 48. Greenup County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Greenup County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "20", h.court_name = "Greenup County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Greenup County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Greenup County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Greenup County Circuit Court, Division I"
else
  echo "  ❌ Error: Greenup County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 49. Fayette County Circuit Court, Division VII
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Fayette County Circuit Court, Division VII", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "07", h.circuit_number = "22", h.court_name = "Fayette County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County Circuit Court, Division VII"
elif echo "$RESULT" | grep -q "Fayette County Circuit Court, Division VII"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County Circuit Court, Division VII"
else
  echo "  ❌ Error: Fayette County Circuit Court, Division VII"
  echo "$RESULT" | head -3
fi

# 50. Kenton County Circuit Court, Division III
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Kenton County Circuit Court, Division III", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.circuit_number = "16", h.court_name = "Kenton County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kenton County Circuit Court, Division III"
elif echo "$RESULT" | grep -q "Kenton County Circuit Court, Division III"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kenton County Circuit Court, Division III"
else
  echo "  ❌ Error: Kenton County Circuit Court, Division III"
  echo "$RESULT" | head -3
fi

# 51. Lincoln County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Lincoln County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "28", h.court_name = "Lincoln County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Lincoln County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Lincoln County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Lincoln County Circuit Court, Division II"
else
  echo "  ❌ Error: Lincoln County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 52. Calloway County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Calloway County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "42", h.court_name = "Calloway County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Calloway County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Calloway County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Calloway County Circuit Court, Division I"
else
  echo "  ❌ Error: Calloway County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 53. Jefferson County Circuit Court, Division X
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division X", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "10", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division X"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division X"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division X"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division X"
  echo "$RESULT" | head -3
fi

# 54. Jefferson County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division II"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 55. Daviess County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Daviess County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "06", h.court_name = "Daviess County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Daviess County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Daviess County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Daviess County Circuit Court, Division II"
else
  echo "  ❌ Error: Daviess County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 56. Calloway County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Calloway County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "42", h.court_name = "Calloway County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Calloway County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Calloway County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Calloway County Circuit Court, Division II"
else
  echo "  ❌ Error: Calloway County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 57. Jefferson County Circuit Court, Division III
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division III", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division III"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division III"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division III"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division III"
  echo "$RESULT" | head -3
fi

# 58. Boyle County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Boyle County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "50", h.court_name = "Boyle County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boyle County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Boyle County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boyle County Circuit Court, Division II"
else
  echo "  ❌ Error: Boyle County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 59. Carter County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Carter County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "37", h.court_name = "Carter County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Carter County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Carter County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Carter County Circuit Court, Division I"
else
  echo "  ❌ Error: Carter County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 60. Caldwell County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Caldwell County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "56", h.court_name = "Caldwell County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Caldwell County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Caldwell County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Caldwell County Circuit Court, Division I"
else
  echo "  ❌ Error: Caldwell County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 61. Green County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Green County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "11", h.court_name = "Green County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Green County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Green County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Green County Circuit Court, Division II"
else
  echo "  ❌ Error: Green County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 62. McCracken County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "McCracken County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "02", h.court_name = "McCracken County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McCracken County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "McCracken County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McCracken County Circuit Court, Division I"
else
  echo "  ❌ Error: McCracken County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 63. Boone County Circuit Court, Division III
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Boone County Circuit Court, Division III", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.circuit_number = "54", h.court_name = "Boone County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boone County Circuit Court, Division III"
elif echo "$RESULT" | grep -q "Boone County Circuit Court, Division III"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boone County Circuit Court, Division III"
else
  echo "  ❌ Error: Boone County Circuit Court, Division III"
  echo "$RESULT" | head -3
fi

# 64. Franklin County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Franklin County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "48", h.court_name = "Franklin County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Franklin County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Franklin County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Franklin County Circuit Court, Division I"
else
  echo "  ❌ Error: Franklin County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 65. Hardin County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Hardin County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "09", h.court_name = "Hardin County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hardin County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Hardin County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hardin County Circuit Court, Division II"
else
  echo "  ❌ Error: Hardin County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 66. Hart County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Hart County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "10", h.court_name = "Hart County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hart County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Hart County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hart County Circuit Court, Division I"
else
  echo "  ❌ Error: Hart County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 67. Jefferson County Circuit Court, Division XIII
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division XIII", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "13", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division XIII"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division XIII"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division XIII"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division XIII"
  echo "$RESULT" | head -3
fi

# 68. Green County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Green County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "11", h.court_name = "Green County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Green County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Green County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Green County Circuit Court, Division I"
else
  echo "  ❌ Error: Green County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 69. Kenton County Circuit Court, Division IV
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Kenton County Circuit Court, Division IV", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.circuit_number = "16", h.court_name = "Kenton County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kenton County Circuit Court, Division IV"
elif echo "$RESULT" | grep -q "Kenton County Circuit Court, Division IV"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kenton County Circuit Court, Division IV"
else
  echo "  ❌ Error: Kenton County Circuit Court, Division IV"
  echo "$RESULT" | head -3
fi

# 70. Allen County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Allen County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "49", h.court_name = "Allen County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Allen County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Allen County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Allen County Circuit Court, Division I"
else
  echo "  ❌ Error: Allen County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 71. Fayette County Circuit Court, Division VIII
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Fayette County Circuit Court, Division VIII", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "08", h.circuit_number = "22", h.court_name = "Fayette County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County Circuit Court, Division VIII"
elif echo "$RESULT" | grep -q "Fayette County Circuit Court, Division VIII"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County Circuit Court, Division VIII"
else
  echo "  ❌ Error: Fayette County Circuit Court, Division VIII"
  echo "$RESULT" | head -3
fi

# 72. Fayette County Circuit Court, Division III
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Fayette County Circuit Court, Division III", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.circuit_number = "22", h.court_name = "Fayette County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County Circuit Court, Division III"
elif echo "$RESULT" | grep -q "Fayette County Circuit Court, Division III"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County Circuit Court, Division III"
else
  echo "  ❌ Error: Fayette County Circuit Court, Division III"
  echo "$RESULT" | head -3
fi

# 73. Lincoln County Circuit Court, Division IV
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Lincoln County Circuit Court, Division IV", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.circuit_number = "28", h.court_name = "Lincoln County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Lincoln County Circuit Court, Division IV"
elif echo "$RESULT" | grep -q "Lincoln County Circuit Court, Division IV"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Lincoln County Circuit Court, Division IV"
else
  echo "  ❌ Error: Lincoln County Circuit Court, Division IV"
  echo "$RESULT" | head -3
fi

# 74. Boyd County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Boyd County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "32", h.court_name = "Boyd County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boyd County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Boyd County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boyd County Circuit Court, Division II"
else
  echo "  ❌ Error: Boyd County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 75. Campbell County Circuit Court, Division III
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Campbell County Circuit Court, Division III", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.circuit_number = "17", h.court_name = "Campbell County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Campbell County Circuit Court, Division III"
elif echo "$RESULT" | grep -q "Campbell County Circuit Court, Division III"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Campbell County Circuit Court, Division III"
else
  echo "  ❌ Error: Campbell County Circuit Court, Division III"
  echo "$RESULT" | head -3
fi

# 76. Clark County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Clark County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "25", h.court_name = "Clark County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clark County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Clark County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clark County Circuit Court, Division I"
else
  echo "  ❌ Error: Clark County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 77. Campbell County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Campbell County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "17", h.court_name = "Campbell County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Campbell County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Campbell County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Campbell County Circuit Court, Division I"
else
  echo "  ❌ Error: Campbell County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 78. Breathitt County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Breathitt County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "39", h.court_name = "Breathitt County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Breathitt County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Breathitt County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Breathitt County Circuit Court, Division I"
else
  echo "  ❌ Error: Breathitt County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 79. Lincoln County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Lincoln County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "28", h.court_name = "Lincoln County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Lincoln County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Lincoln County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Lincoln County Circuit Court, Division I"
else
  echo "  ❌ Error: Lincoln County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 80. Caldwell County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Caldwell County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "56", h.court_name = "Caldwell County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Caldwell County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Caldwell County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Caldwell County Circuit Court, Division II"
else
  echo "  ❌ Error: Caldwell County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 81. Jefferson County Circuit Court, Division VIII
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Jefferson County Circuit Court, Division VIII", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "08", h.circuit_number = "30", h.court_name = "Jefferson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County Circuit Court, Division VIII"
elif echo "$RESULT" | grep -q "Jefferson County Circuit Court, Division VIII"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County Circuit Court, Division VIII"
else
  echo "  ❌ Error: Jefferson County Circuit Court, Division VIII"
  echo "$RESULT" | head -3
fi

# 82. Franklin County Circuit Court, Division III
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Franklin County Circuit Court, Division III", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.circuit_number = "48", h.court_name = "Franklin County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Franklin County Circuit Court, Division III"
elif echo "$RESULT" | grep -q "Franklin County Circuit Court, Division III"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Franklin County Circuit Court, Division III"
else
  echo "  ❌ Error: Franklin County Circuit Court, Division III"
  echo "$RESULT" | head -3
fi

# 83. Henderson County Circuit Court, Division I
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Henderson County Circuit Court, Division I", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.circuit_number = "51", h.court_name = "Henderson County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Henderson County Circuit Court, Division I"
elif echo "$RESULT" | grep -q "Henderson County Circuit Court, Division I"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Henderson County Circuit Court, Division I"
else
  echo "  ❌ Error: Henderson County Circuit Court, Division I"
  echo "$RESULT" | head -3
fi

# 84. McCreary County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "McCreary County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "34", h.court_name = "McCreary County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McCreary County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "McCreary County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McCreary County Circuit Court, Division II"
else
  echo "  ❌ Error: McCreary County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 85. Franklin County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Franklin County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "48", h.court_name = "Franklin County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Franklin County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Franklin County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Franklin County Circuit Court, Division II"
else
  echo "  ❌ Error: Franklin County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

# 86. Campbell County Circuit Court, Division II
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:CircuitDivision {name: "Campbell County Circuit Court, Division II", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.circuit_number = "17", h.court_name = "Campbell County Circuit Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Campbell County Circuit Court, Division II"
elif echo "$RESULT" | grep -q "Campbell County Circuit Court, Division II"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Campbell County Circuit Court, Division II"
else
  echo "  ❌ Error: Campbell County Circuit Court, Division II"
  echo "$RESULT" | head -3
fi

echo ""
echo "CircuitDivision Summary: Created=$CREATED_COUNT, Matched=$MATCHED_COUNT"
echo ""

echo "Ingesting DistrictDivision: 94 entities..."
CREATED_COUNT=0
MATCHED_COUNT=0

# 1. Christian County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Christian County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "03", h.court_name = "Christian County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Christian County District Court"
elif echo "$RESULT" | grep -q "Christian County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Christian County District Court"
else
  echo "  ❌ Error: Christian County District Court"
  echo "$RESULT" | head -3
fi

# 2. Green County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Green County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "11", h.court_name = "Green County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Green County District Court, Division 01"
elif echo "$RESULT" | grep -q "Green County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Green County District Court, Division 01"
else
  echo "  ❌ Error: Green County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 3. Clay County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Clay County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "41", h.court_name = "Clay County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clay County District Court, Division 02"
elif echo "$RESULT" | grep -q "Clay County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clay County District Court, Division 02"
else
  echo "  ❌ Error: Clay County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 4. Boyle County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Boyle County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "50", h.court_name = "Boyle County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boyle County District Court"
elif echo "$RESULT" | grep -q "Boyle County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boyle County District Court"
else
  echo "  ❌ Error: Boyle County District Court"
  echo "$RESULT" | head -3
fi

# 5. Fayette County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Fayette County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "22", h.court_name = "Fayette County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County District Court, Division 02"
elif echo "$RESULT" | grep -q "Fayette County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County District Court, Division 02"
else
  echo "  ❌ Error: Fayette County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 6. Bourbon County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Bourbon County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "14", h.court_name = "Bourbon County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bourbon County District Court, Division 01"
elif echo "$RESULT" | grep -q "Bourbon County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bourbon County District Court, Division 01"
else
  echo "  ❌ Error: Bourbon County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 7. Bath County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Bath County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "21", h.court_name = "Bath County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bath County District Court, Division 02"
elif echo "$RESULT" | grep -q "Bath County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bath County District Court, Division 02"
else
  echo "  ❌ Error: Bath County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 8. Campbell County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Campbell County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "17", h.court_name = "Campbell County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Campbell County District Court, Division 01"
elif echo "$RESULT" | grep -q "Campbell County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Campbell County District Court, Division 01"
else
  echo "  ❌ Error: Campbell County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 9. Butler County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Butler County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "38", h.court_name = "Butler County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Butler County District Court, Division 02"
elif echo "$RESULT" | grep -q "Butler County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Butler County District Court, Division 02"
else
  echo "  ❌ Error: Butler County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 10. Henderson County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Henderson County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "51", h.court_name = "Henderson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Henderson County District Court, Division 01"
elif echo "$RESULT" | grep -q "Henderson County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Henderson County District Court, Division 01"
else
  echo "  ❌ Error: Henderson County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 11. Jefferson County District Court, Division 12
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 12", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "12", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 12"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 12"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 12"
else
  echo "  ❌ Error: Jefferson County District Court, Division 12"
  echo "$RESULT" | head -3
fi

# 12. Jefferson County District Court, Division 14
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 14", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "14", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 14"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 14"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 14"
else
  echo "  ❌ Error: Jefferson County District Court, Division 14"
  echo "$RESULT" | head -3
fi

# 13. Johnson County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Johnson County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "24", h.court_name = "Johnson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Johnson County District Court, Division 02"
elif echo "$RESULT" | grep -q "Johnson County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Johnson County District Court, Division 02"
else
  echo "  ❌ Error: Johnson County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 14. Breckinridge County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Breckinridge County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "46", h.court_name = "Breckinridge County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Breckinridge County District Court, Division 01"
elif echo "$RESULT" | grep -q "Breckinridge County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Breckinridge County District Court, Division 01"
else
  echo "  ❌ Error: Breckinridge County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 15. Johnson County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Johnson County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "24", h.court_name = "Johnson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Johnson County District Court, Division 01"
elif echo "$RESULT" | grep -q "Johnson County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Johnson County District Court, Division 01"
else
  echo "  ❌ Error: Johnson County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 16. Carroll County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Carroll County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "15", h.court_name = "Carroll County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Carroll County District Court, Division 01"
elif echo "$RESULT" | grep -q "Carroll County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Carroll County District Court, Division 01"
else
  echo "  ❌ Error: Carroll County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 17. Knox County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Knox County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "27", h.court_name = "Knox County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Knox County District Court, Division 02"
elif echo "$RESULT" | grep -q "Knox County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Knox County District Court, Division 02"
else
  echo "  ❌ Error: Knox County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 18. Christian County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Christian County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "03", h.court_name = "Christian County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Christian County District Court, Division 02"
elif echo "$RESULT" | grep -q "Christian County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Christian County District Court, Division 02"
else
  echo "  ❌ Error: Christian County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 19. Greenup County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Greenup County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "20", h.court_name = "Greenup County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Greenup County District Court"
elif echo "$RESULT" | grep -q "Greenup County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Greenup County District Court"
else
  echo "  ❌ Error: Greenup County District Court"
  echo "$RESULT" | head -3
fi

# 20. Breckinridge County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Breckinridge County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "46", h.court_name = "Breckinridge County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Breckinridge County District Court, Division 02"
elif echo "$RESULT" | grep -q "Breckinridge County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Breckinridge County District Court, Division 02"
else
  echo "  ❌ Error: Breckinridge County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 21. Jefferson County District Court, Division 04
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 04", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 04"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 04"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 04"
else
  echo "  ❌ Error: Jefferson County District Court, Division 04"
  echo "$RESULT" | head -3
fi

# 22. Jefferson County District Court, Division 13
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 13", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "13", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 13"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 13"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 13"
else
  echo "  ❌ Error: Jefferson County District Court, Division 13"
  echo "$RESULT" | head -3
fi

# 23. Anderson County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Anderson County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "53", h.court_name = "Anderson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Anderson County District Court, Division 02"
elif echo "$RESULT" | grep -q "Anderson County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Anderson County District Court, Division 02"
else
  echo "  ❌ Error: Anderson County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 24. Kenton County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Kenton County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "16", h.court_name = "Kenton County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kenton County District Court, Division 02"
elif echo "$RESULT" | grep -q "Kenton County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kenton County District Court, Division 02"
else
  echo "  ❌ Error: Kenton County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 25. Jefferson County District Court, Division 08
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 08", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "08", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 08"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 08"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 08"
else
  echo "  ❌ Error: Jefferson County District Court, Division 08"
  echo "$RESULT" | head -3
fi

# 26. Oldham County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Oldham County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "12", h.court_name = "Oldham County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Oldham County District Court, Division 01"
elif echo "$RESULT" | grep -q "Oldham County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Oldham County District Court, Division 01"
else
  echo "  ❌ Error: Oldham County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 27. Clark County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Clark County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "25", h.court_name = "Clark County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clark County District Court, Division 01"
elif echo "$RESULT" | grep -q "Clark County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clark County District Court, Division 01"
else
  echo "  ❌ Error: Clark County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 28. Carroll County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Carroll County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "15", h.court_name = "Carroll County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Carroll County District Court, Division 02"
elif echo "$RESULT" | grep -q "Carroll County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Carroll County District Court, Division 02"
else
  echo "  ❌ Error: Carroll County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 29. Jefferson County District Court, Division 03
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 03", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 03"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 03"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 03"
else
  echo "  ❌ Error: Jefferson County District Court, Division 03"
  echo "$RESULT" | head -3
fi

# 30. Warren County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Warren County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "08", h.court_name = "Warren County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Warren County District Court, Division 01"
elif echo "$RESULT" | grep -q "Warren County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Warren County District Court, Division 01"
else
  echo "  ❌ Error: Warren County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 31. Hopkins County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Hopkins County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "04", h.court_name = "Hopkins County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hopkins County District Court, Division 02"
elif echo "$RESULT" | grep -q "Hopkins County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hopkins County District Court, Division 02"
else
  echo "  ❌ Error: Hopkins County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 32. Perry County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Perry County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "33", h.court_name = "Perry County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Perry County District Court"
elif echo "$RESULT" | grep -q "Perry County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Perry County District Court"
else
  echo "  ❌ Error: Perry County District Court"
  echo "$RESULT" | head -3
fi

# 33. Floyd County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Floyd County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "31", h.court_name = "Floyd County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Floyd County District Court, Division 02"
elif echo "$RESULT" | grep -q "Floyd County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Floyd County District Court, Division 02"
else
  echo "  ❌ Error: Floyd County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 34. Kenton County District Court, Division 03
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Kenton County District Court, Division 03", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.district_number = "16", h.court_name = "Kenton County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kenton County District Court, Division 03"
elif echo "$RESULT" | grep -q "Kenton County District Court, Division 03"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kenton County District Court, Division 03"
else
  echo "  ❌ Error: Kenton County District Court, Division 03"
  echo "$RESULT" | head -3
fi

# 35. Fayette County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Fayette County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "22", h.court_name = "Fayette County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County District Court, Division 01"
elif echo "$RESULT" | grep -q "Fayette County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County District Court, Division 01"
else
  echo "  ❌ Error: Fayette County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 36. Green County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Green County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "11", h.court_name = "Green County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Green County District Court, Division 02"
elif echo "$RESULT" | grep -q "Green County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Green County District Court, Division 02"
else
  echo "  ❌ Error: Green County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 37. Knox County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Knox County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "27", h.court_name = "Knox County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Knox County District Court, Division 01"
elif echo "$RESULT" | grep -q "Knox County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Knox County District Court, Division 01"
else
  echo "  ❌ Error: Knox County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 38. Pulaski County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Pulaski County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "28", h.court_name = "Pulaski County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Pulaski County District Court, Division 01"
elif echo "$RESULT" | grep -q "Pulaski County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Pulaski County District Court, Division 01"
else
  echo "  ❌ Error: Pulaski County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 39. Bourbon County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Bourbon County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "14", h.court_name = "Bourbon County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bourbon County District Court, Division 02"
elif echo "$RESULT" | grep -q "Bourbon County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bourbon County District Court, Division 02"
else
  echo "  ❌ Error: Bourbon County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 40. Jefferson County District Court, Division 09
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 09", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "09", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 09"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 09"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 09"
else
  echo "  ❌ Error: Jefferson County District Court, Division 09"
  echo "$RESULT" | head -3
fi

# 41. McCracken County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "McCracken County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "02", h.court_name = "McCracken County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McCracken County District Court, Division 02"
elif echo "$RESULT" | grep -q "McCracken County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McCracken County District Court, Division 02"
else
  echo "  ❌ Error: McCracken County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 42. Harlan County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Harlan County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "26", h.court_name = "Harlan County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Harlan County District Court"
elif echo "$RESULT" | grep -q "Harlan County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Harlan County District Court"
else
  echo "  ❌ Error: Harlan County District Court"
  echo "$RESULT" | head -3
fi

# 43. Clark County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Clark County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "25", h.court_name = "Clark County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clark County District Court, Division 02"
elif echo "$RESULT" | grep -q "Clark County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clark County District Court, Division 02"
else
  echo "  ❌ Error: Clark County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 44. Jefferson County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 01"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 01"
else
  echo "  ❌ Error: Jefferson County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 45. McCracken County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "McCracken County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "02", h.court_name = "McCracken County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McCracken County District Court, Division 01"
elif echo "$RESULT" | grep -q "McCracken County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McCracken County District Court, Division 01"
else
  echo "  ❌ Error: McCracken County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 46. Jefferson County District Court, Division 16
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 16", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "16", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 16"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 16"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 16"
else
  echo "  ❌ Error: Jefferson County District Court, Division 16"
  echo "$RESULT" | head -3
fi

# 47. Caldwell County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Caldwell County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "56", h.court_name = "Caldwell County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Caldwell County District Court, Division 01"
elif echo "$RESULT" | grep -q "Caldwell County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Caldwell County District Court, Division 01"
else
  echo "  ❌ Error: Caldwell County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 48. Jefferson County District Court, Division 06
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 06", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "06", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 06"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 06"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 06"
else
  echo "  ❌ Error: Jefferson County District Court, Division 06"
  echo "$RESULT" | head -3
fi

# 49. Clinton County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Clinton County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "40", h.court_name = "Clinton County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clinton County District Court, Division 01"
elif echo "$RESULT" | grep -q "Clinton County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clinton County District Court, Division 01"
else
  echo "  ❌ Error: Clinton County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 50. Estill County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Estill County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "23", h.court_name = "Estill County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Estill County District Court"
elif echo "$RESULT" | grep -q "Estill County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Estill County District Court"
else
  echo "  ❌ Error: Estill County District Court"
  echo "$RESULT" | head -3
fi

# 51. Jefferson County District Court, Division 05
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 05", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "05", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 05"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 05"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 05"
else
  echo "  ❌ Error: Jefferson County District Court, Division 05"
  echo "$RESULT" | head -3
fi

# 52. Crittenden County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Crittenden County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "05", h.court_name = "Crittenden County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Crittenden County District Court"
elif echo "$RESULT" | grep -q "Crittenden County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Crittenden County District Court"
else
  echo "  ❌ Error: Crittenden County District Court"
  echo "$RESULT" | head -3
fi

# 53. Hopkins County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Hopkins County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "04", h.court_name = "Hopkins County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hopkins County District Court, Division 01"
elif echo "$RESULT" | grep -q "Hopkins County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hopkins County District Court, Division 01"
else
  echo "  ❌ Error: Hopkins County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 54. Pike County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Pike County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "35", h.court_name = "Pike County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Pike County District Court, Division 02"
elif echo "$RESULT" | grep -q "Pike County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Pike County District Court, Division 02"
else
  echo "  ❌ Error: Pike County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 55. Jefferson County District Court, Division 07
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 07", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "07", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 07"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 07"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 07"
else
  echo "  ❌ Error: Jefferson County District Court, Division 07"
  echo "$RESULT" | head -3
fi

# 56. Oldham County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Oldham County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "12", h.court_name = "Oldham County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Oldham County District Court, Division 02"
elif echo "$RESULT" | grep -q "Oldham County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Oldham County District Court, Division 02"
else
  echo "  ❌ Error: Oldham County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 57. Hart County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Hart County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "10", h.court_name = "Hart County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hart County District Court"
elif echo "$RESULT" | grep -q "Hart County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hart County District Court"
else
  echo "  ❌ Error: Hart County District Court"
  echo "$RESULT" | head -3
fi

# 58. Daviess County District Court, Division 03
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Daviess County District Court, Division 03", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.district_number = "06", h.court_name = "Daviess County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Daviess County District Court, Division 03"
elif echo "$RESULT" | grep -q "Daviess County District Court, Division 03"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Daviess County District Court, Division 03"
else
  echo "  ❌ Error: Daviess County District Court, Division 03"
  echo "$RESULT" | head -3
fi

# 59. Daviess County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Daviess County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "06", h.court_name = "Daviess County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Daviess County District Court, Division 01"
elif echo "$RESULT" | grep -q "Daviess County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Daviess County District Court, Division 01"
else
  echo "  ❌ Error: Daviess County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 60. Jefferson County District Court, Division 11
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 11", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "11", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 11"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 11"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 11"
else
  echo "  ❌ Error: Jefferson County District Court, Division 11"
  echo "$RESULT" | head -3
fi

# 61. Fayette County District Court, Division 04
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Fayette County District Court, Division 04", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "04", h.district_number = "22", h.court_name = "Fayette County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County District Court, Division 04"
elif echo "$RESULT" | grep -q "Fayette County District Court, Division 04"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County District Court, Division 04"
else
  echo "  ❌ Error: Fayette County District Court, Division 04"
  echo "$RESULT" | head -3
fi

# 62. Henderson County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Henderson County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "51", h.court_name = "Henderson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Henderson County District Court, Division 02"
elif echo "$RESULT" | grep -q "Henderson County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Henderson County District Court, Division 02"
else
  echo "  ❌ Error: Henderson County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 63. Jefferson County District Court, Division 10
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 10", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "10", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 10"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 10"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 10"
else
  echo "  ❌ Error: Jefferson County District Court, Division 10"
  echo "$RESULT" | head -3
fi

# 64. Franklin County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Franklin County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "48", h.court_name = "Franklin County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Franklin County District Court, Division 02"
elif echo "$RESULT" | grep -q "Franklin County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Franklin County District Court, Division 02"
else
  echo "  ❌ Error: Franklin County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 65. Barren County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Barren County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "43", h.court_name = "Barren County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Barren County District Court"
elif echo "$RESULT" | grep -q "Barren County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Barren County District Court"
else
  echo "  ❌ Error: Barren County District Court"
  echo "$RESULT" | head -3
fi

# 66. Bullitt County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Bullitt County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "55", h.court_name = "Bullitt County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bullitt County District Court"
elif echo "$RESULT" | grep -q "Bullitt County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bullitt County District Court"
else
  echo "  ❌ Error: Bullitt County District Court"
  echo "$RESULT" | head -3
fi

# 67. Warren County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Warren County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "08", h.court_name = "Warren County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Warren County District Court, Division 02"
elif echo "$RESULT" | grep -q "Warren County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Warren County District Court, Division 02"
else
  echo "  ❌ Error: Warren County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 68. Daviess County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Daviess County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "06", h.court_name = "Daviess County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Daviess County District Court, Division 02"
elif echo "$RESULT" | grep -q "Daviess County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Daviess County District Court, Division 02"
else
  echo "  ❌ Error: Daviess County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 69. Bracken County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Bracken County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "19", h.court_name = "Bracken County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bracken County District Court"
elif echo "$RESULT" | grep -q "Bracken County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bracken County District Court"
else
  echo "  ❌ Error: Bracken County District Court"
  echo "$RESULT" | head -3
fi

# 70. Boyd County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Boyd County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "32", h.court_name = "Boyd County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boyd County District Court, Division 02"
elif echo "$RESULT" | grep -q "Boyd County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boyd County District Court, Division 02"
else
  echo "  ❌ Error: Boyd County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 71. Boyd County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Boyd County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "32", h.court_name = "Boyd County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boyd County District Court, Division 01"
elif echo "$RESULT" | grep -q "Boyd County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boyd County District Court, Division 01"
else
  echo "  ❌ Error: Boyd County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 72. Graves County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Graves County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "52", h.court_name = "Graves County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Graves County District Court"
elif echo "$RESULT" | grep -q "Graves County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Graves County District Court"
else
  echo "  ❌ Error: Graves County District Court"
  echo "$RESULT" | head -3
fi

# 73. Clay County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Clay County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "41", h.court_name = "Clay County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Clay County District Court, Division 01"
elif echo "$RESULT" | grep -q "Clay County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Clay County District Court, Division 01"
else
  echo "  ❌ Error: Clay County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 74. Bath County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Bath County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "21", h.court_name = "Bath County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bath County District Court, Division 01"
elif echo "$RESULT" | grep -q "Bath County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bath County District Court, Division 01"
else
  echo "  ❌ Error: Bath County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 75. Kenton County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Kenton County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "16", h.court_name = "Kenton County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kenton County District Court, Division 01"
elif echo "$RESULT" | grep -q "Kenton County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kenton County District Court, Division 01"
else
  echo "  ❌ Error: Kenton County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 76. Breathitt County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Breathitt County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "39", h.court_name = "Breathitt County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Breathitt County District Court"
elif echo "$RESULT" | grep -q "Breathitt County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Breathitt County District Court"
else
  echo "  ❌ Error: Breathitt County District Court"
  echo "$RESULT" | head -3
fi

# 77. Caldwell County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Caldwell County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "56", h.court_name = "Caldwell County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Caldwell County District Court, Division 02"
elif echo "$RESULT" | grep -q "Caldwell County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Caldwell County District Court, Division 02"
else
  echo "  ❌ Error: Caldwell County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 78. Hardin County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Hardin County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "09", h.court_name = "Hardin County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Hardin County District Court, Division 01"
elif echo "$RESULT" | grep -q "Hardin County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Hardin County District Court, Division 01"
else
  echo "  ❌ Error: Hardin County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 79. Campbell County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Campbell County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "17", h.court_name = "Campbell County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Campbell County District Court, Division 02"
elif echo "$RESULT" | grep -q "Campbell County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Campbell County District Court, Division 02"
else
  echo "  ❌ Error: Campbell County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 80. Pulaski County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Pulaski County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "28", h.court_name = "Pulaski County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Pulaski County District Court, Division 02"
elif echo "$RESULT" | grep -q "Pulaski County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Pulaski County District Court, Division 02"
else
  echo "  ❌ Error: Pulaski County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 81. McLean County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "McLean County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "45", h.court_name = "McLean County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McLean County District Court"
elif echo "$RESULT" | grep -q "McLean County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McLean County District Court"
else
  echo "  ❌ Error: McLean County District Court"
  echo "$RESULT" | head -3
fi

# 82. Fayette County District Court, Division 05
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Fayette County District Court, Division 05", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "05", h.district_number = "22", h.court_name = "Fayette County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County District Court, Division 05"
elif echo "$RESULT" | grep -q "Fayette County District Court, Division 05"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County District Court, Division 05"
else
  echo "  ❌ Error: Fayette County District Court, Division 05"
  echo "$RESULT" | head -3
fi

# 83. Boone County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Boone County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "54", h.court_name = "Boone County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Boone County District Court, Division 02"
elif echo "$RESULT" | grep -q "Boone County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Boone County District Court, Division 02"
else
  echo "  ❌ Error: Boone County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 84. Fayette County District Court, Division 03
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Fayette County District Court, Division 03", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "03", h.district_number = "22", h.court_name = "Fayette County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Fayette County District Court, Division 03"
elif echo "$RESULT" | grep -q "Fayette County District Court, Division 03"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Fayette County District Court, Division 03"
else
  echo "  ❌ Error: Fayette County District Court, Division 03"
  echo "$RESULT" | head -3
fi

# 85. Butler County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Butler County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "38", h.court_name = "Butler County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Butler County District Court, Division 01"
elif echo "$RESULT" | grep -q "Butler County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Butler County District Court, Division 01"
else
  echo "  ❌ Error: Butler County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 86. Letcher County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Letcher County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "47", h.court_name = "Letcher County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Letcher County District Court"
elif echo "$RESULT" | grep -q "Letcher County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Letcher County District Court"
else
  echo "  ❌ Error: Letcher County District Court"
  echo "$RESULT" | head -3
fi

# 87. McCreary County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "McCreary County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "34", h.court_name = "McCreary County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: McCreary County District Court, Division 02"
elif echo "$RESULT" | grep -q "McCreary County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: McCreary County District Court, Division 02"
else
  echo "  ❌ Error: McCreary County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 88. Carter County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Carter County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "37", h.court_name = "Carter County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Carter County District Court"
elif echo "$RESULT" | grep -q "Carter County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Carter County District Court"
else
  echo "  ❌ Error: Carter County District Court"
  echo "$RESULT" | head -3
fi

# 89. Logan County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Logan County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "07", h.court_name = "Logan County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Logan County District Court"
elif echo "$RESULT" | grep -q "Logan County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Logan County District Court"
else
  echo "  ❌ Error: Logan County District Court"
  echo "$RESULT" | head -3
fi

# 90. Anderson County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Anderson County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "53", h.court_name = "Anderson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Anderson County District Court, Division 01"
elif echo "$RESULT" | grep -q "Anderson County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Anderson County District Court, Division 01"
else
  echo "  ❌ Error: Anderson County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 91. Jefferson County District Court, Division 02
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 02", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "02", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 02"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 02"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 02"
else
  echo "  ❌ Error: Jefferson County District Court, Division 02"
  echo "$RESULT" | head -3
fi

# 92. Jefferson County District Court, Division 15
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Jefferson County District Court, Division 15", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "15", h.district_number = "30", h.court_name = "Jefferson County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Jefferson County District Court, Division 15"
elif echo "$RESULT" | grep -q "Jefferson County District Court, Division 15"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Jefferson County District Court, Division 15"
else
  echo "  ❌ Error: Jefferson County District Court, Division 15"
  echo "$RESULT" | head -3
fi

# 93. Pike County District Court, Division 01
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Pike County District Court, Division 01", group_id: "roscoe_graph"}) ON CREATE SET h.division_number = "01", h.district_number = "35", h.court_name = "Pike County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Pike County District Court, Division 01"
elif echo "$RESULT" | grep -q "Pike County District Court, Division 01"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Pike County District Court, Division 01"
else
  echo "  ❌ Error: Pike County District Court, Division 01"
  echo "$RESULT" | head -3
fi

# 94. Bell County District Court
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:DistrictDivision {name: "Bell County District Court", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "44", h.court_name = "Bell County District Court", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Bell County District Court"
elif echo "$RESULT" | grep -q "Bell County District Court"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Bell County District Court"
else
  echo "  ❌ Error: Bell County District Court"
  echo "$RESULT" | head -3
fi

echo ""
echo "DistrictDivision Summary: Created=$CREATED_COUNT, Matched=$MATCHED_COUNT"
echo ""

echo "Ingesting AppellateDistrict: 5 entities..."
CREATED_COUNT=0
MATCHED_COUNT=0

# 1. Kentucky Court of Appeals, Lexington Office
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:AppellateDistrict {name: "Kentucky Court of Appeals, Lexington Office", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "Lexington", h.region = "Central KY", h.counties = "Lexington area", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Court of Appeals, Lexington Office"
elif echo "$RESULT" | grep -q "Kentucky Court of Appeals, Lexington Office"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Court of Appeals, Lexington Office"
else
  echo "  ❌ Error: Kentucky Court of Appeals, Lexington Office"
  echo "$RESULT" | head -3
fi

# 2. Kentucky Court of Appeals, Louisville Office
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:AppellateDistrict {name: "Kentucky Court of Appeals, Louisville Office", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "Louisville", h.region = "Louisville Metro", h.counties = "Jefferson", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Court of Appeals, Louisville Office"
elif echo "$RESULT" | grep -q "Kentucky Court of Appeals, Louisville Office"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Court of Appeals, Louisville Office"
else
  echo "  ❌ Error: Kentucky Court of Appeals, Louisville Office"
  echo "$RESULT" | head -3
fi

# 3. Kentucky Court of Appeals, Covington Office
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:AppellateDistrict {name: "Kentucky Court of Appeals, Covington Office", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "Covington", h.region = "Northern KY", h.counties = "Kenton/Campbell", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Court of Appeals, Covington Office"
elif echo "$RESULT" | grep -q "Kentucky Court of Appeals, Covington Office"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Court of Appeals, Covington Office"
else
  echo "  ❌ Error: Kentucky Court of Appeals, Covington Office"
  echo "$RESULT" | head -3
fi

# 4. Kentucky Court of Appeals, Frankfort Office
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:AppellateDistrict {name: "Kentucky Court of Appeals, Frankfort Office", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "Frankfort", h.region = "Capital", h.counties = "Franklin", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Court of Appeals, Frankfort Office"
elif echo "$RESULT" | grep -q "Kentucky Court of Appeals, Frankfort Office"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Court of Appeals, Frankfort Office"
else
  echo "  ❌ Error: Kentucky Court of Appeals, Frankfort Office"
  echo "$RESULT" | head -3
fi

# 5. Kentucky Court of Appeals, Paducah Office
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:AppellateDistrict {name: "Kentucky Court of Appeals, Paducah Office", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "Paducah", h.region = "Western KY", h.counties = "McCracken", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Court of Appeals, Paducah Office"
elif echo "$RESULT" | grep -q "Kentucky Court of Appeals, Paducah Office"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Court of Appeals, Paducah Office"
else
  echo "  ❌ Error: Kentucky Court of Appeals, Paducah Office"
  echo "$RESULT" | head -3
fi

echo ""
echo "AppellateDistrict Summary: Created=$CREATED_COUNT, Matched=$MATCHED_COUNT"
echo ""

echo "Ingesting SupremeCourtDistrict: 7 entities..."
CREATED_COUNT=0
MATCHED_COUNT=0

# 1. Kentucky Supreme Court, District 1
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:SupremeCourtDistrict {name: "Kentucky Supreme Court, District 1", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "1", h.region = "Western KY", h.counties = "Paducah area", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Supreme Court, District 1"
elif echo "$RESULT" | grep -q "Kentucky Supreme Court, District 1"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Supreme Court, District 1"
else
  echo "  ❌ Error: Kentucky Supreme Court, District 1"
  echo "$RESULT" | head -3
fi

# 2. Kentucky Supreme Court, District 2
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:SupremeCourtDistrict {name: "Kentucky Supreme Court, District 2", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "2", h.region = "North Central KY", h.counties = "Louisville/Jefferson", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Supreme Court, District 2"
elif echo "$RESULT" | grep -q "Kentucky Supreme Court, District 2"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Supreme Court, District 2"
else
  echo "  ❌ Error: Kentucky Supreme Court, District 2"
  echo "$RESULT" | head -3
fi

# 3. Kentucky Supreme Court, District 3
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:SupremeCourtDistrict {name: "Kentucky Supreme Court, District 3", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "3", h.region = "Northern KY", h.counties = "Kenton/Campbell/Boone", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Supreme Court, District 3"
elif echo "$RESULT" | grep -q "Kentucky Supreme Court, District 3"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Supreme Court, District 3"
else
  echo "  ❌ Error: Kentucky Supreme Court, District 3"
  echo "$RESULT" | head -3
fi

# 4. Kentucky Supreme Court, District 4
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:SupremeCourtDistrict {name: "Kentucky Supreme Court, District 4", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "4", h.region = "Bluegrass", h.counties = "Fayette/Lexington", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Supreme Court, District 4"
elif echo "$RESULT" | grep -q "Kentucky Supreme Court, District 4"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Supreme Court, District 4"
else
  echo "  ❌ Error: Kentucky Supreme Court, District 4"
  echo "$RESULT" | head -3
fi

# 5. Kentucky Supreme Court, District 5
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:SupremeCourtDistrict {name: "Kentucky Supreme Court, District 5", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "5", h.region = "Eastern KY", h.counties = "Boyd/Greenup area", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Supreme Court, District 5"
elif echo "$RESULT" | grep -q "Kentucky Supreme Court, District 5"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Supreme Court, District 5"
else
  echo "  ❌ Error: Kentucky Supreme Court, District 5"
  echo "$RESULT" | head -3
fi

# 6. Kentucky Supreme Court, District 6
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:SupremeCourtDistrict {name: "Kentucky Supreme Court, District 6", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "6", h.region = "South Central KY", h.counties = "Bowling Green area", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Supreme Court, District 6"
elif echo "$RESULT" | grep -q "Kentucky Supreme Court, District 6"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Supreme Court, District 6"
else
  echo "  ❌ Error: Kentucky Supreme Court, District 6"
  echo "$RESULT" | head -3
fi

# 7. Kentucky Supreme Court, District 7
RESULT=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MERGE (h:SupremeCourtDistrict {name: "Kentucky Supreme Court, District 7", group_id: "roscoe_graph"}) ON CREATE SET h.district_number = "7", h.region = "Capital", h.counties = "Franklin/Frankfort", h.created_at = timestamp() ON MATCH SET h.updated_at = timestamp() RETURN h.name" --raw 2>&1)
if echo "$RESULT" | grep -q "Nodes created: 1"; then
  ((CREATED_COUNT++))
  echo "  ✓ Created: Kentucky Supreme Court, District 7"
elif echo "$RESULT" | grep -q "Kentucky Supreme Court, District 7"; then
  ((MATCHED_COUNT++))
  echo "  ⊙ Exists: Kentucky Supreme Court, District 7"
else
  echo "  ❌ Error: Kentucky Supreme Court, District 7"
  echo "$RESULT" | head -3
fi

echo ""
echo "SupremeCourtDistrict Summary: Created=$CREATED_COUNT, Matched=$MATCHED_COUNT"
echo ""

# Post-ingestion verification
AFTER=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (n) RETURN count(n)" --raw | grep -E "^[0-9]+$" | head -1)
ADDED=$((AFTER - BEFORE))
echo "======================================================================="
echo "INGESTION COMPLETE"
echo "======================================================================="
echo "Nodes before: $BEFORE"
echo "Nodes after: $AFTER"
echo "Nodes added: $ADDED"
echo "Expected: 192"
echo ""

# Verify Abby Sitgraves case integrity (canary)
ABBY_RELS=$(docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (c:Case {name: \"Abby-Sitgraves-MVA-7-13-2024\"})-[r]-() RETURN count(r)" --raw | grep -E "^[0-9]+$" | head -1)
echo "Abby Sitgraves relationships: $ABBY_RELS (should be 93)"
echo ""

# List all division types
echo "Division types in graph:"
docker exec roscoe-graphdb redis-cli -p 6379 GRAPH.QUERY roscoe_graph "MATCH (d) WHERE labels(d)[0] CONTAINS \"Division\" RETURN labels(d)[0], count(*) ORDER BY labels(d)[0]" --raw | grep -v "Cached"
echo ""
echo "✅ Phase 1b complete"