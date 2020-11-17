import pandas as pd
from numpy import log, square, sqrt, random, mean, inf, loadtxt, array
from math import ceil, erf, floor
from prettytable import PrettyTable
from scipy.integrate import quad
from scipy.stats import norm, binom, poisson, lognorm
import matplotlib.pyplot as plt
from datetime import datetime
import streamlit

global lognorm


def lognorm(x, mu, sigma):
    a = (log(x) - mu) / sqrt(2 * sigma ** 2)
    p = 0.5 + 0.5 * erf(a)
    return p


global lognormc


def lognormc(x, mu, sigma):
    return 1 - lognorm(x, mu, sigma)


global f


def f(s, t, mu, stddev, Arrival_rate):
    hourofday = floor((t - s) % 24)
    p = flambda(t - s, Arrival_rate) * (1 - lognorm(s, mu, stddev))
    return p


global flambda

def flambda(x, Arrival_rate):
    p = floor(x)
    return Arrival_rate[p]


global rs


def rs(x, mu, stddev, length_of_stay_mean):
    temp_int, temp_err = quad(lognormc, 0, x, args=(mu, stddev), limit=500)
    return temp_int / length_of_stay_mean

def maxc(datalist):
    temp = max(datalist)
    if temp <= 0:
        return round(0, 2)
    else:
        return round(temp, 2)


@streamlit.cache(suppress_st_warning=True)
def hos_run(Hospital_length_of_stay_mean, Hospital_length_of_stay_std, Hospital_initial_condition, rate,
            Percentage_hospitalized, maxp):
    mu = log(square(Hospital_length_of_stay_mean) / sqrt(
        square(Hospital_length_of_stay_mean) + square(Hospital_length_of_stay_mean)))
    stddev = sqrt(log(1 + square(Hospital_length_of_stay_mean) / square(Hospital_length_of_stay_mean)))
    ArrivalRate = array(rate, dtype=float)
    ArrivalRate = ArrivalRate * Percentage_hospitalized
    TotalTimeLength = ArrivalRate.size
    initial_condition = Hospital_initial_condition

    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    mt = []
    mt5 = []
    mt95 = []
    pt25 = []
    pt50 = []
    pt75 = []
    pt100 = []
    pt125 = []
    pt150 = []
    pt175 = []
    error = []
    st = []
    stl = []

    p1 = int(1 / 6 * maxp)
    p2 = int(2 / 6 * maxp)
    p3 = int(3 / 6 * maxp)
    p4 = int(4 / 6 * maxp)
    p5 = int(5 / 6 * maxp)
    p6 = int(6 / 6 * maxp)

    my_bar = streamlit.progress(0)
    while t <= TotalTimeLength:
        percent_complete = t / TotalTimeLength
        my_bar.progress(percent_complete)

        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate))
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, Hospital_length_of_stay_mean)
        # Calculate the mean
        mt_temp = initial_condition * probability_still_in_system + ans
        mt.append(mt_temp)

        temptotal = 0
        flag = [False, False]
        tempcdf = 0

        while tempcdf <= 0.99:
            i = 0
            if t <= 20:
                while i <= temptotal and i <= initial_condition:
                    if i <= initial_condition:
                        tempcdf = tempcdf + binom.pmf(i, initial_condition, probability_still_in_system) \
                                  * poisson.pmf((temptotal - i), ans)
                    i = i + 1
            else:
                tempcdf = poisson.cdf(temptotal, ans)

            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == p1:
                pt25.append(1 - tempcdf)
            if temptotal == p2:
                pt50.append(1 - tempcdf)
            if temptotal == p3:
                pt75.append(1 - tempcdf)
            if temptotal == p4:
                pt100.append(1 - tempcdf)
            if temptotal == p5:
                pt125.append(1 - tempcdf)
            if temptotal == p6:
                pt150.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < p1:
            pt25.append(float(0))
        if temptotal < p2:
            pt50.append(float(0))
        if temptotal < p3:
            pt75.append(float(0))
        if temptotal < p4:
            pt100.append(float(0))
        if temptotal < p5:
            pt125.append(float(0))
        if temptotal < p6:
            pt150.append(float(0))
        t = t + 1

    l = len(rate)
    l1 = int(1 / 10 * l)
    l2 = int(2 / 10 * l)
    l3 = int(3 / 10 * l)
    l4 = int(4 / 10 * l)
    l5 = int(5 / 10 * l)
    l6 = int(6 / 10 * l)
    l7 = int(7 / 10 * l)
    l8 = int(8 / 10 * l)
    l9 = int(9 / 10 * l)

    data = {
        "# Patients": [p1, p2, p3, p4, p5, p6],
        str(l1) + "Days": [maxc(pt25[0:l1]), maxc(pt50[0:l1]), maxc(pt75[0:l1]), maxc(pt100[0:l1]), maxc(pt125[0:l1]),
                           maxc(pt150[0:l1])],
        str(l2) + "Days": [maxc(pt25[0:l2]), maxc(pt50[0:l2]), maxc(pt75[0:l2]), maxc(pt100[0:l2]), maxc(pt125[0:l2]),
                           maxc(pt150[0:l2])],
        str(l3) + "Days": [maxc(pt25[0:l3]), maxc(pt50[0:l3]), maxc(pt75[0:l3]), maxc(pt100[0:l3]), maxc(pt125[0:l3]),
                           maxc(pt150[0:l3])],
        str(l4) + "Days": [maxc(pt25[0:l4]), maxc(pt50[0:l4]), maxc(pt75[0:l4]), maxc(pt100[0:l4]), maxc(pt125[0:l4]),
                           maxc(pt150[0:l4])],
        str(l5) + "Days": [maxc(pt25[0:l5]), maxc(pt50[0:l5]), maxc(pt75[0:l5]), maxc(pt100[0:l5]), maxc(pt125[0:l5]),
                           maxc(pt150[0:l5])],
        str(l6) + "Days": [maxc(pt25[0:l6]), maxc(pt50[0:l6]), maxc(pt75[0:l6]), maxc(pt100[0:l6]), maxc(pt125[0:l6]),
                           maxc(pt150[0:l6])],
        str(l7) + "Days": [maxc(pt25[0:l7]), maxc(pt50[0:l7]), maxc(pt75[0:l7]), maxc(pt100[0:l7]), maxc(pt125[0:l7]),
                           maxc(pt150[0:l7])],
        str(l8) + "Days": [maxc(pt25[0:l8]), maxc(pt50[0:l8]), maxc(pt75[0:l8]), maxc(pt100[0:l8]), maxc(pt125[0:l8]),
                           maxc(pt150[0:l8])],
        str(l9) + "Days": [maxc(pt25[0:l9]), maxc(pt50[0:l9]), maxc(pt75[0:l9]), maxc(pt100[0:l9]), maxc(pt125[0:l9]),
                           maxc(pt150[0:l9])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


@streamlit.cache(suppress_st_warning=True)
def icu_run(ICU_length_of_stay_mean, ICU_length_of_stay_std, ICU_initial_condition, rate, Percentage_icu, maxp):
    mu = log(square(ICU_length_of_stay_mean) / sqrt(
        square(ICU_length_of_stay_mean) + square(ICU_length_of_stay_mean)))
    stddev = sqrt(
        log(1 + square(ICU_length_of_stay_mean) / square(ICU_length_of_stay_mean)))
    ArrivalRate = array(rate, dtype=float)
    ArrivalRate = ArrivalRate * Percentage_icu
    TotalTimeLength = ArrivalRate.size
    initial_condition = ICU_initial_condition

    step = 1
    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    zeros = [0 for i in tlist]
    mt = []
    mt5 = []
    mt95 = []
    pt15 = []
    pt20 = []
    pt25 = []
    pt30 = []
    pt35 = []
    pt40 = []
    pt45 = []
    error = []
    st = []
    stl = []

    p1 = int(1 / 6 * maxp)
    p2 = int(2 / 6 * maxp)
    p3 = int(3 / 6 * maxp)
    p4 = int(4 / 6 * maxp)
    p5 = int(5 / 6 * maxp)
    p6 = int(6 / 6 * maxp)

    my_bar = streamlit.progress(0)
    while t <= TotalTimeLength:
        percent_complete = t / TotalTimeLength
        my_bar.progress(percent_complete)

        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate), limit=500)
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, ICU_length_of_stay_mean)
        mttemp = initial_condition * probability_still_in_system + ans
        mt.append(mttemp)
        temptotal = 0
        flag = [False, False]
        tempcdf = 0
        while tempcdf <= 0.99:
            i = 0
            if t <= 40:
                while i <= temptotal and i <= initial_condition:
                    if i <= initial_condition:
                        tempcdf = tempcdf + binom.pmf(i, initial_condition,
                                                      probability_still_in_system) * poisson.pmf(
                            (temptotal - i), ans)
                    i = i + 1
            else:
                tempcdf = poisson.cdf(temptotal, ans)
            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == p1:
                pt15.append(1 - tempcdf)
            if temptotal == p2:
                pt20.append(1 - tempcdf)
            if temptotal == p3:
                pt25.append(1 - tempcdf)
            if temptotal == p4:
                pt30.append(1 - tempcdf)
            if temptotal == p5:
                pt35.append(1 - tempcdf)
            if temptotal == p6:
                pt40.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < p1:
            pt15.append(float(0))
        if temptotal < p2:
            pt20.append(float(0))
        if temptotal < p3:
            pt25.append(float(0))
        if temptotal < p4:
            pt30.append(float(0))
        if temptotal < p5:
            pt35.append(float(0))
        if temptotal < p6:
            pt40.append(float(0))
        t = t + step

    l = len(rate)
    l1 = int(1 / 10 * l)
    l2 = int(2 / 10 * l)
    l3 = int(3 / 10 * l)
    l4 = int(4 / 10 * l)
    l5 = int(5 / 10 * l)
    l6 = int(6 / 10 * l)
    l7 = int(7 / 10 * l)
    l8 = int(8 / 10 * l)
    l9 = int(9 / 10 * l)

    data = {
        "# Patients": [p1, p2, p3, p4, p5, p6],
        str(l1) + "Days": [maxc(pt15[0:l1]), maxc(pt20[0:l1]), maxc(pt25[0:l1]), maxc(pt30[0:l1]), maxc(pt35[0:l1]),
                           maxc(pt40[0:l1])],
        str(l2) + "Days": [maxc(pt15[0:l2]), maxc(pt20[0:l2]), maxc(pt25[0:l2]), maxc(pt30[0:l2]), maxc(pt35[0:l2]),
                           maxc(pt40[0:l2])],
        str(l3) + "Days": [maxc(pt15[0:l3]), maxc(pt20[0:l3]), maxc(pt25[0:l3]), maxc(pt30[0:l3]), maxc(pt35[0:l3]),
                           maxc(pt40[0:l3])],
        str(l4) + "Days": [maxc(pt15[0:l4]), maxc(pt20[0:l4]), maxc(pt25[0:l4]), maxc(pt30[0:l4]), maxc(pt35[0:l4]),
                           maxc(pt40[0:l4])],
        str(l5) + "Days": [maxc(pt15[0:l5]), maxc(pt20[0:l5]), maxc(pt25[0:l5]), maxc(pt30[0:l5]), maxc(pt35[0:l5]),
                           maxc(pt40[0:l5])],
        str(l6) + "Days": [maxc(pt15[0:l6]), maxc(pt20[0:l6]), maxc(pt25[0:l6]), maxc(pt30[0:l6]), maxc(pt35[0:l6]),
                           maxc(pt40[0:l6])],
        str(l7) + "Days": [maxc(pt15[0:l7]), maxc(pt20[0:l7]), maxc(pt25[0:l7]), maxc(pt30[0:l7]), maxc(pt35[0:l7]),
                           maxc(pt40[0:l7])],
        str(l8) + "Days": [maxc(pt15[0:80]), maxc(pt20[0:80]), maxc(pt25[0:80]), maxc(pt30[0:80]), maxc(pt35[0:80]),
                           maxc(pt40[0:80])],
        str(l9) + "Days": [maxc(pt15[0:90]), maxc(pt20[0:90]), maxc(pt25[0:90]), maxc(pt30[0:90]), maxc(pt35[0:90]),
                           maxc(pt40[0:90])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


@streamlit.cache(suppress_st_warning=True)
def ed_run(ED_length_of_stay_mean, ED_length_of_stay_std, ED_initial_condition, Daily_arrival_rate, Hourly_pattern,
           maxp):
    mu = log(square(ED_length_of_stay_mean) / sqrt(
        square(ED_length_of_stay_mean) + square(ED_length_of_stay_mean)))
    stddev = sqrt(
        log(1 + square(ED_length_of_stay_mean) / square(ED_length_of_stay_mean)))

    ArrivalRate = []
    for j in range(len(Daily_arrival_rate)):
        for k in range(24):
            ArrivalRate.append(float(Daily_arrival_rate[j]) * float(Hourly_pattern[k]))
    ArrivalRate = array(ArrivalRate, dtype=float)
    TotalTimeLength = ArrivalRate.size
    initial_condition = ED_initial_condition

    step = 1
    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    mt = []
    mt5 = []
    mt95 = []
    pt10 = []
    pt15 = []
    pt20 = []
    pt25 = []
    pt30 = []
    pt35 = []
    pt40 = []
    error = []
    st = []
    stl = []

    p1 = int(1 / 6 * maxp)
    p2 = int(2 / 6 * maxp)
    p3 = int(3 / 6 * maxp)
    p4 = int(4 / 6 * maxp)
    p5 = int(5 / 6 * maxp)
    p6 = int(6 / 6 * maxp)
    my_bar = streamlit.progress(0)

    while t <= TotalTimeLength:
        percent_complete = t / TotalTimeLength
        my_bar.progress(percent_complete)
        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate), limit=500)
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, ED_length_of_stay_mean)
        # Calculate the mean
        mttemp = initial_condition * probability_still_in_system + ans
        mt.append(mttemp)
        # Calculate the numerical distribution:
        temptotal = 0
        flag = [False, False]
        tempcdf = 0
        while tempcdf <= 0.99:
            i = 0
            if t <= 48:
                while i <= temptotal and i <= initial_condition:
                    if i <= initial_condition:
                        tempcdf = tempcdf + binom.pmf(i, initial_condition,
                                                      probability_still_in_system) * poisson.pmf(
                            (temptotal - i), ans)
                    i = i + 1
            else:
                tempcdf = poisson.cdf(temptotal, ans)
            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == p1:
                pt10.append(1 - tempcdf)
            if temptotal == p2:
                pt15.append(1 - tempcdf)
            if temptotal == p3:
                pt20.append(1 - tempcdf)
            if temptotal == p4:
                pt25.append(1 - tempcdf)
            if temptotal == p5:
                pt30.append(1 - tempcdf)
            if temptotal == p6:
                pt35.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < p1:
            pt10.append(float(0))
        if temptotal < p2:
            pt15.append(float(0))
        if temptotal < p3:
            pt20.append(float(0))
        if temptotal < p4:
            pt25.append(float(0))
        if temptotal < p5:
            pt30.append(float(0))
        if temptotal < p6:
            pt35.append(float(0))
        t = t + step

    l = len(Daily_arrival_rate * 24)
    # print(l)
    l1 = int(1 / 10 * l)
    l2 = int(2 / 10 * l)
    l3 = int(3 / 10 * l)
    l4 = int(4 / 10 * l)
    l5 = int(5 / 10 * l)
    l6 = int(6 / 10 * l)
    l7 = int(7 / 10 * l)
    l8 = int(8 / 10 * l)
    l9 = int(9 / 10 * l)

    data = {
        "# Patients": [p1, p2, p3, p4, p5, p6],
        str(int(l1 / 24)) + "Days": [maxc(pt10[0:l1]), maxc(pt15[0:l1]), maxc(pt20[0:l1]), maxc(pt25[0:l1]),
                                     maxc(pt30[0:l1]),
                                     maxc(pt35[0:l1])],
        str(int(l2 / 24)) + "Days": [maxc(pt10[0:l2]), maxc(pt15[0:l2]), maxc(pt20[0:l2]), maxc(pt25[0:l2]),
                                     maxc(pt30[0:l2]),
                                     maxc(pt35[0:l2])],
        str(int(l3 / 24)) + "Days": [maxc(pt10[0:l3]), maxc(pt15[0:l3]), maxc(pt20[0:l3]), maxc(pt25[0:l3]),
                                     maxc(pt30[0:l3]),
                                     maxc(pt35[0:l3])],
        str(int(l4 / 24)) + "Days": [maxc(pt10[0:l4]), maxc(pt15[0:l4]), maxc(pt20[0:l4]), maxc(pt25[0:l4]),
                                     maxc(pt30[0:l4]),
                                     maxc(pt35[0:l4])],
        str(int(l5 / 24)) + "Days": [maxc(pt10[0:l5]), maxc(pt15[0:l5]), maxc(pt20[0:l5]), maxc(pt25[0:l5]),
                                     maxc(pt30[0:l5]),
                                     maxc(pt35[0:l5])],
        str(int(l6 / 24)) + "Days": [maxc(pt10[0:l6]), maxc(pt15[0:l6]), maxc(pt20[0:l6]), maxc(pt25[0:l6]),
                                     maxc(pt30[0:l6]),
                                     maxc(pt35[0:l6])],
        str(int(l7 / 24)) + "Days": [maxc(pt10[0:l7]), maxc(pt15[0:l7]), maxc(pt20[0:l7]), maxc(pt25[0:l7]),
                                     maxc(pt30[0:l7]),
                                     maxc(pt35[0:l7])],
        str(int(l8 / 24)) + "Days": [maxc(pt10[0:l8]), maxc(pt15[0:l8]), maxc(pt20[0:l8]), maxc(pt25[0:l8]),
                                     maxc(pt30[0:l8]),
                                     maxc(pt35[0:l8])],
        str(int(l9 / 24)) + "Days": [maxc(pt10[0:l9]), maxc(pt15[0:l9]), maxc(pt20[0:l9]), maxc(pt25[0:l9]),
                                     maxc(pt30[0:l9]),
                                     maxc(pt35[0:l9])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df

@streamlit.cache(suppress_st_warning=True)
def h_nor(Hospital_length_of_stay_mean, Hospital_length_of_stay_std, Hospital_initial_condition, rate,
            Percentage_hospitalized, maxp):
    mu = log(square(Hospital_length_of_stay_mean) / sqrt(
        square(Hospital_length_of_stay_mean) + square(Hospital_length_of_stay_mean)))
    stddev = sqrt(log(1 + square(Hospital_length_of_stay_mean) / square(Hospital_length_of_stay_mean)))
    ArrivalRate = array(rate, dtype=float)
    ArrivalRate = ArrivalRate * Percentage_hospitalized
    TotalTimeLength = ArrivalRate.size
    initial_condition = Hospital_initial_condition

    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    mt = []
    mt5 = []
    mt95 = []
    pt25 = []
    pt50 = []
    pt75 = []
    pt100 = []
    pt125 = []
    pt150 = []
    pt175 = []
    error = []
    st = []
    stl = []

    p1 = int(1 / 6 * maxp)
    p2 = int(2 / 6 * maxp)
    p3 = int(3 / 6 * maxp)
    p4 = int(4 / 6 * maxp)
    p5 = int(5 / 6 * maxp)
    p6 = int(6 / 6 * maxp)

    my_bar = streamlit.progress(0)
    while t <= TotalTimeLength:
        percent_complete = t / TotalTimeLength
        my_bar.progress(percent_complete)

        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate))
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, Hospital_length_of_stay_mean)
        # Calculate the mean
        mt_temp = initial_condition * probability_still_in_system + ans
        mt.append(mt_temp)

        variance = initial_condition * probability_still_in_system * (1 - probability_still_in_system) + ans

        temptotal = 0
        flag = [False, False]
        tempcdf = 0

        while tempcdf <= 0.99:
            if t <= 40:
                tempcdf = norm.cdf(temptotal, mt_temp, sqrt(variance))
            else:
                tempcdf = poisson.cdf(temptotal, ans)

            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == p1:
                pt25.append(1 - tempcdf)
            if temptotal == p2:
                pt50.append(1 - tempcdf)
            if temptotal == p3:
                pt75.append(1 - tempcdf)
            if temptotal == p4:
                pt100.append(1 - tempcdf)
            if temptotal == p5:
                pt125.append(1 - tempcdf)
            if temptotal == p6:
                pt150.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < p1:
            pt25.append(float(0))
        if temptotal < p2:
            pt50.append(float(0))
        if temptotal < p3:
            pt75.append(float(0))
        if temptotal < p4:
            pt100.append(float(0))
        if temptotal < p5:
            pt125.append(float(0))
        if temptotal < p6:
            pt150.append(float(0))
        t = t + 1

    l = len(rate)
    l1 = int(1 / 10 * l)
    l2 = int(2 / 10 * l)
    l3 = int(3 / 10 * l)
    l4 = int(4 / 10 * l)
    l5 = int(5 / 10 * l)
    l6 = int(6 / 10 * l)
    l7 = int(7 / 10 * l)
    l8 = int(8 / 10 * l)
    l9 = int(9 / 10 * l)

    data = {
        "# Patients": [p1, p2, p3, p4, p5, p6],
        str(l1) + "Days": [maxc(pt25[0:l1]), maxc(pt50[0:l1]), maxc(pt75[0:l1]), maxc(pt100[0:l1]), maxc(pt125[0:l1]),
                           maxc(pt150[0:l1])],
        str(l2) + "Days": [maxc(pt25[0:l2]), maxc(pt50[0:l2]), maxc(pt75[0:l2]), maxc(pt100[0:l2]), maxc(pt125[0:l2]),
                           maxc(pt150[0:l2])],
        str(l3) + "Days": [maxc(pt25[0:l3]), maxc(pt50[0:l3]), maxc(pt75[0:l3]), maxc(pt100[0:l3]), maxc(pt125[0:l3]),
                           maxc(pt150[0:l3])],
        str(l4) + "Days": [maxc(pt25[0:l4]), maxc(pt50[0:l4]), maxc(pt75[0:l4]), maxc(pt100[0:l4]), maxc(pt125[0:l4]),
                           maxc(pt150[0:l4])],
        str(l5) + "Days": [maxc(pt25[0:l5]), maxc(pt50[0:l5]), maxc(pt75[0:l5]), maxc(pt100[0:l5]), maxc(pt125[0:l5]),
                           maxc(pt150[0:l5])],
        str(l6) + "Days": [maxc(pt25[0:l6]), maxc(pt50[0:l6]), maxc(pt75[0:l6]), maxc(pt100[0:l6]), maxc(pt125[0:l6]),
                           maxc(pt150[0:l6])],
        str(l7) + "Days": [maxc(pt25[0:l7]), maxc(pt50[0:l7]), maxc(pt75[0:l7]), maxc(pt100[0:l7]), maxc(pt125[0:l7]),
                           maxc(pt150[0:l7])],
        str(l8) + "Days": [maxc(pt25[0:l8]), maxc(pt50[0:l8]), maxc(pt75[0:l8]), maxc(pt100[0:l8]), maxc(pt125[0:l8]),
                           maxc(pt150[0:l8])],
        str(l9) + "Days": [maxc(pt25[0:l9]), maxc(pt50[0:l9]), maxc(pt75[0:l9]), maxc(pt100[0:l9]), maxc(pt125[0:l9]),
                           maxc(pt150[0:l9])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


@streamlit.cache(suppress_st_warning=True)
def icu_nor(ICU_length_of_stay_mean, ICU_length_of_stay_std, ICU_initial_condition, rate, Percentage_icu, maxp):
    mu = log(square(ICU_length_of_stay_mean) / sqrt(
        square(ICU_length_of_stay_mean) + square(ICU_length_of_stay_mean)))
    stddev = sqrt(
        log(1 + square(ICU_length_of_stay_mean) / square(ICU_length_of_stay_mean)))
    ArrivalRate = array(rate, dtype=float)
    ArrivalRate = ArrivalRate * Percentage_icu
    TotalTimeLength = ArrivalRate.size
    initial_condition = ICU_initial_condition

    step = 1
    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    zeros = [0 for i in tlist]
    mt = []
    mt5 = []
    mt95 = []
    pt15 = []
    pt20 = []
    pt25 = []
    pt30 = []
    pt35 = []
    pt40 = []
    pt45 = []
    error = []
    st = []
    stl = []

    p1 = int(1 / 6 * maxp)
    p2 = int(2 / 6 * maxp)
    p3 = int(3 / 6 * maxp)
    p4 = int(4 / 6 * maxp)
    p5 = int(5 / 6 * maxp)
    p6 = int(6 / 6 * maxp)

    my_bar = streamlit.progress(0)
    while t <= TotalTimeLength:
        percent_complete = t / TotalTimeLength
        my_bar.progress(percent_complete)

        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate), limit=500)
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, ICU_length_of_stay_mean)
        mttemp = initial_condition * probability_still_in_system + ans
        mt.append(mttemp)
        variance = initial_condition * probability_still_in_system * (1 - probability_still_in_system) + ans

        temptotal = 0
        flag = [False, False]
        tempcdf = 0
        while tempcdf <= 0.99:
            if t <= 40:
                tempcdf = norm.cdf(temptotal, mttemp, sqrt(variance))
            else:
                tempcdf = poisson.cdf(temptotal, ans)

            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == p1:
                pt15.append(1 - tempcdf)
            if temptotal == p2:
                pt20.append(1 - tempcdf)
            if temptotal == p3:
                pt25.append(1 - tempcdf)
            if temptotal == p4:
                pt30.append(1 - tempcdf)
            if temptotal == p5:
                pt35.append(1 - tempcdf)
            if temptotal == p6:
                pt40.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < p1:
            pt15.append(float(0))
        if temptotal < p2:
            pt20.append(float(0))
        if temptotal < p3:
            pt25.append(float(0))
        if temptotal < p4:
            pt30.append(float(0))
        if temptotal < p5:
            pt35.append(float(0))
        if temptotal < p6:
            pt40.append(float(0))
        t = t + step

    l = len(rate)
    l1 = int(1 / 10 * l)
    l2 = int(2 / 10 * l)
    l3 = int(3 / 10 * l)
    l4 = int(4 / 10 * l)
    l5 = int(5 / 10 * l)
    l6 = int(6 / 10 * l)
    l7 = int(7 / 10 * l)
    l8 = int(8 / 10 * l)
    l9 = int(9 / 10 * l)

    data = {
        "# Patients": [p1, p2, p3, p4, p5, p6],
        str(l1) + "Days": [maxc(pt15[0:l1]), maxc(pt20[0:l1]), maxc(pt25[0:l1]), maxc(pt30[0:l1]), maxc(pt35[0:l1]),
                           maxc(pt40[0:l1])],
        str(l2) + "Days": [maxc(pt15[0:l2]), maxc(pt20[0:l2]), maxc(pt25[0:l2]), maxc(pt30[0:l2]), maxc(pt35[0:l2]),
                           maxc(pt40[0:l2])],
        str(l3) + "Days": [maxc(pt15[0:l3]), maxc(pt20[0:l3]), maxc(pt25[0:l3]), maxc(pt30[0:l3]), maxc(pt35[0:l3]),
                           maxc(pt40[0:l3])],
        str(l4) + "Days": [maxc(pt15[0:l4]), maxc(pt20[0:l4]), maxc(pt25[0:l4]), maxc(pt30[0:l4]), maxc(pt35[0:l4]),
                           maxc(pt40[0:l4])],
        str(l5) + "Days": [maxc(pt15[0:l5]), maxc(pt20[0:l5]), maxc(pt25[0:l5]), maxc(pt30[0:l5]), maxc(pt35[0:l5]),
                           maxc(pt40[0:l5])],
        str(l6) + "Days": [maxc(pt15[0:l6]), maxc(pt20[0:l6]), maxc(pt25[0:l6]), maxc(pt30[0:l6]), maxc(pt35[0:l6]),
                           maxc(pt40[0:l6])],
        str(l7) + "Days": [maxc(pt15[0:l7]), maxc(pt20[0:l7]), maxc(pt25[0:l7]), maxc(pt30[0:l7]), maxc(pt35[0:l7]),
                           maxc(pt40[0:l7])],
        str(l8) + "Days": [maxc(pt15[0:80]), maxc(pt20[0:80]), maxc(pt25[0:80]), maxc(pt30[0:80]), maxc(pt35[0:80]),
                           maxc(pt40[0:80])],
        str(l9) + "Days": [maxc(pt15[0:90]), maxc(pt20[0:90]), maxc(pt25[0:90]), maxc(pt30[0:90]), maxc(pt35[0:90]),
                           maxc(pt40[0:90])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


@streamlit.cache(suppress_st_warning=True)
def ed_nor(ED_length_of_stay_mean, ED_length_of_stay_std, ED_initial_condition, Daily_arrival_rate, Hourly_pattern,
           maxp):
    mu = log(square(ED_length_of_stay_mean) / sqrt(
        square(ED_length_of_stay_mean) + square(ED_length_of_stay_mean)))
    stddev = sqrt(
        log(1 + square(ED_length_of_stay_mean) / square(ED_length_of_stay_mean)))

    ArrivalRate = []
    for j in range(len(Daily_arrival_rate)):
        for k in range(24):
            ArrivalRate.append(float(Daily_arrival_rate[j]) * float(Hourly_pattern[k]))
    ArrivalRate = array(ArrivalRate, dtype=float)
    TotalTimeLength = ArrivalRate.size
    initial_condition = ED_initial_condition

    step = 1
    t = 1
    tlist = []
    tlist = range(1, TotalTimeLength + 1)
    mt = []
    mt5 = []
    mt95 = []
    pt10 = []
    pt15 = []
    pt20 = []
    pt25 = []
    pt30 = []
    pt35 = []
    pt40 = []
    error = []
    st = []
    stl = []

    p1 = int(1 / 6 * maxp)
    p2 = int(2 / 6 * maxp)
    p3 = int(3 / 6 * maxp)
    p4 = int(4 / 6 * maxp)
    p5 = int(5 / 6 * maxp)
    p6 = int(6 / 6 * maxp)
    my_bar = streamlit.progress(0)

    while t <= TotalTimeLength:
        percent_complete = t / TotalTimeLength
        my_bar.progress(percent_complete)
        ans, err = quad(f, 0, t, args=(t, mu, stddev, ArrivalRate), limit=500)
        total_probability = 0
        probability_still_in_system = 1 - rs(t, mu, stddev, ED_length_of_stay_mean)
        # Calculate the mean
        mttemp = initial_condition * probability_still_in_system + ans
        mt.append(mttemp)
        variance = initial_condition * probability_still_in_system * (1 - probability_still_in_system) + ans
        # Calculate the numerical distribution:
        temptotal = 0
        flag = [False, False]
        tempcdf = 0
        while tempcdf <= 0.99:
            if t <= 48:
                tempcdf = norm.cdf(temptotal, mttemp, sqrt(variance))
            else:
                tempcdf = poisson.cdf(temptotal, ans)

            if tempcdf >= 0.05 and flag[0] == False:
                if temptotal - 1 > 0:
                    tempq = temptotal - 1
                else:
                    tempq = 0
                mt5.append(tempq)
                flag[0] = True
            if tempcdf >= 0.95 and flag[1] == False:
                mt95.append(temptotal)
                flag[1] = True
            if temptotal == p1:
                pt10.append(1 - tempcdf)
            if temptotal == p2:
                pt15.append(1 - tempcdf)
            if temptotal == p3:
                pt20.append(1 - tempcdf)
            if temptotal == p4:
                pt25.append(1 - tempcdf)
            if temptotal == p5:
                pt30.append(1 - tempcdf)
            if temptotal == p6:
                pt35.append(1 - tempcdf)
            temptotal = temptotal + 1
        temptotal = temptotal - 1
        if temptotal < p1:
            pt10.append(float(0))
        if temptotal < p2:
            pt15.append(float(0))
        if temptotal < p3:
            pt20.append(float(0))
        if temptotal < p4:
            pt25.append(float(0))
        if temptotal < p5:
            pt30.append(float(0))
        if temptotal < p6:
            pt35.append(float(0))
        t = t + step

    l = len(Daily_arrival_rate * 24)
    # print(l)
    l1 = int(1 / 10 * l)
    l2 = int(2 / 10 * l)
    l3 = int(3 / 10 * l)
    l4 = int(4 / 10 * l)
    l5 = int(5 / 10 * l)
    l6 = int(6 / 10 * l)
    l7 = int(7 / 10 * l)
    l8 = int(8 / 10 * l)
    l9 = int(9 / 10 * l)

    data = {
        "# Patients": [p1, p2, p3, p4, p5, p6],
        str(int(l1 / 24)) + "Days": [maxc(pt10[0:l1]), maxc(pt15[0:l1]), maxc(pt20[0:l1]), maxc(pt25[0:l1]),
                                     maxc(pt30[0:l1]),
                                     maxc(pt35[0:l1])],
        str(int(l2 / 24)) + "Days": [maxc(pt10[0:l2]), maxc(pt15[0:l2]), maxc(pt20[0:l2]), maxc(pt25[0:l2]),
                                     maxc(pt30[0:l2]),
                                     maxc(pt35[0:l2])],
        str(int(l3 / 24)) + "Days": [maxc(pt10[0:l3]), maxc(pt15[0:l3]), maxc(pt20[0:l3]), maxc(pt25[0:l3]),
                                     maxc(pt30[0:l3]),
                                     maxc(pt35[0:l3])],
        str(int(l4 / 24)) + "Days": [maxc(pt10[0:l4]), maxc(pt15[0:l4]), maxc(pt20[0:l4]), maxc(pt25[0:l4]),
                                     maxc(pt30[0:l4]),
                                     maxc(pt35[0:l4])],
        str(int(l5 / 24)) + "Days": [maxc(pt10[0:l5]), maxc(pt15[0:l5]), maxc(pt20[0:l5]), maxc(pt25[0:l5]),
                                     maxc(pt30[0:l5]),
                                     maxc(pt35[0:l5])],
        str(int(l6 / 24)) + "Days": [maxc(pt10[0:l6]), maxc(pt15[0:l6]), maxc(pt20[0:l6]), maxc(pt25[0:l6]),
                                     maxc(pt30[0:l6]),
                                     maxc(pt35[0:l6])],
        str(int(l7 / 24)) + "Days": [maxc(pt10[0:l7]), maxc(pt15[0:l7]), maxc(pt20[0:l7]), maxc(pt25[0:l7]),
                                     maxc(pt30[0:l7]),
                                     maxc(pt35[0:l7])],
        str(int(l8 / 24)) + "Days": [maxc(pt10[0:l8]), maxc(pt15[0:l8]), maxc(pt20[0:l8]), maxc(pt25[0:l8]),
                                     maxc(pt30[0:l8]),
                                     maxc(pt35[0:l8])],
        str(int(l9 / 24)) + "Days": [maxc(pt10[0:l9]), maxc(pt15[0:l9]), maxc(pt20[0:l9]), maxc(pt25[0:l9]),
                                     maxc(pt30[0:l9]),
                                     maxc(pt35[0:l9])]
    }

    df = pd.DataFrame(data)
    return tlist, mt, mt5, mt95, df


