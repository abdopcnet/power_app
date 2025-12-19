# Power App Code Structure

## Organization Principle
Each functionality has its own Python file and corresponding JavaScript file (if needed).

## File Structure

### Python Files (Backend)

#### `quotation.py` → `quotation.js`
**Purpose:** Quotation-related functions

**Functions:**
- `get_supplier_quotation_items()` - Get supplier quotation items linked to customer quotation
- `get_material_requests_from_quotation()` - Get material requests linked to quotation
- `quotation_update()` - Document event handler for Quotation on_update

**Document Events:**
- `Quotation.on_update` → `quotation_update()`

---

#### `item.py` → `quotation.js` (used by)
**Purpose:** Item-related functions

**Functions:**
- `get_item_details()` - Get item details (stock, rates, supplier)

**Called from:**
- `quotation.js` - Show Item History button

---

#### `supplier_quotation.py` → `supplier_quotation.js`
**Purpose:** Supplier Quotation-related functions

**Functions:**
- `check_quotation_linked()` - Check if supplier quotation is linked to customer quotation
- `update_quotation_linked()` - Update customer quotation with items from supplier quotation

**Called from:**
- `supplier_quotation.js` - Update Quotation button

---

#### `sales_order.py` → (Document Events only)
**Purpose:** Sales Order-related functions

**Functions:**
- `copy_quotation_expenses_to_sales_order()` - Copy expenses from quotation to sales order
- `create_je_from_service_expence()` - Create journal entry on sales order submit

**Document Events:**
- `Sales Order.before_save` → `copy_quotation_expenses_to_sales_order()`
- `Sales Order.on_submit` → `create_je_from_service_expence()`

---

#### `mapper.py` → `quotation.js` (used by)
**Purpose:** Document mapping functions

**Functions:**
- `make_material_request_from_quotation()` - Create material request from quotation

**Called from:**
- `quotation.js` - Material Request button

---

### JavaScript Files (Frontend)

#### `quotation.js`
**Purpose:** Quotation form client-side logic

**Functions:**
- `add_show_item_history_button()` - Show item history dialog
- `add_compare_supplier_quotations_button()` - Open supplier quotation comparison report
- `add_select_items_from_supplier_quotations_button()` - Select items from supplier quotations
- `make_MR()` - Create material request button
- `show_item_selection_dialog()` - Display supplier quotation items
- `setup_item_selection_checkboxes()` - Enable multi-select functionality

**Calls:**
- `power_app.item.get_item_details`
- `power_app.quotation.get_material_requests_from_quotation`
- `power_app.quotation.get_supplier_quotation_items`
- `power_app.mapper.make_material_request_from_quotation`

---

#### `supplier_quotation.js`
**Purpose:** Supplier Quotation form client-side logic

**Functions:**
- `update_quotation()` - Update customer quotation button

**Calls:**
- `power_app.supplier_quotation.check_quotation_linked`
- `power_app.supplier_quotation.update_quotation_linked`

---

## Mapping Summary

| Python File | JavaScript File | Relationship |
|------------|----------------|--------------|
| `quotation.py` | `quotation.js` | Direct mapping |
| `item.py` | `quotation.js` | Used by |
| `supplier_quotation.py` | `supplier_quotation.js` | Direct mapping |
| `sales_order.py` | - | Document events only |
| `mapper.py` | `quotation.js` | Used by |

---

## Removed Files

- `overried.py` - Removed (was overriding ERPNext's make_sales_order)
  - **Replaced by:** Document events in `sales_order.py`
  - **Reason:** To preserve ERPNext's original logic without override

---

## Notes

1. **No Overrides:** We use document events instead of method overrides to preserve ERPNext's original logic
2. **One File Per Functionality:** Each major functionality has its own Python and JavaScript files
3. **Clear Naming:** File names match their primary DocType or functionality

