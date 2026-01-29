import streamlit as st
import random
import string
import pandas as pd

from Database import conn
from main import (
    create_accounts_table,
    create_audit_table,
    insert_account_data,
    insert_audit_data,
    login_account,
    fetch_account_details,
    deposit_amount,
    withdraw_amount,
    transaction_history,
)

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="SmartBank",
    page_icon="🏦",
    layout="wide"
)

create_accounts_table()
create_audit_table()

if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- CLEAN CSS ----------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
}

.card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e6e6e6;
    background-color: white;
}

h1,h2,h3 {
    color:#1f2937;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🏦 SmartBank")

menu = st.sidebar.radio(
    "Menu",
    ["Home","Create Account","Login"] if not st.session_state.user
    else ["Dashboard","Transfer","History","Profile","Logout"]
)

# =================================================
# HOME
# =================================================
if menu=="Home":
    st.title("🏦 SmartBank")
    st.subheader("Simple • Secure • Smart Banking")

    c1,c2,c3 = st.columns(3)

    c1.metric("Security","High")
    c2.metric("Speed","Fast")
    c3.metric("Support","24/7")

    st.info("Welcome to a clean and modern digital banking system.")

# =================================================
# CREATE ACCOUNT
# =================================================
elif menu=="Create Account":
    st.title("📝 Create Account")

    name = st.text_input("Full Name")
    pin = st.text_input("4-digit PIN",type="password")

    if st.button("Create Account"):
        if not(pin.isdigit() and len(pin)==4):
            st.error("PIN must be 4 digits")
        else:
            acc = ''.join(random.choices(string.digits,k=10))
            insert_account_data(acc,name,pin,0)
            insert_audit_data(acc,name,"Account Created",0)

            st.success("Account Created Successfully")
            st.code(f"Your Account Number: {acc}")

# =================================================
# LOGIN
# =================================================
elif menu=="Login":
    st.title("🔐 Login")

    acc = st.text_input("Account Number")
    pin = st.text_input("PIN",type="password")

    if st.button("Login"):
        user = login_account(acc,pin)
        if user:
            st.session_state.user = user
            insert_audit_data(acc,user[1],"Login",0)
            st.success("Login Successful")
            st.rerun()
        else:
            st.error("Invalid Credentials")

# =================================================
# DASHBOARD
# =================================================
elif menu=="Dashboard":
    user = fetch_account_details(st.session_state.user[0])

    st.title(f"Welcome, {user[1]} 👋")

    c1,c2,c3 = st.columns(3)

    c1.markdown(f"""
    <div class="card">
        <h3>Balance</h3>
        <h2>₹{user[3]}</h2>
    </div>
    """, unsafe_allow_html=True)

    c2.markdown(f"""
    <div class="card">
        <h3>Account No</h3>
        <p>{user[0]}</p>
    </div>
    """, unsafe_allow_html=True)

    c3.markdown("""
    <div class="card">
        <h3>Status</h3>
        <p>Active</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    col1,col2 = st.columns(2)

    amt = col1.number_input("Deposit Amount",min_value=0.0)
    if col1.button("Deposit"):
        deposit_amount(user[0],amt)
        insert_audit_data(user[0],user[1],"Deposit",amt)
        st.success("Deposited")
        st.rerun()

    amt2 = col2.number_input("Withdraw Amount",min_value=0.0)
    if col2.button("Withdraw"):
        if amt2>user[3]:
            st.error("Insufficient Balance")
        else:
            withdraw_amount(user[0],amt2)
            insert_audit_data(user[0],user[1],"Withdraw",amt2)
            st.success("Withdrawn")
            st.rerun()

# =================================================
# TRANSFER
# =================================================
elif menu=="Transfer":
    st.title("💸 Fund Transfer")

    sender = fetch_account_details(st.session_state.user[0])

    target = st.text_input("Recipient Account Number")
    amt = st.number_input("Amount",min_value=0.0)
    pin = st.text_input("Enter PIN",type="password")

    if st.button("Transfer"):
        rec = fetch_account_details(target)

        if not rec:
            st.error("Recipient not found")
        elif pin!=sender[2]:
            st.error("Wrong PIN")
        elif amt>sender[3]:
            st.error("Low balance")
        else:
            withdraw_amount(sender[0],amt)
            deposit_amount(target,amt)

            insert_audit_data(sender[0],sender[1],"Transfer Sent",amt)
            insert_audit_data(target,rec[1],"Transfer Received",amt)

            st.success("Transfer Successful")

# =================================================
# HISTORY
# =================================================
elif menu=="History":
    st.title("📜 Transaction History")

    tx = transaction_history(st.session_state.user[0])

    if tx:
        df = pd.DataFrame(
            tx,
            columns=["ID","Account","Name","Action","Amount","Time"]
        )
        st.dataframe(df,use_container_width=True)
    else:
        st.info("No Transactions Found")

# =================================================
# PROFILE
# =================================================
elif menu=="Profile":
    st.title("👤 Profile")

    acc_no = st.session_state.user[0]
    acc = fetch_account_details(acc_no)

    new_name = st.text_input("New Name")
    if st.button("Update Name"):
        cur=conn.cursor()
        cur.execute(
            "UPDATE accounts SET name=%s WHERE account_number=%s",
            (new_name,acc_no)
        )
        conn.commit()
        cur.close()

        insert_audit_data(acc_no,new_name,"Changed Name",0)
        st.success("Name Updated")

    new_pin = st.text_input("New PIN",type="password")
    if st.button("Update PIN"):
        if new_pin.isdigit() and len(new_pin)==4:
            cur=conn.cursor()
            cur.execute(
                "UPDATE accounts SET pin=%s WHERE account_number=%s",
                (new_pin,acc_no)
            )
            conn.commit()
            cur.close()

            insert_audit_data(acc_no,acc[1],"Changed PIN",0)
            st.success("PIN Updated")
        else:
            st.error("PIN must be 4 digits")

    st.divider()

    st.subheader("Delete Account")

    if st.button("Delete My Account"):
        if acc[3] != 0:
            st.error("Balance must be 0 to delete account")
        else:
            # Insert audit BEFORE deleting
            insert_audit_data(acc_no, acc[1], "Deleted Account", 0)

            # Now delete
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM accounts WHERE account_number=%s",
                (acc_no,)
            )
            conn.commit()
            cur.close()

            st.session_state.user = None
            st.success("Account Deleted Successfully")
            st.rerun()


# =================================================
# LOGOUT
# =================================================
elif menu=="Logout":
    st.session_state.user=None
    st.success("Logged Out")
    st.rerun()