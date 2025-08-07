SELECT 
    c.CustomerID,
    c.FirstName,
    c.LastName,
    p.Name AS ProductName,
    pc.Quantity,
    pc.PriceAtPurchase,
    (pc.Quantity * pc.PriceAtPurchase) AS TotalPrice
FROM Customer c
JOIN Purchase pu ON c.CustomerID = pu.CustomerID
JOIN PurchaseContains pc ON pu.PurchaseID = pc.PurchaseID
JOIN Product p ON pc.ProductID = p.ProductID
ORDER BY c.CustomerID