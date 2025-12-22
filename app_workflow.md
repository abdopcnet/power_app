# Power App - Workflow

## Complete Workflow

```
1. Quotation (Draft)
   ├── Create Material Request
   ├── Create RFQ
   ├── Receive Supplier Quotations
   ├── Select Items from Supplier Quotations
   ├── Add Expenses (auto-distributed to items)
   ├── Check Approved
   └── Submit (only if Approved = 1)

2. Sales Order
   ├── Create from Quotation (expenses auto-copied)
   └── Submit (Journal Entry auto-created)

3. Continue Standard Flow
   ├── Delivery Note
   └── Sales Invoice
```

## Document States

| State     | Actions Available                          |
| --------- | ------------------------------------------ |
| Draft     | Add items, Add expenses, Check Approved    |
| Approved  | Submit (button visible)                    |
| Submitted | View items (read-only), Create Sales Order |

## Expense Flow

1. **Quotation:** Add expenses → Auto-distribute to items
2. **Sales Order:** Expenses copied automatically
3. **Journal Entry:** Created on Sales Order submit

## Key Features

-   Material Request from Draft Quotation
-   Supplier Quotation item selection
-   Real-time expense recalculation (500ms debounce)
-   Approval required before submission
-   Automatic Journal Entry creation
-   Payment Schedule auto-set due_date
