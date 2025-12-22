# Power App - Features Summary

## Core Features

1. **Material Request from Quotation** - Create MR from Draft Quotation
2. **Supplier Quotation Comparison** - Compare supplier offers
3. **Item Selection** - Multi-select items from supplier quotations
4. **Expense Allocation** - Add expenses at Quotation, auto-distribute
5. **Approval Workflow** - Required before submission
6. **Expense Flow** - Quotation → Sales Order → Journal Entry
7. **Auto Journal Entry** - Created on Sales Order submit
8. **Real-time Recalculation** - Auto-update rates (500ms debounce)
9. **Rate Restoration** - Uses supplier/price list rates
10. **Landed Cost Extension** - Supports Service Items
11. **Item History** - Show price & stock details
12. **Payment Schedule** - Auto-set due_date

## Custom Fields

**Quotation:**

-   `custom_approved` (Check)
-   `custom_service_expense_table` (Table)
-   `custom_item_margin` (Float)
-   `custom_total_expenses` (Currency)

**Quotation Item:**

-   `custom_supplier_quotation` (Link)
-   `custom_supplier_quotation_item_rate` (Currency)
-   `custom_item_expense_amount` (Currency)

**Sales Order:**

-   `custom_sales_order_service_expenses_table` (Table)

**Company:**

-   `custom_default_service_expense_account` (Link)

**Journal Entry:**

-   `custom_created_from_doctype` (Data)
-   `custom_sales_order_refrence` (Link)

## Workflow

1. Create Quotation (Draft) → Material Request → RFQ → Supplier Quotations
2. Select Items from Supplier Quotations
3. Add Expenses → Auto-distribute
4. Check Approved → Submit
5. Create Sales Order (expenses auto-copied)
6. Submit Sales Order (Journal Entry auto-created)

## Key Files

**Python:** `quotation.py`, `sales_order.py`, `quotation_mapper.py`, `supplier_quotation.py`, `material_request.py`

**JavaScript:** `quotation.js`, `sales_order.js`, `supplier_quotation.js`
