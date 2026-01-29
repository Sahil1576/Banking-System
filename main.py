from Database import conn
import random
import string
import pandas as pd

def create_accounts_table():
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            account_number VARCHAR(50) PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            pin VARCHAR(10) NOT NULL,
            balance DECIMAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    
def create_audit_table():
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit (
            id SERIAL PRIMARY KEY,
            account_number VARCHAR(50) NOT NULL,
            holder_name VARCHAR(50) NOT NULL,
            action VARCHAR(100) NOT NULL,
            amount DECIMAL DEFAULT 0,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_number) REFERENCES accounts(account_number)
            ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')
    conn.commit()
    cursor.close()
    
def insert_account_data(account_number, name, pin, balance):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO accounts (account_number, name, pin, balance)
        VALUES (%s, %s, %s, %s)
    ''', (account_number, name, pin, balance))
    conn.commit()
    cursor.close()

def insert_audit_data(account_number, holder_name, action, amount):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audit (account_number, holder_name, action, amount)
        VALUES (%s, %s, %s, %s)
    ''', (account_number, holder_name, action, amount))
    conn.commit()
    cursor.close()

def login_account(account_number, pin):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM accounts WHERE account_number = %s AND pin = %s
    ''', (account_number, pin))
    account = cursor.fetchone()
    cursor.close()
    return account

def fetch_account_details(account_number):
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT * FROM accounts WHERE account_number = %s''', (account_number,))
    account = cursor.fetchone()
    cursor.close()
    return account

def deposit_amount(account_number, amount):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE accounts SET balance = balance + %s WHERE account_number = %s
    ''', (amount, account_number))
    conn.commit()
    cursor.close()
    
def withdraw_amount(account_number, amount):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE accounts SET balance = balance - %s WHERE account_number = %s
    ''', (amount, account_number))
    conn.commit()
    cursor.close()

def transaction_history(account_number):
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM audit WHERE account_number = %s ORDER BY timestamp DESC
    ''', (account_number,))
    transactions = cursor.fetchall()
    cursor.close()
    return transactions

while True:
    create_accounts_table()
    create_audit_table()
    print('='*30)
    print("1. Create Account")
    print("2. Login to Account")
    print("3. Exit")
    print('='*30)
    print('-'*30)
    choice = input("Enter your choice: ").strip()
    print('-'*30)
    
    if choice == '1':
        name = input("Enter your name: ").strip()
        pin = input("Set a 4-digit PIN: ").strip()
        confirm_pin = input("Confirm your PIN: ").strip()
        if pin != confirm_pin or not pin.isdigit() or len(pin) != 4:
            print('='*30)
            print("PINs do not match or are invalid. Please try again.")
            print('='*30)
            continue
        account_number = ''.join(random.choices(string.digits, k=10))
        print(f"Your account number is: {account_number.upper()}")
        insert_account_data(account_number, name, pin, 0)
        insert_audit_data(account_number, name, "Account Created", 0)
        print("Account created successfully!")
        input("Press Enter to continue...")
        
    elif choice == '2':
        account_number = input("Enter your account number: ").strip()
        pin = input("Enter your PIN: ").strip()
        account = login_account(account_number, pin)
        insert_audit_data(account_number, account[1] if account else "Unknown", "Login Attempt", 0)
        if account is not None and account[0] == account_number and account[2] == pin:
            print('='*30)
            print(f"Welcome, {account[1]}! You have successfully logged in.")
            print('='*30)
            print("1. Check Balance")
            print("2. Deposit")
            print("3. Withdraw")
            print("4. Transactions History")
            print("5. Change PIN")
            print("6. Change Name")
            print("7. Fund Transfer")
            print("8. Delete Account")
            print("9. Logout")
            print('='*30)
            choice1 = input("Enter your choice: ").strip()
            print('-'*30)
            
            if choice1 == '1':
                print(f"Account Number: {account[0]}")
                print(f"Holder Name: {account[1]}")
                print(f"Balance: ₹{account[3]}")
                insert_audit_data(account_number, account[1], "Viewed Account Details", 0)
                
            elif choice1 == '2':
                amount = float(input("Enter amount to deposit: ₹").strip())
                deposit_amount(account_number, amount)
                insert_audit_data(account_number, account[1], "Deposited Amount", amount)
                print(f"₹{amount} deposited successfully!")
                
            elif choice1 == '3':
                amount = float(input("Enter amount to withdraw: ₹").strip())
                if amount > account[3]:
                    print("Insufficient balance.")
                else:
                    withdraw_amount(account_number, amount)
                    insert_audit_data(account_number, account[1], "Withdrew Amount", amount)
                    print(f"₹{amount} withdrawn successfully!")
                    
            elif choice1 == '4':
                transactions = transaction_history(account_number)
                if transactions:
                    print(pd.DataFrame(transactions, 
                                       columns=['ID', 'Account Number', 'Holder Name', 'Action', 'Amount', 'Timestamp']))
                else:
                    print("No transactions found.")
                    
            elif choice1 == '5':
                new_pin = input("Enter new 4-digit PIN: ").strip()
                confirm_new_pin = input("Confirm new PIN: ").strip()
                if new_pin != confirm_new_pin or not new_pin.isdigit() or len(new_pin) != 4:
                    print("PINs do not match or are invalid. Please try again.")
                else:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE accounts SET pin = %s WHERE account_number = %s
                    ''', (new_pin, account_number))
                    conn.commit()
                    cursor.close()
                    insert_audit_data(account_number, account[1], "Changed PIN", 0)
                    print("PIN changed successfully!")
                    
            elif choice1 == '6':
                new_name = input("Enter new name: ").strip()
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE accounts SET name = %s WHERE account_number = %s
                ''', (new_name, account_number))
                conn.commit()
                cursor.close()
                insert_audit_data(account_number, new_name, "Changed Name", 0)
                print("Name changed successfully!")
                
            elif choice1 == '7':
                target_account_number = input("Enter recipient's account number: ").strip()
                amount = float(input("Enter amount to transfer: ₹").strip())
                if amount > account[3]:
                    print("Insufficient balance.")
                else:
                    target_account = fetch_account_details(target_account_number)  # Just to check existence
                    if target_account is None:
                        print("Recipient account not found.")
                        insert_audit_data(account_number, account[1], f"Failed Transfer Attempt to {target_account_number}", amount)
                        insert_audit_data(target_account_number, "Unknown", f"Failed Transfer Attempt from {account_number}", amount)
                    else:
                        transfer_pin = input("Enter your PIN to confirm transfer: ").strip()
                        if transfer_pin != account[2]:
                            print("Incorrect PIN. Transfer cancelled.")
                            insert_audit_data(account_number, account[1], f"Failed Transfer Attempt to {target_account_number} due to incorrect PIN", amount)
                            insert_audit_data(target_account_number, target_account[1], f"Failed Transfer Attempt from {account_number} due to incorrect PIN", amount)
                        else:
                            withdraw_amount(account_number, amount)
                            deposit_amount(target_account_number, amount)
                            insert_audit_data(account_number, account[1], f"Transferred ₹{amount} to {target_account_number}", amount)
                            insert_audit_data(target_account_number, target_account[1], f"Received ₹{amount} from {account_number}", amount)
                            print(f"₹{amount} transferred successfully to account {target_account_number}!")
                
            elif choice1 == '8':
                confirm_delete = input("Are you sure you want to delete your account? (yes/no): ").strip().lower()
                if confirm_delete == 'yes':
                    if account[3] == 0:
                        cursor = conn.cursor()
                        cursor.execute('''
                            DELETE FROM accounts WHERE account_number = %s
                        ''', (account_number,))
                        conn.commit()
                        cursor.close()
                        insert_audit_data(account_number, account[1], "Deleted Account", 0)
                        print("Account deleted successfully!")
                    else:
                        print("First withdraw all funds before deleting the account.")
                else:
                    print("Account deletion cancelled.")
                    
            elif choice1 == '9':
                insert_audit_data(account_number, account[1], "Logged Out", 0)
                print("Logged out successfully.")
                break
            
        elif account is None:
            print('='*30)
            print("Account not found. Please check your account number and PIN.")
            print('='*30)        
        input("Press Enter to continue...")
    elif choice == '3':
        break
    else:
        print("Invalid choice. Please try again.")