USE final_db;

CREATE TABLE Customer (
    CustomerID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE Staff (
    StaffID INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Role VARCHAR(100)
);

CREATE TABLE Product (
    ProductID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    StockQuantity INT NOT NULL DEFAULT 0
);

CREATE TABLE Purchase (
    PurchaseID INT PRIMARY KEY AUTO_INCREMENT,
    PurchaseDate DATE NOT NULL,
    CustomerID INT,
    StaffID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
);

CREATE TABLE PurchaseContains (
    PurchaseID INT,
    ProductID INT,
    PriceAtPurchase DECIMAL(10, 2) NOT NULL,
    Quantity INT NOT NULL,
    PRIMARY KEY (PurchaseID, ProductID),
    FOREIGN KEY (PurchaseID) REFERENCES Purchase(PurchaseID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

INSERT INTO Customer (FirstName, LastName, Email) VALUES
('John', 'Doe', 'john.doe@email.com'),
('Jane', 'Smith', 'jane.smith@email.com'),
('Emily', 'White', 'emily.white@email.com'),
('Michael', 'Brown', 'michael.brown@email.com');

INSERT INTO Staff (FirstName, LastName, Role) VALUES
('Alice', 'Jones', 'Manager'),
('Bob', 'Williams', 'Sales Associate'),
('Chris', 'Green', 'Tech Support');

INSERT INTO Product (Name, Price, StockQuantity) VALUES
('Laptop', 1200.00, 50),
('Mouse', 25.00, 200),
('Keyboard', 75.00, 150),
('Webcam', 45.00, 80),
('Monitor', 300.00, 40);

INSERT INTO Purchase (PurchaseDate, CustomerID, StaffID) VALUES
('2025-08-06', 1, 2), 
('2025-08-07', 2, 2),
('2025-08-07', 3, 3),
('2025-08-07', 4, 2);

INSERT INTO PurchaseContains (PurchaseID, ProductID, PriceAtPurchase, Quantity) VALUES
(1, 1, 1200.00, 1),
(1, 2, 25.00, 1),
(2, 3, 75.00, 2),
(3, 4, 45.00, 1),
(4, 5, 300.00, 2),
(4, 2, 25.00, 1);