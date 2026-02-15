Summary of Changes                                                                                          
                                         
  Files Created/Modified:                                                                                     
                                                                                                              
  1. install-dmr.md (created)
    - Comprehensive DMR installation guide
    - Added critical hardware requirement: 16GB RAM minimum for CPU-only inference
    - Ready to integrate into main documentation
  2. docker-compose.yml (modified)
    - Added extra_hosts mapping for model-runner.docker.internal:host-gateway
    - Required for containers to reach DMR on the host machine
  3. universes/MINE/domains/peter/domain.json (modified)
    - Removed llm_config section that pointed to local DMR
    - Now uses remote model from .env (works on 8GB machines)

  Key Learnings:

  - DMR local models require 16GB+ RAM - not suitable for 8GB machines
  - z.ai API is currently overloaded - 19-38 second response times
  - The system works correctly - just need appropriate hardware or faster API

  When you merge to the main machine, you'll want to:
  1. Keep the extra_hosts in docker-compose.yml
  2. Use the full install-dmr.md documentation
  3. Restore llm_config in peter domain.json for that machine (since it likely has more RAM)

  Good luck with the merge!
