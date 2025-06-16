using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using Microsoft.Extensions.Logging;
using YourApp.BusinessLogic;

namespace YourApp.Web
{
    /// <summary>
    /// Customer management page code-behind
    /// This demonstrates the backend page pattern that the MCP server can analyze
    /// </summary>
    public partial class CustomerManagement : System.Web.UI.Page
    {
        private readonly CustomerManager _customerManager;
        private readonly ILogger<CustomerManagement> _logger;
        
        // Page properties for data binding
        protected List<Customer> CustomerList { get; set; }
        protected Customer CurrentCustomer { get; set; }
        
        public CustomerManagement()
        {
            // In a real application, these would be injected via DI container
            // This is a simplified example for demonstration
            // _customerManager = ServiceLocator.GetService<CustomerManager>();
            // _logger = ServiceLocator.GetService<ILogger<CustomerManagement>>();
        }
        
        protected async void Page_Load(object sender, EventArgs e)
        {
            if (!IsPostBack)
            {
                await InitializePageAsync();
            }
        }
        
        /// <summary>
        /// Initialize the page with default data
        /// </summary>
        private async Task InitializePageAsync()
        {
            try
            {
                // Load initial customer data
                await LoadCustomerDataAsync();
                
                // Setup dropdown lists
                SetupStatusDropdown();
                
                // Clear any previous messages
                HideMessage();
                
                _logger?.LogInformation("Customer management page initialized successfully");
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error initializing customer management page");
                ShowMessage("Error loading page. Please refresh and try again.", "danger");
            }
        }
        
        /// <summary>
        /// Load customer data into the grid
        /// </summary>
        private async Task LoadCustomerDataAsync()
        {
            try
            {
                // Get filter parameters from UI
                string searchName = txtSearchName.Text.Trim();
                bool? isActive = null;
                
                if (!string.IsNullOrEmpty(ddlStatusFilter.SelectedValue))
                {
                    isActive = Convert.ToBoolean(ddlStatusFilter.SelectedValue);
                }
                
                // Load data from business layer
                CustomerList = await _customerManager.GetCustomerListAsync(null, isActive ?? true, searchName);
                
                // Apply additional client-side filtering if needed
                if (!string.IsNullOrEmpty(searchName))
                {
                    CustomerList = CustomerList
                        .Where(c => c.CustomerName.ToLower().Contains(searchName.ToLower()))
                        .ToList();
                }
                
                // Bind to grid
                gvCustomers.DataSource = CustomerList;
                gvCustomers.DataBind();
                
                // Update result count
                lblResultCount.Text = $"Found {CustomerList.Count} customer(s)";
                
                ShowMessage($"Loaded {CustomerList.Count} customers successfully", "success");
                
                _logger?.LogInformation("Loaded {Count} customers for display", CustomerList.Count);
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error loading customer data");
                ShowMessage("Error loading customer data. Please try again.", "danger");
            }
        }
        
        /// <summary>
        /// Setup the status filter dropdown
        /// </summary>
        private void SetupStatusDropdown()
        {
            if (ddlStatusFilter.Items.Count == 0)
            {
                ddlStatusFilter.Items.Clear();
                ddlStatusFilter.Items.Add(new ListItem("All Customers", ""));
                ddlStatusFilter.Items.Add(new ListItem("Active Only", "true"));
                ddlStatusFilter.Items.Add(new ListItem("Inactive Only", "false"));
            }
        }
        
        #region Event Handlers
        
        /// <summary>
        /// Handle add new customer button click
        /// </summary>
        protected void btnAddCustomer_Click(object sender, EventArgs e)
        {
            try
            {
                // Clear form for new customer
                ClearCustomerForm();
                
                // Show edit panel
                pnlEditCustomer.Visible = true;
                pnlCustomerList.Visible = false;
                
                // Set form mode
                lblFormTitle.Text = "Add New Customer";
                btnSaveCustomer.Text = "Save Customer";
                
                // Focus on first field
                txtCustomerName.Focus();
                
                _logger?.LogInformation("Add customer form opened");
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error opening add customer form");
                ShowMessage("Error opening add customer form", "danger");
            }
        }
        
        /// <summary>
        /// Handle search button click
        /// </summary>
        protected async void btnSearch_Click(object sender, EventArgs e)
        {
            await LoadCustomerDataAsync();
        }
        
        /// <summary>
        /// Handle clear search button click
        /// </summary>
        protected async void btnClearSearch_Click(object sender, EventArgs e)
        {
            txtSearchName.Text = "";
            ddlStatusFilter.SelectedValue = "";
            await LoadCustomerDataAsync();
        }
        
        /// <summary>
        /// Handle refresh button click
        /// </summary>
        protected async void btnRefresh_Click(object sender, EventArgs e)
        {
            await LoadCustomerDataAsync();
        }
        
        /// <summary>
        /// Handle save customer button click
        /// </summary>
        protected async void btnSaveCustomer_Click(object sender, EventArgs e)
        {
            try
            {
                // Validate form data
                if (!ValidateCustomerForm())
                {
                    return;
                }
                
                // Create customer object from form
                var customer = CreateCustomerFromForm();
                
                // Save via business layer
                var savedCustomer = await _customerManager.SaveCustomerAsync(customer);
                
                // Show success message
                ShowMessage($"Customer '{savedCustomer.CustomerName}' saved successfully", "success");
                
                // Return to list view
                await ReturnToListView();
                
                _logger?.LogInformation("Customer {CustomerName} saved with ID {CustomerId}", 
                    savedCustomer.CustomerName, savedCustomer.CustomerID);
            }
            catch (ValidationException vex)
            {
                ShowMessage($"Validation Error: {vex.Message}", "warning");
                _logger?.LogWarning("Customer validation failed: {Message}", vex.Message);
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error saving customer");
                ShowMessage("Error saving customer. Please try again.", "danger");
            }
        }
        
        /// <summary>
        /// Handle cancel edit button click
        /// </summary>
        protected async void btnCancelEdit_Click(object sender, EventArgs e)
        {
            await ReturnToListView();
        }
        
        /// <summary>
        /// Handle grid view paging
        /// </summary>
        protected async void gvCustomers_PageIndexChanging(object sender, GridViewPageEventArgs e)
        {
            gvCustomers.PageIndex = e.NewPageIndex;
            await LoadCustomerDataAsync();
        }
        
        /// <summary>
        /// Handle grid view row commands
        /// </summary>
        protected async void gvCustomers_RowCommand(object sender, GridViewCommandEventArgs e)
        {
            try
            {
                int customerId = Convert.ToInt32(e.CommandArgument);
                
                if (e.CommandName == "EditCustomer")
                {
                    await EditCustomer(customerId);
                }
                else if (e.CommandName == "DeleteCustomer")
                {
                    await DeleteCustomer(customerId);
                }
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error handling grid row command");
                ShowMessage("Error processing request", "danger");
            }
        }
        
        /// <summary>
        /// Handle grid view row data bound for custom formatting
        /// </summary>
        protected void gvCustomers_RowDataBound(object sender, GridViewRowEventArgs e)
        {
            if (e.Row.RowType == DataControlRowType.DataRow)
            {
                var customer = (Customer)e.Row.DataItem;
                
                // Format inactive customers differently
                if (!customer.IsActive)
                {
                    e.Row.CssClass += " table-secondary text-muted";
                }
                
                // Add tooltips to action buttons
                var editButton = e.Row.FindControl("lnkEdit") as LinkButton;
                if (editButton != null)
                {
                    editButton.ToolTip = $"Edit {customer.CustomerName}";
                }
                
                var deleteButton = e.Row.FindControl("lnkDelete") as LinkButton;
                if (deleteButton != null)
                {
                    deleteButton.ToolTip = $"Delete {customer.CustomerName}";
                    deleteButton.OnClientClick = $"return confirm('Are you sure you want to delete {customer.CustomerName}?');";
                }
            }
        }
        
        #endregion
        
        #region Helper Methods
        
        /// <summary>
        /// Edit an existing customer
        /// </summary>
        private async Task EditCustomer(int customerId)
        {
            try
            {
                // Get customer data
                var customers = await _customerManager.GetCustomerListAsync(customerId);
                var customer = customers.FirstOrDefault();
                
                if (customer == null)
                {
                    ShowMessage("Customer not found", "warning");
                    return;
                }
                
                // Populate form with customer data
                PopulateCustomerForm(customer);
                
                // Show edit panel
                pnlEditCustomer.Visible = true;
                pnlCustomerList.Visible = false;
                
                // Set form mode
                lblFormTitle.Text = $"Edit Customer: {customer.CustomerName}";
                btnSaveCustomer.Text = "Update Customer";
                
                _logger?.LogInformation("Edit form opened for customer ID {CustomerId}", customerId);
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error loading customer for edit: {CustomerId}", customerId);
                ShowMessage("Error loading customer for edit", "danger");
            }
        }
        
        /// <summary>
        /// Delete a customer
        /// </summary>
        private async Task DeleteCustomer(int customerId)
        {
            try
            {
                bool success = await _customerManager.DeleteCustomerAsync(customerId);
                
                if (success)
                {
                    ShowMessage("Customer deleted successfully", "success");
                    await LoadCustomerDataAsync();
                }
                else
                {
                    ShowMessage("Error deleting customer", "danger");
                }
                
                _logger?.LogInformation("Customer ID {CustomerId} deleted", customerId);
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Error deleting customer ID {CustomerId}", customerId);
                ShowMessage("Error deleting customer", "danger");
            }
        }
        
        /// <summary>
        /// Return to list view from edit mode
        /// </summary>
        private async Task ReturnToListView()
        {
            pnlEditCustomer.Visible = false;
            pnlCustomerList.Visible = true;
            ClearCustomerForm();
            await LoadCustomerDataAsync();
        }
        
        /// <summary>
        /// Validate customer form data
        /// </summary>
        private bool ValidateCustomerForm()
        {
            bool isValid = true;
            var errors = new List<string>();
            
            if (string.IsNullOrWhiteSpace(txtCustomerName.Text))
            {
                errors.Add("Customer name is required");
                isValid = false;
            }
            
            if (!string.IsNullOrEmpty(txtEmail.Text) && !IsValidEmail(txtEmail.Text))
            {
                errors.Add("Please enter a valid email address");
                isValid = false;
            }
            
            if (!isValid)
            {
                ShowMessage($"Please correct the following errors: {string.Join(", ", errors)}", "warning");
            }
            
            return isValid;
        }
        
        /// <summary>
        /// Create customer object from form data
        /// </summary>
        private Customer CreateCustomerFromForm()
        {
            return new Customer
            {
                CustomerID = string.IsNullOrEmpty(hfCustomerID.Value) ? 0 : Convert.ToInt32(hfCustomerID.Value),
                CustomerName = txtCustomerName.Text.Trim(),
                Email = txtEmail.Text.Trim(),
                Phone = txtPhone.Text.Trim(),
                Address = txtAddress.Text.Trim(),
                City = txtCity.Text.Trim(),
                State = txtState.Text.Trim(),
                ZipCode = txtZipCode.Text.Trim(),
                IsActive = chkIsActive.Checked
            };
        }
        
        /// <summary>
        /// Populate form with customer data
        /// </summary>
        private void PopulateCustomerForm(Customer customer)
        {
            hfCustomerID.Value = customer.CustomerID.ToString();
            txtCustomerName.Text = customer.CustomerName;
            txtEmail.Text = customer.Email ?? "";
            txtPhone.Text = customer.Phone ?? "";
            txtAddress.Text = customer.Address ?? "";
            txtCity.Text = customer.City ?? "";
            txtState.Text = customer.State ?? "";
            txtZipCode.Text = customer.ZipCode ?? "";
            chkIsActive.Checked = customer.IsActive;
        }
        
        /// <summary>
        /// Clear customer form
        /// </summary>
        private void ClearCustomerForm()
        {
            hfCustomerID.Value = "";
            txtCustomerName.Text = "";
            txtEmail.Text = "";
            txtPhone.Text = "";
            txtAddress.Text = "";
            txtCity.Text = "";
            txtState.Text = "";
            txtZipCode.Text = "";
            chkIsActive.Checked = true;
        }
        
        /// <summary>
        /// Show message to user
        /// </summary>
        private void ShowMessage(string message, string type = "info")
        {
            lblMessage.Text = message;
            lblMessage.CssClass = $"alert alert-{type} alert-dismissible fade show";
            pnlMessage.Visible = true;
        }
        
        /// <summary>
        /// Hide message panel
        /// </summary>
        private void HideMessage()
        {
            pnlMessage.Visible = false;
        }
        
        /// <summary>
        /// Simple email validation
        /// </summary>
        private bool IsValidEmail(string email)
        {
            try
            {
                var addr = new System.Net.Mail.MailAddress(email);
                return addr.Address == email;
            }
            catch
            {
                return false;
            }
        }
        
        #endregion
    }
} 