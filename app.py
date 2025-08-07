import mysql.connector
import os
import platform
from datetime import date
from config import database_config # Config stored in a config.py file not on cloud

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if platform.system() == "Windows" else 'clear')

def view_all_products():
    """Fetches and displays all products from the Product table."""
    try:
        cnx = mysql.connector.connect(**database_config)
        cursor = cnx.cursor()
        query = "SELECT ProductID, Name, Price, StockQuantity FROM Product ORDER BY ProductID"
        cursor.execute(query)

        print("\n--- Available Products ---")
        print(f"{'ID':<5}{'Name':<20}{'Price':<15}{'Stock'}")
        print("-" * 50)
        for (product_id, name, price, quantity) in cursor:
            print(f"{product_id:<5}{name:<20}{'$' + str(price):<15}{quantity}")
        print("-" * 50)
        return True
    except mysql.connector.Error as err:
        print(f"Error viewing products: {err}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()

def purchase_product(customer_id):
    """Allows a customer to purchase a product."""
    if not view_all_products():
        input("\nCould not retrieve products. Press Enter to return to the menu...")
        return

    try:
        product_id = int(input("Enter the Product ID you wish to buy: "))
        quantity_to_buy = int(input("Enter the Quantity you wish to buy: "))

        cnx = mysql.connector.connect(**database_config)
        cursor = cnx.cursor()
        cnx.start_transaction()

        cursor.execute("SELECT Price, StockQuantity FROM Product WHERE ProductID = %s FOR UPDATE", (product_id,))
        product_data = cursor.fetchone()

        if not product_data:
            print("\nError: Product not found.")
            cnx.rollback()
            return

        price_at_purchase, stock = product_data
        if stock < quantity_to_buy:
            print(f"\nSorry, product with ID '{product_id}' is out of stock.")
            cnx.rollback()
            return
            
        update_stock_query = "UPDATE Product SET StockQuantity = StockQuantity - %s WHERE ProductID = %s"
        cursor.execute(update_stock_query, (quantity_to_buy, product_id))

        add_purchase_query = "INSERT INTO Purchase (PurchaseDate, CustomerID, StaffID) VALUES (%s, %s, NULL)"
        cursor.execute(add_purchase_query, (date.today(), customer_id))
        purchase_id = cursor.lastrowid

        add_contains_query = "INSERT INTO PurchaseContains (PurchaseID, ProductID, PriceAtPurchase, Quantity) VALUES (%s, %s, %s, %s)"
        cursor.execute(add_contains_query, (purchase_id, product_id, price_at_purchase, quantity_to_buy))

        cnx.commit()
        print(f"\nSuccess! Purchase complete. Your Purchase ID is {purchase_id}.")

    except ValueError:
        print("\nInvalid input. Please enter a valid Product ID.")
    except mysql.connector.Error as err:
        print(f"\nDatabase error during purchase: {err}")
        if 'cnx' in locals() and cnx.is_connected():
            cnx.rollback()
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()
    input("\nPress Enter to return to the menu...")

def view_my_purchases(customer_id):
    """Displays the purchase history for a specific customer."""
    try:
        cnx = mysql.connector.connect(**database_config)
        cursor = cnx.cursor(dictionary=True)
        
        query = """
        SELECT 
            pu.PurchaseID,
            pu.PurchaseDate,
            p.Name AS ProductName,
            pc.Quantity,
            pc.PriceAtPurchase
        FROM Purchase pu
        JOIN PurchaseContains pc ON pu.PurchaseID = pc.PurchaseID
        JOIN Product p ON pc.ProductID = p.ProductID
        WHERE pu.CustomerID = %s
        ORDER BY pu.PurchaseDate DESC, pu.PurchaseID DESC;
        """
        cursor.execute(query, (customer_id,))
        purchases = cursor.fetchall()
        
        print("\n--- Your Purchase History ---")
        if not purchases:
            print("You have no past purchases.")
        else:
            print(f"{'Date':<12}{'Product':<20}{'Qty':<5}{'Price Paid'}")
            print("-" * 50)
            for row in purchases:
                print(f"{str(row['PurchaseDate']):<12}{row['ProductName']:<20}{row['Quantity']:<5}{'$' + str(row['PriceAtPurchase'])}")
            print("-" * 50)

    except mysql.connector.Error as err:
        print(f"Error viewing your history: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()
    input("\nPress Enter to return to the menu...")

def add_new_product():
    """Adds a new product to the database."""
    try:
        cnx = mysql.connector.connect(**database_config)
        cursor = cnx.cursor()

        print("\n--- Adding a New Product ---")
        name = input("Enter product name: ")
        price = float(input("Enter product price: "))
        quantity = int(input("Enter stock quantity: "))

        add_product_query = "INSERT INTO Product (Name, Price, StockQuantity) VALUES (%s, %s, %s)"
        cursor.execute(add_product_query, (name, price, quantity))
        
        cnx.commit()
        print(f"\nSuccess! Product '{name}' was added.")

    except ValueError:
        print("\nInvalid input. Price must be a number and quantity must be an integer.")
    except mysql.connector.Error as err:
        print(f"Error adding product: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()
    input("\nPress Enter to return to the menu...")


def delete_product():
    """Deletes a product from the database."""
    if not view_all_products():
        input("\nCould not retrieve products. Press Enter to return to the menu...")
        return
    
    try:
        product_id_to_delete = int(input("\nEnter the ID of the product to delete: "))

        cnx = mysql.connector.connect(**database_config)
        cursor = cnx.cursor()
        
        cursor.execute("SELECT 1 FROM PurchaseContains WHERE ProductID = %s LIMIT 1", (product_id_to_delete,))
        if cursor.fetchone():
            print("\nWarning: This product is part of a past purchase and cannot be deleted.")
            print("Consider setting its stock to 0 instead.")
            return

        delete_query = "DELETE FROM Product WHERE ProductID = %s"
        cursor.execute(delete_query, (product_id_to_delete,))
        cnx.commit()

        if cursor.rowcount > 0:
            print(f"\nSuccess! Product with ID {product_id_to_delete} was deleted.")
        else:
            print(f"\nWarning: No product found with ID {product_id_to_delete}.")

    except ValueError:
        print("\nInvalid input. Please enter a valid product ID.")
    except mysql.connector.Error as err:
        print(f"Error deleting product: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()
    input("\nPress Enter to return to the menu...")

def view_all_customers():
    """Fetches and displays all customers."""
    try:
        cnx = mysql.connector.connect(**database_config)
        cursor = cnx.cursor()
        query = "SELECT CustomerID, FirstName, LastName, Email FROM Customer ORDER BY CustomerID"
        cursor.execute(query)
        
        print("\n--- All Customers ---")
        print(f"{'ID':<5}{'First Name':<15}{'Last Name':<15}{'Email'}")
        print("-" * 60)
        for (cust_id, first, last, email) in cursor:
            print(f"{cust_id:<5}{first:<15}{last:<15}{email}")
        print("-" * 60)

    except mysql.connector.Error as err:
        print(f"Error viewing customers: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()
    input("\nPress Enter to return to the menu...")


def view_all_purchases():
    """Displays a detailed list of all purchases."""
    try:
        cnx = mysql.connector.connect(**database_config)
        cursor = cnx.cursor()
        query = """
        SELECT 
            pu.PurchaseID,
            pu.PurchaseDate,
            CONCAT(c.FirstName, ' ', c.LastName) AS CustomerName,
            p.Name AS ProductName,
            pc.Quantity,
            pc.PriceAtPurchase,
            (pc.Quantity * pc.PriceAtPurchase) AS TotalPrice
        FROM Purchase pu
        JOIN Customer c ON pu.CustomerID = c.CustomerID
        JOIN PurchaseContains pc ON pu.PurchaseID = pc.PurchaseID
        JOIN Product p ON pc.ProductID = p.ProductID
        ORDER BY pu.PurchaseID;
        """
        cursor.execute(query)

        print("\n--- All Purchase Records ---")
        print(f"{'ID':<5}{'Date':<12}{'Customer':<20}{'Product':<15}{'Qty':<5}{'Price':<10}{'Total'}")
        print("-" * 80)
        for (pid, pdate, cname, pname, qty, price, total) in cursor:
            print(f"{pid:<5}{str(pdate):<12}{cname:<20}{pname:<15}{qty:<5}{'$'+str(price):<10}{'$'+str(total)}")
        print("-" * 80)

    except mysql.connector.Error as err:
        print(f"Error viewing purchases: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()
    input("\nPress Enter to return to the menu...")


def customer_menu(customer_id, customer_name):
    """Displays the menu for customers."""
    while True:
        clear_screen()
        print(f"\n===== Customer Menu (Logged in as: {customer_name}) =====")
        print("1. View All Products")
        print("2. Purchase a Product")
        print("3. View My Purchase History")
        print("4. Logout (Return to Main Menu)")
        choice = input("Enter your choice: ")

        if choice == '1':
            view_all_products()
            input("\nPress Enter to return to the menu...")
        elif choice == '2':
            purchase_product(customer_id)
        elif choice == '3':
            view_my_purchases(customer_id)
        elif choice == '4':
            break
        else:
            print("Invalid choice, please try again.")
            input("\nPress Enter to continue...")

def staff_menu():
    """Displays the menu for staff."""
    while True:
        clear_screen()
        print("\n===== Staff Menu =====")
        print("1. View All Products")
        print("2. Add a New Product")
        print("3. Delete an Existing Product")
        print("4. View All Customers")
        print("5. View All Purchase Records")
        print("6. Exit to Main Menu")
        choice = input("Enter your choice: ")

        if choice == '1':
            view_all_products()
            input("\nPress Enter to return to the menu...")
        elif choice == '2':
            add_new_product()
        elif choice == '3':
            delete_product()
        elif choice == '4':
            view_all_customers()
        elif choice == '5':
            view_all_purchases()
        elif choice == '6':
            break
        else:
            print("Invalid choice, please try again.")
            input("\nPress Enter to continue...")

def main():
    """Main function to run the application."""
    while True:
        clear_screen()
        print("\n===== E-commerce Database System =====")
        print("Are you a customer or a staff member?")
        print("1. Customer")
        print("2. Staff")
        print("3. Exit Application")
        role = input("Enter your choice: ")

        if role == '1':
            try:
                customer_id = int(input("Please enter your Customer ID to log in: "))
                cnx = mysql.connector.connect(**database_config)
                cursor = cnx.cursor(dictionary=True)
                cursor.execute("SELECT FirstName, LastName FROM Customer WHERE CustomerID = %s", (customer_id,))
                customer = cursor.fetchone()
                
                if customer:
                    customer_name = f"{customer['FirstName']} {customer['LastName']}"
                    customer_menu(customer_id, customer_name)
                else:
                    print("\nError: Customer ID not found.")
                    input("Press Enter to return to the main menu...")
            
            except ValueError:
                print("\nInvalid ID format. Please enter a number.")
                input("Press Enter to return to the main menu...")
            except mysql.connector.Error as err:
                print(f"Database error: {err}")
                input("Press Enter to return to the main menu...")
            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'cnx' in locals() and cnx.is_connected():
                    cnx.close()

        elif role == '2':
            staff_menu()
        elif role == '3':
            print("Exiting application.")
            break
        else:
            print("Invalid choice, please select a valid role.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()