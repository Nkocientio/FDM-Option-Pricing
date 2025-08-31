# FDM Model For Options.
## American, Bermudan and European options.

### Useful Links

- About American, Bermudan and European styles read [(0)](https://corporatefinanceinstitute.com/resources/derivatives/american-vs-european-vs-bermudan-options/)
- FDM methods [Quintus-Zhang](https://quintus-zhang.github.io/post/on_pricing_options_with_finite_difference_methods/)⭐️ also read [(1)](http://www.goddardconsulting.ca/option-pricing-finite-diff-index.html).
- Projected Successive Over-Relaxation (PSOR) [(2)](https://en.wikipedia.org/wiki/Successive_over-relaxation).
- Watch Reindolf Boadu Youtube [here](https://youtu.be/0t4ks24Szvs?si=zOkBtG_NyK1LOkBB).
  
### Model Summary
- An Explicit method is unstable, time steps is increased accordingly read [(3)](https://en.wikipedia.org/wiki/Von_Neumann_stability_analysis) [(4)](https://math.stackexchange.com/questions/3989847/stability-analysis-finite-difference-methods-black-scholes-pde).
- An exercisable node under (Implicit, Crank-Nicolson) is priced using the PSOR Algorithm.
- Bermudan Option exercise dates can be customized, monthly,quarterly, half-yearly or annually.
- Excel file is downloadable.
  
### Streamlit app
See the app [here](https://fdm-model-option-pricing-k.streamlit.app/).
