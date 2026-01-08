 Graph possibilities:
 
 (Client)-[:TREATED_AT]->(Location: "Norton Orthopedic Institute - Downtown")
                                ↓ [PART_OF]
                           (Facility: "Norton Orthopedic Institute")
                                ↓ [PART_OF]
                           (HealthSystem: "Norton Healthcare")

          
             
                          (HealthSystem: "Norton Healthcare")
                                [Has_Facility]                     
 (Client)-[:TREATED_AT]->(Facility: "Norton Orthopedic Institute")
                                [Has_Location]
                         (Location: "Norton Orthopedic Institute - Downtown")

                         
                                                