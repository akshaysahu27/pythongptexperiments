import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import locale

# Set locale for formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_IN')
except:
    locale.setlocale(locale.LC_ALL, '')

def format_inr(value):
    try:
        return locale.currency(value, grouping=True, symbol=True)
    except:
        return f"₹{value:,.2f}"

def calculate_amortization_schedule(loan_amount, annual_interest_rate, tenure_years, extra_payment=0):
    monthly_interest_rate = (annual_interest_rate / 100) / 12
    number_of_payments = tenure_years * 12

    emi = loan_amount * monthly_interest_rate * ((1 + monthly_interest_rate) ** number_of_payments) / \
          ((1 + monthly_interest_rate) ** number_of_payments - 1)

    schedule = []
    remaining_principal = loan_amount
    total_interest = 0
    month = 0

    while remaining_principal > 0:
        month += 1
        interest_paid = remaining_principal * monthly_interest_rate
        principal_paid = emi - interest_paid + extra_payment
        if principal_paid > remaining_principal:
            principal_paid = remaining_principal
            emi_total = remaining_principal + interest_paid
        else:
            emi_total = emi + extra_payment
        remaining_principal -= principal_paid
        total_interest += interest_paid

        schedule.append({
            "Month": month,
            "EMI Paid": round(emi_total, 2),
            "Principal Paid": round(principal_paid, 2),
            "Interest Paid": round(interest_paid, 2),
            "Remaining Principal": round(max(remaining_principal, 0), 2),
            "Total Interest": round(total_interest, 2)
        })

    total_payment = sum(item['EMI Paid'] for item in schedule)

    return round(emi, 2), round(total_payment, 2), round(total_interest, 2), pd.DataFrame(schedule)

# Streamlit App
st.set_page_config(page_title="Home Loan Calculator", layout="wide")
st.title("🏡 Home Loan EMI Calculator")

with st.sidebar:
    st.header("Loan Parameters")
    loan_amount = st.number_input("Loan Amount (₹)", value=5000000, step=50000)
    annual_interest_rate = st.number_input("Annual Interest Rate (%)", value=8.5, step=0.1)
    tenure_years = st.number_input("Loan Tenure (Years)", value=20, step=1)
    extra_payment = st.number_input("Extra Monthly Payment (₹)", value=0, step=1000)
    calculate = st.button("Calculate EMI")

if calculate:
    emi, total_payment, total_interest, df_schedule = calculate_amortization_schedule(
        loan_amount, annual_interest_rate, tenure_years, extra_payment
    )

    st.success(f"🗓️ Monthly EMI (without extra): {format_inr(emi)}")
    st.info(f"💵 Total Payment: {format_inr(total_payment)}")
    st.warning(f"📈 Total Interest Paid: {format_inr(total_interest)}")
    st.caption(f"Loan paid off in {len(df_schedule)} months ({len(df_schedule)//12} years and {len(df_schedule)%12} months)")

    st.subheader("📊 Amortization Schedule")
    df_display = df_schedule.copy()
    for col in df_display.columns[1:]:
        df_display[col] = df_display[col].apply(format_inr)
    st.dataframe(df_display, use_container_width=True, height=400)

    # Charts
    st.subheader("🌐 Visualizations")
    chart1 = go.Figure()
    chart1.add_trace(go.Scatter(x=df_schedule["Month"], y=df_schedule["Principal Paid"], mode='lines', name='Principal'))
    chart1.add_trace(go.Scatter(x=df_schedule["Month"], y=df_schedule["Interest Paid"], mode='lines', name='Interest'))
    chart1.update_layout(title="EMI Split Over Time", xaxis_title="Month", yaxis_title="Amount (₹)")
    st.plotly_chart(chart1, use_container_width=True)

    chart2 = px.area(df_schedule, x="Month", y="Remaining Principal", title="Remaining Principal Over Time")
    st.plotly_chart(chart2, use_container_width=True)

    # Download option
    csv = df_schedule.to_csv(index=False).encode('utf-8')
    st.download_button("Download Schedule as CSV", data=csv, file_name='amortization_schedule.csv', mime='text/csv')
