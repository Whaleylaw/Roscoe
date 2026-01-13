 Here is Claude's plan:                                                                                                                                                            
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
 Second Brain Integration Plan                                                                                                                                                     
                                                                                                                                                                                   
 Overview                                                                                                                                                                          
                                                                                                                                                                                   
 Integrate the Second Brain implementation from /src/roscoe/second_brain_implementation/ into the main Roscoe paralegal agent. This adds persistent memory, attorney context       
 (TELOS), topic continuity detection, and proactive morning digests.                                                                                                               
                                                                                                                                                                                   
 Components to Integrate                                                                                                                                                           
 ┌──────────────────────────────┬──────────────────────────────────────────────────────────────────────┐                                                                           
 │          Component           │                               Purpose                                │                                                                           
 ├──────────────────────────────┼──────────────────────────────────────────────────────────────────────┤                                                                           
 │ TELOSMiddleware              │ Load attorney context (mission, goals, preferences) at session start │                                                                           
 ├──────────────────────────────┼──────────────────────────────────────────────────────────────────────┤                                                                           
 │ ContinuityMiddleware         │ Detect topic continuity, create MemoryBox segments                   │                                                                           
 ├──────────────────────────────┼──────────────────────────────────────────────────────────────────────┤                                                                           
 │ ProactiveSurfacingMiddleware │ Generate morning digests at 7 AM, deliver via Slack                  │                                                                           
 ├──────────────────────────────┼──────────────────────────────────────────────────────────────────────┤                                                                           
 │ CompositeBackend             │ Route /memories/ to persistent storage                               │                                                                           
 ├──────────────────────────────┼──────────────────────────────────────────────────────────────────────┤                                                                           
 │ MorningBrief skill           │ User-invocable skill for daily briefings                             │                                                                           
 └──────────────────────────────┴──────────────────────────────────────────────────────────────────────┘                                                                           
 Note: fix_capture tool deferred - requires CaptureMiddleware (Phase 1) which was never implemented.                                                                               
                                                                                                                                                                                   
 Implementation Tasks                                                                                                                                                              
                                                                                                                                                                                   
 Phase 1: Pre-Integration Setup                                                                                                                                                    
                                                                                                                                                                                   
 Task 1.1: Create Graph Client Adapter                                                                                                                                             
                                                                                                                                                                                   
 Create /src/roscoe/core/graph_adapter.py:                                                                                                                                         
 """Graph client adapter for Second Brain middleware compatibility."""                                                                                                             
 from roscoe.core.graphiti_client import run_cypher_query                                                                                                                          
                                                                                                                                                                                   
 class GraphClientAdapter:                                                                                                                                                         
     """Adapter to provide graph_client.run() interface."""                                                                                                                        
                                                                                                                                                                                   
     async def run(self, query: str, params: dict = None):                                                                                                                         
         """Execute Cypher query against FalkorDB."""                                                                                                                              
         return await run_cypher_query(query, params or {})                                                                                                                        
                                                                                                                                                                                   
 graph_client = GraphClientAdapter()                                                                                                                                               
                                                                                                                                                                                   
 Task 1.2: Create Slack Client Adapter                                                                                                                                             
                                                                                                                                                                                   
 Create /src/roscoe/core/slack_adapter.py:                                                                                                                                         
 """Slack client adapter for ProactiveSurfacingMiddleware."""                                                                                                                      
 import os                                                                                                                                                                         
 import logging                                                                                                                                                                    
                                                                                                                                                                                   
 logger = logging.getLogger(__name__)                                                                                                                                              
                                                                                                                                                                                   
 class SlackClientAdapter:                                                                                                                                                         
     """Adapter to provide slack_client.send_message() interface."""                                                                                                               
                                                                                                                                                                                   
     def __init__(self):                                                                                                                                                           
         self._client = None                                                                                                                                                       
                                                                                                                                                                                   
     def _get_client(self):                                                                                                                                                        
         """Lazy init Slack WebClient."""                                                                                                                                          
         if self._client is None:                                                                                                                                                  
             try:                                                                                                                                                                  
                 from slack_sdk import WebClient                                                                                                                                   
                 token = os.environ.get("SLACK_BOT_TOKEN")                                                                                                                         
                 if token:                                                                                                                                                         
                     self._client = WebClient(token=token)                                                                                                                         
             except Exception as e:                                                                                                                                                
                 logger.warning(f"Slack client init failed: {e}")                                                                                                                  
         return self._client                                                                                                                                                       
                                                                                                                                                                                   
     def send_message(self, message: str, channel: str = None):                                                                                                                    
         """Send message to Slack channel."""                                                                                                                                      
         client = self._get_client()                                                                                                                                               
         if not client:                                                                                                                                                            
             logger.warning("Slack not configured, skipping message")                                                                                                              
             return False                                                                                                                                                          
                                                                                                                                                                                   
         # Default to ROSCOE_SLACK_CHANNEL or first available channel                                                                                                              
         target_channel = channel or os.environ.get("ROSCOE_SLACK_CHANNEL", "#roscoe")                                                                                             
         try:                                                                                                                                                                      
             client.chat_postMessage(channel=target_channel, text=message)                                                                                                         
             return True                                                                                                                                                           
         except Exception as e:                                                                                                                                                    
             logger.error(f"Failed to send Slack message: {e}")                                                                                                                    
             return False                                                                                                                                                          
                                                                                                                                                                                   
 _slack_client = None                                                                                                                                                              
                                                                                                                                                                                   
 def get_slack_client():                                                                                                                                                           
     """Get or create Slack client singleton."""                                                                                                                                   
     global _slack_client                                                                                                                                                          
     if _slack_client is None:                                                                                                                                                     
         _slack_client = SlackClientAdapter()                                                                                                                                      
     return _slack_client                                                                                                                                                          
                                                                                                                                                                                   
 Task 1.3: Add Package Init Files                                                                                                                                                  
                                                                                                                                                                                   
 Create __init__.py files:                                                                                                                                                         
 - src/roscoe/second_brain_implementation/__init__.py                                                                                                                              
 - src/roscoe/second_brain_implementation/core/__init__.py                                                                                                                         
                                                                                                                                                                                   
 Task 1.4: Fix Import Paths                                                                                                                                                        
                                                                                                                                                                                   
 Update src/roscoe/second_brain_implementation/core/proactive_surfacing_middleware.py line 238-241:                                                                                
 # Change from:                                                                                                                                                                    
 from paralegal.digest_generator.agent import generate_morning_digest, format_digest_markdown                                                                                      
 # To:                                                                                                                                                                             
 from roscoe.second_brain_implementation.paralegal.digest_generator.agent import generate_morning_digest, format_digest_markdown                                                   
                                                                                                                                                                                   
 Update src/roscoe/second_brain_implementation/paralegal/digest_generator/agent.py:                                                                                                
 # Change from:                                                                                                                                                                    
 from paralegal.models import get_agent_llm                                                                                                                                        
 from paralegal.tools import graph_query                                                                                                                                           
 from paralegal.calendar_tools import list_events                                                                                                                                  
 # To:                                                                                                                                                                             
 from roscoe.agents.paralegal.models import get_agent_llm                                                                                                                          
 from roscoe.agents.paralegal.tools import graph_query                                                                                                                             
 from roscoe.agents.paralegal.calendar_tools import list_events                                                                                                                    
                                                                                                                                                                                   
 Phase 2: Middleware Integration                                                                                                                                                   
                                                                                                                                                                                   
 Task 2.1: Update agent.py Imports                                                                                                                                                 
                                                                                                                                                                                   
 Add to /src/roscoe/agents/paralegal/agent.py:                                                                                                                                     
 # Second Brain middleware imports                                                                                                                                                 
 from roscoe.second_brain_implementation.core.telos_middleware import TELOSMiddleware                                                                                              
 from roscoe.second_brain_implementation.core.continuity_middleware import ContinuityMiddleware                                                                                    
 from roscoe.second_brain_implementation.core.proactive_surfacing_middleware import ProactiveSurfacingMiddleware                                                                   
 from roscoe.second_brain_implementation.core.memory_backend import create_memory_backend                                                                                          
 from roscoe.core.graph_adapter import graph_client                                                                                                                                
 from roscoe.core.slack_adapter import get_slack_client                                                                                                                            
                                                                                                                                                                                   
 Task 2.2: Create Middleware Instances                                                                                                                                             
                                                                                                                                                                                   
 Add after existing middleware instances:                                                                                                                                          
 # Second Brain middleware                                                                                                                                                         
 telos_middleware = TELOSMiddleware(workspace_dir=workspace_dir)                                                                                                                   
 continuity_middleware = ContinuityMiddleware(graph_client=graph_client)                                                                                                           
 proactive_surfacing_middleware = ProactiveSurfacingMiddleware(                                                                                                                    
     graph_client=graph_client,                                                                                                                                                    
     slack_client=get_slack_client()  # Slack delivery enabled                                                                                                                     
 )                                                                                                                                                                                 
                                                                                                                                                                                   
 Task 2.3: Switch to CompositeBackend                                                                                                                                              
                                                                                                                                                                                   
 Change the backend from FilesystemBackend to create_memory_backend:                                                                                                               
 # Change from:                                                                                                                                                                    
 backend=FilesystemBackend(root_dir=workspace_dir, virtual_mode=True),                                                                                                             
                                                                                                                                                                                   
 # To:                                                                                                                                                                             
 backend=create_memory_backend,  # Factory function - routes /memories/ to persistent storage                                                                                      
                                                                                                                                                                                   
 Task 2.4: Update Middleware Stack                                                                                                                                                 
                                                                                                                                                                                   
 New middleware order:                                                                                                                                                             
 middleware=[                                                                                                                                                                      
     telos_middleware,                # 1. Load attorney context (TELOS)                                                                                                           
     case_context_middleware,         # 2. Detect client/case mentions                                                                                                             
     workflow_middleware,             # 3. Inject workflow guidance                                                                                                                
     continuity_middleware,           # 4. Topic continuity detection                                                                                                              
     skill_selector_middleware,       # 5. Semantic skill matching                                                                                                                 
     UIContextMiddleware(),           # 6. UI state bridging                                                                                                                       
     proactive_surfacing_middleware,  # 7. Morning digests (7 AM)                                                                                                                  
     get_patched_shell_middleware(                                                                                                                                                 
         workspace_root=local_workspace_dir,                                                                                                                                       
         execution_policy=HostExecutionPolicy(),                                                                                                                                   
     ),                                                                                                                                                                            
 ]                                                                                                                                                                                 
                                                                                                                                                                                   
 Phase 3: Workspace Files                                                                                                                                                          
                                                                                                                                                                                   
 Task 3.1: Create TELOS Directory Structure                                                                                                                                        
                                                                                                                                                                                   
 On VM:                                                                                                                                                                            
 mkdir -p /mnt/workspace/memories/TELOS                                                                                                                                            
 mkdir -p /mnt/workspace/memories/digests                                                                                                                                          
                                                                                                                                                                                   
 Task 3.2: Copy TELOS Templates                                                                                                                                                    
                                                                                                                                                                                   
 cp /home/aaronwhaley/roscoe/src/roscoe/second_brain_implementation/workspace/memories/TELOS/*.md /mnt/workspace/memories/TELOS/                                                   
                                                                                                                                                                                   
 Task 3.3: Copy MorningBrief Skill                                                                                                                                                 
                                                                                                                                                                                   
 mkdir -p /mnt/workspace/Skills/MorningBrief                                                                                                                                       
 cp /home/aaronwhaley/roscoe/src/roscoe/second_brain_implementation/workspace/Skills/MorningBrief/SKILL.md /mnt/workspace/Skills/MorningBrief/                                     
                                                                                                                                                                                   
 Phase 4: Database Migrations                                                                                                                                                      
                                                                                                                                                                                   
 Task 4.1: Run Migrations on VM                                                                                                                                                    
                                                                                                                                                                                   
 docker exec -it roscoe-agents bash -c "                                                                                                                                           
   cd /app/src/roscoe/second_brain_implementation/migrations &&                                                                                                                    
   python add_inbox_log_indexes.py &&                                                                                                                                              
   python add_memorybox_schema.py                                                                                                                                                  
 "                                                                                                                                                                                 
                                                                                                                                                                                   
 Phase 5: Deployment                                                                                                                                                               
                                                                                                                                                                                   
 Task 5.1: Commit and Push                                                                                                                                                         
                                                                                                                                                                                   
 git add -A                                                                                                                                                                        
 git commit -m "feat: integrate Second Brain (TELOS, Continuity, ProactiveSurfacing middleware)"                                                                                   
 git push                                                                                                                                                                          
                                                                                                                                                                                   
 Task 5.2: Deploy to VM                                                                                                                                                            
                                                                                                                                                                                   
 gcloud compute ssh roscoe-paralegal-vm --zone=us-central1-a                                                                                                                       
 cd /home/aaronwhaley/roscoe && git pull                                                                                                                                           
 docker restart roscoe-agents                                                                                                                                                      
                                                                                                                                                                                   
 Phase 6: Verification                                                                                                                                                             
                                                                                                                                                                                   
 Task 6.1: Check Middleware Initialization                                                                                                                                         
                                                                                                                                                                                   
 docker logs roscoe-agents 2>&1 | grep -E "(TELOS|CONTINUITY|PROACTIVE)"                                                                                                           
                                                                                                                                                                                   
 Expected:                                                                                                                                                                         
 🎯 TELOS MIDDLEWARE INITIALIZED                                                                                                                                                   
 🔗 CONTINUITY MIDDLEWARE INITIALIZED                                                                                                                                              
 📬 PROACTIVE SURFACING MIDDLEWARE INITIALIZED                                                                                                                                     
                                                                                                                                                                                   
 Task 6.2: Test TELOS Loading                                                                                                                                                      
                                                                                                                                                                                   
 1. Edit /mnt/workspace/memories/TELOS/goals.md with actual content                                                                                                                
 2. Start new chat session                                                                                                                                                         
 3. Verify agent has attorney context                                                                                                                                              
                                                                                                                                                                                   
 Task 6.3: Test Morning Digest (after 7 AM)                                                                                                                                        
                                                                                                                                                                                   
 1. Start session after 7 AM                                                                                                                                                       
 2. Check /mnt/workspace/memories/digests/ for generated file                                                                                                                      
                                                                                                                                                                                   
 Files to Modify                                                                                                                                                                   
 ┌───────────────────────────────────────────────────────────────────────────────┬─────────────────────────────────────────────────────────────────┐                               
 │                                     File                                      │                             Changes                             │                               
 ├───────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤                               
 │ src/roscoe/agents/paralegal/agent.py                                          │ Add imports, middleware instances, switch backend, update stack │                               
 ├───────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤                               
 │ src/roscoe/second_brain_implementation/core/proactive_surfacing_middleware.py │ Fix import path (line 238-241)                                  │                               
 ├───────────────────────────────────────────────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤                               
 │ src/roscoe/second_brain_implementation/paralegal/digest_generator/agent.py    │ Fix import paths                                                │                               
 └───────────────────────────────────────────────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘                               
 Files to Create                                                                                                                                                                   
 ┌─────────────────────────────────────────────────────────┬───────────────────────────────────────────────────┐                                                                   
 │                          File                           │                      Purpose                      │                                                                   
 ├─────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┤                                                                   
 │ src/roscoe/core/graph_adapter.py                        │ Adapter for graph_client.run() interface          │                                                                   
 ├─────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┤                                                                   
 │ src/roscoe/core/slack_adapter.py                        │ Adapter for slack_client.send_message() interface │                                                                   
 ├─────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┤                                                                   
 │ src/roscoe/second_brain_implementation/__init__.py      │ Package init                                      │                                                                   
 ├─────────────────────────────────────────────────────────┼───────────────────────────────────────────────────┤                                                                   
 │ src/roscoe/second_brain_implementation/core/__init__.py │ Package init                                      │                                                                   
 └─────────────────────────────────────────────────────────┴───────────────────────────────────────────────────┘                                                                   
 Deferred Items                                                                                                                                                                    
                                                                                                                                                                                   
 - fix_capture tool: Requires CaptureMiddleware (Phase 1) which was never implemented. This is needed to correct misclassified captures.                                           
 - CaptureMiddleware: Not part of this integration - should be implemented separately as Phase 1 of Second Brain.                                                                  
                                                                                                                                                                                   
 Environment Variables Required                                                                                                                                                    
                                                                                                                                                                                   
 # Slack (for digest delivery)                                                                                                                                                     
 SLACK_BOT_TOKEN=xoxb-...   # Bot User OAuth Token                                                                                                                                 
 ROSCOE_SLACK_CHANNEL=#roscoe  # Channel for digests (default: #roscoe)                                                                                                            
                                                                                                                                                                                   
 Risk Mitigation                                                                                                                                                                   
                                                                                                                                                                                   
 - TELOS middleware gracefully handles missing files (no crash)                                                                                                                    
 - Morning digest falls back to file delivery if Slack not configured                                                                                                              
 - Migrations support --dry-run and --rollback flags                                                                                                                               
 - CompositeBackend falls back gracefully if StoreBackend unavailable                                                                                                              
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌
                                                                                                                                                                                   
 Requested permissions:                                                                                                                                                            
   · Bash(prompt: run database migrations)                                                                                                                                         
   · Bash(prompt: run pytest tests)                                                                                                                                                
   · Bash(prompt: check git status)                                                                