# Power App - File Structure

```
power_app/
├── power_app/
│   ├── hooks.py                    # Document events, JS mapping
│   ├── quotation.py                # Quotation functions
│   ├── sales_order.py              # Sales Order events
│   ├── quotation_mapper.py         # Sales Order mapper override
│   ├── supplier_quotation.py       # Supplier Quotation functions
│   ├── material_request.py         # Material Request mapping
│   ├── item.py                     # Item details
│   ├── landed_cost_voucher.py      # Landed Cost override
│   ├── power_app/
│   │   ├── doctype/                # Custom DocTypes
│   │   └── custom/                 # Custom field JSON
│   └── public/js/
│       ├── quotation.js            # Quotation client logic
│       ├── sales_order.js          # Sales Order client logic
│       └── supplier_quotation.js   # Supplier Quotation UI
└── README.md
```

## Key Files

**Python:**

-   `quotation.py` - Expense distribution, approval
-   `sales_order.py` - Journal Entry, payment schedule
-   `quotation_mapper.py` - Expense table copy

**JavaScript:**

-   `quotation.js` - Buttons, dialogs, calculations
-   `sales_order.js` - Payment schedule handling

**Custom Fields:**

-   `quotation.json`, `quotation_item.json`
-   `sales_order.json`, `company.json`
