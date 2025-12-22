frappe.ui.form.on('Sales Order', {
	transaction_date: function (frm) {
		// When transaction_date changes, update first payment_schedule row due_date
		if (frm.doc.payment_schedule && frm.doc.payment_schedule.length > 0) {
			const first_row = frm.doc.payment_schedule[0];
			const posting_date = frm.doc.transaction_date || frm.doc.posting_date;

			if (!posting_date) {
				return;
			}

			// Determine due_date: use delivery_date if after posting_date, otherwise use posting_date + 1 day
			let due_date = frm.doc.delivery_date || posting_date;
			const deliveryDate = frm.doc.delivery_date ? new Date(frm.doc.delivery_date) : null;
			const postingDate = new Date(posting_date);

			if (deliveryDate && deliveryDate >= postingDate) {
				due_date = frm.doc.delivery_date;
			} else {
				const postDate = new Date(posting_date);
				postDate.setDate(postDate.getDate() + 1);
				due_date = frappe.datetime.obj_to_str(postDate);
			}

			// Final check
			const finalDueDate = new Date(due_date);
			if (finalDueDate < postingDate) {
				const postDate = new Date(posting_date);
				postDate.setDate(postDate.getDate() + 1);
				due_date = frappe.datetime.obj_to_str(postDate);
			}

			frappe.model.set_value(first_row.doctype, first_row.name, 'due_date', due_date);
		}
	},
	delivery_date: function (frm) {
		// When delivery_date changes, update first payment_schedule row due_date
		if (
			frm.doc.delivery_date &&
			frm.doc.payment_schedule &&
			frm.doc.payment_schedule.length > 0
		) {
			const first_row = frm.doc.payment_schedule[0];
			const posting_date = frm.doc.transaction_date || frm.doc.posting_date;

			if (!posting_date) {
				return;
			}

			// Determine due_date: use delivery_date if after posting_date, otherwise use posting_date + 1 day
			let due_date = frm.doc.delivery_date;
			const deliveryDate = new Date(frm.doc.delivery_date);
			const postingDate = new Date(posting_date);

			if (deliveryDate < postingDate) {
				const postDate = new Date(posting_date);
				postDate.setDate(postDate.getDate() + 1);
				due_date = frappe.datetime.obj_to_str(postDate);
			}

			// Final check: ensure due_date is after posting_date
			const finalDueDate = new Date(due_date);
			if (finalDueDate < postingDate) {
				const postDate = new Date(posting_date);
				postDate.setDate(postDate.getDate() + 1);
				due_date = frappe.datetime.obj_to_str(postDate);
			}

			// Update due_date for first row (even if payment_term is not set)
			frappe.model.set_value(first_row.doctype, first_row.name, 'due_date', due_date);
		}
	},
	payment_schedule_remove: function (frm, cdt, cdn) {
		// After row removal, update first row due_date if needed
		if (
			frm.doc.delivery_date &&
			frm.doc.payment_schedule &&
			frm.doc.payment_schedule.length > 0
		) {
			const first_row = frm.doc.payment_schedule[0];
			const posting_date = frm.doc.transaction_date || frm.doc.posting_date;

			if (!posting_date) {
				return;
			}

			let due_date = frm.doc.delivery_date;
			const deliveryDate = new Date(frm.doc.delivery_date);
			const postingDate = new Date(posting_date);

			if (deliveryDate < postingDate) {
				const postDate = new Date(posting_date);
				postDate.setDate(postDate.getDate() + 1);
				due_date = frappe.datetime.obj_to_str(postDate);
			}

			// Final check
			const finalDueDate = new Date(due_date);
			if (finalDueDate < postingDate) {
				const postDate = new Date(posting_date);
				postDate.setDate(postDate.getDate() + 1);
				due_date = frappe.datetime.obj_to_str(postDate);
			}

			// Update due_date for first row (even if payment_term is not set)
			frappe.model.set_value(first_row.doctype, first_row.name, 'due_date', due_date);
		}
	},
});

frappe.ui.form.on('Payment Schedule', {
	payment_term: function (frm, cdt, cdn) {
		// When payment_term is set, update due_date to delivery_date for first row
		const row = locals[cdt][cdn];

		if (row.payment_term && frm.doc.delivery_date) {
			// Check if this is the first row
			const payment_schedule = frm.doc.payment_schedule || [];
			if (payment_schedule.length > 0 && payment_schedule[0].name === row.name) {
				const posting_date = frm.doc.transaction_date || frm.doc.posting_date;

				if (!posting_date) {
					return;
				}

				let due_date = frm.doc.delivery_date;
				const deliveryDate = new Date(frm.doc.delivery_date);
				const postingDate = new Date(posting_date);

				if (deliveryDate < postingDate) {
					const postDate = new Date(posting_date);
					postDate.setDate(postDate.getDate() + 1);
					due_date = frappe.datetime.obj_to_str(postDate);
				}

				// Final check
				const finalDueDate = new Date(due_date);
				if (finalDueDate < postingDate) {
					const postDate = new Date(posting_date);
					postDate.setDate(postDate.getDate() + 1);
					due_date = frappe.datetime.obj_to_str(postDate);
				}

				frappe.model.set_value(cdt, cdn, 'due_date', due_date);
			}
		}
	},
});
