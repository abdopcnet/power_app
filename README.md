# Power App - Documentation

![Version](https://img.shields.io/badge/version-19.12.2025-blue)


## Overview

Power App is a Frappe/ERPNext customization for intermediary service companies. It extends ERPNext's standard workflow to support:

-   Supplier quotation comparison and item selection
-   Expense allocation to quotation items
-   Material Request workflow from Customer Quotation

## Code Structure

### Python Files

| File                    | Purpose                      | JavaScript              |
| ----------------------- | ---------------------------- | ----------------------- |
| `quotation.py`          | Quotation functions          | `quotation.js`          |
| `item.py`               | Item details                 | Used by `quotation.js`  |
| `supplier_quotation.py` | Supplier Quotation functions | `supplier_quotation.js` |
| `sales_order.py`        | Sales Order document events  | -                       |
| `material_request.py`   | Material Request mapping     | Used by `quotation.js`  |

### JavaScript Files

| File                    | Purpose                       | Python                                           |
| ----------------------- | ----------------------------- | ------------------------------------------------ |
| `quotation.js`          | Quotation form logic          | `quotation.py`, `item.py`, `material_request.py` |
| `supplier_quotation.js` | Supplier Quotation form logic | `supplier_quotation.py`                          |

## Key Features

### 1. Supplier Quotation Item Selection

-   Select items from multiple supplier quotations
-   Add selected items to customer quotation
-   Track supplier rates and original rates

### 2. Expense Allocation

-   Add expenses to quotations
-   Automatically distribute expenses to items proportionally
-   Calculate final rates with expenses

### 3. Material Request Workflow

-   Create Material Request from Draft Quotation
-   Link Material Request to Quotation
-   Track supplier quotations via Material Request

### 4. Supplier Quotation Comparison

-   Open comparison report from Quotation
-   Filter by Material Request/RFQ
-   Select Material Request if multiple exist

## Document Events

### Quotation

-   `on_update`: Calculate expense allocation and item rates (`quotation.py::quotation_update`)

### Sales Order

-   `before_save`: Copy quotation expenses to sales order (`sales_order.py::copy_quotation_expenses_to_sales_order`)
-   `on_submit`: Create journal entry for service expenses (`sales_order.py::create_je_from_service_expence`)

## API Methods

### Quotation

-   `power_app.quotation.get_supplier_quotation_items(quotation_name)` - Get supplier quotation items
-   `power_app.quotation.get_material_requests_from_quotation(quotation_name)` - Get material requests

### Item

-   `power_app.item.get_item_details(item_code)` - Get item stock, rates, supplier

### Supplier Quotation

-   `power_app.supplier_quotation.check_quotation_linked(doc)` - Check if linked to quotation
-   `power_app.supplier_quotation.update_quotation_linked(doc, q)` - Update quotation with items

### Mapper

-   `power_app.material_request.make_material_request_from_quotation(source, target)` - Create Material Request

## Workflow

```
Customer Quotation (Draft)
    ↓
Material Request (from Quotation)
    ↓
Request for Quotation (RFQ)
    ↓
Supplier Quotations (Multiple)
    ↓
Select Items from Supplier Quotations
    ↓
Update Customer Quotation with Selected Items
    ↓
Add Expenses
    ↓
Submit Customer Quotation
    ↓
Sales Order → Delivery Note → Sales Invoice
```

## Installation

1. Install app in Frappe bench
2. Run migrations
3. Clear cache: `bench clear-cache`
4. Restart: `bench restart`

## Notes

-   No method overrides - uses document events to preserve ERPNext's original logic
-   All code organized by functionality (one file per DocType/feature)
-   Python and JavaScript files have matching names where applicable
