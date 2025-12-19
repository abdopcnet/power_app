# Power App - Code Structure

## Organization Principle

Each functionality has its own Python file and corresponding JavaScript file (if needed).

## File Mapping

| Python File             | JavaScript File         | Purpose                                           |
| ----------------------- | ----------------------- | ------------------------------------------------- |
| `quotation.py`          | `quotation.js`          | Quotation functions                               |
| `item.py`               | -                       | Item details (used by `quotation.js`)             |
| `supplier_quotation.py` | `supplier_quotation.js` | Supplier Quotation functions                      |
| `sales_order.py`        | -                       | Sales Order document events                       |
| `material_request.py`   | -                       | Material Request mapping (used by `quotation.js`) |

## Python Functions

### `quotation.py`

-   `get_supplier_quotation_items(quotation_name)` - Get supplier quotation items
-   `get_material_requests_from_quotation(quotation_name)` - Get material requests
-   `add_items_from_supplier_quotations(quotation_name, selected_items)` - Add selected items to quotation
-   `quotation_validate(doc, method)` - Document event: Quotation.validate

### `item.py`

-   `get_item_details(item_code)` - Get item stock, rates, supplier

### `supplier_quotation.py`

-   `check_quotation_linked(doc)` - Check if linked to quotation
-   `update_quotation_linked(doc, q)` - Update quotation with items

### `sales_order.py`

-   `copy_quotation_expenses_to_sales_order(doc, method)` - Document event: Sales Order.before_save
-   `create_je_from_service_expence(doc, method)` - Document event: Sales Order.on_submit

### `material_request.py`

-   `make_material_request_from_quotation(source, target)` - Create Material Request from Quotation

## JavaScript Functions

### `quotation.js`

-   `add_show_item_history_button(frm)` - Show item history
-   `add_compare_supplier_quotations_button(frm)` - Open comparison report
-   `add_select_items_from_supplier_quotations_button(frm)` - Select items dialog
-   `make_MR(frm)` - Create Material Request button
-   `show_item_selection_dialog(frm)` - Display items dialog
-   `setup_item_selection_checkboxes(dialog, totalItems)` - Enable multi-select

### `supplier_quotation.js`

-   `update_quotation(frm, q)` - Update quotation button

## Document Events

-   `Quotation.validate` → `quotation.quotation_validate()`
-   `Sales Order.before_save` → `sales_order.copy_quotation_expenses_to_sales_order()`
-   `Sales Order.on_submit` → `sales_order.create_je_from_service_expence()`

## Notes

-   No method overrides - uses document events only
-   One file per functionality
-   Clear naming convention
