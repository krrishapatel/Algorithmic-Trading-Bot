import argparse
from collections import deque
from enum import Enum
import time
import socket
import json
from itertools import chain


team_name = "MANKEY"

# ~~~~~============== MAIN LOOP ==============~~~~~

def on_startup(state_manager):
    state_manager.send_order("BOND", "BUY", 999, 10)
    global global_past_five_WFC
    global_past_five_WFC = []

    global global_past_five_XLF
    global_past_five_XLF = []

    global global_past_five_GS
    global_past_five_GS = []

    global global_past_five_MS
    global_past_five_MS = []

    global global_past_five_VALE
    global_past_five_VALE = []

    global global_past_five_VALBZ
    global_past_five_VALBZ = []

def on_book(state_manager, book_message):
    """Called whenever the book for a symbol updates."""
    try:

        # Retrieve the highest buy price for each symbol
        xlf_orders = state_manager.open_and_pending_orders_in_symbol_and_direction_by_price_level('XLF', Dir.BUY)
        bond_orders = state_manager.open_and_pending_orders_in_symbol_and_direction_by_price_level('BOND', Dir.BUY)
        gs_orders = state_manager.open_and_pending_orders_in_symbol_and_direction_by_price_level('GS', Dir.BUY)
        ms_orders = state_manager.open_and_pending_orders_in_symbol_and_direction_by_price_level('MS', Dir.BUY)
        wfc_orders = state_manager.open_and_pending_orders_in_symbol_and_direction_by_price_level('WFC', Dir.BUY)

        XLF_price = max(xlf_orders.keys(), default=None)
        BOND_price = max(bond_orders.keys(), default=None)
        GS_price = max(gs_orders.keys(), default=None)
        MS_price = max(ms_orders.keys(), default=None)
        WFC_price = max(wfc_orders.keys(), default=None)

        # Ensure all prices are available before proceeding
        if None in [XLF_price, BOND_price, GS_price, MS_price, WFC_price]:
            return

        # Calculate the sum of the prices of the individual stocks
        stocks_sum = 3 * BOND_price + 2 * GS_price + 3 * MS_price + 2 * WFC_price

        # Check if converting XLF and selling the underlying stocks is profitable
        while XLF_price * 10 + 101 < stocks_sum:
            xlf_holdings = state_manager.position_for_symbol("XLF")
            if xlf_holdings <= 0:
                break

            state_manager.send_convert_message(state_manager.next_order_id(), "XLF", Dir.SELL, xlf_holdings)

            state_manager.send_order("BOND", Dir.SELL, BOND_price, 3)
            state_manager.send_order("GS", Dir.SELL, GS_price, 2)
            state_manager.send_order("MS", Dir.SELL, MS_price, 3)
            state_manager.send_order("WFC", Dir.SELL, WFC_price, 2)

    except IndexError:
        pass

    pass

def on_fill(state_manager, fill_message):
    """Called when one of your orders is filled."""


def on_trade(state_manager, trade_message):
    """Called when someone else's order is filled."""
    bond_position = state_manager.position_for_symbol("BOND")
    target_position = 0  # Define a target position for BOND

    if bond_position < target_position:
        # Buy BOND to reach the target position
        state_manager.send_order("BOND", Dir.BUY, 999, 1)
    elif bond_position > target_position:
        # Sell excess BOND to reach the target position
        state_manager.send_order("BOND", Dir.SELL, 1001, 1)

    #if trade_message['symbol'] == 'XLF':
        global_past_five_XLF.append(trade_message['price'])
        if len(global_past_five_XLF) > 6:
            global_past_five_XLF.pop(0)
    last_five_avg_XLF = sum(global_past_five_XLF) // 5
    state_manager.send_order("XLF", Dir.BUY, last_five_avg_XLF-3, 1)
    state_manager.send_order("XLF", Dir.SELL, last_five_avg_XLF+3, 1)


    if trade_message['symbol'] == 'WFC':
        global_past_five_WFC.append(trade_message['price'])
        if len(global_past_five_WFC) > 6:
            global_past_five_WFC.pop(0)
    last_five_avg_WFC = sum(global_past_five_WFC) // 5
    state_manager.send_order("WFC", Dir.BUY, last_five_avg_WFC-1, 1)
    state_manager.send_order("WFC", Dir.SELL, last_five_avg_WFC+1, 1)


    if trade_message['symbol'] == 'GS':
        global_past_five_GS.append(trade_message['price'])
        if len(global_past_five_GS) > 6:
            global_past_five_GS.pop(0)
    last_five_avg_GS = sum(global_past_five_GS) // 5
    state_manager.send_order("GS", Dir.BUY, last_five_avg_GS-1, 1)
    state_manager.send_order("GS", Dir.SELL, last_five_avg_GS+1, 1)

    if trade_message['symbol'] == 'MS':
        global_past_five_MS.append(trade_message['price'])
        if len(global_past_five_MS) > 6:
            global_past_five_MS.pop(0)
    last_five_avg_MS = sum(global_past_five_MS) // 5
    state_manager.send_order("MS", Dir.BUY, last_five_avg_MS-1, 1)
    state_manager.send_order("MS", Dir.SELL, last_five_avg_MS+1, 1)

    if trade_message['symbol'] == 'VALBZ':
        global_past_five_VALBZ.append(trade_message['price'])
        if len(global_past_five_VALBZ) > 6:
            global_past_five_VALBZ.pop(0)
    last_five_avg_VALBZ = sum(global_past_five_VALBZ) // 5

    if trade_message['symbol'] == 'VALE':
        global_past_five_VALE.append(trade_message['price'])
        if len(global_past_five_VALE) > 6:
            global_past_five_VALE.pop(0)
    last_five_avg_VALE = sum(global_past_five_VALE) // 5


    # if last_five_avg_VALBZ - last_five_avg_VALE > 30:
    #     state_manager.send_order("VALE", Dir.BUY, last_five_avg_VALE, 1)
    #     state_manager.send_convert_order("VALE", Dir.SELL, 1)
    #     state_manager.send_order("VALBZ", Dir.SELL, last_five_avg_VALBZ-5, 1)
    if last_five_avg_VALE - last_five_avg_VALBZ > 30:
        state_manager.send_order("VALBZ", Dir.BUY, last_five_avg_VALBZ, 1)
        state_manager.send_convert_order("VALBZ", Dir.SELL, 1)
        state_manager.send_order("VALBZ", Dir.SELL, last_five_avg_VALE-5, 1)



def main():
    args = parse_arguments()

    exchange = ExchangeConnection(args=args)
    state_manager = State_manager(exchange)

    # Store and print the "hello" message received from the exchange. This
    # contains useful information about your positions. Normally you start with
    # all positions at zero, but if you reconnect during a round, you might
    # have already bought/sold symbols and have non-zero positions.
    hello_message = exchange.read_message()
    print("First message from exchange:", hello_message)
    state_manager.on_hello(hello_message)

    on_startup(state_manager)
    

    # Here is the main loop of the program. It will continue to read and
    # process messages in a loop until a "close" message is received. You
    # should write to code handle more types of messages (and not just print
    # the message). Feel free to modify any of the starter code below.
    #
    # Note: a common mistake people make is to call _write_message() at least
    # once for every read_message() response.
    #
    # Every message sent to the exchange generates at least one response
    # message. Sending a message in response to every exchange message will
    # cause a feedback loop where your bot's messages will quickly be
    # rate-limited and ignored. Please, don't do that!
    while True:
        message = exchange.read_message()

        # Some of the message types below happen infrequently and contain
        # important information to help you understand what your bot is doing,
        # so they are printed in full. We recommend not always printing every
        # message because it can be a lot of information to read. Instead, let
        # your code handle the messages and just print the information
        # important for you!
        if message["type"] == "close":
            print("The round has ended")
            break
        elif message["type"] == "error":
            print(message)
        elif message["type"] == "reject":
            #print(message)
            state_manager.on_reject(message)
        elif message["type"] == "fill":
            print(message)
            state_manager.on_fill(message)
            on_fill(state_manager, message)
        elif message["type"] == "trade":
            print(message)
            on_trade(state_manager, message)
        elif message["type"] == "ack":
            print(message)
            state_manager.on_ack(message)
        elif message["type"] == "out":
            print(message)
            state_manager.on_out(message)
        elif message["type"] == "book":
            #print(message)
            on_book(state_manager, message)


# ~~~~~============== PROVIDED CODE ==============~~~~~

# You probably don't need to edit anything below this line, but feel free to
# ask if you have any questions about what it is doing or how it works. If you
# do need to change anything below this line, please feel free to


class Dir(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ExchangeConnection:
    def __init__(self, args):
        self.message_timestamps = deque(maxlen=500)
        self.exchange_hostname = args.exchange_hostname
        self.port = args.port
        exchange_socket = self._connect(add_socket_timeout=args.add_socket_timeout)
        self.reader = exchange_socket.makefile("r", 1)
        self.writer = exchange_socket

        self._write_message({"type": "hello", "team": team_name.upper()})

    def read_message(self):
        """Read a single message from the exchange"""
        message = json.loads(self.reader.readline())
        if "dir" in message:
            message["dir"] = Dir(message["dir"])
        return message

    def send_add_message(
        self, order_id: int, symbol: str, dir: Dir, price: int, size: int
    ):
        """Add a new order"""
        self._write_message(
            {
                "type": "add",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "price": price,
                "size": size,
            }
        )

    def send_convert_message(self, order_id: int, symbol: str, dir: Dir, size: int):
        """Convert between related symbols"""
        self._write_message(
            {
                "type": "convert",
                "order_id": order_id,
                "symbol": symbol,
                "dir": dir,
                "size": size,
            }
        )

    def send_cancel_message(self, order_id: int):
        """Cancel an existing order"""
        self._write_message({"type": "cancel", "order_id": order_id})

    def _connect(self, add_socket_timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if add_socket_timeout:
            # Automatically raise an exception if no data has been recieved for
            # multiple seconds. This should not be enabled on an "empty" test
            # exchange.
            s.settimeout(5)
        s.connect((self.exchange_hostname, self.port))
        return s

    def _write_message(self, message):
        what_to_write = json.dumps(message)
        if not what_to_write.endswith("\n"):
            what_to_write = what_to_write + "\n"

        length_to_send = len(what_to_write)
        total_sent = 0
        while total_sent < length_to_send:
            sent_this_time = self.writer.send(
                what_to_write[total_sent:].encode("utf-8")
            )
            if sent_this_time == 0:
                raise Exception("Unable to send data to exchange")
            total_sent += sent_this_time

        now = time.time()
        self.message_timestamps.append(now)
        if len(
            self.message_timestamps
        ) == self.message_timestamps.maxlen and self.message_timestamps[0] > (now - 1):
            print(
                "WARNING: You are sending messages too frequently. The exchange will start ignoring your messages. Make sure you are not sending a message in response to every exchange message."
            )


class Order:
    def __init__(self, symbol, size, price, dir):
        self.symbol = symbol
        self.size = size                   # size is always positive
        self.price = price
        self.dir = dir

    def __str__(self):
        """give us a good way of printing out the order"""
        return f'Order(size={self.size}, dir={self.dir.value}, price={self.price}, size={self.size})'

    def __repr__(self):
        """python sometimes calls the __str__() method and others calls the __repr__
        method. The details are unimportant, so we do the same in both cases"""
        return self.__str__()


class State_manager:
    def __init__(self, exchange):
        """Setup the initial state in the state manager"""
        self.exchange = exchange
        self.order_id_counter = -1         # start at -1 because we increment before returning the id
        # BOND, VALE, VALBZ, MS, GS, WFC, and XLF
        self.positions_by_symbol = {}
        self.unacked_orders = {}
        self.open_orders = {}
        self.pending_cancels = set()

    def position_for_symbol(self, symbol):
        """Get the current position in the provided symbol"""
        # NB: this gets set by the hello message right after initialization, so we don't
        # handle defaulting to zero
        return self.positions_by_symbol[symbol]


    def next_order_id(self):
        """Generate unique order ids using a monotonically increasing counter"""
        self.order_id_counter += 1
        return self.order_id_counter


    def on_ack(self, message):
        """Handle an ack by marking the order as live"""
        assert(message['type'] == 'ack')
        order_id = message['order_id']
        if order_id in self.unacked_orders:
            self.open_orders[order_id] = self.unacked_orders.pop(order_id)
        else:
            print("Unexpectedly got ack on unknown order_id", order_id)


    def on_fill(self, message):
        """Handle a fill by decrementing the open size of the order and updating our
        positions"""
        assert(message['type'] == 'fill')
        order_id = message['order_id']
        symbol = message['symbol']
        dir = message['dir']
        raw_size = message['size']
        size_multiplier = 1 if dir == Dir.BUY.value else -1
        size = raw_size * size_multiplier
        if order_id in self.open_orders:
            self.open_orders[order_id].size -= raw_size
            self.positions_by_symbol[symbol] = self.positions_by_symbol.get(symbol, 0) + size
        else:
            print("Unexpectedly got fill on order_id that we did not expect to be live", order_id)

    def on_out(self, message):
        """Handle an out by marking the order as no longer live"""
        assert(message['type'] == 'out')
        order_id = int(message['order_id'])
        if order_id in self.open_orders:
            del self.open_orders[order_id]
            self.pending_cancels.discard(order_id)
        else:
            print("Unexpectedly got out on order_id we did not expect to be live", order_id)

    def on_hello(self, message):
        """Handle a hello message by setting our current positions"""
        assert(message['type'] == 'hello')
        symbol_positions = message['symbols']
        for symbol_position in symbol_positions:
            symbol = symbol_position['symbol']
            position = symbol_position['position']
            self.positions_by_symbol[symbol] = position


    def on_reject(self, message):
        """Handle a reject message by removing that order from the live set of orders"""
        assert(message['type'] == 'reject')
        order_id = message['order_id']
        order = self.unacked_orders.pop(order_id)
        print("Got a reject on order_id", order_id)

    def send_order(self, symbol, dir, price, size):
        """Send an order, updating the internal state accordingly"""
        order_id = self.next_order_id()
        order = Order(symbol, size, price, Dir(dir))
        self.unacked_orders[order_id] = order
        self.exchange.send_add_message(order_id, symbol, dir, price, size)

    def send_convert_order(self, symbol, dir, size):
        """Send an order, updating the internal state accordingly"""
        order_id = self.next_order_id()
        order = Order(symbol, size, 0, Dir(dir))
        self.unacked_orders[order_id] = order
        self.exchange.send_convert_message(order_id, symbol, dir, size)

    def cancel_order(self, order_id):
        """Cancel an order, updating the internal state accordingly"""
        self.pending_cancels.add(order_id)
        self.exchange.send_cancel_message(order_id)

    def open_and_pending_orders_in_symbol_and_direction_by_price_level(self, symbol, dir):
        """Helper for getting the open and pending orders. This is used to compute the
        live orders by price level, which is how we determine which orders to cancel or
        send when setting orders"""
        output = {}
        for order_id, order in chain(self.open_orders.items(), self.unacked_orders.items()):
            if order.symbol == symbol and order.dir == dir and order_id not in self.pending_cancels:
                price_level = order.price
                if price_level not in output:
                    output[price_level] = {}

                output[price_level][order_id] = order

        return output

    def set_orders_in_symbol_for_direction(self, symbol, dir, size_by_price_level):
        """Send new orders and cancel existing orders such that the live orders match the provided orders"""
        current_orders = self.open_and_pending_orders_in_symbol_and_direction_by_price_level(symbol, dir)
        for price_level in (size_by_price_level | current_orders):
            current_orders_by_order_id = current_orders.get(price_level, {})
            current_size_at_price_level = 0

            for order in current_orders_by_order_id.values():
                current_size_at_price_level += order.size

            desired_size_for_price_level = size_by_price_level.get(price_level, 0)

            assert(desired_size_for_price_level >= 0)

            if current_size_at_price_level == desired_size_for_price_level:
                pass
            elif current_size_at_price_level < desired_size_for_price_level:
                self.send_order(symbol, dir, price_level, desired_size_for_price_level - current_size_at_price_level)
            else:
                # we're doing this the easy way. There's a DP solution (knapsack
                # problem) that would make this send the minimal number of messages to
                # the exchange, but that's probably overkill for what we're doing.
                for order_id in current_orders_by_order_id:
                    if order_id not in self.pending_cancels:
                        self.cancel_order(order_id)

                if desired_size_for_price_level != 0:
                    self.send_order(symbol, dir, price_level, desired_size_for_price_level)

def parse_arguments():
    test_exchange_port_offsets = {"prod-like": 0, "slower": 1, "empty": 2}

    parser = argparse.ArgumentParser(description="Trade on an ETC exchange!")
    exchange_address_group = parser.add_mutually_exclusive_group(required=True)
    exchange_address_group.add_argument(
        "--production", action="store_true", help="Connect to the production exchange."
    )
    exchange_address_group.add_argument(
        "--test",
        type=str,
        choices=test_exchange_port_offsets.keys(),
        help="Connect to a test exchange.",
    )

    # Connect to a specific host. This is only intended to be used for debugging.
    exchange_address_group.add_argument(
        "--specific-address", type=str, metavar="HOST:PORT", help=argparse.SUPPRESS
    )

    args = parser.parse_args()
    args.add_socket_timeout = True

    if args.production:
        args.exchange_hostname = "production"
        args.port = 25000
    elif args.test:
        args.exchange_hostname = "test-exch-" + team_name
        args.port = 22000 + test_exchange_port_offsets[args.test]
        if args.test == "empty":
            args.add_socket_timeout = False
    elif args.specific_address:
        args.exchange_hostname, port = args.specific_address.split(":")
        args.port = int(port)

    return args


if __name__ == "__main__":
    # Check that [team_name] has been updated.
    assert (
        team_name != "REPLAC" + "EME"
    ), "Please put your team name in the variable [team_name]."

    main()
