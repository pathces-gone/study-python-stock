import pandas as pd
import pandas_datareader.data as web

from StockPrice import StockPrice



class Backtesting():
    def __init__(self):
        def get_prices(item='삼성전자', page=5):
            item = StockPrice(item_name=item, page=page)
            prices=item.get_price(False)
            prices.set_index(prices.columns[0], inplace=True)
            return prices
        self.prices = get_prices(item='삼성전자',page=5)

    def trade(self,
            capital:int=10_000_000, 
            symbol_trade:str='Close', 
            symbol_benchmark='Close'):
        """
            prices: 종목시세
            symbol_trade: 트레이드할 
        """
        prices = self.prices

        # Init
        df_init   = (prices[symbol_trade]*0).to_frame().assign(cash = 0)
        df_update = (prices[symbol_trade]*0).to_frame().assign(cash = 0)
        df_end    = (prices[symbol_trade]*0).to_frame().assign(cash = 0)
        df_init.iloc[0, df_init.columns.get_loc('cash')] = capital
        df_end.iloc[0, df_end.columns.get_loc('cash')]   = capital
        calendar = pd.Series(prices.index).iloc[1:]



        for date in calendar:
            prev_date = df_init.index[df_init.index<date][-1]
            df_init.loc[date, :] = df_end.loc[prev_date, :]


            a = df_init.loc[date, symbol_trade]
            b = prices.loc[date, symbol_trade]
            print(a)
            print(b)


            port_value = df_init.loc[date, symbol_trade] * prices.loc[date, symbol_trade] + df_init.loc[date, 'cash']
            #print(port_value)
            
            #print()
            #if prices.loc[date == '2021-12-30']:


            df_end.loc[date, symbol_trade] = port_value/prices.loc[date, symbol_trade]
            df_end.loc[date, 'cash'] = 0
            df_update.loc[date] = df_end.loc[date] - df_init.loc[date]
            
            '''
            if prices.loc[date, symbol_volatility] > volatility_threshold: # volatility is high -> be fully in cash
                df_end.loc[date, symbol_trade] = 0
                df_end.loc[date, 'cash']       = port_value
            else: # volatility is low -> be in market position
                df_end.loc[date, symbol_trade] = port_value/prices.loc[date, symbol_trade]
                df_end.loc[date, 'cash'] = 0
            df_update.loc[date] = df_end.loc[date] - df_init.loc[date]
            '''

        portval = (df_end*prices.assign(cash = 1)[[symbol_trade, 'cash']]).sum(axis = 1).to_frame().rename(columns = {0:'strategy'})
        portval['benchmark'] = prices[symbol_benchmark]
        portval = portval/portval.iloc[0].values
        return portval
        

if __name__ == '__main__':
    res = Backtesting().trade()
    #print(res)
    #res = backtest_strategy(prices = prices, symbol_trade = 'SPY', symbol_volatility = '^VIX', volatility_threshold = 20, capital = 10000, symbol_benchmark = '^GSPC')
    #res.plot()