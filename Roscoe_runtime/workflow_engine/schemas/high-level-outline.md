Here is a high-level of what I want it to do:And it does a lot of this already. Follow this hierarchy.(workflow and skill designations and numbers are strictly illustrative placeholders)

I. Project
   A. Phase_1_intake: Landmarks 1. HIPAA Authorization, 2. Retainer Agreement, 3. Intake Form
      1. Workflow_1_intake
        A. Skill_1_intake
        B. Skill_2_intake
       
      2. Workflow_2_intake
        A. Skill_1_intake
        B. Skill_2_intake
      
      3. Workflow_3_intake
        A. Skill_1_intake
        B. Skill_2_intake
      
  B. Phase_2_file_setup: Landmarks 1. Accident Report, 2. Insurance Claims, 3. Medical Providers Setup, 4. Employment Documentation, 5. Health Insurance Liens
      1. Workflow_1_file_setup
        A. Skill_1_file_setup
        B. Skill_2_file_setup
      
      2. Workflow_2_file_setup
        A. Skill_1_file_setup
        B. Skill_2_file_setup
      
      3. Workflow_3_file_setup
        A. Skill_1_file_setup
        B. Skill_2_file_setup 
  
  C. Phase_3_treatment: Landmarks 1. Medical Provider Setup, 2. Request Records & Bills, 3. Client Check-In, 4. Lien Identification
      1. Workflow_1_treatment: 
        A. Skill_1_treatment
        B. Skill_2_treatment
    
  D. Phase_3_demand: Landmarks 1. Get remaining records and bills, 2. Finalize medical chronology, 3. Calculate special damages, 4. Assemble supporting documentation, 5. Attorney approval, 6. Send demand
      1. Workflow_1_demand: 
        A. Skill_1_demand
        B. Skill_2_demand
   
  D. Phase_4_negotiation: Landmarks 1. One-Week Follow-Up, 2. Deficiencies Addressed, 3. Thirty-Day Follow-Up, 4. Initial Offer Received, 5. Client Authorization, 6. Iterative Negotiation, 7. Settlement Acceptance
      1. Workflow_1_negotiation
        A. Skill_1_negotiation
        B. Skill_2_negotiation
      
      2. Workflow_2_negotiation
        A. Skill_1_negotiation
        B. Skill_2_negotiation
      
      3. Workflow_3_negotiation
        A. Skill_1_negotiation
        B. Skill_2_negotiation

  E. Phase_5_settlement: Landmarks 1. Settlement Breakdown, 2. Settlement Processing, 3. Lien Identification, 4. Final Distribution
      1. Workflow_1_settlement
        A. Skill_1_settlement
        B. Skill_2_settlement
      
      2. Workflow_2_settlement
        A. Skill_1_settlement
        B. Skill_2_settlement
      
      3. Workflow_3_settlement
        A. Skill_1_settlement
        B. Skill_2_settlement

  F. Phase_6_litigation:
      1. Workflow_1_litigation
        A. Skill_1_litigation
        B. Skill_2_litigation
      
      2. Workflow_2_litigation
        A. Skill_1_litigation
        B. Skill_2_litigation
      
      3. Workflow_3_litigation
        A. Skill_1_litigation
        B. Skill_2_litigation


The state_machine loads what the phase is and what the state is and then also loads the dynamic actual data and compares it and I know the system does this just fine.
And then after it's determined exactly where it is in the process, what phase, what workflows are done, have been done, it then tells the agent, which tells the user that we're in such and such phase. We have completed such and such workflows. We are on this step of this workflow. We have fulfilled these landmarks as each phase has landmarks that it has to achieve to advance to the next phase.
And so it would say we are on step 2 of workflow XYZ and then reference where that is, like a file path.Because then that workflow will actually exist as a Markdown document.The agent can then go to that document and just follow the workflow.If there are granular things it needs to do besides say checklists or informational, then it goes and uses skills.The workflow document will reference the skill path to go do that skill. So if it's on step 3 and step 3 is skill XYZ, it'll say perform skill XYZ.
And then skill XYZ will be what it is, granular step-by-step actions to take to the agent with tools, references, etc.With the goal of achieving whatever objective and landing markets trying to acquire.When that's done it marks it as done, updates the JSON, and then reruns the state machine. Then it says, "Okay, that's workflow's done, now we have to do this workflow."
The agent keeps going until it reaches a blocker, and then it reports that to the user. At any time this state is loaded until the blocker is unblocked, it just reports to the user where is this blocker?
