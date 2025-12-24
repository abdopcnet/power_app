frappe.ui.form.on('Supplier Quotation', {
	refresh(frm) {
		if (!frm.is_new()) {
			frappe.call({
				method: 'power_app.supplier_quotation.check_quotation_linked',
				args: {
					doc: frm.doc.name,
				},
				callback: function (r) {
					if (r.message) {
						console.log(`[supplier_quotation.js] (Quotation linked: ${r.message})`);
						update_quotation(frm, r.message);
					}
				},
			});
		}
		// Update total expenses when form is refreshed (only for draft/new documents)
		if (frm.doc.docstatus === 0 || frm.doc.__islocal) {
			update_total_expenses(frm);
		}
	},
	custom_expense_template: function (frm) {
		// Only fetch template data for draft/new documents
		if (frm.doc.docstatus !== 0 && !frm.doc.__islocal) {
			return;
		}

		if (frm.doc.custom_expense_template) {
			fetch_expense_template(frm);
		} else {
			// Clear expenses if template is cleared
			frm.clear_table('custom_service_expense');
			frm.refresh_field('custom_service_expense');
			update_total_expenses(frm);
		}
	},
});

/**
 * Fetch expense template data and populate custom_service_expense child table
 */
function fetch_expense_template(frm) {
	if (!frm.doc.custom_expense_template) {
		return;
	}

	frappe.call({
		method: 'power_app.supplier_quotation.get_expense_template_data',
		args: {
			template_name: frm.doc.custom_expense_template,
		},
		callback: function (r) {
			if (!r.exc && r.message && r.message.length > 0) {
				// Clear existing expenses
				frm.clear_table('custom_service_expense');

				// Add expenses from template
				r.message.forEach(function (expense) {
					let row = frm.add_child('custom_service_expense');
					row.service_expense_type = expense.service_expense_type;
					row.company = expense.company;
					row.default_account = expense.default_account;
					row.amount = expense.amount;
					row.description = expense.description;
				});

				frm.refresh_field('custom_service_expense');
				update_total_expenses(frm);
			}
		},
	});
}

/**
 * Calculate and update total expenses in custom_total_expenses field
 * Only works on draft or new documents
 */
function update_total_expenses(frm) {
	// Only update if document is draft or new
	if (frm.doc.docstatus !== 0 && !frm.doc.__islocal) {
		return;
	}

	if (!frm.doc.custom_service_expense || frm.doc.custom_service_expense.length === 0) {
		frm.set_value('custom_total_expenses', 0);
		return;
	}

	let total_expenses = 0;
	frm.doc.custom_service_expense.forEach((expense) => {
		total_expenses += flt(expense.amount) || 0;
	});

	frm.set_value('custom_total_expenses', total_expenses);
}

frappe.ui.form.on('Service Expense', {
	amount: function (frm, cdt, cdn) {
		// When amount is changed, update total (only for draft/new documents)
		update_total_expenses(frm);
	},
});

frappe.ui.form.on('Supplier Quotation', {
	custom_service_expense_add: function (frm, cdt, cdn) {
		// When expense row is added, update total (only for draft/new documents)
		update_total_expenses(frm);
	},
	custom_service_expense_remove: function (frm, cdt, cdn) {
		// When expense row is removed, update total (only for draft/new documents)
		update_total_expenses(frm);
	},
});

function update_quotation(frm, q) {
	if (frm.doc.docstatus === 1) {
		frm.page.add_inner_button(
			__('Update Qutation'),
			function () {
				console.log(`[supplier_quotation.js] (Updating quotation: ${q})`);
				// frappe.route_options = {
				//     "Quotation": sq
				// };
				frappe.call({
					method: 'power_app.supplier_quotation.update_quotation_linked',
					args: {
						doc: frm.doc.name,
						q: q,
					},
					callback: function (r) {
						if (r.message) {
							console.log(
								`[supplier_quotation.js] (Quotation updated successfully)`,
							);
						}
					},
				});
				frappe.set_route('Form', 'Quotation', q);
			},
			null,
			'success',
		);
	}
}
