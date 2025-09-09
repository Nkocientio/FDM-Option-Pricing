import numpy as np
import streamlit as st
from datetime import datetime,timedelta

def interval_dates(now,expire,freq,yrs):
    freq_dict ={
        'Monthly' : 1,
        'Quarterly' :3,
        'Half-Yearly': 6,
        'Anually': 12
    }
    start_date = now + timedelta(days=365*freq_dict[freq]/12)
    end_date = start_date + timedelta(days = yrs*365) 
  
    dates = np.arange(start_date, end_date, dtype=f'datetime64[{freq_dict[freq]}M]')
    dates = np.unique( np.append(dates, [expire]).astype('datetime64[D]') )
    return dates

def get_dates(freqency,yrs):
    st.write(f'{freqency} exercise Dates ')
    today = datetime.now()
    expire_date = today + timedelta(days=365*yrs)
    if 'b_dates' not in st.session_state:
        st.session_state.b_dates = np.array([expire_date], dtype='datetime64[D]')
    if freqency == 'Customized':
        with st.form(key='bermuda_dates'):
            dt = st.date_input('Enter the exercise date', value =today, min_value=today, max_value = expire_date)
            
            col1, col2 = st.columns(2) 
            with col1:
                submit_button = st.form_submit_button()
            with col2:
                clear_button = st.form_submit_button(label='Clear Date')
                
            if submit_button and dt not in st.session_state.b_dates:
                st.session_state.b_dates = np.hstack((st.session_state.b_dates, dt))  # Append new column
                
            if clear_button:
                st.session_state.b_dates = st.session_state.b_dates[:-1]
    else:
        st.session_state.b_dates = interval_dates(today,expire_date,freqency,yrs)
        
    # Display the dates Horizontally
    st.write(st.session_state.b_dates[:, np.newaxis].T)
    return st.session_state.b_dates
