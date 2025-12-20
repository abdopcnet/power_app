# Landed Cost Voucher - Complete Analysis

## Overview

Landed Cost Voucher is an ERPNext document used to distribute additional costs (shipping, customs, handling, etc.) to items received via Purchase Receipt or Purchase Invoice. This analysis explains why manual row addition is not allowed and what conditions are required for the "Get Items From Purchase Receipts" button to work.

## Why Manual Row Addition is Not Allowed

### 1. Design Philosophy

Landed Cost Voucher items **MUST** be linked to actual Purchase Receipt/Invoice items. This ensures:

-   **Data Integrity**: Items in LCV must exist in source documents
-   **Traceability**: Every LCV item references a specific Purchase Receipt Item
-   **Validation**: System can verify item existence and prevent orphaned records

### 2. Code Enforcement

**Location:** `erpnext/erpnext/stock/doctype/landed_cost_voucher/landed_cost_voucher.py`

**Line 126:**

```python
if not item.receipt_document:
    frappe.throw(_("Item must be added using 'Get Items from Purchase Receipts' button"))
```

This validation **prevents** manual addition of items without proper Purchase Receipt linkage.

### 3. Child Table Field Configuration

**Location:** `erpnext/erpnext/stock/doctype/landed_cost_item/landed_cost_item.json`

**Key Fields are Read-Only:**

-   `item_code` - `read_only: 1` (Line 31)
-   `description` - `read_only: 1` (Line 45)
-   `receipt_document_type` - `read_only: 1` (Line 58)
-   `receipt_document` - `read_only: 1` (Line 69)
-   `qty` - `read_only: 1` (Line 84)
-   `rate` - `read_only: 1` (Line 93)
-   `amount` - `read_only: 1` (Line 105)
-   `purchase_receipt_item` - `read_only: 1` (Line 127)

**Editable Fields:**

-   `applicable_charges` - Editable only if `distribute_charges_based_on != 'Distribute Manually'` (Line 116)
-   `cost_center` - Editable (Line 132)

**Note:** `editable_grid: 1` (Line 6) allows editing existing rows, but **not adding new rows manually**.

## Conditions for "Get Items From Purchase Receipts" Button

### Prerequisites (Must be Completed First)

#### 1. Company Field

-   **Field:** `company` (Link: Company)
-   **Required:** Yes (`reqd: 1`)
-   **Location:** Main form
-   **Why:** Needed for currency and cost center defaults

#### 2. Purchase Receipts Table

-   **Field:** `purchase_receipts` (Table: Landed Cost Purchase Receipt)
-   **Required:** Yes (`reqd: 1`)
-   **Minimum:** At least 1 row must exist
-   **Location:** Before "Get Items" button

#### 3. Purchase Receipt Row Details

Each row in `purchase_receipts` table must have:

-   **`receipt_document_type`** (Select): "Purchase Receipt" or "Purchase Invoice"
-   **`receipt_document`** (Dynamic Link): Valid Purchase Receipt/Invoice name

### Validation Conditions (Checked When Button is Clicked)

#### JavaScript Validation (Client-Side)

**Location:** `landed_cost_voucher.js` - Line 73-86

```javascript
get_items_from_purchase_receipts() {
    if (!this.frm.doc.purchase_receipts.length) {
        frappe.msgprint(__("Please enter Purchase Receipt first"));
        return; // Stops execution
    }
    // ... continues to server call
}
```

**Condition:** `purchase_receipts.length > 0`

#### Server-Side Validation (Python)

**Location:** `landed_cost_voucher.py`

##### A. Mandatory Check (Line 96-98)

```python
def check_mandatory(self):
    if not self.get("purchase_receipts"):
        frappe.throw(_("Please enter Receipt Document"))
```

**Condition:** `purchase_receipts` table must have at least 1 row

##### B. Receipt Document Validation (Line 100-120)

```python
def validate_receipt_documents(self):
    for d in self.get("purchase_receipts"):
        # 1. Document must be Submitted
        docstatus = frappe.db.get_value(d.receipt_document_type, d.receipt_document, "docstatus")
        if docstatus != 1:
            frappe.throw("... must be submitted")

        # 2. If Purchase Invoice, must have update_stock = 1
        if d.receipt_document_type == "Purchase Invoice":
            update_stock = frappe.db.get_value("Purchase Invoice", d.receipt_document, "update_stock")
            if not update_stock:
                frappe.throw("... has no stock impact")
```

**Conditions:**

1. Purchase Receipt/Invoice must be **Submitted** (`docstatus = 1`)
2. If Purchase Invoice: `update_stock = 1` (must have stock impact)
3. Company must match: Purchase Receipt/Invoice company = LCV company

##### C. Item Filtering (Line 312-337)

```python
def get_pr_items(purchase_receipt):
    return (
        frappe.qb.from_(pr_item)
        .inner_join(item)
        .on(item.name == pr_item.item_code)
        .where(
            (pr_item.parent == purchase_receipt.receipt_document)
            & ((item.is_stock_item == 1) | (item.is_fixed_asset == 1))
        )
    )
```

**Conditions:**

-   Item must be **Stock Item** (`is_stock_item = 1`) **OR**
-   Item must be **Fixed Asset** (`is_fixed_asset = 1`)
-   Items that are neither stock items nor fixed assets are **excluded**

### Query Filters (For Purchase Receipt Selection)

**Location:** `landed_cost_voucher.js` - Line 10-30

```javascript
this.frm.fields_dict.purchase_receipts.grid.get_field('receipt_document').get_query = function (
	doc,
	cdt,
	cdn,
) {
	var filters = [
		[d.receipt_document_type, 'docstatus', '=', '1'], // Must be Submitted
		[d.receipt_document_type, 'company', '=', me.frm.doc.company], // Same company
	];

	if (d.receipt_document_type == 'Purchase Invoice') {
		filters.push(['Purchase Invoice', 'update_stock', '=', '1']); // Must update stock
	}

	if (!me.frm.doc.company) {
		frappe.msgprint(__('Please enter company first'));
	}

	return { filters: filters };
};
```

**Filters Applied:**

1. `docstatus = 1` (Submitted only)
2. `company = LCV.company` (Same company)
3. If Purchase Invoice: `update_stock = 1`

## Complete Workflow

### Step-by-Step Process

1. **Create Landed Cost Voucher (Draft)**

    - Enter `company` (required)
    - Enter `posting_date` (optional)

2. **Add Purchase Receipts**

    - Click "Add Row" in `purchase_receipts` table
    - Select `receipt_document_type`: "Purchase Receipt" or "Purchase Invoice"
    - Select `receipt_document`: Only shows:
        - Submitted documents (`docstatus = 1`)
        - Same company
        - If Purchase Invoice: `update_stock = 1`
    - Save row

3. **Get Items**

    - Click "Get Items From Purchase Receipts" button
    - System validates:
        - ✅ `purchase_receipts` table has rows
        - ✅ Each receipt document is Submitted
        - ✅ Company matches
        - ✅ Purchase Invoice has `update_stock = 1`
    - System fetches items:
        - Only items where `is_stock_item = 1` OR `is_fixed_asset = 1`
    - Items are added to `items` table with:
        - All fields populated from Purchase Receipt Item
        - `purchase_receipt_item` field set (hidden, read-only)
        - `receipt_document_type` and `receipt_document` set

4. **Add Charges**

    - Add rows to `taxes` table (Landed Cost Taxes and Charges)
    - Enter expense account and amount
    - Charges are automatically distributed to items

5. **Distribute Charges**

    - Select `distribute_charges_based_on`: "Qty", "Amount", or "Distribute Manually"
    - If not "Distribute Manually": Charges auto-calculated
    - If "Distribute Manually": Enter `applicable_charges` manually for each item

6. **Submit**
    - System validates:
        - All items have `receipt_document` reference
        - Total applicable charges = total taxes and charges
        - Cost center is set for each item
    - On submit: Updates Purchase Receipt items with landed cost

## Common Issues and Solutions

### Issue 1: "Please enter Purchase Receipt first"

**Cause:** `purchase_receipts` table is empty

**Solution:**

1. Add at least one row to `purchase_receipts` table
2. Select `receipt_document_type` and `receipt_document`
3. Save the row
4. Then click "Get Items From Purchase Receipts"

### Issue 2: Cannot select Purchase Receipt/Invoice

**Possible Causes:**

1. **Company not set:**

    - Set `company` field first
    - Query filter requires company

2. **Document not Submitted:**

    - Submit Purchase Receipt/Invoice first
    - Query filter: `docstatus = 1`

3. **Different Company:**

    - Purchase Receipt company ≠ LCV company
    - Query filter: `company = LCV.company`

4. **Purchase Invoice without stock impact:**
    - Purchase Invoice has `update_stock = 0`
    - Query filter: `update_stock = 1` (for Purchase Invoice only)

**Solution:** Check all conditions above

### Issue 3: Button works but no items appear

**Possible Causes:**

1. **No stock items or fixed assets:**

    - Purchase Receipt has only service items
    - Filter: `is_stock_item = 1` OR `is_fixed_asset = 1`
    - Service items (`is_stock_item = 0` and `is_fixed_asset = 0`) are excluded

2. **Empty Purchase Receipt:**
    - Purchase Receipt has no items
    - Check Purchase Receipt items table

**Solution:**

-   Verify Purchase Receipt has stock items or fixed assets
-   Check Purchase Receipt items table

### Issue 4: Cannot add rows manually to items table

**Cause:** By design - items must come from Purchase Receipts

**Solution:**

-   This is **intentional** - use "Get Items From Purchase Receipts" button
-   Manual addition is not supported

### Issue 5: "Item must be added using 'Get Items from Purchase Receipts' button"

**Cause:** Trying to add item manually or item missing `receipt_document`

**Solution:**

-   Use "Get Items From Purchase Receipts" button
-   Do not try to add rows manually
-   Ensure all items have `receipt_document` reference

## Technical Details

### Item Fetching Logic

**Function:** `get_pr_items(purchase_receipt)` (Line 312-337)

**Query:**

```python
SELECT
    pr_item.item_code,
    pr_item.description,
    pr_item.qty,
    pr_item.base_rate,
    pr_item.base_amount,
    pr_item.name AS purchase_receipt_item,
    pr_item.cost_center,
    pr_item.is_fixed_asset
FROM `tabPurchase Receipt Item` pr_item
INNER JOIN `tabItem` item ON item.name = pr_item.item_code
WHERE
    pr_item.parent = 'PR-00001'
    AND (item.is_stock_item = 1 OR item.is_fixed_asset = 1)
ORDER BY pr_item.idx
```

**Items Included:**

-   Stock items (`is_stock_item = 1`)
-   Fixed assets (`is_fixed_asset = 1`)

**Items Excluded:**

-   Service items (not stock, not fixed asset)
-   Items that don't exist in Item master

### Automatic Item Fetching

**Location:** `landed_cost_voucher.py` - Line 71-72

```python
if not self.get("items"):
    self.get_items_from_purchase_receipts()
```

**Behavior:** If `items` table is empty during `validate`, system automatically calls `get_items_from_purchase_receipts()`

**Note:** This happens on save, but button click is still recommended for user control

## Summary

### Why Manual Addition is Not Allowed

1. **Data Integrity:** Items must reference actual Purchase Receipt items
2. **Validation:** System validates item existence in source document
3. **Traceability:** Every LCV item links to specific Purchase Receipt Item
4. **Field Configuration:** Most fields are read-only, preventing manual entry

### Conditions for "Get Items" Button

**Prerequisites:**

1. ✅ Company field set
2. ✅ At least 1 row in `purchase_receipts` table
3. ✅ Each row has `receipt_document_type` and `receipt_document`

**Validation:**

1. ✅ Purchase Receipt/Invoice is Submitted (`docstatus = 1`)
2. ✅ Same company as LCV
3. ✅ If Purchase Invoice: `update_stock = 1`
4. ✅ Items are stock items or fixed assets

**Result:**

-   Items fetched and added to `items` table
-   All fields populated automatically
-   Items linked to Purchase Receipt Items via `purchase_receipt_item` field

## Intermediary Company Workflow in ERPNext

### Overview

For intermediary companies (trading/import companies), the workflow involves:

1. Getting customer agreement on quotation
2. Finding supplier quotations
3. Selecting best offers and items
4. Placing purchase orders
5. Adding expenses (landed costs)
6. Delivering to customer with added expenses

### Complete Workflow

#### Phase 1: Customer Quotation

1. **Create Customer Quotation**
    - Create Quotation for customer
    - Add items, rates, and terms
    - Submit Quotation (`docstatus = 1`)
    - Customer approves quotation

#### Phase 2: Material Request & Supplier Quotations

2. **Create Material Request**

    - **Standard ERPNext:** From Sales Order (after customer confirms order)
    - **Power App Extension:** From Quotation (for procurement planning)
    - Material Request links to Sales Order (Standard) or Quotation (Power App)
    - Material Request status: Draft → Submit
    - **Note:** In standard ERPNext workflow, Material Request is **NOT** part of Quotation workflow. It is created from Sales Order when materials need to be procured.

3. **Create Request for Quotation (RFQ)**

    - From Material Request, create RFQ
    - Send RFQ to multiple suppliers
    - RFQ links to Material Request

4. **Receive Supplier Quotations**

    - Suppliers submit Supplier Quotations
    - Each Supplier Quotation links to RFQ
    - Supplier Quotations status: Draft → Submit

5. **Compare Supplier Quotations**
    - Use "Supplier Quotation Comparison" report
    - Filter by RFQ/Material Request
    - Compare rates, terms, and conditions

#### Phase 3: Purchase Order

6. **Create Purchase Order**
    - From Supplier Quotation, create Purchase Order
    - Purchase Order links to:
        - Supplier Quotation (via `supplier_quotation` field)
        - Material Request (via `material_request` field)
    - Purchase Order status: Draft → Submit

#### Phase 4: Purchase Receipt & Landed Cost

7. **Receive Goods (Purchase Receipt)**

    - When goods arrive, create Purchase Receipt
    - Purchase Receipt links to Purchase Order
    - Purchase Receipt status: Draft → Submit
    - Stock is updated automatically

8. **Add Landed Costs**
    - Create Landed Cost Voucher
    - Link to Purchase Receipt(s)
    - Add expenses (shipping, customs, handling, etc.)
    - Click "Get Items From Purchase Receipts"
    - Distribute charges to items:
        - Based on Qty
        - Based on Amount
        - Distribute Manually
    - Submit Landed Cost Voucher
    - **Result:** Purchase Receipt item rates are updated with landed costs

#### Phase 5: Sales Order & Delivery

9. **Create Sales Order**

    - From Customer Quotation, create Sales Order
    - Sales Order links to Quotation
    - Sales Order status: Draft → Submit

10. **Create Delivery Note**

    - From Sales Order, create Delivery Note
    - Delivery Note links to Sales Order
    - Stock is reduced (goods delivered to customer)
    - Delivery Note status: Draft → Submit

11. **Create Sales Invoice**
    - From Sales Order or Delivery Note, create Sales Invoice
    - Sales Invoice links to Sales Order
    - Customer is billed
    - Sales Invoice status: Draft → Submit

### Key Points

#### Landed Cost Voucher Role

-   **Purpose:** Add additional costs to purchased items
-   **Timing:** After Purchase Receipt is submitted
-   **Effect:** Updates Purchase Receipt item valuation rates
-   **Distribution:** Charges distributed proportionally to items

#### Document Linking

```
Customer Quotation
    ↓
Material Request
    ↓
Request for Quotation (RFQ)
    ↓
Supplier Quotations (Multiple)
    ↓
Purchase Order (from selected Supplier Quotation)
    ↓
Purchase Receipt
    ↓
Landed Cost Voucher (adds expenses)
    ↓
Sales Order (from Customer Quotation)
    ↓
Delivery Note
    ↓
Sales Invoice
```

#### Expense Flow

1. **Purchase Side:**

    - Purchase Receipt: Base item cost
    - Landed Cost Voucher: Additional expenses
    - Final Cost = Base Cost + Landed Costs

2. **Sales Side:**
    - Sales Order: Customer price (includes margin)
    - Delivery Note: Physical delivery
    - Sales Invoice: Customer billing

#### Important Notes

-   **Landed Cost Voucher** is the standard ERPNext way to add expenses to purchased items
-   Expenses are distributed to items and update their valuation rates
-   This ensures accurate cost calculation and profit margins
-   All expenses must be added before creating Sales Order to ensure correct pricing

### Standard ERPNext Limitations

1. **No Direct Link:**

    - Landed Cost Voucher doesn't directly link to Customer Quotation
    - Expenses are added at Purchase Receipt level, not Quotation level

2. **Manual Process:**

    - Supplier quotation comparison is manual
    - Item selection from multiple supplier quotations is manual
    - No automatic selection of best offers

3. **Expense Timing:**
    - Expenses can only be added after Purchase Receipt
    - Cannot add expenses at Quotation stage for pricing

### Power App Enhancements

Power App extends ERPNext to support:

-   Selecting items from multiple supplier quotations at Quotation stage
-   Adding expenses at Quotation stage (before purchase)
-   Automatic expense distribution to items
-   Better supplier quotation comparison and selection

## Code References

-   **JavaScript:** `erpnext/erpnext/stock/doctype/landed_cost_voucher/landed_cost_voucher.js`
-   **Python:** `erpnext/erpnext/stock/doctype/landed_cost_voucher/landed_cost_voucher.py`
-   **DocType JSON:** `erpnext/erpnext/stock/doctype/landed_cost_voucher/landed_cost_voucher.json`
-   **Child Table JSON:** `erpnext/erpnext/stock/doctype/landed_cost_item/landed_cost_item.json`
