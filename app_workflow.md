# Power App - Complete Workflow Documentation

## Overview

Power App extends ERPNext's standard sales cycle to support intermediary service companies with expense allocation and supplier quotation management.

## Complete Workflow

### Phase 1: Quotation Creation (Draft)

1. **Create Customer Quotation (Draft)**

    - Add customer, company, and basic information
    - Items can be added manually or from supplier quotations

2. **Create Material Request**

    - Click "Material Request" button (standalone, info color)
    - Material Request is created and linked to Quotation
    - Material Request status: Draft

3. **Create Request for Quotation (RFQ)**

    - From Material Request, create RFQ
    - Send RFQ to multiple suppliers

4. **Receive Supplier Quotations**
    - Suppliers submit Supplier Quotations
    - Each Supplier Quotation is linked to Material Request
    - Supplier Quotations status: Submitted

### Phase 2: Item Selection (Draft Quotation)

5. **Compare Supplier Quotations**

    - Click "Compare Supplier Quotations" button (standalone, warning/orange color)
    - Opens Supplier Quotation Comparison report
    - Pre-filtered by Material Request/RFQ if available
    - If multiple Material Requests exist, selection dialog appears

6. **Select Items from Supplier Quotations**
    - Click "Select Items from Supplier Quotations" button (standalone, success/green color)
    - Dialog shows all items from linked Supplier Quotations
    - Select items using checkboxes
    - Click "Add Selected Items"
    - **Logic:** `rate` is updated with supplier rate from selected items
    - Items are added/updated in Customer Quotation with:
        - `custom_supplier_quotation` - Supplier Quotation reference
        - `rate` - Updated with supplier rate from selected items

### Phase 3: Expense Allocation (Draft Quotation)

7. **Add Expenses**

    - In Quotation Expenses Table (after Items table)
    - Add expense rows:
        - Service Expense Type (Link)
        - Amount (Currency)
        - Company and Default Account (auto-fetched)

8. **Expense Distribution**
    - On save (validate event):
        1. First, restore original rates:
            - If `custom_supplier_quotation` exists: Get rate from Supplier Quotation Item
            - If `custom_supplier_quotation` is empty: Use `price_list_rate`
        2. Then, distribute expenses proportionally based on item amounts
        3. Formula: `rate = original_rate + (expense_per_item / qty)`
        4. If margin exists: `rate = rate + (rate * margin_percentage / 100)`
    - **Real-time Recalculation:**
        - When expense amount is changed: Auto-save after 500ms (debounced)
        - When expense row is added: Auto-save after 500ms
        - When expense row is removed: Auto-save after 500ms
        - Rates update automatically without manual save
    - **Note:** When expenses are deleted/changed, rates automatically return to original values

### Phase 4: Approval and Submission

9. **Check Approved**

    - Check "Approved" checkbox in Quotation
    - Submit button becomes visible
    - Without Approved: Submit button is hidden

10. **Submit Quotation**
    - Click Submit button (only visible if Approved = 1)
    - `before_submit` event validates Approved checkbox
    - If not approved: Error message shown
    - If approved: Quotation is submitted (docstatus = 1)

### Phase 5: Post-Submission (Submitted Quotation)

11. **View Supplier Quotation Items (Read-Only)**

    -   Button changes to "View Supplier Quotation Items" (standalone, info color)
    -   Dialog shows items without checkboxes
    -   No "Add Selected Items" button
    -   Read-only view for reference

12. **Create Sales Order**
    -   Standard ERPNext "Create Sales Order" button appears
    -   Click to create Sales Order from Quotation
    -   Expenses are automatically copied to Sales Order via mapper override:
        -   `custom_service_expense_table` → `custom_sales_order_service_expenses_table`
        -   Copied in `set_missing_values` function during document mapping
        -   Only copied if table is empty (prevents duplicates)

### Phase 6: Sales Order Processing

13. **Submit Sales Order**

    -   Submit Sales Order (standard ERPNext workflow)
    -   `on_submit` event triggers automatically:
        -   Creates Journal Entry for service expenses
        -   Debit: Expense accounts (from each expense row)
        -   Credit: Default service expense account (from Company settings)
    -   Journal Entry is automatically submitted

14. **Continue Standard ERPNext Flow**
    -   Sales Order → Delivery Note → Sales Invoice
    -   Standard ERPNext workflow continues

## Document States

### Quotation States

| State     | docstatus | custom_approved | Available Actions                                |
| --------- | --------- | --------------- | ------------------------------------------------ |
| Draft     | 0         | 0               | Add items, Add expenses, Check Approved          |
| Draft     | 0         | 1               | Add items, Add expenses, Submit (button visible) |
| Submitted | 1         | 1               | View items (read-only), Create Sales Order       |

### Button Visibility

| Button                                | Draft (approved=0) | Draft (approved=1) | Submitted                     |
| ------------------------------------- | ------------------ | ------------------ | ----------------------------- |
| Material Request                      | ✅ Visible         | ✅ Visible         | ❌ Hidden                     |
| Compare Supplier Quotations           | ✅ Visible         | ✅ Visible         | ❌ Hidden                     |
| Select Items from Supplier Quotations | ✅ Visible (full)  | ✅ Visible (full)  | ❌ Hidden                     |
| View Supplier Quotation Items         | ❌ Hidden          | ❌ Hidden          | ✅ Visible (read-only)        |
| Submit                                | ❌ Hidden          | ✅ Visible         | ❌ Hidden                     |
| Create Sales Order                    | ❌ Hidden          | ❌ Hidden          | ✅ Visible (ERPNext standard) |

## Key Differences from Standard ERPNext

### Standard ERPNext Workflow:

```
Quotation (Draft) → Submit → Quotation (Open) → Create Sales Order
```

### Power App Workflow:

```
Quotation (Draft)
├── Create Material Request
├── Select Items from Supplier Quotations
├── Add Expenses (distributed to items)
├── Check Approved
└── Submit (only if Approved = 1)
    ↓
Quotation (Submitted)
├── View Supplier Quotation Items (read-only)
└── Create Sales Order (standard ERPNext)
```

## Expense Flow

1. **Quotation Level:**

    - Expenses added in `custom_service_expense_table`
    - Distributed to items on save (validate event)

2. **Sales Order Level:**

    - Expenses copied to `custom_sales_order_service_expenses_table`
    - Copied automatically when creating Sales Order from Quotation

3. **Journal Entry:**
    - Created automatically on Sales Order submit
    - Records expenses in accounting system

## Field Mapping

### Quotation → Sales Order Expense Copy

| Quotation Field                | Sales Order Field                           |
| ------------------------------ | ------------------------------------------- |
| `custom_service_expense_table` | `custom_service_expense_table`              |
|                                | `custom_sales_order_service_expenses_table` |
|                                | (legacy)                                    |
| `service_expense_type`         | `service_expense_type`                      |
| `company`                      | `company`                                   |
| `default_account`              | `default_account`                           |
| `amount`                       | `amount`                                    |

## Custom Fields Reference

### Quotation

-   `custom_approved` (Check) - Required for submission
-   `custom_service_expense_table` (Table: Service Expense) - Expense entries
-   `custom_item_margin` (Float) - Margin percentage
-   `custom_total_expenses` (Currency) - Total expenses from expense table (auto-calculated)

### Quotation Item

-   `custom_supplier_quotation` (Link) - Supplier Quotation reference
-   `custom_supplier_quotation_item_rate` (Currency) - Supplier quotation item rate (auto-saved from Supplier Quotation)
-   `custom_item_expense_amount` (Currency) - Expense amount per item (auto-calculated on expense distribution)

### Sales Order

-   `custom_sales_order_service_expenses_table` (Table: Service Expense) - Copied expenses

### Company

-   `custom_default_service_expense_account` (Link: Account) - Default account for Journal Entry credit

## Notes

-   Quotation can remain in Draft indefinitely
-   Submit is only allowed when Approved = 1
-   After submission, item selection becomes read-only
-   Expenses are distributed proportionally based on item amounts
-   Journal Entry is created automatically on Sales Order submit
-   All custom logic uses document events (no method overrides, except Landed Cost Voucher)
-   Real-time expense recalculation with 500ms debounce
-   Landed Cost Voucher extended to support Service Items (after purchase)
-   Service Expense Table is still required for Quotation-level expenses (before purchase)
