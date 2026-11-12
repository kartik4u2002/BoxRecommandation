# AI-Assisted Box Selection System

An automated, deterministic packaging recommendation engine and REST API built with Django and Django REST Framework for ecommerce fulfillment warehouses.

---

## 1. Project Overview

In ecommerce logistics, packing customer orders into oversized boxes increases shipping expenses, wastes void-fill material, and increases carbon footprint. Packing orders into undersized boxes leads to product damage or shipment rejection.

The **AI-Assisted Box Selection System** provides a deterministic backend solution that evaluates customer orders, accounts for product dimensions, weights, and quantities, tests real 3D spatial packing feasibility, and automatically recommends the cheapest available shipping box that can safely hold the order.

---

## 2. Problem Statement

Given:
- A catalog of products, each with 3D dimensions (length, width, height) and weight.
- An inventory of available shipping boxes, each with internal dimensions, maximum weight capacity, cost, and availability status.
- A customer order comprising one or more products with specified quantities.

The system must:
1. Reject boxes that cannot support the total order weight or combined product volume.
2. Explore 3D spatial orientations (up to 6 unique rotations per item).
3. Validate that all items physically fit within the box boundaries without overlapping using a 3D packing heuristic.
4. Select the lowest-cost suitable box, breaking cost ties by choosing the box with the smallest internal volume.
5. Provide a REST API for warehouse operations and client integrations.

---

## 3. Features

- **Product Management:** CRUD endpoints with strict validation ensuring positive dimensions ($> 0$) and non-negative weight ($\ge 0$).
- **Shipping Box Inventory:** Box catalog management with validation for internal dimensions, weight limits, cost, and active/inactive availability.
- **Order Management:** Atomic order creation supporting multiple items and quantities with validation rejecting empty orders or non-positive quantities.
- **Extreme Point 3D Packing Engine:** Deterministic spatial heuristic placing items bottom-to-top, back-to-front, and left-to-right with 3D collision detection and boundary checks.
- **Rotation Awareness:** Tests all 6 spatial orientations per rectangular product while eliminating redundant rotations for symmetrical items (e.g., cubes).
- **Cost-Optimized Recommendation:** Evaluates eligible boxes, sorts by ascending cost, and applies volume as a tie-breaker.
- **Clean RESTful API:** Built with Django REST Framework, returning clean JSON payloads and proper HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`).
- **Comprehensive Test Suite:** 51 automated unit and integration tests covering models, services, heuristics, and API endpoints.

---

## 4. Technology Stack

- **Language:** Python 3 (tested on 3.13)
- **Framework:** Django 5.x
- **API Toolkit:** Django REST Framework (DRF) 3.16.x
- **Database:** SQLite
- **Testing:** Django `TestCase` and DRF `APITestCase` (Python `unittest`)
- **Version Control:** Git

*No external LLM APIs, machine learning libraries, or third-party packing binaries are used. All packing and recommendation logic is 100% deterministic Python.*

---

## 5. Project Directory Structure

```text
box_selection_system/
│
├── manage.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── TEST_OUTPUT.md
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── products/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│
├── boxes/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│
├── orders/
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   └── migrations/
│
└── recommendations/
    ├── __init__.py
    ├── apps.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    ├── tests.py
    ├── migrations/
    └── services/
        ├── __init__.py
        ├── packing_engine.py
        └── box_selector.py
```

---

## 6. Database Model Explanation

### 1. `Product` (`products/models.py`)
Represents an item available in the ecommerce catalog.
- `id`: AutoField primary key.
- `name`: CharField (max 255 characters).
- `length`: DecimalField ($> 0$), internal dimension in centimeters.
- `width`: DecimalField ($> 0$), internal dimension in centimeters.
- `height`: DecimalField ($> 0$), internal dimension in centimeters.
- `weight`: DecimalField ($\ge 0$), weight in kilograms.
- `volume`: Computed property returning $L \times W \times H$.

### 2. `Box` (`boxes/models.py`)
Represents a standardized shipping container.
- `id`: AutoField primary key.
- `name`: CharField (max 255 characters).
- `length`: DecimalField ($> 0$), internal usable length in centimeters.
- `width`: DecimalField ($> 0$), internal usable width in centimeters.
- `height`: DecimalField ($> 0$), internal usable height in centimeters.
- `max_weight`: DecimalField ($> 0$), maximum allowable payload in kilograms.
- `cost`: DecimalField ($\ge 0$), packaging cost.
- `is_active`: BooleanField, defaults to `True`. Inactive boxes are skipped during recommendations.
- `volume`: Computed property returning $L \times W \times H$.

### 3. `Order` (`orders/models.py`)
Represents a customer shipment request.
- `id`: AutoField primary key.
- `customer_name`: CharField (max 255 characters).
- `created_at`: DateTimeField with `auto_now_add=True`.
- `status`: CharField with choices (`PENDING`, `PACKED`, `SHIPPED`, etc.), defaults to `PENDING`.
- `total_weight`: Computed property aggregating $(\text{weight} \times \text{quantity})$ for all items.
- `total_volume`: Computed property aggregating $(\text{volume} \times \text{quantity})$ for all items.

### 4. `OrderItem` (`orders/models.py`)
Intermediary line item linking an Order with a Product and quantity.
- `id`: AutoField primary key.
- `order`: ForeignKey to `Order` with `on_delete=models.CASCADE` and `related_name='items'`.
- `product`: ForeignKey to `Product` with `on_delete=models.CASCADE` and `related_name='order_items'`.
- `quantity`: PositiveIntegerField with `MinValueValidator(1)`.

*Model integrity is guaranteed: each model's `save()` method calls `self.full_clean()` to enforce field validations at both ORM and serializer layers.*

---

## 7. Box Selection Algorithm Explanation

The recommendation process runs inside `recommendations/services/` through five sequential steps:

### Step 1: Calculate Order Requirements
- Fetch all line items for the order and expand them into individual product units based on their quantities.
- Compute the aggregate order weight ($\sum \text{weight} \times \text{qty}$) and aggregate volume ($\sum \text{volume} \times \text{qty}$).
- Reject orders that contain zero items.

### Step 2: Preliminary Filtering
Reject a box if:
- `is_active` is `False`.
- `box.max_weight < total_order_weight`.
- `box.volume < total_product_volume`.

*Note: Preliminary volume filtering is a necessary condition for feasibility, but not a sufficient proof that products fit spatially.*

### Step 3: Product Orientation Generation
Each rectangular item has up to 6 spatial rotations:
1. $L \times W \times H$
2. $L \times H \times W$
3. $W \times L \times H$
4. $W \times H \times L$
5. $H \times L \times W$
6. $H \times W \times L$

Duplicate rotations are dynamically pruned while preserving deterministic evaluation order (e.g., a cube of $10 \times 10 \times 10$ yields exactly 1 unique orientation; an item with two equal dimensions yields 3).

### Step 4: 3D Extreme Point Packing Validation
Implemented in `recommendations/services/packing_engine.py`:
1. **Item Ordering:** Sort product units by descending volume, using maximum single dimension as a tie-breaker, placing bulkier items first.
2. **Coordinate Pool:** Maintain candidate placement points starting at $(0, 0, 0)$. Points are sorted by lowest $Z$ (gravity / layer-by-layer), lowest $Y$, and lowest $X$.
3. **Collision & Boundary Check:** For each item, iterate over candidate points and unique orientations. Ensure:
   - $px + dx \le \text{box.length}$, $py + dy \le \text{box.width}$, $pz + dz \le \text{box.height}$.
   - No 3D Axis-Aligned Bounding Box (AABB) overlap with any previously placed item. Two boxes overlap if and only if:
     $$\max(x_1, x_2) < \min(x_1+dx_1, x_2+dx_2) \land \max(y_1, y_2) < \min(y_1+dy_1, y_2+dy_2) \land \max(z_1, z_2) < \min(z_1+dz_1, z_2+dz_2)$$
4. **Point Update:** When an item is placed at $(px, py, pz)$, generate extreme points along its faces and projected against neighboring placed items.
5. If any single item cannot find a valid placement coordinate and orientation, the box is marked unfeasible and the engine returns `False`.

### Step 5: Optimal Box Selection
- All candidate boxes that pass preliminary checks and 3D packing are collected into `feasible_boxes`.
- Feasible boxes are sorted using:
  $$\text{sort key} = (\text{cost}, \text{volume}, \text{id})$$
- The first box is returned as the cheapest suitable container.
- If multiple boxes share the lowest cost, the one with the smallest internal volume is selected to minimize void space.
- If no boxes can accommodate the order, an explanatory failure message is returned.

---

## 8. API Endpoint Documentation

| Method | Endpoint | Description | Status Codes |
|---|---|---|---|
| `POST` | `/api/products/` | Create a new product | `201 Created`, `400 Bad Request` |
| `GET` | `/api/products/` | List all products | `200 OK` |
| `POST` | `/api/boxes/` | Create a new shipping box | `201 Created`, `400 Bad Request` |
| `GET` | `/api/boxes/` | List all shipping boxes | `200 OK` |
| `POST` | `/api/orders/` | Create a new order with items | `201 Created`, `400 Bad Request` |
| `GET` | `/api/orders/{id}/` | Retrieve order details & line items | `200 OK`, `404 Not Found` |
| `POST` | `/api/orders/{id}/recommend-box/` | Recommend best box for order | `200 OK`, `400 Bad Request`, `404 Not Found` |

---

## 9. Example API Request and Response

### Create an Order
**Request:**
`POST /api/orders/`
```json
{
  "customer_name": "Alice Smith",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 2,
      "quantity": 1
    }
  ]
}
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "customer_name": "Alice Smith",
  "status": "PENDING",
  "created_at": "2026-11-12T14:45:00Z",
  "total_weight": 3.0,
  "total_volume": 4200.0,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Wireless Headphones",
        "length": "20.00",
        "width": "15.00",
        "height": "7.00",
        "weight": "0.50"
      },
      "quantity": 2,
      "subtotal_weight": "1.00",
      "subtotal_volume": "4200.00"
    }
  ]
}
```

### Recommend Box for Order
**Request:**
`POST /api/orders/1/recommend-box/`

**Successful Response (`200 OK`):**
```json
{
  "success": true,
  "order_id": 1,
  "recommended_box": {
    "id": 2,
    "name": "Medium Box",
    "dimensions": {
      "length": 45,
      "width": 35,
      "height": 15
    },
    "max_weight": 10,
    "actual_weight": 3,
    "cost": 30
  },
  "reason": "Lowest-cost box satisfying weight and packing requirements."
}
```

**No Suitable Box Response (`400 Bad Request`):**
```json
{
  "success": false,
  "order_id": 1,
  "error": "No available box can physically accommodate the dimensions of the items in this order."
}
```

**Order Not Found Response (`404 Not Found`):**
```json
{
  "success": false,
  "order_id": 9999,
  "error": "Order with ID 9999 does not exist."
}
```

---

## 10. Installation Instructions

### Prerequisites
- Python 3.10+ installed.
- Git installed.

### Setup Steps
1. Clone the repository and navigate into the project root:
   ```bash
   git clone <repository_url>
   cd Box_recommendation
   ```

2. (Optional) Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 11. Instructions to Run Migrations

To apply database migrations to the SQLite database:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 12. Instructions to Start the Django Server

To launch the local development server:

```bash
python manage.py runserver
```

The API endpoints will be accessible at `http://127.0.0.1:8000/api/`.

---

## 13. Instructions to Execute Unit Tests

To run the complete automated test suite:

```bash
python manage.py test
```

For verbose test-by-test output:

```bash
python manage.py test -v 2
```

---

## 14. Test Execution Output

All 51 automated unit and integration tests have been executed and verified.

[View Test Execution Output](TEST_OUTPUT.md)

---

## 15. Assumptions and Limitations

1. **Single-Box Assumption:** Each order must fit completely inside a single shipping box. Multi-box order splitting is intentionally excluded per project specifications.
2. **Cuboidal / Rectangular Shapes:** All products and shipping boxes are modeled as 3D axis-aligned cuboids. Irregular or deformable items (e.g., apparel in polybags) are approximated by their outer bounding rectangular dimensions.
3. **Deterministic Heuristic vs. Global Optimum:** 3D Bin Packing is known to be NP-hard. The packing engine employs a greedy Extreme Point placement heuristic. While deterministic, fast, and effective for ecommerce scenarios, it does not guarantee finding a solution for pathological edge cases where complex interlocking patterns are required.
4. **No Dynamic Shifting / Gravity Settling:** Items are placed rigidly without modeling physical settling or friction.
5. **No Authentication / Authorization:** Per requirements, endpoints are open and do not implement user authentication or roles.
