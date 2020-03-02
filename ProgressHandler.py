#!/usr/bin/env python3
"""
A StreamHandler for the logging module that supports progress indicators.

Based on Ethan Furman's answer at
https://stackoverflow.com/questions/3118059/how-to-write-custom-python-logging-handler
"""

import logging
import curses.ascii

class ProgressHandler(logging.StreamHandler):
    """
    A logging console handler that supports staying on the same line, as well as
    going back to redraw lines.

    The handler supports two 'extra' attributes:

        - same_line     If set, no terminator will be added at the end of the
                        line.
        - overwrite     If set, the cursor will be rewound to the start of the
                        message, allowing the message to be overwritten. This is
                        useful for drawing progress bar backgrounds.
    """

    on_same_line = False
    overwriting = False
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            same_line = hasattr(record, 'same_line')
            overwrite = hasattr(record, 'overwrite')

            # Add an endline character if we start a new line, and we're in
            # same-line-mode
            if self.on_same_line and not (same_line or self.overwriting):
                stream.write(self.terminator)

            # If we're writing on the same line, only write the message and not
            # the context information
            if self.on_same_line:
                msg = record.getMessage()

            # Write the actual message
            stream.write(msg)

            # if it's in overwrite mode, rewind the cursor over the message
            if overwrite:
                stream.write(('%c' % curses.ascii.BS ) * len(record.getMessage()))
                self.overwriting = True
            else:
                self.overwriting = False

            # remember if the next message is to go on the same line
            if same_line or overwrite:
                self.on_same_line = True
            # end the line if the next message doesn't go on the same line
            else:
                stream.write(self.terminator)
                self.on_same_line = False
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

if __name__ == '__main__':

    import time

    progress_handler = ProgressHandler()

    logging.basicConfig(level=logging.DEBUG, handlers=[progress_handler])

    logging.info("Regular message")
    logging.info("Messages on the same line: ", extra={'same_line':True})


    for i in range(5):
        logging.info('%i ', i, extra={'same_line':True})
        time.sleep(.2)

    logging.info("A regular message automatically adds a trailing newline")

    logging.info("This message can be overwritten", extra={'overwrite':True})

    time.sleep(1)

    logging.info("Now the message has been replaced")
    logging.info("Progress: [", extra={'same_line':True})
    logging.info("                                        ]",
                 extra={'overwrite':True, 'same_line':True})

    for i in range(40):
        logging.info('=', extra={'same_line':True})
        time.sleep(.1)

    logging.info("DONE")
