# Expenses Implementation Workflow

## Overview

Power App implements expense allocation and distribution at the Quotation level, with automatic copying to Sales Order and Journal Entry creation.

## Expense Flow

### Phase 1: Quotation Level (Draft)

1. **Add Expenses to Quotation**

    - User adds expense rows in `custom_service_expense_table`
    - Each expense row contains:
        - `service_expense_type` (Link) - Type of expense
        - `company` (Link) - Company
        - `default_account` (Link) - Expense account (Debit in Journal Entry)
        - `amount` (Currency) - Expense amount

2. **Expense Distribution on Save**
    - Trigger: `Quotation.validate` event
    - Handler: `power_app.quotation.quotation_validate`
    - Logic:
        1. **Restore Original Rates:**
            - For each item, check if `custom_supplier_quotation` exists
            - If exists: Get rate from Supplier Quotation Item
            - If empty: Use `price_list_rate`
            - Restore `rate` and `net_rate` to original values
        2. **Calculate Total Expenses:**
            - Calculate total expenses from `custom_service_expense_table`
        3. **Calculate Total Item Amount:**
            - Calculate total item amount from `items` table (using restored rates)
        4. **Distribute Expenses:**
            - Distribute expenses proportionally to each item:
                - `expense_per_item = (item_amount / total_item_amount) * total_expenses`
                - `expense_amount_for_item = expense_per_item * item_qty`
                - `rate = original_rate + (expense_per_item / item_qty)`
                - `custom_item_expense_amount = expense_amount_for_item` (total expense for this item)
        5. **Apply Margin:**
            - If `custom_item_margin` exists:
                - `rate = rate + (rate * margin_percentage / 100)`
    - Updates: `rate`, `net_rate`, `amount`, `net_amount`, `custom_item_expense_amount` fields
    - **Note:** If no expenses exist, `custom_item_expense_amount` is reset to 0
    - **Real-time Recalculation:**
        - Event handlers on Service Expense table changes
        - Auto-save after 500ms debounce when expenses are modified
        - Rates update automatically without manual save
    - **Note:** When expenses are deleted/changed, rates automatically return to original values

### Phase 2: Sales Order Creation

3. **Copy Expenses to Sales Order**
    - Trigger: `make_sales_order` method override (via mapper)
    - Handler: `power_app.quotation_mapper._make_sales_order`
    - Logic:
        - Override `make_sales_order` method in `quotation_mapper.py`
        - Copy expenses in `set_missing_values` function during document mapping
        - Only copy if `custom_sales_order_service_expenses_table` is empty (prevents duplicates)
        - Fields copied:
            - `service_expense_type`
            - `company`
            - `default_account`
            - `amount`
    - **Note:** `before_save` event handler was removed to prevent duplicate rows on every save

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

| Quotation Field                | Sales Order Field                           |
| ------------------------------ | ------------------------------------------- |
| `custom_service_expense_table` | `custom_sales_order_service_expenses_table` |
| `service_expense_type`         | `service_expense_type`                      |
| `company`                      | `company`                                   |
| `default_account`              | `default_account`                           |
| `amount`                       | `amount`                                    |

### Sales Order → Journal Entry

| Sales Order Field                                | Journal Entry Field           |
| ------------------------------------------------ | ----------------------------- |
| `default_account` (per expense)                  | `accounts[].account` (Debit)  |
| Company `custom_default_service_expense_account` | `accounts[].account` (Credit) |

## Custom Fields

### Quotation

-   `custom_service_expense_table` (Table: Service Expense) - Expense entries
-   `custom_item_margin` (Float) - Margin percentage applied to items

### Sales Order

-   `custom_sales_order_service_expenses_table` (Table: Service Expense) - Copied expenses

### Company

-   `custom_default_service_expense_account` (Link: Account) - Default credit account for Journal Entry

## Implementation Details

### Expense Distribution Formula

```python
# Step 1: Restore original rates
for item in items:
    original_rate = None

    # Check if item has supplier quotation
    if item.custom_supplier_quotation:
        # Get rate from Supplier Quotation Item
        sq_items = frappe.get_all(
            "Supplier Quotation Item",
            filters={
                "parent": item.custom_supplier_quotation,
                "item_code": item.item_code
            },
            fields=["rate"],
            limit=1
        )
        if sq_items:
            original_rate = sq_items[0].rate

    # If no supplier quotation, use price_list_rate
    if not original_rate:
        original_rate = item.price_list_rate or item.rate

    # Restore original rate
    item.rate = original_rate
    item.net_rate = original_rate

# Step 2: Calculate total expenses
total_expenses = sum(expense.amount for expense in custom_service_expense_table)

# Step 3: Calculate total item amount (using restored rates)
total_item_amount = sum(item.amount for item in items)

# Step 4: Distribute expenses to items
for item in items:
    expense_per_item = (item.amount / total_item_amount) * total_expenses
    expense_amount_for_item = expense_per_item * item.qty
    item.rate = item.rate + (expense_per_item / item.qty)
    item.custom_item_expense_amount = expense_amount_for_item

# Step 5: Apply margin if exists
if custom_item_margin:
    for item in items:
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
-   Real-time recalculation when expenses are modified/deleted (500ms debounce)
-   Expenses are copied via mapper override when creating Sales Order from Quotation
-   Duplicate prevention: Only copy if expenses table is empty
-   Journal Entry is created automatically on Sales Order submit
-   Minimal method overrides - primarily document events
-   Service Expense Table is used at Quotation level (before purchase)
-   Landed Cost Voucher can be used after Purchase Receipt (supports Service Items via override)
