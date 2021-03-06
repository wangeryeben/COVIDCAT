import webbrowser
import datetime
from PIL import Image
import streamlit as st
import pandas as pd
import numpy as np
import collections
import functools
import inspect
import textwrap
import altair as alt
import matplotlib.pyplot as plt
import base64
import time
import another
import sir


def valid_input_range(num):
    if num < 0 or num > 100:
        st.sidebar.error("Error! Please put a number between 0 and 100.")


@st.cache
def open_file(file):
    if file is not None:
        txtstr = ""
        lines = file.readlines()
        Daily_arrival_rate = []
        try:
            for line in lines:
                txtstr = txtstr + line
                line = line.strip('\n')
                Daily_arrival_rate.extend(line.split(' '))
            return Daily_arrival_rate
        except:
            st.warning("Error! Incorrect format.")


def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


st.set_option('deprecation.showfileUploaderEncoding', False)

# img = Image.open(r"logo.png")
# st.image(img)
st.title('COVID-CAT')

st.markdown("COVID-CAT is a tool for hospital and emergency department (ED) managers, physicians, "
            "and health care workers to quickly convert predictions of future COVID-19 patient arrivals "
            "into predictions of future COVID-19 census levels in the ED, main hospital, and the ICU. ")

link = '[A complete description of the methodology is provided here]' \
       '(https://covidcat.web.unc.edu/files/2020/06/COVID-CAT.pdf)'

if st.checkbox("Click here to see methodology", key="M"):
    st.markdown("Below is a visual representation of what the mathematical model assumes regarding patient flow. "
                "COVID-19 suspected or confirmed patients arrive at the ED. After their stay in the ED is complete, "
                "they are either discharged from the ED, admitted to the main hospital COVID-19 unit, "
                "or admitted directly to the ICU. Patients who are admitted to the COVID-19 unit initially may later "
                "be transferred to the ICU if their condition deteriorates; "
                "similarly, patients who are first admitted to the ICU may be transferred to the COVID-19 unit "
                "in the hospital if their condition improves. The user may set the percentages of admission "
                "to the hospital and the ICU so as to account for these possibilities. "
                "However, it is important to note that the mathematical model assumes that patients start "
                "occupying a bed in the hospital and/or the ICU right after the patient’s stay in the ED is over "
                "and therefore the model would be biased towards capturing the bed demand in the hospital "
                "and the ICU slightly early.")
    # img2 = Image.open(r"Patient-Flow.png")
    # st.image(img2, width=720)

    st.markdown("The methodology behind COVID-CAT is based on known results from queueing theory, "
                "more specifically the analysis of the $M_t/G/\infty$ queue, which assumes Poisson arrivals "
                "with time-variant rates and infinitely many servers.")
    st.markdown(link, unsafe_allow_html=True)
    st.markdown("One implicit assumption of the model is that all patients who arrive at "
                "the ED are admitted, and all patients who need hospitalization and/or ICU are also admitted. "
                "This means that the model assumes that there are no limits on the numbers of COVID-19 patients "
                "the ED, the hospital, and the ICU can have at any point in time. Therefore, the predictions made by "
                "COVID-CAT should be interpreted as bed capacities that would be needed to fully meet the patient "
                "demand at different points in time in the future. They should NOT be interpreted as what "
                "the actual census levels will be as those levels would be ED and hospital specific depending on "
                "the number of beds available as well as the policies the ED and the hospital would adopt to deal with "
                "the excess demand. By not making specific assumptions on bed capacities as well as such "
                "policy choices, we aim to make the tool useful not only for UNC but other EDs and hospitals as well.")

st.sidebar.subheader("Click for SIR Model or Upload Files")

st.sidebar.subheader("SIR")
current_hospitalized = st.sidebar.number_input("Current Hospitalized Patients", value=50)
doubling_time = st.sidebar.number_input("Doubling Time in Days (Up to Today)", value=8)
hospitalized_rate = st.sidebar.number_input("Hospitalized Rate (%)", value=10.0)
infectious_days = st.sidebar.number_input("Infectious Days", value=10)
market_share = st.sidebar.number_input("Hospital Market Share (%)", value=30)
n_days = st.sidebar.number_input("Days To Predict From Today", value=20)
population = st.sidebar.number_input("Regional Population", value=100000)
recovered = st.sidebar.number_input("Recovered Patients", value=200)
mitigation_date = st.sidebar.text_input("Mitigation Date (YYYY-MM-DD)", value=datetime.date(2020, 10, 8))
relative_contact_rate = st.sidebar.number_input("Relative Contact Rate (%)", value=50.0)
arriving_rate = st.sidebar.number_input("Arriving Rate (%)", value=50.0)

hourly_ratio = st.sidebar.text_input("Hourly Ratio (Only for ED: input ratio for 24 hrs)（1:2:2:3:xxx)",
                                     value=1)
hourly_ratio = hourly_ratio.split(":")
hourly_distribution = []
for i in hourly_ratio:
    hourly_distribution.append(int(i))
    # st.write(type(hourly_ratio[1]))
    # st.write(type(int(hourly_ratio[1])))

    # st.write(hourly_distribution)
    # st.write(type(hourly_distribution))
    # a = np.array(hourly_distribution)
p = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                  n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate)
s = sir.Sir(p).get_SIR_model()
sir_data = pd.DataFrame(
    {
        "Susceptible": s[0],
        "Infected": s[1],
        "Recovered": s[2]
    }
)
st.subheader("SIR")
st.line_chart(sir_data)

st.markdown(f"The estimated number of currently infected individuals is {round(s[1][0])}. "
            f"This is based on current inputs for Hospitalizations {current_hospitalized}, "
            f"Hospitalization rate {hospitalized_rate}, Regional population {population}, "
            f"and Hospital market share {market_share}.")
st.markdown(f"An initial doubling time of {doubling_time} days and a recovery time of {infectious_days} days "
            f"imply an $R_0$ of {round(s[2][0])}.")

if st.sidebar.checkbox("Use SIR model for prediction"):
    p = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                      n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate)
    r_daily = sir.Sir(p).get_prediction()

    p_hourly = sir.parameter(current_hospitalized, doubling_time, hospitalized_rate, infectious_days, market_share,
                             n_days, population, recovered, mitigation_date, relative_contact_rate, arriving_rate,
                             hourly_distribution)
    r_hourly = sir.Sir(p_hourly).get_hourly_prediction()

if st.sidebar.checkbox("Upload Files"):
    f_daily = st.sidebar.file_uploader("Update Daily Arrival Predictions", key="D", type="txt")
    f_hourly = st.sidebar.file_uploader("Update ED Hourly Arrival Predictions", key="H", type="txt")
    r_daily = open_file(f_daily)
    r_hourly = open_file(f_hourly)

st.sidebar.subheader("ED")
ed_mean = st.sidebar.number_input("Mean ED LOS (Hours)", value=7.5)
ed_std = st.sidebar.number_input("STD. ED LOS (Hours)", value=8.2)
ed_initial = st.sidebar.number_input("Current Census (Patients)", value=8, key="E")

st.sidebar.subheader("Hospital")
h_mean = st.sidebar.number_input("Mean H LOS (Days)", value=8)
h_std = st.sidebar.number_input("STD. H LOS (Days)", value=6)
h_initial = st.sidebar.number_input("Current Census (Patients)", value=15, key="HOS")
p_hos = st.sidebar.number_input("% COVID Patients Hospitalized:", value=30) / 100
valid_input_range(p_hos)

st.sidebar.subheader("ICU")
icu_mean = st.sidebar.number_input("Mean ICU LOS (Days)", value=13)
icu_std = st.sidebar.number_input("STD. ICU LOS (Days)", value=8)
icu_initial = st.sidebar.number_input("Current Census (Patients)", value=3, key="ICU")
p_icu = st.sidebar.number_input("% COVID Patients Need ICU:", value=6) / 100
valid_input_range(p_icu)

# r_daily = [40.79408289, 43.51368842, 46.67691754, 52.21256851, 57.36245982, 65.1933807,
#            69.24385702, 73.68009298, 77.53768947, 79.46648772, 80.43088684]

if st.sidebar.button("run"):
    if ed_mean != 0 and ed_std != 0 and r_hourly is not None and r_daily is not None:
        with st.spinner("Running .. progress shown here"):
            st.subheader("ED")
            tlist, mt, mt5, mt95, df = another.ed_run(ed_mean, ed_std, ed_initial, r_daily, r_hourly)
            dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                               columns=["Mean", "Lower", "Upper"],
                               index=pd.RangeIndex(len(tlist), name="x"))
            line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
                x="x",
                y="Mean",
            )
            band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
                x='x',
                y='Lower',
                y2='Upper'
            )
            band.encoding.x.title = "Days"
            band.encoding.y.title = "Census"
            st.markdown(f"The output is based on the ED staying hours with a mean of {ed_mean}, "
                        f"standard deviation of {ed_std}, current ED patients {ed_initial}, "
                        "and daily and hourly arrival rate according to SIR or uploaded files")

            line + band
            st.write(df)

            if df is not None:
                tmp_download_link = download_link(df, 'ED_data.csv', 'Click here to download the data report')
                st.markdown(tmp_download_link, unsafe_allow_html=True)

    # if st.sidebar.checkbox("Click here to display results", key="B"):
    if h_mean != 0 and h_std != 0 and r_daily is not None and p_hos != 0:
        with st.spinner("Running .. progress shown here"):
            st.subheader("Hospital")
            tlist, mt, mt5, mt95, df = another.hos_run(h_mean, h_std, h_initial, r_daily, p_hos)
            dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                               columns=["Mean", "Lower", "Upper"],
                               index=pd.RangeIndex(len(tlist), name="x"))
            line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
                x="x",
                y="Mean",
            )
            band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
                x='x',
                y='Lower',
                y2='Upper'
            )
            band.encoding.x.title = "Days"
            band.encoding.y.title = "Census"

            st.markdown(f"The output is based on the hospital staying hours with a mean of {h_mean}, "
                        f"standard deviation of {h_std}, current hospital patients {h_initial},"
                        f"percentage of hospitalized patients ({p_hos} "
                        "and daily arrival rate according to SIR or uploaded files")

            line + band
            st.write(df)

            if df is not None:
                tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
                st.markdown(tmp_download_link, unsafe_allow_html=True)

    if icu_mean != 0 and icu_std != 0 and r_daily is not None and p_icu != 0:
        with st.spinner("Running .. progress shown here"):
            st.subheader("ICU")
            tlist, mt, mt5, mt95, df = another.icu_run(icu_mean, icu_std, icu_initial, r_daily, p_icu)

            dfr = pd.DataFrame(list(zip(mt, mt5, mt95)),
                               columns=["Mean", "Lower", "Upper"],
                               index=pd.RangeIndex(len(tlist), name="x"))
            line = alt.Chart(dfr.reset_index()).mark_line(color="#0E6678").encode(
                x="x",
                y="Mean",
            )
            band = line.mark_area(opacity=0.5, color="#9CD3E7").encode(
                x='x',
                y='Lower',
                y2='Upper'
            )
            band.encoding.x.title = "Days"
            band.encoding.y.title = "Census"
            st.markdown(f"The output is based on the hospital staying hours with a mean of {icu_mean}, "
                        f"standard deviation of {icu_std}, current hospital patients {icu_initial}, "
                        f"percentage of patients that needed ICU ({p_icu}),"
                        "and daily arrival rate according to SIR or uploaded files")

            line + band
            st.write(df)

            if df is not None:
                tmp_download_link = download_link(df, 'hospital_data.csv', 'Click here to download the data report')
                st.markdown(tmp_download_link, unsafe_allow_html=True)
