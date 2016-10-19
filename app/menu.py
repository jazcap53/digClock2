from __future__ import print_function
import time
import menu_data
# TODO: import subprocess, use
# TODO: rows, columns = subprocess.popen('stty size', 'r').read().split()
# TODO: to get terminal window size

# TODO: find out how to close subprocess after CycleMenus completes


# TODO: update docstrings throughout this file
def clear_screen():
    """
    Using this function because calling os.system('clear') inserts
    multiple blank lines into the output of unit tests.
    :return: None
    """
    print('\n' * 45)


class CycleMenus(object):

    def __init__(self):
        self.chosen = []  # holds selections from all menus
        self.this_menu = None

    def cycle(self):
        """
        Calls run() for each menu in turn.
        :return: the collected user choices for the menus run
        Called by: DigClock.run_clock()
        """
        for m in menu_data.menu_list:
            self.this_menu = Menu(m, self.chosen, menu_data.header,
                                  menu_data.message, menu_data.footer, self.send_choice)
            # read and display menu, get and validate selection
            self.this_menu.run()
        clear_screen()
        for item in self.chosen:  # self.chosen is empty for first menu
            print('Your {}: {}'.format(item[0], item[2]))
        _ = raw_input('\n\nPress \'Enter\' to start clock...')
        # TODO: replace with callback in DigClock?
        return self.chosen  # to DigClock.set_menu_option()

    def send_choice(self, choice):
        """
        Callback handed to Menu object.
        Retrieves the user's menu selection.
        :param choice:
        :return: None
        """
        self.chosen.append(choice)


# TODO: prepend '_' to 'private' data member names ?
class Menu(object):
    """
    Class provided: an interactive menu presented to user
    The menu shows options (with the default option marked by an
    asterisk) and gets the user's choice.
    Instantiated by global function cycle_menus()
    """
    def __init__(self, source, chosen, headr, msg, footr, send_choice):
        self.source = source
        self.header = headr
        self.message = msg
        self.footer = footr
        self.description = None
        self.entries = [('', '', '')]  # make self.entries 1-indexed
        self.default = None
        self.selection = None
        self.reformatted_selection = None
        self.bad_combinations = menu_data.bad_combinations
        self.chosen = chosen[:]  # TODO: comment on why [:] is necessary
        self.err_msg = None
        self.send_choice = send_choice

    def run(self):
        """
        Calls subroutines that:
            read and display the current menu
            get and validate the user response
            reformat that response
            send response back to CycleMenus object
        Called by: CycleMenus.cycle()
        """
        self.read()
        self.display()
        self.get_valid_selection()
        self.reformat_selection(self.selection)
        # callback sends reformatted selection back to CycleMenus object
        self.send_choice(self.reformatted_selection)

    def read(self):
        """
        Reads the menu data
        Called by: self.run()
        """
        for ix, item in enumerate(self.source):
            if ix == 0:
                self.description = item[:]
            else:
                self.entries.append(item[:])
                # remove trailing ' (*)' from default selection
                if item[1] and item[1].endswith(' (*)'):
                    self.default = list(item)
                    self.default[1] = self.default[1].rstrip(' ()*')

    def display(self):
        """
        Present current menu to the user.
        Called by: self.run()
        """
        clear_screen()
        print(self.header + '\n')
        print(self.message + self.description + ':\n')
        for item in self.entries[1:]:
            print('{:2}) {:10}'.format(item[0], item[1]))
        print()
        for item in self.chosen:  # self.chosen is empty for first menu
            print('Your {}: {}'.format(item[0], item[2]))

    def get_valid_selection(self):
        while True:  # loop until user makes a valid selection
            self.get_selection()
            test_1 = self.validate_selection()
            if not test_1:
                self.print_err_msg()
                continue
            test_2 = self.good_combination()
            if not test_2:
                self.print_err_msg()
                continue
            if test_1 and test_2:  # both tests passed
                break
            else:
                self.err_msg = '\n\nINPUT ERROR'
                self.print_err_msg()

    def get_selection(self):
        """
        Get the user selection.
        Called by: self.run()
        """
        self.selection = raw_input('\n\n' + self.footer + ' ')

    def validate_selection(self):
        """
        Checks that user input represents an integer in the correct
        range, or is a null string.
        :return: True on good input
                 False otherwise
        Called by: self.run()
        """
        menu_len = len(self.entries)
        ret = False
        self.selection = self.selection.strip()
        if self.selection:
            try:
                sel_as_int = int(self.selection)
                if 0 < sel_as_int < menu_len:
                    ret = True
                else:
                    self.err_msg = '\n\nSorry. Value entered is out of range.'
            except ValueError:  # input is not an integer
                self.err_msg = '\n\nPlease input an integer value'
        else:
            ret = True  # empty string is a valid input
        return ret

    def good_combination(self):
        """
        Checks for validity of *combinations* of selections.
        :return: True if combination of inputs so far is valid
                 False otherwise
        """
        if not self.selection:  # self.selection has already been strip()ped
            new_value = self.get_current_default()
        else:
            selection_int = int(self.selection)
            new_value = int(self.entries[selection_int][0])
        choices_so_far = [int(item[1]) for item in self.chosen]
        choices_so_far.append(new_value)
        choices_tuple = tuple(choices_so_far)
        if choices_tuple in self.bad_combinations:
            # get error message corresponding to this bad combination
            self.err_msg = self.bad_combinations[choices_tuple]
            return False
        return True

    def get_current_default(self):
        return int(self.default[0])

    def print_err_msg(self):
        """
        Called by: self.run()
        """
        print('\033[41m')  # red background
        print(self.err_msg)
        time.sleep(2)
        print('\033[40m')  # black background

    # TODO: clarify this code
    def reformat_selection(self, selected):
        """
        Reformat option selected by user
        :param selected: a string holding the user's choice (e.g., '3')
                         -- may be '' to represent the default option
        :return:
        Called by: self.run()
        """
        # self.description is a string describing the current menu
        # e.g., 'text color'
        if selected:
            self.reformatted_selection = [self.description]
            # self.entries is a list of tuples
            # each tuple holds strings
            for ix, entry in enumerate(self.entries[int(selected)]):
                # replace the trailing ' (*)' in the default selection
                if ix == 1 and '*' in entry:
                    short_entry = entry.rstrip(' ()*')
                    self.reformatted_selection += [short_entry]
                else:
                    self.reformatted_selection += [entry]
        else:
            self.reformatted_selection = [self.description] + self.default


if __name__ == '__main__':
    c = CycleMenus()
    c.cycle()
