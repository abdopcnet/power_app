import frappe
from datetime import date
from frappe import _, msgprint, throw
from frappe.model.mapper import get_mapped_doc
from frappe.utils import today
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html

@frappe.whitelist()
def make_material_request_from_quotation(source, target=None):
    """
    Creates a Material Request from a Quotation.
    Maps item details and sets the Material Request Type to 'Purchase'.
    """
    
    # Define the core mapping settings
    def set_missing_values( source, target):
        # Set the Material Request Type
        target.material_request_type = "Purchase"
        # target.schedule_date = source.transaction_date or frappe.utils.today()
        target.company = source.company
        target.custom_create_from_dc = "Material Request"
        target.custom_dc_refrance = source.name
        target.run_method("set_missing_values")

    # Execute the mapping process
    doc = get_mapped_doc(
        "Quotation",
        source,
        {
            "Quotation": {
                "doctype": "Material Request",
                "validation": {
                    "docstatus": ["=", 1] # Only map from submitted Quotations
                },
                "field_map": {

                } ,
            },
            "Quotation Item": {
                "doctype": "Material Request Item",
                "field_map": {
                    "item_code": "item_code", # Default field mapping
                    "qty": "qty",             # Default field mapping
                },
            }
        },
        target,
        set_missing_values
    )
    
    return doc


