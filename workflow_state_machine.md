1. Phase\_0\_onboarding  
   1. [README.MD](http://README.MD)  
   2. [landmarks.md](http://landmarks.md)  
      1. Client\_info\_received  
      2. Contract\_signed  
      3. medical\_auth\_signed  
   3. Workflows  
      1. Case\_setup  
         1) [workflow.md](http://workflow.md)  
         2) Tools  
            1) create\_case.py  
      2. Document\_collection  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Document-intake  
               1) skill.md  
            2) Document-request  
               1) skill.md  
            3) Docusign-send  
               1) [skill.md](http://skill.md)  
               2) Tools  
                  1) Docusign\_config.py  
                  2) docusign\_send.py  
                       
               3) References  
                  1) [anchor-strings.md](http://anchor-strings.md)  
                  2) [multiple-signers.md](http://multiple-signers.md)  
                  3) [tool-usage.md](http://tool-usage.md)  
                  4) tracking.md  
         3) Templates  
            1) [document-checklist.md](http://document-checklist.md)  
            2) [request-email.md](http://request-email.md)  
            3) Intake\_forms  
               1)  2021 Whaley Authorization of Digitally Signature Replication (1).pdf  
               2) 2021 Whaley CMS Medicare Verification Form (1).pdf  
               3)   \- 2021 Whaley MVA Accident Detail Information Sheet (1).pdf  
               4) 2021 Whaley MVA Fee Agreement (1).pdf  
               5)   \- 2021 Whaley Medical Authorization (HIPAA) (1).pdf  
               6)   \- 2021 Whaley Medical Treatment Questionnaire (1).pdf  
               7)   \- 2021 Whaley New Client Information Sheet (1).pdf  
               8)   \- 2021 Whaley S\&F Accident Detail Information Sheet (1).pdf  
               9)   \- 2021 Whaley S\&F Fee Agreement (1).pdf  
               10)   \- 2021 Whaley WC Fee Agreement \- Final (1).pdf  
               11)   \- 2021 Whaley Wage & Salary Verification (1).pdf  
               12)   \- INDEX.md  
         4) tools  
2. Phase\_1\_file\_setup  
   1. [readme.md](http://readme.md)  
   2. [landmarks.md](http://landmarks.md)  
      1. Full\_intake\_complete  
      2. Accident\_report\_obtained  
      3. insurance\_claims\_setup (with BI/PIP sub-steps)  
      4. providers\_setup  
   3. Workflows  
      1. accident\_report/  
         1) [workflow.md](http://workflow.md)  
         2) skills/  
            1) Police-report-analysis  
               1) [skill.md](http://skill.md)  
               2) References  
                  1)  kentucky\_codes.md  
                  2)   \- output\_template.md  
                  3)   \- tool-usage.md  
         3) Templates  
         4) Tools  
            1) Lexis\_crash\_order.py  
            2) read\_pdf.py  
      2. insurance\_bi\_claim/  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Liability\_analysis  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) comparative-fault.md  
                  2)  denied-liability.md  
                  3)  evidence-recommendations.md  
                  4)  passenger-scenarios.md  
                  5)  um-uim-claims.md  
            2) Lor-generator  
               1) [skill.md](http://skill.md)  
               2) Tools  
                  (i) generate\_document.py  
                    
               3) references  
                  1) error-handling.md  
                  2) placeholder-mapping.md  
                  3) tool-usage.md  
         3) Templates  
            1) 2022 Whaley LOR to BI Adjuster(1)(1)(1) (1).docx  
         4) Tools  
            1) generate\_document.py  
      3. Insurance\_pip\_claim  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Pip-aplication  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) Common-issues.md  
                  2) Field-mapping.md  
                  3) form-sections.md  
            2) Pip-waterfall  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) disqualification.md  
                  2) kac-process.md  
                  3) tool-usage.md  
                  4) waterfall-steps.md  
         3) Templates  
            1) 2022 Whaley LOR to PIP Adjuster(1)(1) (1).docx  
            2) KACP-Application-03.2021(1) (1).pdf  
         4) Tools  
            1) Generate\_document.py  
            2) pip\_waterfall.py  
      4. Medical\_provider\_setup  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Medical-records-request  
               1) Skills  
               2) Tools  
                  1) generate\_document.py  
               3) References  
                  1) error-handling.md  
                  2) follow-up-process.md  
                  3) sending-methods.md  
                  4) [template-placeholders.md](http://template-placeholders.md)  
         3) Templates  
            1) 2022 Whaley Medical Record Request (URR) (1).docx  
            2) 2023 Whaley Initial Medical Billing Request to Provider (MBR) (1).pdf  
            3) 2023 Whaley Law Firm Medical Request Template (1).pdf  
         4) Tools  
            1) Generate\_document.py  
      5. Send\_documents\_for\_signature.md  
3. Phase\_2\_treatment  
   1. [README.MD](http://README.MD)  
   2. Landmarks  
      1. Client\_check\_in\_schedule\_active  
      2. All\_providers\_have\_records\_requested  
      3. Records\_received(per-provider)  
      4. bills\_received(per-provider)  
      5. Liens\_identified  
      6. Medical\_chronology\_started  
      7. Treatment\_status\_known  
      8. Treatment\_complete  
      9. Exit\_conditions  
         1) Early\_demand\_conditions\_met  
         2) SOL\_critical  
   3. Workflows  
      1. Client\_check\_in  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Calendar-scheduling  
               1) [skill.md](http://skill.md)  
               2) References  
         3) Templates  
            1) Check\_in\_note.md  
      2. Lien\_identification  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Lien-classification  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) erisa-subrogation.md  
                  2) medicaid-liens.md  
                  3) medicare-liens.md  
                  4) [provider-liens.md](http://provider-liens.md)  
         3) Templates  
            1) Lien\_inventory.md  
      3. Medical\_chronology  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Medical-chronology-generation  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) [extraction-fields.md](http://extraction-fields.md)  
                  2) [red-flags.md](http://red-flags.md)  
                  3) [research-process.md](http://research-process.md)  
               3) Templates  
                  1) Chronology\_entry.md  
               4) Tools  
                  1) Chronology\_tools.py  
                  2) Read\_pdf.py  
      4. Medical\_provider\_status  
         1) [workflow.md](http://workflow.md)  
         2) Templates  
            1) Provider\_status\_summary.md  
      5. Referral\_new\_provider  
         1) [workflow.md](http://workflow.md)  
         2) Templates  
            1) Referral\_note.md  
      6. Request\_records\_bills  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Medical-records-request  
               1) [skill.md](http://skill.md)  
               2) Tools  
                  1) Generate\_document.py  
               3) References  
                  1) Error-handling.md  
                  2) [follow-up-process.md](http://follow-up-process.md)  
                  3) [sending-methods.md](http://sending-methods.md)  
                  4) [template-placeholders.md](http://template-placeholders.md)  
         3) Templates  
            1) Records\_request\_template.md  
         4) Tools  
            1) Generate\_document.py  
            2) Medical\_request\_generator.py  
            3) Read\_pdf.py  
4. Phase\_3\_demand  
   1. [readme.md](http://readme.md)  
   2. [landmarks.md](http://landmarks.md)  
      1. All\_records\_received  
      2. All\_bills\_received  
      3. Special\_damages\_calculated  
      4. Medical\_chronology\_finalized  
      5. Liens\_identified  
      6. Wage\_loss\_documented  
      7. Demad\_draft\_prepared  
      8. Exhibits\_compiled  
      9. Attorney\_approved  
      10. Demand\_sent  
      11. Client\_notified  
      12. Follow-up-scheduled  
   3. Workflows  
      1. Draft\_demand  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) [skill.md](http://skill.md)  
            2) References  
               1) demand-valuation.md  
               2) exhibit-compilation.md  
               3) [narrative-sections.md](http://narrative-sections.md)  
         3) Templates  
            1) Demand\_letter\_template.md  
            2) Demand\_template.md  
         4) Tools  
            1) Firm\_config.json  
            2) Generate\_demand\_pdf.py  
            3) Read\_pdf.py  
      2. Gather\_demand\_materials  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Damages-calculation  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) Code\_extraction.md  
                  2) [wage-calculation.md](http://wage-calculation.md)  
            2) Lien-classification  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) erisa-subrogation.md  
                  2) medicaid-liens.md  
                  3) medicare-liens.md  
                  4) [provider-liens.md](http://provider-liens.md)  
            3) Medical-chronology-generation  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) extraction-fields.md  
                  2) red-flags.md  
                  3) [research-process.md](http://research-process.md)  
         3) Templates  
            1) Materials\_checklist.md  
         4) Tools  
            1) Chronology\_tools.py  
            2) Generate\_document.py  
            3) Read\_pdf.py  
      3. Send\_demand  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Calendar-scheduling  
               1) [skill.md](http://skill.md)  
               2) References  
         3) Templates  
            1) Demand\_tracking.md  
5. Phase\_4\_negotiation  
   1. [readme.md](http://readme.md)  
   2. [landmarks.md](http://landmarks.md)  
      1. One\_week\_followup\_completed  
      2. Deficiencies\_addressed  
      3. Thirty-day-follow-up-completed  
      4. Initial-offer-received  
      5. Net-to-client-calculated  
      6. Offer-evaluated-by-attorney  
      7. Client-authorized-decision  
      8. Iterative-negotiation-documented  
      9. Settlement-reached  
      10. Negotiation-impasse  
   3. Workflows  
      1. Negotiated\_claim  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Calendar-scheduling  
               1) [skill.md](http://skill.md)  
            2) Negotiation-strategy  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) [counter-strategies.md](http://counter-strategies.md)  
                  2) [tactics.md](http://tactics.md)  
         3) Templates  
            1) Counter\_offer\_letter.md  
            2) Settlement\_summary.md  
         4) Tools  
            1) Generate\_document.py  
      2. Offer-evaluation  
         1) [skill.md](http://skill.md)  
         2) References  
            1) [comparable-analysis.md](http://comparable-analysis.md)  
            2) [net-calculation.md](http://net-calculation.md)  
         3) Templates  
            1) Offer\_analysis\_template.md  
      3. Track\_offers  
         1) [workflows.md](http://workflows.md)  
         2) Skills  
            1) Offer\_tracking  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) Tracking-fields  
         3) Templates  
            1) Negotiation\_summary.md  
6. Phase\_5\_settlement  
   1. [readme.md](http://readme.md)  
   2. [landmarks.md](http://landmarks.md)  
      1. Settlement\_statement\_prepared  
      2. Authorization\_to\_settle\_prepared  
      3. Client\_signed\_authorization  
      4. Settlement\_confirmed\_with\_adjuster  
      5. Release\_received  
      6. Release\_signed\_by\_client  
      7. Release\_returned\_to\_insurance  
      8. Settlement\_check\_received  
      9. Check\_deposited\_and\_cleared  
      10. Liens\_paid  
      11. Client\_received\_funds  
   3. Workflows  
      1. Lien\_negotiation  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Lien\_classification  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) erisa-subrogation.md  
                  2) medicaid-liens.md  
                  3) medicare-liens.md  
                  4) [provider-liens.md](http://provider-liens.md)  
            2) Lien\_resolution  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) medicaid-process.md  
                  2) [medicare-process.md](http://medicare-process.md)  
         3) Templates  
            1) Lien\_reduction\_letter.md  
      2. Settlement\_processing  
         1) [workflow.md](http://workflow.md)  
         2) [skills.md](http://skills.md)  
            1) Docusign-send  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) anchor-strings.md  
                  2) multiple-signers.md  
                  3) tool-usage.md  
                  4) [tracking.md](http://tracking.md)  
            2) Settlement-statement  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) fee-calculation.md  
                  2) [trust-requirements.md](http://trust-requirements.md)  
               3) Templates  
                  1) Authorization\_to\_settle.md  
                  2) Settlement\_statemen.md  
               4) Tools  
                  1) Generate\_document.py  
7. Phase\_6\_lien  
   1. [readme.md](http://readme.md)  
   2. [landmarks.md](http://landmarks.md)  
      1. Outstanding\_liens\_identified  
      2. Final\_lien\_amounts\_requested  
      3. Medicare\_final\_demand\_received  
      4. Lien\_negotiations\_complete  
      5. All\_liens\_paid  
      6. Supplement\_settlement\_statement\_prepared  
      7. Final\_distribution\_complete  
   3. Workflows  
      1. Final\_distribution  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Supplement-statement  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) Calculation-guide  
         3) Templates  
            1) Supplemental\_settlement\_statement.md  
         4) Tools  
            1) Generate\_document.py  
      2. Get\_final\_lien  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Final-lien-request  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) [lien-type-contacts.md](http://lien-type-contacts.md)  
         3) Templates  
            1) Final\_lien\_request.md  
      3. Negotiate\_lien  
         1) [workflow.md](http://workflow.md)  
         2) Skills  
            1) Lien-reduction  
               1) [skill.md](http://skill.md)  
               2) References  
                  1) compromise-waiver.md  
                  2) [erisa-negotiation.md](http://erisa-negotiation.md)  
         3) Templates  
            1) Lien\_reduction\_request.md  
8. Phase\_7\_litigation  
   1. [readme.md](http://readme.md)  
   2. [landmarks.md](http://landmarks.md)  
      1. Litigation\_commenced  
      2. Complaint\_filed  
         1) Defendant\_served  
         2) Answer-response-received  
         3) Scheduling\_order\_entered  
      3. Discovery  
         1) Written\_discovery\_complete  
         2) Depositions\_complete  
      4. Mediation  
         1) Mediation\_attended  
      5. Trial\_prep  
         1) Expert\_disclosures\_filed  
         2) Trial\_ready  
      6. Trial\_concluded  
   3. Subphases  
      1. complaint  
         1) [readme.md](http://readme.md)  
         2) [landmarks.md](http://landmarks.md)  
            1) Complaint\_drafted  
            2) Complaint\_filed  
            3) Summons\_issued  
            4) Defendant\_served  
            5) Answer\_received\_or\_default\_sought  
            6) All\_defendants\_resolved  
         3) Complaint\_library  
            1) [readme.md](http://readme.md)  
            2) Decision\_tree.md  
            3) Supporting  
               1) Certificate\_of\_eservice.md  
               2) Certificate\_of\_service.md  
               3) notice\_to\_bi\_adjuster.md  
            4) Templates  
               1) Base  
                  1) mva\_standard.md  
                  2) mva\_um.md  
                  3) mva\_uim.md  
                  4) mva\_vicarious\_liability.md  
                  5) mva\_negligent\_entrustment.md  
                  6) mva\_stolen\_vehicle\_fraud.md  
                  7) premises\_standard.md  
                  8) premises\_dog\_bite.md  
                  9) premises\_government\_entity.md  
                  10) bi\_with\_bad\_faith.md  
                  11) Bi\_bad\_faith\_uim.md  
               2) Modules  
                  1) count\_negligence.md  
                  2) count\_um.md  
                  3) count\_uim.md  
                  4) count\_vicarious\_liability.md  
                  5) count\_negligent\_entrustment.md  
                  6) count\_parental\_liability.md  
                  7) count\_fraud.md  
                  8) Count\_bad\_faith.md  
         4) Workflows  
            1) Draft\_file\_complaint  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Complaint-drafting  
                     1) [skill.md](http://skill.md)  
                     2) References  
                        1) caption-format.md  
                        2) [cause-action-templates.md](http://cause-action-templates.md)  
                        3) [court-rules.md](http://court-rules.md)  
               3) Templates  
                  1) Complaint\_template.md  
               4) Tools  
                  1) Generate\_document.py  
            2) Process\_answer  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Answer-analysis  
                     1) [skill.md](http://skill.md)  
                     2) References  
                        1) [alternative-defenses.md](http://alternative-defenses.md)  
                        2) [counterclaim-handling.md](http://counterclaim-handling.md)  
               3) Templates  
                  1) [answer-summary.md](http://answer-summary.md)  
            3) Serve\_defendant  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Service-of-process  
                     1) [skill.md](http://skill.md)  
                     2) References  
                        1) Proof-of-service.md  
                        2) [service-methods.md](http://service-methods.md)  
               3) Templates  
                  1) Service\_tracking.md  
                  2) Special\_bailiff\_affidavit.md  
                  3) special\_baliff\_order.md

                     

                     

      2. Discovery  
         1) [readme.md](http://readme.md)  
         2) [landmarks.md](http://landmarks.md)  
            1) Our\_discovery\_propounded  
            2) Defendant\_responses\_received  
            3) Our\_responses\_served  
            4) Client\_deposition\_complete  
            5) Defendant\_deposition\_complete  
            6) Discovery\_cutoff\_passed  
         3) Deposition\_library  
            1) [readme.md](http://readme.md)  
            2) Decision\_tree.md  
            3) Skills  
               1) Corp-rep-deposition  
                  1) [skill.md](http://skill.md)  
               2) Deposition-defense  
                  1) [skill.md](http://skill.md)  
               3) Expert-deposition  
                  1) [skill.md](http://skill.md)  
               4) Rules-based-examination  
                  1) [skill.md](http://skill.md)  
            4) References  
               1) Client\_defense  
                  1) [readme.md](http://readme.md)  
                  2) Day\_of\_support.md  
                  3) Objections\_guide.md  
                  4) Post\_analysis.md  
                  5) Pre\_deposition.md  
               2) Corp\_rep  
                  1) [readme.md](http://readme.md)  
                  2) Know\_nothing.md  
                  3) Sample\_topics.md  
                  4) Strategic\_goals.md  
                  5) Topic\_drafting.md  
               3) Expert\_depo  
                  1) [readme.md](http://readme.md)  
                  2) Conflict\_mapping.md  
                  3) Dossier\_compilation.md  
                  4) Juror\_archetypes.md  
                  5) Trial\_preservation.md  
               4) Rules\_framework  
                  1) [readme.md](http://readme.md)  
                  2) Question\_frameworks.md  
                  3) Rule\_discovery.md  
                  4) Transcript\_extraction.md  
            5) Templates  
               1) Client\_prep  
                  1) Client\_checklist.md  
                  2) Client\_letter.md  
                  3) Privilege\_review.md  
               2) Notices  
                  1) Notice\_corp\_rep.md  
                  2) Notice\_corp\_rep\_pip.md  
                  3) Notice\_corp\_rep\_uim.md  
                  4) Notice\_expert.md  
                  5) Notice\_standard.md  
                  6) Notice\_video.md  
               3) Outlines  
                  1) Outline\_corp\_rep.md  
                  2) Outline\_expert.md  
                  3) Outline\_rules\_based.md  
               4) Tracking  
                  1) Depo\_schedule.md  
                  2) Testimony\_tracker.md  
         4) Discovery\_library  
            1) [readme.md](http://readme.md)  
            2) Analysis  
               1) Defense\_answer\_review.md  
               2) Meet\_and\_confer\_guide.md  
               3) Motion\_to\_compel\_outline.md  
               4) Response\_deficiency\_checklist.md  
            3) Propounding  
               1) Decision\_tree.md  
               2) Modules  
                  1) Mod\_cell\_phone.md  
                  2) Mod\_employment\_scope.md  
                  3) Mod\_expert\_disclosure.md  
                  4) Mod\_insurance\_coverage.md  
                  5) Mod\_prior\_incidents.md  
                  6) Mod\_witness\_identification.md  
               3) Templates  
                  1) Interrogatories  
                     1) Bad\_faith.md  
                     2) Mva\_pip.md  
                     3) Mva\_respondeat\_superior.md  
                     4) Mva\_standard.md  
                     5) Mva\_trucking\_company.md  
                     6) Mva\_trucking\_driver.md  
                     7) Mva\_um\_uim.md  
                     8) Premises\_standard.md  
                  2) Rfas  
                     1) Bad\_faith.md  
                     2) Mva\_damages.md  
                     3) Mva\_liability.md  
                     4) Premises\_liability.md  
                  3) Rfps  
                     1) Bad\_faith.md  
                     2) Mva\_damages.md  
                     3) Mva\_liability.md  
                     4) Premises\_liability.md  
            4) Responding  
               1) Decision\_tree.md  
               2) References  
                  1) Privilege\_log.md  
                  2) Valid\_objections.md  
                  3) Verification\_page.md  
               3) Templates  
                  1) General\_objections.md  
                  2) Response\_shell.md  
            5) Workflows  
               1) Client\_deposition\_prep  
                  1) [workflow.md](http://workflow.md)  
                  2) Skills  
                     1) Deposition-defense  
                        1) [skill.md](http://skill.md)  
                        2) References  
                        3) [common-traps.md](http://common-traps.md)  
                        4) [preparation-checklist.md](http://preparation-checklist.md)  
               2) Corp\_rep\_deposition  
                  1) [workflow.md](http://workflow.md)  
               3) Defense\_expert\_depo  
                  1) [workflow.md](http://workflow.md)  
               4) Party\_depositions  
                  1) [workflow.md](http://workflow.md)  
                  2) Skills  
                     1) Deposition-planning  
                        1) [skill.md](http://skill.md)  
                        2) [depo-outline.md-exhibit-management.md](http://depo-outline.md-exhibit-management.md)  
               5) Propound\_discovery  
                  1) [workflow.md](http://workflow.md)  
                  2) Skills  
                     1) Discovery-drafting  
                        1) [skill.md](http://skill.md)  
                        2) [interrogatory-templates.md](http://interrogatory-templates.md)  
                        3) [rfa-templates.md](http://rfa-templates.md)  
                        4) [rfp-templates.md](http://rfp-templates.md)  
               6) Respond\_to\_discovery  
                  1) [workflow.md](http://workflow.md)  
                  2) Skills  
                     1) Discovery-response  
                        1) [skill.md](http://skill.md)  
                        2) [common-objections.md](http://common-objections.md)  
                        3) [privilege-log.md](http://privilege-log.md)  
               7) Review\_responses  
                  1) [workflows.md](http://workflows.md)  
                  2) Skills  
                     1) Response-analysis  
                        1) [skill.md](http://skill.md)  
                        2) [deficiency-checklist.md](http://deficiency-checklist.md)  
                        3) [motion-to-compel.md](http://motion-to-compel.md)  
               8) Third\_party\_deposition  
                  1) [workflow.md](http://workflow.md)  
      3. Mediation  
         1) [readme.md](http://readme.md)  
         2) [landmarks.md](http://landmarks.md)  
            1) Mediation-scheduled  
            2) Mediation-brief-submitted  
            3) Client-prepared  
            4) Mediation-attended  
         3) Workflows  
            1) Attend\_mediation  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Mediation-strategy  
                     1) [skill.md](http://skill.md)  
                     2) References  
                        1) [negotiation-tactics.md](http://negotiation-tactics.md)  
                        2) [settlement-authority.md](http://settlement-authority.md)  
            2) Prepare\_mediation  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Mediation-prep  
                     1) [skill.md](http://skill.md)  
                     2) References	  
                        1) [damage-summary.md](http://damage-summary.md)  
                        2) [mediationbrief-template.md](http://mediation0brief-template.md)  
      4. Trial\_prep  
         1) [readme.md](http://readme.md)  
         2) [landmarks.md](http://landmarks.md)  
            1) Expert\_disclosures\_filed  
            2) Expert\_depositions\_complete  
            3) Exhibit\_list\_filed  
            4) Witness\_list\_filed  
            5) Pretrial\_brief\_filed  
            6) Trial\_ready  
         3) Workflows  
            1) Expert\_management  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Expert-coordination  
                     1) [skill.md](http://skill.md)  
                     2) References  
                        1) [disclosure-requirements.md](http://disclosure-requirements.md)  
                        2) [rebuttal-timing.md](http://rebuttal-timing.md)  
            2) Trial\_materials  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Trial-exhibit-prep  
                     1) [skill.md](http://skill.md)  
                     2) References  
                        1) [exhibit-list-format.md](http://exhibit-list-format.md)  
                        2) [jury-instructions.md](http://jury-instructions.md)  
                        3) [witness-list.md](http://witness-list.md)  
      5. Trial  
         1) [readme.md](http://readme.md)  
         2) [landmarks.md](http://landmarks.md)  
            1) Jury-selected  
            2) Plaintiffs-case-presented  
            3) All-evidence-closed  
            4) Verdict-rendered  
         3) Workflows  
            1) Conduct\_trial  
               1) [workflow.md](http://workflow.md)  
               2) Skills  
                  1) Trial-presentation  
                     1) [skill.md](http://skill.md)  
                     2) References  
                        1) Opening-structure.md  
                        2) [direct-examination.md](http://direct-examination.md)  
                        3) [closing-structure.md](http://closing-structure.md)  
9. Closed  
   1. [readme.md](http://readme.md)  
   2. [landmarks.md](http://landmarks.md)  
      1. All-obligations-verified  
      2. Final-letter-sent  
      3. Review-requested  
      4. Physical-file-archived  
      5. Digital-file-archived  
      6. Case-fully-closed  
   3. Workflows  
      1. close\_case.md

         

         

         

         

         

         

         

         

         

         

         

         

         

         

         

         

       


         

         

         

         

         

					      						

					

					  
