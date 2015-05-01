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
    """
    finds the next instance of a target weekday and returns the corresponding datetime object
    :param weekday: day of the week to find (0 = monday, 1 = tuesday
    :param today: date to search from
    :return:
    """
    days_to_go = 6 - today.weekday()
    if days_to_go:
        today += datetime.timedelta(days_to_go)
    return today


def datetime_from_dict(values, reverse=False):
    """
    takes a dictionary containing symbols such as $Y, $M, $D, etc. and turns them into a datetime object. The
    dictionaries are used when multiple years, months, or days need to be included but are not compatible with
    the datetime module.
    :param values: either a dictionary or a datetime object depending on 'reverse'
    :param reverse: If reverse is  false (default), this will change a dict into a datetime. Otherwise, it turns a
    datetime into a dict
    :return:
    """
    if not reverse:
        return datetime.datetime(
            year=int(math.ceil(float(values['$Y']))) + 0,
            month=int(math.ceil(float(values['$M']))) + 0,
            day=int(math.ceil(float(values['$D']))) + 0,
            hour=int(math.ceil(float(values['%H']))) + 0,
            minute=int(math.ceil(float(values['%M']))) + 0,
            second=int(math.ceil(float(values['%S']))) + 0
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


def echo(*args):
    """does nothing"""
    pass


class Variable():
    """
    post:   passes post method the value of variable and post_args
    listen: executes the passed function with the optional 'listArgs' whenever the value of this variable is set
    set: sets the value of this variable and executes listening functions
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

    def convert_value(self, value):
        """
        A function used internally that converts 'value' to a valid value. Used in set().
        """
        return value

    def post(self):
        """
        activates post method and passes it postArgs
        """
        self.postMethod(self.value, *self.postArgs)

    def listen(self, alert_function, *alertArgs):
        """
        :param alert_function: function to be called when the value of this variable is altered
        :param alertArgs: arguments to pass to alert_function when it is called
        """
        self.listeners.append((alert_function, alertArgs))

    def set(self, value):
        """
        sets the value of the variable to 'value'
        """
        self.value = self.convert_value(value)
        for listener in self.listeners:
            listener[0](*listener[1])


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
            :param modules: string list/tuple of modules to load
            recommended that the modules list/tuple be duplicated in the function args.
            """
        self.bannedModules = []
        self.adminPass = adminPass
        self.modules = self.load(modules)
        self.commands = commands

    def secure(self, modules):
        """
        if self.adminPass is correct, it will unlock the sys, os, and os2 variables and allow them to be used.
        This method is far from complete and only really exists as a placeholder.
        :param modules: list of modules to be filtered
        :return:
        """
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
        """
        This function is presently the same as execute, but child classes change this function. It is also recommended
        over execute because post() is very universal, execute is not.
        :return:
        """
        self.execute()

    def load(self, modules):
        """
        takes modules and puts them in a tuple so they may be passed to the functions that are to be executed
        :param modules: modules to be loaded
        :return:
        """
        modules = self.secure(modules)
        module_object_list = []
        for module in modules:
            for key in globals().keys():
                if key == module:
                    module_object_list.append(module)
                    break
        return tuple(module_object_list)

    def execute(self):
        """
        runs each command specified in __init__ and runs it with the modules also loaded in __init__
        :return: None
        """
        for command in self.commands:
            command(*self.modules)


class IntegerVariable(Variable):
    """
    :var self.post: corresponds to post_method will be used to update the variable
    :var self.value: the current value of the object. Will automatically be used in mathematical operations
    :var self.listeners: a list of functions to be called (without post_arguments) when the value changes
    A variable is an integer like object which can be listened to. IntegerVariable.listen(function) will cause the
    execution of
    that function should the variable be modified. For this reason, IntegerVariable.set(x) should be used instead of
    IntegerVariable.value = x. the value can be any class with numerical operation methods, (e.g. int, float,
    or any sub-class
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
        self.value = self.convert_value(start_state)


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

    def convert_value(self, value):
        """
        converts value to one inside the range. Specifically, makes anything higher than max equal to max and
        anything lower than min equal to min.
        """
        value = min(self.max, value)
        value = max(self.min, value)
        return value

    def set(self, value):
        self.value = value
        if not self.max >= self.value >= self.min:
            self.value = self.convert_value(value)
        for listener in self.listeners:
            listener()


class TimeVariable(Variable):
    """
    will alert listeners when target_time is reached
    """

    def weekday(self, weekday):
        """
        :param weekday: weekdays are from 0-6 and may be in tuple, integer, or string form
        :return: TimeVariable
        """
        return self.__init__(str(weekday).strip(')').strip('('), "$d")

    def hour(self, hour):
        """
        :param hour: hours from 1-24 and may be in tuple, integer, or string form
        :return: TimeVariable
        """
        return self.__init__(str(hour).strip(')').strip('('), "$H")

    def __init__(self, target_time, post_method=echo, time_format="%H%M%S", *post_arguments):
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
        self.set_target_time(target_time)
        self.convert_target_time()
        self.value = self.get_next_time()

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
        while i < len(keys) - 1:
            i += 1
            key = keys[i]  # the current unit being evaluated
            current_value_list = sorted(valid_times[key])  # should be sorted in ascending order; list of valid values

            if key == '$D' and valid_times['$d']:  # if we are deciding the day-of-the-week
                valid_weekdays = sorted(valid_times['$d'])
                for weekday in valid_weekdays:
                    new_date = date_of_next_weekday(weekday,
                                                    datetime_from_dict(next_time))  # datetime object for next 'weekday'
                    if new_date >= today:  # if new_date occurs after today
                        valid_times['$D'].append(int(new_date.date))  # add the new_date to the days

            if not current_value_list:
                """
                checks if next_time[key] is a float because, if it is, the next key has no valid values.
                If it is, it will try to add one to the current next_time[key]. To test whether this is a
                real time or not, a datetime obj will be created. If a valueError is raised, to signal an
                invalid date/time, done will be set to False and the preceding value will be pushed forward
                """
                if next_time[key] != math.ceil(next_time[key]):
                    next_time[key] = math.ceil(next_time[key])

                    datetime_from_dict(next_time)
                    done = True

                    """except ValueError:
                        print ValueError
                        done = False
                        next_time[key] -= 1"""
                else:
                    done = True

            else:
                done = False  # a valid date has not yet been found
                for value in current_value_list:
                    if value >= next_time[key]:  # if the value being inspected is past now:
                        if value != next_time[key]:
                            for lesser_unit in range(i + 1, len(keys)):
                                # this makes sure that, if it is 11:00 on a monday, 9:00 next tuesday is still valid.
                                # Without this, 9:00 would be interpreted as before 11:00 and marked invalid
                                # because that time has already passed. In fact, that time has not passed, and the
                                # computer must not think that it has. This loop goes through every unit of time smaller
                                # than the one being edited and sets it's value to 0. Nothing can be before 0, and thus
                                # the bug is remedied.
                                lesser_unit = keys[lesser_unit]
                                next_time[lesser_unit] = .5
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
                except ValueError:
                    next_time[previous_key] = float(next_time[previous_key] + .5)
                for lesser_unit in range(i, len(keys)):
                    # this makes sure that, if it is 11:00 on a monday, 9:00 next tuesday is still valid.
                    # Without this, 9:00 would be interpreted as before 11:00 and marked invalid
                    # because that time has already passed. In fact, that time has not passed, and the
                    # computer must not think that it has. This loop goes through every unit of time smaller
                    # than the one being edited and sets it's value to 0. Nothing can be before 0, and thus
                    # the bug is remedied.
                    lesser_unit = keys[lesser_unit]
                    next_time[lesser_unit] = .5
                # the above thingy removes from the valid_times the
                i -= 2
        next_time = datetime_from_dict(next_time)
        return next_time

    def convert_target_time(self):
        """
        cleans up target_time dictionary and merges redundant variables. Does not clear days of the week, this
        is left to the get_next_time function
        :return:
        """
        if len(self.targetTime['$m']):
            for month in self.targetTime['$m']:
                self.targetTime['$M'].append(self.month_converter[month.lower()])

        if len(self.targetTime['%h']):
            for hour in self.targetTime['%h']:
                self.targetTime['%H'].append(int(hour))
                self.targetTime['%H'].append(int(hour) + 12)

        self.timeSymbols.remove('$m')
        self.timeSymbols.remove('%h')
        del self.targetTime['$m']
        del self.targetTime['%h']

    def set_target_time(self, string):
        """
        goes through time mask and finds all '$' and '%'. Beginning with the lowest indexes, it lists the separators and
        symbols in order, in two lists. A for loop begins which iterates through each list. It looks between the end of
        each separator and the beginning of the next and adds that value to the target time dict according to the
        current symbol
        """
        endCap = '@#@#@#@#'
        symbols = []
        separators = []
        temp_string_mask = endCap + self.format + endCap  # for editing
        string = endCap + string + endCap
        while len(temp_string_mask):
            next_date = max(temp_string_mask.find('$'), -1)
            next_time = max(temp_string_mask.find('%'), -1)
            if next_date < 0 or next_time < 0:  # if either % or $ is not found
                if next_date < 0 and next_time < 0:  # if there are no more of either in the string
                    separators.append(temp_string_mask)  # add the ending of the mask to the separators
                    break
                else:  # if only one has run out, the nextTag is at the higher one
                    next_tag = max(next_date, next_time)
            else:
                next_tag = min(next_date, next_time)

            separators.append(temp_string_mask[0:next_tag])  # add the characters preceding the var to separators
            symbols.append(temp_string_mask[next_tag:next_tag + 2])  # adds the time var to the symbols list
            temp_string_mask = temp_string_mask[next_tag + 2:]  # takes the processed code out of the mask
        # now have a list of separators, and what variables come between those separators
        for i in range(len(symbols)):  # this will look between each set of separators and find the time var there
            start_slice = string.find(separators[i]) + len(separators[i])  # TODO: replace find with index (later)
            string = string[start_slice:]
            end_slice = string.find(separators[i + 1])
            # found either side of value
            value = sorted(string[:end_slice].split(','))  # pulls content out and converts to list form
            self.targetTime[symbols[i]] = value  # modifies the appropriate dictionary entry
            string = string[end_slice:]


class Event(Command):
    """
    checks over conditions upon triggers being activated. Useful for common commands and scheduled objects
    """
    # TODO: must add time conditions handler (new 'Scheduled object' class?)
    def __init__(self, commands, modules, triggers, conditions, adminPass=False):
        """
            :param commands: list of functions to be passed the requested modules and run. recommend define with *args
            :param modules: string list of modules to load
            :param triggers: list of Variable objects to listen to. Time objects must be created and then added
            as triggers
            :param conditions: list of python functions that should return True or False when passed ALL loaded modules
            ensure all conditions can take enough variables
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

    def __init__(self, variables=None):
        """
        :param variables: a dictionary object of variable and their keys
        :return:
        """
        if not variables:
            variables = dict()
        self.variables = variables
        self.old_values = {}
        self.update_old_values()

    def update_old_values(self):
        keys = sorted(self.variables.keys())
        for i in range(len(keys)):
            value = int(self.variables[keys[i]])
            self.old_values[keys[i]] = value

    def post(self):
        keys = self.variables.keys()
        for i in range(len(self.variables)):
            if self.old_values[keys[i]] != int(self.variables[keys[i]]):
                self.variables[keys[i]].post()

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
