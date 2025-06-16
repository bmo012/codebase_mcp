using System;
using System.Collections.Generic;
using System.Data;
using System.Data.SqlClient;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace YourApp.BusinessLogic
{
    /// <summary>
    /// Customer Manager - handles all customer-related business logic
    /// This demonstrates the business logic layer pattern that the MCP server can analyze
    /// </summary>
    public class CustomerManager
    {
        private readonly ILogger<CustomerManager> _logger;
        private readonly string _connectionString;
        
        public CustomerManager(ILogger<CustomerManager> logger, IConfiguration configuration)
        {
            _logger = logger ?? throw new ArgumentNullException(nameof(logger));
            _connectionString = configuration.GetConnectionString("DefaultConnection");
            
            if (string.IsNullOrEmpty(_connectionString))
            {
                throw new InvalidOperationException("Database connection string is not configured");
            }
        }
        
        /// <summary>
        /// Get a list of customers based on filter criteria
        /// </summary>
        /// <param name="customerId">Optional customer ID filter</param>
        /// <param name="isActive">Filter by active status</param>
        /// <param name="searchName">Optional name search filter</param>
        /// <returns>List of customers</returns>
        public async Task<List<Customer>> GetCustomerListAsync(int? customerId = null, bool isActive = true, string searchName = null)
        {
            try
            {
                var customerList = new List<Customer>();
                
                using (var connection = new SqlConnection(_connectionString))
                {
                    using (var command = new SqlCommand("sp_GetCustomerList", connection))
                    {
                        command.CommandType = CommandType.StoredProcedure;
                        command.CommandTimeout = 30;
                        
                        // Add parameters
                        command.Parameters.Add("@CustomerID", SqlDbType.Int).Value = customerId ?? (object)DBNull.Value;
                        command.Parameters.Add("@IsActive", SqlDbType.Bit).Value = isActive;
                        command.Parameters.Add("@SearchName", SqlDbType.NVarChar, 255).Value = searchName ?? (object)DBNull.Value;
                        
                        await connection.OpenAsync();
                        
                        using (var reader = await command.ExecuteReaderAsync())
                        {
                            while (await reader.ReadAsync())
                            {
                                var customer = new Customer
                                {
                                    CustomerID = reader.GetInt32("CustomerID"),
                                    CustomerName = reader.GetString("CustomerName"),
                                    Email = reader.IsDBNull("Email") ? null : reader.GetString("Email"),
                                    Phone = reader.IsDBNull("Phone") ? null : reader.GetString("Phone"),
                                    Address = reader.IsDBNull("Address") ? null : reader.GetString("Address"),
                                    City = reader.IsDBNull("City") ? null : reader.GetString("City"),
                                    State = reader.IsDBNull("State") ? null : reader.GetString("State"),
                                    ZipCode = reader.IsDBNull("ZipCode") ? null : reader.GetString("ZipCode"),
                                    IsActive = reader.GetBoolean("IsActive"),
                                    CreatedDate = reader.GetDateTime("CreatedDate"),
                                    ModifiedDate = reader.IsDBNull("ModifiedDate") ? null : reader.GetDateTime("ModifiedDate")
                                };
                                
                                customerList.Add(customer);
                            }
                        }
                    }
                }
                
                _logger.LogInformation("Retrieved {Count} customers", customerList.Count);
                return customerList;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error retrieving customer list with parameters: CustomerId={CustomerId}, IsActive={IsActive}, SearchName={SearchName}", 
                    customerId, isActive, searchName);
                throw;
            }
        }
        
        /// <summary>
        /// Save a customer (insert or update)
        /// </summary>
        /// <param name="customer">Customer to save</param>
        /// <returns>Saved customer with updated ID</returns>
        public async Task<Customer> SaveCustomerAsync(Customer customer)
        {
            if (customer == null)
                throw new ArgumentNullException(nameof(customer));
            
            // Business validation
            ValidateCustomer(customer);
            
            try
            {
                using (var connection = new SqlConnection(_connectionString))
                {
                    using (var command = new SqlCommand("sp_SaveCustomer", connection))
                    {
                        command.CommandType = CommandType.StoredProcedure;
                        command.CommandTimeout = 30;
                        
                        // Add parameters
                        command.Parameters.Add("@CustomerID", SqlDbType.Int).Value = customer.CustomerID == 0 ? (object)DBNull.Value : customer.CustomerID;
                        command.Parameters.Add("@CustomerName", SqlDbType.NVarChar, 255).Value = customer.CustomerName;
                        command.Parameters.Add("@Email", SqlDbType.NVarChar, 255).Value = customer.Email ?? (object)DBNull.Value;
                        command.Parameters.Add("@Phone", SqlDbType.NVarChar, 50).Value = customer.Phone ?? (object)DBNull.Value;
                        command.Parameters.Add("@Address", SqlDbType.NVarChar, 500).Value = customer.Address ?? (object)DBNull.Value;
                        command.Parameters.Add("@City", SqlDbType.NVarChar, 100).Value = customer.City ?? (object)DBNull.Value;
                        command.Parameters.Add("@State", SqlDbType.NVarChar, 50).Value = customer.State ?? (object)DBNull.Value;
                        command.Parameters.Add("@ZipCode", SqlDbType.NVarChar, 20).Value = customer.ZipCode ?? (object)DBNull.Value;
                        command.Parameters.Add("@IsActive", SqlDbType.Bit).Value = customer.IsActive;
                        
                        await connection.OpenAsync();
                        
                        using (var reader = await command.ExecuteReaderAsync())
                        {
                            if (await reader.ReadAsync())
                            {
                                customer.CustomerID = reader.GetInt32("CustomerID");
                                var message = reader.GetString("Message");
                                _logger.LogInformation("Customer saved: {Message}", message);
                            }
                        }
                    }
                }
                
                return customer;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error saving customer: {CustomerName}", customer.CustomerName);
                throw;
            }
        }
        
        /// <summary>
        /// Delete a customer (soft delete)
        /// </summary>
        /// <param name="customerId">ID of customer to delete</param>
        /// <returns>True if successful</returns>
        public async Task<bool> DeleteCustomerAsync(int customerId)
        {
            if (customerId <= 0)
                throw new ArgumentException("Customer ID must be greater than 0", nameof(customerId));
            
            try
            {
                using (var connection = new SqlConnection(_connectionString))
                {
                    using (var command = new SqlCommand("sp_DeleteCustomer", connection))
                    {
                        command.CommandType = CommandType.StoredProcedure;
                        command.CommandTimeout = 30;
                        
                        command.Parameters.Add("@CustomerID", SqlDbType.Int).Value = customerId;
                        
                        await connection.OpenAsync();
                        
                        var returnValue = await command.ExecuteScalarAsync();
                        
                        _logger.LogInformation("Customer {CustomerId} deleted successfully", customerId);
                        return true;
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error deleting customer with ID: {CustomerId}", customerId);
                throw;
            }
        }
        
        /// <summary>
        /// Validate customer business rules
        /// </summary>
        /// <param name="customer">Customer to validate</param>
        private void ValidateCustomer(Customer customer)
        {
            var validationErrors = new List<string>();
            
            if (string.IsNullOrWhiteSpace(customer.CustomerName))
                validationErrors.Add("Customer name is required");
            
            if (customer.CustomerName?.Length > 255)
                validationErrors.Add("Customer name cannot exceed 255 characters");
            
            if (!string.IsNullOrEmpty(customer.Email) && !IsValidEmail(customer.Email))
                validationErrors.Add("Invalid email format");
            
            if (!string.IsNullOrEmpty(customer.Phone) && customer.Phone.Length > 50)
                validationErrors.Add("Phone number cannot exceed 50 characters");
            
            if (validationErrors.Count > 0)
            {
                throw new ValidationException($"Customer validation failed: {string.Join(", ", validationErrors)}");
            }
        }
        
        /// <summary>
        /// Simple email validation
        /// </summary>
        /// <param name="email">Email to validate</param>
        /// <returns>True if valid</returns>
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
    }
    
    /// <summary>
    /// Customer data model
    /// </summary>
    public class Customer
    {
        public int CustomerID { get; set; }
        public string CustomerName { get; set; }
        public string Email { get; set; }
        public string Phone { get; set; }
        public string Address { get; set; }
        public string City { get; set; }
        public string State { get; set; }
        public string ZipCode { get; set; }
        public bool IsActive { get; set; } = true;
        public DateTime CreatedDate { get; set; }
        public DateTime? ModifiedDate { get; set; }
    }
    
    /// <summary>
    /// Custom validation exception
    /// </summary>
    public class ValidationException : Exception
    {
        public ValidationException(string message) : base(message) { }
        public ValidationException(string message, Exception innerException) : base(message, innerException) { }
    }
} 