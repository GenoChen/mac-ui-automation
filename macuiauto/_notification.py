import logging
import signal
import threading
import time

from ApplicationServices import AXObserverGetRunLoopSource, NSDefaultRunLoopMode
from macuiauto._macos import (
    PAXObserverAddNotification,
    PAXObserverCallback,
    PAXObserverCreate,
    PAXObserverRemoveNotification,
)
from CoreFoundation import CFRunLoopAddSource, CFRunLoopGetCurrent
from PyObjCTools import AppHelper

try:
    from PyObjCTools import MachSignals
except ImportError:

    class MachSignals:
        signal = signal.signal


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _sigHandler(sig):
    AppHelper.stopEventLoop()
    raise KeyboardInterrupt("Keyboard interrupted Run Loop")


class Observer:
    def __init__(self, uielement=None):
        self.ref = uielement
        self.callback = None
        self.callback_result = None

    def wait_for(self, notification=None, filter_=None, timeout=5):
        self.callback_result = None

        @PAXObserverCallback
        def _callback(observer, element, notification, refcon):
            logger.debug("CALLBACK")
            logger.debug("%s, %s, %s, %s" % (observer, element, notification, refcon))
            ret_element = self.ref.__class__(element)
            if filter_(ret_element):
                self.callback_result = ret_element

        observer = PAXObserverCreate(self.ref.pid, _callback)

        PAXObserverAddNotification(
            observer, self.ref.ref, notification, id(self.ref.ref)
        )

        # Add observer source to run loop
        CFRunLoopAddSource(
            CFRunLoopGetCurrent(),
            AXObserverGetRunLoopSource(observer),
            NSDefaultRunLoopMode,
        )

        def event_stopper():
            end_time = time.time() + timeout
            while time.time() < end_time:
                if self.callback_result is not None:
                    break
            AppHelper.callAfter(AppHelper.stopEventLoop)

        event_watcher = threading.Thread(target=event_stopper)
        event_watcher.daemon = True
        event_watcher.start()

        # Set the signal handlers prior to running the run loop
        oldSigIntHandler = MachSignals.signal(signal.SIGINT, _sigHandler)
        AppHelper.runConsoleEventLoop()
        MachSignals.signal(signal.SIGINT, oldSigIntHandler)

        PAXObserverRemoveNotification(observer, self.ref.ref, notification)

        return self.callback_result
