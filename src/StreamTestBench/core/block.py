# block.py - StreamTestBench - A signal processing block interface

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import StreamTestBench.core.stream as stream


class Block(stream.Listener):
    """ A block has one or more input streams that it processes in some way
     then sends that result to a single output stream.

     A block can be as complex as a filter or pid, or simply a sign inversion or summation.

     result_stream is an empty reference that must be allocated and populated by the
     subclass with the results of the block process.

     testpoints can optionally be used to output intermediary data for
     visualization of the inner workings of the block.
    """

    def __init__(self, block_name='block'):
        """ Block initialization

        The specialized block receives one or more streams on instantiation which it
        must keep references to in order to complete its processing of those streams.

        The block must register its interest in updates to each stream by calling
        that streams add_listener() method with 'self' as its parameter.

        Args:
            block_name: The name of the block used by the gui for annotation
        """

        super().__init__()

        self.block_name = block_name
        self.result_stream = None

        return

    @property
    def name(self):
        """
        Returns:
            (str): The block name.
        """
        return self.block_name

    @property
    def stream(self):
        """
        Returns:
            (Stream): The output or result stream of the process.
        """
        return self.result_stream

    def listener_update(self, stream):
        """ Notification to the block of a change in stream values

        Block delegates processing of the stream by calling the update method of the
        specialized block, then notifies the next block of change by calling the result
        stream's update_listeners() method allowing the change to ripple through the
        signal chain.

        Args:
            stream (Stream): The stream that changed.

        Returns:

        """

        result = self.process(stream)
        result.update_listeners()

        return

    @property
    def testpoints(self):
        """ Optional streams container for process diagnostics

        Returns:
            None: if no test points configured or
            (TestPoints): a testpoints instance containing some number of streams
        """

        return None
    
    def process(self, input_stream):
        """ Called when a stream of interest has changed and processing needs to occur.

        If this block processes a single stream input, the input_stream argument can be used as
        that input. Otherwise, stream references saved during __init__(name, stream, stream, ...)
        should be used, with input_stream optionally serving as an indicator of which stream changed.

        Process results must be stored in result_stream.

        Args:
            input_stream (Stream): The input stream to process

        Returns:
            (Stream): a stream instance containing the results of the process.
        """

        raise NotImplemented
    
