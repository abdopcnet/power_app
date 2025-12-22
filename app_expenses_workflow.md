# Power App - Expense Workflow

## Expense Flow

```
Quotation (Draft)
├── Add Expenses → custom_service_expense_table
├── Auto-distribute to items (proportional)
└── Update item rates

Sales Order
├── Expenses copied automatically
└── custom_sales_order_service_expenses_table

Sales Order Submit
└── Journal Entry created automatically
    ├── Debit: Expense accounts
    └── Credit: Default service expense account
```

## Distribution Formula

```
1. Restore original rates (supplier/price_list)
2. Calculate total expenses
3. Distribute proportionally:
   expense_per_item = (item_amount / total_item_amount) * total_expenses / qty
4. Update rate = original_rate + expense_per_item
5. Apply margin (if exists) after expenses
```

## Real-time Updates

- Auto-save on expense changes (500ms debounce)
- Rates update automatically
- No manual save required

## Journal Entry Structure

- **Debit:** One entry per expense account
- **Credit:** Default service expense account (Company setting)