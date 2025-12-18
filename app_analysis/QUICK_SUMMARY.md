# Power App - Quick Summary

## What This App Does

Power App is a **customization package for ERPNext** that enhances the quotation and sales workflow for Power Key Company. It adds expense management, service tracking, and automated accounting features.

---

## Main Features (At a Glance)

### 1. ✅ Expense Management on Quotations
- Add expenses to quotations (shipping, installation, etc.)
- Expenses automatically distributed to items proportionally
- Apply margin percentage to items

### 2. ✅ Service Expense Tracking
- Track service expenses on Sales Orders
- Automatically creates Journal Entries when Sales Order is submitted
- Groups expenses by account for proper accounting

### 3. ✅ Material Request Creation
- Create Material Requests directly from Quotations
- Maintains reference link between documents

### 4. ✅ Supplier Quotation Integration
- Update Customer Quotations with rates from Supplier Quotations
- Maintains rate consistency (uses base currency)

### 5. ✅ Item Information Display
- Quick view of item stock, last selling/purchase rates
- Shows last supplier information
- Accessible via button on Quotation form

### 6. ✅ Service Items Support
- Special handling for service quotations
- Filters items to show only non-stock, service items

---

## Key Workflows

### Workflow 1: Quotation with Expenses
```
1. Create Quotation
2. Add Items
3. Add Expenses (optional)
4. Set Margin % (optional)
5. Save → Rates automatically recalculated
6. Submit Quotation
```

### Workflow 2: Material Request from Quotation
```
1. Submit Quotation
2. Click "Create > Material Request"
3. Material Request created with items
4. Use Material Request to create Supplier Quotation
```

### Workflow 3: Update Quotation from Supplier
```
1. Supplier Quotation submitted
2. System detects linked Customer Quotation
3. Click "Update Quotation" button
4. Customer Quotation updated with supplier rates
```

### Workflow 4: Service Expense Journal Entry
```
1. Create Sales Order with service expenses
2. Submit Sales Order
3. Journal Entry automatically created and submitted
4. Expenses grouped by account
```

---

## Custom Doctypes

1. **Service Expense** - Child table for service expenses
2. **Service Expense Type** - Master for expense categories
3. **Quotation Expenses** - Child table for quotation expenses
4. **Service Line** - (Details to be confirmed)

---

## Modified Standard Doctypes

1. **Quotation** - Added expense and margin fields
2. **Sales Order** - Added service expense table
3. **Material Request** - Added reference fields
4. **Company** - Added default service expense account
5. **Quotation Item** - Added fields to preserve supplier rates

---

## Technical Components

### Python Files
- `customization.py` - Main business logic
- `mapper.py` - Document mapping utilities
- `overried.py` - Method overrides

### JavaScript Files
- `quotation.js` - Quotation form enhancements
- `supplier_quotation.js` - Supplier Quotation form enhancements

### Configuration
- `hooks.py` - App configuration and event hooks

---

## Key Calculations

### Expense Distribution
```
Item New Rate = Original Rate + (Item Amount / Total Amount × Total Expenses) / Qty
```

### Margin Application
```
Final Rate = Rate × (1 + Margin / 100)
```

### Journal Entry Structure
```
Debit: Expense Accounts (grouped)
Credit: Company Default Service Expense Account
```

---

## Setup Requirements

1. **Company Configuration**
   - Set `custom_default_service_expense` account in Company master

2. **Service Expense Types**
   - Create Service Expense Type records
   - Link to default accounts

3. **Permissions**
   - Standard ERPNext permissions apply
   - No special permissions required

---

## Common Use Cases

### Use Case 1: Quotation with Shipping Costs
- Add items to quotation
- Add "Shipping" expense (e.g., 100)
- System distributes 100 across items based on their amounts
- Items get updated rates

### Use Case 2: Service Project
- Enable "Services" checkbox
- Add service items (non-stock)
- Add service expenses on Sales Order
- Journal Entry created automatically on submit

### Use Case 3: Procurement Workflow
- Create Customer Quotation
- Create Material Request from Quotation
- Send Material Request to suppliers
- Receive Supplier Quotations
- Update Customer Quotation with supplier rates

---

## Files to Review

### For Understanding Business Logic
- `power_app/customization.py` - Core calculations
- `power_app/overried.py` - Sales Order creation

### For Understanding Workflows
- `power_app/public/js/quotation.js` - Quotation UI
- `power_app/public/js/supplier_quotation.js` - Supplier Quotation UI

### For Understanding Structure
- `power_app/hooks.py` - App configuration
- `power_app/mapper.py` - Document mapping

---

## Important Notes

⚠️ **Expense Allocation**: Expenses are distributed proportionally. This may not suit all scenarios.

⚠️ **Journal Entry Automation**: Journal Entries are auto-submitted. Ensure proper account setup.

⚠️ **Currency Handling**: Uses `base_rate` when copying rates to avoid currency issues.

⚠️ **Service Items**: When "Services" is enabled, only non-stock items are shown.

---

## Support

**Publisher:** Hadeel Milad
**Email:** hadeelnr88@gmail.com
**License:** MIT

---

## Documentation Files

- **README.md** - Complete overview and architecture
- **FUNCTIONALITY_DETAILS.md** - Detailed functionality explanations
- **API_REFERENCE.md** - API methods and technical reference
- **QUICK_SUMMARY.md** - This file (quick overview)

---

*For detailed information, refer to the other documentation files in this directory.*

