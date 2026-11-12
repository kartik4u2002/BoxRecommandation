# AI Assistance and Usage Disclosure

This document provides a transparent, truthful disclosure of the AI assistance utilized in the architecture, implementation, and verification of the **AI-Assisted Box Selection System**.

---

## 1. AI Tools Used

- **AI Assistant:** Antigravity (Google DeepMind advanced agentic coding assistant powered by Gemini 3.8 Flash).
- **Environment:** Windows PowerShell, Python 3.13.3, Django 5.2.5, Django REST Framework 3.16.1.

---

## 2. Actual Prompts Used

The complete specification was provided via the master user prompt:
- **Prompt:** `"Perform a final code review of the completed Box Selection System.

Do not add new features.

Review the implementation against the original assignment and verify:

1. All database models have appropriate validation.
2. The packing engine checks all six orientations.
3. Products cannot overlap or exceed box boundaries.
4. Product quantities are handled correctly.
5. Weight and volume checks work correctly.
6. The cheapest feasible box is selected.
7. Every module has relevant unit tests.
8. Tests execute against actual business logic.
9. All tests pass when running `python manage.py test`.
10. README.md links to TEST_OUTPUT.md.
Run the complete test suite again after any code changes.

Report any remaining limitations honestly."`
- The prompt specified exact requirements for:
  - Four models (`Product`, `Box`, `Order`, `OrderItem`).
  - Business rules for preliminary filtering (active status, weight, volume).
  - 3D packing engine using Extreme Point placement, deduplicated 6-axis rotation, non-overlapping validation, and boundary containment.
  - Box selection with cost prioritization and volume tie-breaker.
  - Modular REST API endpoints and strict test coverage.

---

## 3. Code Suggestions Accepted

1. **Modular Django Architecture:**
   - Kept each domain model isolated in its respective app (`products/`, `boxes/`, `orders/`).
   - Isolated business logic and algorithms inside `recommendations/services/` instead of views.

2. **Model Integrity and Validation:**
   - Used `DecimalField` for dimensions, weight, and monetary values.
   - Enforced validation both at the Django ORM level (overriding `save()` to invoke `full_clean()`) and at the DRF serializer level.
   - Implemented `volume`, `total_weight`, and `total_volume` calculation properties.

3. **3D Extreme Point Packing Engine:**
   - Implemented an Extreme Point coordinate-based heuristic that maintains candidate points sorted bottom-to-top ($Z$), back-to-front ($Y$), and left-to-right ($X$).
   - Generated the 6 canonical rectangular orientations and deduplicated them while preserving order.
   - Used 3D Axis-Aligned Bounding Box (AABB) intersection tests to ensure zero volume overlap.

4. **Recommendation Service (`BoxSelector`):**
   - Implemented the full 5-step pipeline: order aggregation $\rightarrow$ preliminary filtering $\rightarrow$ 3D packing validation $\rightarrow$ cost/volume sorting $\rightarrow$ result delivery.

---

## 4. Code Suggestions Rejected or Modified

1. **App Routing Placement:**
   - *Initial consideration:* Putting `recommend_box` endpoint under `orders/views.py`.
   - *Modification:* Adhered strictly to the prompt's suggested project structure by housing `RecommendBoxView` under `recommendations/views.py` and exposing it via `recommendations/urls.py` mounted at `api/orders/<id>/recommend-box/`.

2. **Extreme Point Projection Enhancement:**
   - *Initial thought:* Only adding $(x+dx, y, z)$, $(x, y+dy, z)$, and $(x, y, z+dz)$ as new candidate points.
   - *Modification:* Added coordinate projections against the surfaces of other already placed items so that corner steps, gaps, and notches between adjacent items are discovered as valid placement locations.

3. **Response Number Formatting:**
   - *Initial thought:* Relying on DRF's default Decimal serializer representation, which converts Decimals to strings (e.g., `"45.00"`).
   - *Modification:* Created a dedicated `format_number` serializer utility to serialize numeric values as numbers (`45` or `45.5`) exactly matching the prompt's example JSON response.

---

## 5. Mistakes Identified in AI-Generated Suggestions

1. **Initial Migration Discovery:**
   - *Issue:* When `python manage.py makemigrations` was first run, Django reported `"No changes detected"`.
   - *Root Cause:* Because the workspace was created from scratch, the app directories lacked the initial `migrations/` package folders with `__init__.py`.
   - *Correction:* Created `migrations/__init__.py` in `products/`, `boxes/`, `orders/`, and `recommendations/`, after which `makemigrations` detected all models and generated `0001_initial.py` migrations properly.

---

## 6. How the Final Implementation Was Verified

The entire application was verified directly through automated test execution and system checks:

1. **System Check:**
   - Ran `python manage.py check` to verify application configuration, model relations, and URL routing. Zero issues detected.
2. **Migrations Verification:**
   - Ran `python manage.py migrate` to verify all schema tables and foreign key constraints were created cleanly in SQLite.
3. **Automated Unit & Integration Test Suite:**
   - Executed `python manage.py test` and `python manage.py test -v 2`.
   - Executed 51 comprehensive automated test cases covering:
     - Product model and API validations (dimensions > 0, weight $\ge$ 0, negative/zero rejections).
     - Box model and API validations (dimensions > 0, max weight > 0, cost $\ge$ 0, inactive exclusion).
     - Order model and API validations (order creation, retrieval, item quantities, empty order rejection).
     - Packing engine unit tests (single product, rotation, multiple products, cannot-pack-together, overlap prevention, boundary confinement, deduplication).
     - Box selector unit tests (cost prioritization, volume tie-breaker, weight/volume limits, inactive exclusion).
     - Primary API endpoint tests (success payload, no suitable box, invalid order ID, empty order).
   - Confirmed 51 out of 51 tests passed with `OK` (0 failures, 0 errors).
