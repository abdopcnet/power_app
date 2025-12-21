# Power App

![Version](https://img.shields.io/badge/version-21.12.2025-blue)

## Overview

Power App is a Frappe/ERPNext customization for intermediary service companies. It extends ERPNext's standard workflow to support supplier quotation management, expense allocation, and automated pricing calculations.

---

## Features

### 1. Material Request from Quotation

-   **Create Material Request directly from Draft Quotation**
-   Material Request is automatically linked to Quotation
-   Enables procurement workflow before Sales Order creation
-   Supports intermediary company workflow

**Button:** "Material Request" (standalone, info color)

---

### 2. Supplier Quotation Comparison

-   **Open Supplier Quotation Comparison report from Quotation**
-   Pre-filtered by Material Request/RFQ if available
-   If multiple Material Requests exist, selection dialog appears
-   Quick comparison of supplier offers

**Button:** "Compare Supplier Quotations" (standalone, warning/orange color)

---

### 3. Select Items from Supplier Quotations

-   **Multi-select items from multiple Supplier Quotations**
-   Dialog displays all items from linked Supplier Quotations
-   Select items using checkboxes
-   Items are added/updated in Customer Quotation with supplier rates
-   Tracks supplier quotation reference for each item

**Features:**

-   Full functionality in Draft Quotation
-   Read-only view in Submitted Quotation
-   Automatic rate updates from supplier quotations
-   Supplier quotation reference tracking

**Button:** "Select Items from Supplier Quotations" (standalone, success/green color)
**Read-only Button:** "View Supplier Quotation Items" (standalone, info color)

---

### 4. Expense Allocation at Quotation Level

-   **Add expenses to Quotation before purchase**
-   Automatic expense distribution to items proportionally
-   Real-time rate recalculation when expenses are modified/deleted
-   Expenses included in final pricing upfront

**Features:**

-   Add multiple expense types (shipping, customs, handling, etc.)
-   Proportional distribution based on item amounts
-   Auto-save with 500ms debounce when expenses change
-   Rates automatically restore to original when expenses are removed
-   Margin can be applied after expense distribution

**Table:** `custom_quotation_expenses_table` (Service Expense)

---

### 5. Approved Workflow for Quotation

-   **Approval required before Quotation submission**
-   Submit button visibility controlled by Approved checkbox
-   Prevents accidental submission without approval
-   Read-only item selection after submission

**Features:**

-   Approved checkbox (`custom_approved`) required
-   Submit button hidden until Approved = 1
-   Validation on submit attempt
-   Prevents modifications after submission

---

### 6. Automatic Expense Flow to Sales Order

-   **Expenses automatically copied from Quotation to Sales Order**
-   No manual data entry required
-   Maintains expense tracking through sales cycle

**Flow:**

-   Quotation Expenses → Sales Order Expenses (automatic copy)
-   Sales Order Expenses → Journal Entry (automatic creation on submit)

---

### 7. Automatic Journal Entry Creation

-   **Journal Entry created automatically on Sales Order submit**
-   Records expenses in accounting system
-   No manual Journal Entry creation required

**Structure:**

-   **Debit:** Expense accounts (from each expense row)
-   **Credit:** Default service expense account (from Company settings)
-   Journal Entry automatically submitted

---

### 8. Real-time Expense Recalculation

-   **Rates update automatically when expenses change**
-   No manual save required
-   Debounced auto-save (500ms delay)
-   Prevents multiple saves during rapid changes

**Triggers:**

-   Expense amount changed
-   Expense row added
-   Expense row removed

---

### 9. Rate Restoration Logic

-   **Automatic rate restoration before expense distribution**
-   Uses supplier quotation rate if available
-   Falls back to price list rate if no supplier quotation
-   Ensures accurate expense distribution

**Logic:**

1. Check if item has supplier quotation → Use supplier rate
2. If no supplier quotation → Use price_list_rate
3. Restore rate to original value
4. Distribute expenses proportionally
5. Apply margin if set

---

### 10. Landed Cost Voucher Extension

-   **Extended Landed Cost Voucher to support Service Items**
-   Original ERPNext: Only Stock Items and Fixed Assets
-   Power App: Stock Items, Fixed Assets, and Service Items

**Use Case:**

-   Add expenses after Purchase Receipt (for purchased items)
-   Works with Service Items (not just stock items)
-   Safe implementation (doesn't affect stock ledger or valuation)

**Note:** Service Expense Table in Quotation is still required for expenses before purchase.

---

### 11. Item History Display

-   **Show item price and stock details in dialog**
-   Displays item information from multiple sources
-   Helps in decision-making during item selection

**Button:** "Show Item History" (standalone, info color)

---

### 12. Unified Logging System

-   **Consistent logging format across all files**
-   Frontend: `console.log('[filename.js] (message)')`
-   Backend: `frappe.log_error(f"[filename.py] function: message")`
-   Easier debugging and troubleshooting

---

## Key Benefits

### 💰 Expense Management

-   Add expenses at Quotation stage (before purchase)
-   Automatic expense distribution to items
-   Real-time rate recalculation when expenses change

### 🔗 Supplier Integration

-   Direct item selection from supplier quotations
-   Multi-select items from multiple suppliers
-   Automatic rate updates from supplier quotations

### ⚙️ Automated Calculations

-   Automatic expense distribution and rate updates
-   Rate restoration logic (supplier rate → price list rate)
-   Margin application after expense distribution

### ⚡ Real-time Updates

-   Rates recalculate automatically when expenses change
-   Debounced auto-save (500ms delay)
-   No manual save required

### ✅ Approval Control

-   Prevent submission without approval
-   Submit button visibility controlled by Approved checkbox
-   Read-only item selection after submission

### 📊 Accounting Integration

-   Automatic Journal Entry creation on Sales Order submit
-   Expenses recorded in accounting system
-   No manual Journal Entry creation required

### 🔧 Service Items Support

-   Extended Landed Cost Voucher for service items
-   Works with Stock Items, Fixed Assets, and Service Items
-   Safe implementation (doesn't affect stock ledger)

### 🛡️ Code Quality

-   No method overrides (uses document events)
-   Preserves ERPNext's original logic
-   Unified logging system across all files

---

## Installation

1. Install app in Frappe bench
2. Run migrations
3. Clear cache: `bench clear-cache`
4. Restart: `bench restart`

---

## Documentation

-   **Complete Workflow:** `app_workflow.md`
-   **Expense Flow:** `app_expenses_workflow.md`
-   **File Structure:** `app_file_structure.md`
-   **API Reference:** `app_api_tree.md`
-   **Implementation Plan:** `app_plan.md`
-   **vs ERPNext:** `app_vs_erpnext_differences.md`

---

## Notes

-   All custom logic uses document events (no method overrides, except Landed Cost Voucher class override)
-   Code organized by functionality (one file per DocType/feature)
-   Python and JavaScript files have matching names where applicable
-   Follows AGENTS.md guidelines
