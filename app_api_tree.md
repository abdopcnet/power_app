# Power App - API Structure

## Server-Side API

```
power_app.quotation
├── get_supplier_quotation_items(quotation_name)
├── get_material_requests_from_quotation(quotation_name)
├── add_items_from_supplier_quotations(quotation_name, selected_items)
├── quotation_validate(doc, method) [Event]
└── quotation_before_submit(doc, method) [Event]

power_app.sales_order
├── sales_order_validate(doc, method) [Event]
└── create_je_from_service_expence(doc, method) [Event]

power_app.quotation_mapper
└── make_sales_order(source_name, target_doc, args) [Override]

power_app.supplier_quotation
├── check_quotation_linked(doc)
└── update_quotation_linked(doc, q)

power_app.material_request
└── make_material_request_from_quotation(source, target)

power_app.item
└── get_item_details(item_code)
```

## Client-Side Functions

```
quotation.js
├── refresh(frm)
├── show_item_selection_dialog(frm)
├── calculate_expense_rates(frm)
└── trigger_expense_recalculation(frm)

sales_order.js
├── delivery_date(frm)
├── transaction_date(frm)
└── payment_schedule handlers
```

## Document Events

```
Quotation
├── validate → quotation_validate
└── before_submit → quotation_before_submit

Sales Order
├── validate → sales_order_validate
└── on_submit → create_je_from_service_expence
```