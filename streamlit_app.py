import hmac

import streamlit as st

from market_scout.crew import MarketScout


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="MarketScout",
    page_icon="📈",
    layout="wide"
)


# --------------------------------------------------
# Small layout customization
# --------------------------------------------------

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 2rem;
            max-width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Access code
# --------------------------------------------------
# Anyone can look around, but running MarketScout (which calls the AI and
# costs money) needs the access code. The code lives in Streamlit's secrets
# as ACCESS_CODE, never in this file.

def access_code_ok(code: str) -> bool:
    try:
        expected = st.secrets.get("ACCESS_CODE", "")
    except Exception:  # no secrets set up yet: nobody can run it
        expected = ""
    if not expected or not code:
        return False
    return hmac.compare_digest(code.strip(), str(expected))


# --------------------------------------------------
# Sidebar — screening controls
# --------------------------------------------------

with st.sidebar:

    st.header("Market Screening")

    st.caption(
        "Set the quantitative criteria used to screen "
        "the S&P 500."
    )

    min_return = st.number_input(
        "Minimum 1-Year Return (%)",
        min_value=0,
        max_value=200,
        value=10,
        step=5
    )

    max_volatility = st.number_input(
        "Maximum Volatility (%)",
        min_value=0,
        max_value=100,
        value=40,
        step=5
    )

    research_count = st.number_input(
        "Companies to Research",
        min_value=1,
        max_value=5,
        value=3,
        step=1
    )

    diversify = st.checkbox(
        "Diversify across sectors",
        value=True,
        help="Limits concentration among research candidates."
    )
    st.divider()

    # Ask for the code until it's been entered correctly once in this visit.
    if not st.session_state.get("access_ok"):
        code = st.text_input(
            "Access code",
            type="password",
            help="Running MarketScout needs an access code."
        )
        if access_code_ok(code):
            st.session_state.access_ok = True
        elif code:
            st.error("That code didn't work.")

    run = st.button(
        "Run MarketScout",
        type="primary",
        use_container_width=True
    )


# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown("## 📈 MarketScout")

st.caption(
    "AI-powered equity research — quantitative screening "
    "combined with current company research."
)


# --------------------------------------------------
# App overview
# --------------------------------------------------

overview1, overview2, overview3 = st.columns(3)

with overview1:
    st.caption("UNIVERSE")
    st.markdown("**S&P 500**")

with overview2:
    st.caption("SCREENING")
    st.markdown("**Quantitative**")

with overview3:
    st.caption("RESEARCH")
    st.markdown("**AI + Live Web**")


# --------------------------------------------------
# Run MarketScout
# --------------------------------------------------

if run and not st.session_state.get("access_ok"):

    st.warning(
        "Enter the access code in the sidebar to run MarketScout."
    )

elif run:

    inputs = {
        "min_return": min_return / 100,
        "max_volatility": max_volatility / 100,
        "research_count": research_count,
        "diversify": diversify
    }

    with st.spinner(
        "Screening the S&P 500 and researching candidates..."
    ):

        result = (
            MarketScout()
            .crew()
            .kickoff(inputs=inputs)
        )

    report = result.pydantic
    # st.write("DEBUG result:", result)
    # st.write("DEBUG pydantic:", report)

    # if report:
    #     st.write("DEBUG companies:", report.companies)

    if report is None:
        st.error(
            "MarketScout completed, but structured research "
            "results were not returned."
        )
        st.stop()


    # --------------------------------------------------
    # Research results
    # --------------------------------------------------

    st.markdown("### Research Candidates")

    if not report.companies:
        st.warning(
            "No research candidates were returned. "
            "Try relaxing the screening criteria."
        )
        st.stop()

    tabs = st.tabs(
        [company.ticker for company in report.companies]
    )
    # --------------------------------------------------
    # Company tabs
    # --------------------------------------------------

    for tab, company in zip(tabs, report.companies):

        with tab:

            st.markdown(
                f"## {company.ticker} — {company.company_name}"
            )


            # ------------------------------------------
            # Quantitative metrics
            # ------------------------------------------

            metric1, metric2, metric3 = st.columns(3)

            with metric1:
                st.metric(
                    "1-Year Return",
                    f"{company.period_return:.1%}"
                )

            with metric2:
                st.metric(
                    "Volatility",
                    f"{company.volatility:.1%}"
                )

            with metric3:
                st.metric(
                    "Sharpe Ratio",
                    f"{company.sharpe_ratio:.2f}"
                )


            # ------------------------------------------
            # Research summary
            # ------------------------------------------

            st.markdown("### Research Summary")

            st.write(
                company.research_summary
            )


            # ------------------------------------------
            # Catalysts and risks
            # ------------------------------------------

            catalyst_col, risk_col = st.columns(2)

            with catalyst_col:

                st.markdown("### Potential Catalysts")

                for catalyst in company.catalysts:
                    st.write(f"• {catalyst}")


            with risk_col:

                st.markdown("### Key Risks")

                for risk in company.risks:
                    st.write(f"• {risk}")


            # ------------------------------------------
            # Recent developments
            # ------------------------------------------

            with st.expander(
                "Recent Developments",
                expanded=False
            ):

                for development in company.recent_developments:
                    st.write(f"• {development}")


            # ------------------------------------------
            # Sources
            # ------------------------------------------

            with st.expander(
                "Sources",
                expanded=False
            ):

                for source in company.sources:
                    st.markdown(
                        f"[{source.title}]({source.url})"
                    )


# --------------------------------------------------
# Initial empty state
# --------------------------------------------------

else:

    st.info(
        "Set your screening criteria in the sidebar "
        "and click **Run MarketScout** to begin."
    )