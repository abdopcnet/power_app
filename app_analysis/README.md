# Power App - Application Analysis

## Overview

**Power App** is a custom Frappe/ERPNext application designed for Power Key Company. It provides extensive customizations to the standard ERPNext workflow, particularly focusing on quotation management, expense tracking, and service-related operations.

**Publisher:** Hadeel Milad
**Version:** 0.0.1
**License:** MIT

---

## Table of Contents

1. [Core Functionality](#core-functionality)
2. [Key Features](#key-features)
3. [Custom Doctypes](#custom-doctypes)
4. [Standard Doctype Customizations](#standard-doctype-customizations)
5. [Workflow & Business Logic](#workflow--business-logic)
6. [Technical Architecture](#technical-architecture)
7. [File Structure](#file-structure)

---

## Core Functionality

The Power App extends ERPNext's standard quotation and sales order processes with:

1. **Expense Management**: Track and allocate expenses to quotation items
2. **Service Quotations**: Special handling for service-based quotations
3. **Material Request Integration**: Create Material Requests directly from Quotations
4. **Supplier Quotation Sync**: Update Customer Quotations from Supplier Quotations
5. **Automatic Journal Entry Creation**: Generate Journal Entries for service expenses on Sales Order submission
6. **Item History & Pricing**: Display item stock, last selling rate, and purchase rate information

---

## Key Features

### 1. Quotation Expense Allocation

-   Add expenses to quotations via a child table
-   Automatically distribute expenses proportionally across quotation items
-   Apply item margin percentage to adjust rates
-   Expenses are allocated based on item amounts (gross and net)

### 2. Service Expense Management

-   Track service expenses on Sales Orders
-   Automatically create Journal Entries when Sales Orders are submitted
-   Group expenses by account for efficient accounting
-   Uses company-level default service expense account

### 3. Material Request Creation

-   Create Material Requests directly from submitted Quotations
-   Maintains reference link between Quotation and Material Request
-   Automatically sets Material Request Type to "Purchase"

### 4. Supplier Quotation Integration

-   Link Supplier Quotations to Customer Quotations via Material Requests
-   Update Customer Quotation items from Supplier Quotation
-   Maintains rate consistency (uses base_rate to avoid currency conversion issues)

### 5. Item Information Display

-   "Show Item History" button on Quotation form
-   Displays:
    -   Current stock quantity (from Bin)
    -   Last selling rate (from Sales Invoice)
    -   Last purchase rate (from Purchase Invoice)
    -   Last supplier name

### 6. Service Items Filtering

-   When "Services" checkbox is enabled on Quotation:
    -   Filters items to show only non-stock items (`is_stock_item: 0`)
    -   Shows only sales items (`is_sales_item: 1`)
    -   Excludes items with variants (`has_variants: 0`)

---

## Custom Doctypes

### 1. Service Expense

**Location:** `power_app/doctype/service_expense/`

A child table doctype used to track service-related expenses on Sales Orders.

**Fields:**

-   `service_expense_type` (Link to Service Expense Type) - Required
-   `compnay` (Link to Company) - Auto-fetched, Read-only
-   `default_account` (Link to Account) - Auto-fetched, Read-only
-   `amount` (Currency) - Required, Non-negative

**Usage:**

-   Added to Sales Orders as `custom_service_expense` table
-   Used to create Journal Entries automatically on Sales Order submission

### 2. Service Expense Type

**Location:** `power_app/doctype/service_expense_type/`

Master doctype for defining types of service expenses.

**Purpose:**

-   Defines expense categories
-   Links to default accounting accounts
-   Company-specific configuration

### 3. Quotation Expenses

**Location:** `power_app/doctype/quotation_expenses/`

A child table doctype for tracking expenses on Quotations.

**Fields:**

-   `expenses_item` (Data) - Description of the expense
-   `amount` (Currency) - Required, Non-negative

**Usage:**

-   Added to Quotations as `custom_quotation_expenses` table
-   Expenses are proportionally distributed to quotation items

### 4. Service Line

**Location:** `power_app/doctype/service_line/`

(Details to be confirmed - file exists but content not fully analyzed)

---

## Standard Doctype Customizations

### 1. Quotation

**Custom Fields Added:**

-   `custom_customer_qoutation_number` (Data) - Customer's quotation reference number
-   `custom_quotation_expenses` (Table: Quotation Expenses) - Expense tracking
-   `custom_item_margin` (Float) - Percentage margin to apply to items
-   `custom_services` (Check) - Flag to indicate service quotation

**Property Setters:**

-   Hidden/print settings for `base_rounded_total`, `rounded_total`, `in_words`
-   Field ordering customizations

**Document Events:**

-   `on_update`: Calls `quotation_update()` to recalculate item rates with expenses and margins

**JavaScript Enhancements:**

-   "Show Item History" button
-   "Create Material Request" button (for submitted quotations)
-   Dynamic item query filtering based on `custom_services` flag

### 2. Sales Order

**Custom Fields Added:**

-   `custom_service_expense` (Table: Service Expense) - Service expense tracking

**Document Events:**

-   `on_submit`: Calls `create_je_from_service_expence()` to automatically create Journal Entry

**Override:**

-   `make_sales_order()` method overridden to include service expenses in mapping

### 3. Material Request

**Custom Fields Added:**

-   `custom_create_from_dc` (Data) - Indicates source document type
-   `custom_dc_refrance` (Data) - Reference to source Quotation

**Usage:**

-   Set automatically when creating Material Request from Quotation
-   Used to link back to original Quotation

### 4. Company

**Custom Fields Added:**

-   `custom_default_service_expense` (Link to Account) - Default account for service expenses

**Usage:**

-   Used as credit account when creating Journal Entries for service expenses

### 5. Quotation Item

**Custom Fields (inferred from code):**

-   `custom_sq_rate` - Stores Supplier Quotation rate
-   `custom_sq_net_rate` - Stores Supplier Quotation net rate
-   `custom_sq_amount` - Stores Supplier Quotation amount
-   `custom_sq_net_amount` - Stores Supplier Quotation net amount

**Purpose:**

-   Preserves original Supplier Quotation rates when expenses are added
-   Used in expense allocation calculations

---

## Workflow & Business Logic

### Quotation Workflow

1. **Create Quotation**

    - User can add items (products or services based on `custom_services` flag)
    - User can add expenses in `custom_quotation_expenses` table
    - User can set `custom_item_margin` percentage

2. **Update Quotation (on_update event)**

    - If expenses exist, they are proportionally distributed to items:
        - Each item's rate = Original rate + (Item amount / Total items amount × Total expenses) / Item qty
    - If margin is set, it's applied to all items:
        - New rate = Rate + (Rate × Margin / 100)
    - Original Supplier Quotation rates are preserved in custom fields

3. **Submit Quotation**

    - User can create Material Request (if needed)
    - User can create Sales Order

4. **Create Sales Order from Quotation**
    - Standard ERPNext flow with customizations:
        - Service expenses are copied to Sales Order
        - Alternative items handling
        - Balance quantity calculation

### Sales Order Workflow

1. **Submit Sales Order**
    - If `custom_service_expense` table has entries:
        - Expenses are grouped by account
        - Journal Entry is created with:
            - Debit entries: One per expense account (grouped amounts)
            - Credit entry: Company's default service expense account
        - Journal Entry is automatically submitted

### Supplier Quotation to Customer Quotation Workflow

1. **Supplier Quotation Submitted**

    - System checks if linked to Material Request
    - Material Request checked for `custom_dc_refrance` (Quotation reference)

2. **Update Customer Quotation**
    - "Update Quotation" button appears on Supplier Quotation form
    - When clicked:
        - Customer Quotation is set to draft (docstatus = 0)
        - All existing items are cleared
        - Items from Supplier Quotation are copied
        - Rates use `base_rate` to avoid currency conversion issues
        - Quotation totals are recalculated
        - User is redirected to updated Quotation

### Material Request Creation

1. **From Quotation**
    - User clicks "Create > Material Request" on submitted Quotation
    - Material Request is created with:
        - Type: "Purchase"
        - Items from Quotation
        - `custom_create_from_dc`: "Material Request"
        - `custom_dc_refrance`: Quotation name
    - Material Request can be used to create Supplier Quotation

---

## Technical Architecture

### Python Modules

#### `customization.py`

Main business logic module containing:

-   `get_item_details(item_code)`: Returns stock qty, last selling/purchase rates, supplier
-   `quotation_update(doc, method)`: Handles expense allocation and margin application
-   `create_je_from_service_expence(doc, method)`: Creates Journal Entry for service expenses
-   `check_quotation_linked(doc)`: Finds linked Quotation from Supplier Quotation
-   `update_quotation_linked(doc, q)`: Updates Quotation with Supplier Quotation items

#### `mapper.py`

Document mapping utilities:

-   `make_material_request_from_quotation(source, target)`: Maps Quotation to Material Request

#### `overried.py`

Standard method overrides:

-   `make_sales_order(source_name, target_doc)`: Overrides ERPNext's standard method
    -   Includes service expenses in Sales Order creation
    -   Handles customer creation from Lead/Prospect
    -   Manages alternative items and balance quantities

### JavaScript Files

#### `public/js/quotation.js`

Client-side enhancements for Quotation:

-   Item query filtering (service vs. product items)
-   "Show Item History" button and dialog
-   "Create Material Request" button
-   Item details fetching and display

#### `public/js/supplier_quotation.js`

Client-side enhancements for Supplier Quotation:

-   "Update Quotation" button
-   Linked Quotation detection
-   Quotation update workflow

### Hooks Configuration

**File:** `hooks.py`

Key configurations:

-   `doctype_js`: Links JavaScript files to doctypes
-   `doc_events`: Document event handlers
-   `override_whitelisted_methods`: Method overrides

---

## File Structure

```
power_app/
├── power_app/
│   ├── __init__.py
│   ├── hooks.py                    # App configuration and hooks
│   ├── customization.py            # Main business logic
│   ├── mapper.py                   # Document mapping utilities
│   ├── overried.py                 # Method overrides
│   ├── power_app/
│   │   ├── doctype/
│   │   │   ├── service_expense/
│   │   │   ├── service_expense_type/
│   │   │   ├── quotation_expenses/
│   │   │   └── service_line/
│   │   └── custom/                 # Custom field definitions
│   │       ├── quotation.json
│   │       ├── sales_order.json (implied)
│   │       ├── material_request.json
│   │       ├── company.json
│   │       └── ...
│   └── public/
│       └── js/
│           ├── quotation.js
│           └── supplier_quotation.js
└── app_analysis/                   # This analysis directory
```

---

## Dependencies

-   **ERPNext**: Core dependency (Selling, Buying, Stock modules)
-   **Frappe Framework**: Base framework
-   **Python 3.10+**: Runtime requirement

---

## Usage Examples

### Adding Expenses to Quotation

1. Open a Quotation
2. Add items as usual
3. Scroll to "Quotation Expenses" section
4. Add expense rows with description and amount
5. Optionally set "Item Margin" percentage
6. Save the Quotation
7. System automatically recalculates item rates

### Creating Material Request from Quotation

1. Submit a Quotation
2. Click "Create > Material Request"
3. Material Request is created with items from Quotation
4. Material Request references the Quotation in `custom_dc_refrance`

### Updating Quotation from Supplier Quotation

1. Create Material Request from Customer Quotation
2. Create Supplier Quotation from Material Request
3. Submit Supplier Quotation
4. "Update Quotation" button appears
5. Click button to update Customer Quotation with Supplier Quotation rates

### Service Expense Journal Entry

1. Create Sales Order with service expenses in `custom_service_expense` table
2. Submit Sales Order
3. Journal Entry is automatically created and submitted
4. Debits: Expense accounts (grouped)
5. Credit: Company's default service expense account

---

## Notes & Considerations

1. **Expense Allocation**: Expenses are distributed proportionally based on item amounts. This may not suit all business scenarios.

2. **Margin Application**: Margin is applied after expense allocation. Order matters: expenses first, then margin.

3. **Currency Handling**: Supplier Quotation to Customer Quotation update uses `base_rate` to avoid currency conversion issues.

4. **Journal Entry Automation**: Service expense Journal Entries are automatically submitted. Ensure proper account setup in Company master.

5. **Material Request Link**: The link between Quotation and Material Request is one-way (Quotation → Material Request). Reverse lookup requires checking Material Request's `custom_dc_refrance`.

6. **Service Items**: When `custom_services` is enabled, only non-stock, sales items without variants are shown in item selection.

---

## Future Enhancements (Potential)

Based on code analysis, potential improvements:

1. Bidirectional linking between Quotation and Material Request
2. Expense allocation methods (proportional, fixed, manual)
3. Margin calculation options (per item, per category)
4. Service expense approval workflow
5. Enhanced item history with multiple warehouses
6. Supplier Quotation comparison view

---

## Support & Contact

**Publisher:** Hadeel Milad
**Email:** hadeelnr88@gmail.com
**License:** MIT

---

_This analysis was generated on: 2025-01-XX_
_App Version: 0.0.1_
