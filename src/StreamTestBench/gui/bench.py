# bench.py A container for shelves of instruments of a virtual testbench

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import warnings as warnings
import matplotlib.pyplot as plt

import matplotlib.lines as lines
from matplotlib.backend_tools import ToolBase

import StreamTestBench.core.stream as stream


with warnings.catch_warnings():  # suppress 'experimental api' warning
    warnings.simplefilter("ignore")
    plt.rcParams['toolbar'] = 'toolmanager'


class ResetButton(ToolBase):
    default_keymap = 'm'  # keyboard shortcut
    # description = 'Reload'

    def __init__(self, toolmanager, name):
        super().__init__(toolmanager, name)

        self.handlers = []
        return

    def trigger(self, *args, **kwargs):
        self.reset(None)
        return

    def reset(self, event):
        print('reset')
        for handler in self.handlers:
            handler()
        return

    def on_reset(self, handler):
        print('appending callable')
        self.handlers.append(handler)
        return


class Bench(object):
    """
    Bench object.  The primary gui container for all components associated with a test.

    StreamTestBench uses a shelf and panel model for layout of a TestBench.  Any object with
    a visual element to be placed on the bench must be derived from a Panel class.  Objects
    created from those Panels are appended to shelves, which are then appended to a Bench object.
    The final viewable is then assembled as a left to right, top to bottom grid of panels when
    the bench is activated.
    """
    def __init__(self, name):
        self.name = name
        self.shelves = []

        # with enough mips, set layout to constrained for prettier layout
        layout = 'none'
        # layout='constrained'

        # setting num puts name in window top bar
        self.figure = plt.figure(layout=layout, num=name)

        # add reset button to toolbar
        self.figure.canvas.manager.toolmanager.add_tool('Reset', ResetButton)
        self.reset_button = self.figure.canvas.manager.toolmanager.get_tool('Reset')
        self.figure.canvas.manager.toolbar.add_tool(self.reset_button, "stream")

        return

    def __len__(self):
        return len(self.shelves)

    def append(self, shelf):
        """ append a virtual shelf to the test bench.

        Args:
            shelf (Shelf): the shelf to add

        Returns:

        """
        self.shelves.append(shelf)
        return

    def activate(self, name):
        """ Activate the test bench.

        Draws each shelf and its panels.  A bench is only activated once after
        all items have been appended.  Once activated, the user can then
        interact with the controls of the various panels

        Args:
            name:

        Returns:

        """
        self.figure.suptitle(name)
        
        shelf_count = len(self.shelves)
        figs = self.figure.subfigures(nrows=shelf_count, ncols=1)
        
        for i in range(0, shelf_count):
            fig = figs[i]
            self.shelves[i].place_on(fig)
            fig.add_artist(lines.Line2D([0, 1], [0.01, 0.01], color='0.75'))

        plt.show()

        return

    def on_reset(self, handler):
        """ Add a handler to the reset button event

        Args:
            handler: the function to call on reset button event

        Returns:

        """
        self.reset_button.on_reset(handler)
        return


class Shelf(object):
    """
    A container for a row of Panel objects.
    """
    def __init__(self, name, height):
        self.name = name
        self.height = height
        
        self.panels = []

        return

    def __len__(self):
        return len(self.panels)
    
    def append(self, panel, width=1):
        """ Append a panel to this shelf.

        Args:
            panel (Panel): The panel of a virtual instrument to be appended
            width (float): The relative width of this panel in relation to the
                        sum of all panels widths on this shelf

        Returns:

        """
        panel.width = width
        self.panels.append(panel)
        
        return

    def place_on(self, figure):
        """ request from Bench to build and place the shelf on the supplied figure

        Args:
            figure (Figure): matplotlib Figure object to draw shelf on.

        Returns:

        """
        panel_count = len(self.panels)

        width_ratios = [0] # allocate title entry
        total_width = 0
        for panel in self.panels:
            width_ratios.append(panel.width)
            total_width += panel.width 

        width_ratios[0] = total_width / 20 # insert real title width
        
        figs = figure.subfigures(nrows=1, ncols=panel_count+1,
                                 width_ratios=width_ratios)

        fig = figs[0]
        fig.set_facecolor('0.75')
        fig.text(0.5,0.5, self.name, size='large', rotation=90,
                 horizontalalignment='center', verticalalignment='center')
        
        for i in range(0, panel_count):
            fig = figs[i+1]
            self.panels[i].place_on(fig)

        return


class Panel(stream.Listener):
    """
    The Panel is the basic building block of a bench.  It contains the
    various widgets and plots of a virtual instrument. Any object to be
    placed on a Bench should be derived from a Panel.
    """
    def __init__(self):
        super().__init__()
        self._width = 1.0
        return

    @property
    def width(self):
        """The relative width of this panel in relation to the sum of
        the widths of all panels in the same shelf
        """
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        return

    def place_on(self, figure):
        """ request from Shelf to build and place the panel on the supplied figure

        Args:
            figure (Figure): matplotlib Figure object to draw the panel on.

        Returns:

        """
        raise NotImplemented

    def listener_update(self, stream):
        result_stream = self.update(stream)
        # result_stream.update_listeners(result_stream) # panel is sink only

        return

    def update(self, stream):
        """ process an updated data stream

        Args:
            stream (Stream): The Stream or Parameter that has changed.
        """
        raise NotImplemented


class BlankPanel(Panel):
    """
    A blank filler panel for spacing compensation
    """
    def place_on(self, figure):
        return
