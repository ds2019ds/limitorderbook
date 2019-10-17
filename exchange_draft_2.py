from enum import IntEnum

from events import Events
from sortedcontainers import SortedDict


class ExchangeErrorCodes(IntEnum):
    NO_ERROR = 0
    INVALID_STOCK_CODE = -1
    INVALID_BUY_SELL = -2
    INVALID_VOLUME = -4
    INVALID_PRICE = -4
    UNKNOWN_ORDER = -5


class BuySell(IntEnum):
    BUY = 1
    SELL = 2


class Exchange(Events):
    __events__ = 'on_order_added', 'on_order_removed', 'on_best_price_changed'

    allowed_stock_codes = {'AAPL', 'MSFT', 'GOOG'}

    def __init__(self):
        self.exchange = {}
        self.orders = {}
        self.current_order_id = 0

    def add_order(self, stock_code, buy_sell, volume, price, user_reference):
        """
        Doing the checks for errorcode.
        Define the order information.
        Add orders
        Fire the order_added event.
        If best price has changed also fire the best price changed event
        """
        if stock_code not in self.allowed_stock_codes:
            return ExchangeErrorCodes.INVALID_STOCK_CODE.value

        if not isinstance(buy_sell, BuySell):
            return ExchangeErrorCodes.INVALID_BUY_SELL.value

        if not self.volume_valid(volume):
            return ExchangeErrorCodes.INVALID_VOLUME.value

        if not self.price_valid(price):
            return ExchangeErrorCodes.INVALID_PRICE.value

        order = self.add_to_order_book(stock_code, buy_sell, volume, price, user_reference)

        self.send_add_order_events(order)

        return 0

    def remove_order(self, order_id):
        """
        Check for the UNKNOWN errorcode.
        Remove orders.
        Fire the order_removed event.
        If best price has changed also fire the best price changed event.
        """
        if order_id not in self.orders:
            return ExchangeErrorCodes.UNKNOWN_ORDER.value

        order = self.remove_from_order_book(order_id)

        self.send_remove_order_events(order)

        return 0

    def send_remove_order_events(self, order):
        self.on_order_removed({
            'order_id': order['order_id'],
            'user_reference': order['user_reference']
        })
        if self.has_best_price_changed(order):
            self.emit_best_price_changed(order['stock_code'])

    def remove_from_order_book(self, order_id):
        """
        Removes the order from book.
        When the volume of a pricelevel is reduced to 0 after the order is removed, we'll pop that price level.
        """
        order = self.orders.pop(order_id)
        price_levels = self.get_price_levels(order['stock_code'], order['buy_sell'])
        price = order['price']
        price_levels[price] -= order['volume']
        if price_levels[price] == 0:
            price_levels.pop(price)

        return order

    def add_to_order_book(self, stock_code, buy_sell, volume, price, user_reference):
        """
        This method first builds the order with order information and add to orders dict
        then build the pricelevels for each stock & buySell 
        """
        order = self.build_order(buy_sell, price, stock_code, user_reference, volume)
        order_id = order['order_id']

        self.orders[order_id] = order

        price_levels = self.get_price_levels(stock_code, buy_sell)
        if price not in price_levels:
            price_levels[price] = 0
        price_levels[price] += order['volume']

        return order

    def send_add_order_events(self, order):
        self.on_order_added(order)
        if self.has_best_price_changed(order):
            self.emit_best_price_changed(order['stock_code'])

    def has_best_price_changed(self, order):
        """
        returns if best price has changed.
        Note that when dealing with Sell orders, 
        we shouldn't compare when there's no sell price level as 0 will always be the min value
        """
        buy_sell = order['buy_sell']
        price = order['price']
        price_levels = self.get_price_levels(order['stock_code'], buy_sell)
        if buy_sell == BuySell.BUY:
            limit_price, _ = self.get_best_buy_price_level(price_levels)
            best_price_changed = limit_price <= price
        else:
            limit_price, _ = self.get_best_sell_price_level(price_levels)
            best_price_changed = True if not price_levels else limit_price >= price
        return best_price_changed

    def emit_best_price_changed(self, stock_code):
        buy_price_levels = self.get_price_levels(stock_code, BuySell.BUY)
        best_buy_price, best_buy_volume = self.get_best_buy_price_level(buy_price_levels)

        sell_price_levels = self.get_price_levels(stock_code, BuySell.SELL)
        best_sell_price, best_sell_volume = self.get_best_sell_price_level(sell_price_levels)

        self.on_best_price_changed({
            'stock_code': stock_code,
            'best_buy_price': best_buy_price,
            'best_buy_volume': best_buy_volume,
            'best_sell_price': best_sell_price,
            'best_sell_volume': best_sell_volume
        })

    def get_price_levels(self, stock_code, buy_sell):
        """
        get price level of stock & buySell. Used SortedDict here for performance adding in price level whilst maintaining the sorting in the dict
        """
        if stock_code not in self.exchange:
            self.exchange[stock_code] = {}

        stock_book = self.exchange[stock_code]
        if buy_sell not in stock_book:
            stock_book[buy_sell] = SortedDict()

        return stock_book[buy_sell]

    def build_order(self, buy_sell, price, stock_code, user_reference, volume):
        self.current_order_id += 1
        order = {
            'order_id': self.current_order_id,
            'user_reference': user_reference,
            'volume': volume,
            'price': price,
            'stock_code': stock_code,
            'buy_sell': buy_sell
        }
        return order

    @staticmethod
    def get_best_sell_price_level(sell_price_levels):
        """
        This returns min in sell_price_levels which is a sortedDict
        """
        try:
            return sell_price_levels.peekitem(0)
        except IndexError:
            return 0, 0

    @staticmethod
    def get_best_buy_price_level(buy_price_levels):
        """
        This returns max in buy_price_levels which is a sortedDict
        """
        try:
            return buy_price_levels.peekitem()
        except IndexError:
            return 0, 0

    @staticmethod
    def volume_valid(volume):
        try:
            return int(volume) > 0
        except ValueError:
            return False

    @staticmethod
    def price_valid(price):
        try:
            return float(price) > 0
        except ValueError:
            return False

########################################################validation cases
exchange = Exchange()

def print_order_added(event):
    print('Order added: ' + str(event))
    print()


def print_best_price_changed(event):
    print('Best price changed: ' + str(event))
    print()


def print_order_removed(event):
    print('Order removed: ' + str(event))
    print()


exchange.on_order_added += print_order_added
exchange.on_order_removed += print_order_removed
exchange.on_best_price_changed += print_best_price_changed

exchange.add_order('AAPL', BuySell.BUY, 1, 50.0, 'xyxy')
exchange.add_order('AAPL', BuySell.BUY, 1, 52.0, 'xyxy')
exchange.add_order('AAPL', BuySell.BUY, 1, 51.0, 'xyxy')
exchange.remove_order(2)
exchange.add_order('AAPL', BuySell.SELL, 4, 100, 'david')
exchange.add_order('AAPL', BuySell.BUY, 6, 45.0, 'david')
exchange.remove_order(5)
exchange.add_order('GOOG', BuySell.BUY, 8, 123, 'xyxy')
exchange.add_order('AAPL', BuySell.SELL, 2, 79, 'david')
exchange.add_order('AAPL', BuySell.SELL, 2, 79, 'david')
exchange.add_order('AAPL', BuySell.SELL, 5, 80, 'david')
error_code = exchange.add_order('lol', BuySell.BUY, 8, 123, 'xyxy')
print(error_code)