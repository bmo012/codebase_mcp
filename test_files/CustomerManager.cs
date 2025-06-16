using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace TestApp.BusinessLogic
{
    public class CustomerManager
    {
        private readonly string _connectionString;
        
        public CustomerManager(string connectionString)
        {
            _connectionString = connectionString;
        }
        
        public async Task<List<Customer>> GetCustomersAsync()
        {
            // Implementation here
            return new List<Customer>();
        }
        
        public async Task<bool> SaveCustomerAsync(Customer customer)
        {
            // Implementation here
            return true;
        }
    }
    
    public class Customer
    {
        public int CustomerID { get; set; }
        public string CustomerName { get; set; }
        public string Email { get; set; }
        public bool IsActive { get; set; }
    }
}