
import calendar as cal
import fire
import datetime as dt
import pandas as pd
from typing import List
import numpy as np

BILLS_FILEPATH = "monthly_bills.csv"

PAYCHECK_STARTDATE = dt.date(2023, 9, 1)
TWO_WEEKS = dt.timedelta(days=14)
ONE_DAY = dt.timedelta(days=1)

PAYCHECK_VALUE = 2581

end_of_month = lambda date: dt.date(date.year, date.month, cal.monthrange(date.year, date.month)[1])

def get_paychecks(start_date: dt.date, end_date:dt.date) -> List[dt.date]:
    """Get the dates of all paychecks within a time period.

    Args:
        start_date (dt.date): inclusive
        end_date (dt.date): inclusive

    Returns:
        List[dt.date]: the dates of paychecks within the time period
    """
    pc_date = PAYCHECK_STARTDATE

    paycheck_dates:List[dt.date] = []
    # loop through ALL dates from then till now
    while pc_date <= end_date:
        if pc_date >= start_date:
            paycheck_dates.append(pc_date)

        pc_date += TWO_WEEKS

    return paycheck_dates


def health_check(today: dt.date=dt.date.today()):

    # load the csv file
    m_bills_df = pd.read_csv(BILLS_FILEPATH)
    # remove empty rows
    remove_condition = m_bills_df["Amount"].notnull()
    m_bills_df = m_bills_df[remove_condition]

    # Get past paychecks this month
    past_paychecks: List[dt.date] = get_paychecks(dt.date(today.year, today.month, 1),
                                                  today)

    # Remove bills up to first_paycheck ---------------------------------------
    past_bills = 0
    if past_paychecks:
        remove_condition = m_bills_df["Day-recurring"] > past_paychecks[0]
        past_bills_df = m_bills_df[remove_condition]

        # Get paid bills in this pay period -----------------------------------
        past_condition = past_bills_df["Day-recurring"] <= today.day

        for _, row in past_bills_df[past_condition].iterrows():
            past_bills += row["Amount"]

    # Get incoming bills before next pay check --------------------------------
    next_paycheck:dt.date = get_paychecks(today + ONE_DAY , today + TWO_WEEKS)[0]
    not_past_condition = m_bills_df["Day-recurring"] > today.day
    not_future_condition = m_bills_df["Day-recurring"] < next_paycheck.day

    imminent_bills_df = m_bills_df[not_past_condition]
    imminent_bills_df = imminent_bills_df[not_future_condition]

    imminent_bills = 0
    for _, row in imminent_bills_df.iterrows():
        imminent_bills += row["Amount"]

    # Get incoming bills after next pay check --------------------------------
    future_condition = m_bills_df["Day-recurring"] >= next_paycheck.day
    future_bills = 0
    for _, row in m_bills_df[future_condition].iterrows():
        future_bills += row["Amount"]

    ## incoming bills can include some of next month
    if next_paycheck > end_of_month(today):
        extra_condition = m_bills_df["Day-recurring"] < next_paycheck.day
        for _, row in m_bills_df[extra_condition].iterrows():
            future_bills += row["Amount"]

    # The leftovers -----------------------------------------------------------
    leftover_condition = m_bills_df["Day-recurring"].isnull()

    leftover_bills = 0
    for _, row in m_bills_df[leftover_condition].iterrows():
        leftover_bills += row["Amount"]


    # Make sense of it all ----------------------------------------------------
    # Get paycheck values
    past_money: int = PAYCHECK_VALUE * len(past_paychecks)
    future_money = PAYCHECK_VALUE * len(get_paychecks(today + ONE_DAY,
                                                      end_of_month(today)))
    # Calculate bills paid
    current_balance = past_money - past_bills
    # Calculate paychecks - bills
    incoming_balance = future_money - future_bills

    print(f'Bills paid: {past_bills}')
    print(f'You should have this much money: {current_balance}')
    print(f'Minimum for Imminent Bills: {imminent_bills}')
    print(f'Usable incoming money: {incoming_balance}')
    print(f'Living expenses: {leftover_bills}')





if __name__ == '__main__':
    fire.Fire(health_check)