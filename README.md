# Power App

![Version](https://img.shields.io/badge/version-28.12.2025-blue)

## Overview

Frappe/ERPNext customization for intermediary service companies. Extends ERPNext workflow for supplier quotation management, expense allocation, and automated pricing.

## Key Features

-   **Material Request from Quotation** - Create MR directly from Draft Quotation
-   **Supplier Quotation Integration** - Select items from multiple supplier quotations
-   **Expense Allocation** - Add expenses at Quotation level, auto-distribute to items
-   **Approval Workflow** - Required approval before Quotation submission
-   **Automatic Journal Entry** - Created on Sales Order submit
-   **Real-time Calculations** - Auto-update rates when expenses change
-   **Payment Schedule** - Auto-set due_date based on delivery_date

## Installation

```bash
bench get-app power_app
bench --site [site] install-app power_app
bench clear-cache
bench restart
```

## Documentation

-   `app_workflow.md` - Complete workflow
-   `app_expenses_workflow.md` - Expense flow
-   `app_file_structure.md` - File structure
-   `app_api_tree.md` - API reference
-   `app_plan.md` - Implementation plan
-   `app_vs_erpnext_differences.md` - ERPNext comparison

## Notes

-   All custom logic uses document events (no method overrides except Landed Cost Voucher)
-   Code follows AGENTS.md guidelines
