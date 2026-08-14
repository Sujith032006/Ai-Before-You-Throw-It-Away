# 🏗️ Before You Throw It Away — System Architecture

## Overview
"Before You Throw It Away" is a full-stack AI reuse assistant. It empowers users to scan household items using computer vision (RF-DETR Transformer + Multimodal Vision AI), ranks reuse ideas using a deterministic recommendation engine, personalizes step-by-step instructions using Generative AI, tracks completion, and visualizes impact metrics in a user dashboard backed by database persistence.

---

## 🏛️ System Architecture

```
                         USER
                           │
                           ▼
                  ┌─────────────────┐
                  │ React Frontend  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   FastAPI API   │
                  └───────┬─────────┘
                          │
          ┌───────────────┼────────────────┐
          │               │                │
          ▼               ▼                ▼
       RF-DETR      Recommendation       LLM
   (rtdetr-l.pt)        Engine        (Vision AI)
          │               │                │
          └───────────────┼────────────────┘
                          │
                          ▼
                     SQLAlchemy
                          │
                          ▼
                PostgreSQL / SQLite
                          │
                          ▼
                 Dashboard & History
```

---

## 💾 Database Schema (ORM Models)

- **`User`**: `id` (UUID), `name`, `email`, `created_at`
- **`Scan`**: `id` (UUID), `user_id` (FK), `image_reference`, `status`, `created_at`
- **`Detection`**: `id` (UUID), `scan_id` (FK), `object_name`, `confidence`, `bounding_box`, `created_at`
- **`Recommendation`**: `id` (UUID), `scan_id` (FK), `project_id`, `score`, `rank`, `created_at`
- **`SelectedProject`**: `id` (UUID), `user_id` (FK), `scan_id` (FK), `project_id`, `status` (`selected`, `in_progress`, `completed`), `selected_at`
- **`PersonalizedGuide`**: `id` (UUID), `selected_project_id` (FK), `guide_content` (JSON), `created_at`
- **`ProjectCompletion`**: `id` (UUID), `selected_project_id` (FK), `project_id`, `user_id` (FK), `completed_at`
- **`ChatSession`**: `id` (UUID), `user_id` (FK), `selected_project_id` (FK), `created_at`
- **`ChatMessage`**: `id` (UUID), `session_id` (FK), `role` (`user`/`assistant`), `content`, `created_at`

---

## 📡 API Reference

### Scan & Analyze
- `POST /api/analyze` & `POST /api/scan`: Upload image, run image quality pre-checker, RF-DETR Transformer detection, confidence evaluation, Multimodal Vision AI verification, and persist scan & detection record.

### Recommendations
- `POST /api/recommendations`: Submit user context (goal, tools, materials, budget, time, difficulty). Compute & persist ranked recommendations.
- `GET /api/projects/{id}`: Fetch factual project knowledge base details.

### Generative AI & Personalization
- `POST /api/projects/personalized-guide`: Generate & persist personalized step-by-step instructions.
- `POST /api/chat`: Send message to AI Project Assistant, return context-aware response, and log conversation turn.

### Dashboard, History & Completion
- `GET /api/dashboard`: Aggregates key impact metrics (`total_scans`, `total_projects`, `completed_projects`) and recent activity.
- `GET /api/history`: Fetch list of user's previous scans with status badges and match scores.
- `POST /api/projects/{id}/complete`: Record project completion event.
- `GET /api/health`: Health status returning `"database": "connected"` and `"ai": "available"`.
