# Power App - File Structure

## Directory Structure

```
power_app/
├── power_app/
│   ├── __init__.py                    # App version
│   ├── hooks.py                       # Document events, doctype JS mapping
│   ├── quotation.py                   # Quotation functions and events
│   ├── sales_order.py                 # Sales Order events
│   ├── supplier_quotation.py          # Supplier Quotation functions
│   ├── material_request.py            # Material Request mapping
│   ├── item.py                        # Item details functions
│   ├── landed_cost_voucher.py         # Landed Cost Voucher override (Service Items support)
│   ├── config/                        # Configuration files
│   ├── power_app/                     # Custom DocTypes
│   │   ├── doctype/
│   │   │   ├── service_expense/
│   │   │   ├── service_expense_type/
│   │   │   └── service_line/
│   │   └── custom/                     # Custom field JSON files
│   │       ├── quotation.json
│   │       ├── quotation_item.json
│   │       ├── sales_order.json
│   │       └── company.json
│   └── public/
│       └── js/
│           ├── quotation.js           # Quotation client-side logic
│           └── supplier_quotation.js  # Supplier Quotation client-side logic
├── README.md                          # App overview
├── CODE_STRUCTURE.md                  # Code organization
├── API.md                             # API reference
├── power_app_workflow.md              # Complete workflow documentation
├── expenses_implementation_workflow.md # Expense flow details
├── app_file_structure.md              # This file
├── api_tree.md                        # API tree structure
├── plan.md                            # Implementation plan
└── original_erpnext_sales_cycle_symmery.md # ERPNext workflow reference
```

## File Descriptions

### Python Files

#### `power_app/quotation.py`

-   **Purpose:** Quotation-related functions and document events
-   **Functions:**
    -   `get_supplier_quotation_items()` - Whitelisted: Get supplier items
    -   `get_material_requests_from_quotation()` - Whitelisted: Get Material Requests
    -   `add_items_from_supplier_quotations()` - Whitelisted: Add selected items
    -   `quotation_validate()` - Document event: Expense distribution
    -   `quotation_before_submit()` - Document event: Approval validation

#### `power_app/sales_order.py`

-   **Purpose:** Sales Order document events
-   **Functions:**
    -   `copy_quotation_expenses_to_sales_order()` - Document event: Copy expenses
    -   `create_je_from_service_expence()` - Document event: Create Journal Entry

#### `power_app/supplier_quotation.py`

-   **Purpose:** Supplier Quotation functions
-   **Functions:**
    -   `check_quotation_linked()` - Whitelisted: Check linkage
    -   `update_quotation_linked()` - Whitelisted: Update quotation

#### `power_app/material_request.py`

-   **Purpose:** Material Request mapping
-   **Functions:**
    -   `make_material_request_from_quotation()` - Whitelisted: Create MR from Quotation

#### `power_app/item.py`

-   **Purpose:** Item details retrieval
-   **Functions:**
    -   `get_item_details()` - Whitelisted: Get item stock, rates, supplier

#### `power_app/hooks.py`

-   **Purpose:** Frappe hooks configuration
-   **Configuration:**
    -   `doctype_js` - Maps DocTypes to JavaScript files
    -   `doc_events` - Document event handlers
    -   `override_doctype_class` - Override standard DocType classes

### JavaScript Files

#### `power_app/public/js/quotation.js`

-   **Purpose:** Quotation form client-side logic
-   **Key Functions:**
    -   `refresh()` - Form refresh handler
    -   `add_show_item_history_button()` - Item history button
    -   `add_compare_supplier_quotations_button()` - Comparison report button
    -   `add_select_items_from_supplier_quotations_button()` - Item selection button
    -   `make_MR()` - Material Request button
    -   `show_item_selection_dialog()` - Editable item selection dialog
    -   `show_item_selection_dialog_readonly()` - Read-only item view dialog
    -   `build_supplier_items_table_html()` - Table with checkboxes
    -   `build_supplier_items_table_html_readonly()` - Table without checkboxes
    -   `trigger_expense_recalculation()` - Auto-save on expense changes (debounced)

#### `power_app/public/js/supplier_quotation.js`

-   **Purpose:** Supplier Quotation form client-side logic
-   **Key Functions:**
    -   `refresh()` - Form refresh handler
    -   `update_quotation()` - Update quotation button

### Custom Field JSON Files

#### `power_app/power_app/custom/quotation.json`

-   Custom fields for Quotation DocType
-   Fields: `custom_approved`, `custom_quotation_expenses_table`, `custom_item_margin`

#### `power_app/power_app/custom/quotation_item.json`

-   Custom fields for Quotation Item DocType
-   Fields: `custom_supplier_quotation`, `custom_item_expense_amount`

#### `power_app/power_app/custom/sales_order.json`

-   Custom fields for Sales Order DocType
-   Fields: `custom_sales_order_service_expenses_table`

#### `power_app/power_app/custom/company.json`

-   Custom fields for Company DocType
-   Fields: `custom_default_service_expense_account`

## Code Organization Principles

1. **One File Per Functionality**

    - Each major functionality has its own Python file
    - JavaScript files match Python files when applicable

2. **Document Events Over Method Overrides**

    - All custom logic uses document events
    - No method overrides of ERPNext core functions

3. **Unified Logging**

    - Frontend: `console.log('[filename.js] (message)')`
    - Backend: `frappe.log_error(f"[filename.py] function: message")`

4. **Clear Naming Convention**
    - Python functions: `snake_case`
    - JavaScript functions: `camelCase`
    - Custom fields: `custom_fieldname`

## Dependencies

-   **Frappe Framework:** Core framework
-   **ERPNext:** Standard ERPNext modules (Selling, Buying, Stock, Accounts)

## Notes

-   All code follows AGENTS.md guidelines
-   Code comments and documentation in English
-   User-facing messages preserve original language
-   No method overrides - only document events (except Landed Cost Voucher class override)
-   Landed Cost Voucher override extends functionality to support Service Items
-   Service Expense Table is still required for Quotation-level expenses (before purchase)
