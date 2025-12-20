# Expenses Implementation Workflow

## Overview

Power App implements expense allocation and distribution at the Quotation level, with automatic copying to Sales Order and Journal Entry creation.

## Expense Flow

### Phase 1: Quotation Level (Draft)

1. **Add Expenses to Quotation**

    - User adds expense rows in `custom_quotation_expenses_table`
    - Each expense row contains:
        - `service_expense_type` (Link) - Type of expense
        - `compnay` (Link) - Company (Note: Typo in JSON field name, kept as-is for compatibility)
        - `default_account` (Link) - Expense account (Debit in Journal Entry)
        - `amount` (Currency) - Expense amount

2. **Expense Distribution on Save**
    - Trigger: `Quotation.validate` event
    - Handler: `power_app.quotation.quotation_validate`
    - Logic:
        - Calculate total expenses from `custom_quotation_expenses_table`
        - Calculate total item amount from `items` table
        - Distribute expenses proportionally to each item:
            - `expense_per_item = (item_amount / total_item_amount) * total_expenses`
            - `rate = current_rate + (expense_per_item / item_qty)`
        - Apply margin if `custom_item_margin` exists:
            - `rate = rate + (rate * margin_percentage / 100)`
    - Updates: `rate`, `net_rate`, `amount`, `net_amount` fields

### Phase 2: Sales Order Creation

3. **Copy Expenses to Sales Order**
    - Trigger: `Sales Order.before_save` event
    - Handler: `power_app.sales_order.copy_quotation_expenses_to_sales_order`
    - Logic:
        - Check if Sales Order created from Quotation
        - Get Quotation reference from `items[].quotation_item`
        - Copy `custom_quotation_expenses_table` → `custom_sales_order_service_expenses_table`
        - Fields copied:
            - `service_expense_type`
            - `compnay` (Note: Typo in JSON field name, kept as-is)
            - `default_account`
            - `amount`
    - Prevents duplicate copying with `_quotation_expenses_copied` flag

### Phase 3: Sales Order Submission

4. **Create Journal Entry**
    - Trigger: `Sales Order.on_submit` event
    - Handler: `power_app.sales_order.create_je_from_service_expence`
    - Logic:
        - Get default service expense account from Company (`custom_default_service_expense_account`)
        - Group expenses by `default_account`
        - Create Journal Entry:
            - **Debit entries:** One per expense account (from `default_account` field)
            - **Credit entry:** Default service expense account (from Company)
        - Journal Entry is automatically submitted
    - Result: Expenses recorded in accounting system

## Field Mapping

### Quotation → Sales Order

| Quotation Field                   | Sales Order Field                           |
| --------------------------------- | ------------------------------------------- |
| `custom_quotation_expenses_table` | `custom_sales_order_service_expenses_table` |
| `service_expense_type`            | `service_expense_type`                      |
| `compnay` (Note: Typo in JSON)    | `compnay` (Note: Typo in JSON)              |
| `default_account`                 | `default_account`                           |
| `amount`                          | `amount`                                    |

### Sales Order → Journal Entry

| Sales Order Field                                | Journal Entry Field           |
| ------------------------------------------------ | ----------------------------- |
| `default_account` (per expense)                  | `accounts[].account` (Debit)  |
| Company `custom_default_service_expense_account` | `accounts[].account` (Credit) |

## Custom Fields

### Quotation

-   `custom_quotation_expenses_table` (Table: Service Expense) - Expense entries
-   `custom_item_margin` (Float) - Margin percentage applied to items

### Sales Order

-   `custom_sales_order_service_expenses_table` (Table: Service Expense) - Copied expenses

### Company

-   `custom_default_service_expense_account` (Link: Account) - Default credit account for Journal Entry

## Implementation Details

### Expense Distribution Formula

```python
# Calculate total expenses
total_expenses = sum(expense.amount for expense in custom_quotation_expenses_table)

# Calculate total item amount
total_item_amount = sum(item.amount for item in items)

# Distribute to each item
for item in items:
    expense_per_item = (item.amount / total_item_amount) * total_expenses
    item.rate = item.rate + (expense_per_item / item.qty)

    # Apply margin if exists
    if custom_item_margin:
        item.rate = item.rate + (item.rate * custom_item_margin / 100)
```

### Journal Entry Structure

```
Journal Entry:
├── Debit: Expense Account 1 (amount from expense row 1)
├── Debit: Expense Account 2 (amount from expense row 2)
└── Credit: Default Service Expense Account (total of all expenses)
```

## Notes

-   Expenses are distributed proportionally based on item amounts
-   Distribution happens on every save (validate event)
-   Expenses are copied only once when creating Sales Order from Quotation
-   Journal Entry is created automatically on Sales Order submit
-   All logic uses document events (no method overrides)
