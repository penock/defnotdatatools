"""
defnotdatatools.timing module is for things related to timestamp and timing how long things take. Notably, it's where the Timer class lives.

For how to import, see defnotdatatools/README.md.
"""


# < Setup > ============================================================================

import time



# < Constants > ===============================================================



# < Datetime items > ===============================================================

def now_for_filename(date_only=False):
    """Return local timestamp for a filename (eg "20151231T235900" was New Year's Eve 11:59pm)"""
    if date_only:
        return time.strftime("%Y%m%d", time.localtime())
    else:
        return time.strftime("%Y%m%dT%H%M%S", time.localtime())

def now_for_str(date_only=False):
    """Return local timestamp as str (eg "2015-12-31 23:59:00" was New Year's Eve 11:59pm)"""
    if date_only:
        return time.strftime("%Y-%m-%d", time.localtime())
    else:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())



# < Timer class > ===============================================================

class Timer:

    """Timer class for timing how long parts of your code take."""

    ENOUGH_SECS_TO_USE_MINS = 120
    ENOUGH_SECS_TO_USE_HRS = 120 * 60
    DECIMAL_PLACES_FOR_STR = 2

    def __init__(self, name=''):
        """Creates and starts timer"""
        self._time_created = time.time()
        self._time_restarted = self._time_created

    @classmethod
    def construct_historical_timer(cls, time_created, time_restarted=None):
        """Alternate constructor so you could rebuild an old Timer from its repr()"""
        new_timer = Timer()
        new_timer._time_created = time_created
        new_timer._time_restarted = time_restarted
        return new_timer

    def __repr__(self):
        return 'Timer.construct_historical_timer(time_created=' + str(self._time_created) + \
               ', ' + 'time_restarted=' + str(self._time_restarted) + ')'

    def __str__(self):
        return 'Timer created at ' + \
               time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._time_created)) + \
               ', last restarted at ' + \
               time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._time_restarted)) + \
               ' (local time)'

    def start(self):
        """Starts timer (technically it's a restart, since timer is always considered running)"""
        self._time_restarted = time.time()

    def check_num(self, units='mins'):
        """Returning time since start, using passed units arg: 'secs' | 'mins' (default) | 'hrs' """
        DIVIDEBY_DICT = {'secs': 1,
                         'mins': 60,
                         'hrs': 60*60}
        if units not in DIVIDEBY_DICT:
            raise KeyError("You gave an invalid units arg" + units)
        return (time.time() - self._time_restarted) / DIVIDEBY_DICT[units]

    def check_num_and_start(self, units='mins'):
        """Checks (returning number) and starts timer"""
        ret = self.check_num(units=units)
        self._time_restarted = time.time()
        return ret

    def cnums(self, units='mins'):
        """Shortcut alias for check_str_and_start()"""
        return self.check_num_and_start(units=units)

    def check_str(self, units='auto'):
        """Returns time since start, as a string, with reasonable units based on time"""
        if units == 'auto':
            time_amount = self.check_num(units='secs')
            if time_amount >= Timer.ENOUGH_SECS_TO_USE_HRS:
                units = 'hrs'
            elif time_amount >= Timer.ENOUGH_SECS_TO_USE_MINS:
                units = 'mins'
            else:
                units = 'secs'

        time_amount = self.check_num(units=units)
        return ''.join(('{:.', str(Timer.DECIMAL_PLACES_FOR_STR), 'f} {}')).format(time_amount, units)

    def check_str_and_start(self, units='auto'):
        """Checks (returning str) and starts timer"""
        ret = self.check_str(units=units)
        self._time_restarted = time.time()
        return ret

    def css(self, units='auto'):
        """Shortcut alias for check_str_and_start()"""
        return self.check_str_and_start(units=units)
