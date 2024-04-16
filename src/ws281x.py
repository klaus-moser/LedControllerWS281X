#!/usr/bin/env python3

# Filename: ws281x.py

"""
RPI WS281X PixelStrip driver.
https://github.com/klaus-moser/LedControllerWS281X

MIT License
Copyright (c) 2024 Klaus Moser

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


import os
import time

__version__ = "0.0.1"
__author__ = "klaus-moser"
__date__ = time.ctime(os.path.getmtime(__file__))


class LedControllerWS281X:
    """
    LedControllerWS281X Class.

    Example:

    oooo   o  oooo  oooo o  o oooo oooo oooo oooo oooo
    o  o   o     o     o o  o o    o       o o  o o  o
    o  o   o     o     o o  o o    o       o o  o o  o
    o  o   o  oooo   ooo oooo oooo oooo    o oooo oooo
    o  o   o  o        o    o    o o  o    o o  o    o
    o  o   o  o        o    o    o o  o    o o  o    o
    o  o   o  o        o    o    o o  o    o o  o    o
    oooo   o  oooo  oooo    o oooo oooo    o oooo oooo
    """

    # class variables
    free    = "00000000"
    dot     = "00010000"
    zero_0  = "11111111100000011000000111111111"
    one_1   = "00000000000000001111111100000000"
    two_2   = "10011111100100011001000111110001"
    three_3 = "10000001100100011001000111111111"
    four_4  = "11110000000100000001000011111111"
    five_5  = "11110001100100011001000110011111"
    six_6   = "11111111100100011001000110011111"
    seven_7 = "10000000100000001000000011111111"
    eight_8 = "11111111100100011001000111111111"
    nine_9  = "11110001100100011001000111111111"

    numbers_dict = {
        ' ': free,
        '0': zero_0,
        '1': one_1,
        '2': two_2,
        '3': three_3,
        '4': four_4,
        '5': five_5,
        '6': six_6,
        '7': seven_7,
        '8': eight_8,
        '9': nine_9
    }

    def __init__(self, rows: int = 8, cols: int = 32):
        self.ROWS = rows
        self.COLS = cols
        self.NUM_LEDS = rows * cols
        self.FIRST_LED = [0]

        try:
            self.__create_first_led_numbers_array()
        except ValueError as err:
            print(err)
            exit(1)

    @staticmethod
    def __is_digit(digit: str) -> bool:
        """
        Check if the ASCII value of the character is between the ASCII values of '0' and '9'.
        Also ignore white spaces.

        @param digit: Digit (char) to be checked.
        @return: Boolean value representing the digit.
        """

        if 48 <= ord(digit) <= 57 or ord(digit) == 32:  # 0-9 or ' ' (white space)
            return True
        else:
            return False

    def __create_first_led_numbers_array(self) -> None:
        """
        Create an array that contains the number of the LED in the first of row.
        This array then initializes the 'FIRST_LED' class variable.

        e.g. row x col: 3 x 4

        cols    1   2   3   4
        rows
        1     | 0 | 5 | 6 | 11 |  <--- FIRST_LED = [0, 5, 6, 11]
        2     | 1 | 4 | 7 | 10 |
        3     | 2 | 3 | 8 | 9 |

        This array is needed to set the right LEDs for the display. If the row is even
        the LED number is counted up, otherwise (odd) the LED number is counted down.

        @return:
        """

        if self.ROWS < 0 or self.COLS < 0:
            raise ValueError("ROWS and COLS cannot be negative")

        elif self.ROWS == 0 or self.COLS == 0:
            raise ValueError("ROWS and COLS must be > 1.")

        i = 0
        while i < self.NUM_LEDS:
            first = i + (2 * self.ROWS) - 1
            i = i + (2 * self.ROWS)
            self.FIRST_LED.append(first)

            if i != self.NUM_LEDS:
                self.FIRST_LED.append(i)

    def __text_to_bit_string(self, text: str) -> list:
        """
        This function takes the input text and converts it to a list of bits by
        replacing the numbers 0-9 with the predefined bit-strings for each number.

        e.g.
        - '0' --> "11111111100000011000000111111111"
        - "11111111100000011000000111111111" --> [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]

        @param text: Input text to be converted to a bit-string.
        @return: List of integers representing the bit-string [0,1].
        """

        bit_string = []
        text_bits = [i for i in text if self.__is_digit(i)]  # e.g. "123 456" --> ['1','2','3',' ','4','5','6']

        for text_bit in text_bits:
            for bit in self.numbers_dict[text_bit]:  # replace string e.g. '1' --> "00000000000000001111111100000000"
                if bit == '0':
                    bit_string.append(0)  # create integer array
                else:
                    bit_string.append(1)

        if len(bit_string) < self.NUM_LEDS:  # string smaller than number of leds
            while len(bit_string) < self.NUM_LEDS:  # fill the rest with '0'
                bit_string.append(0)

        elif len(bit_string) > self.NUM_LEDS:  # string bigger than number of leds
            while len(bit_string) > self.NUM_LEDS:
                bit_string.pop()

        return bit_string  # e.g. [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0]

    @staticmethod
    def __create_columns_array(bit_string: list) -> list:
        """
        Splits the bit string into a list of lists of length=rows.
        This is necessary for the next step: to adapt the numbers to the inverse counting order.

        @param bit_string: List of integers representing the bit-string [0,1].
        @return: List of lists of length=rows.

        e.g.
        '0'

        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0] -->

        [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0]]
        """

        byte_array = []

        i = 0
        tmp = []
        for bit in bit_string:

            if i == 0:  # first row
                tmp.append(int(bit))
                i += 1
            elif i % 8 != 0:  # TODO: make dynamic
                tmp.append(int(bit))
                i += 1
            else:
                byte_array.append(tmp)  # every 'elf.ROWS = rows' bits append sub-list to list
                tmp = [int(bit)]  # reset
                i = 1
        byte_array.append(tmp)  # add last 8 bits

        return byte_array  # e.g. [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[1,1,1,1,1,1,1,1],[0,0,0,0,0,0,0,0]]

    @staticmethod
    def __arrange_array(columns_array: list) -> list:
        """
        Because the counting direction is inverse in any odd column, this function
        adapts the sub-lists in the correct order.

        @param columns_array: List with sub-lists of length=rows.
        @return: Arranged array containing integers [0,1] to display any number.
        """

        arranged_array = []
        columns_array_sorted = []

        for j in range(len(columns_array)):

            if j == 0:  # 0
                columns_array_sorted.append(columns_array[j])

            elif j % 2 != 0:  # 1,3,5,7, ...
                array_inv = columns_array[j][::-1]
                columns_array_sorted.append(array_inv)

            else:  # 2,4,6,8, ...
                columns_array_sorted.append(columns_array[j])

        for arr in columns_array_sorted:  # create one array with integers [0,1].
            for a in arr:
                arranged_array.append(a)

        return arranged_array

    def __print_to_console(self, arranged_array: list) -> None:
        """
        Prints the input text to the console.

        @param arranged_array: Input array to be printed.
        @return:
        """

        for i in range(self.ROWS):
            for j in range(self.COLS):

                if j == 0:
                    led = self.FIRST_LED[j] + i

                elif j % 2 == 0:
                    led = self.FIRST_LED[j] + i

                else:
                    led = self.FIRST_LED[j] - i

                if arranged_array[led] == 0:
                    print(" ", end=" ")
                else:
                    print("1", end=" ")
            print("")

    def run(self, text: str, show: bool = False) -> list:
        """
        Runs the LED controller and returns the result.

        @param text: Text to be converted.
        @param show: If text should be printed out to the console.
        @return: List of integers representing the numbers for the LED dot matrix.
        """

        text_bits = self.__text_to_bit_string(text)  # convert text
        bit_string = self.__create_columns_array(text_bits)  # bit string
        arranged_array = self.__arrange_array(bit_string)  # adapt reverse numbers etc.

        if show:
            self.__print_to_console(arranged_array)

        return arranged_array


if __name__ == "__main__":
    # Example
    e = LedControllerWS281X(cols=49, rows=8)
    e.run(text="0 1 2 3 4 5 6 7 8 9", show=True)
