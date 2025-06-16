<%@ Page Title="Customer Management" Language="C#" MasterPageFile="~/Site.Master" 
    AutoEventWireup="true" CodeBehind="CustomerManagement.aspx.cs" 
    Inherits="YourApp.Web.CustomerManagement" %>

<asp:Content ID="Content1" ContentPlaceHolderID="MainContent" runat="server">
    <div class="container-fluid">
        <!-- Page Header -->
        <div class="row mb-4">
            <div class="col-12">
                <h2><i class="fas fa-users"></i> Customer Management</h2>
                <p class="text-muted">Manage your customer database efficiently</p>
            </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="row mb-3">
            <div class="col-12">
                <asp:Button ID="btnAddCustomer" runat="server" 
                    Text="Add New Customer" 
                    CssClass="btn btn-primary"
                    OnClick="btnAddCustomer_Click" />
                <asp:Button ID="btnRefresh" runat="server" 
                    Text="Refresh" 
                    CssClass="btn btn-secondary ml-2"
                    OnClick="btnRefresh_Click" />
            </div>
        </div>
        
        <!-- Search Panel -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0"><i class="fas fa-search"></i> Search & Filter</h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-4">
                        <label for="txtSearchName">Search by Name:</label>
                        <asp:TextBox ID="txtSearchName" runat="server" 
                            CssClass="form-control" 
                            placeholder="Enter customer name..."></asp:TextBox>
                    </div>
                    <div class="col-md-3">
                        <label for="ddlStatusFilter">Status:</label>
                        <asp:DropDownList ID="ddlStatusFilter" runat="server" CssClass="form-control">
                            <asp:ListItem Text="All Customers" Value=""></asp:ListItem>
                            <asp:ListItem Text="Active Only" Value="true" Selected="true"></asp:ListItem>
                            <asp:ListItem Text="Inactive Only" Value="false"></asp:ListItem>
                        </asp:DropDownList>
                    </div>
                    <div class="col-md-3 d-flex align-items-end">
                        <asp:Button ID="btnSearch" runat="server" 
                            Text="Search" 
                            CssClass="btn btn-info mr-2"
                            OnClick="btnSearch_Click" />
                        <asp:Button ID="btnClearSearch" runat="server" 
                            Text="Clear" 
                            CssClass="btn btn-outline-secondary"
                            OnClick="btnClearSearch_Click" />
                    </div>
                    <div class="col-md-2">
                        <asp:Label ID="lblResultCount" runat="server" 
                            CssClass="badge badge-info float-right mt-4"></asp:Label>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Customer List Panel -->
        <asp:Panel ID="pnlCustomerList" runat="server" Visible="true">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0"><i class="fas fa-list"></i> Customer List</h5>
                </div>
                <div class="card-body">
                    <asp:GridView ID="gvCustomers" runat="server" 
                        CssClass="table table-striped table-hover table-bordered"
                        AutoGenerateColumns="false"
                        AllowPaging="true"
                        PageSize="20"
                        OnPageIndexChanging="gvCustomers_PageIndexChanging"
                        OnRowCommand="gvCustomers_RowCommand"
                        OnRowDataBound="gvCustomers_RowDataBound"
                        EmptyDataText="No customers found matching your criteria.">
                        
                        <HeaderStyle CssClass="table-dark" />
                        <PagerStyle CssClass="pagination-wrapper" />
                        
                        <Columns>
                            <asp:BoundField DataField="CustomerID" 
                                HeaderText="ID" 
                                ItemStyle-Width="80px" 
                                ItemStyle-CssClass="text-center" />
                                
                            <asp:BoundField DataField="CustomerName" 
                                HeaderText="Customer Name" 
                                ItemStyle-Width="200px" />
                                
                            <asp:BoundField DataField="Email" 
                                HeaderText="Email" 
                                ItemStyle-Width="180px" />
                                
                            <asp:BoundField DataField="Phone" 
                                HeaderText="Phone" 
                                ItemStyle-Width="120px" />
                                
                            <asp:BoundField DataField="City" 
                                HeaderText="City" 
                                ItemStyle-Width="100px" />
                                
                            <asp:BoundField DataField="CreatedDate" 
                                HeaderText="Created" 
                                DataFormatString="{0:MM/dd/yyyy}"
                                ItemStyle-Width="100px"
                                ItemStyle-CssClass="text-center" />
                                
                            <asp:TemplateField HeaderText="Status" ItemStyle-Width="80px" ItemStyle-CssClass="text-center">
                                <ItemTemplate>
                                    <span class='<%# (bool)Eval("IsActive") ? "badge badge-success" : "badge badge-secondary" %>'>
                                        <%# (bool)Eval("IsActive") ? "Active" : "Inactive" %>
                                    </span>
                                </ItemTemplate>
                            </asp:TemplateField>
                            
                            <asp:TemplateField HeaderText="Actions" ItemStyle-Width="120px" ItemStyle-CssClass="text-center">
                                <ItemTemplate>
                                    <asp:LinkButton ID="lnkEdit" runat="server" 
                                        CommandName="EditCustomer" 
                                        CommandArgument='<%# Eval("CustomerID") %>'
                                        CssClass="btn btn-sm btn-outline-primary mr-1"
                                        ToolTip="Edit Customer">
                                        <i class="fas fa-edit"></i>
                                    </asp:LinkButton>
                                    
                                    <asp:LinkButton ID="lnkDelete" runat="server" 
                                        CommandName="DeleteCustomer" 
                                        CommandArgument='<%# Eval("CustomerID") %>'
                                        CssClass="btn btn-sm btn-outline-danger"
                                        ToolTip="Delete Customer"
                                        OnClientClick="return confirm('Are you sure you want to delete this customer?');">
                                        <i class="fas fa-trash"></i>
                                    </asp:LinkButton>
                                </ItemTemplate>
                            </asp:TemplateField>
                        </Columns>
                    </asp:GridView>
                </div>
            </div>
        </asp:Panel>
        
        <!-- Edit Customer Panel -->
        <asp:Panel ID="pnlEditCustomer" runat="server" Visible="false">
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">
                        <i class="fas fa-user-edit"></i> 
                        <asp:Label ID="lblFormTitle" runat="server" Text="Edit Customer"></asp:Label>
                    </h5>
                </div>
                <div class="card-body">
                    <asp:HiddenField ID="hfCustomerID" runat="server" />
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="txtCustomerName">Customer Name <span class="text-danger">*</span></label>
                                <asp:TextBox ID="txtCustomerName" runat="server" 
                                    CssClass="form-control" 
                                    MaxLength="255"
                                    required></asp:TextBox>
                                <asp:RequiredFieldValidator ID="rfvCustomerName" runat="server"
                                    ControlToValidate="txtCustomerName"
                                    ErrorMessage="Customer name is required"
                                    CssClass="text-danger"
                                    Display="Dynamic" />
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="txtEmail">Email Address</label>
                                <asp:TextBox ID="txtEmail" runat="server" 
                                    CssClass="form-control" 
                                    TextMode="Email"
                                    MaxLength="255"></asp:TextBox>
                                <asp:RegularExpressionValidator ID="revEmail" runat="server"
                                    ControlToValidate="txtEmail"
                                    ValidationExpression="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                                    ErrorMessage="Please enter a valid email address"
                                    CssClass="text-danger"
                                    Display="Dynamic" />
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="txtPhone">Phone Number</label>
                                <asp:TextBox ID="txtPhone" runat="server" 
                                    CssClass="form-control" 
                                    MaxLength="50"></asp:TextBox>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label for="txtCity">City</label>
                                <asp:TextBox ID="txtCity" runat="server" 
                                    CssClass="form-control" 
                                    MaxLength="100"></asp:TextBox>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-8">
                            <div class="form-group">
                                <label for="txtAddress">Address</label>
                                <asp:TextBox ID="txtAddress" runat="server" 
                                    CssClass="form-control" 
                                    MaxLength="500"
                                    TextMode="MultiLine"
                                    Rows="2"></asp:TextBox>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="form-group">
                                <label for="txtState">State</label>
                                <asp:TextBox ID="txtState" runat="server" 
                                    CssClass="form-control" 
                                    MaxLength="50"></asp:TextBox>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="form-group">
                                <label for="txtZipCode">Zip Code</label>
                                <asp:TextBox ID="txtZipCode" runat="server" 
                                    CssClass="form-control" 
                                    MaxLength="20"></asp:TextBox>
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-12">
                            <div class="form-check">
                                <asp:CheckBox ID="chkIsActive" runat="server" 
                                    CssClass="form-check-input" 
                                    Checked="true" />
                                <label class="form-check-label" for="chkIsActive">
                                    Active Customer
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <asp:Button ID="btnSaveCustomer" runat="server" 
                        Text="Save Customer" 
                        CssClass="btn btn-success"
                        OnClick="btnSaveCustomer_Click" />
                    <asp:Button ID="btnCancelEdit" runat="server" 
                        Text="Cancel" 
                        CssClass="btn btn-secondary ml-2"
                        OnClick="btnCancelEdit_Click"
                        CausesValidation="false" />
                </div>
            </div>
        </asp:Panel>
        
        <!-- Message Panel -->
        <asp:Panel ID="pnlMessage" runat="server" Visible="false" CssClass="mt-3">
            <asp:Label ID="lblMessage" runat="server" CssClass="alert"></asp:Label>
        </asp:Panel>
    </div>
    
    <!-- Custom JavaScript for enhanced UX -->
    <script type="text/javascript">
        $(document).ready(function() {
            // Auto-hide success messages after 3 seconds
            setTimeout(function() {
                $('.alert-success').fadeOut('slow');
            }, 3000);
            
            // Format phone numbers on input
            $('#<%= txtPhone.ClientID %>').on('input', function() {
                var value = this.value.replace(/\D/g, '');
                var formattedValue = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
                if (value.length >= 10) {
                    this.value = formattedValue;
                }
            });
            
            // Uppercase state field
            $('#<%= txtState.ClientID %>').on('input', function() {
                this.value = this.value.toUpperCase();
            });
        });
        
        // Confirm delete function
        function confirmDelete(customerName) {
            return confirm('Are you sure you want to delete customer: ' + customerName + '?');
        }
    </script>
</asp:Content> 