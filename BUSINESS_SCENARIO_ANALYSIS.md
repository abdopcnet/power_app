# Business Scenario Analysis & Solution Proposal

## Business Context

You are a **service/intermediary company** that:

-   Receives customer requests for items (stock) or services (non-stock)
-   Doesn't hold inventory - acts as a middleman
-   Searches the market to find suppliers
-   Incurs expenses (transportation, communication, etc.)
-   Collects multiple supplier quotations
-   Compares supplier quotations
-   Selects best items/prices from supplier quotations
-   Adds selected items to customer quotation with proper pricing

## Current System Analysis

### What Power App Currently Does

1. ✅ **Expense Management**: Can add expenses to quotations
2. ✅ **Expense Distribution**: Distributes expenses proportionally to items
3. ✅ **Supplier Quotation Sync**: Can update customer quotation from supplier quotation
4. ✅ **Comparison Tool**: Can use ERPNext's built-in "Supplier Quotation Comparison" report
5. ⚠️ **Manual Selection**: No easy way to select items from multiple supplier quotations

### What's Missing

1. ✅ **Supplier Quotation Comparison Report**: ERPNext has built-in "Supplier Quotation Comparison" report (may need enhancement to filter by Customer Quotation)
2. ❌ **Item Selection Interface**: Need easy way to select items from supplier quotations and add to customer quotation
3. ❌ **Price Breakdown Display**: Need to show original price, supplier price, expenses, final price in Quotation Item table
4. ❌ **Multi-Supplier Selection**: Need to select items from different supplier quotations in one action
5. ❌ **Expense Tracking per Item**: Need to track which expenses apply to which items

## Proposed Solution - Professional Workflow

### Phase 1: Standard ERPNext Workflow (Foundation)

**Selected Workflow: Standard ERPNext Flow with Material Request**

```
1. Customer Quotation (Draft)
   ↓
2. Material Request (from Quotation)
   ↓
3. Request for Quotation (RFQ) - Send to multiple suppliers
   ↓
4. Supplier Quotations (Multiple) - Suppliers respond
   ↓
5. Supplier Quotation Comparison Report - Compare all quotes
   ↓
6. Select Items from Supplier Quotations
   ↓
7. Update Customer Quotation with selected items
   ↓
8. Add Expenses (transportation, etc.)
   ↓
9. Submit Customer Quotation
   ↓
10. Sales Order → Delivery Note → Sales Invoice
```

**Why This Workflow:**

-   ✅ Uses standard ERPNext workflow (maintainable and upgrade-safe)
-   ✅ Material Request provides proper linking between Customer Quotation and Supplier Quotations
-   ✅ RFQ allows sending requests to multiple suppliers systematically
-   ✅ Full traceability: Can track from Customer Quotation → Material Request → RFQ → Supplier Quotations
-   ✅ Supports ERPNext's built-in comparison report
-   ✅ Current Power App already implements this approach

### Phase 2: Enhanced Features (Power App Customizations)

#### Feature 1: Enhanced Supplier Quotation Comparison Report

**Location:** ERPNext Built-in Report (with enhancements)

**Current Status:**

-   ✅ ERPNext has built-in "Supplier Quotation Comparison" report
-   ✅ Can compare supplier quotations by item
-   ✅ Shows supplier, rate, amount, valid till, lead time

**Enhancements Needed:**

-   Add filter to show supplier quotations linked to specific Customer Quotation
-   Add direct link/button from Customer Quotation form to open comparison report
-   Optionally: Add custom columns showing expense allocation and final rates

**Implementation:**

-   Use ERPNext's existing "Supplier Quotation Comparison" report
-   Add custom filter parameter for Customer Quotation
-   Add button in Customer Quotation form to open report with pre-filled filters

#### Feature 2: Item Selection Interface

**Location:** Custom Dialog/Page accessible from Customer Quotation

**Functionality:**

-   Shows all items from all supplier quotations linked to Customer Quotation
-   For each item, shows:
    -   Item Code
    -   Supplier Name
    -   Supplier Quotation Number
    -   Supplier Rate
    -   Original Customer Quotation Rate (if exists)
    -   Expense Amount (if allocated)
    -   Final Rate (Supplier Rate + Expenses)
-   Allows multi-select
-   "Add Selected Items" button

**Implementation:**

-   Custom JavaScript dialog
-   Server-side method to fetch supplier quotation items
-   Server-side method to add items to customer quotation

#### Feature 3: Enhanced Quotation Item Display

**Custom Fields on Quotation Item:**

-   `custom_supplier_quotation` (Link to Supplier Quotation)
-   `custom_supplier_quotation_item` (Link to Supplier Quotation Item)
-   `custom_supplier_rate` (Currency) - Rate from supplier
-   `custom_original_rate` (Currency) - Original rate before supplier update
-   `custom_expense_amount` (Currency) - Expenses allocated to this item
-   `custom_final_rate` (Currency) - Final rate (supplier + expenses)

**Display Logic:**

-   Show these fields in Quotation Item table
-   Calculate `custom_final_rate = custom_supplier_rate + custom_expense_amount`
-   Update main `rate` field with `custom_final_rate`

#### Feature 4: Expense Allocation per Item

**Current System:** Expenses distributed proportionally to all items

**Enhanced System:**

-   Option to allocate expenses to specific items
-   Or keep proportional distribution
-   Track which expenses apply to which items

**Implementation:**

-   Add `custom_expense_allocation_method` field (Proportional / Manual)
-   If Manual: Add expense allocation table linking expenses to items
-   If Proportional: Use current logic

## Detailed Workflow Implementation

### Step 1: Customer Requests Quotation

**Action:**

1. Create Customer Quotation
2. Add items (can be stock or service items)
3. Set initial rates (if known) or leave blank
4. Save as Draft

**System State:**

-   Quotation status: Draft
-   Items have initial rates (if set)
-   No supplier quotations linked yet

### Step 2: Create Material Request

**Action:**

1. Submit Customer Quotation
2. Click "Create > Material Request" (button added by Power App)
3. Material Request created with items from Quotation

**System State:**

-   Material Request linked to Customer Quotation via `custom_dc_refrance` field
-   Material Request Type: "Purchase"
-   Items ready to be sent to suppliers via RFQ

**Implementation:**

-   Power App already has `make_material_request_from_quotation()` function
-   Maps Quotation Items → Material Request Items
-   Sets `custom_dc_refrance` to link back to Customer Quotation

### Step 3: Create Request for Quotation (RFQ)

**Action:**

1. Open Material Request
2. Click "Create > Request for Quotation" (standard ERPNext button)
3. RFQ created with items from Material Request
4. Add multiple suppliers to RFQ
5. Send RFQ to suppliers (via portal or manually)

**System State:**

-   RFQ linked to Material Request
-   Multiple suppliers added
-   RFQ sent to suppliers for response

**System State:**

-   RFQ sent to multiple suppliers
-   Suppliers can respond via portal or manually

### Step 4: Receive Supplier Quotations

**Action:**

1. Suppliers create Supplier Quotations
2. Link to Material Request or RFQ (standard ERPNext linking)
3. Submit Supplier Quotations

**System State:**

-   Multiple Supplier Quotations exist
-   All linked to same Material Request (via `material_request` field in Supplier Quotation Item)
-   All linked to same RFQ (via `request_for_quotation` field in Supplier Quotation Item)
-   Can be compared using ERPNext's "Supplier Quotation Comparison" report

### Step 5: Compare Supplier Quotations

**Action:**

1. Open Customer Quotation
2. Click "Compare Supplier Quotations" button
3. View comparison report/dialog
4. See all suppliers, rates, terms

**System State:**

-   Comparison view shows all options
-   User can see best prices
-   User can see supplier details

### Step 6: Select Items from Supplier Quotations

**Action:**

1. Click "Select Items from Supplier Quotations" button
2. Dialog opens showing:
    - All items from all supplier quotations
    - Grouped by item_code
    - Shows supplier, rate, etc.
3. Select items (can select same item from different suppliers)
4. Click "Add to Quotation"

**System Logic:**

```python
def add_items_from_supplier_quotations(quotation_name, selected_items):
    """
    selected_items = [
        {
            "item_code": "ITEM-001",
            "supplier_quotation": "SQ-0001",
            "supplier_quotation_item": "sq_item_123",
            "rate": 100.00
        },
        ...
    ]
    """
    quotation = frappe.get_doc("Quotation", quotation_name)

    for item_data in selected_items:
        sq_item = frappe.get_doc(
            "Supplier Quotation Item",
            item_data["supplier_quotation_item"]
        )

        # Check if item already exists in quotation
        existing_item = None
        for q_item in quotation.items:
            if q_item.item_code == item_data["item_code"]:
                existing_item = q_item
                break

        if existing_item:
            # Update existing item
            existing_item.custom_original_rate = existing_item.rate
            existing_item.custom_supplier_quotation = item_data["supplier_quotation"]
            existing_item.custom_supplier_quotation_item = item_data["supplier_quotation_item"]
            existing_item.custom_supplier_rate = item_data["rate"]
            existing_item.rate = item_data["rate"]  # Will be updated after expense allocation
        else:
            # Add new item
            new_item = quotation.append("items", {
                "item_code": sq_item.item_code,
                "item_name": sq_item.item_name,
                "qty": sq_item.qty,
                "uom": sq_item.uom,
                "rate": item_data["rate"],
                "custom_supplier_quotation": item_data["supplier_quotation"],
                "custom_supplier_quotation_item": item_data["supplier_quotation_item"],
                "custom_supplier_rate": item_data["rate"],
                "custom_original_rate": 0,  # New item, no original rate
            })

    quotation.save()
    return quotation
```

### Step 7: Add Expenses

**Action:**

1. Add expenses to `custom_quotation_expenses` table
2. System distributes expenses to items
3. Updates item rates

**System Logic:**

```python
def quotation_update(doc, method):
    # Preserve supplier rates
    for item in doc.items:
        if not item.custom_supplier_rate:
            # If no supplier rate, use current rate as original
            if not item.custom_original_rate:
                item.custom_original_rate = item.rate
        else:
            # Supplier rate exists, use it as base
            item.rate = item.custom_supplier_rate

    # Calculate total expenses
    total_expenses = sum(exp.amount for exp in doc.custom_quotation_expenses)

    # Calculate total item amounts (using supplier rates)
    total_item_amount = sum(
        (item.custom_supplier_rate or item.rate) * item.qty
        for item in doc.items
    )

    # Distribute expenses proportionally
    if total_item_amount > 0:
        for item in doc.items:
            base_rate = item.custom_supplier_rate or item.rate
            base_amount = base_rate * item.qty

            # Calculate expense share
            expense_share = (base_amount / total_item_amount) * total_expenses
            expense_per_unit = expense_share / item.qty if item.qty > 0 else 0

            # Update item
            item.custom_expense_amount = expense_share
            item.custom_final_rate = base_rate + expense_per_unit
            item.rate = item.custom_final_rate
            item.amount = item.rate * item.qty

    # Apply margin if set
    if doc.custom_item_margin:
        for item in doc.items:
            item.rate = item.rate * (1 + doc.custom_item_margin / 100)
            item.amount = item.rate * item.qty
```

### Step 8: Display Price Breakdown

**Quotation Item Table Columns:**

1. Item Code
2. Item Name
3. Qty
4. UOM
5. **Original Rate** (custom_original_rate) - Rate before supplier update
6. **Supplier Quotation** (custom_supplier_quotation) - Link to SQ
7. **Supplier Rate** (custom_supplier_rate) - Rate from supplier
8. **Expense Amount** (custom_expense_amount) - Expenses allocated
9. **Final Rate** (custom_final_rate) - Supplier Rate + Expenses
10. **Rate** (rate) - Final rate (after margin if applied)
11. Amount

**Display Logic:**

-   Show all fields in table
-   Calculate `custom_final_rate` automatically
-   Update `rate` field with final rate

## Technical Implementation Plan

### 1. Custom Fields to Add

**Quotation Item:**

```json
{
  "fieldname": "custom_supplier_quotation",
  "fieldtype": "Link",
  "options": "Supplier Quotation",
  "label": "Supplier Quotation"
},
{
  "fieldname": "custom_supplier_quotation_item",
  "fieldtype": "Data",
  "label": "Supplier Quotation Item ID"
},
{
  "fieldname": "custom_supplier_rate",
  "fieldtype": "Currency",
  "label": "Supplier Rate",
  "options": "currency"
},
{
  "fieldname": "custom_original_rate",
  "fieldtype": "Currency",
  "label": "Original Rate",
  "options": "currency"
},
{
  "fieldname": "custom_expense_amount",
  "fieldtype": "Currency",
  "label": "Expense Amount",
  "options": "currency"
},
{
  "fieldname": "custom_final_rate",
  "fieldtype": "Currency",
  "label": "Final Rate",
  "options": "currency",
  "read_only": 1
}
```

### 2. JavaScript Enhancements

**quotation.js:**

```javascript
frappe.ui.form.on('Quotation', {
	refresh(frm) {
		// Add "Compare Supplier Quotations" button
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Compare Supplier Quotations'), function () {
				show_supplier_quotation_comparison(frm);
			});

			frm.add_custom_button(__('Select Items from Supplier Quotations'), function () {
				show_item_selection_dialog(frm);
			});
		}
	},
});

function show_supplier_quotation_comparison(frm) {
	// Open comparison report filtered by this quotation
	frappe.set_route('query-report', 'Supplier Quotation Comparison', {
		quotation: frm.doc.name,
	});
}

function show_item_selection_dialog(frm) {
	frappe.call({
		method: 'power_app.customization.get_supplier_quotation_items',
		args: {
			quotation_name: frm.doc.name,
		},
		callback: function (r) {
			if (r.message) {
				show_item_selection_dialog_content(frm, r.message);
			}
		},
	});
}
```

### 3. Server-Side Methods

**customization.py:**

```python
@frappe.whitelist()
def get_supplier_quotation_items(quotation_name):
    """
    Get all items from supplier quotations linked to this customer quotation

    Linking method: Via Material Request
    1. Customer Quotation → Material Request (via custom_dc_refrance)
    2. Material Request → Supplier Quotation Items (via material_request field)
    """
    # Get Material Request linked to Customer Quotation
    mr_list = frappe.get_all(
        "Material Request",
        filters={"custom_dc_refrance": quotation_name},
        fields=["name"]
    )

    if not mr_list:
        return []

    mr_names = [mr.name for mr in mr_list]

    # Get all Supplier Quotation Items linked to these Material Requests
    sq_items = frappe.get_all(
        "Supplier Quotation Item",
        filters={
            "material_request": ["in", mr_names],
            "docstatus": 1
        },
        fields=[
            "name",
            "parent as supplier_quotation",
            "item_code",
            "item_name",
            "qty",
            "uom",
            "rate",
            "amount",
            "material_request"
        ]
    )

    if not sq_items:
        return []
        fields=[
            "name",
            "parent as supplier_quotation",
            "item_code",
            "item_name",
            "qty",
            "uom",
            "rate",
            "amount"
        ],
        order_by="item_code, rate"
    )

    # Get supplier names
    for item in sq_items:
        sq_doc = frappe.get_doc("Supplier Quotation", item["supplier_quotation"])
        item["supplier"] = sq_doc.supplier
        item["supplier_name"] = sq_doc.supplier_name
        item["valid_till"] = sq_doc.valid_till

    return sq_items

@frappe.whitelist()
def add_items_from_supplier_quotations(quotation_name, selected_items):
    """
    Add selected items from supplier quotations to customer quotation
    """
    quotation = frappe.get_doc("Quotation", quotation_name)

    # Parse selected items
    if isinstance(selected_items, str):
        selected_items = json.loads(selected_items)

    for item_data in selected_items:
        sq_item = frappe.get_doc(
            "Supplier Quotation Item",
            item_data["supplier_quotation_item"]
        )

        # Check if item exists
        existing_item = None
        for q_item in quotation.items:
            if (q_item.item_code == item_data["item_code"] and
                q_item.custom_supplier_quotation == item_data["supplier_quotation"]):
                existing_item = q_item
                break

        if existing_item:
            # Update existing
            existing_item.custom_original_rate = existing_item.rate
            existing_item.custom_supplier_rate = item_data["rate"]
            existing_item.rate = item_data["rate"]
        else:
            # Add new
            new_item = quotation.append("items", {
                "item_code": sq_item.item_code,
                "item_name": sq_item.item_name,
                "qty": sq_item.qty or 1,
                "uom": sq_item.uom,
                "rate": item_data["rate"],
                "custom_supplier_quotation": item_data["supplier_quotation"],
                "custom_supplier_quotation_item": item_data["supplier_quotation_item"],
                "custom_supplier_rate": item_data["rate"],
                "custom_original_rate": 0,
            })

    quotation.save()
    frappe.db.commit()

    return quotation.name
```

## Workflow Diagram

```
┌─────────────────────┐
│ Customer Quotation  │
│      (Draft)        │
└──────────┬──────────┘
           │
           │ Create Material Request
           ▼
┌─────────────────────┐
│  Material Request   │
└──────────┬──────────┘
           │
           │ Create RFQ
           ▼
┌─────────────────────┐
│ Request for Quotation│
│  (Multiple Suppliers)│
└──────────┬──────────┘
           │
           │ Suppliers Respond
           ▼
┌─────────────────────┐
│ Supplier Quotations │
│   (Multiple)        │
└──────────┬──────────┘
           │
           │ Compare & Select
           ▼
┌─────────────────────┐
│  Item Selection     │
│     Dialog          │
└──────────┬──────────┘
           │
           │ Add Selected Items
           ▼
┌─────────────────────┐
│ Customer Quotation  │
│  (Items Added)      │
└──────────┬──────────┘
           │
           │ Add Expenses
           ▼
┌─────────────────────┐
│ Customer Quotation  │
│ (Rates Updated)     │
└──────────┬──────────┘
           │
           │ Submit
           ▼
┌─────────────────────┐
│   Sales Order       │
└─────────────────────┘
```

## Benefits of This Approach

1. ✅ **Uses Standard ERPNext Workflow**: Material Request → RFQ → Supplier Quotation
2. ✅ **Leverages Built-in Features**: Uses ERPNext's comparison report
3. ✅ **Maintains Data Integrity**: Proper linking between documents
4. ✅ **Clear Price Breakdown**: Shows all price components
5. ✅ **Flexible Selection**: Can select items from multiple suppliers
6. ✅ **Proper Expense Tracking**: Expenses allocated correctly
7. ✅ **Audit Trail**: All changes tracked via document links

## Implementation Priority

### Phase 1 (Critical - Must Have)

1. Add custom fields to Quotation Item
2. Create `get_supplier_quotation_items()` method
3. Create `add_items_from_supplier_quotations()` method
4. Update `quotation_update()` to handle supplier rates
5. Add buttons to Quotation form

### Phase 2 (Important - Should Have)

1. Enhance comparison report
2. Create item selection dialog
3. Add price breakdown display
4. Improve expense allocation logic

### Phase 3 (Nice to Have)

1. Dashboard for quotation management
2. Automated supplier selection suggestions
3. Expense allocation per item (manual mode)

## Next Steps

1. Review this proposal
2. Confirm workflow matches your business needs
3. Prioritize features
4. Start implementation with Phase 1
5. Test with real data
6. Iterate based on feedback
