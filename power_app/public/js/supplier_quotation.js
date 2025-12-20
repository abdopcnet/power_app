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
