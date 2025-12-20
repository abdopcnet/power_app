# Power App - API Tree

## Overview

This document provides a tree structure of all API methods, document events, and client-side functions in Power App.

## API Structure

```
power_app
│
├── quotation (power_app.quotation)
│   ├── get_supplier_quotation_items(quotation_name)
│   │   └── Returns: List of supplier quotation items
│   │
│   ├── get_material_requests_from_quotation(quotation_name)
│   │   └── Returns: List of Material Requests with RFQ details
│   │
│   ├── add_items_from_supplier_quotations(quotation_name, selected_items)
│   │   └── Returns: Updated Quotation document
│   │
│   ├── quotation_validate(doc, method) [Document Event]
│   │   └── Event: Quotation.validate
│   │   └── Purpose: Expense distribution and rate calculation
│   │
│   └── quotation_before_submit(doc, method) [Document Event]
│       └── Event: Quotation.before_submit
│       └── Purpose: Validate Approved checkbox
│
├── sales_order (power_app.sales_order)
│   ├── copy_quotation_expenses_to_sales_order(doc, method) [Document Event]
│   │   └── Event: Sales Order.before_save
│   │   └── Purpose: Copy expenses from Quotation
│   │
│   └── create_je_from_service_expence(doc, method) [Document Event]
│       └── Event: Sales Order.on_submit
│       └── Purpose: Create Journal Entry for expenses
│
├── supplier_quotation (power_app.supplier_quotation)
│   ├── check_quotation_linked(doc)
│   │   └── Returns: Quotation name if linked, None otherwise
│   │
│   └── update_quotation_linked(doc, q)
│       └── Returns: Updated Quotation document
│
├── material_request (power_app.material_request)
│   └── make_material_request_from_quotation(source, target)
│       └── Returns: Material Request document
│
└── item (power_app.item)
    └── get_item_details(item_code)
        └── Returns: Dict with stock, rates, supplier details
```

## Client-Side Functions

### quotation.js

```
quotation.js
│
├── refresh(frm) [Form Handler]
│   ├── Show/hide Submit button based on custom_approved
│   ├── Add buttons based on docstatus
│   └── Set item query filters
│
├── add_show_item_history_button(frm)
│   └── Shows item price & stock details dialog
│
├── add_compare_supplier_quotations_button(frm)
│   └── Opens Supplier Quotation Comparison report
│
├── add_select_items_from_supplier_quotations_button(frm)
│   ├── Draft (docstatus=0): Full functionality
│   └── Submitted (docstatus=1): Read-only view
│
├── make_MR(frm)
│   └── Creates Material Request from Quotation
│
├── show_item_selection_dialog(frm)
│   └── Fetches and displays supplier items (editable)
│
├── show_item_selection_dialog_readonly(frm)
│   └── Fetches and displays supplier items (read-only)
│
├── show_item_selection_dialog_content(frm, items)
│   └── Builds dialog with checkboxes and "Add Selected Items" button
│
├── show_item_selection_dialog_content_readonly(frm, items)
│   └── Builds dialog without checkboxes (read-only)
│
├── build_supplier_items_table_html(items, currency)
│   └── Returns: HTML table with checkboxes
│
├── build_supplier_items_table_html_readonly(items, currency)
│   └── Returns: HTML table without checkboxes
│
├── setup_item_selection_checkboxes(dialog, totalItems)
│   └── Enables multi-select functionality
│
├── get_selected_items_from_dialog(dialog)
│   └── Returns: Array of selected items
│
├── fetch_item_details(frm, item_codes)
│   └── Returns: Promise with item details
│
└── build_item_details_html(item_details, currency)
    └── Returns: HTML table for item details
```

### supplier_quotation.js

```
supplier_quotation.js
│
├── refresh(frm) [Form Handler]
│   └── Checks for linked quotation and shows update button
│
└── update_quotation(frm, q)
    └── Updates Customer Quotation with Supplier Quotation items
```

## Document Events Tree

```
Document Events
│
├── Quotation
│   ├── validate
│   │   └── power_app.quotation.quotation_validate
│   │       ├── Calculate total expenses
│   │       ├── Distribute expenses to items
│   │       └── Apply margin if exists
│   │
│   └── before_submit
│       └── power_app.quotation.quotation_before_submit
│           └── Validate custom_approved checkbox
│
└── Sales Order
    ├── before_save
    │   └── power_app.sales_order.copy_quotation_expenses_to_sales_order
    │       └── Copy expenses from Quotation
    │
    └── on_submit
        └── power_app.sales_order.create_je_from_service_expence
            └── Create Journal Entry for expenses
```

## API Call Flow Examples

### Item Selection Flow

```
User clicks "Select Items from Supplier Quotations"
    ↓
quotation.js: show_item_selection_dialog()
    ↓
frappe.call('power_app.quotation.get_supplier_quotation_items')
    ↓
quotation.py: get_supplier_quotation_items()
    ↓
Returns: List of supplier items
    ↓
quotation.js: show_item_selection_dialog_content()
    ↓
User selects items and clicks "Add Selected Items"
    ↓
quotation.js: get_selected_items_from_dialog()
    ↓
frappe.call('power_app.quotation.add_items_from_supplier_quotations')
    ↓
quotation.py: add_items_from_supplier_quotations()
    ↓
Updates Quotation and returns
    ↓
quotation.js: frm.reload_doc()
```

### Expense Distribution Flow

```
User adds expenses and saves Quotation
    ↓
Quotation.validate event triggered
    ↓
quotation.py: quotation_validate()
    ↓
Calculate total expenses
    ↓
Distribute expenses to items proportionally
    ↓
Apply margin if exists
    ↓
Update item rates
    ↓
Document saved with updated rates
```

### Sales Order Creation Flow

```
User creates Sales Order from Quotation
    ↓
Sales Order.before_save event triggered
    ↓
sales_order.py: copy_quotation_expenses_to_sales_order()
    ↓
Copy expenses from Quotation to Sales Order
    ↓
Sales Order saved
    ↓
User submits Sales Order
    ↓
Sales Order.on_submit event triggered
    ↓
sales_order.py: create_je_from_service_expence()
    ↓
Create Journal Entry
    ↓
Journal Entry submitted automatically
```

## Notes

-   All whitelisted methods use `@frappe.whitelist()` decorator
-   Document events are registered in `hooks.py`
-   Client-side functions are called from form handlers
-   All API methods follow unified logging format
-   No method overrides - only document events and whitelisted methods
-   **Note:** The field `compnay` (typo for `company`) is used in Service Expense DocType JSON and must be kept as-is in code to match the JSON field name
