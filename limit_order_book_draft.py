#!/usr/bin/env python
# coding: utf-8

################################################ Overall Structure ################################################

# In[ ]:


from events import Events


class Exchange(Events):
    __events__ = "on_order_added", "on_order_removed", "on_best_price_changed"

    def add_order(self, stock_code):
        # addOrdderStuff
        best_price_changed = False
        # Figoure out best price changed or not

        self.on_order_added({'order_id': '1234', 'stock_code': stock_code})
        if best_price_changed:
            self.on_best_price_changed(stock_code, 10)

        return 0

    def remove_order(self, order_id):
        best_price_changed = False
        # remove the order
        # figure out best price changed

        self.on_order_removed(order_id)
        if best_price_changed:
            self.on_best_price_changed({'stock_code': 'AAPL', 'price': 5})

        return 0


################################################ add_order method ################################################

# In[ ]:


test={'AAPL':{'BID':{1:{'Price':1000,'Volume':900},2:{'Price':2000,'Volume':800},3:{'Price':500,'Volume':700}},
             'ASK':{4:{'Price':1000,'Volume':900},5:{'Price':2000,'Volume':800},6:{'Price':500,'Volume':700}}},
      'MSFT':{'BID':{7:{'Price':1000,'Volume':900},8:{'Price':2000,'Volume':800},9:{'Price':500,'Volume':700}},
             'ASK':{10:{'Price':1000,'Volume':900},11:{'Price':2000,'Volume':800},12:{'Price':500,'Volume':700}}}
     }
# the 1,2,3..etc are the orderIDs
ticker_map={}

def add_order(stock_code, buySell, volume, price, userReference):
###########how to make buySell enum?

    best_price_changed = False
#   want orderID a class variable
    orderID = 12
    
    if buySell == 1:
        # higher bid price
        if price > sorted(test[stock_code]['BID'].values(),key=lambda x: x['Price'],reverse=True)[0]['Price']:
            orderID += 1
            test[stock_code]['BID'][orderID]={'Price': price,'Volume': volume, 'userReference': userReference}
            ticker_map[orderID]=[stock_code,'BID']
###########do we need to sort the book? as we are only displaying top of the book. I don't think so######
    #         test['AAPL']['BID'].sort(key=lambda x: x['Price'])
            best_price_changed=True
            print('best price changed case 1')

############do we need to display the top of the book differently? as there's one price and two volumes
        # same best price, add in volume    
        elif price == sorted(test[stock_code]['BID'].values(),key=lambda x: x['Price'],reverse=True)[0]['Price']:
            orderID += 1
            test[stock_code]['BID'][orderID]={'Price': price,'Volume': volume, 'userReference': userReference}
            ticker_map[orderID]=[stock_code,'BID']
            best_price_changed=True
            print('best price changed case 2')

        else:
            orderID += 1
            test[stock_code]['BID'][orderID]={'Price': price,'Volume': volume, 'userReference': userReference}
            ticker_map[orderID]=[stock_code,'BID']
        
 
    elif buySell == 2:
        # lower ask price
        if price < sorted(test[stock_code]['ASK'].values(),key=lambda x: x['Price'],reverse=False)[0]['Price'] and price != 0:
            orderID += 1
            test[stock_code]['ASK'][orderID]={'Price': price,'Volume': volume, 'userReference': userReference}
            ticker_map[orderID]=[stock_code,'ASK']
            best_price_changed=True
            print('best price changed case 3')

        # same best price, add in volume    
        elif price == sorted(test[stock_code]['ASK'].values(),key=lambda x: x['Price'],reverse=False)[0]['Price'] and price != 0:
            orderID += 1
            test[stock_code]['ASK'][orderID]={'Price': price,'Volume': volume, 'userReference': userReference}
            ticker_map[orderID]=[stock_code,'ASK']
            best_price_changed=True
            print('best price changed case 4')

        else:
            orderID += 1
            test[stock_code]['ASK'][orderID]={'Price': price,'Volume': volume, 'userReference': userReference}
            ticker_map[orderID]=[stock_code,'ASK']
        
    else:
        print('do i need to raise buySell error code here?')
    

    
#     # Figoure out best price changed or not

#     self.on_order_added({'order_id': 1234, 'stock_code': 'AAPL'})
    
#     if best_price_changed:
#         self.on_best_price_changed(stock_code, 10)

#     return 0



add_order('AAPL', 2, 500, 500, 'xxbbjhjd')
test
ticker_map


################################################ remove_order method ################################################

# In[ ]:


test={'AAPL':{'BID':{1:{'Price':1000,'Volume':900},2:{'Price':2000,'Volume':800},3:{'Price':500,'Volume':700}},
             'ASK':{4:{'Price':1000,'Volume':900},5:{'Price':2000,'Volume':800},6:{'Price':500,'Volume':700}}},
      'MSFT':{'BID':{7:{'Price':1000,'Volume':900},8:{'Price':2000,'Volume':800},9:{'Price':500,'Volume':700}},
             'ASK':{10:{'Price':1000,'Volume':900},11:{'Price':2000,'Volume':800},12:{'Price':500,'Volume':700}}}
     }


ticker_map={2:['AAPL','BID']}

order_id=2

def remove_order(self, order_id):
    best_price_changed = False
    # remove the order
    ##########this is very complicated way of displaying the price
    price=test[ticker_map[order_id][0]][ticker_map[order_id][1]][order_id]['Price']

    if ticker_map[order_id][1]=='BID' and price == sorted(test[ticker_map[order_id][0]][ticker_map[order_id][1]].values(),key=lambda x: x['Price'],reverse=True)[0]['Price']:
        test[ticker_map[order_id][0]][ticker_map[order_id][1]].pop(order_id)
        best_price_changed=True
        print('best price changed')

    if ticker_map[order_id][1]=='ASK' and price == sorted(test[ticker_map[order_id][0]][ticker_map[order_id][1]].values(),key=lambda x: x['Price'],reverse=False)[0]['Price']:
        test[ticker_map[order_id][0]][ticker_map[order_id][1]].pop(order_id)
        best_price_changed=True
        print('best price changed')
        
    else:
        test[ticker_map[order_id][0]][ticker_map[order_id][1]].pop(order_id)
        
    ############else: errors??
    
    # figure out best price changed

    self.on_order_removed(order_id)
    if best_price_changed:
        self.on_best_price_changed({'stock_code': 'AAPL', 'price': 5})

    return 0

