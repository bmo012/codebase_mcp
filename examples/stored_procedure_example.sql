-- Example Stored Procedure for Customer Management
-- This demonstrates the database layer pattern that the MCP server can analyze

-- Get Customer List Procedure
CREATE PROCEDURE sp_GetCustomerList
    @CustomerID INT = NULL,
    @IsActive BIT = 1,
    @SearchName NVARCHAR(255) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        SELECT 
            CustomerID,
            CustomerName,
            Email,
            Phone,
            Address,
            City,
            State,
            ZipCode,
            IsActive,
            CreatedDate,
            ModifiedDate
        FROM Customers
        WHERE 
            (@CustomerID IS NULL OR CustomerID = @CustomerID)
            AND IsActive = @IsActive
            AND (@SearchName IS NULL OR CustomerName LIKE '%' + @SearchName + '%')
        ORDER BY CustomerName
        
        RETURN 0 -- Success
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE()
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY()
        DECLARE @ErrorState INT = ERROR_STATE()
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState)
        RETURN -1 -- Error
    END CATCH
END
GO

-- Save Customer Procedure (Insert/Update)
CREATE PROCEDURE sp_SaveCustomer
    @CustomerID INT = NULL,
    @CustomerName NVARCHAR(255),
    @Email NVARCHAR(255) = NULL,
    @Phone NVARCHAR(50) = NULL,
    @Address NVARCHAR(500) = NULL,
    @City NVARCHAR(100) = NULL,
    @State NVARCHAR(50) = NULL,
    @ZipCode NVARCHAR(20) = NULL,
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        -- Validation
        IF @CustomerName IS NULL OR LEN(TRIM(@CustomerName)) = 0
        BEGIN
            RAISERROR('Customer name is required', 16, 1)
            RETURN -1
        END
        
        IF @CustomerID IS NULL OR @CustomerID = 0
        BEGIN
            -- Insert new customer
            INSERT INTO Customers (
                CustomerName, Email, Phone, Address, City, State, ZipCode, 
                IsActive, CreatedDate, ModifiedDate
            )
            VALUES (
                @CustomerName, @Email, @Phone, @Address, @City, @State, @ZipCode,
                @IsActive, GETDATE(), GETDATE()
            )
            
            SET @CustomerID = SCOPE_IDENTITY()
            SELECT @CustomerID AS CustomerID, 'Customer created successfully' AS Message
        END
        ELSE
        BEGIN
            -- Update existing customer
            UPDATE Customers
            SET 
                CustomerName = @CustomerName,
                Email = @Email,
                Phone = @Phone,
                Address = @Address,
                City = @City,
                State = @State,
                ZipCode = @ZipCode,
                IsActive = @IsActive,
                ModifiedDate = GETDATE()
            WHERE CustomerID = @CustomerID
            
            IF @@ROWCOUNT = 0
            BEGIN
                RAISERROR('Customer not found', 16, 1)
                RETURN -1
            END
            
            SELECT @CustomerID AS CustomerID, 'Customer updated successfully' AS Message
        END
        
        RETURN 0
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE()
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY()
        DECLARE @ErrorState INT = ERROR_STATE()
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState)
        RETURN -1
    END CATCH
END
GO

-- Delete Customer Procedure (Soft Delete)
CREATE PROCEDURE sp_DeleteCustomer
    @CustomerID INT
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        IF @CustomerID IS NULL OR @CustomerID <= 0
        BEGIN
            RAISERROR('Valid Customer ID is required', 16, 1)
            RETURN -1
        END
        
        -- Soft delete by setting IsActive = 0
        UPDATE Customers
        SET 
            IsActive = 0,
            ModifiedDate = GETDATE()
        WHERE CustomerID = @CustomerID
        
        IF @@ROWCOUNT = 0
        BEGIN
            RAISERROR('Customer not found', 16, 1)
            RETURN -1
        END
        
        SELECT 'Customer deleted successfully' AS Message
        RETURN 0
    END TRY
    BEGIN CATCH
        DECLARE @ErrorMessage NVARCHAR(4000) = ERROR_MESSAGE()
        DECLARE @ErrorSeverity INT = ERROR_SEVERITY()
        DECLARE @ErrorState INT = ERROR_STATE()
        
        RAISERROR(@ErrorMessage, @ErrorSeverity, @ErrorState)
        RETURN -1
    END CATCH
END
GO 