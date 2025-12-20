# Power App vs Original ERPNext - Key Differences

## Overview

This document highlights the key differences between Power App workflow and standard ERPNext workflow, specifically for intermediary service companies that need to manage expenses and supplier quotations.

---

## 1. Expense Management

### Original ERPNext Approach

**Location:** Purchase Side Only

-   **Landed Cost Voucher** is used to add expenses to purchased items
-   **Timing:** Expenses can only be added **after** Purchase Receipt is submitted
-   **Process:**
    1. Create Purchase Receipt from Purchase Order
    2. Submit Purchase Receipt
    3. Create Landed Cost Voucher
    4. Link to Purchase Receipt
    5. Add expenses (shipping, customs, handling, etc.)
    6. Submit Landed Cost Voucher
    7. **Result:** Purchase Receipt item valuation rates are updated

**Limitations:**

-   ❌ Cannot add expenses at Quotation stage
-   ❌ Expenses are unknown until goods are received
-   ❌ Cannot include expenses in customer quotation pricing upfront
-   ❌ Expenses are added to Purchase Receipt items, not Quotation items
-   ❌ Landed Cost Voucher only supports Stock Items and Fixed Assets (not Service Items)

**Reference:** `original_erpnext_workflow/landed_cost_voucher_analysis.md`

### Power App Approach

**Location:** Sales Side (Quotation Level)

-   **Custom Expense Table** (`custom_quotation_expenses_table`) is used
-   **Timing:** Expenses are added **at Quotation stage** (before purchase)
-   **Process:**
    1. Create Customer Quotation (Draft)
    2. Add expenses in `custom_quotation_expenses_table`
    3. On save (validate event), expenses are automatically distributed to items
    4. Expenses are included in item rates immediately
    5. Expenses are copied to Sales Order when created
    6. Journal Entry is created automatically on Sales Order submit

**Advantages:**

-   ✅ Expenses can be added at Quotation stage
-   ✅ Expenses are distributed to items automatically
-   ✅ Final rates include expenses upfront
-   ✅ Expenses flow from Quotation → Sales Order → Journal Entry
-   ✅ Real-time recalculation when expenses are modified/deleted

**Reference:** `app_expenses_workflow.md`

---

## 2. Expense Distribution

### Original ERPNext

**Method:** Landed Cost Voucher

-   Expenses are distributed based on:
    -   **Qty:** Proportional to item quantities
    -   **Amount:** Proportional to item amounts
    -   **Manual:** User enters charges per item manually
-   Distribution happens **after** Purchase Receipt
-   Updates Purchase Receipt item valuation rates

### Power App

**Method:** Automatic Distribution in Quotation

-   Expenses are distributed **proportionally based on item amounts**
-   Formula: `expense_per_item = (item_amount / total_item_amount) * total_expenses`
-   Distribution happens **on every save** (validate event)
-   Updates Quotation item rates immediately
-   Can apply margin after expense distribution

---

## 3. Intermediary Company Workflow

### Original ERPNext Workflow

**For Intermediary Companies (Trading/Import):**

```
1. Customer Quotation (Draft)
   ↓
2. Submit Quotation
   ↓
3. Create Sales Order
   ↓
4. Create Material Request (from Sales Order)
   ↓
5. Create RFQ
   ↓
6. Receive Supplier Quotations
   ↓
7. Create Purchase Order
   ↓
8. Receive Goods → Purchase Receipt
   ↓
9. Add Expenses → Landed Cost Voucher (AFTER receipt)
   ↓
10. Deliver to Customer → Delivery Note
   ↓
11. Bill Customer → Sales Invoice
```

**Key Points:**

-   Material Request is created **from Sales Order** (not from Quotation)
-   Expenses are added **after** Purchase Receipt
-   Expenses update Purchase Receipt valuation, not Quotation pricing

**Reference:** `original_erpnext_workflow/original_erpnext_sales_cycle_symmery.md` (Section: Intermediary Company Workflow)

### Power App Workflow

**For Intermediary Companies:**

```
1. Customer Quotation (Draft)
   ├── Create Material Request (from Quotation)
   ├── Create RFQ
   ├── Receive Supplier Quotations
   ├── Select Items from Supplier Quotations
   ├── Add Expenses (at Quotation level)
   ├── Expenses distributed to items automatically
   ├── Check Approved
   └── Submit (only if Approved = 1)
   ↓
2. Create Sales Order (from Submitted Quotation)
   ├── Expenses copied automatically
   └── Submit Sales Order
       └── Journal Entry created automatically
   ↓
3. Continue standard ERPNext flow
   ├── Delivery Note
   └── Sales Invoice
```

**Key Points:**

-   Material Request is created **from Quotation** (Draft status)
-   Expenses are added **at Quotation stage** (before purchase)
-   Expenses are distributed to items and included in pricing
-   Expenses flow through to Sales Order and Journal Entry

**Reference:** `app_workflow.md`

---

## 4. Quotation Submission Control

### Original ERPNext

-   Quotation can be submitted immediately (no approval required)
-   Status changes: Draft → Open (on submit)
-   No custom approval workflow

### Power App

-   Quotation requires **Approved checkbox** (`custom_approved`) to be checked
-   Submit button is **hidden** until Approved = 1
-   `before_submit` event validates approval
-   Prevents submission without approval

---

## 5. Supplier Quotation Integration

### Original ERPNext

-   Supplier Quotations are independent documents
-   No direct integration with Customer Quotation
-   Comparison is done manually via reports

### Power App

-   Supplier Quotations are linked to Customer Quotation via Material Request
-   **"Select Items from Supplier Quotations"** button:
    -   Shows all items from linked Supplier Quotations
    -   Allows selecting items to add to Customer Quotation
    -   Updates item rates with supplier rates
-   **"Compare Supplier Quotations"** button:
    -   Opens comparison report with pre-filled filters
-   Items can be selected and added directly to Customer Quotation

---

## 6. Item Rate Management

### Original ERPNext

-   Item rates are set manually or from Price List
-   Rates don't change based on supplier quotations
-   Expenses (Landed Cost) update Purchase Receipt valuation, not sales rates

### Power App

-   Item rates can be updated from Supplier Quotations
-   **Logic:**
    1. Rate is updated with supplier rate from selected items
    2. On save, original rate is restored (from Supplier Quotation or price_list_rate)
    3. Expenses are distributed and added to rates
    4. Margin is applied if set
-   Rates reflect supplier pricing + expenses + margin
-   When expenses are deleted/changed, rates automatically return to original values

---

## 7. Journal Entry Creation

### Original ERPNext

-   Journal Entries are created manually
-   No automatic expense recording
-   Landed Cost Voucher updates item valuation but doesn't create Journal Entry

### Power App

-   Journal Entry is created **automatically** on Sales Order submit
-   **Structure:**
    -   **Debit:** Expense accounts (from each expense row)
    -   **Credit:** Default service expense account (from Company settings)
-   Journal Entry is automatically submitted
-   Expenses are recorded in accounting system without manual intervention

---

## 8. Document Events vs Method Overrides

### Original ERPNext

-   Uses standard document events
-   Some methods can be overridden
-   Core logic is in controller classes
-   Landed Cost Voucher only supports Stock Items and Fixed Assets

### Power App

-   **Minimal method overrides** - primarily document events
-   All custom logic uses:
    -   `validate` event for calculations
    -   `before_save` event for copying data
    -   `before_submit` event for validation
    -   `on_submit` event for Journal Entry creation
-   **Exception:** Landed Cost Voucher class override to support Service Items
-   Preserves ERPNext's original logic while extending functionality

---

## Summary Table

| Feature                            | Original ERPNext                       | Power App                               |
| ---------------------------------- | -------------------------------------- | --------------------------------------- |
| **Expense Location**               | Purchase Receipt (Landed Cost Voucher) | Quotation (Custom Table)                |
| **Expense Timing**                 | After goods received                   | At Quotation stage                      |
| **Expense Distribution**           | Manual via Landed Cost Voucher         | Automatic on save                       |
| **Material Request Source**        | Sales Order                            | Quotation (Draft)                       |
| **Supplier Quotation Integration** | Manual comparison                      | Direct item selection                   |
| **Quotation Approval**             | No approval required                   | Required (custom_approved)              |
| **Item Rate Updates**              | Manual or Price List                   | From Supplier Quotations                |
| **Journal Entry**                  | Manual creation                        | Automatic on Sales Order submit         |
| **Expense Flow**                   | Purchase Receipt → Valuation           | Quotation → Sales Order → Journal Entry |
| **Landed Cost Voucher Support**   | Stock Items & Fixed Assets only        | Stock Items, Fixed Assets & Service Items |
| **Real-time Recalculation**       | Manual save required                   | Auto-save on expense changes (500ms debounce) |

---

## When to Use Each Approach

### Use Original ERPNext When:

-   You're a direct seller (not intermediary)
-   Expenses are known only after goods are received
-   You don't need to quote prices with expenses upfront
-   Standard sales cycle is sufficient

### Use Power App When:

-   You're an intermediary service company
-   You need to quote prices with expenses included upfront
-   You want automatic expense distribution
-   You need supplier quotation integration
-   You want automatic Journal Entry creation

---

## References

-   **Power App Workflow:** `app_workflow.md`
-   **Power App Expenses:** `app_expenses_workflow.md`
-   **Original ERPNext Sales Cycle:** `original_erpnext_workflow/original_erpnext_sales_cycle_symmery.md`
-   **Landed Cost Voucher:** `original_erpnext_workflow/landed_cost_voucher_analysis.md`
