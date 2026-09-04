import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="SmartSpend",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# SESSION STATE
# =========================================================
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Description", "Amount", "Category"]
    )

# =========================================================
# CATEGORY DETECTION
# =========================================================
CATEGORY_KEYWORDS = {
    "Food": [
        "food", "pizza", "burger", "restaurant", "dosa",
        "coffee", "lunch", "dinner", "swiggy", "zomato"
    ],
    "Transport": [
        "uber", "ola", "metro", "bus", "auto",
        "cab", "petrol", "fuel", "rapido"
    ],
    "Shopping": [
        "amazon", "flipkart", "shopping", "clothes",
        "shoes", "mall", "myntra"
    ],
    "Entertainment": [
        "movie", "netflix", "game", "cinema",
        "spotify", "entertainment"
    ],
    "Education": [
        "book", "course", "college", "education",
        "exam", "study", "udemy"
    ],
    "Bills": [
        "rent", "electricity", "water", "recharge",
        "bill", "internet", "mobile"
    ],
    "Health": [
        "medicine", "doctor", "hospital",
        "pharmacy", "health"
    ]
}


def suggest_category(description):
    text = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category

    return "Other"


# =========================================================
# SMART INSIGHTS
# =========================================================
def generate_insights(df, budget):

    insights = []

    if df.empty:
        return ["Add some expenses to generate spending insights."]

    total = df["Amount"].sum()

    category_total = (
        df.groupby("Category")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    top_category = category_total.index[0]
    top_amount = category_total.iloc[0]

    average = df["Amount"].mean()

    insights.append(
        f"Your total recorded spending is ₹{total:,.0f}."
    )

    insights.append(
        f"{top_category} is your highest spending category "
        f"with ₹{top_amount:,.0f}."
    )

    insights.append(
        f"Your average transaction is ₹{average:,.0f}."
    )

    if budget > 0:

        percentage = (total / budget) * 100

        if percentage >= 100:
            insights.append(
                "You have crossed your monthly budget. "
                "Review your largest expenses."
            )

        elif percentage >= 80:
            insights.append(
                f"You have used {percentage:.0f}% of your budget. "
                "Keep an eye on upcoming expenses."
            )

        else:
            insights.append(
                f"You have used {percentage:.0f}% of your budget."
            )

    if top_amount > total * 0.5:
        insights.append(
            f"More than half of your spending is concentrated "
            f"in {top_category}."
        )

    return insights


# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:

    st.title("💰 SmartSpend")

    st.caption("Personal Finance Assistant")

    st.divider()

    st.subheader("Monthly Budget")

    budget = st.number_input(
        "Set your budget (₹)",
        min_value=0.0,
        value=10000.0,
        step=500.0
    )

    st.divider()

    st.subheader("Quick Actions")

    if st.button("🗑️ Clear All Expenses", use_container_width=True):

        st.session_state.expenses = pd.DataFrame(
            columns=["Date", "Description", "Amount", "Category"]
        )

        st.success("All expenses cleared.")
        st.rerun()


# =========================================================
# HEADER
# =========================================================
st.title("💰 SmartSpend")

st.write(
    "A simple and intelligent personal finance assistant "
    "to track, understand and manage your everyday spending."
)

st.divider()


# =========================================================
# ADD EXPENSE
# =========================================================
st.header("➕ Add Expense")

col1, col2, col3, col4 = st.columns([1.2, 2, 1.2, 1])

with col1:

    expense_date = st.date_input(
        "Date",
        value=date.today()
    )

with col2:

    description = st.text_input(
        "Description",
        placeholder="e.g. Pizza, Uber, Amazon"
    )

with col3:

    amount = st.number_input(
        "Amount (₹)",
        min_value=0.0,
        step=10.0
    )

with col4:

    st.write("")

    add_expense = st.button(
        "Add",
        type="primary",
        use_container_width=True
    )


if add_expense:

    if not description.strip():

        st.warning("Please enter a description.")

    elif amount <= 0:

        st.warning("Please enter an amount greater than zero.")

    else:

        category = suggest_category(description)

        new_row = pd.DataFrame({
            "Date": [expense_date],
            "Description": [description],
            "Amount": [amount],
            "Category": [category]
        })

        st.session_state.expenses = pd.concat(
            [
                st.session_state.expenses,
                new_row
            ],
            ignore_index=True
        )

        st.success(
            f"Expense added successfully • Category: {category}"
        )


# =========================================================
# CSV UPLOAD
# =========================================================
with st.expander("📁 Import transactions from CSV"):

    st.write(
        "CSV should contain: Date, Description and Amount."
    )

    uploaded_file = st.file_uploader(
        "Choose CSV file",
        type=["csv"]
    )

    if uploaded_file:

        try:

            uploaded = pd.read_csv(uploaded_file)

            required = {"Date", "Description", "Amount"}

            if not required.issubset(uploaded.columns):

                st.error(
                    "CSV must contain Date, Description and Amount columns."
                )

            else:

                uploaded["Date"] = pd.to_datetime(
                    uploaded["Date"],
                    errors="coerce"
                ).dt.date

                uploaded["Amount"] = pd.to_numeric(
                    uploaded["Amount"],
                    errors="coerce"
                )

                uploaded = uploaded.dropna(
                    subset=["Date", "Description", "Amount"]
                )

                uploaded["Category"] = uploaded[
                    "Description"
                ].apply(suggest_category)

                if st.button("Import CSV"):

                    st.session_state.expenses = pd.concat(
                        [
                            st.session_state.expenses,
                            uploaded[
                                [
                                    "Date",
                                    "Description",
                                    "Amount",
                                    "Category"
                                ]
                            ]
                        ],
                        ignore_index=True
                    )

                    st.success(
                        f"{len(uploaded)} transactions imported."
                    )

        except Exception as e:

            st.error(f"Could not process the CSV: {e}")


# =========================================================
# DASHBOARD
# =========================================================
df = st.session_state.expenses

st.header("📊 Financial Overview")

if df.empty:

    st.info(
        "No transactions yet. Add your first expense above "
        "to start your financial dashboard."
    )

else:

    total_spending = df["Amount"].sum()

    transaction_count = len(df)

    remaining_budget = budget - total_spending

    average_transaction = df["Amount"].mean()

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Spending",
        f"₹{total_spending:,.0f}"
    )

    c2.metric(
        "Transactions",
        transaction_count
    )

    c3.metric(
        "Remaining Budget",
        f"₹{remaining_budget:,.0f}"
    )

    c4.metric(
        "Average Expense",
        f"₹{average_transaction:,.0f}"
    )

    # -----------------------------------------------------
    # BUDGET PROGRESS
    # -----------------------------------------------------

    st.subheader("🎯 Budget Progress")

    if budget > 0:

        budget_percentage = min(
            total_spending / budget,
            1.0
        )

        st.progress(budget_percentage)

        used_percentage = (
            total_spending / budget
        ) * 100

        if total_spending > budget:

            st.error(
                f"Budget exceeded by ₹"
                f"{total_spending - budget:,.0f}"
            )

        elif used_percentage >= 80:

            st.warning(
                f"You have used {used_percentage:.0f}% "
                f"of your monthly budget."
            )

        else:

            st.success(
                f"You have used {used_percentage:.0f}% "
                f"of your monthly budget."
            )

    # -----------------------------------------------------
    # FILTERS
    # -----------------------------------------------------

    st.subheader("🔎 Filter Transactions")

    f1, f2 = st.columns(2)

    with f1:

        categories = ["All"] + sorted(
            df["Category"].unique().tolist()
        )

        selected_category = st.selectbox(
            "Category",
            categories
        )

    with f2:

        search = st.text_input(
            "Search description"
        )

    filtered_df = df.copy()

    if selected_category != "All":

        filtered_df = filtered_df[
            filtered_df["Category"] == selected_category
        ]

    if search:

        filtered_df = filtered_df[
            filtered_df["Description"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # -----------------------------------------------------
    # CHARTS
    # -----------------------------------------------------

    left, right = st.columns(2)

    category_data = (
        df.groupby("Category")["Amount"]
        .sum()
        .reset_index()
        .sort_values(
            "Amount",
            ascending=False
        )
    )

    with left:

        st.subheader("📈 Spending by Category")

        fig = px.bar(
            category_data,
            x="Category",
            y="Amount",
            text_auto=".0f"
        )

        fig.update_layout(
            xaxis_title="Category",
            yaxis_title="Amount (₹)",
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        st.subheader("🥧 Spending Distribution")

        fig2 = px.pie(
            category_data,
            names="Category",
            values="Amount",
            hole=0.45
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    # -----------------------------------------------------
    # DAILY TREND
    # -----------------------------------------------------

    st.subheader("📅 Spending Trend")

    trend = (
        df.groupby("Date")["Amount"]
        .sum()
        .reset_index()
    )

    trend["Date"] = pd.to_datetime(
        trend["Date"]
    )

    fig3 = px.line(
        trend,
        x="Date",
        y="Amount",
        markers=True
    )

    fig3.update_layout(
        xaxis_title="Date",
        yaxis_title="Amount (₹)"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # -----------------------------------------------------
    # SMART INSIGHTS
    # -----------------------------------------------------

    st.header("💡 Smart Spending Insights")

    insights = generate_insights(
        df,
        budget
    )

    for insight in insights:

        st.write(
            f"• {insight}"
        )

    # -----------------------------------------------------
    # TRANSACTION TABLE
    # -----------------------------------------------------

    st.subheader("📋 Transactions")

    display_df = filtered_df.copy()

    display_df["Amount"] = display_df[
        "Amount"
    ].apply(
        lambda x: f"₹{x:,.2f}"
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # DOWNLOAD
    # -----------------------------------------------------

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "⬇️ Download Transactions",
        data=csv_data,
        file_name="smartspend_transactions.csv",
        mime="text/csv"
    )


# =========================================================
# FOOTER
# =========================================================
st.divider()

st.caption(
    "SmartSpend • Personal Finance Assistant • "
    "Built with Python, Streamlit and Pandas"
)