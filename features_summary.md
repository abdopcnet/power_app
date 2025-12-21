# Power App - Features Summary

![Version](https://img.shields.io/badge/version-21.12.2025-blue)

## Overview

Frappe/ERPNext customization for intermediary service companies. Extends ERPNext workflow for supplier quotation management, expense allocation, and automated pricing.

---

## Features

1. **Material Request from Quotation** - Create MR directly from Draft Quotation
2. **Supplier Quotation Comparison** - Compare supplier offers with pre-filtered report
3. **Select Items from Supplier Quotations** - Multi-select items with automatic rate updates
4. **Expense Allocation at Quotation Level** - Add expenses before purchase, auto-distribute to items
5. **Approved Workflow** - Approval required before Quotation submission
6. **Automatic Expense Flow** - Expenses copied from Quotation → Sales Order → Journal Entry
7. **Automatic Journal Entry** - Created on Sales Order submit (Debit: expense accounts, Credit: default account)
8. **Real-time Expense Recalculation** - Auto-save with 500ms debounce when expenses change
9. **Rate Restoration Logic** - Restores original rates (supplier/price list) before expense distribution
10. **Landed Cost Voucher Extension** - Supports Service Items (not just Stock/Fixed Assets)
11. **Item History Display** - Show item price and stock details in dialog
12. **Unified Logging System** - Consistent logging format across all files

---

## Custom Fields

**Quotation:**

-   `custom_approved` (Check)
-   `custom_quotation_expenses_table` (Table: Service Expense)
-   `custom_item_margin` (Float)

**Quotation Item:**

-   `custom_supplier_quotation` (Link)
-   `custom_item_expense_amount` (Currency)

**Sales Order:**

-   `custom_sales_order_service_expenses_table` (Table: Service Expense)

**Company:**

-   `custom_default_service_expense_account` (Link: Account)

---

## Key Files

**Python:**

-   `quotation.py` - Expense distribution, approval validation
-   `sales_order.py` - Journal Entry creation
-   `quotation_mapper.py` - Copy expenses to Sales Order
-   `supplier_quotation.py` - Supplier quotation functions
-   `material_request.py` - MR creation from Quotation
-   `item.py` - Item details retrieval
-   `landed_cost_voucher.py` - Service Items support

**JavaScript:**

-   `quotation.js` - Client-side logic, buttons, dialogs
-   `supplier_quotation.js` - Supplier quotation UI

---

## Workflow

1. Create Quotation (Draft) → Create Material Request → RFQ → Receive Supplier Quotations
2. Compare & Select Items from Supplier Quotations
3. Add Expenses → Auto-distribute to items
4. Check Approved → Submit Quotation
5. Create Sales Order (expenses auto-copied)
6. Submit Sales Order (Journal Entry auto-created)

---

## Differences from ERPNext

| Feature                 | ERPNext                 | Power App          |
| ----------------------- | ----------------------- | ------------------ |
| Expense Location        | Purchase Receipt        | Quotation          |
| Expense Timing          | After receipt           | At Quotation stage |
| Expense Distribution    | Manual                  | Automatic          |
| Material Request Source | Sales Order             | Quotation (Draft)  |
| Supplier Integration    | Manual                  | Direct selection   |
| Approval                | Not required            | Required           |
| Journal Entry           | Manual                  | Automatic          |
| Landed Cost Support     | Stock/Fixed Assets only | + Service Items    |

---

## Installation

1. Install app in Frappe bench
2. Run migrations
3. `bench clear-cache`
4. `bench restart`

---

## Documentation

-   `app_workflow.md` - Complete workflow
-   `app_expenses_workflow.md` - Expense flow details
-   `app_file_structure.md` - File structure
-   `app_api_tree.md` - API reference
-   `app_vs_erpnext_differences.md` - ERPNext comparison

---

**Version:** 21.12.2025
