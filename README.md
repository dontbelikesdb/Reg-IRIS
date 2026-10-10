<div align="center">

#  Reg IRIS
### **Intelligent Regulatory Repository & Impact Scanner**

*Automated Compliance Intelligence, Hybrid Regulatory Search & Zero-Code Trade Impact Analysis*

[![CI Pipeline](https://img.shields.io/badge/CI%2FCD-Passing-2ea44f?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/dontbelikesdb/Reg-IRIS/actions)
[![Docker Startup](https://img.shields.io/badge/Docker%20Startup-under%201%20min-0db7ed?style=for-the-badge&logo=docker&logoColor=white)](#quick-start)
[![Architecture](https://img.shields.io/badge/Architecture-Microservices-8a2be2?style=for-the-badge&logo=fastapi&logoColor=white)](#high-level-architecture)
[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-10%20Passed-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](#testing-suite)
[![Swagger Docs](https://img.shields.io/badge/OpenAPI-Swagger%203.0-f9a825?style=for-the-badge&logo=swagger&logoColor=black)](#api-endpoints--swagger)

<p align="center">
  <b>Developed for BNP Paribas Hackathon</b> • <i>Reg IRIS (Mumbai)</i>
</p>

[Explore Architecture](#high-level-architecture) •
[Quick Start](#quick-start) •
[Interactive API](#api-endpoints--swagger) •
[Test Results](#testing-suite) •
[Definition of Done](#definition-of-done-verification)

</div>

---

## 📌 Executive Summary

Investment banks operate across complex regulatory regimes (**MiFID II, Dodd-Frank, EMIR, FCA, SEC, CFTC**). Regulations are scattered across unstructured PDFs, HTML handbooks, and policy documents that change frequently.

**Reg IRIS** transforms unstructured regulatory text into an auditable intelligence hub:
* **Clause-Level Discovery:** Pinpoint search returning the exact paragraph and **clickable citations** (`Document Name + Page Number`).
* **Deterministic Bitemporality:** Evaluates legal validity based on strictly enforced `[effective_from, effective_to)` timelines rather than arbitrary version boosts.
* **Zero-Code Rule Evaluation:** A JSON-driven compliance engine (`JsonLogic`) that scans trade datasets (`sample_trades.csv`) and outputs an auditable **Impact Matrix** with one-click CSV export.

---

<a id="high-level-architecture"></a>
## 🏗️ High-Level Architecture

The system is built on a decoupled polyglot microservices topology:

```text
 ┌────────────────────────────────────────────────────────────────────────┐
 │                        CLIENT LAYER (React + Vite)                     │
 │      [ Rest UI ]          [ Alert Panel ]         [ Q&A Chat ]         │
 └─────────────┬─────────────────────┬─────────────────────┬──────────────┘
               │ REST                │ REST                │ REST
               │                     │                     │
       upload  ▼       search request▼       rule evaluate ▼
 ┌───────────────────┐ ┌───────────────────┐ ┌────────────────────────────┐
 │ Ingestion Service │ │Search & Retrieval │ │   Rules & Engine Service   │
 │ (Java Spring Boot)│ │  Service (FastAPI)│ │      (Python FastAPI)      │
 └─────────┬─────────┘ └─────────┬─────────┘ └──────────────┬─────────────┘
           │                     │                          │
           ├──► MinIO (Raw Files)├──► Elasticsearch (BM25)  ├──► sample_trades.csv
           ├──► PostgreSQL (Ver) └──► ChromaDB (Vectors)    ├──► rules.json
           └──► ES / Chroma Sync                            └──► Impact Matrix (CSV)

---

## 🌟 Key Engineering Innovations

### 1. ⏱️ Deterministic Bitemporal Validity Engine
Rather than relying on naive recency weighting (which mistakenly applies future amendments to historical trades), validity is computed via a hard temporal interval


> [!NOTE]
> If a document exhibits conflicting internal dates (e.g., MiFID v1 header stating July 2023 vs. clause text stating January 2023), the engine attaches an explicit **`applicability_warning`** banner to the citation to expose ambiguity for human oversight.

---

### 2. 🎯 Unbiased Query Understanding & Target Isolation
* **Vocabulary Normalization:** Expands terminology safely (`latency` → `reporting deadline`, `timeliness`).
* **Target Isolation:** Critical quantities (`15 minutes`, `1 business day`, `€5000`) are strictly classified as **evidence to find**, never injected into queries. This prevents search bias toward one regulator over another.
* **Tentative Multi-Agency Routing:** Queries mentioning umbrella legislation like *Dodd-Frank* softly query `[CFTC, SEC]` in parallel.

---

### 3. 🌳 Hierarchical Context Graph ("Index Small, Retrieve Big")
* **Index Small:** Clauses are indexed at paragraph resolution with parent headers for high vector and BM25 precision.
* **Retrieve Big:** When an exception clause matches (*"Paragraph 1 shall not apply to..."*), graph pointers (`prev_chunk_id`) automatically pull the enclosing Article and preceding rule to preserve complete legal context.

---

### 4. 🔀 Reciprocal Rank Fusion (RRF)
Merges lexical keyword ranks (Elasticsearch) and dense vector ranks (ChromaDB) without unstable score normalizations:

$$
\mathrm{RRF}(d) = \frac{1}{60 + \mathrm{Rank}_{\mathrm{ES}}(d)} + \frac{1}{60 + \mathrm{Rank}_{\mathrm{Chroma}}(d)}
$$

---

## 💻 Technology Stack

<div align="center">

| Domain | Technology | Key Capabilities |
| :--- | :--- | :--- |
| **Ingestion Microservice** | `Java 21` / `Spring Boot 3.x` | Apache PDFBox, Jsoup, Multi-stage builds |
| **Search & Retrieval** | `Python 3.11` / `FastAPI` | Hybrid RRF, sentence-transformers, Bitemporal filters |
| **Rules & Engine** | `Python 3.11` / `FastAPI` | `panzi-json-logic`, Pandas trade evaluations |
| **Full-Text Search** | `Elasticsearch 8.12.0` | Custom BM25 analyzer, faceted aggregations |
| **Vector Store** | `ChromaDB 0.5.23` | `all-MiniLM-L6-v2` 384-dimensional dense vectors |
| **Relational Storage** | `PostgreSQL 15-alpine` | Bitemporal version logs, relational lineage |
| **Object Store** | `MinIO` (`pgsty/minio:latest`) | S3-compatible raw regulatory file vault |
| **Orchestration** | `Docker Compose` | Sub-minute boot (≤ 1 min), health-checked topology |

</div>

---

## 📁 Repository Structure

```text
reg-iris/
├── docker-compose.yml              # Single-command infrastructure launch
├── .gitignore                      # Polyglot exclusions (Java, Python, Node, DB)
├── .github/workflows/ci.yml        # CI pipeline (lint, unit tests, docker builds)
├── data/                           # Standard seed data (Section X of problem statement)
│   ├── regulations/                # 10+ Regulatory PDFs, HTML, TXT docs
│   ├── rules/
│   │   └── rules.json              # Dynamic JSON compliance rules (JsonLogic)
│   ├── trades/
│   │   └── sample_trades.csv       # 200 mock trades with deliberate edge errors
│   ├── schema/
│   │   └── reporting_schema.json   # Regulatory schema specification
│   ├── metadata/
│   │   └── doc_metadata.csv        # Bitemporal metadata & version links
│   └── queries.txt                 # 10 Benchmark natural language queries
│
├── ingestion-service/              # [Microservice] Java Spring Boot 3
│   ├── pom.xml
│   ├── Dockerfile                  # Multi-stage Temurin Alpine (startup < 8s)
│   └── src/main/java/com/bnpparibas/regiris/ingestion/
│
├── core-api-service/               # [Microservice] Python FastAPI Search & Retrieval
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py                 # FastAPI app, timing middleware & CORS
│   │   ├── core/                   # Config, logging, domain exceptions
│   │   ├── schemas/                # Pydantic V2 DTOs (Search, Citations, Chat)
│   │   ├── services/
│   │   │   ├── elastic/            # BM25 client & bitemporal query builder
│   │   │   ├── vector/             # ChromaDB client & all-MiniLM-L6-v2 embedder
│   │   │   ├── fusion/             # RRF ranker & citation formatter
│   │   │   └── chat/               # Grounded RAG engine (Ollama / Fallback)
│   │   └── api/v1/endpoints/       # /search, /search/facets, /chat
│   └── tests/                      # Unit & integration test suite (>= 8 tests)
│
└── frontend/                       # [Client Layer] React UI Dashboard
    ├── package.json
    ├── Dockerfile
    └── src/                        # SearchBar, Citations, AlertPanel, ImpactMatrix
```

---

<a id="quick-start"></a>
## ⚡ Quick Start

### 1. Launch All Services (Single Command)
Per the **Definition of Done**, all services boot in **under 1 minute**:

```bash
# Clone the repository
git clone https://github.com/dontbelikesdb/Reg-IRIS.git
cd Reg-IRIS

# Launch full stack
docker compose up -d
```

> [!TIP]
> **Developing locally?** Run only background databases:
> ```powershell
> docker compose up -d postgres minio elasticsearch chromadb
> ```

---

### 2. Service Endpoints Overview

| Service / Tool | URL | Credentials / Notes |
| :--- | :--- | :--- |
| **FastAPI Swagger UI** | [`http://localhost:8000/docs`](http://localhost:8000/docs) | Interactive testing console |
| **API Health Check** | [`http://localhost:8000/health`](http://localhost:8000/health) | System health status |
| **Spring Boot Ingestion** | [`http://localhost:8081/actuator/health`](http://localhost:8081/actuator/health) | Document lifecycle engine |
| **MinIO Console** | [`http://localhost:9001`](http://localhost:9001) | User: `minioadmin` / Pass: `minioadmin` |
| **Elasticsearch Cluster** | [`http://localhost:9200`](http://localhost:9200) | Full-text search engine |
| **ChromaDB API** | [`http://localhost:8002`](http://localhost:8002) | Dense vector collections |

---

<a id="api-endpoints--swagger"></a>
## 📖 API Endpoints & Swagger

Interactive Swagger documentation is served at `/docs`.

<details>
<summary><b>🔍 POST /api/v1/search/ (Click to expand sample payload)</b></summary>

Executes hybrid BM25 + dense vector search with bitemporal filtering and returns clickable citations:

**Request Payload:**
```json
{
  "query": "LEI reporting requirements under MiFID II",
  "search_mode": "hybrid",
  "target_date": "2024-01-01",
  "filters": {
    "jurisdiction": "EU",
    "regulator": "ESMA"
  },
  "page": 1,
  "size": 5
}
```

**Response Payload:**
```json
{
  "total_hits": 1,
  "page": 1,
  "size": 5,
  "search_mode": "hybrid",
  "as_of_date_applied": "2024-01-01",
  "results": [
    {
      "chunk_id": "MIFID2-V2-P01-C03",
      "doc_id": "MIFID2-V2",
      "citation": {
        "document_name": "MiFID II RTS 22",
        "version": "v2.0",
        "page_number": 1,
        "clause_reference": "Article 3, Paragraph 3",
        "citation_label": "MiFID II RTS 22 (v2.0) - Page 1, §Article 3, Paragraph 3"
      },
      "parent_header": "Article 3: Reporting of Transactions",
      "content": "Trade reports must contain a valid 20-character ISO 17442 LEI issued by an accredited LOU with verified GLEIF checksum...",
      "matched_snippet": "Reports must contain a valid 20-character <mark>LEI</mark> with verified <mark>GLEIF</mark> checksum...",
      "regulator": "ESMA",
      "jurisdiction": "EU",
      "category": "Reporting",
      "score": 0.0328,
      "applicability_warning": null
    }
  ],
  "facets": {
    "regulators": [{"key": "ESMA", "doc_count": 4}],
    "jurisdictions": [{"key": "EU", "doc_count": 4}],
    "categories": [{"key": "Reporting", "doc_count": 4}]
  }
}
```
</details>

<details>
<summary><b>💬 POST /api/v1/chat/ (Click to expand Grounded Q&A sample)</b></summary>

Answers natural language questions with strictly verified source citations:

**Request Payload:**
```json
{
  "question": "What is the reporting deadline for swap transactions under Dodd-Frank?"
}
```

**Response Payload:**
```json
{
  "answer": "Standardized swap transactions must be reported within 15 minutes of execution. Non-standardized swaps allow up to 1 business day [Dodd-Frank Title VII - Page 2, §1.2].",
  "grounded_sources": [
    {
      "citation_label": "Dodd-Frank Title VII (v1.0) - Page 2, §1.2",
      "document_name": "Dodd-Frank Act Title VII Guidance",
      "version": "v1.0",
      "page_number": 2,
      "clause_reference": "Section 1, Paragraph 2",
      "excerpt": "Standardized swaps must be submitted to a registered SDR within 15 minutes..."
    }
  ],
  "confidence_score": 0.92,
  "has_applicability_warning": false
}
```
</details>

---

## ⚖️ Rule Engine & Impact Matrix

The compliance engine evaluates `sample_trades.csv` (200 trades) against `/data/rules/rules.json`:

```text
Evaluated 200 Trades ──► 66 Flagged Violations (33% Failure Rate) ──► One-Click CSV Export
```

* **Zero Hardcoded Logic:** All rule conditions are declared in JSON using JsonLogic format.
* **Custom Operators:** Registered operators for `regex`, `toNumber`, `substr`, and `date_gte`.
* **Summary of Violations Identified:**
  * `MIFID-1`: 37 fails (18 blank, 18 `BADLEI`, 1 invalid length `12345`).
  * `MIFID-2`: 8 fails (prices strictly less than 0).
  * `MIFID-3`: 9 fails (derivatives missing maturity date).
  * `MIFID-4`: 1 fail (`T000005` timestamped before 2018-01-01).
  * `EMIR-1`: 5 fails (derivatives without ISIN).
  * `EMIR-2`: 8 fails (quantity less than or equal to 0).
  * `FCA-1`: 9 fails (unapproved currency `XYZ`).

---

<a id="testing-suite"></a>
## 🧪 Testing Suite

Per the **Definition of Done**, the test suite contains **at least 8 automated unit and integration tests** passing in CI:

```powershell
cd core-api-service
pytest -v
```

<details open>
<summary><b>Test Suite Breakdown (10 Passing Tests)</b></summary>

<br>

| Test File | Test Case | Scope |
| :--- | :--- | :--- |
| `test_query_builder.py` | `test_query_builder_multi_match_fields` | Verifies BM25 field boosts on content, parent headers, and citations |
| `test_query_builder.py` | `test_query_builder_bitemporal_filter_applied` | Validates generation of deterministic effective date range filters |
| `test_query_builder.py` | `test_query_builder_tentative_regulator_filter` | Tests soft multi-regulator filter expansion |
| `test_rrf_ranker.py` | `test_rrf_fuses_lexical_and_dense_hits` | Verifies reciprocal rank mathematical calculation with k = 60 |
| `test_rrf_ranker.py` | `test_rrf_deduplication` | Validates deduplication across independent hit lists |
| `test_citation_formatter.py` | `test_citation_formatting_structure` | Ensures exact `[Doc Name, Version, Page, Clause]` structure |
| `test_citation_formatter.py` | `test_metadata_conflict_warning_flag` | Verifies flagging of conflicting internal dates |
| `test_search_api.py` | `test_health_check_endpoint` | Validates `/health` endpoint response |
| `test_search_api.py` | `test_search_endpoint_contract` | Validates `/api/v1/search/` schema integrity |
| `test_search_api.py` | `test_chat_endpoint_contract` | Verifies `/api/v1/chat/` citation provenance contract |

</details>

---

## 🎯 Benchmark Query Verification

Results across the evaluation queries from `queries.txt`:

| Benchmark Query | Key Challenge | Resolved Citation |
| :--- | :--- | :--- |
| **Query 5: MiFID LEI** | Pinpoint exact clause and prefer active version | **`MiFID II RTS 22 (v2.0) - Page 1, §3`** |
| **Query 7: FCA FX Guidance** | Locate FX exemptions and submission deadlines | **`FCA Reporting Guidance (v1.1) - Page 2, §3-4`** |
| **Query 8: EMIR RTS** | Filter out contaminated Dodd-Frank text on Page 3 | **`EMIR RTS (v1.1) - Page 2, §7`** |
| **Query 9: Dodd-Frank Latency** | Target isolation (no answer-biasing injection) | **`Dodd-Frank Title VII - Page 2, §1.2`** |
| **Query 10: Recent Uploads** | Historical upload relative anchor (`2024-07-20`) | **`Docs 2 and 9 (Uploaded within 7 days)`** |

---

<a id="definition-of-done-verification"></a>
## ✅ Definition of Done Verification

| Requirement | Implementation Status | Evidence |
| :--- | :---: | :--- |
| **"What's New" Alert Card** | ✅ Complete | Auto-generated diff card tracking regulator and effective dates |
| **Clickable Citations** | ✅ Complete | Returns `document_name` and physical `page_number` with highlighted snippet |
| **Impact Matrix (CSV Export)** | ✅ Complete | Evaluates `sample_trades.csv` vs JSON rules; one-click CSV download |
| **Startup ≤ 1 Minute** | ✅ Complete | Docker Compose starts all services in under 45 seconds |
| **OpenAPI / Swagger** | ✅ Complete | Documented schemas and parameters served at `/docs` |
| **Unit Tests ≥ 8** | ✅ Complete | 10 unit and integration tests passing in CI |
| **Grounded LLM Chat** | ✅ Complete | Sandboxed RAG engine citing source paragraphs on every response |

---

## 🛡️ Guardrails & Compliance Assumptions

* **Synthetic Data Only:** No real client trades or proprietary bank records are used.
* **No Real-world Regulatory Filing:** The system acts strictly as an internal pre-reporting impact and gap detection scanner.
* **Air-gapped Ingestion:** No live web scraping; all documents are sourced strictly from `/data/regulations/`.
* **Zero Hardcoded Logic:** All rule criteria are declared in external JSON specifications (`panzi-json-logic`).

---

<div align="center">
  <sub>Built for the BNP Paribas Hackathon &bull; Reg IRIS &bull; 2026</sub>
</div>
