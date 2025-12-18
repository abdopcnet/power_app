frappe.ui.form.on('Supplier Quotation', {
  refresh(frm) {
    if (!frm.is_new()) {
        frappe.call({
            method: "power_app.customization.check_quotation_linked",
            args: {
                doc: frm.doc.name, 
            },
            callback: function (r) {
                if (r.message) {
                    console.log(r.message); 
                    update_quotation(frm , r.message);
                } 
            },
        });
    }   
  },

});

function update_quotation(frm , q){
    if (frm.doc.docstatus === 1) {
                frm.add_custom_button(
					__("Update Qutation"),
					function () {
                        console.log("Quotation")
                        console.log(q)
                        // frappe.route_options = {
                        //     "Quotation": sq
                        // };
                        frappe.call({
                            method: "power_app.customization.update_quotation_linked",
                            args: {
                                doc: frm.doc.name, 
                                q : q,
                            },
                            callback: function (r) {
                                if (r.message) {
                                    console.log(r.message); 
                                } 
                            },
                        });
                         frappe.set_route('Form',"Quotation",q);
					
					},
				);
    }
}
