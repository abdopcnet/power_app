frappe.ui.form.on('Quotation', {
  refresh(frm) {
    if (frm.doc.docstatus === 1) {
    // frm.remove_custom_button("Sales Order", "Create");
    // cur_frm.remove_custom_button('Sales Order', 'Create');
    // frm.add_custom_button(
	// 				__("Sales Order"),
	// 				function () {
	// 					frappe.model.open_mapped_doc({
    //                     method: "power_app.overried.make_sales_order",
    //                     frm: frm.doc,
    //                     });
    //                     console.log("making sales order")
	// 				},
	// 				__("Create")
	// 			);
    }
    add_show_item_history_button(frm);
    make_MR(frm);
    frm.trigger("set_item_query");
    // Set query for a Link field in the child table named 'items' for a service new featur on the quotation doctype

  },
  set_item_query: function (frm) {
    frm.set_query('item_code', 'items', function() {
        console.log("item query ")
        if (frm.doc.custom_services){
            return {
        filters: {
            // Apply filters based on fields in the current child row
            // For example, filter 'item_code' based on 'item_group' in the same row
            is_stock_item:0,
            is_sales_item: 1,
            has_variants: 0

            // Or apply filters based on fields in the parent document
            // 'is_sales_item': doc.is_sales_order // Assuming 'is_sales_order' is a field in the parent DocType
            }
        };
        }
        else{
            return {
                    query: "erpnext.controllers.queries.item_query",
							filters: { is_sales_item: 1, customer: frm.doc.customer, has_variants: 0 },
                };
        }
    
    });
  },
  custom_services:function(frm){
        frm.trigger("set_item_query");

  }
});



// Function to add the "Show Item History" button and handle its logic
function add_show_item_history_button(frm) {
    // Only show the button if items exist and the form is not new
    if (frm.doc.items && frm.doc.items.length > 0 && !frm.is_new()) {
        frm.add_custom_button(__('Show Item History'), async function () {
            try {
                // 1. Get unique items from the current quotation
                const unique_items = [...new Set(frm.doc.items.map(item => item.item_code))];
                
                if (unique_items.length === 0) {
                    frappe.msgprint(__('No items in the current quotation.'));
                    return;
                }

                frappe.show_alert({ message: __('Fetching item details...'), indicator: 'blue' }, 3);

                // 2. Fetch the required details for each unique item
                const item_details = await fetch_item_details(frm, unique_items);

                // 3. Build HTML and show dialog
                const d = new frappe.ui.Dialog({
                    title: __('Item Price & Stock Details'),
                    fields: [
                        {
                            fieldtype: 'HTML',
                            fieldname: 'item_details_html',
                            options: build_item_details_html(item_details, frm.doc.currency)
                        }
                    ],
                    indicator: 'green',
                });
                d.show();
            } 
            catch (e) {
                console.error('Error fetching item details:', e);
                frappe.msgprint({
                    title: __('Error'),
                    message: __('Failed to fetch item details: ') + e.message,
                    indicator: 'red'
                });
            }
        });
    }
}
// Function to fetch item-specific data
async function fetch_item_details(frm, item_codes) {
    const details_promises = item_codes.map(async item_code => {
        
        // --- 1. Get On Hand Quantity (CORRECTED FUNCTION PATH) ---
        const stock_res = await frappe.call({
            // *** CHANGE MADE HERE ***
            method: 'power_app.customization.get_item_details',
            args: {
                item_code: item_code,
                // warehouse: frm.doc.warehouse || frappe.defaults.get_user_default('default_warehouse'),
                // The API often returns stock under the 'actual_qty' key
            }
        });
        console.log(stock_res)
        console.log(stock_res.stock_qty)
        console.log(stock_res.message.stock_qty)
        console.log(stock_res.message.last_selling_rate)
        console.log(stock_res.message.last_purchase_rate)
        // Adjusting how the result is read, as 'get_item_stock' returns an object
        const stock_qty = (stock_res.message && stock_res.message.stock_qty) ? stock_res.message.stock_qty : 0;

        // ... rest of your function remains the same ...
        // --- 2. Get Last Selling Rate ---
        // ... (your existing code for selling price) ...
        // const last_selling_rate = 0; // Placeholder
        const last_selling_rate = (stock_res.message && stock_res.message.last_selling_rate) ? stock_res.message.last_selling_rate : 0;
        // --- 3. Get Last Supplier Purchase Rate ---
        // ... (your existing code for purchase rate) ...
        // const last_purchase_rate = 0; // Placeholder
        const last_purchase_rate = (stock_res.message && stock_res.message.last_purchase_rate) ? stock_res.message.last_purchase_rate : 0;
        const supplier =  (stock_res.message && stock_res.message.supplier) ? stock_res.message.supplier : 0;

        return {
            item_code: item_code,
            stock_qty: stock_qty,
            last_selling_rate: last_selling_rate,
            last_purchase_rate: last_purchase_rate,
            supplier: supplier || __('Default'),
        };
    });

    return Promise.all(details_promises);
}

// Build the HTML table for the item details dialog
function build_item_details_html(item_details, currency) {
    let html = `
        <p><strong>${__('Note:')}</strong> ${__('Stock Qty is based on the current default/selected warehouse.')}</p>
        <div class="form-section card-section" style="margin-top:0">
            <table class="table table-bordered table-hover">
                <thead style="color: #1c5cab;">
                    <tr>
                        <th style="width:25%;">${__('Item')}</th>
                        <th style="width:25%;">${__('Qty in Warehouse')}</th>
                        <th style="width:25%;">${__('Last Selling Rate')}</th>
                        <th style="width:25%;">${__('Last Purchase Rate')}</th>
                        <th style="width:25%;">${__('Last Purchase Supplier')}</th>
                    </tr>
                </thead>
                <tbody>
    `;

    item_details.forEach(item => {
        const selling_rate_formatted = frappe.format(item.last_selling_rate, { fieldtype: 'Currency', options: currency });
        const purchase_rate_formatted = frappe.format(item.last_purchase_rate, { fieldtype: 'Currency', options: currency });
        
        // Format stock quantity
        const qty_formatted = frappe.format(item.stock_qty, { fieldtype: 'Float' });

        html += `
            <tr>
                <td><a href="/app/item/${item.item_code}" target="_blank" rel="noopener">${item.item_code}</a></td>
                <td>${qty_formatted} </td>
                <td>${selling_rate_formatted}</td>
                <td>${purchase_rate_formatted}</td>
                <td>${item.supplier}</td>
            </tr>
        `;
    });

    html += `
                </tbody>
            </table>
        </div>
    `;
    return html;
}

function make_MR(frm){

    if (frm.doc.docstatus === 1) {
                frm.add_custom_button(
					__("Material Requst"),
					function () {
						frappe.model.open_mapped_doc({
							method: "power_app.mapper.make_material_request_from_quotation",
							frm: frm,
                            args: {}
						});
					},
					__("Create")
				);
    }
}

