# VEX ROBOTICS RAMP robot
# noinspection PyPep8
import time
import datetime
import math

"""Modules
    set()
        sets a variable
        alerts listeners to change
        adds the variable to the changeList
    get()
        gives variable value
    post()
        sends variables in variable chageList to output drivers

Requests
    load()
        loads all listeners
    checkConditions()
        when listener alerts to change, check conditions
    executeCommand()
        code to execute

Output Drivers
    put()
        update current state with some object
    post()
        output current state
    clear()
        clear driver
    engaged(boolean)
        turns driver on or off
"""

waitingQue = []


def date_of_next_weekday(weekday, today=datetime.datetime.today()):
    days_to_go = 6 - today.weekday()
    if days_to_go:
        today += datetime.timedelta(days_to_go)
    return today


def echo():
    pass


class Command():  # update variables matrix and listener related functions
    """
    methods
        load: loads relevant variables for execution
        post: executes, exists for subclass creation
        execute: runs all of the commands and passes them the modules listed. recommended commands have *args
        secure: removes system oriented modules from list of modules and returns it in tuple form
    """

    def __init__(self, commands, modules, adminPass=False):
        """
            :param commands: list of python functions to run with 'modules' as args
            :param modules: string list of modules to load
            """
        self.bannedModules = []
        self.adminPass = adminPass
        self.modules = self.load(modules)
        self.commands = commands

    def secure(self, modules):
        if self.adminPass == "PassPhrase":
            self.bannedModules = []
        else:
            self.bannedModules = ['sys', 'os', 'os2']
        for bannedModule in self.bannedModules:
            try:
                modules.remove(bannedModule)
            except:
                pass
        return modules

    def post(self):
        self.execute()

    def load(self, modules):
        modules = self.secure(modules)
        module_object_list = []
        for key in globals().keys():
            for module in modules:
                if key == module:
                    module_object_list.append(module)
                    break
        return tuple(module_object_list)

    def execute(self):
        """
        :return: None
        """
        for command in self.commands:
            command(*self.modules)


class Event(Command):
    """
    checks over conditions upon triggers being activated. Useful for common commands and scheduled objects
    """
    # TODO: must add time conditions handler (new 'Scheduled object' class?)
    def __init__(self, commands, modules, triggers, conditions, adminPass=False):
        """
            :param commands: list of functions to be passed the requested modules and run. recommend define with *args
            :param modules: string list of modules to load
            :param triggers: list of IntegerVariable objects to listen to
            :param conditions: list of python functions that should return True or False when passed requested modules
            """
        Command.__init__(self, commands, modules, adminPass)
        for variable in triggers:
            variable.listen(self.post)
        self.conditions = conditions

    def check_conditions(self):
        """
        :return: If all conditions are true, it returns true; otherwise it returns false.
        checks all of the conditions that exist on this command.
        """
        for condition in self.conditions:
            if not condition(*self.modules):
                return False
        return True

    def post(self):
        """
        checks conditions and executes if conditions are met
        :return: None
        """
        if self.check_conditions():
            self.execute()


class Variable():
    """
    post:   passes post method the value of variable and post_args
    listen:
    set:
    """

    def __str__(self):
        return str(self.value)

    def __init__(self, initial=0, post_method=echo, *post_arguments):
        """
        :param post_method:  a function which will send the variables value to a driver when passed that value
        :param initial:  an initial representing the initial value of the variable
        :param post_arguments: any arguments to be called with post(notably those that would identify the var)
        class contains post, value, and listeners
        """

        self.postMethod = post_method
        self.postArgs = post_arguments
        self.value = initial
        self.listeners = []

    def convertValue(self, value):
        return value

    def post(self):
        self.postMethod(self.value, *self.postArgs)

    def listen(self, alert_function):
        self.listeners.append(alert_function)

    def set(self, value):
        self.value = self.convertValue(value)
        for listener in self.listeners:
            listener()


class IntegerVariable(Variable):
    """
    :var self.post: corresponds to post_method will be used to update the variable
    :var self.value: the current value of the object. Will automatically be used in mathematical operations
    :var self.listeners: a list of functions to be called (without post_arguments) when the value changes
    A variable is an integer like object which can be listened to. IntegerVariable.listen(function) will cause the execution of
    that function should the variable be modified. For this reason, IntegerVariable.set(x) should be used instead of
    IntegerVariable.value = x. the value can be any class with numerical operation methods, (e.g. int, float, or any sub-class
    of those).
    NOTE: use RangedVariable.set(value) to set value, do NOT use RangedVariable.value=value
        THESE SHOULD NOT BE DONE
            WRONG RangedVariable = x + y
            WRONG RangedVariable.value = x + y
            WRONG RangedVariable = RangedVariable + 1
        THESE SHOULD BE DONE
            RIGHT RangedVariable += 1
            RIGHT RangedVariable.set(x + y)
        this is due to the nature of the '=', if '=' is used, the variable will become a simple integer. It will no
        longer be a RangedVariable. the normal mathematical operators will work.
        Using RangedVariable.value = ... can cause problems because the value will not be converted properly. it will
        be set to a new number without checking that it is within it's limits
    """

    def __add__(self, other):
        if type(other) == int:
            return int(self.value) + other
        if isinstance(other, IntegerVariable):
            return self.value + other.value
        return self.value

    def __sub__(self, other):
        if type(other) == int:
            return self.value - other
        if isinstance(other, IntegerVariable):
            return self.value - other.value
        return self

    def __mul__(self, other):
        if type(other) == int:
            return self.value * other
        if isinstance(other, IntegerVariable):
            return self.value * other.value
        return self

    def __floordiv__(self, other):
        if type(other) == int:
            return self.value // other
        if isinstance(other, IntegerVariable):
            return self.value // other.value
        return self

    def __mod__(self, other):
        if type(other) == int:
            return self.value % other
        if isinstance(other, IntegerVariable):
            return self.value % other.value
        return self

    def __divmod__(self, other):
        if type(other) == int:
            return divmod(self.value, other)
        if isinstance(other, IntegerVariable):
            return divmod(self.value, other.value)
        return self

    def __pow__(self, other, modulo=None):
        if type(other) == int:
            return pow(self.value, other, modulo)
        if isinstance(other, IntegerVariable):
            return pow(self.value, other.value)
        return self, modulo

    def __lshift__(self, other):
        if type(other) == int:
            return self.value << other
        if isinstance(other, IntegerVariable):
            return self.value << other.value
        return self

    def __rshift__(self, other):
        if type(other) == int:
            return self.value >> other
        if isinstance(other, IntegerVariable):
            return self.value >> other.value
        return self

    def __and__(self, other):
        if type(other) == int:
            return self.value & other
        if isinstance(other, IntegerVariable):
            return self.value & other.value
        return self

    def __xor__(self, other):
        if type(other) == int:
            return self.value ^ other
        if isinstance(other, IntegerVariable):
            return self.value ^ other.value
        return self

    def __or__(self, other):
        if type(other) == int:
            return self.value | other
        if isinstance(other, IntegerVariable):
            return self.value | other.value
        return self

    def __div__(self, other):
        if type(other) == int:
            return self.value / other
        if isinstance(other, IntegerVariable):
            return self.value / other.value
        return self

    def __truediv__(self, other):
        if type(other) == int:
            return self.value / other
        if isinstance(other, IntegerVariable):
            return self.value / other.value
        return self

    def __iadd__(self, other):
        if type(other) == int:
            self.set(self.value + other)
        if isinstance(other, IntegerVariable):
            self.set(self.value + other.value)

    def __isub__(self, other):
        if type(other) == int:
            self.set(self.value - other)
        if isinstance(other, IntegerVariable):
            self.set(self.value - other.value)

    def __imul__(self, other):
        if type(other) == int:
            self.set(self.value * other)
        if isinstance(other, IntegerVariable):
            self.set(self.value * other.value)

    def __idiv__(self, other):
        if type(other) == int:
            self.set(self.value / other)
        if isinstance(other, IntegerVariable):
            self.set(self.value / other.value)

    def __itruediv__(self, other):
        if type(other) == int:
            self.set(self.value / other)
        if isinstance(other, IntegerVariable):
            self.set(self.value / other.value)

    def __ifloordiv__(self, other):
        if type(other) == int:
            self.set(self.value // other)
        if isinstance(other, IntegerVariable):
            self.set(self.value // other.value)

    def __imod__(self, other):
        if type(other) == int:
            self.set(self.value % other)
        if isinstance(other, IntegerVariable):
            self.set(self.value % other.value)

    def __ipow__(self, other, modulo=None):
        if type(other) == int:
            self.set(pow(self.value, other, modulo))
        if isinstance(other, IntegerVariable):
            self.set(pow(self.value, other.value, modulo))

    def __ilshift__(self, other):
        if type(other) == int:
            self.set(self.value << other)
        if isinstance(other, IntegerVariable):
            self.set(self.value << other.value)

    def __irshift__(self, other):
        if type(other) == int:
            self.set(self.value >> other)
        if isinstance(other, IntegerVariable):
            self.set(self.value >> other.value)

    def __iand__(self, other):
        if type(other) == int:
            self.set(self.value & other)
        if isinstance(other, IntegerVariable):
            self.set(self.value & other.value)

    def __ixor__(self, other):
        if type(other) == int:
            self.set(self.value ^ other)
        if isinstance(other, IntegerVariable):
            self.set(self.value ^ other.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __ior__(self, other):
        if type(other) == int:
            self.set(self.value | other)
        if isinstance(other, IntegerVariable):
            self.set(self.value | other.value)

    def __str__(self):
        return str(self.value)

    def __init__(self, start_state=0, post_method=echo, *post_arguments):
        """
            :param post_method:  a function which will send the variables value to a driver when passed that value
            :param start_state:  an integer representing the initial value of the variable
            :param post_arguments: any arguments to be called with post(notably those that would identify the var)
            class contains post, value, and listeners
            """
        Variable.__init__(self, start_state, post_method, *post_arguments)
        self.value = self.convertValue(start_state)


def datetime_from_dict(values, reverse=False):
    if not reverse:
        return datetime.datetime(
            values['$Y'],
            values['$M'],
            values['$D'],
            values['%H'],
            values['%M'],
            values['%S']
        )
    else:
        return {
            '$Y': values.year,
            '$M': values.month,
            '$D': values.day,
            '%H': values.hour,
            '%M': values.minute,
            '%S': values.second,
        }


class TimeVariable(Variable):
    """
    will alert listeners when target_time is reached
    """

    def __init__(self, target_time, post_method, time_format="%H%M%S", *post_arguments):
        """
            tokens:
                $: date value
                %: time value
                capital: formal value
                lowercase: informal value
                $Y  year            (e.g. 2014)
                $M month number     (e.g. 4)
                $m month name       (e.g. january)
                $D Day number       (e.g. 14, 29, 31)(not day number /7)
                $d Day name         (e.g. tuesday, thursday)

                %H 24 hour hour     (e.g. 22)
                %h 12 hour hour     (e.g. 1)
                %M minute           (e.g. 32)
                %S second           (e.g. 15)
            if a value is not specified, this function will not automatically set it to zero, nor will it in any way
            account for the value.
            :param target_time: time, according to format specified. Each variable should be separated with some mark
                if several numbers are inside a single variable separated by a comma, each will be tested (e.g. 1,2,
                3,4:30)
                example
                    time_format = $M:$D:%H:%M
                    target_time = 12,3,4:30,45
                    will trigger at 12:30, 12:45, 3:30, 3:45, 4:30, 4:45
            :param time_format: time format, include any formatting marks (e.g. %H:%M)
            """

        Variable.__init__(self, post_method, *post_arguments)
        self.format = time_format
        self.timeSymbols = ['$Y', '$M', '$m', '$D', '$d', '%H', '%h', '%M', '%S']
        self.dateTimeEquivelent = []
        self.targetTime = {
            '$Y': [],
            '$M': [],
            '$m': [],
            '$D': [],
            '$d': [],
            '%H': [],
            '%h': [],
            '%M': [],
            '%S': [],
        }
        self.month_converter = {
            'january': 1,
            'february': 2,
            'march': 3,
            'april': 4,
            'may': 5,
            'june': 6,
            'july': 7,
            'august': 8,
            'september': 9,
            'october': 10,
            'november': 11,
            'december': 12
        }
        self.value = self.get_next_time

    def post(self):
        self.postMethod(self.value, self.postArgs)
        self.set(self.get_next_time())
        global waitingQue
        waitingQue.append((self.value, self.post))

    def get_next_time(self):
        """
        :return: datetime.datetime for the next time this object should be posted according to the preset schedule
        """
        valid_times = self.targetTime  # times that this object is permitted to run, to be modified in this method
        today = datetime.datetime.today()  # the time at the moment that the next_time is to be retrieved
        next_time = datetime_from_dict(today, True)  # 'today' in dictionary form
        keys = ['$Y', '$M', '$D', '%H', '%M', '%S']  # all of the different units of time to be considered
        i = -1
        while i < len(keys):
            i += 1
            key = keys[i]  # the current unit being evaluated
            current_value_list = sorted(valid_times[key])  # should be sorted in ascending order; list of valid values

            if key == '$D' and valid_times['$d']:  # if we are deciding the day-of-the-week
                valid_weekdays = sorted(valid_times['$d'])
                for weekday in valid_weekdays:
                    new_date = date_of_next_weekday(weekday,
                                                    datetime_from_dict(next_time))  # datetime object for next 'weekday'
                    if new_date >= today:  # if new_date occurs after today
                        valid_times['$D'].append(new_date)  # add the new_date to the days

            if not current_value_list:
                """
                checks if next_time[key] is a float because the next key has no valid values. If it is, it will try
                to add one to the current next_time[key]. To test whether this is a real time or not, a datetime
                obj will be created. If a valueError is raised, to signal an invalid date/time, done will be set to
                False and the preceding value will be pushed forward
                """
                if type(next_time[key]) == float:
                    next_time[key] = math.ceil(next_time[key])
                    try:
                        datetime_from_dict(next_time)
                        done = True
                    except ValueError:
                        done = False
                        next_time[key] -= 1
                else:
                    done = True

            else:
                done = False  # a valid date has not yet been found
                for value in current_value_list:
                    if value >= next_time[key]:  # if the value being inspected is past now:
                        if value != next_time[key]:
                            for lesser_unit in range(i, len(keys)):
                                # this makes sure that, if it is 11:00 on a monday, 9:00 next tuesday is still valid.
                                # Without this, 9:00 would be interpreted as before 11:00 and marked invalid
                                # because that time has already passed. In fact, that time has not passed, and the
                                # computer must not think that it has. This loop goes through every unit of time smaller
                                # than the one being edited and sets it's value to 0. Nothing can be before 0, and thus
                                # the bug is remedied.
                                lesser_unit = keys[lesser_unit]
                                next_time[lesser_unit] = 0
                        next_time[key] = value
                        done = True
                        break
            if not done:  # if no valid date has been found,
                """
                if no valid date has been found, one must change the unit of time preceding the current unit of
                time to another value.
                if there it is 11:00 on monday, monday is a valid day, but 9:00 is not a valid time. If 9:00 is
                the only option, this function must change the "next time"'s day to another valid_value for day
                that is after monday.
                This tries to delete the value that originally set the day to monday,
                If that is not possible (most likely because '$D' is an empty list and monday is the default because
                it is today) it will add .5 to the
                This sets i back one unit to re-evaluate the previous thing
                if there is an empty list in the valid_times[key], and the next_time entry is a float, one unit of
                time will be added to the value. if that results in a change in it's parent value, this will happen
                again
                """
                previous_key = keys[i - 1]
                try:
                    del valid_times[previous_key][valid_times[previous_key].index(next_time[previous_key])]
                except KeyError:
                    next_time[previous_key] = float(next_time[previous_key] + .5)
                # the above thingy removes from the valid_times the
                i -= 2
        next_time = datetime_from_dict(next_time)
        return next_time

    def convert_target_time(self, value):
        if len(self.targetTime['$m']):
            for month in self.targetTime['$m']:
                self.targetTime['$M'].append(self.month_converter[month])

        if len(self.targetTime['%h']):
            for hour in self.targetTime['%h']:
                self.targetTime['%H'].append(hour)
                self.targetTime['%H'].append(hour + 12)

        self.timeSymbols.remove('$m')
        self.timeSymbols.remove('%h')
        del self.targetTime['$m']
        del self.targetTime['$h']

    def set_target_time(self, string):
        """
        goes through time mask and finds all '$' and '%'. Beginning with the lowest indexes, it lists the seporators and
        symbols in order, in two lists. A for loop begins which itterates through each list. It looks between the end of
        each separator and the beginning of the next and adds that value to the target time dict according to the
        current symbol
        """
        ending = '&^%$#'
        symbols = []
        separators = []
        temp_string_mask = self.format  # for editing
        while True:
            position = min(temp_string_mask.find('%'), temp_string_mask.find('$'))
            separators.append(self.format[0:position])
            symbols.append(string[position:position + 2])
            temp_string_mask = temp_string_mask[position + 2:]
        separators.append(ending)
        string += ending
        for i in range(len(symbols)):
            start_slice = string.find(separators[i]) + len(symbols)  # TODO: replace find with index (later)
            end_slice = string.find(separators[i + 1])
            value = string[start_slice:end_slice].split(',').sort()  # turns to list of different possible values
            self.targetTime[separators[i]] = value


class RangedVariable(IntegerVariable):
    """
    A ranged variable is one which is an integer-like object restricted to a certain range. If one attempted to set()
    this variable to a value outside that range, it will instead be set() to the nearest possible value.
    example:
        var = RangedVariable(initial_value = 0, min_value = 0, max_value = 10)
        set(var, 5)
        print var  # prints 5
        set(var, 10)
        print var  # prints 10
        set(var, 15)
        print var  # prints 10
        set(var, -1)
        print var  # prints 0
    It can be either an int or a float and is useful for controlling things that cannot exceed a certain value.
    NOTE: use RangedVariable.set(value) to set value, do NOT use RangedVariable.value=value
        THESE SHOULD NOT BE DONE
            WRONG RangedVariable = x + y
            WRONG RangedVariable.value = x + y
            WRONG RangedVariable = RangedVariable + 1
        THESE SHOULD BE DONE
            RIGHT RangedVariable += 1
            RIGHT RangedVariable.set(x + y)
        this is due to the nature of the '=', if '=' is used, the variable will become a simple integer. It will no
        longer be a RangedVariable. the normal mathematical operators will work.
        Using RangedVariable.value = ... can cause problems because the value will not be converted properly. it will
        be set to a new number without checking that it is within it's limits
    """

    def __init__(self, initial=0, min_value=0, max_value=10, post_method=echo(), *post_arguments):
        """
            :param post_method:  a function which will send the variables value to a driver when passed that value
            :param initial:  an integer representing the initial value of the variable
            :param max_value:    an integer representing the maximum value of the variable
            :param min_value: an integer representing the minimum value of the variable

        """

        self.post = post_method
        self.max = max_value
        self.min = min_value
        IntegerVariable.__init__(self, initial, post_method, *post_arguments)

    def convertValue(self, value):
        value = min(self.max, value)
        value = max(self.min, value)
        return value

    def set(self, value):
        self.value = value
        if not self.max >= self.value >= self.min:
            self.value = self.convertValue(value)
        for listener in self.listeners:
            listener()


class VariableMatrix():
    """
    A dictionary-like object containing variables that automates the variable setting process with the __setitem__
    It is the root-class of the module, and is useful for classes that require many variables to be easily referenced
    can use
        VariableMatrix['IntegerVariable'] = x
        same as IntegerVariable.set(x)
    can use
        for IntegerVariable in VariableMatrix
    can use
        VariableMatrix['new variable'] = IntegerVariable(x)
    post() iterates through variables and posts them each
    """

    def __init__(self, variables={}):
        """
        :param variables: a dictionary object of variable and their keys
        :return:
        """
        self.variables = variables

    def post(self):
        for variable in self.variables:
            variable.post()

    def __setitem__(self, key, value):
        value = value
        self.variables[key].set(value)

    def __getitem__(self, key):
        value = self.variables[key].value
        return value

    def __delitem__(self, key):
        del self.variables[key]

    def __len__(self):
        return len(self.variables)

    def listen(self, alert_function, variable):
        self.variables[variable].listen(alert_function)


class Module(VariableMatrix):
    """
    pass variable dictionary to reference and post_method with args, and all variable posting will become automated.
    """

    def __init__(self, variables, post_method=echo, *postArgs):
        """
        :param variables: dictionary of string keys and IntegerVariable values which will be contained in the module
        :param post_method: a function which will be used to post each variable. This method will replace the previously
        configured method. if set to echo, it will have no effect.
        :param *postArgs: arguments that will be past to the post_method (unless post_method is echo)

        :type postArgs: dict
        """
        VariableMatrix.__init__(self, variables)
        assert isinstance(variables, dict)
        if post_method != echo:
            for key in variables.keys():
                variables[key].postMethod = post_method
                temporary_post_args = list(postArgs).insert(0, key)
                variables[key].postArgs = temporary_post_args
        self.postMethod = post_method
        self.postArgs = postArgs

    def post(self):
        for variable in self.variables:
            variable.post()


class InputDriver():
    """
    Uses sweeps for new data with raw_data_source and then uses command_parser to create new command objects.
    It is useful for user-interface, accessed via raw_data_source, that can be fully parsed by a custom function.
    It should be noted that this is a very bare-bones class, the two major methods may require lengthy definitions that
    should be located in separate files, preferably named after the driver. They should be located in the same folder
    as this and will be loaded with it
    In the boot-lacer, all drivers will be run() simultaneously in separate threads, for this reason a high refresh
    period is desirable to lower CPU usage. Recommendations
    Direct and spontaneous user interface   :   0.25 seconds
    Direct and continuous user interface    :   0.5 seconds, changed to .1 when interface begins
    Direct and predictable user interface   :   1.5 seconds, changed to .1 when interface begins
    Automated interface                     :   1.0 seconds, changed to .1 when interface begins
    These should keep usage very low and allow quick responses to unexpected direct interface
    """

    def __init__(self, raw_data_source, command_parser, refresh_period=0):
        """
        :param raw_data_source: function to call that will return a list of new raw data
            should take no parameters
            should always return a list of strings of data (even an empty one)
        :param command_parser: function to call that will parse raw data into commands (or sub-class thereof)
        :param refresh_rate: time to sleep between checking raw_data_source
        :return:
        """
        self.getRawData = raw_data_source
        self.parse = command_parser
        self.refreshPeriod = refresh_period

    def post(self):
        """
        This function checks for new data, creating new command instances if appropriate. Unlike run(), it will end
        :return: None
        """
        new_raw_data = self.getRawData
        for data in new_raw_data:
            command = self.parse(data)
            command.post()

    def run(self):
        """
        !WARNING! This function will never end. It is meant to be run in a separate thread.
        This function will continually check for new data and create & post new command objects
        To run only once, use the .post() function instead
        """
        while True:
            self.post()
            print 'hi'
            time.sleep(self.refreshPeriod)


class OutputDriver(VariableMatrix):
    """
    this should not interface with modules, nor should it parse any data significantly. It should use as few lines
    of code as possible to simply submit, with proper formatting, the relevant variables. Variables can be stored as
    variables and accessed like in a IntegerVariable Matrix or stored as any other type and accessed like a normal dictionary
    example:
        a display OutputDriver should have an image as a variable and simply push the image to the screen on post()
    """

    def __init__(self, variables, post_method, *postArgs):
        """
        :param variables: dictionary of keys and IntegerVariable objects
        :param post_method: a method that must accept this output driver as an argument, as well as:
        :param postArgs: all postArgs will be passed to post_method along with the driver
        post_method(OutputDriver, *postArgs)
        :return:
        """
        VariableMatrix.__init__(self, variables)
        self.postMethod = post_method
        self.postArgs = postArgs

    def post(self):
        self.postMethod(self, *self.postArgs)

    def __setitem__(self, key, value):
        value = value
        try:
            test = self.variables[key]
            if isinstance(self.variables[key], IntegerVariable):
                self.variables[key].set(value)
            else:
                self.variables[key] = value
        except ReferenceError:
            self.variables[key] = value

    def __getitem__(self, key):
        target = self.variables[key]
        if isinstance(target, IntegerVariable):
            value = self.variables[key].value
        else:
            value = target
        return value

    def listen(self, alert_function, variable):
        try:
            self.variables[variable].listen(alert_function)
        except AttributeError:
            raise (AttributeError, "cannot listen to type " + type(self.variables[variable]))
