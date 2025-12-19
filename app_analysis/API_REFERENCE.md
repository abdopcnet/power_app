# Power App - API Reference

## Table of Contents

1. [Python API Methods](#python-api-methods)
2. [JavaScript API Methods](#javascript-api-methods)
3. [Document Events](#document-events)
4. [Custom Fields Reference](#custom-fields-reference)

---

## Python API Methods

### `power_app.customization.get_item_details`

**Purpose:** Retrieves item stock, pricing, and supplier information.

**Signature:**

```python
@frappe.whitelist()
def get_item_details(item_code)
```

**Parameters:**

-   `item_code` (str): Item code to query

**Returns:**

```python
{
    "item_code": str,
    "stock_qty": float,
    "last_selling_rate": float,
    "last_purchase_rate": float,
    "supplier": str
}
```

**Data Sources:**

-   Stock: Latest Bin record (actual_qty)
-   Selling Rate: Latest submitted Sales Invoice Item
-   Purchase Rate: Latest submitted Purchase Invoice Item
-   Supplier: Supplier from Purchase Invoice

**Example:**

```python
frappe.call({
    method: "power_app.customization.get_item_details",
    args: {
        item_code: "ITEM-001"
    }
})
```

---

### `power_app.customization.quotation_update`

**Purpose:** Recalculates quotation item rates based on expenses and margin.

**Signature:**

```python
@frappe.whitelist()
def quotation_update(doc, method)
```

**Parameters:**

-   `doc`: Quotation document object
-   `method`: Event method name (typically "on_update")

**Behavior:**

1. Preserves Supplier Quotation rates in custom fields
2. Distributes expenses proportionally to items
3. Applies margin percentage if set
4. Recalculates amounts
5. Commits database changes

**Triggers:**

-   Quotation `on_update` event

**Example:**

```python
# Called automatically on Quotation save
# No manual call needed
```

---

### `power_app.customization.create_je_from_service_expence`

**Purpose:** Creates Journal Entry for service expenses on Sales Order submission.

**Signature:**

```python
@frappe.whitelist()
def create_je_from_service_expence(doc, method)
```

**Parameters:**

-   `doc`: Sales Order document object
-   `method`: Event method name (typically "on_submit")

**Behavior:**

1. Groups expenses by account
2. Creates Journal Entry with debit/credit entries
3. Submits Journal Entry automatically

**Requirements:**

-   `custom_service_expense` table must have entries
-   Company must have `custom_default_service_expense` account set

**Triggers:**

-   Sales Order `on_submit` event

**Example:**

```python
# Called automatically on Sales Order submit
# No manual call needed
```

---

### `power_app.customization.check_quotation_linked`

**Purpose:** Finds linked Customer Quotation from Supplier Quotation.

**Signature:**

```python
@frappe.whitelist()
def check_quotation_linked(doc)
```

**Parameters:**

-   `doc` (str): Supplier Quotation name

**Returns:**

-   `str`: Quotation name if found, empty string otherwise

**Logic:**

1. Gets Material Request from Supplier Quotation items
2. Checks Material Request's `custom_dc_refrance` field
3. Returns Quotation name

**Example:**

```python
frappe.call({
    method: "power_app.customization.check_quotation_linked",
    args: {
        doc: "SQ-00001"
    }
})
```

---

### `power_app.customization.update_quotation_linked`

**Purpose:** Updates Customer Quotation with items from Supplier Quotation.

**Signature:**

```python
@frappe.whitelist()
def update_quotation_linked(doc, q)
```

**Parameters:**

-   `doc` (str): Supplier Quotation name
-   `q` (str): Customer Quotation name

**Returns:**

-   Updated Quotation document object

**Behavior:**

1. Sets Quotation to draft
2. Clears existing items
3. Copies items from Supplier Quotation
4. Uses `base_rate` for rate mapping
5. Recalculates totals
6. Adds timeline comment
7. Saves quotation

**Example:**

```python
frappe.call({
    method: "power_app.customization.update_quotation_linked",
    args: {
        doc: "SQ-00001",
        q: "QTN-00001"
    }
})
```

---

### `power_app.mapper.make_material_request_from_quotation`

**Purpose:** Creates Material Request from Quotation.

**Signature:**

```python
@frappe.whitelist()
def make_material_request_from_quotation(source, target=None)
```

**Parameters:**

-   `source` (str): Quotation name
-   `target` (str, optional): Existing Material Request name (for update)

**Returns:**

-   Material Request document object

**Mapping:**

-   Quotation → Material Request
-   Quotation Item → Material Request Item
-   Sets Material Request Type to "Purchase"
-   Sets `custom_create_from_dc` to "Material Request"
-   Sets `custom_dc_refrance` to Quotation name

**Validation:**

-   Only works with submitted Quotations (docstatus = 1)

**Example:**

```python
frappe.model.open_mapped_doc({
    method: "power_app.mapper.make_material_request_from_quotation",
    frm: quotation_form
})
```

---

### `power_app.overried.make_sales_order`

**Purpose:** Creates Sales Order from Quotation (overrides standard method).

**Signature:**

```python
@frappe.whitelist()
def make_sales_order(source_name: str, target_doc=None)
```

**Parameters:**

-   `source_name` (str): Quotation name
-   `target_doc` (str, optional): Existing Sales Order name

**Returns:**

-   Sales Order document object

**Customizations:**

-   Includes service expenses in mapping
-   Handles alternative items
-   Creates customer from Lead/Prospect if needed
-   Calculates balance quantities

**Validation:**

-   Checks quotation validity period (if enabled in Selling Settings)

**Example:**

```python
frappe.model.open_mapped_doc({
    method: "power_app.overried.make_sales_order",
    frm: quotation_form
})
```

---

## JavaScript API Methods

### Quotation Form Events

#### `set_item_query`

**Purpose:** Filters items based on `custom_services` flag.

**Trigger:** Form refresh, `custom_services` change

**Behavior:**

-   If `custom_services` is checked:
    -   Shows only non-stock items (`is_stock_item: 0`)
    -   Shows only sales items (`is_sales_item: 1`)
    -   Excludes items with variants (`has_variants: 0`)
-   Otherwise: Uses standard ERPNext item query

---

#### `add_show_item_history_button`

**Purpose:** Adds button to display item history.

**Trigger:** Form refresh

**Behavior:**

-   Fetches item details for all unique items
-   Displays in dialog with formatted table
-   Shows stock, rates, and supplier information

---

#### `make_MR`

**Purpose:** Adds Material Request creation button.

**Trigger:** Form refresh (only for submitted quotations)

**Behavior:**

-   Shows "Create > Material Request" button
-   Opens mapped document dialog

---

### Supplier Quotation Form Events

#### `refresh`

**Purpose:** Checks for linked Quotation and adds update button.

**Trigger:** Form refresh

**Behavior:**

1. Calls `check_quotation_linked()`
2. If linked Quotation found:
    - Adds "Update Quotation" button (if submitted)
    - Button calls `update_quotation_linked()`
    - Navigates to updated Quotation

---

## Document Events

### Quotation Events

#### `on_update`

-   **Handler:** `power_app.customization.quotation_update`
-   **Purpose:** Recalculates item rates with expenses and margin
-   **Triggers:** Every time Quotation is saved

---

### Sales Order Events

#### `on_submit`

-   **Handler:** `power_app.customization.create_je_from_service_expence`
-   **Purpose:** Creates Journal Entry for service expenses
-   **Triggers:** When Sales Order is submitted
-   **Requirements:** `custom_service_expense` table must have entries

---

## Custom Fields Reference

### Quotation Custom Fields

| Field Name                         | Type  | Label                     | Description                 |
| ---------------------------------- | ----- | ------------------------- | --------------------------- |
| `custom_customer_qoutation_number` | Data  | Customer Qoutation Number | Customer's reference number |
| `custom_quotation_expenses`        | Table | Quotation Expenses        | Child table for expenses    |
| `custom_item_margin`               | Float | Item Margin               | Percentage margin to apply  |
| `custom_services`                  | Check | Services                  | Flag for service quotation  |

### Quotation Item Custom Fields

| Field Name             | Type     | Description                            |
| ---------------------- | -------- | -------------------------------------- |
| `custom_sq_rate`       | Currency | Original Supplier Quotation rate       |
| `custom_sq_net_rate`   | Currency | Original Supplier Quotation net rate   |
| `custom_sq_amount`     | Currency | Original Supplier Quotation amount     |
| `custom_sq_net_amount` | Currency | Original Supplier Quotation net amount |

### Sales Order Custom Fields

| Field Name               | Type  | Label           | Description                      |
| ------------------------ | ----- | --------------- | -------------------------------- |
| `custom_service_expense` | Table | Service Expense | Child table for service expenses |

### Material Request Custom Fields

| Field Name              | Type | Label          | Description                   |
| ----------------------- | ---- | -------------- | ----------------------------- |
| `custom_create_from_dc` | Data | Create From DC | Source document type          |
| `custom_dc_refrance`    | Data | DC Refrance    | Reference to source Quotation |

### Company Custom Fields

| Field Name                       | Type | Label                   | Description                          |
| -------------------------------- | ---- | ----------------------- | ------------------------------------ |
| `custom_default_service_expense` | Link | Default Service Expense | Default account for service expenses |

---

## Error Handling

### Common Errors

1. **Missing Default Service Expense Account**

    - Error: "Please set the default service expense account in Company: {company}"
    - Solution: Set `custom_default_service_expense` in Company master

2. **Document Not Found**

    - Error: "Document not found: {doctype} {name}"
    - Solution: Ensure document exists and user has permissions

3. **Database Errors**
    - Errors are logged via `frappe.log_error()`
    - User-friendly messages shown via `frappe.throw()`

---

## Best Practices

1. **Always check document status** before operations
2. **Use base_rate** when copying rates to avoid currency issues
3. **Group expenses** by account for efficient Journal Entry creation
4. **Preserve original rates** in custom fields for calculations
5. **Validate required fields** before processing
6. **Commit database changes** after calculations

---

_End of API Reference_
