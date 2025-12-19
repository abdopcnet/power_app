# Power App - Detailed Functionality

## Table of Contents

1. [Quotation Expense Management](#quotation-expense-management)
2. [Service Expense Management](#service-expense-management)
3. [Item Rate Calculations](#item-rate-calculations)
4. [Material Request Integration](#material-request-integration)
5. [Supplier Quotation Sync](#supplier-quotation-sync)
6. [Item Information Display](#item-information-display)
7. [Sales Order Creation](#sales-order-creation)

---

## Quotation Expense Management

### Purpose

Allows users to add additional expenses to quotations that are then automatically distributed across quotation items, ensuring accurate pricing.

### How It Works

1. **Adding Expenses**

    - User adds rows to `custom_quotation_expenses` table
    - Each row contains:
        - `expenses_item`: Description (e.g., "Shipping", "Installation")
        - `amount`: Expense amount in quotation currency

2. **Expense Distribution Algorithm**

    ```
    For each item:
      - Calculate item's share = (Item amount / Total items amount) × Total expenses
      - Add share to item rate: New rate = Original rate + (Share / Item qty)
    ```

3. **Implementation Details**

    - Triggered on `on_update` event
    - Function: `quotation_update()` in `customization.py`
    - Preserves original Supplier Quotation rates in custom fields:
        - `custom_sq_rate`, `custom_sq_net_rate`
        - `custom_sq_amount`, `custom_sq_net_amount`
    - Calculates both gross and net rates/amounts

4. **Margin Application**
    - After expense allocation, if `custom_item_margin` is set:
        ```
        Final rate = Rate + (Rate × Margin / 100)
        ```
    - Applied to all items uniformly

### Example

**Initial State:**

-   Item A: Qty 10, Rate 100, Amount 1000
-   Item B: Qty 5, Rate 200, Amount 1000
-   Total Items Amount: 2000
-   Expenses: 200

**After Expense Distribution:**

-   Item A share: (1000/2000) × 200 = 100
    -   New rate: 100 + (100/10) = 110
    -   New amount: 110 × 10 = 1100
-   Item B share: (1000/2000) × 200 = 100
    -   New rate: 200 + (100/5) = 220
    -   New amount: 220 × 5 = 1100

**With 10% Margin:**

-   Item A: 110 × 1.10 = 121
-   Item B: 220 × 1.10 = 242

---

## Service Expense Management

### Purpose

Tracks service-related expenses on Sales Orders and automatically creates Journal Entries for accounting when the Sales Order is submitted.

### How It Works

1. **Adding Service Expenses**

    - User adds rows to `custom_service_expense` table on Sales Order
    - Each row contains:
        - `service_expense_type`: Links to Service Expense Type master
        - `compnay`: Auto-fetched from Service Expense Type
        - `default_account`: Auto-fetched from Service Expense Type
        - `amount`: Expense amount

2. **Journal Entry Creation (on_submit)**
    - Triggered when Sales Order is submitted
    - Function: `create_je_from_service_expence()` in `customization.py`
3. **Journal Entry Structure**

    ```
    Debit Entries (one per unique expense account):
      - Account: Expense account from Service Expense Type
      - Amount: Sum of all expenses for that account
      - Cost Center: From Sales Order

    Credit Entry (one):
      - Account: Company's custom_default_service_expense
      - Amount: Total of all expenses
    ```

4. **Grouping Logic**
    - Expenses are grouped by `default_account`
    - Multiple expenses with same account are summed
    - One debit entry per unique account

### Example

**Sales Order with Service Expenses:**

-   Expense 1: Type "Installation", Account "Installation Expenses", Amount 500
-   Expense 2: Type "Delivery", Account "Delivery Expenses", Amount 300
-   Expense 3: Type "Setup", Account "Installation Expenses", Amount 200
-   Company Default Service Expense Account: "Service Revenue"

**Journal Entry Created:**

```
Debit: Installation Expenses    700 (500 + 200)
Debit: Delivery Expenses         300
Credit: Service Revenue         1000
```

---

## Item Rate Calculations

### Rate Calculation Flow

1. **Initial Rates**

    - When items are added, rates come from:
        - Item Price List
        - Manual entry
        - Supplier Quotation (if copied)

2. **Supplier Quotation Rate Preservation**

    - When items are copied from Supplier Quotation:
        - Original rates stored in: `custom_sq_rate`, `custom_sq_net_rate`
        - Original amounts stored in: `custom_sq_amount`, `custom_sq_net_amount`
    - These are used as base for expense calculations

3. **Expense Allocation**

    - Uses preserved Supplier Quotation amounts if available
    - Otherwise uses current item amounts
    - Formula:
        ```
        Item rate = SQ_rate + (SQ_amount / Total SQ_amount × Total expenses) / Qty
        ```

4. **Margin Application**
    - Applied after expense allocation
    - Formula:
        ```
        Final rate = Rate × (1 + Margin/100)
        ```

### Rate Fields

-   `rate`: Gross rate (before tax)
-   `net_rate`: Net rate (after tax)
-   `amount`: Gross amount (rate × qty)
-   `net_amount`: Net amount (net_rate × qty)

All fields are recalculated when expenses or margin change.

---

## Material Request Integration

### Purpose

Enables creating Material Requests directly from Quotations, maintaining a reference link for traceability.

### Workflow

1. **Creation Process**

    - User submits Quotation
    - Clicks "Create > Material Request" button
    - Function: `make_material_request_from_quotation()` in `mapper.py`

2. **Mapping Details**

    ```
    Quotation → Material Request
      - Items mapped (item_code, qty)
      - Company copied
      - Material Request Type: "Purchase"
      - custom_create_from_dc: "Material Request"
      - custom_dc_refrance: Quotation name
    ```

3. **Validation**

    - Only submitted Quotations (docstatus = 1) can create Material Request

4. **Usage**
    - Material Request can be used to:
        - Create Supplier Quotation
        - Track procurement requirements
        - Link back to original Customer Quotation

### Reference Chain

```
Customer Quotation
  ↓ (creates)
Material Request (custom_dc_refrance = Quotation name)
  ↓ (creates)
Supplier Quotation (linked via Material Request)
  ↓ (updates back)
Customer Quotation (items updated with supplier rates)
```

---

## Supplier Quotation Sync

### Purpose

Allows updating Customer Quotation items and rates from Supplier Quotation, maintaining rate consistency.

### Workflow

1. **Link Detection**

    - Function: `check_quotation_linked()` in `customization.py`
    - Checks Supplier Quotation items for Material Request reference
    - Follows Material Request to find `custom_dc_refrance` (Quotation name)

2. **Update Process**

    - Function: `update_quotation_linked()` in `customization.py`
    - Steps:
        1. Set Customer Quotation to draft (docstatus = 0)
        2. Clear all existing items
        3. Copy items from Supplier Quotation
        4. Map fields: item_code, qty, uom, rate, amount, etc.
        5. Use `base_rate` to avoid currency conversion issues
        6. Recalculate totals
        7. Add comment to timeline
        8. Save quotation

3. **Rate Handling**

    - Uses `base_rate` from Supplier Quotation Item
    - Ensures rates are in company's base currency
    - Avoids currency conversion discrepancies

4. **User Interface**
    - "Update Quotation" button appears on Supplier Quotation form
    - Only visible when:
        - Supplier Quotation is submitted
        - Linked Quotation is found
    - Clicking button updates Quotation and navigates to it

### Field Mapping

```
Supplier Quotation Item → Quotation Item
  - item_code
  - qty
  - uom
  - base_rate → rate
  - amount
  - description
  - brand
  - stock_uom
```

---

## Item Information Display

### Purpose

Provides quick access to item pricing and stock information directly from the Quotation form.

### Features

1. **"Show Item History" Button**

    - Appears on Quotation form when items exist
    - Only visible for existing (non-new) quotations

2. **Information Retrieved**

    - **Stock Quantity**: From Bin table (actual_qty)
        - Latest modified Bin record
    - **Last Selling Rate**: From Sales Invoice Item
        - Latest submitted Sales Invoice
    - **Last Purchase Rate**: From Purchase Invoice Item
        - Latest submitted Purchase Invoice
    - **Last Supplier**: From Purchase Invoice
        - Supplier name from the Purchase Invoice

3. **Display Format**

    - Dialog box with HTML table
    - Columns:
        - Item Code (linked to Item form)
        - Qty in Warehouse
        - Last Selling Rate (formatted as currency)
        - Last Purchase Rate (formatted as currency)
        - Last Purchase Supplier

4. **Implementation**
    - Function: `get_item_details()` in `customization.py`
    - Called via `frappe.call()` from JavaScript
    - Fetches data for all unique items in quotation
    - Displays in formatted table

### Data Sources

-   **Stock**: `Bin` table, filtered by item_code, ordered by modified desc
-   **Selling Rate**: `Sales Invoice Item`, docstatus=1, ordered by creation desc
-   **Purchase Rate**: `Purchase Invoice Item`, docstatus=1, ordered by creation desc
-   **Supplier**: `Purchase Invoice` parent document

---

## Sales Order Creation

### Purpose

Customizes the standard Sales Order creation from Quotation to include service expenses and handle alternative items.

### Customizations

1. **Service Expenses Mapping**

    - Service expenses from Quotation are copied to Sales Order
    - Table: `custom_service_expense`
    - Included in document mapping

2. **Alternative Items Handling**

    - Checks for alternative items
    - Only maps selected items if alternatives exist
    - Calculates balance quantity (qty - already ordered qty)

3. **Customer Creation**

    - If Quotation is to Lead or Prospect:
        - Checks if Customer already exists
        - Creates Customer if needed
        - Links to Sales Order

4. **Override Details**
    - Function: `make_sales_order()` in `overried.py`
    - Overrides: `erpnext.selling.doctype.quotation.quotation.make_sales_order`
    - Maintains standard ERPNext functionality
    - Adds service expense support

### Mapping Structure

```
Quotation → Sales Order
  - Standard fields (customer, company, etc.)
  - Items (with balance qty calculation)
  - Taxes and Charges
  - Sales Team
  - Payment Schedule
  - Service Expense (custom table)
```

---

## Technical Implementation Notes

### Document Events

1. **Quotation.on_update**

    - Triggers: `quotation_update()`
    - Recalculates item rates with expenses and margin
    - Commits database changes

2. **Sales Order.on_submit**
    - Triggers: `create_je_from_service_expence()`
    - Creates and submits Journal Entry
    - Groups expenses by account

### Method Overrides

1. **make_sales_order()**
    - Overrides standard ERPNext method
    - Adds service expense mapping
    - Handles customer creation

### JavaScript Enhancements

1. **Quotation Form**

    - Item query filtering
    - Item history display
    - Material Request creation button

2. **Supplier Quotation Form**
    - Linked Quotation detection
    - Update Quotation button

### Database Queries

-   Uses `frappe.db.get_all()` for efficient queries
-   Orders by creation/modified desc for latest records
-   Filters by docstatus for submitted documents
-   Groups expenses using `defaultdict` for efficiency

---

_End of Functionality Details_
