-- Customer Management Stored Procedures

CREATE PROCEDURE sp_GetCustomers
    @CustomerID INT = NULL,
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        SELECT CustomerID, CustomerName, Email, IsActive
        FROM Customers
        WHERE (@CustomerID IS NULL OR CustomerID = @CustomerID)
        AND IsActive = @IsActive
        ORDER BY CustomerName
        
        RETURN 0
    END TRY
    BEGIN CATCH
        RETURN -1
    END CATCH
END
GO

CREATE PROCEDURE sp_SaveCustomer
    @CustomerID INT = NULL,
    @CustomerName NVARCHAR(255),
    @Email NVARCHAR(255),
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    BEGIN TRY
        IF @CustomerID IS NULL
            INSERT INTO Customers (CustomerName, Email, IsActive)
            VALUES (@CustomerName, @Email, @IsActive)
        ELSE
            UPDATE Customers 
            SET CustomerName = @CustomerName,
                Email = @Email,
                IsActive = @IsActive
            WHERE CustomerID = @CustomerID
            
        RETURN 0
    END TRY
    BEGIN CATCH
        RETURN -1
    END CATCH
END