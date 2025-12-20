# Power App

Implementation - Step by Step Plan (User-Guided)

## Overview

This plan provides step-by-step instructions. You will:

-   Perform JSON modifications yourself (after approval prompts)
-   Review code changes before implementation
-   Test each step before proceeding
-   Follow AGENTS.md rules (especially JSON modification protocol)

**Workflow:** Customer Quotation → Material Request → RFQ → Supplier Quotations → Item Selection → Expense Allocation---

## Step 1: Add Custom Fields to Quotation Item

**What You Need to Do:**

1. **I will show you the JSON structure** for the custom fields
2. **You will add these fields** to `power_app/custom/quotation_item.json`
3. **I will provide the exact field definitions** - you copy them into the JSON file

**Custom Fields to Add:**

-   `custom_supplier_quotation` (Link to Supplier Quotation)
-   `custom_supplier_quotation_item` (Data)
-   `custom_supplier_rate` (Currency)
-   `custom_original_rate` (Currency)
-   `custom_expense_amount` (Currency)
-   `custom_final_rate` (Currency, read-only)

**⚠️ JSON Modification Required:**

-   File: `power_app/custom/quotation_item.json`
-   Action: Add 6 custom field definitions to the fields array
-   Impact: New fields will appear in Quotation Item form and table

**After You Add Fields:**

-   Run: `bench --site all clear-cache`
-   Test: Create a Quotation, verify fields appear in items table

**Next Step:** Step 2---

## Step 2: Create get_supplier_quotation_items() Method

**What I Will Do:**

-   Add new method to `power_app/customization.py`
-   Method fetches supplier quotation items via Material Request

**What You Need to Do:**

1. Review the code I provide
2. I will add the method to the file
3. Test the method via API call

**Method Details:**

-   Name: `get_supplier_quotation_items(quotation_name)`
-   Returns: List of supplier quotation items with supplier details
-   Links via: Material Request → Supplier Quotation Items

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Call method via API, verify it returns correct items

**Next Step:** Step 3---

## Step 3: Add "Compare Supplier Quotations" Button

**What I Will Do:**

-   Add button code to `power_app/public/js/quotation.js`
-   Button opens ERPNext's comparison report

**What You Need to Do:**

1. Review the JavaScript code I provide
2. I will add it to the file
3. Test the button functionality

**Button Details:**

-   Location: Quotation form (refresh function)
-   Action: Opens "Supplier Quotation Comparison" report
-   Visibility: Only when quotation is in Draft status

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Click button, verify report opens

**Next Step:** Step 4---

## Step 4: Create Item Selection Dialog (UI Only)

**What I Will Do:**

-   Add dialog function to `power_app/public/js/quotation.js`
-   Dialog displays supplier quotation items in table format

**What You Need to Do:**

1. Review the JavaScript code I provide
2. I will add it to the file
3. Test the dialog displays correctly

**Dialog Details:**

-   Triggered by: "Select Items from Supplier Quotations" button
-   Shows: Item Code, Supplier Name, Rate
-   Functionality: Display only (no selection yet)

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Click button, verify dialog opens and shows items

**Next Step:** Step 5---

## Step 5: Add Multi-Select to Item Selection Dialog

**What I Will Do:**

-   Add checkboxes to dialog table
-   Add selection tracking logic
-   Add "Add Selected Items" button (disabled initially)

**What You Need to Do:**

1. Review the JavaScript code I provide
2. I will add it to the file
3. Test multi-select functionality

**Functionality:**

-   Checkboxes for each item
-   Track selected items
-   "Add Selected Items" button (will be enabled in Step 7)

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Select items, verify selection tracked

**Next Step:** Step 6---

## Step 6: Create add_items_from_supplier_quotations() Method

**What I Will Do:**

-   Add new method to `power_app/customization.py`
-   Method adds selected items to Customer Quotation

**What You Need to Do:**

1. Review the Python code I provide
2. I will add the method to the file
3. Test the method via API call

**Method Details:**

-   Name: `add_items_from_supplier_quotations(quotation_name, selected_items)`
-   Action: Adds items from supplier quotations to customer quotation
-   Sets: supplier_quotation, supplier_rate, original_rate fields

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Call method via API, verify items added correctly

**Next Step:** Step 7---

## Step 7: Connect Dialog to add_items_from_supplier_quotations()

**What I Will Do:**

-   Enable "Add Selected Items" button
-   Connect button to server method
-   Add form reload after items added

**What You Need to Do:**

1. Review the JavaScript code I provide
2. I will add it to the file
3. Test complete item selection flow

**Functionality:**

-   Collect selected items from dialog
-   Call `add_items_from_supplier_quotations()` method
-   Reload quotation form
-   Close dialog

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Select items, click button, verify items added to quotation

**Next Step:** Step 8---

## Step 8: Move quotation_update() to validate Event

**What I Will Do:**

-   Update `power_app/hooks.py` - Change event from `on_update` to `validate`
-   This fixes recursion issue

**What You Need to Do:**

1. Review the hook change I provide
2. I will update the file
3. Test that rate calculation still works

**Change Details:**

-   File: `power_app/hooks.py`
-   Change: `"on_update"` → `"validate"` for quotation_update
-   Reason: Prevents recursion when modifying items during update

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Add expenses, verify rates update without recursion

**Next Step:** Step 9---

## Step 9: Update quotation_update() - Handle Supplier Rates

**What I Will Do:**

-   Update `quotation_update()` function in `power_app/customization.py`
-   Use supplier rates as base for expense distribution
-   Preserve original rates

**What You Need to Do:**

1. Review the code changes I provide
2. I will update the function
3. Test expense distribution with supplier rates

**Changes:**

-   Check if item has `custom_supplier_rate`
-   Use supplier rate as base (instead of current rate)
-   Store original rate in `custom_original_rate`
-   Calculate expenses based on supplier rates

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Add items from supplier quotations, add expenses, verify distribution

**Next Step:** Step 10---

## Step 10: Remove Manual Commits from quotation_update()

**What I Will Do:**

-   Remove `frappe.db.commit()` calls from `quotation_update()` function
-   Let Frappe handle transactions automatically

**What You Need to Do:**

1. Review the code changes I provide
2. I will remove the commit calls
3. Test that functionality still works

**Changes:**

-   Remove line 164: `frappe.db.commit()`
-   Remove line 175: `frappe.db.commit()`
-   Reason: Frappe handles transactions automatically

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Verify functionality still works without manual commits

**Next Step:** Step 11---

## Step 11: Calculate and Display Final Rate

**What I Will Do:**

-   Update `quotation_update()` to calculate `custom_final_rate`
-   Update main `rate` field with final rate

**What You Need to Do:**

1. Review the code changes I provide
2. I will update the function
3. Test final rate calculation

**Calculation:**

-   `custom_final_rate = custom_supplier_rate + expense_per_unit`
-   Update `rate` field with final rate
-   Apply margin if set

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Add items and expenses, verify final rate calculated correctly

**Next Step:** Step 12---

## Step 12: Enhance Price Breakdown Display

**What You Need to Do:**

1. **I will show you which fields need to be visible** in the Quotation Item table
2. **You will modify** `power_app/custom/quotation_item.json` to make fields visible
3. **I will provide instructions** on which fields to show in list view

**⚠️ JSON Modification Required:**

-   File: `power_app/custom/quotation_item.json`
-   Action: Set `in_list_view: 1` for custom fields
-   Impact: Fields will appear in Quotation Item table columns

**Fields to Make Visible:**

-   `custom_supplier_quotation`
-   `custom_supplier_rate`
-   `custom_original_rate`
-   `custom_expense_amount`
-   `custom_final_rate`

**After You Make Fields Visible:**

-   Run: `bench --site all clear-cache`
-   Test: View quotation items, verify all fields visible

**Next Step:** Step 13 (Optional)---

## Step 13: Enhance Comparison Report Integration (Optional)

**What I Will Do:**

-   Enhance button functionality in `power_app/public/js/quotation.js`
-   Add pre-filtering for comparison report

**What You Need to Do:**

1. Review the JavaScript code I provide
2. I will add it to the file
3. Test report filtering

**Enhancement:**

-   Pre-filter report by Material Request
-   Improve report link functionality

**After Implementation:**

-   Run cache clearing commands (I will provide them)
-   Test: Click button, verify report shows correct data

---

## Step 14: Implement Approved Workflow for Quotation Submit

**Status:** ✅ **COMPLETED**

**What Was Done:**

1. **Python Changes:**

    - Updated `quotation_before_submit()` in `power_app/quotation.py`
    - Now allows Submit only if `custom_approved` checkbox is checked
    - Throws error if trying to submit without approval

2. **JavaScript Changes:**

    - Updated `refresh()` function in `power_app/public/js/quotation.js`
    - Shows/hides Submit button based on `custom_approved` checkbox
    - When `custom_approved = 1`: Submit button is visible
    - When `custom_approved = 0`: Submit button is hidden

3. **Read-Only View for Submitted Quotations:**

    - Added `show_item_selection_dialog_readonly()` function
    - Added `build_supplier_items_table_html_readonly()` function
    - Modified `add_select_items_from_supplier_quotations_button()`:
        - Draft (docstatus = 0): Shows "Select Items from Supplier Quotations" with full functionality
        - Submitted (docstatus = 1): Shows "View Supplier Quotation Items" (read-only, no Add button)

4. **Hooks Updated:**
    - `before_submit` event registered in `power_app/hooks.py`

**What You Need to Do:**

1. **⚠️ JSON Modification Required:**

    - File: `power_app/power_app/custom/quotation.json`
    - Action: Add `custom_approved` field (Checkbox type)
    - Field Details:
        - `fieldname`: `custom_approved`
        - `fieldtype`: `Check`
        - `label`: `Approved`
        - `insert_after`: `custom_item_margin`
        - `default`: `0`
        - `idx`: `31`

2. **After Adding Field:**
    - Run: `bench --site all clear-cache`
    - Test:
        - Create Quotation
        - Verify Approved checkbox appears
        - Check Approved → Verify Submit button appears
        - Uncheck Approved → Verify Submit button hides
        - Try to Submit without Approved → Should show error
        - Submit with Approved → Should work
        - After Submit → Verify "View Supplier Quotation Items" button appears (read-only)

**Workflow Summary:**

```
Quotation (Draft)
├── Add Items from Supplier Quotations ✅ (Full functionality)
├── Add Expenses ✅
├── Check Approved ✅
├── Submit ✅ (Only if Approved = 1)
└── Quotation (Submitted)
    ├── View Supplier Quotation Items ✅ (Read-only)
    └── Create Sales Order ✅ (Standard ERPNext button)
```

**Status:** ✅ **COMPLETED - Approved field added by user**

**Next Step:** Testing and validation

---

## Step 15: Simplify Code - Remove custom*sq*\* Fields

**Status:** ✅ **COMPLETED**

**What Was Done:**

1. **Simplified `add_items_from_supplier_quotations()`:**

    - Removed complex logic for custom*sq*\* fields
    - Simple logic: Copy current `rate` to `custom_original_rate`, then update `rate` with supplier rate
    - Only updates: `custom_original_rate`, `rate`, `custom_supplier_quotation`

2. **Simplified `quotation_validate()`:**

    - Removed all references to `custom_sq_rate`, `custom_sq_net_rate`, `custom_sq_amount`, `custom_sq_net_amount`
    - Uses current `rate` and `amount` fields directly
    - Expense distribution based on current item amounts
    - Margin applied to current rates

3. **Updated Documentation:**
    - Removed custom*sq*\* fields from `power_app_workflow.md`
    - Updated field references

**Result:** Code is now simpler and easier to maintain.

---

## Step 16: Unified Logging Implementation

**Status:** ✅ **COMPLETED**

**What Was Done:**

1. **Frontend Logging (JavaScript):**

    - Updated all `console.log` statements to unified format: `console.log('[filename.js] (message)')`
    - Removed `console.error`, `console.info`, `console.warn` usage
    - Added logging to key functions in:
        - `quotation.js` - Item selection, supplier items fetching, errors
        - `supplier_quotation.js` - Quotation linking, updates

2. **Backend Logging (Python):**

    - Added `frappe.log_error()` to all key functions
    - Format: `frappe.log_error(f"[filename.py] function_name: message")`
    - Added logging to:
        - `quotation.py` - All functions
        - `sales_order.py` - Expense copying and Journal Entry creation
        - `material_request.py` - Material Request creation
        - `supplier_quotation.py` - Quotation linking and updates
        - `item.py` - Item details fetching

3. **Logging Guidelines:**
    - Short, important results only
    - No long arrays or full objects
    - Filename included in brackets
    - Function name included when relevant

**Result:** Unified logging across all files for easier debugging.

---

## Step 17: Landed Cost Voucher Override for Service Items

**Status:** ✅ **COMPLETED**

**What Was Done:**

1. **Created `landed_cost_voucher.py`:**

    - Extended `LandedCostVoucher` class to support Service Items
    - Override `get_items_from_purchase_receipts()` method
    - Created `get_pr_items_extended()` function that includes Service Items

2. **Updated `hooks.py`:**

    - Added `override_doctype_class` configuration
    - Registered override: `"Landed Cost Voucher": "power_app.landed_cost_voucher.LandedCostVoucher"`

3. **Safety Analysis:**
    - Verified that `update_stock_ledger()` automatically skips non-stock items (safe)
    - Verified that `update_valuation_rate()` automatically skips non-stock items (safe)
    - Verified that `make_gl_entries()` handles service items correctly (safe)

**Result:** Landed Cost Voucher now supports Service Items in addition to Stock Items and Fixed Assets.

**Note:** Service Expense Table in Quotation is still required because:

-   It's used at Quotation stage (before purchase)
-   Landed Cost Voucher is used after Purchase Receipt (after purchase)
-   Both serve different purposes in the workflow

---

## Step 18: Real-time Expense Recalculation

**Status:** ✅ **COMPLETED**

**What Was Done:**

1. **Added Event Handlers in `quotation.js`:**

    - `frappe.ui.form.on('Service Expense', ...)` handlers
    - `amount` - Triggers recalculation when expense amount changes
    - `custom_quotation_expenses_table_add` - Triggers when expense row added
    - `custom_quotation_expenses_table_remove` - Triggers when expense row removed

2. **Debounce Mechanism:**

    - Added `trigger_expense_recalculation()` function with 500ms debounce
    - Prevents multiple saves when user makes rapid changes
    - Uses `is_recalculating` flag to prevent recursion

3. **Auto-save Logic:**
    - When expense is modified/deleted, automatically saves (silent)
    - Triggers `validate` event which recalculates rates
    - Reloads form to show updated rates

**Result:** Rates update automatically when expenses are added, modified, or deleted (after 500ms delay).

---

## Implementation Checklist

-   [x] Step 1: Add Custom Fields (You do JSON modification)
-   [x] Step 2: Create get_supplier_quotation_items() Method (I add code)
-   [x] Step 3: Add Compare Button (I add code)
-   [x] Step 4: Create Item Selection Dialog UI (I add code)
-   [x] Step 5: Add Multi-Select (I add code)
-   [x] Step 6: Create add_items_from_supplier_quotations() Method (I add code)
-   [x] Step 7: Connect Dialog to Method (I add code)
-   [x] Step 8: Move quotation_update to validate (I update hook)
-   [x] Step 9: Handle Supplier Rates (I update function)
-   [x] Step 10: Remove Manual Commits (I remove code)
-   [x] Step 11: Calculate Final Rate (I update function)
-   [x] Step 14: Implement Approved Workflow (I add code, You add JSON field)
-   [x] Step 15: Simplify Code - Remove custom*sq*\* fields (I simplify code)
-   [x] Step 16: Unified Logging Implementation (I add logging to all files)
-   [x] Step 17: Landed Cost Voucher Override for Service Items (I add override class)
-   [x] Step 18: Real-time Expense Recalculation (I add auto-save on expense changes)
