frappe.ui.form.on('Quotation', {
	refresh(frm) {
		// Show/hide Submit button based on Approved checkbox
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			// Show Submit button only if Approved is checked
			setTimeout(() => {
				const submit_btn = frm.page.inner_toolbar.find(
					'button[data-label="Submit"], button:contains("Submit")',
				);
				const submit_btn_by_class = frm.page.inner_toolbar
					.find('.btn-primary')
					.filter(function () {
						return $(this).text().trim() === __('Submit');
					});

				if (frm.doc.custom_approved) {
					// Show Submit button if Approved is checked
					if (submit_btn.length) {
						submit_btn.show();
					}
					if (submit_btn_by_class.length) {
						submit_btn_by_class.show();
					}
				} else {
					// Hide Submit button if Approved is not checked
					if (submit_btn.length) {
						submit_btn.hide();
					}
					if (submit_btn_by_class.length) {
						submit_btn_by_class.hide();
					}
				}
			}, 100);
		}

		// Show Create Sales Order button when Quotation is Submitted and Approved
		if (frm.doc.docstatus === 1 && frm.doc.custom_approved) {
			// Add Create Sales Order button (standard ERPNext behavior)
			// This will be handled by ERPNext's standard button, but we ensure it's visible
		}

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
		add_compare_supplier_quotations_button(frm);
		add_select_items_from_supplier_quotations_button(frm);
		frm.trigger('set_item_query');
		// Set query for a Link field in the child table named 'items' for a service new featur on the quotation doctype
	},
	set_item_query: function (frm) {
		frm.set_query('item_code', 'items', function () {
			console.log('[quotation.js] (Item query triggered)');
			if (frm.doc.custom_services) {
				return {
					filters: {
						// Apply filters based on fields in the current child row
						// For example, filter 'item_code' based on 'item_group' in the same row
						is_stock_item: 0,
						is_sales_item: 1,
						has_variants: 0,

						// Or apply filters based on fields in the parent document
						// 'is_sales_item': doc.is_sales_order // Assuming 'is_sales_order' is a field in the parent DocType
					},
				};
			} else {
				return {
					query: 'erpnext.controllers.queries.item_query',
					filters: { is_sales_item: 1, customer: frm.doc.customer, has_variants: 0 },
				};
			}
		});
	},
	custom_services: function (frm) {
		frm.trigger('set_item_query');
	},
});

// Handle Service Expense table changes - Update rates immediately
let expense_update_timeout = null;
let is_recalculating = false;

function trigger_expense_recalculation(frm) {
	// Skip if already recalculating to avoid recursion
	if (is_recalculating) {
		return;
	}

	// Debounce to avoid multiple saves
	if (expense_update_timeout) {
		clearTimeout(expense_update_timeout);
	}

	expense_update_timeout = setTimeout(() => {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			is_recalculating = true;
			console.log('[quotation.js] (Recalculating rates after expense change)');
			// Save silently to trigger validate event
			frm.save(undefined, undefined, undefined, true)
				.then(() => {
					frm.reload_doc();
					is_recalculating = false;
				})
				.catch(() => {
					is_recalculating = false;
				});
		}
	}, 500); // Wait 500ms after last change
}

frappe.ui.form.on('Service Expense', {
	amount: function (frm, cdt, cdn) {
		// When amount is changed, trigger recalculation
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			console.log('[quotation.js] (Expense amount changed)');
			trigger_expense_recalculation(frm);
		}
	},
	custom_quotation_expenses_table_add: function (frm, cdt, cdn) {
		// When expense row is added, trigger recalculation
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			console.log('[quotation.js] (Expense row added)');
			trigger_expense_recalculation(frm);
		}
	},
	custom_quotation_expenses_table_remove: function (frm, cdt, cdn) {
		// When expense row is removed, trigger recalculation
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			console.log('[quotation.js] (Expense row removed)');
			trigger_expense_recalculation(frm);
		}
	},
});

// Function to add the "Show Item History" button and handle its logic
function add_show_item_history_button(frm) {
	// Only show the button if items exist and the form is not new
	if (frm.doc.items && frm.doc.items.length > 0 && !frm.is_new()) {
		frm.page.add_inner_button(
			__('Show Item History'),
			async function () {
				try {
					// 1. Get unique items from the current quotation
					const unique_items = [...new Set(frm.doc.items.map((item) => item.item_code))];

					if (unique_items.length === 0) {
						frappe.msgprint(__('No items in the current quotation.'));
						return;
					}

					frappe.show_alert(
						{ message: __('Fetching item details...'), indicator: 'blue' },
						3,
					);

					// 2. Fetch the required details for each unique item
					const item_details = await fetch_item_details(frm, unique_items);

					// 3. Build HTML and show dialog
					const d = new frappe.ui.Dialog({
						title: __('Item Price & Stock Details'),
						fields: [
							{
								fieldtype: 'HTML',
								fieldname: 'item_details_html',
								options: build_item_details_html(item_details, frm.doc.currency),
							},
						],
						indicator: 'green',
					});
					d.show();
				} catch (e) {
					console.log(
						`[quotation.js] (Error fetching item details: ${e.message || 'Unknown'})`,
					);
					frappe.msgprint({
						title: __('Error'),
						message: __('Failed to fetch item details: ') + e.message,
						indicator: 'red',
					});
				}
			},
			null,
			'info',
		);
	}
}
// Function to fetch item-specific data
async function fetch_item_details(frm, item_codes) {
	const details_promises = item_codes.map(async (item_code) => {
		// --- 1. Get On Hand Quantity (CORRECTED FUNCTION PATH) ---
		const stock_res = await frappe.call({
			// *** CHANGE MADE HERE ***
			method: 'power_app.item.get_item_details',
			args: {
				item_code: item_code,
				// warehouse: frm.doc.warehouse || frappe.defaults.get_user_default('default_warehouse'),
				// The API often returns stock under the 'actual_qty' key
			},
		});
		console.log(`[quotation.js] (Item details fetched: ${item_code})`);
		// Adjusting how the result is read, as 'get_item_stock' returns an object
		const stock_qty =
			stock_res.message && stock_res.message.stock_qty ? stock_res.message.stock_qty : 0;

		// ... rest of your function remains the same ...
		// --- 2. Get Last Selling Rate ---
		// ... (your existing code for selling price) ...
		// const last_selling_rate = 0; // Placeholder
		const last_selling_rate =
			stock_res.message && stock_res.message.last_selling_rate
				? stock_res.message.last_selling_rate
				: 0;
		// --- 3. Get Last Supplier Purchase Rate ---
		// ... (your existing code for purchase rate) ...
		// const last_purchase_rate = 0; // Placeholder
		const last_purchase_rate =
			stock_res.message && stock_res.message.last_purchase_rate
				? stock_res.message.last_purchase_rate
				: 0;
		const supplier =
			stock_res.message && stock_res.message.supplier ? stock_res.message.supplier : 0;

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
	// Add CSS for better styling
	const css = `
		<style>
			.item-details-container {
				padding: 15px;
				background-color: #f8f9fa;
				border-radius: 4px;
				margin-bottom: 15px;
			}
			.item-details-note {
				background-color: #e7f3ff;
				border-left: 4px solid #1c5cab;
				padding: 10px 15px;
				margin-bottom: 15px;
				border-radius: 4px;
				font-size: 13px;
			}
			.item-details-table {
				width: 100%;
				border-collapse: collapse;
				background-color: #fff;
				box-shadow: 0 1px 3px rgba(0,0,0,0.1);
			}
			.item-details-table thead {
				background-color: #1c5cab;
				color: #fff;
			}
			.item-details-table thead th {
				padding: 12px 15px;
				text-align: left;
				font-weight: 600;
				font-size: 13px;
				border-bottom: 2px solid #0d3d6b;
			}
			.item-details-table tbody tr {
				border-bottom: 1px solid #e0e0e0;
				transition: background-color 0.2s;
			}
			.item-details-table tbody tr:hover {
				background-color: #f5f5f5;
			}
			.item-details-table tbody td {
				padding: 12px 15px;
				font-size: 13px;
				vertical-align: middle;
			}
			.item-details-table tbody td:first-child {
				font-weight: 500;
			}
			.item-details-table tbody td a {
				color: #1c5cab;
				text-decoration: none;
				font-weight: 500;
			}
			.item-details-table tbody td a:hover {
				text-decoration: underline;
			}
			.item-details-table .text-right {
				text-align: right;
			}
			.item-details-table .text-center {
				text-align: center;
			}
		</style>
	`;

	let html =
		css +
		`
		<div class="item-details-container">
			<div class="item-details-note">
				<strong>${__('Note:')}</strong> ${__(
			'Stock Qty is based on the current default/selected warehouse.',
		)}
			</div>
			<table class="item-details-table">
				<thead>
					<tr>
						<th style="width: 20%;">${__('Item Code')}</th>
						<th style="width: 15%;" class="text-center">${__('Qty in Warehouse')}</th>
						<th style="width: 20%;" class="text-right">${__('Last Selling Rate')}</th>
						<th style="width: 20%;" class="text-right">${__('Last Purchase Rate')}</th>
						<th style="width: 25%;">${__('Last Purchase Supplier')}</th>
					</tr>
				</thead>
				<tbody>
	`;

	item_details.forEach((item) => {
		const selling_rate_formatted = frappe.format(item.last_selling_rate, {
			fieldtype: 'Currency',
			options: currency,
		});
		const purchase_rate_formatted = frappe.format(item.last_purchase_rate, {
			fieldtype: 'Currency',
			options: currency,
		});

		// Format stock quantity
		const qty_formatted = frappe.format(item.stock_qty, { fieldtype: 'Float' });

		// Escape HTML to prevent XSS
		const item_code_escaped = frappe.utils.escape_html(item.item_code);
		const supplier_escaped = frappe.utils.escape_html(item.supplier);

		html += `
			<tr>
				<td>
					<a href="/app/item/${item.item_code}" target="_blank" rel="noopener">
						${item_code_escaped}
					</a>
				</td>
				<td class="text-center">${qty_formatted}</td>
				<td class="text-right">${selling_rate_formatted || '-'}</td>
				<td class="text-right">${purchase_rate_formatted || '-'}</td>
				<td>${supplier_escaped}</td>
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

function make_MR(frm) {
	// Allow creating Material Request from Draft Quotation
	// This is needed for the workflow: Draft Quotation → Material Request → RFQ → Supplier Quotations
	if (frm.doc.docstatus === 0 && !frm.is_new()) {
		frm.page.add_inner_button(
			__('Material Request'),
			function () {
				frappe.model.open_mapped_doc({
					method: 'power_app.material_request.make_material_request_from_quotation',
					frm: frm,
					args: {},
				});
			},
			null, // No group, makes it a standalone button
			'info', // Light blue color (different from primary)
		);
	}
}

// Function to add "Compare Supplier Quotations" button
function add_compare_supplier_quotations_button(frm) {
	// Show button when quotation is in Draft status
	if (frm.doc.docstatus === 0 && !frm.is_new()) {
		frm.page.add_inner_button(
			__('Compare Supplier Quotations'),
			function () {
				// Get Material Requests linked to this Quotation
				frappe.call({
					method: 'power_app.quotation.get_material_requests_from_quotation',
					args: {
						quotation_name: frm.doc.name,
					},
					callback: function (r) {
						if (r.message && r.message.length > 0) {
							// If multiple Material Requests, show selection dialog
							if (r.message.length > 1) {
								show_material_request_selection_dialog(frm, r.message);
							} else {
								// Single Material Request, open report directly
								const mr_data = r.message[0];
								open_supplier_quotation_comparison(frm, mr_data);
							}
						} else {
							// No Material Request found, open report without filter
							const reportUrl = build_supplier_quotation_comparison_url(
								frm.doc.company,
								null,
							);
							window.open(reportUrl, '_blank');
							frappe.show_alert(
								{
									message: __(
										'No Material Request found. Opening report without filter.',
									),
									indicator: 'orange',
								},
								5,
							);
						}
					},
					error: function (r) {
						// On error, open report without filter
						const reportUrl = build_supplier_quotation_comparison_url(
							frm.doc.company,
							null,
						);
						window.open(reportUrl, '_blank');
					},
				});
			},
			null,
			'warning',
		);
	}
}

// Function to show Material Request selection dialog
function show_material_request_selection_dialog(frm, mr_list) {
	// Build options for Material Request selection
	const options = mr_list.map((mr) => {
		const label = `${mr.material_request} - ${frappe.datetime.str_to_user(
			mr.transaction_date,
		)} (${mr.status})`;
		return { label: label, value: mr.material_request, rfq_name: mr.rfq_name };
	});

	// Create dialog
	const d = new frappe.ui.Dialog({
		title: __('Select Material Request'),
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'message',
				options: `<p>${__(
					'Please select which Material Request you want to display supplier quotation comparison for',
				)}</p>`,
			},
			{
				fieldtype: 'Select',
				fieldname: 'material_request',
				label: __('Material Request'),
				options: options.map((opt) => opt.label).join('\n'),
				reqd: 1,
			},
		],
		primary_action_label: __('Open Report'),
		primary_action: function () {
			const values = d.get_values();
			if (values && values.material_request) {
				// Find selected Material Request data
				const selectedMr = mr_list.find(
					(mr) => mr.material_request === values.material_request,
				);
				if (selectedMr) {
					open_supplier_quotation_comparison(frm, selectedMr);
					d.hide();
				}
			}
		},
	});

	d.show();
}

// Function to open Supplier Quotation Comparison report
function open_supplier_quotation_comparison(frm, mr_data) {
	if (mr_data.rfq_name) {
		// Build report URL with RFQ filter
		const reportUrl = build_supplier_quotation_comparison_url(
			frm.doc.company,
			mr_data.rfq_name,
		);
		window.open(reportUrl, '_blank');
	} else {
		// No RFQ found for this Material Request
		const reportUrl = build_supplier_quotation_comparison_url(frm.doc.company, null);
		window.open(reportUrl, '_blank');
		frappe.show_alert(
			{
				message: __(
					'No Request for Quotation found for selected Material Request. Opening report without filter.',
				),
				indicator: 'orange',
			},
			5,
		);
	}
}

// Function to build Supplier Quotation Comparison report URL
function build_supplier_quotation_comparison_url(company, rfq_name) {
	// Get date range (last 30 days to today)
	const today = frappe.datetime.get_today();
	const fromDate = frappe.datetime.add_months(today, -1);

	// Base URL
	let url = '/app/query-report/Supplier%20Quotation%20Comparison?';

	// Add filters
	url += `company=${encodeURIComponent(company)}`;
	url += `&from_date=${fromDate}`;
	url += `&to_date=${today}`;
	url += `&categorize_by=${encodeURIComponent('Categorize by Supplier')}`;

	// Add RFQ filter if provided
	if (rfq_name) {
		url += `&request_for_quotation=${encodeURIComponent(rfq_name)}`;
	}

	return url;
}

// Function to add "Select Items from Supplier Quotations" button
function add_select_items_from_supplier_quotations_button(frm) {
	// Show button when quotation is in Draft status (for editing)
	// Or when Submitted (for viewing only)
	if (!frm.is_new()) {
		if (frm.doc.docstatus === 0) {
			// Draft: Show button with full functionality
			frm.page.add_inner_button(
				__('Select Items from Supplier Quotations'),
				function () {
					show_item_selection_dialog(frm);
				},
				null,
				'success',
			);
		} else if (frm.doc.docstatus === 1) {
			// Submitted: Show button for viewing only (no Add Selected Items)
			frm.page.add_inner_button(
				__('View Supplier Quotation Items'),
				function () {
					show_item_selection_dialog_readonly(frm);
				},
				null,
				'info',
			);
		}
	}
}

// Function to show item selection dialog (Step 4 - UI only, display items)
function show_item_selection_dialog(frm) {
	// Show loading message
	frappe.show_alert(
		{ message: __('Fetching supplier quotation items...'), indicator: 'blue' },
		3,
	);

	// Call server method to get supplier quotation items
	frappe.call({
		method: 'power_app.quotation.get_supplier_quotation_items',
		args: {
			quotation_name: frm.doc.name,
		},
		callback: function (r) {
			if (r.message && r.message.length > 0) {
				console.log(`[quotation.js] (Supplier items fetched: ${r.message.length} items)`);
				show_item_selection_dialog_content(frm, r.message);
			} else {
				frappe.msgprint({
					title: __('No Items Found'),
					message: __(
						'No supplier quotation items found. Please create Material Request and Supplier Quotations first.',
					),
					indicator: 'orange',
				});
			}
		},
		error: function (r) {
			console.log(
				`[quotation.js] (Error fetching supplier items readonly: ${
					r.message || 'Unknown'
				})`,
			);
			frappe.msgprint({
				title: __('Error'),
				message:
					__('Failed to fetch supplier quotation items: ') +
					(r.message || 'Unknown error'),
				indicator: 'red',
			});
		},
	});
}

// Function to show items in read-only mode (when Quotation is Submitted)
function show_item_selection_dialog_readonly(frm) {
	// Show loading message
	frappe.show_alert(
		{ message: __('Fetching supplier quotation items...'), indicator: 'blue' },
		3,
	);

	// Call server method to get supplier quotation items
	frappe.call({
		method: 'power_app.quotation.get_supplier_quotation_items',
		args: {
			quotation_name: frm.doc.name,
		},
		callback: function (r) {
			if (r.message && r.message.length > 0) {
				show_item_selection_dialog_content_readonly(frm, r.message);
			} else {
				frappe.msgprint({
					title: __('No Items Found'),
					message: __('No supplier quotation items found.'),
					indicator: 'orange',
				});
			}
		},
		error: function (r) {
			frappe.msgprint({
				title: __('Error'),
				message:
					__('Failed to fetch supplier quotation items: ') +
					(r.message || 'Unknown error'),
				indicator: 'red',
			});
		},
	});
}

// Function to display items in read-only dialog (no Add Selected Items button)
function show_item_selection_dialog_content_readonly(frm, items) {
	// Build HTML table for items (read-only, no checkboxes)
	let html = build_supplier_items_table_html_readonly(items, frm.doc.currency);

	// Create dialog with wider width (read-only)
	const d = new frappe.ui.Dialog({
		title: __('Supplier Quotation Items (Read Only)'),
		size: 'extra-large',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'items_table_html',
				options: html,
			},
		],
		// No primary_action - read-only view
	});

	d.show();
}

// Function to display items in dialog (Step 5 - with multi-select enabled)
function show_item_selection_dialog_content(frm, items) {
	// Build HTML table for items
	let html = build_supplier_items_table_html(items, frm.doc.currency);

	// Create dialog with wider width
	const d = new frappe.ui.Dialog({
		title: __('Select Items from Supplier Quotations'),
		size: 'extra-large',
		fields: [
			{
				fieldtype: 'HTML',
				fieldname: 'items_table_html',
				options: html,
			},
		],
		primary_action_label: __('Add Selected Items'),
		primary_action: function () {
			// Get selected items
			const selectedItems = get_selected_items_from_dialog(d);
			console.log(`[quotation.js] (Selected items: ${selectedItems.length})`);
			if (selectedItems.length === 0) {
				frappe.msgprint({
					title: __('No Items Selected'),
					message: __('Please select at least one item to add.'),
					indicator: 'orange',
				});
				return;
			}

			// Call server method to add items
			frappe.call({
				method: 'power_app.quotation.add_items_from_supplier_quotations',
				args: {
					quotation_name: frm.doc.name,
					selected_items: selectedItems,
				},
				callback: function (r) {
					if (r.message) {
						console.log(
							`[quotation.js] (Items added successfully: ${selectedItems.length})`,
						);
						frappe.show_alert(
							{
								message: __('Successfully added {0} item(s) to quotation', [
									selectedItems.length,
								]),
								indicator: 'green',
							},
							5,
						);
						// Refresh form to show new items
						frm.reload_doc();
						// Close dialog
						d.hide();
					}
				},
				error: function (r) {
					console.log(`[quotation.js] (Error adding items: ${r.message || 'Unknown'})`);
					frappe.msgprint({
						title: __('Error'),
						message: __('Failed to add items: ') + (r.message || 'Unknown error'),
						indicator: 'red',
					});
				},
			});
		},
	});

	// Enable checkboxes and add select all functionality
	setup_item_selection_checkboxes(d, items.length);

	d.show();
}

// Function to setup checkboxes and select all functionality (Step 5)
function setup_item_selection_checkboxes(dialog, totalItems) {
	// Wait for dialog to be fully rendered
	setTimeout(() => {
		// Enable all checkboxes
		const checkboxes = dialog.$wrapper.find('.item-select-checkbox');
		checkboxes.prop('disabled', false);

		// Add select all / deselect all button
		const selectAllHtml = `
			<div style="margin-bottom: 10px;">
				<button type="button" class="btn btn-sm btn-secondary" id="select-all-items-btn">
					${__('Select All')}
				</button>
				<button type="button" class="btn btn-sm btn-secondary" id="deselect-all-items-btn" style="margin-left: 5px;">
					${__('Deselect All')}
				</button>
				<span id="selected-count" style="margin-left: 15px; font-weight: bold; color: #1c5cab;">
					${__('0 items selected')}
				</span>
			</div>
		`;

		// Insert select all buttons before the table
		dialog.$wrapper.find('.form-section').first().before(selectAllHtml);

		// Handle select all button
		dialog.$wrapper.find('#select-all-items-btn').on('click', function () {
			checkboxes.prop('checked', true);
			update_selected_count(dialog);
		});

		// Handle deselect all button
		dialog.$wrapper.find('#deselect-all-items-btn').on('click', function () {
			checkboxes.prop('checked', false);
			update_selected_count(dialog);
		});

		// Handle individual checkbox changes
		checkboxes.on('change', function () {
			update_selected_count(dialog);
		});

		// Initial count update
		update_selected_count(dialog);
	}, 100);
}

// Function to update selected items count (Step 5)
function update_selected_count(dialog) {
	const checked = dialog.$wrapper.find('.item-select-checkbox:checked').length;
	const total = dialog.$wrapper.find('.item-select-checkbox').length;
	const countElement = dialog.$wrapper.find('#selected-count');

	if (countElement.length) {
		countElement.text(`${checked} ${__('of')} ${total} ${__('items selected')}`);
	}
}

// Function to get selected items from dialog (Step 5)
function get_selected_items_from_dialog(dialog) {
	const selectedItems = [];
	const checkedBoxes = dialog.$wrapper.find('.item-select-checkbox:checked');

	checkedBoxes.each(function () {
		const $checkbox = $(this);
		selectedItems.push({
			item_id: $checkbox.data('item-id'),
			supplier_quotation: $checkbox.data('supplier-quotation'),
			item_code: $checkbox.data('item-code'),
			rate: parseFloat($checkbox.data('rate')) || 0,
			qty: parseFloat($checkbox.data('qty')) || 0,
			uom: $checkbox.data('uom') || '',
			item_name: $checkbox.data('item-name') || '',
		});
	});

	return selectedItems;
}

// Function to build HTML table for supplier items (read-only, no checkboxes)
function build_supplier_items_table_html_readonly(items, currency) {
	let html = `
		<div class="form-section card-section" style="margin-top:0; overflow-x: auto;">
			<table class="table table-bordered table-hover" style="width: 100%; min-width: 800px; table-layout: fixed;">
				<thead style="color: #1c5cab;">
					<tr>
						<th style="width: 120px;">${__('Item Code')}</th>
						<th style="width: 200px;">${__('Item Name')}</th>
						<th style="width: 150px;">${__('Supplier')}</th>
						<th style="width: 150px;">${__('Supplier Quotation')}</th>
						<th style="width: 80px; text-align: right;">${__('Qty')}</th>
						<th style="width: 80px;">${__('UOM')}</th>
						<th style="width: 120px; text-align: right;">${__('Rate')}</th>
					</tr>
				</thead>
				<tbody>
	`;

	items.forEach((item) => {
		const rate_formatted = frappe.format(item.rate, {
			fieldtype: 'Currency',
			options: currency,
		});

		// Truncate long text to prevent overflow
		const item_code = (item.item_code || '').substring(0, 20);
		const item_name = (item.item_name || '').substring(0, 30);
		const supplier_name = (item.supplier_name || item.supplier || '').substring(0, 25);
		const sq_name = (item.supplier_quotation || '').substring(0, 20);

		html += `
			<tr>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
					<a href="/app/item/${frappe.utils.escape_html(
						item.item_code || '',
					)}" target="_blank" title="${frappe.utils.escape_html(
			item.item_code || '',
		)}">${frappe.utils.escape_html(item_code)}</a>
				</td>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${frappe.utils.escape_html(
					item.item_name || '',
				)}">${frappe.utils.escape_html(item_name)}</td>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${frappe.utils.escape_html(
					item.supplier_name || item.supplier || '',
				)}">${frappe.utils.escape_html(supplier_name)}</td>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
					<a href="/app/supplier-quotation/${frappe.utils.escape_html(
						item.supplier_quotation || '',
					)}" target="_blank" title="${frappe.utils.escape_html(
			item.supplier_quotation || '',
		)}">${frappe.utils.escape_html(sq_name)}</a>
				</td>
				<td style="text-align: right;">${item.qty || 0}</td>
				<td>${item.uom || ''}</td>
				<td style="text-align: right;">${rate_formatted}</td>
			</tr>
		`;
	});

	html += `
				</tbody>
			</table>
		</div>
		<p><strong>${__('Note:')}</strong> ${__(
		'This is a read-only view. Items cannot be modified after Quotation is submitted.',
	)}</p>
	`;

	return html;
}

// Function to build HTML table for supplier items
function build_supplier_items_table_html(items, currency) {
	let html = `
		<div class="form-section card-section" style="margin-top:0; overflow-x: auto;">
			<table class="table table-bordered table-hover" style="width: 100%; min-width: 900px; table-layout: fixed;">
				<thead style="color: #1c5cab;">
					<tr>
						<th style="width: 50px; text-align: center;">${__('Select')}</th>
						<th style="width: 120px;">${__('Item Code')}</th>
						<th style="width: 200px;">${__('Item Name')}</th>
						<th style="width: 150px;">${__('Supplier')}</th>
						<th style="width: 150px;">${__('Supplier Quotation')}</th>
						<th style="width: 80px; text-align: right;">${__('Qty')}</th>
						<th style="width: 80px;">${__('UOM')}</th>
						<th style="width: 120px; text-align: right;">${__('Rate')}</th>
					</tr>
				</thead>
				<tbody>
	`;

	items.forEach((item) => {
		const rate_formatted = frappe.format(item.rate, {
			fieldtype: 'Currency',
			options: currency,
		});

		// Truncate long text to prevent overflow
		const item_code = (item.item_code || '').substring(0, 20);
		const item_name = (item.item_name || '').substring(0, 30);
		const supplier_name = (item.supplier_name || item.supplier || '').substring(0, 25);
		const sq_name = (item.supplier_quotation || '').substring(0, 20);

		html += `
			<tr>
				<td style="text-align: center;">
					<input type="checkbox" class="item-select-checkbox" data-item-id="${item.name}"
						data-supplier-quotation="${item.supplier_quotation}"
						data-item-code="${item.item_code}"
						data-rate="${item.rate}"
						data-qty="${item.qty || 0}"
						data-uom="${item.uom || ''}"
						data-item-name="${item.item_name || ''}"
						data-supplier="${item.supplier || ''}"
						data-supplier-name="${item.supplier_name || ''}">
				</td>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
					<a href="/app/item/${item.item_code}" target="_blank" title="${
			item.item_code || ''
		}">${item_code}</a>
				</td>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${
					item.item_name || ''
				}">${item_name}</td>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${
					item.supplier_name || item.supplier || ''
				}">${supplier_name}</td>
				<td style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
					<a href="/app/supplier-quotation/${item.supplier_quotation}" target="_blank" title="${
			item.supplier_quotation || ''
		}">${sq_name}</a>
				</td>
				<td style="text-align: right;">${item.qty || 0}</td>
				<td>${item.uom || ''}</td>
				<td style="text-align: right;">${rate_formatted}</td>
			</tr>
		`;
	});

	html += `
				</tbody>
			</table>
		</div>
		<p><strong>${__('Note:')}</strong> ${__(
		'Select items from the table below. Adding items to quotation will be enabled in next step.',
	)}</p>
	`;

	return html;
}
