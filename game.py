from __future__ import print_function
from threading import Thread
from random import randrange, choice
from time import sleep
import os

try:
    from Queue import Queue as queue
except ImportError:
    from queue import Queue as queue

xrange = range


class PeriodicExecutor(Thread):
    def __init__(self, sleep, func, *args, **kwargs):
        """ execute func(params) every 'sleep' seconds """
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.sleep = sleep
        Thread.__init__(self, name="PeriodicExecutor")
        self.setDaemon(1)

    def run(self):
        while 1:
            sleep(self.sleep)
            self.func(*self.args, **self.kwargs)


class AbstractCell(object):
    prize = 0

    def __str__(self):
        return self.symbol


class EmptyCell(AbstractCell):
    prize = 0
    symbol = '-'


class SilverCell(AbstractCell):
    prize = 50
    symbol = '$'


class GoldenCell(AbstractCell):
    prize = 100
    symbol = '#'


class Map(object):
    empty, silver, golden = cells = [EmptyCell(), SilverCell(), GoldenCell()]

    def __init__(self, x, y):

        self.map = [[self.empty for i in xrange(y)]
                    for i in xrange(x)]
        self.x = x
        self.y = y

    def __str__(self):
        return '\n'.join(' '.join(str(i) for i in y) for y in self.map)

    def rows(self):
        for i in self.map:
            yield list(i)

    def __iter__(self):
        for row in self.map:
            for cell in row:
                yield cell

    def get(self, x, y):
        return self.map[x][y]

    def set(self, x, y, v):
        self.map[x][y] = v

    def add_player(self, player, symbol):
        self.map[player.x][player.y] = player
        player.symbol = symbol

    def move_player(self, who, dx, dy):
        x, y = who.x, who.y
        cell = self.get(x, y)
        if not isinstance(cell, Bot):
            return False
        x_, y_ = x+dx, y+dy
        if not (0 <= x_ < self.x and 0 <= y_< self.y):
            return False
        to_cell = self.get(x_, y_)
        if isinstance(to_cell, Bot):
            return False

        self.map[x][y], self.map[x_][y_] = self.empty, who
        who.x, who.y = x_, y_
        who.count += to_cell.prize
        return True


class Logic(object):

    def step(self, bot):
        return choice((-1, 0, 1)), choice((-1, 0, 1))


class Bot(object):
    def __init__(self, x, y, engine, logic):
        self.x = x
        self.y = y
        self.count = 0
        self.engine = engine
        self.logic = logic

    def run(self):
        dx, dy = self.logic.step(self)
        self.make_step(dx, dy)

    def make_step(self, dx,dy):
        return self.engine.send('step', self, (dx, dy))

    def __str__(self):
        return self.symbol


class Engine:
    def __init__(self, map):
        self.map = map
        self.queue = queue()

    def send(self, sign, who, args):
        self.queue.put((sign, who, args))

    def make_step(self, who, dx, dy):
        return self.map.move_player(who, dx, dy)

    def generate_cell(self):
        x, y = self.map.x, self.map.y
        x, y = randrange(x), randrange(y)
        if self.map.get(x, y) == self.map.empty:
            self.map.set(x, y, choice(self.map.cells))

    def start(self):
        logic = Logic()
        bot1 = self.bot1 = Bot(5, 4, self, logic)
        self.map.add_player(bot1, '1')
        PeriodicExecutor(0.1, bot1.run).start()

        bot2 = self.bot2 = Bot(5, 11, self, logic)
        self.map.add_player(bot2, '2')
        PeriodicExecutor(0.1, bot2.run).start()

        PeriodicExecutor(0.4, self.generate_cell).start()
        PeriodicExecutor(0.4, self.generate_cell).start()

        self.mainloop()

    signals = {'step': make_step}

    def mainloop(self):
        while True:
            os.system('cls')
            while not self.queue.empty():
                (sign, who, arg) = self.queue.get()
                if sign in self.signals:
                    self.signals[sign](self, who, *arg)
            print(self.map)
            print('bot1:', self.bot1.count)
            print('bot2:', self.bot2.count)
            sleep(0.1)


def main():
    field = Map(11, 16)
    engine = Engine(field)
    engine.start()

if __name__ == '__main__':
    main()
