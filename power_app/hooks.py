app_name = "power_app"
app_title = "Power App"
app_publisher = "Hadeel Milad"
app_description = "Customization Workflow for a Power Key Compnay"
app_email = "hadeelnr88@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "power_app",
# 		"logo": "/assets/power_app/logo.png",
# 		"title": "Power App",
# 		"route": "/power_app",
# 		"has_permission": "power_app.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/power_app/css/power_app.css"
# app_include_js = "/assets/power_app/js/power_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/power_app/css/power_app.css"
# web_include_js = "/assets/power_app/js/power_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "power_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Quotation": "public/js/quotation.js",
    "Supplier Quotation": "public/js/supplier_quotation.js",

}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "power_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "power_app.utils.jinja_methods",
# 	"filters": "power_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "power_app.install.before_install"
# after_install = "power_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "power_app.uninstall.before_uninstall"
# after_uninstall = "power_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "power_app.utils.before_app_install"
# after_app_install = "power_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "power_app.utils.before_app_uninstall"
# after_app_uninstall = "power_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "power_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
    "Landed Cost Voucher": "power_app.landed_cost_voucher.LandedCostVoucher"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Quotation": {
        "validate": "power_app.quotation.quotation_validate",
        "before_submit": "power_app.quotation.quotation_before_submit",
        # "on_cancel": "method",
        # "on_trash": "method"
    },
    "Sales Order": {
        "before_save": "power_app.sales_order.copy_quotation_expenses_to_sales_order",
        "on_submit": "power_app.sales_order.create_je_from_service_expence",
        # "on_cancel": "method",
        # "on_trash": "method"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"power_app.tasks.all"
# 	],
# 	"daily": [
# 		"power_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"power_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"power_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"power_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "power_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# Override make_sales_order to copy expenses table from Quotation to Sales Order
override_whitelisted_methods = {
    "erpnext.selling.doctype.quotation.quotation.make_sales_order": "power_app.quotation_mapper.make_sales_order"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "power_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["power_app.utils.before_request"]
# after_request = ["power_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["power_app.utils.before_job"]
# after_job = ["power_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"power_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
