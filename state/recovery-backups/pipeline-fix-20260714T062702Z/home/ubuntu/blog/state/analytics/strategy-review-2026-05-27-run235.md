# Strategy Review - 2026-05-27 Run 235

## Phase 1 Status

- Current phase: Phase 1 (First Signal Integration)
- KD range: 0-25
- Search volume filter: 200+ estimated monthly searches
- Analytics files found: prior strategy reviews only; no separate GSC query export was present in `~/blog/state/analytics/`
- Queue health before run: 2746 total topics, 2214 queued
- Queue health after run: 2766 total topics, 2234 queued

## New Topics Added This Run (+20)

### AI For Developers (+18)

1. `huggingface-open-agent-leaderboard-guide-2026` - Hugging Face Open Agent Leaderboard. KD 5, SV 420
2. `huggingface-hub-agents-mcp-skills-guide-2026` - Hugging Face agents MCP skills. KD 4, SV 360
3. `huggingface-deepinfra-inference-providers-guide-2026` - Hugging Face DeepInfra inference providers. KD 5, SV 300
4. `openai-privacy-filter-web-apps-guide-2026` - OpenAI Privacy Filter web apps. KD 4, SV 280
5. `pinecone-marketplace-guide-2026` - Pinecone Marketplace. KD 5, SV 420
6. `pinecone-knowledge-agent-toolkit-guide-2026` - Pinecone Knowledge Agent Toolkit. KD 4, SV 320
7. `pinecone-rag-agent-evaluation-metrics-guide-2026` - RAG agent evaluation metrics Pinecone. KD 5, SV 380
8. `pinecone-rerankers-rag-guide-2026` - Pinecone rerankers for RAG. KD 6, SV 460
9. `pinecone-multi-query-rag-guide-2026` - multi-query RAG Pinecone. KD 5, SV 310
10. `weaviate-built-in-mcp-server-guide-2026` - Weaviate MCP Server. KD 4, SV 320
11. `weaviate-query-profiling-guide-2026` - Weaviate query profiling. KD 4, SV 260
12. `weaviate-diversity-search-mmr-guide-2026` - Weaviate diversity search MMR. KD 4, SV 240
13. `qdrant-skills-ai-agents-guide-2026` - Qdrant Skills for AI agents. KD 4, SV 330
14. `qdrant-turboquant-guide-2026` - Qdrant TurboQuant. KD 4, SV 280
15. `qdrant-gpu-indexing-multi-az-audit-logging-guide-2026` - Qdrant GPU indexing Multi-AZ audit logging. KD 5, SV 300
16. `qdrant-hybrid-graph-rag-platform-guide-2026` - Qdrant hybrid graph RAG. KD 5, SV 360
17. `langchain-mongodb-agent-stack-guide-2026` - LangChain MongoDB agent stack. KD 5, SV 340
18. `langchain-nvidia-agent-platform-guide-2026` - LangChain NVIDIA agent platform. KD 6, SV 380

### AI Coding Tools (+1)

1. `weaviate-engram-memory-claude-code-guide-2026` - Weaviate Engram Claude Code memory. KD 4, SV 300

### LLM Comparison (+1)

1. `nemotron-3-nano-omni-agents-guide-2026` - Nemotron 3 Nano Omni agents. KD 5, SV 340

## Candidate Validation

All promoted candidates passed:

- KD within configured range (0-25)
- Search volume estimate >= 200
- Unique slug across `topics.json` and published post filenames
- Required title, slug, and keyword present
- Cluster fits current focus topics or cluster priority

Rejected this run: 0

## Competitor Signals

- Hugging Face is expanding from model hosting into agent execution surfaces: Open Agent Leaderboard, Hub Agents, MCP, Skills, and provider routing. This creates topics with practical evaluation and integration intent.
- Pinecone is moving from vector database education into managed knowledge apps via Marketplace and Knowledge Agent Toolkit. The strongest gaps are evaluation, reranking, and multi-query RAG implementation.
- Weaviate 1.37 adds built-in MCP, query profiling, and MMR preview features. These map cleanly to developer how-to content and internal links from existing Weaviate/vector search coverage.
- Qdrant is pushing production retrieval primitives: agent skills, TurboQuant, GPU indexing, Multi-AZ, audit logging, and hybrid Graph RAG. These support bottom-funnel production RAG articles.
- LangChain's MongoDB and NVIDIA partnerships reinforce a larger enterprise agent backend trend: durable state, operational data access, observability, deployment, and model serving in one stack.

## Strategy Adjustments

- Keep Phase 1 behavior. No Phase 2 performance logic was applied because there is no separate GSC query export.
- Increase emphasis on the "agent infrastructure" subcluster: MCP-enabled data systems, retrieval evaluation, managed knowledge apps, agent skill packages, query profiling, and enterprise agent backends.
- Use existing RAG/vector database posts as internal-link hubs. New Qdrant, Pinecone, and Weaviate topics should link back to vector database comparison, RAG best practices, agent memory, and LLM observability articles.
- Preserve the current KD range. All new estimates are low-KD, long-tail topics with implementation intent rather than broad "what is RAG" coverage.

## Sources Reviewed

- Hugging Face Blog: https://huggingface.co/blog
- Hugging Face Open Agent Leaderboard: https://huggingface.co/blog/ibm-research/open-agent-leaderboard
- Hugging Face Hub Agents docs: https://huggingface.co/docs/hub/en/agents
- Pinecone RAG series: https://www.pinecone.io/learn/series/rag/
- Pinecone RAG agent evaluation: https://www.pinecone.io/learn/series/rag/ragas/
- Pinecone 2026 release notes: https://docs.pinecone.io/release-notes/2026
- Weaviate Blog: https://weaviate.io/blog.html
- Weaviate Agent Skills: https://weaviate.io/blog/weaviate-agent-skills
- Qdrant Blog: https://qdrant.tech/blog/
- Qdrant Skills for AI Agents: https://qdrant.tech/blog/qdrant-skills-release/
- Qdrant Hybrid Graph RAG case study: https://qdrant.tech/blog/case-study-datagraphs/
- LangChain NVIDIA announcement: https://www.langchain.com/blog/nvidia-enterprise
- LangChain MongoDB partnership: https://www.langchain.com/blog/announcing-the-langchain-mongodb-partnership-the-ai-agent-stack-that-runs-on-the-database-you-already-trust
