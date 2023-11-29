import os
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

from pynput import keyboard
from utils.Utils import Utils

symbol = 'RB'
mode = 'short'  # 'long' | 'short' | 'both'

plt.rcParams["figure.dpi"] = 140

if __name__ == '__main__':
    res_dir_path = 'Research/dev/filtered_times_results'
    Utils.system.safe_dir_access(res_dir_path)
    res_file_name = f'{symbol}_{mode}_filtered_time_sections.csv'
    res_file_path = os.path.join(res_dir_path, res_file_name)
    res_file_exists = os.path.exists(Utils.system.add_abs_path(res_file_path))

    data_files = Utils.system.get_data_files(os.path.join(Utils.data.ADJ_DATA_PATH, symbol))
    data_start_date = Utils.system.read_ftr_df(data_files[0]).index[0].date()
    data_end_date = Utils.system.read_ftr_df(data_files[-1]).index[0].date()
    if res_file_exists:
        res = pd.read_csv(Utils.system.add_abs_path(res_file_path), index_col=0)
        res.date = pd.to_datetime(res.date.apply(lambda t: t if ' 00:00:00' in t else t + ' 00:00:00'),
                                  # format='%d-%m-%Y %H:%M:%S')
                                  format='%Y-%m-%d %H:%M:%S')
        chosen_times_last_date = res.date.iloc[-1].date()
    else:
        res = pd.DataFrame(columns=['date', 'num', 'start', 'end'])
        chosen_times_last_date = None

    print()
    print(f'start date: {data_start_date}')
    print(f'last inserted date: {chosen_times_last_date}')
    print(f'end date: {data_end_date}')
    print()
    start_date = Utils.datetime.date_from_str(
        Utils.system.get_user_input('insert the wanted date to start from (yyyymmdd): '))

    for file in data_files:
        date = Utils.datetime.date_from_str(Utils.datetime.find_date(file)[0])
        daily_data = Utils.system.read_ftr_df(file)

        if date < start_date:
            continue

        daily_data[Utils.data.PRICE_COLS].plot(lw=0.3, figsize=(12, 6))
        plt.title(date)
        plt.grid(True)
        # add vertical lines every 15 minutes
        for i in range(1, 24 * 4):
            plt.axvline(x=dt.datetime(date.year, date.month, date.day, i // 4, (i % 4) * 15), color='k', lw=0.1)
        plt.show()

        counter = 1
        inputs = []
        while True:
            prompt = f'insert the {Utils.prints.ordinal(counter)} <SECTION> time'
            start_time = Utils.datetime.get_datetime_inp(prompt.replace('<SECTION>', 'start'), date=False,
                                                         time=True, minutes=True)
            if start_time is None:
                break
            if inputs and start_time < inputs[-1][1]:
                Utils.prints.color_print('invalid start time', color=Utils.prints.Color.Red)
                continue

            end_time = Utils.datetime.get_datetime_inp(prompt.replace('<SECTION>', 'end'), date=False, time=True,
                                                       minutes=True)

            if end_time < start_time:
                Utils.prints.color_print('invalid input pair', color=Utils.prints.Color.Red)
                continue
            inputs.append((start_time, end_time))
            res.loc[res.shape[0]] = [date, counter, start_time, end_time]
            counter += 1

        Utils.prints.color_print(f'saving {date}...', color=Utils.prints.Color.Green)
        res.to_csv(Utils.system.add_abs_path(res_file_path))
