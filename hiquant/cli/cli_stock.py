# -*- coding: utf-8; py-indent-offset:4 -*-

import os
import sys
import tabulate as tb

from ..utils import date_from_str, symbol_normalize
from ..core import symbol_to_name
from ..core import list_signal_indicators, get_all_stock_list_df, get_order_cost
from ..core import Market, Stock

def cli_stock(params, options):
    syntax_tips = '''Syntax:
    __argv0__ stock list [update]
    __argv0__ stock <symbol> [<from_date>] [<to_date>] [<options>]

<symbol> ....................... stock symbol, like 600036
<from_date> .................... default from 3 year ago
<to_date> ...................... default to yesterday

<options> ...................... options to plot the stock
    -ma, -macd, -kdj, etc. ..... add some indicators
    -all ....................... add all indicators
    -mix ....................... show trade result if mix trade signal of the indicators
    -top5 ...................... show only top 5 indicators according to result

Example:
    __argv0__ stock 600036 -ma
    __argv0__ stock 600036 20180101 -ma -macd -kdj
    __argv0__ stock 600036 20180101 20210101 -ma -macd -kdj
    __argv0__ stock 600036 -ma -macd -mix
'''.replace('__argv0__',os.path.basename(sys.argv[0]))

    if (len(params) == 0) or (params[0] == 'help'):
        print( syntax_tips )
        return

    if params[0] == 'list':
        df = get_all_stock_list_df()
        print( tb.tabulate(df, headers='keys', showindex=False, tablefmt='psql') )
        print( 'Totally', df.shape[0], 'rows.\n')
        return

    symbol = symbol_normalize(params[0])
    name = symbol_to_name(symbol)

    date_start = date_from_str(params[1] if len(params) > 1 else '3 years ago')
    date_end = date_from_str(params[2] if len(params) > 2 else 'yesterday')

    market = Market(date_start, date_end, adjust='qfq')
    df = market.get_daily(symbol, start = date_start, end = date_end)
    stock = Stock(symbol, name, df)

    all_indicators = list_signal_indicators()

    indicators = []
    topN = 5
    inplace = True
    out_file = None
    for option in options:
        if option.startswith('-top'):
            topN = int(option.replace('-top',''))
        elif option.startswith('-out=') and (option.endswith('.png') or option.endswith('.jpg')):
            out_file = option.replace('-out=', '')
        else:
            k = option.replace('-','')
            if (k in all_indicators) and (not k in indicators):
                indicators.append(k)
    if '-all' in options:
        indicators = all_indicators
        inplace = False

    mix = '-mix' in options

    # add indicators and calculate performance
    stock.add_indicator(indicators, mix=mix, inplace= inplace, order_cost = get_order_cost())

    rank_df = stock.rank_indicator(by = 'final')
    if rank_df.shape[0] > 0:
        print(rank_df)

    # find top indicators
    ranked_indicators = rank_df['indicator'].tolist()
    other_indicators = ranked_indicators[topN:]
    df.drop(columns = other_indicators, inplace=True)

    stock.plot(out_file= out_file)
