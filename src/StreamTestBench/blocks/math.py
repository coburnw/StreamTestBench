# math.py - StreamTestBench -  basic math signal processsing blocks

# Copyright (c) 2024 Coburn Wightman
# AGPL-3.0-or-later

import numpy as np

import StreamTestBench.core.block as block


class Invert(block.Block):
    """
    Invert the sign of a series of samples
    """
    def __init__(self, result_name, input_stream):
        """
        Args:
            result_name (str): Name of the result stream of this block.
            input_stream (Stream): the stream to process.
        """

        super().__init__('Inverse')  # name of our block

        # allocate and configure an output stream that matches the input
        self.result_stream = input_stream.copy(result_name)
        input_stream.add_listener(self)

        return

    def process(self, input_stream):
        """ Process the input stream, storing result in self.result_stream

        Because this process has only one input, the input_stream is not ambiguous, and
        we can use its data directly.

        Args:
            input_stream (Stream): The stream that has changed and needs to be processed.

        Returns:
            (Stream): The result stream
        """

        # invert a stream
        self.result_stream.samples = -1.0 * input_stream.samples

        return self.result_stream


class Absolute(block.Block):
    """
        Absolute value a series of samples
        """

    def __init__(self, result_name, input_stream):
        """
        Args:
            result_name (str): Name of the result stream of this block.
            input_stream (Stream): the stream to process.
        """

        super().__init__('Absolute')  # name of our block

        self.result_stream = input_stream.copy(result_name)
        input_stream.add_listener(self)

        return

    def process(self, input_stream):
        """ Process the input stream, storing result in self.stream

        Because this process has only one input, the input_stream is not ambiguous, and
        we can use its data directly.

        Args:
            input_stream (Stream): The stream that has changed and needs to be processed.

        Returns:
            (Stream): The result stream
        """

        # convert to absolute values
        self.result_stream.samples = np.absolute(input_stream.samples)

        return self.result_stream


class Multiply(block.Block):
    """
    Find the product of two streams
    """

    def __init__(self, result_name, input_stream_a, input_stream_b):
        """
        Args:
            result_name (str): Name of the result stream of this block.
            input_stream_a (Stream): the stream to process.
            input_stream_b (Stream): the other stream to process.
        """

        super().__init__('Product')  # name of our block

        self.result_stream = input_stream_a.copy(result_name)

        self.input_a = input_stream_a
        self.input_b = input_stream_b
        
        self.input_a.add_listener(self)
        self.input_b.add_listener(self)

        return
    
    def process(self, input_stream):
        """ Process the input streams, storing result in self.stream

        Because this process has two input streams, It is easier to use the saved
        references than peak inside this one to determine which it is.

        Args:
            input_stream (Stream): The stream that has changed and needs to be processed.

        Returns:
            (Stream): The product of the two input stream
        """

        # create a product of the two streams
        self.result_stream.samples = self.input_a.samples * self.input_b.samples
        
        return self.result_stream

class Add(block.Block):
    """
    Find the sum of two streams
    """

    def __init__(self, result_name, input_stream_a, input_stream_b):
        """
        Args:
            result_name (str): Name of the result stream of this block.
            input_stream_a (Stream): the stream to process.
            input_stream_b (Stream): the other stream to process.
        """

        super().__init__('Sum')

        self.result_stream = input_stream_a.copy(result_name)

        self.input_a = input_stream_a
        self.input_b = input_stream_b
        
        self.input_a.add_listener(self)
        self.input_b.add_listener(self)

        return
    
    def process(self, stream):
        # create a sum of the two streams
        self.result_stream.samples = self.input_a.samples + self.input_b.samples
        
        return self.result_stream

