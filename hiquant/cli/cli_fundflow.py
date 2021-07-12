# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import datetime as dt
import pandas as pd
import tabulate as tb
import matplotlib.pyplot as plt

from ..core import get_cn_stock_fund_flow_rank, get_stock_fund_flow_daily, get_all_symbol_name, get_daily

def cli_fundflow_rank(symbols, options):
    df = get_cn_stock_fund_flow_rank()
    df = df[ df['symbol'].isin(symbols) ]
    df = df[ (df['main_pct'] > 3) | (df['main_pct'] < -3) ]
    df = df.sort_values(by='main_pct', ascending=False).reset_index(drop=True)
    df = df.drop(columns=['medium_pct', 'small_pct'])
    print( tb.tabulate(df, headers='keys', tablefmt='psql') )

def trim_axs(axs, N):
    """
    Reduce *axs* to *N* Axes. All further Axes are removed from the figure.
    """
    axs = axs.flat
    for ax in axs[N:]:
        ax.remove()
    return axs[:N]

def cli_fundflow_view(symbols, options):
    df = get_cn_stock_fund_flow_rank()
    df = df[ df['symbol'].isin(symbols) ]
    df = df.sort_values(by='main_pct', ascending=False).reset_index(drop=True)
    symbols = df.symbol.tolist()
    all_symbol_name = get_all_symbol_name()

    plt.rcParams['font.sans-serif'] = ['SimHei'] # Chinese font
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams["axes.unicode_minus"] = False

    figsize = (20, 8)
    cols = 10
    rows = len(symbols) // cols + 1
    axs = plt.figure(figsize=figsize, constrained_layout=True).subplots(rows, cols)
    axs = trim_axs(axs, len(symbols))
    for ax, symbol in zip(axs, symbols):
        ax.set_title(symbol + ' - ' + all_symbol_name[symbol])

        df = get_stock_fund_flow_daily(symbol)
        fundflow = 'main_pct' if ('-pct' in options) else 'main_fund'
        data = df[ fundflow ].tail(20)
        color = ['r' if v >= 0 else 'g' for v in data]
        ax.bar(data.index, data, color=color)

        max_y = max(data)
        min_y = min(data)

        df = get_daily(symbol).tail(20)
        data = df['close']
        max_data = max(data)
        min_data = min(data)
        data = (data - min_data) / (max_data - min_data) * (max_y - min_y) + min_y
        ax.plot(data.index, data, color='black', linewidth=1)

        ax.set_xticks([])

    plt.show()

def cli_fundflow(params, options):
    syntax_tips = '''Syntax:
    __argv0__ fundflow <action> <symbols | symbols.csv>

Actioin:
    rank ............................. rank the main fund flow
    view ............................. view & plot history fund flow of symbols

Options:
    -pct ............................. plot main fundflow percertage data
    -fund ............................ by default, plot main fundflow fund data

Example:
    __argv0__ fundflow 600036 000002 600276
    __argv0__ fundflow stockpool/realtime_trade.csv -pct

'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    action = params[0]
    params = params[1:]

    if action not in ['rank', 'view']:
        print('\nError: invalid action: ', action)
        return

    if params[0].endswith('.csv'):
        stock_df = pd.read_csv(params[0], dtype=str)
        symbols = stock_df['symbol'].tolist()
    else:
        symbols = params

    if action == 'rank':
        cli_fundflow_rank(symbols, options)
    elif action == 'view':
        cli_fundflow_view(symbols, options)
    