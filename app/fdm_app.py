import random
from methods import*
from bermuda import get_dates

def main():
    st.title("FDM Option Pricing")
    st.markdown(f"##### (American, Bermudan and European) style options")
    st.markdown(f"Good article: [Quintus-Zhang](https://quintus-zhang.github.io/post/on_pricing_options_with_finite_difference_methods/)⭐️ also read [(0)](http://www.goddardconsulting.ca/option-pricing-finite-diff-index.html).")
    st.sidebar.title("Options Pricer")
    st.sidebar.markdown("**Made by:**")
    st.sidebar.write(random.choice(['Nkosembi','Matsie','Siba','Diya', 'Adriaan','Nasreen','Tumo','Levy'])) 
    st.sidebar.header("Model Inputs")
    
    method = st.sidebar.selectbox("FDM Method", ['Crank','Explicit','Implicit'])
    BC = st.sidebar.selectbox("Boundary Condition", ['Dirichlet','Neumann'])
    style = st.sidebar.selectbox("Style", ['European','American', 'Bermudan'])
    C_P = st.sidebar.selectbox("Option Type", ['Call', 'Put'])
    S = st.sidebar.number_input("Spot Price (S)", min_value=0.001, value=100.0)
    K = st.sidebar.number_input("Strike Price (K)", min_value=0.001, value=99.0)
    vol = st.sidebar.number_input("Volatility (σ)", min_value=0.0001,max_value=1.0, value=0.2)
    T = st.sidebar.number_input("Time to Maturity (T)", min_value=0.001, value=1.0)
    r = st.sidebar.number_input("Risk-Free Rate (r)", min_value=0.0, value=0.06)
    q = st.sidebar.number_input("Dividend Yield (q)", min_value=0.0,max_value = r, value=0.0)
    sMin = st.sidebar.number_input("Asset Min", min_value=0.00,max_value = S, value=0.00)
    sMax = st.sidebar.number_input( "Asset Max", min_value=sMin, value=round(2*max(S,K)*np.exp((r-q)*T),2) )
    Ns = st.sidebar.number_input("Number of Asset Steps", min_value=3, max_value=1000, value=12)
    Nt = st.sidebar.number_input("Number of Time Steps", min_value=3, max_value=1000, value=12) # max_value to be increased...

    _dates = np.array([datetime.now()], dtype='datetime64[D]' )
    if style == 'Bermudan':
        _exercised = st.sidebar.selectbox('Enter exercise_dates', ['Half-Yearly','Monthly','Quarterly','Anually','Customized'])
        _dates = get_dates(_exercised,T)
    if style == 'European':
        option = FDM_Method(style,C_P,S,K,T,r,q,vol,Nt,Ns,sMin,sMax,method,BC,_dates)
    else:
        w = st.sidebar.number_input("Omega", min_value=1.00,max_value=2.0, value=1.10)
        tol = st.sidebar.number_input("Tolerance 1e-N", min_value=2 ,max_value=10, value=6)
        st.markdown(f"About the PSOR algorithm read [[1]](https://en.wikipedia.org/wiki/Successive_over-relaxation) and watch [Reindolf](https://youtu.be/0t4ks24Szvs?si=zOkBtG_NyK1LOkBB).")
        option = FDM_Method(style,C_P,S,K,T,r,q,vol,Nt,Ns,sMin,sMax,method,BC,_dates,w,tol)
        new_tol = option.tolN
        if tol != new_tol and method != 'Explicit':
            st.write(f"For speed purposes, tol is set to: 1e-{new_tol} 😭")
    
    if method == 'Explicit':
        new_Nt = option.tSteps
        if Nt != new_Nt:
            st.markdown(f"For stability purposes, timestep is set to {new_Nt} — read "
    "[[2]](https://en.wikipedia.org/wiki/Von_Neumann_stability_analysis) "
    "[[3]](https://math.stackexchange.com/questions/3989847/stability-analysis-finite-difference-methods-black-scholes-pde). "
    "$\\Delta t = \\frac{{0.99}}{{(N_{{s}} \\cdot \\sigma)^2}}$")
    
    Nt = option.tSteps
    file_name = f"{style}_{C_P} {Ns} x {Nt} step by {method} ({BC}-BC).xlsx"
    if (Ns+Nt) < 201:
        download = st.sidebar.selectbox("Download the Grid ?", ['No','Yes'])
    else: 
        download = 'No'
        
    if st.button(f"Evaluate {file_name[:-5]}"):
        with st.spinner('Calculating...'):
            price = option.price()
            if option.mayNotConverge:
                st.write(f"Taking longer (may not converge). Total loops ({option.loopCount})")
                
            st.markdown(f"##### Calculated value: {price:.10f}")
            if style == 'European':
                analytical_price = option.blackScholes()
                st.markdown(f"##### Black_Scholes gives: {analytical_price:.10f}")
            else:
                analytical_price = 'N/A'
        st.markdown(f"_Binomial Model app:_ [here](https://binomial-model-option-pricing-k.streamlit.app/).")
        if download == 'Yes':
            with st.spinner('⌛ Saving...'):
                workbook_bytes = option.excel_values(analytical_price,price)
                st.download_button(
                    label="Save in Excel",
                    data=workbook_bytes,
                    file_name=file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        st.write("Oops sorry my friend")
