# Power App vs ERPNext - Differences

## Key Differences

| Feature                 | ERPNext                 | Power App          |
| ----------------------- | ----------------------- | ------------------ |
| Expense Location        | Purchase Receipt        | Quotation          |
| Expense Timing          | After receipt           | At Quotation stage |
| Expense Distribution    | Manual                  | Automatic          |
| Material Request Source | Sales Order             | Quotation (Draft)  |
| Supplier Integration    | Manual                  | Direct selection   |
| Approval                | Not required            | Required           |
| Journal Entry           | Manual                  | Automatic          |
| Landed Cost Support     | Stock/Fixed Assets only | + Service Items    |
| Real-time Updates       | Manual save             | Auto-save (500ms)  |

## Workflow Comparison

**ERPNext:**

```
Quotation → Sales Order → Material Request → RFQ → Supplier Quotations
```

**Power App:**

```
Quotation (Draft)
├── Material Request
├── RFQ
├── Supplier Quotations
├── Select Items
├── Add Expenses
└── Submit (if Approved)
    ↓
Sales Order (expenses copied)
    ↓
Journal Entry (auto-created)
```

## When to Use

**Use Power App when:**

-   Intermediary service company
-   Need to quote with expenses upfront
-   Want automatic expense distribution
-   Need supplier quotation integration
