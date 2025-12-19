# Original ERPNext Sales Cycle - Complete Flow Analysis

## Overview

This document analyzes the original ERPNext sales cycle flow from the actual codebase. It documents how the system handles the complete sales process from Quotation to Sales Order to Delivery Note to Sales Invoice.

**Analysis Date:** 2025-01-XX
**ERPNext Version:** Based on current codebase
**Location:** `/home/administrator/frappe-bench/apps/erpnext`

---

## Table of Contents

1. [Sales Cycle Flow Diagram](#sales-cycle-flow-diagram)
2. [Document Hierarchy](#document-hierarchy)
3. [Quotation Flow](#quotation-flow)
4. [Sales Order Flow](#sales-order-flow)
5. [Delivery Note Flow](#delivery-note-flow)
6. [Sales Invoice Flow](#sales-invoice-flow)
7. [Status Management System](#status-management-system)
8. [Quantity & Amount Tracking](#quantity--amount-tracking)
9. [Document Creation Methods](#document-creation-methods)
10. [Key Business Rules](#key-business-rules)

---

## Sales Cycle Flow Diagram

```
┌─────────────┐
│  Quotation  │
│  (Draft)    │
└──────┬──────┘
       │ Submit
       ▼
┌─────────────┐
│  Quotation  │
│  (Open)     │
└──────┬──────┘
       │ make_sales_order()
       ▼
┌─────────────┐
│ Sales Order │
│  (Draft)    │
└──────┬──────┘
       │ Submit
       ▼
┌─────────────┐
│ Sales Order │
│ (To Deliver │
│  and Bill)  │
└──────┬──────┘
       │
       ├──────────────┬──────────────┐
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  Delivery   │ │   Sales    │ │  Material   │
│    Note     │ │  Invoice    │ │  Request    │
│             │ │            │ │             │
└──────┬──────┘ └──────┬──────┘ └─────────────┘
       │              │
       │              │
       └──────┬───────┘
              │
              ▼
       ┌─────────────┐
       │   Sales     │
       │  Invoice    │
       │ (Completed) │
       └─────────────┘
```

---

## Document Hierarchy

### 1. Quotation

- **Controller:** `erpnext.selling.doctype.quotation.quotation.Quotation`
- **Extends:** `SellingController` → `StockController` → `Document`
- **Purpose:** Initial customer quote with pricing and terms
- **Key Fields:**
  - `quotation_to`: Customer, Lead, Prospect, or CRM Deal
  - `valid_till`: Expiration date
  - `status`: Draft, Open, Partially Ordered, Ordered, Lost, Cancelled, Expired

### 2. Sales Order

- **Controller:** `erpnext.selling.doctype.sales_order.sales_order.SalesOrder`
- **Extends:** `SellingController` → `StockController` → `Document`
- **Purpose:** Confirmed order from customer
- **Key Fields:**
  - `delivery_date`: Expected delivery date
  - `per_delivered`: Percentage delivered
  - `per_billed`: Percentage billed
  - `status`: Draft, To Deliver and Bill, To Bill, To Deliver, Completed, Cancelled, Closed, On Hold

### 3. Delivery Note

- **Controller:** `erpnext.stock.doctype.delivery_note.delivery_note.DeliveryNote`
- **Extends:** `SellingController` → `StockController` → `Document`
- **Purpose:** Physical delivery of goods
- **Key Fields:**
  - `per_billed`: Percentage billed
  - `status`: Draft, To Bill, Completed, Return Issued, Cancelled, Closed

### 4. Sales Invoice

- **Controller:** `erpnext.accounts.doctype.sales_invoice.sales_invoice.SalesInvoice`
- **Extends:** `SellingController` → `StockController` → `Document`
- **Purpose:** Bill customer for goods/services
- **Key Fields:**
  - `update_stock`: Whether to update stock ledger
  - `is_return`: Whether this is a return invoice

---

## Quotation Flow

### Document Lifecycle

#### 1. Creation (Draft)

- **Status:** `Draft`
- **Validation:**
  - `validate()`: Sets status, validates UOM, validates valid_till date
  - `set_has_unit_price_items()`: Checks if any item has 0 qty
  - `set_customer_name()`: Sets customer name based on quotation_to

#### 2. Submission

- **Event:** `on_submit()`
- **Actions:**
  - Validates approving authority
  - Updates Opportunity status to "Quotation"
  - Updates Lead status
- **Status Change:** `Draft` → `Open`

#### 3. Status Management

- **Status Options:**
  - `Draft`: Initial state
  - `Open`: Submitted (docstatus = 1)
  - `Partially Ordered`: Some items converted to Sales Order
  - `Ordered`: All items converted to Sales Order
  - `Lost`: Declared as lost
  - `Cancelled`: Cancelled (docstatus = 2)
  - `Expired`: Validity period ended

#### 4. Status Calculation

```python
def get_ordered_status(self):
    ordered_items = get_ordered_items(self.name)
    # Returns: "Open", "Partially Ordered", or "Ordered"
```

### Document Creation Methods

#### make_sales_order()

**Location:** `erpnext.selling.doctype.quotation.quotation.make_sales_order()`

**Process:**

1. **Validation:**

   - Checks quotation validity period (if enabled in Selling Settings)
   - Throws error if quotation expired

2. **Customer Creation:**

   - If `quotation_to == "Customer"`: Uses existing customer
   - If `quotation_to == "Lead"`: Creates customer from lead (if not exists)
   - If `quotation_to == "Prospect"`: Creates customer from prospect (if not exists)

3. **Item Mapping:**

   - Maps Quotation Item → Sales Order Item
   - Calculates balance quantity: `qty - ordered_items.get(item.name, 0.0)`
   - Handles alternative items
   - Maps field: `parent` → `prevdoc_docname`, `name` → `quotation_item`

4. **Additional Mappings:**

   - Sales Taxes and Charges (reset_value: True)
   - Sales Team (add_if_empty: True)
   - Payment Schedule (add_if_empty: True)

5. **Post-Processing:**
   - Sets customer and customer_name
   - Copies sales team from customer
   - Sets sales partner and commission rate
   - Runs `set_missing_values()` and `calculate_taxes_and_totals()`

**Key Code:**

```python
def update_item(obj, target, source_parent):
    balance_qty = obj.qty - ordered_items.get(obj.name, 0.0)
    target.qty = balance_qty if balance_qty > 0 else 0
    target.stock_qty = flt(target.qty) * flt(obj.conversion_factor)
```

#### make_sales_invoice()

**Location:** `erpnext.selling.doctype.quotation.quotation.make_sales_invoice()`

**Process:**

- Similar to make_sales_order but creates Sales Invoice directly
- Maps all items (no balance qty calculation)
- Excludes alternative items

---

## Sales Order Flow

### Document Lifecycle

#### 1. Creation

- **Source:** Created from Quotation via `make_sales_order()`
- **Status:** `Draft`
- **Validation:**
  - `validate_delivery_date()`: Ensures delivery date is after transaction date
  - `validate_warehouse()`: Ensures warehouse for stock items
  - `validate_with_previous_doc()`: Validates against Quotation

#### 2. Submission

- **Event:** `on_submit()`
- **Actions:**
  - Checks credit limit
  - Updates reserved quantity (if stock reservation enabled)
  - Validates approving authority
  - Updates project
  - **Updates Quotation status** via `update_prevdoc_status("submit")`
  - Updates blanket order
  - Creates stock reservation entries (if enabled)

#### 3. Status Management

- **Status Options:**
  - `Draft`: Initial state
  - `To Deliver and Bill`: per_delivered < 100 and per_billed < 100
  - `To Bill`: (per_delivered >= 100 or skip_delivery_note) and per_billed < 100
  - `To Deliver`: per_delivered < 100 and per_billed >= 100
  - `Completed`: (per_delivered >= 100 or skip_delivery_note) and per_billed >= 100
  - `Cancelled`: docstatus = 2
  - `Closed`: status = 'Closed' and docstatus != 2
  - `On Hold`: status = 'On Hold'

#### 4. Status Calculation

```python
# Status is calculated based on:
- per_delivered: Percentage of items delivered
- per_billed: Percentage of items billed
- skip_delivery_note: Whether delivery note is skipped
- docstatus: Document status (0=Draft, 1=Submitted, 2=Cancelled)
```

### Document Creation Methods

#### make_delivery_note()

**Location:** `erpnext.selling.doctype.sales_order.sales_order.make_delivery_note()`

**Process:**

1. **Item Mapping:**

   - Maps Sales Order Item → Delivery Note Item
   - Calculates pending qty: `qty - delivered_qty`
   - Maps field: `name` → `so_detail`, `parent` → `against_sales_order`

2. **Quantity Calculation:**

   ```python
   target.qty = flt(source.qty) - flt(source.delivered_qty)
   target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
   ```

3. **Condition:**
   - Only maps items where: `abs(delivered_qty) < abs(qty)`
   - Excludes items with `delivered_by_supplier = 1`

#### make_sales_invoice()

**Location:** `erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice()`

**Process:**

1. **Item Mapping:**

   - Maps Sales Order Item → Sales Invoice Item
   - Calculates pending amount: `amount - billed_amt`
   - Maps field: `name` → `so_detail`, `parent` → `sales_order`

2. **Quantity Calculation:**

   ```python
   # For unit price items (qty = 0):
   target.qty = source.qty
   target.amount = pending_amount

   # For normal items:
   target.qty = source.qty - get_billed_qty(source.name)
   target.amount = flt(source.amount) - flt(source.billed_amt)
   ```

3. **Condition:**
   - Maps items where: `abs(billed_amt) < abs(amount)` or `base_amount == 0`

#### make_material_request()

**Location:** `erpnext.selling.doctype.sales_order.sales_order.make_material_request()`

**Process:**

- Creates Material Request for procurement
- Calculates remaining qty considering:
  - Already requested qty
  - Already delivered qty
  - Already received qty

---

## Delivery Note Flow

### Document Lifecycle

#### 1. Creation

- **Source:** Created from Sales Order via `make_delivery_note()`
- **Purpose:** Record physical delivery of goods
- **Stock Update:** Updates stock ledger (reduces stock)

#### 2. Submission

- **Event:** `on_submit()`
- **Actions:**
  - Updates stock ledger
  - Updates Sales Order `delivered_qty` via StatusUpdater
  - Updates Sales Order `per_delivered` percentage
  - Updates Sales Order status

#### 3. Status Management

- **Status Options:**
  - `Draft`: Initial state
  - `To Bill`: per_billed < 100
  - `Completed`: per_billed == 100
  - `Return Issued`: per_returned == 100
  - `Cancelled`: docstatus = 2
  - `Closed`: status = 'Closed'

### Quantity Tracking

**Delivery Note Item:**

- `qty`: Quantity delivered
- `so_detail`: Reference to Sales Order Item

**Sales Order Item (Updated):**

- `delivered_qty`: Sum of all Delivery Note Item qty where `so_detail = Sales Order Item.name`
- Updated via StatusUpdater mechanism

---

## Sales Invoice Flow

### Document Lifecycle

#### 1. Creation

- **Source:** Created from Sales Order or Quotation
- **Two Modes:**
  - **With Delivery Note:** `update_stock = 0` (standard flow)
  - **Without Delivery Note:** `update_stock = 1` (direct invoice)

#### 2. Submission

- **Event:** `on_submit()`
- **Actions:**
  - **If update_stock = 1:**
    - Updates stock ledger (reduces stock)
    - Updates Sales Order `delivered_qty` (via status_updater)
  - **Always:**
    - Updates Sales Order `billed_amt` (via status_updater)
    - Updates Delivery Note `billed_amt` (if linked)
    - Creates GL entries
    - Updates billing status

#### 3. Status Management

- Sales Invoice doesn't have complex status like Sales Order
- Status is simple: Draft, Submitted, Cancelled

### Amount Tracking

**Sales Invoice Item:**

- `amount`: Invoice amount
- `so_detail`: Reference to Sales Order Item
- `dn_detail`: Reference to Delivery Note Item (optional)

**Sales Order Item (Updated):**

- `billed_amt`: Sum of all Sales Invoice Item amount where `so_detail = Sales Order Item.name`
- Updated via StatusUpdater mechanism

**Delivery Note Item (Updated):**

- `billed_amt`: Sum of all Sales Invoice Item amount where `dn_detail = Delivery Note Item.name`
- Updated via `update_billed_amount_based_on_so()` function

---

## Status Management System

### StatusUpdater Class

**Location:** `erpnext.controllers.status_updater.StatusUpdater`

**Purpose:** Automatically tracks and updates quantities/amounts between related documents.

### How It Works

#### 1. Configuration (status_updater list)

Each document defines a `status_updater` list in its controller:

```python
# Example from Sales Invoice
self.status_updater = [
    {
        "source_dt": "Sales Invoice Item",
        "target_dt": "Sales Order Item",
        "target_parent_dt": "Sales Order",
        "target_parent_field": "per_billed",
        "target_field": "billed_amt",
        "target_ref_field": "amount",
        "source_field": "amount",
        "join_field": "so_detail",
        "percent_join_field": "sales_order",
        "status_field": "billing_status",
        "keyword": "Billed",
    }
]
```

#### 2. Update Process

**On Submit:**

```python
def on_submit(self):
    self.update_prevdoc_status()  # Calls StatusUpdater.update_prevdoc_status()
```

**Update Flow:**

1. `update_prevdoc_status()` → `update_qty()`
2. `update_qty()` → `_update_children()` (updates child table fields)
3. `_update_percent_field_in_targets()` (updates parent percentage fields)
4. `set_status()` (updates status based on percentages)

#### 3. Quantity/Amount Calculation

**For each target document:**

```sql
-- Sum all source document values
SELECT SUM(source_field)
FROM tabSource_DT
WHERE join_field = 'target_detail_id'
AND docstatus = 1

-- Update target field
UPDATE tabTarget_DT
SET target_field = calculated_sum
WHERE name = 'target_detail_id'
```

**Percentage Calculation:**

```sql
-- Calculate percentage
SELECT
    SUM(MIN(target_ref_field, target_field)) / SUM(target_ref_field) * 100
FROM tabTarget_DT
WHERE parent = 'target_parent_id'

-- Update parent percentage
UPDATE tabTarget_Parent_DT
SET target_parent_field = calculated_percentage
WHERE name = 'target_parent_id'
```

#### 4. Status Update

**Status is calculated based on percentages:**

```python
# Example: Sales Order status
if per_delivered < 100 and per_billed < 100:
    status = "To Deliver and Bill"
elif per_delivered >= 100 and per_billed < 100:
    status = "To Bill"
elif per_delivered < 100 and per_billed >= 100:
    status = "To Deliver"
elif per_delivered >= 100 and per_billed >= 100:
    status = "Completed"
```

---

## Quantity & Amount Tracking

### Sales Order Item Tracking

#### Delivered Quantity

- **Field:** `delivered_qty`
- **Updated From:**
  - Delivery Note Item (qty) where `so_detail = Sales Order Item.name`
  - Sales Invoice Item (qty) where `so_detail = Sales Order Item.name` AND `update_stock = 1`

#### Billed Amount

- **Field:** `billed_amt`
- **Updated From:**
  - Sales Invoice Item (amount) where `so_detail = Sales Order Item.name`

#### Percentage Fields

- **per_delivered:** `(sum(delivered_qty) / sum(qty)) * 100`
- **per_billed:** `(sum(billed_amt) / sum(amount)) * 100`

### Delivery Note Item Tracking

#### Billed Amount

- **Field:** `billed_amt`
- **Updated From:**
  - Sales Invoice Item (amount) where `dn_detail = Delivery Note Item.name`
  - Also considers Sales Invoice Items billed directly against Sales Order (FIFO distribution)

#### Percentage Fields

- **per_billed:** `(sum(billed_amt) / sum(amount)) * 100`

### Key Tracking Functions

#### get_ordered_items()

**Location:** `erpnext.selling.doctype.quotation.quotation.get_ordered_items()`

Returns dictionary of ordered quantities per Quotation Item:

```python
{
    "quotation_item_name": total_ordered_qty,
    ...
}
```

#### update_billed_amount_based_on_so()

**Location:** `erpnext.stock.doctype.delivery_note.delivery_note.update_billed_amount_based_on_so()`

Distributes billed amount from Sales Invoice to Delivery Notes using FIFO:

1. Gets billed amount directly against Sales Order
2. Gets all Delivery Notes against Sales Order Item
3. Distributes billed amount to Delivery Notes based on FIFO (posting_date, posting_time)

---

## Document Creation Methods

### Common Pattern: get_mapped_doc()

All document creation methods use Frappe's `get_mapped_doc()` function:

```python
from frappe.model.mapper import get_mapped_doc

doc = get_mapped_doc(
    source_doctype,      # "Quotation"
    source_name,         # Quotation name
    mapper_dict,         # Field mappings
    target_doc,          # Existing doc (optional)
    set_missing_values,  # Function to set additional values
    ignore_permissions   # Boolean
)
```

### Mapper Dictionary Structure

```python
{
    "Source DocType": {
        "doctype": "Target DocType",
        "validation": {"docstatus": ["=", 1]},  # Only from submitted docs
        "field_map": {
            "source_field": "target_field"
        },
        "field_no_map": ["field1", "field2"],  # Fields to exclude
    },
    "Source Child Table": {
        "doctype": "Target Child Table",
        "field_map": {
            "source_field": "target_field",
            "parent": "prevdoc_docname",  # Link to source document
        },
        "condition": lambda doc: condition_check(doc),  # Filter rows
        "postprocess": update_item,  # Function to modify mapped item
    }
}
```

### Key Mapping Functions

#### set_missing_values(source, target)

- Sets default values
- Copies related data (customer, sales team, etc.)
- Runs `calculate_taxes_and_totals()`

#### update_item(obj, target, source_parent)

- Calculates balance quantities
- Sets warehouse, cost center
- Adjusts rates if needed

#### condition(doc)

- Filters which rows to map
- Example: Only map items with `qty > delivered_qty`

---

## Key Business Rules

### 1. Quotation Validity

- **Rule:** Quotation must be valid (valid_till >= transaction_date and >= today)
- **Exception:** Can be bypassed if "Allow Sales Order Creation for Expired Quotation" is enabled
- **Location:** `quotation.py:make_sales_order()`

### 2. Balance Quantity Calculation

- **Rule:** When creating Sales Order from Quotation, only map items with remaining qty
- **Formula:** `balance_qty = quotation_item.qty - sum(sales_order_item.qty where quotation_item = quotation_item.name)`
- **Location:** `quotation.py:_make_sales_order()`

### 3. Alternative Items

- **Rule:** Alternative items are mutually exclusive
- **Behavior:** Only selected alternative items are mapped to Sales Order
- **Location:** `quotation.py:_make_sales_order()` - `can_map_row()` function

### 4. Over-Delivery Allowance

- **Rule:** Delivery quantity cannot exceed ordered quantity beyond allowance
- **Allowance:** Set in Stock Settings or Item master
- **Validation:** `status_updater.py:validate_qty()`

### 5. Over-Billing Allowance

- **Rule:** Billed amount cannot exceed ordered amount beyond allowance
- **Allowance:** Set in Accounts Settings or Item master
- **Validation:** `status_updater.py:validate_qty()`

### 6. Credit Limit Check

- **Rule:** Sales Order submission checks customer credit limit
- **Exception:** Can be bypassed if `bypass_credit_limit_check` is set in Customer Credit Limit
- **Location:** `sales_order.py:check_credit_limit()`

### 7. Warehouse Validation

- **Rule:** Stock items must have warehouse (unless delivered_by_supplier)
- **Exception:** Unit price items (qty = 0) don't require warehouse
- **Location:** `sales_order.py:validate_warehouse()`

### 8. Delivery Date Validation

- **Rule:** Delivery date must be after Sales Order date
- **Exception:** Not required if `skip_delivery_note = 1`
- **Location:** `sales_order.py:validate_delivery_date()`

### 9. Status Update on Cancel

- **Rule:** When Sales Order is cancelled, Quotation status is updated
- **Action:** `update_prevdoc_status("cancel")` sets Quotation status back to "Quotation"
- **Location:** `sales_order.py:on_cancel()`

### 10. Stock Reservation

- **Rule:** If stock reservation enabled, Sales Order can reserve stock
- **Behavior:** Creates Stock Reservation Entry on submit
- **Location:** `sales_order.py:on_submit()` - `create_stock_reservation_entries()`

---

## Document Event Flow

### Quotation Events

#### on_submit()

1. Validate approving authority
2. Update Opportunity status → "Quotation"
3. Update Lead status

#### on_cancel()

1. Clear lost reasons
2. Call super().on_cancel()
3. Update status
4. Update Opportunity status → "Open"
5. Update Lead status

### Sales Order Events

#### on_submit()

1. Check credit limit
2. Update reserved quantity
3. Validate approving authority
4. Update project
5. **Update Quotation status** → "Partially Ordered" or "Ordered"
6. Update Opportunity status → "Converted"
7. Update blanket order
8. Create stock reservation entries (if enabled)

#### on_cancel()

1. Check if closed (cannot cancel closed SO)
2. Check next document status (cannot cancel if linked invoices exist)
3. Update reserved quantity
4. Update project
5. **Update Quotation status** → "Quotation"
6. Update blanket order
7. Cancel stock reservation entries

### Sales Invoice Events

#### on_submit()

1. Validate POS paid amount
2. Validate approving authority
3. Check previous document status
4. **Update Sales Order:**
   - Update `billed_amt` in Sales Order Item
   - Update `per_billed` in Sales Order
   - Update `billing_status` in Sales Order
5. **Update Delivery Note:**
   - Update `billed_amt` in Delivery Note Item
   - Update `per_billed` in Delivery Note
6. **If update_stock = 1:**
   - Update `delivered_qty` in Sales Order Item
   - Update `per_delivered` in Sales Order
7. Update stock ledger (if update_stock = 1)
8. Create GL entries
9. Check credit limit
10. Update against document in Journal Entry
11. Update time sheet
12. Update company current month sales
13. Update project

---

## Reference Fields & Linking

### Quotation → Sales Order

**Quotation Item:**

- `name`: Row identifier

**Sales Order Item:**

- `prevdoc_docname`: Quotation name
- `quotation_item`: Quotation Item name (row identifier)

### Sales Order → Delivery Note

**Sales Order Item:**

- `name`: Row identifier

**Delivery Note Item:**

- `so_detail`: Sales Order Item name (row identifier)
- `against_sales_order`: Sales Order name

### Sales Order → Sales Invoice

**Sales Order Item:**

- `name`: Row identifier

**Sales Invoice Item:**

- `so_detail`: Sales Order Item name (row identifier)
- `sales_order`: Sales Order name

### Delivery Note → Sales Invoice

**Delivery Note Item:**

- `name`: Row identifier

**Sales Invoice Item:**

- `dn_detail`: Delivery Note Item name (row identifier)
- `delivery_note`: Delivery Note name

---

## Status Calculation Logic

### Quotation Status

```python
def set_status(self):
    if self.docstatus == 0:
        status = "Draft"
    elif self.docstatus == 2:
        status = "Cancelled"
    elif self.status == "Lost":
        status = "Lost"
    elif self.valid_till and self.valid_till < nowdate():
        status = "Expired"
    else:
        status = self.get_ordered_status()  # "Open", "Partially Ordered", "Ordered"
```

### Sales Order Status

```python
def set_status(self):
    if self.docstatus == 0:
        status = "Draft"
    elif self.docstatus == 2:
        status = "Cancelled"
    elif self.status == "Closed":
        status = "Closed"
    elif self.status == "On Hold":
        status = "On Hold"
    elif self.per_delivered < 100 and self.per_billed < 100:
        status = "To Deliver and Bill"
    elif (self.per_delivered >= 100 or self.skip_delivery_note) and self.per_billed < 100:
        status = "To Bill"
    elif self.per_delivered < 100 and self.per_billed >= 100 and not self.skip_delivery_note:
        status = "To Deliver"
    elif (self.per_delivered >= 100 or self.skip_delivery_note) and self.per_billed >= 100:
        status = "Completed"
```

---

## Key Controller Methods

### SellingController (Base Class)

**Location:** `erpnext.controllers.selling_controller.SellingController`

**Key Methods:**

- `validate()`: Validates items, selling price, UOM
- `set_missing_values()`: Sets customer details, price list, item details
- `calculate_taxes_and_totals()`: Calculates taxes and totals
- `update_stock_ledger()`: Updates stock ledger (if applicable)
- `set_incoming_rate()`: Sets incoming rate for stock valuation

### StatusUpdater (Mixin)

**Location:** `erpnext.controllers.status_updater.StatusUpdater`

**Key Methods:**

- `update_prevdoc_status()`: Main entry point
- `update_qty()`: Updates quantities/amounts in target documents
- `validate_qty()`: Validates over-delivery/over-billing
- `set_status()`: Updates status based on percentages

---

## File Structure Reference

### Quotation

- **Controller:** `erpnext/selling/doctype/quotation/quotation.py`
- **JSON:** `erpnext/selling/doctype/quotation/quotation.json`
- **JS:** `erpnext/selling/doctype/quotation/quotation.js`

### Sales Order

- **Controller:** `erpnext/selling/doctype/sales_order/sales_order.py`
- **JSON:** `erpnext/selling/doctype/sales_order/sales_order.json`
- **JS:** `erpnext/selling/doctype/sales_order/sales_order.js`

### Delivery Note

- **Controller:** `erpnext/stock/doctype/delivery_note/delivery_note.py`
- **JSON:** `erpnext/stock/doctype/delivery_note/delivery_note.json`
- **JS:** `erpnext/stock/doctype/delivery_note/delivery_note.js`

### Sales Invoice

- **Controller:** `erpnext/accounts/doctype/sales_invoice/sales_invoice.py`
- **JSON:** `erpnext/accounts/doctype/sales_invoice/sales_invoice.json`
- **JS:** `erpnext/accounts/doctype/sales_invoice/sales_invoice.js`

### Base Controllers

- **SellingController:** `erpnext/controllers/selling_controller.py`
- **StatusUpdater:** `erpnext/controllers/status_updater.py`

---

## Summary

The original ERPNext sales cycle follows a strict hierarchical flow:

1. **Quotation** → Customer quote with pricing
2. **Sales Order** → Confirmed order (tracks delivery and billing)
3. **Delivery Note** → Physical delivery (updates delivered_qty)
4. **Sales Invoice** → Customer billing (updates billed_amt)

**Key Mechanisms:**

- **StatusUpdater:** Automatically tracks and updates quantities/amounts
- **get_mapped_doc():** Standard method for document creation
- **Status Calculation:** Based on percentages (per_delivered, per_billed)
- **Reference Fields:** Maintain links between documents via row identifiers

**Important Points:**

- All document creation requires source document to be submitted (docstatus = 1)
- Quantities are tracked at item level, percentages at document level
- Status is automatically calculated based on delivery and billing percentages
- Over-delivery and over-billing are validated with configurable allowances

---

_This analysis is based on the actual ERPNext codebase as of the analysis date. The flow may vary slightly in different ERPNext versions._
