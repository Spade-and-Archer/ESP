# noinspection PyPep8
import time
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
            :param triggers: list of Variable objects to listen to
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
    :var self.post: corresponds to post_method will be used to update the variable
    :var self.value: the current value of the object. Will automatically be used in mathematical operations
    :var self.listeners: a list of functions to be called (without post_arguments) when the value changes
    A variable is an integer like object which can be listened to. Variable.listen(function) will cause the execution of
    that function should the variable be modified. For this reason, Variable.set(x) should be used instead of
    Variable.value = x. the value can be any class with numerical operation methods, (e.g. int, float, or any sub-class
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
        if isinstance(other, Variable):
            return self.value + other.value
        return self.value

    def __sub__(self, other):
        if type(other) == int:
            return self.value - other
        if isinstance(other, Variable):
            return self.value - other.value
        return self

    def __mul__(self, other):
        if type(other) == int:
            return self.value * other
        if isinstance(other, Variable):
            return self.value * other.value
        return self

    def __floordiv__(self, other):
        if type(other) == int:
            return self.value // other
        if isinstance(other, Variable):
            return self.value // other.value
        return self

    def __mod__(self, other):
        if type(other) == int:
            return self.value % other
        if isinstance(other, Variable):
            return self.value % other.value
        return self

    def __divmod__(self, other):
        if type(other) == int:
            return divmod(self.value, other)
        if isinstance(other, Variable):
            return divmod(self.value, other.value)
        return self

    def __pow__(self, other, modulo=None):
        if type(other) == int:
            return pow(self.value, other, modulo)
        if isinstance(other, Variable):
            return pow(self.value, other.value)
        return self, modulo

    def __lshift__(self, other):
        if type(other) == int:
            return self.value << other
        if isinstance(other, Variable):
            return self.value << other.value
        return self

    def __rshift__(self, other):
        if type(other) == int:
            return self.value >> other
        if isinstance(other, Variable):
            return self.value >> other.value
        return self

    def __and__(self, other):
        if type(other) == int:
            return self.value & other
        if isinstance(other, Variable):
            return self.value & other.value
        return self

    def __xor__(self, other):
        if type(other) == int:
            return self.value ^ other
        if isinstance(other, Variable):
            return self.value ^ other.value
        return self

    def __or__(self, other):
        if type(other) == int:
            return self.value | other
        if isinstance(other, Variable):
            return self.value | other.value
        return self

    def __div__(self, other):
        if type(other) == int:
            return self.value / other
        if isinstance(other, Variable):
            return self.value / other.value
        return self

    def __truediv__(self, other):
        if type(other) == int:
            return self.value / other
        if isinstance(other, Variable):
            return self.value / other.value
        return self

    def __iadd__(self, other):
        if type(other) == int:
            self.set(self.value + other)
        if isinstance(other, Variable):
            self.set(self.value + other.value)

    def __isub__(self, other):
        if type(other) == int:
            self.set(self.value - other)
        if isinstance(other, Variable):
            self.set(self.value - other.value)

    def __imul__(self, other):
        if type(other) == int:
            self.set(self.value * other)
        if isinstance(other, Variable):
            self.set(self.value * other.value)

    def __idiv__(self, other):
        if type(other) == int:
            self.set(self.value / other)
        if isinstance(other, Variable):
            self.set(self.value / other.value)

    def __itruediv__(self, other):
        if type(other) == int:
            self.set(self.value / other)
        if isinstance(other, Variable):
            self.set(self.value / other.value)

    def __ifloordiv__(self, other):
        if type(other) == int:
            self.set(self.value // other)
        if isinstance(other, Variable):
            self.set(self.value // other.value)

    def __imod__(self, other):
        if type(other) == int:
            self.set(self.value % other)
        if isinstance(other, Variable):
            self.set(self.value % other.value)

    def __ipow__(self, other, modulo=None):
        if type(other) == int:
            self.set(pow(self.value, other, modulo))
        if isinstance(other, Variable):
            self.set(pow(self.value, other.value, modulo))

    def __ilshift__(self, other):
        if type(other) == int:
            self.set(self.value << other)
        if isinstance(other, Variable):
            self.set(self.value << other.value)

    def __irshift__(self, other):
        if type(other) == int:
            self.set(self.value >> other)
        if isinstance(other, Variable):
            self.set(self.value >> other.value)

    def __iand__(self, other):
        if type(other) == int:
            self.set(self.value & other)
        if isinstance(other, Variable):
            self.set(self.value & other.value)

    def __ixor__(self, other):
        if type(other) == int:
            self.set(self.value ^ other)
        if isinstance(other, Variable):
            self.set(self.value ^ other.value)

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __ior__(self, other):
        if type(other) == int:
            self.set(self.value | other)
        if isinstance(other, Variable):
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

        self.postMethod = post_method
        self.postArgs = post_arguments
        self.value = start_state
        self.listeners = []
        start_state = self.convertValue(start_state)

    def convertValue(self, value):
        return value

    def post(self):
        self.postMethod(*self.postArgs)

    def listen(self, alert_function):
        self.listeners.append(alert_function)

    def set(self, value):
        self.value = self.convertValue(value)
        for listener in self.listeners:
            listener()


class RangedVariable(Variable):
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
        Variable.__init__(self, initial, post_method, *post_arguments)

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
        VariableMatrix['Variable'] = x
        same as Variable.set(x)
    can use
        for Variable in VariableMatrix
    can use
        VariableMatrix['new variable'] = Variable(x)
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
        :param variables: dictionary of string keys and Variable values which will be contained in the module
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
