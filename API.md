# Power App - API Reference

## Python API Methods

### Quotation Module (`power_app.quotation`)

#### `get_supplier_quotation_items(quotation_name)`

Get all items from supplier quotations linked to customer quotation via Material Request.

**Parameters:**

-   `quotation_name` (str): Customer Quotation name

**Returns:**

-   List of supplier quotation items with supplier details

**Example:**

```python
items = frappe.call({
    method: 'power_app.quotation.get_supplier_quotation_items',
    args: { quotation_name: 'QUO-00001' }
})
```

---

#### `get_material_requests_from_quotation(quotation_name)`

Get all Material Requests linked to Customer Quotation.

**Parameters:**

-   `quotation_name` (str): Customer Quotation name

**Returns:**

-   List of Material Requests with RFQ details

**Example:**

```python
mr_list = frappe.call({
    method: 'power_app.quotation.get_material_requests_from_quotation',
    args: { quotation_name: 'QUO-00001' }
})
```

---

### Item Module (`power_app.item`)

#### `get_item_details(item_code)`

Get item details including stock, last selling rate, last purchase rate, and supplier.

**Parameters:**

-   `item_code` (str): Item code

**Returns:**

-   Dict with: `item_code`, `stock_qty`, `last_selling_rate`, `last_purchase_rate`, `supplier`

**Example:**

```python
details = frappe.call({
    method: 'power_app.item.get_item_details',
    args: { item_code: 'ITEM-001' }
})
```

---

### Supplier Quotation Module (`power_app.supplier_quotation`)

#### `check_quotation_linked(doc)`

Check if Supplier Quotation is linked to Customer Quotation via Material Request.

**Parameters:**

-   `doc` (str): Supplier Quotation name

**Returns:**

-   Quotation name if linked, None otherwise

**Example:**

```python
quotation = frappe.call({
    method: 'power_app.supplier_quotation.check_quotation_linked',
    args: { doc: 'SQ-00001' }
})
```

---

#### `update_quotation_linked(doc, q)`

Update Customer Quotation with items and rates from Supplier Quotation.

**Parameters:**

-   `doc` (str): Supplier Quotation name
-   `q` (str): Customer Quotation name

**Returns:**

-   Updated Quotation document

**Example:**

```python
frappe.call({
    method: 'power_app.supplier_quotation.update_quotation_linked',
    args: { doc: 'SQ-00001', q: 'QUO-00001' }
})
```

---

### Mapper Module (`power_app.mapper`)

#### `make_material_request_from_quotation(source, target)`

Create Material Request from Quotation.

**Parameters:**

-   `source` (str): Quotation name
-   `target` (str, optional): Existing Material Request name

**Returns:**

-   Material Request document

**Example:**

```javascript
frappe.model.open_mapped_doc({
	method: 'power_app.mapper.make_material_request_from_quotation',
	frm: frm,
});
```

---

## Document Events

### Quotation Events

#### `on_update`

**Handler:** `power_app.quotation.quotation_update`

**Functionality:**

-   Calculates expense allocation to items
-   Applies item margins
-   Updates item rates

---

### Sales Order Events

#### `before_save`

**Handler:** `power_app.sales_order.copy_quotation_expenses_to_sales_order`

**Functionality:**

-   Copies `custom_quotation_expenses` from Quotation to Sales Order

#### `on_submit`

**Handler:** `power_app.sales_order.create_je_from_service_expence`

**Functionality:**

-   Creates Journal Entry for service expenses
