# Testing Steps for Steps 4 & 5

## Prerequisites

1. **Clear cache and restart bench:**
   ```bash
   cd /home/administrator/frappe-bench
   bench clear-cache
   bench restart
   ```

2. **Ensure you have:**
   - At least one Customer
   - At least one Supplier
   - At least one Item (stock or service item)

---

## Test Scenario: Complete Workflow

### Step 1: Create Customer Quotation

1. Go to **Selling → Quotation → New**
2. Fill in:
   - **Customer**: Select any customer
   - **Items**: Add at least 2-3 items
   - **Save** the quotation (keep it in Draft status)
3. **Note the Quotation name** (e.g., `QUO-00001`)

---

### Step 2: Create Material Request from Quotation

1. In the same Quotation document, click **Create → Material Request**
2. Fill in required fields (if any)
3. **Submit** the Material Request
4. **Note the Material Request name** (e.g., `MAT-REQ-00001`)

---

### Step 3: Create RFQ (Request for Quotation)

1. Go to **Buying → Request for Quotation → New**
2. Fill in:
   - **Material Request**: Select the Material Request created in Step 2
   - **Suppliers**: Add at least 2 suppliers
   - **Save** and **Submit** the RFQ

---

### Step 4: Create Supplier Quotations

1. Go to **Buying → Supplier Quotation → New**
2. Create **at least 2 Supplier Quotations** for the same Material Request:
   - **Supplier Quotation 1:**
     - **Material Request**: Select the MR from Step 2
     - **Supplier**: Select supplier 1
     - **Items**: Add items with rates (e.g., Item A = 100, Item B = 200)
     - **Save** and **Submit**
   - **Supplier Quotation 2:**
     - **Material Request**: Select the same MR from Step 2
     - **Supplier**: Select supplier 2
     - **Items**: Add same items with different rates (e.g., Item A = 90, Item B = 190)
     - **Save** and **Submit**

---

### Step 5: Test "Compare Supplier Quotations" Button (Step 3)

1. Go back to the **Customer Quotation** created in Step 1
2. Look for the **"Compare Supplier Quotations"** button in the **Tools** menu
3. Click it
4. **Expected Result**: Should open ERPNext's "Supplier Quotation Comparison" report

---

### Step 6: Test "Select Items from Supplier Quotations" Dialog (Steps 4 & 5)

1. In the same **Customer Quotation**, look for the **"Select Items from Supplier Quotations"** button in the **Tools** menu
2. Click it
3. **Expected Results:**
   - Dialog should open with title: "Select Items from Supplier Quotations"
   - Table should display all supplier quotation items linked via Material Request
   - Columns: Select, Item Code, Item Name, Supplier, Supplier Quotation, Qty, UOM, Rate
   - **Checkboxes should be ENABLED** (not disabled)
   - **"Select All"** and **"Deselect All"** buttons should appear above the table
   - **Counter** should show "0 of X items selected" (where X is total items)

---

### Step 7: Test Multi-Select Functionality (Step 5)

1. In the dialog, test the following:

   **a) Individual Selection:**
   - Click a checkbox for one item
   - **Expected**: Counter should update to "1 of X items selected"
   - Click another checkbox
   - **Expected**: Counter should update to "2 of X items selected"

   **b) Select All:**
   - Click **"Select All"** button
   - **Expected**: All checkboxes should be checked, counter should show "X of X items selected"

   **c) Deselect All:**
   - Click **"Deselect All"** button
   - **Expected**: All checkboxes should be unchecked, counter should show "0 of X items selected"

   **d) Mixed Selection:**
   - Select some items manually
   - Click **"Select All"** (should select remaining)
   - Uncheck one item manually
   - **Expected**: Counter should update correctly

---

### Step 8: Test "Add Selected Items" Button (Step 5 - Preview)

1. In the dialog:
   - Select at least 2 items using checkboxes
   - Click **"Add Selected Items"** button
   - **Expected Result**:
     - Message should appear: "Selected X item(s). Adding functionality will be enabled in next step."
     - Dialog should NOT close (functionality not yet connected)

2. Test with no selection:
   - Deselect all items
   - Click **"Add Selected Items"** button
   - **Expected Result**:
     - Error message: "No Items Selected - Please select at least one item to add."

---

## Troubleshooting

### Issue: Button not appearing
- **Solution**:
  - Clear cache: `bench clear-cache`
  - Restart: `bench restart`
  - Refresh browser (Ctrl+F5)
  - Ensure Quotation is in Draft status (docstatus = 0)

### Issue: Dialog shows "No Items Found"
- **Solution**:
  - Ensure Material Request is **Submitted** (docstatus = 1)
  - Ensure Supplier Quotations are **Submitted** (docstatus = 1)
  - Ensure Material Request has `custom_dc_refrance` field set to Quotation name
  - Check that Supplier Quotation Items have `material_request` field set

### Issue: Checkboxes are disabled
- **Solution**:
  - Check browser console for JavaScript errors
  - Ensure `setup_item_selection_checkboxes()` is being called
  - Clear cache and restart

### Issue: Counter not updating
- **Solution**:
  - Check browser console for JavaScript errors
  - Ensure jQuery is loaded
  - Check that checkbox change events are bound correctly

---

## Expected Behavior Summary

✅ **Step 3 Button**: Opens Supplier Quotation Comparison report
✅ **Step 4 Dialog**: Displays supplier quotation items in table
✅ **Step 5 Checkboxes**: Enabled and functional
✅ **Step 5 Select All/Deselect All**: Working correctly
✅ **Step 5 Counter**: Updates in real-time
✅ **Step 5 Add Button**: Shows preview message (not yet connected to server)

---

## Next Steps After Testing

Once testing is successful, proceed to:
- **Step 6**: Create `add_items_from_supplier_quotations()` Python method
- **Step 7**: Connect dialog to server method

