

# MCP Architecture for the Enterprise: Series Content Plan

 · 

## Audience and series shape

The series is for people who build or approve MCP in a large company: platform and integration architects, security architects, SREs and the engineering leads who sign off on agent access to production systems. They already know what MCP is. They want to know how to run it safely at scale, and which parts of the spec changed under them.

Promise. After the series, a viewer can draw their own MCP estate on a whiteboard: where the servers run, how identity flows from a person through an agent to a backend, where policy is enforced, what gets logged, and what breaks when the spec revs.

Shape. A numbered series in the Working Paper design system, one figure per page, played in order and joined into one video. Length is not a constraint, so the plan is organised into acts that can also ship as separate videos:
- Act I, Foundations. The protocol as it stands today: roles, lifecycle, primitives, transports.
- Act II, Identity and access. Authorization, enterprise identity, delegation and consent. This is the core of the series.
- Act III, Running it. Gateways, registries, multi-server routing, context economics, scale and state.
- Act IV, Trust and operations. Threats, supply chain, observability, governance and versioning.
- Act V, Reference architecture. Everything on one page, then the adoption path.

Tone. A working note for experts: exact spec terms, RFC numbers, and version dates. Everything is sourced, and every page cites the spec revision it describes.

## Freshness baseline

Every page describes MCP 2026-07-28, the current revision ([versioning](https://modelcontextprotocol.io/specification/versioning)). Anything older is taught only as "what changed". The draft changelog is empty, and no next revision has been announced ([draft changelog](https://modelcontextprotocol.io/specification/draft/changelog)).
| Date | Revision or event | What it changed for enterprise architects | 
| 2026-08-22 | [Roadmap update](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) | Next priorities: agentic events, maturing Tasks, one HTTP-native transport, agent identity (DPoP, workload identity federation), progressive tool discovery | 
| 2026-07-28 | [Spec 2026-07-28](https://modelcontextprotocol.io/specification/2026-07-28/changelog) | Stateless core: initialize and Mcp-Session-Id removed, server/discover added, per-request _meta capabilities. Multi Round-Trip Requests replace server-initiated requests. Tasks becomes an extension. Mcp-Method / Mcp-Name routing headers. ttlMs / cacheScope on lists. RFC 9207 iss check. Dynamic Client Registration deprecated for CIMD. Roots, Sampling, Logging and HTTP+SSE deprecated. 12-month deprecation policy | 
| 2026-06-18 | [Enterprise-Managed Authorization stable](https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/) | SEP-990 extension: IdP-issued ID-JAG, RFC 8693 token exchange, Cross App Access. No per-user consent screens | 
| 2026-01 | MCP Apps GA ([extensions post](https://blog.modelcontextprotocol.io/posts/2026-03-11-understanding-mcp-extensions/)) | Interactive UI as an official extension (io.modelcontextprotocol/ui) | 
| 2025-12-09 | [MCP joins the Agentic AI Foundation](https://blog.modelcontextprotocol.io/posts/2025-12-09-mcp-joins-agentic-ai-foundation/) | Neutral Linux Foundation home. MCP keeps its maintainers and SEP process | 
| 2025-11-25 | [Spec 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/changelog) | Experimental tasks, CIMD recommended, URL-mode elicitation, incremental scope consent, OIDC discovery, sampling with tools, extensions framework | 
| 2025-09-08 | [Registry preview](http://blog.modelcontextprotocol.io/posts/2025-09-08-mcp-registry-preview/) | Official metadata registry. Still preview today, with the v0.1 API frozen | 
| 2025-06-18 | [Spec 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/changelog) | Servers are OAuth resource servers (RFC 9728), RFC 8707 required, structured output, elicitation, batching removed | 
| 2025-03-26 | [Spec 2025-03-26](https://modelcontextprotocol.io/specification/2025-03-26/changelog) | OAuth 2.1, Streamable HTTP replaces HTTP+SSE, tool annotations | Stale ideas the series must not repeat. Most MCP content online predates 2026-07-28 and gets these wrong:
- Sticky sessions or a shared session store for scaling remote servers. Any instance can now serve any request.
- The initialize handshake and capability negotiation per connection.
- Servers calling back into the client for sampling, roots or elicitation. That is now input_required results the client answers on retry.
- Dynamic Client Registration as the default for unknown clients. The order is now pre-registration, then CIMD, then DCR as a deprecated fallback.
- Session hijacking as the headline threat. The spec now warns about state handle hijacking instead.
- SSE resumability with Last-Event-ID. Interrupted requests are re-issued.

Freshness rule for the verifier. A claim about the protocol must cite a 2026-07-28 page. A claim about a product, draft or incident must cite a page dated within 90 days, or be re-checked on the day of rendering.

## Page-by-page plan

The plan has 35 pages in five acts, about 8 minutes played end to end, and each act also works as its own video. Every page pairs what the spec says with what industry actually runs, using the sources in the industry references section. Page length follows the design system: 1 s still, then two loops of (S + 1) s, where S is the number of story steps.

Running example. An on-call agent in a large company gets paged, reads metrics from an observability MCP server, opens a ticket through an ITSM MCP server, and asks to restart a pod through a Kubernetes MCP server. Every figure reuses these three servers, so the series reads as one story.

### Act I, Foundations (8 pages, 106 s)
| # | Heading | Figure and story (S) | Industry evidence | Claims to check | 
| 1 | MCP 2026-07-28: an enterprise architecture in 35 pages (title) | The whole estate: person, host, IdP, gateway, registry, three servers, backends. One request traced end to end (6) | SDK downloads ~200M a month each on npm and PyPI | Current revision is 2026-07-28; download figures | 
| 2 | Who runs MCP in production | Five estates side by side, each with its pattern and its number; a counterweight panel for regulated industries (6) | Uber 60,000 runs a week; Block 12,000 employees; LinkedIn 8,000 daily users; Pinterest 66,000 calls a month; Cloudflare 60% of staff; Stacklok: 12% of financial services in broad production | Every figure, date and the Pinterest "January 2025" date typo | 
| 3 | Hosts, clients, servers, and what each owns | Host holds the model and consent; one client per server; tools, resources, prompts. Deprecated client features greyed (5) | OpenAI puts custom servers outside its trust boundary; Salesforce runs every call as the user | Roots and Sampling deprecated | 
| 4 | The handshake is gone | Two requests hit two instances; each carries version and capabilities in _meta; server/discover; resultType everywhere (5) | Google and Cloudflare stateless write-ups (Aug 2026) | SEP-2575; server/discover is MUST | 
| 5 | Two transports, one HTTP shape | stdio for local, Streamable HTTP for remote; Mcp-Method and Mcp-Name headers; subscriptions/listen; HTTP+SSE deprecated (5) | Cloudflare portals bridge both revisions; Gemini Enterprise accepts Streamable HTTP only | SEP-2243; resumability removed | 
| 6 | When the server needs something back | Multi Round-Trip Request: input_required, the client collects an elicitation, retries with inputResponses (5) | Cloudflare: MRTR replaces streaming elicitation; AgentCore uses URL elicitation for third-party OAuth | SEP-2322 | 
| 7 | Long-running work as tasks | Restart-pod call returns a task handle; tasks/get polling; tasks/update; result lands (5) | Spec only; no production write-up found yet | SEP-2663 extension status | 
| 8 | Extensions: how MCP grows without forking | Core plus opt-in extensions negotiated via capabilities.extensions (4) | Anthropic and Okta ship Enterprise-Managed Authorization; MCP Apps GA | Apps GA, EMA stable, Client Credentials draft | ### Act II, Identity and access (9 pages, 131 s)
| # | Heading | Figure and story (S) | Industry evidence | Claims to check | 
| 9 | Who is who in MCP authorization | Server as resource server, authorization server, IdP, client; stdio takes credentials from the environment (5) | Kong and agentgateway make the gateway the resource server | Authorization optional, HTTP only | 
| 10 | Discovery starts with a 401 | 401 with resource_metadata → RFC 9728 → RFC 8414 or OIDC metadata; exact issuer match (6) | Kong and Red Hat serve protected-resource metadata at the gateway | Probe order; issuer match new in 2026-07-28 | 
| 11 | Registering a client you have never met | Pre-registration, then CIMD, then DCR as a deprecated fallback; SSRF guard (5) | AWS and agentgateway still depend on DCR shims | DCR deprecated (PR #2858); CIMD draft | 
| 12 | The authorization code flow, hardened | PKCE S256, resource on both requests, iss checked before redemption (7) | Salesforce hosted servers and OpenAI apps use OAuth 2.1 with PKCE per user | RFC 8707 MUST; RFC 9207 | 
| 13 | One audience per token | Server validates audience; four ways to reach the backend: token exchange, OBO, vault credential, header forwarding (crossed out outside the perimeter) (6) | Uber single-hop JWTs at P99 under 40 ms; SAP "never proxy"; AgentCore OBO; Vault dynamic secrets; APIM forwards by default | Passthrough MUST NOT; vendor behaviours | 
| 14 | Scopes and step-up | Read-only token lists pods; restart returns 403 insufficient_scope; union of scopes (5) | AWS interceptors filter tools/list per user; Cedar policy; OpenAI checks scopes on every call | Step-up behaviour | 
| 15 | Enterprise-managed authorization | IdP sign-in; token exchange for an ID-JAG; JWT bearer grant; admin policy replaces consent (7) | Okta Agent SSO GA; 25+ Cross App Access partners; Anthropic central connector auth; Auth0 early access | SEP-990 stable; ID-JAG draft number | 
| 16 | Machines and agents as principals | Client credentials, workload identity, agent identity (5) | Google SPIFFE agent identity; Entra agent identity; Red Hat SPIFFE to Keycloak; Pinterest SPIFFE mesh; CoSAI and NIST papers | SEP-1933 draft only; product statuses | 
| 17 | The confused deputy | Proxy with a static client ID; per-client consent; exact redirect_uri; state after consent (6) | AWS per-hop tokens; ContextForge anti-patterns; CoSAI: "never raw upstream tokens" | Best-practices wording | ### Act III, Running it (8 pages, 112 s)
| # | Heading | Figure and story (S) | Industry evidence | Claims to check | 
| 18 | The gateway is where policy lives | Gateway terminates auth, filters tools per caller, routes on headers, redacts, rate-limits, audits (7) | Uber central gateway; APIM, AgentCore, Apigee, Kong, Cloudflare, ServiceNow, Google Agent Gateway; Gartner recommends gateways | Product capability claims | 
| 19 | Registries decide what can run | Public registry → private registry with approval → client allowlist (6) | Expedia: hundreds of servers in one catalog; Pinterest registry; Azure API Center; AWS Agent Registry GA; GitHub allowlists | Registry preview; AWS GA date | 
| 20 | Many servers, one model | Three servers, prefixed tool names, a shadowing tool blocked (5) | Red Hat gateway prefixes tools; LinkedIn quality fell past 30 tools | SEP-986 | 
| 21 | Tool definitions cost tokens | 50+ tools in context vs tool search vs code execution; deterministic ordering (5) | LinkedIn tool search; Cloudflare Code Mode 94% cut; Anthropic figures; Twilio cost up 27.5% as counterweight | All token figures | 
| 22 | Scaling remote servers | Round-robin, any pod serves any request, state handles, cacheScope (6) | Google and SAP stateless; Red Hat and ContextForge still use sessions (older spec) | SEP-2567 | 
| 23 | Local servers need a sandbox | One-click install, full command shown, container, signed bundle, allowlist (5) | Docker gateway containers and signature checks; Block in-house allowlist; Red Hat three rings; Windows preview | MCPB signing; Windows status | 
| 24 | Wrap an API or design a server | REST-to-MCP generator vs task-shaped tools (5) | Block cut a 30+ tool server to GraphQL executors; Uber generates tools from 10,000 services; AWS: workflow tools ~3x more accurate; Thoughtworks "Caution" | Each figure | 
| 25 | Where vendors and the spec disagree | Four contested choices, spec on one side, vendors on the other (5) | Passthrough, DCR, sessions, generated tools (see the departures table) | Each vendor behaviour, current docs | ### Act IV, Trust and operations (8 pages, 112 s)
| # | Heading | Figure and story (S) | Industry evidence | Claims to check | 
| 26 | The threat model | Lethal trifecta; poisoning, rug pull, injection, shadowing (6) | CoSAI 12 threat categories; OWASP MCP Top 10; CSA: 1,862 servers exposed without auth | Framework names and counts | 
| 27 | Defence in depth | Pinned definitions, approvals, egress control, least privilege, output handling (6) | Bloomberg interceptors; Uber PII redaction and write blocks; Pinterest human approval; Google Model Armor | Each control maps to a threat | 
| 28 | Stopping an agent fast | IdP revokes, short token expires, gateway pauses a tool, registry delists a server (5) | ServiceNow Pause; Anthropic and Okta short-lived tokens; Auth0 immediate revocation; Vault TTLs | Product behaviours | 
| 29 | What actually went wrong | Incident timeline, each lit with the control that would have stopped it (6) | CVEs, Asana, postmark-mcp, CSA May 2026 note | CVE numbers, dates, scores | 
| 30 | Seeing every call | Trace context in _meta, spans per call, audit record (6) | SAP TraceContext end to end; Google Agent Observability; OpenAI Compliance Logs; Five Eyes: log full action chains | SEP-414; OTel status | 
| 31 | Versions and deprecations | Version per request; 12-month window; gateway bridging revisions (5) | Cloudflare bridges revisions; AAIF migration guide | SEP-2596 | 
| 32 | Who decides the protocol | AAIF, maintainers, working groups, SEPs (5) | 170 AAIF members; Bloomberg contributions; security teams own MCP in 43% of financial firms | Member counts | 
| 33 | MCP beside A2A and Skills | Agent to tool, agent to agent, procedural knowledge (5) | A2A in AAIF; LinkedIn playbooks; Thoughtworks on when not to use MCP | A2A date; analysis labelled | ### Act V, Reference architecture (2 pages, 32 s)
| # | Heading | Figure and story (S) | Industry evidence | Claims to check | 
| 34 | The reference architecture | Everything on one page (7) | The eight-point consensus pattern; Google, SAP, Red Hat, Cloudflare, IBM architectures | Consistency with pages 1 to 33 | 
| 35 | An adoption path | Five phases from pilot to org-wide governance (6) | AWS four-scope maturity model; CoSAI three phases; Block's two-month rollout; Five Eyes staged rollout | Each phase maps to earlier pages | ## Coverage map

Eighteen of the twenty-one concerns an enterprise review board raises are covered, each with both a spec source and an industry source. Three are still thin and are listed first. Conformance testing has no industry source at all yet.
| Enterprise concern | Pages | Coverage | 
| Conformance and testing before rollout | 31 | Thin: no industry source found | 
| Multi-tenancy and isolation between business units | 18, 22 | Thin: Google tenant memory isolation, ContextForge team RBAC | 
| Compliance mapping (SOC 2, ISO 42001, EU AI Act logging) | 30, 32 | Thin: CSA AIUC-1 controls, OpenAI compliance logs | 
| Revocation and kill switch | 28 | Covered (new page) | 
| Industry adoption evidence | 2, 25, 34, 35 | Covered (new) | 
| Secrets for downstream systems | 13, 23 | Covered: Vault, AgentCore Identity, Docker | 
| User authentication and consent | 9 to 12, 14 | Covered | 
| Admin-controlled access without consent screens | 15 | Covered | 
| Agent and workload identity | 16 | Covered (spec side mostly drafts) | 
| Least privilege | 14, 18, 27 | Covered | 
| Downstream access without token passthrough | 13, 17, 25 | Covered | 
| Central policy enforcement | 18 | Covered | 
| Approved-server catalog and shadow MCP | 19, 23 | Covered | 
| Supply chain integrity | 23, 29 | Covered | 
| Prompt injection and tool poisoning | 20, 26, 27 | Covered | 
| Human approval for destructive actions | 6, 27 | Covered | 
| Audit and observability | 30 | Covered | 
| Scale and high availability | 22 | Covered | 
| Context and token cost | 21 | Covered | 
| Version upgrades and deprecation | 4, 31 | Covered | 
| Standards governance and ecosystem fit | 32, 33 | Covered | ## Verifier subagent

The verifier is a separate agent that checks a content plan before any video is built. It never sees the drafting conversation, so the plan does not grade itself. It returns one of three verdicts: PASS, FIX, or FAIL. The same agent works for any explainer topic (MCP, RAG, agents), because it builds its own checklist from the topic's canonical sources.

Inputs. The plan (this doc, or the storyboard table the video skill produces), the audience line, the as-of date, and optionally a list of canonical sources the author suggests. The verifier must find its own canonical sources too.

Check 1: Freshness.
- Find the current state of the topic from its authority. For MCP, that is the [versioning page](https://modelcontextprotocol.io/specification/versioning), the draft changelog and the official blog since the as-of date.
- Re-verify every protocol claim against the current revision's pages, not a secondary summary.
- Re-fetch every product, draft or incident claim. A source older than 90 days must be re-confirmed, or the claim is softened or dropped.
- Scan the whole plan for stale ideas (for MCP, the list in the freshness baseline) and flag any page that teaches them.

Check 2: Comprehensiveness.
- Before reading the plan's own coverage map, build an independent checklist from primary sources. For MCP: the spec table of contents, the security best-practices page, the extensions list, the roadmap, and the OWASP MCP Top 10.
- Map each checklist item to pages, and rank the gaps by what the stated audience would miss most.
- Check depth: every page has one figure and 4 to 7 story steps, and every claim has a source.

Check 3: Accuracy. Each claim marked for checking is confirmed from a primary source: the spec for protocol facts, vendor docs for product facts, NVD or the vendor advisory for incidents. A secondary source can only back a claim labelled as such.

Check 4: Series design. One idea per page. S between 4 and 7. The running example stays consistent. No page depends on a later one. The total stays within the design system's budget, or the plan explains why not.

Check 5: Industry evidence. The series says what industry runs, not only what the spec allows. So every page needs at least one named enterprise source (a production write-up, vendor reference architecture, or recognised framework), or it must say plainly that none exists yet. A vendor practice is checked against the vendor's current docs. Guidance written before the current spec revision is flagged wherever it assumes older behaviour. Adoption numbers need the publisher's own page. Where industry departs from the spec, both sides are cited, and the page says which one it recommends.

Output. A verdict, a freshness stamp (current revision and the date it was checked), and one findings table: severity (blocker, major, minor), page, claim, finding, evidence URL opened with the date shown on that page, and the proposed fix. A FAIL needs at least one blocker. A FIX needs majors that the author can apply without a re-plan.

Where it sits. In the explainer video workflow, it runs after the plan and before the user's go. It runs again, freshness only, on the day of rendering if more than 7 days have passed.

How it ships. As an agent in the Content Studio plugin (agents/content-plan-verifier.md), with web search, web fetch and read-only file tools. The video skill's step 2 calls it and will not start rendering on a FAIL.

## Industry adoption and enterprise references

Industry has settled on one enterprise shape for MCP. Remote servers sit behind a gateway, a private registry doubles as the allowlist, each hop gets its own downstream credential, and every call is traced. The series teaches that pattern beside the spec, and it names where vendors still depart from the spec. All sources below were opened on 2026-09-28. ⚠ marks guidance written before the stateless 2026-07-28 revision.

### Production deployments with published numbers
| Company | What they run | Scale | Date | Backs pages | 
| [LinkedIn](https://www.infoq.com/presentations/linkedin-context-engineering/) | Local MCP server serving playbooks; moved to tool search after quality "degraded beyond 30 tools" | 8,000 daily users, 8,000+ tools and playbooks, 1,000+ repos | 2026-09-19 | 2, 21 | 
| [Expedia Group (via AWS)](https://aws.amazon.com/blogs/opensource/governing-ai-assets-at-scale-with-mcp-gateway-and-registry/) | Open-source gateway and registry with IdP scopes, scanning and OpenTelemetry | "Hundreds of MCP servers, tools, and skills alongside tens of agents" | 2026-06-17 | 18, 19 | 
| [Uber, identity](https://www.uber.com/us/en/blog/solving-the-agent-identity-crisis/) | Single-hop, single-audience JWTs with an actor-chain claim, checked against an agent registry; gateway authorizes every tool call | Token exchange P99 under 40 ms | 2026-05-21 | 13, 17, 18 | 
| [Uber, platform](https://aaif.io/blog/how-uber-runs-60000-ai-agent-tasks-per-week-with-mcp) | Central gateway and registry; tools generated from service definitions; PII redaction and write blocks | 60,000 agent runs a week, 1,500+ monthly active agents, 10,000+ services | 2026-05-14 | 2, 18, 24, 27 | 
| [Bloomberg](https://aaif.io/blog/building-trust-into-the-protocol-bloombergs-mcp-contributions) | Agentic app on the Terminal; contributed Interceptors and tool Variants to MCP | No figures published | 2026-05-21 | 27, 32 | 
| [Cloudflare, internal](https://blog.cloudflare.com/enterprise-mcp/) | 13 internal servers behind Access and MCP server portals; Code Mode | 3,683 internal users (60% of staff); 52 tools cut from ~9,400 to ~600 tokens | 2026-04-14, 2026-04-20 | 2, 21, 34 | 
| [Pinterest](https://medium.com/pinterest-engineering/building-an-mcp-ecosystem-at-pinterest-d881eb4c16f1) | Domain servers, central registry as source of truth, user JWT plus SPIFFE mesh identity, human approval for sensitive actions | 66,000 invocations a month, ~7,000 hours saved a month | 2026-03-19 | 2, 16, 19, 27 | 
| [Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents) | Internal "Toolshed" MCP server behind its coding agents | 400+ tools, 1,000+ PRs merged a week | 2026-02-09 | 2, 24 | 
| [Block](https://block.github.io/goose/blog/2025/04/21/mcp-in-enterprise/) | goose client with 100+ internal servers, SSO-based OAuth, allowlist of in-house servers | 12,000 employees in two months; 75% of engineers in the first month | 2025-04 to 2025-12 | 2, 23, 24, 35 | 
| [Stacklok survey](https://stacklok.com/wp-content/uploads/2026/01/State-of-MCP-in-Financial-Services-2026_FINAL.pdf) (counterweight) | 300 financial-services leaders | Only 12% in broad production; security is the top blocker (58%) | 2026-01 | 2, 35 | Platform scale: @modelcontextprotocol/sdk had 202.7M npm downloads and mcp had 219.0M PyPI downloads in the 30 days to 2026-09-27 (registry APIs; raw counts include CI traffic).

### The consensus pattern
- Remote servers behind a gateway that is the OAuth resource server. Azure API Management, Apigee, Kong, agentgateway, AgentCore Gateway, ServiceNow AI Gateway, Google Agent Gateway, Cloudflare portals. Pages 18, 34.
- Per-tool policy at the gateway. Cedar in AgentCore, IAM in Google, Authorino in Red Hat, APIM policies, AWS interceptors. Pages 14, 18.
- A private registry as the allowlist, with approval workflow. Azure API Center, AWS Agent Registry, Google Agent Registry, Kong, ServiceNow AI Control Tower. Page 19.
- A separate credential per hop. Token exchange or OBO, or a vault. AgentCore Identity, Google Auth Manager, HashiCorp Vault, SAP. Page 13.
- First-class agent or workload identity. SPIFFE at Google, Red Hat and Pinterest; Entra agent identity. Page 16.
- Trace context and audit with the caller's identity. Page 30.
- Fewer tool definitions reach the model. Code Mode, tool search, Toolsets, tool filtering. Page 21.
- A kill switch through the IdP or the gateway. ServiceNow Pause; short-lived tokens with Enterprise-Managed Authorization. Page 28.

### Where industry departs from the spec
| Issue | Spec 2026-07-28 | Industry practice | Page | 
| Token passthrough | MUST NOT pass the received token on | [SAP](https://architecture.learning.sap.com/docs/ref-arch/137800) and AWS forbid it; [Azure APIM](https://learn.microsoft.com/en-us/azure/api-management/secure-mcp-servers) forwards Authorization by default; [Agent Router](https://theagentrouter.ai/blog/multi-user-mcp-header-forwarding/) recommends header forwarding inside the trust perimeter | 13, 25 | 
| Client registration | Pre-registration, then CIMD; DCR deprecated | [AgentCore](https://aws.amazon.com/blogs/machine-learning/govern-ai-agent-tool-access-with-amazon-bedrock-agentcore-gateway/) uses a DCR shim; [agentgateway](https://docs.solo.io/agentgateway/latest/mcp/auth/about/) proxies DCR | 11, 25 | 
| State | No sessions; any instance serves any request | [Red Hat](https://www.redhat.com/en/blog/control-your-ai-agent-traffic-scale-model-context-protocol-gateway-red-hat-openshift-now-technology-preview) keeps a Redis session store; [ContextForge](https://ibm.github.io/mcp-context-forge/architecture/) uses session affinity (both written for the older spec) | 22, 25 | 
| Tool design | No rule | APIM, Kong and Apigee generate tools from REST; [AWS guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/mcp-strategies/introduction.html) and ContextForge call API mirroring an anti-pattern | 24, 25 | ### White papers and frameworks
| Title | Publisher | Date | Backs pages | 
| [AI security and safety for Google Cloud MCP servers](https://docs.cloud.google.com/mcp/ai-security-safety) | Google Cloud | Updated 2026-09-24 | 16, 19, 27, 30 | 
| [MCP 2026-07-28: from local tool to distributed protocol](https://aaif.io/blog/mcp-2026-07-28-whats-changing-and-how-to-migrate) | Agentic AI Foundation | 2026-07-21 | 4, 15, 31 | 
| [App Security Whitepaper](https://cdn.openai.com/business-guides-and-resources/app-security-whitepaper.pdf) | OpenAI | 2026-06 | 3, 14, 30 | 
| [AIUC-1 Q2 refresh: MCP security and agent identity controls](https://labs.cloudsecurityalliance.org/research/csa-research-note-aiuc1-agentic-ai-security-standard-q2-2026/) | Cloud Security Alliance | 2026-06-05 | 16, 30 | 
| [Careful adoption of agentic AI services](https://labs.cloudsecurityalliance.org/research/csa-research-note-cisa-agentic-ai-adoption-guide-20260517-cs/) (via CSA summary; primary PDF blocked) | CISA, NSA and Five Eyes partners | 2026-05-01 | 30, 35 | 
| [Technology Radar: MCP by default](https://www.thoughtworks.com/radar/techniques/mcp-by-default) (Caution) | Thoughtworks | 2026-04 | 24, 33 | 
| [Agentic identity and access management](https://www.coalitionforsecureai.org/wp-content/uploads/2026/04/agentic-identity-and-access-control.pdf) | CoSAI (OASIS) | 2026-03-20 | 13, 16, 17, 28, 35 | 
| [Model Context Protocol strategies on AWS](https://docs.aws.amazon.com/prescriptive-guidance/latest/mcp-strategies/introduction.html) ⚠ | AWS Prescriptive Guidance | 2026-03-16 | 21, 24, 35 | 
| [A practical guide for secure MCP server development](https://genai.owasp.org/resource/a-practical-guide-for-secure-mcp-server-development/) ⚠ | OWASP GenAI Security Project | 2026-02-16 | 26, 27 | 
| [Software and AI agent identity and authorization](https://www.nccoe.nist.gov/sites/default/files/2026-02/accelerating-the-adoption-of-software-and-ai-agent-identity-and-authorization-concept-paper.pdf) (concept paper) | NIST NCCoE | 2026-02 | 15, 16 | 
| [Model Context Protocol security](https://www.coalitionforsecureai.org/wp-content/uploads/2026/03/model-context-protocol-security-1.pdf) ⚠ | CoSAI (OASIS) | 2026-01-08 | 26, 27 | 
| [Innovation insight: SaaS-hosted remote MCP servers](https://www.gartner.com/en/documents/7645729) (paywalled) | Gartner | 2026-04-01 | 18, 35 | 
| [OWASP MCP Top 10](https://owasp.org/projects/mcp-top-10) (beta) | OWASP | Undated | 26 | 
| [Identity management for agentic AI](https://openid.net/wp-content/uploads/2025/10/Identity-Management-for-Agentic-AI.pdf) ⚠ | OpenID Foundation | 2025-10-07 | 15, 16 | ### Vendor reference architectures
| Title | Publisher | Date | Pattern | Backs pages | 
| [Agent Gateway overview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/agent-gateway-overview) | Google Cloud | 2026-09-25 | Egress gateway: SPIFFE agent identity, registry check, Model Armor, per-tool policy | 18, 16, 34 | 
| [AI Gateway FAQ](https://www.servicenow.com/community/ai-control-tower-articles/ai-gateway-faq/ta-p/3587429) | ServiceNow | 2026-09-10 | Inventory with approvals, gateway holds tokens, instant Pause per server or tool | 18, 28 | 
| [Govern agent tool access with AgentCore Gateway](https://aws.amazon.com/blogs/machine-learning/govern-ai-agent-tool-access-with-amazon-bedrock-agentcore-gateway/) | AWS | 2026-08-21 | Four-scope maturity model, Cedar policy, OBO exchange, registry intake by PR | 14, 18, 35 | 
| [The next generation of MCP](https://blog.cloudflare.com/mcp-v2/) | Cloudflare | 2026-08-06 | Stateless spec explained for gateways and WAFs | 4, 6, 11 | 
| [Open blueprint for cloud-native AI agents](https://developers.redhat.com/articles/2026/07/20/architect-open-blueprint-cloud-native-ai-agents) | Red Hat | 2026-07-20 | SPIFFE, Keycloak token exchange, Envoy MCP gateway, three sandbox rings | 16, 23, 34 | 
| [Centrally manage authorization for MCP connectors](https://claude.com/blog/enterprise-managed-auth) | Anthropic | 2026-06-18 | Enterprise-Managed Authorization with Okta; provisioning by IdP group | 15, 28 | 
| [Third-party MCP access to SAP solutions](https://architecture.learning.sap.com/docs/ref-arch/137800) | SAP | 2026-06-08 | Never proxy the caller's token; RFC 8693 exchange with agent and user; stateless servers | 13, 17, 30, 34 | 
| [Inventory MCP servers in your API center](https://learn.microsoft.com/en-us/azure/api-center/register-discover-mcp-server) | Microsoft | 2026-06-02 | Private registry exposing the v0.1 registry API | 19 | 
| [Scaling MCP adoption: our reference architecture](https://blog.cloudflare.com/enterprise-mcp/) ⚠ | Cloudflare | 2026-04-14 | Remote only, portals, DLP, shadow-MCP detection, Code Mode | 18, 21, 34 | 
| [MCP architecture patterns](https://ibm.github.io/mcp-context-forge/latest/best-practices/mcp-architecture-patterns/) | IBM ContextForge | Undated | Anti-patterns: passthrough, confused deputy, scope inflation, API mirroring | 17, 24, 28 | 
| [AI agent identity with Vault dynamic secrets](https://developer.hashicorp.com/validated-patterns/vault/ai-agent-identity-with-hashicorp-vault) | HashiCorp | Undated | User JWT, agent OBO, short-lived Vault credentials | 13, 28 | Not found. No public MCP reports from Forrester, IDC, McKinsey, BCG, Deloitte or Accenture. No MCP reference architecture in the Azure Architecture Center. No primary production write-ups from large banks. No industry source on conformance testing.