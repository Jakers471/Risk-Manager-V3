# AI Collaboration Rules (A/B/C)

Agents:
- A = Engine & Enforcer (monitor loop, enforcement, logging)
- B = Policy Brain (tiers, rule precedence, ActionPlan)
- C = ProjectX Client (SDK wrapper, REST/WS adapters, simulators)

Protocol:
1) Work ONLY on your feature branch:
   - A: feat/agents-bootstrap (or feat/agent-a-engine going forward)
   - B: feat/agent-b-policy
   - C: feat/projectx-client
2) Every change:
   - Run the two smoke tests.
   - Commit with Conventional Commits style and your tag: 
     - A: feat(engine): ...
     - B: feat(policy): ...
     - C: feat(client): ...
   - Push immediately.
3) Open/Update your PR. In the PR body, fill the template and paste test output.
4) Handoff: At the bottom of the PR, write a 'next_ai' and bullet list of exact tasks for the next agent.
5) No force-push to main. Squash-merge only via PRs.
