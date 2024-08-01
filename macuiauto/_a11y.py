import fnmatch
import logging

import AppKit
from ApplicationServices import (
    AXIsProcessTrusted,
    AXUIElementCreateApplication,
    AXUIElementCreateSystemWide,
    CFEqual,
)
from macuiauto import _converter
from macuiauto._macos import (
    PAXUIElementCopyActionNames,
    PAXUIElementCopyAttributeNames,
    PAXUIElementCopyAttributeValue,
    PAXUIElementCopyElementAtPosition,
    PAXUIElementGetPid,
    PAXUIElementIsAttributeSettable,
    PAXUIElementPerformAction,
    PAXUIElementSetAttributeValue,
    PAXUIElementSetMessagingTimeout,
)
from macuiauto.errors import (
    AXError,
    AXErrorAPIDisabled,
    AXErrorCannotComplete,
    AXErrorIllegalArgument,
    AXErrorNotImplemented,
    AXErrorNoValue,
    AXErrorUnsupported,
)
from PyObjCTools import AppHelper

logger = logging.getLogger(__name__)


class RunningApplication(object):
    def __init__(self, app_ref):
        self.ref = app_ref

    def process_identifier(self):
        return self.ref.processIdentifier()

    def terminate(self):
        return self.ref.terminate()

    def localized_name(self):
        return self.ref.localizedName()

    def bundle_identifier(self):
        return self.ref.bundleIdentifier()

    def activate_with_options(self, options: int):
        return self.ref.activateWithOptions_(options)


class AXUIElement(object):
    def __init__(self, ref=None):
        self.ref = ref
        self.converter = _converter.Converter(self.__class__)

    def __repr__(self):
        c = repr(self.__class__).partition("<class '")[-1].rpartition("'>")[0]

        for element_describer in ("AXTitle", "AXValue", "AXRoleDescription"):
            title = str(getattr(self, element_describer, ""))
            if title:
                break

        role = getattr(self, "AXRole", "<No role!>")

        return "<%s %s %s>" % (c, role, title)

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        if self.ref is None and other.ref is None:
            return True

        if self.ref is None or other.ref is None:
            return False

        return CFEqual(self.ref, other.ref)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getattr__(self, item):
        if item in self._ax_attributes:
            return self._get_ax_attribute(item)
        elif item in self._ax_actions:

            def perform_ax_action():
                self.perform_ax_action(item)

            return perform_ax_action
        else:
            raise AttributeError(
                "'%s' object has no attribute '%s'" % (type(self), item)
            )

    def __setattr__(self, key, value):
        if key.startswith("AX"):
            try:
                if key in self._ax_attributes:
                    self._set_ax_attribute(key, value)
            except AXErrorIllegalArgument:
                pass
        else:
            super(AXUIElement, self).__setattr__(key, value)

    def __dir__(self):
        return (
            self._ax_attributes
            + self._ax_actions
            + list(self.__dict__.keys())
            + dir(super(AXUIElement, self))  # not working in python 2
        )

    @classmethod
    def _from_bundle_id(cls, bundle_id) -> 'AXUIElement':
        """
        Get the top level element for the application with the specified
        bundle ID, such as com.vmware.fusion.
        """
        apps = running_apps_with_bundle_id(bundle_id)
        if not apps:
            raise ValueError(
                "Specified bundle ID not found in " "running apps: %s" % bundle_id
            )
        return cls._from_pid(apps[0].process_identifier())

    @classmethod
    def _from_localized_name(cls, name) -> 'AXUIElement':
        """Get the top level element for the application with the specified
        localized name, such as VMware Fusion.

        Wildcards are also allowed.
        """
        # Refresh the runningApplications list
        apps = get_running_apps()
        for app in apps:
            if fnmatch.fnmatch(app.localized_name(), name):
                pid = app.process_identifier()
                return cls._from_pid(pid)
        raise ValueError("Specified application not found in running apps.")

    @classmethod
    def _from_pid(cls, pid: int) -> 'AXUIElement':
        """
        Creates an instance with the AXUIElementRef for the application with
        the specified process ID.
        """
        app_ref = AXUIElementCreateApplication(pid)

        return cls(ref=app_ref)

    @classmethod
    def _frontmost(cls) -> 'AXUIElement':
        """
        Creates an instance with the AXUIElementRef for the frontmost application.
        """
        for app in get_running_apps():
            pid = app.process_identifier()
            ref = cls._from_pid(pid)
            try:
                if ref.AXFrontmost:
                    return ref
            except (
                AttributeError,
                AXErrorUnsupported,
                AXErrorCannotComplete,
                AXErrorAPIDisabled,
                AXErrorNotImplemented,
            ):
                # Some applications do not have an explicit GUI
                # and so will not have an AXFrontmost attribute
                # Trying to read attributes from Google Chrome Helper returns
                # ErrorAPIDisabled for some reason - opened radar bug 12837995
                pass
        raise ValueError("No GUI application found.")

    @classmethod
    def _systemwide(cls) -> 'AXUIElement':
        """
        Creates an instance with the AXUIElementRef for the system-wide
        accessibility object.
        """
        app_ref = AXUIElementCreateSystemWide()
        return cls(ref=app_ref)

    @classmethod
    def _with_window(cls) -> 'AXUIElement':
        """
        Creates an instance with the AXUIElementRef for a random application
        that has windows.
        """
        for app in get_running_apps():
            pid = app.process_identifier()
            ref = cls._from_pid(pid)
            if hasattr(ref, "windows") and len(ref.windows()) > 0:
                return ref
        raise ValueError("No GUI application found.")

    @property
    def _ax_actions(self) -> list[str]:
        """Gets the list of actions available on the AXUIElement"""
        try:
            names = PAXUIElementCopyActionNames(self.ref)
            return list(names)
        except AXError:
            return []

    @property
    def _ax_attributes(self) -> list[str]:
        """Gets the list of attributes available on the AXUIElement"""
        try:
            names = PAXUIElementCopyAttributeNames(self.ref)
            return list(names)
        except AXError:
            return []

    @property
    def bundle_id(self) -> str:
        """Gets the AXUIElement's bundle identifier"""
        return self._running_app.bundle_identifier()

    @property
    def pid(self) -> int:
        """Gets the AXUIElement's process ID"""
        pid = PAXUIElementGetPid(self.ref)
        return pid

    @property
    def _running_app(self) -> RunningApplication:
        ra = AppKit.NSRunningApplication
        app = ra.runningApplicationWithProcessIdentifier_(self.pid)
        return RunningApplication(app)

    def _get_element_at_position(self, coord: tuple) -> 'AXUIElement':
        if self.ref is None:
            raise AXErrorUnsupported(
                "Operation not supported on null element references"
            )
        element = PAXUIElementCopyElementAtPosition(self.ref, float(coord[0]), float(coord[1]))

        return self.__class__(element)

    def _set_timeout(self, timeout):
        """
        Sets the timeout value used in the accessibility API

        Args:
            timeout: timeout in seconds
        """
        PAXUIElementSetMessagingTimeout(self.ref, timeout)

    def _activate(self):
        """Activates the application (bringing menus and windows forward)"""
        # NSApplicationActivateAllWindows | NSApplicationActivateIgnoringOtherApps
        # == 3 - PyObjC in 10.6 does not expose these constants though so I have
        # to use the int instead of the symbolic names
        self._running_app.activate_with_options(3)

    def _get_ax_attribute(self, item: str) -> any:
        """Gets the value of the the specified attribute"""
        if item in self._ax_attributes:
            try:
                attr_value = PAXUIElementCopyAttributeValue(self.ref, item)
                return self.converter.convert_value(attr_value)
            except AXErrorNoValue:
                if item == "AXChildren":
                    return []
                return None

        raise AttributeError("'%s' object has no attribute '%s'" % (type(self), item))

    def _set_ax_attribute(self, name: str, value: any):
        """Sets the specified attribute to the specified value"""
        settable = PAXUIElementIsAttributeSettable(self.ref, name)

        if not settable:
            raise AXErrorUnsupported("Attribute is not settable")

        PAXUIElementSetAttributeValue(self.ref, name, value)

    def perform_ax_action(self, name: str):
        """Performs specified action on the AXUIElementRef"""
        PAXUIElementPerformAction(self.ref, name)


def axenabled() -> bool:
    """Return the status of accessibility on the system"""
    return AXIsProcessTrusted()


def get_frontmost_pid() -> int:
    """Return the process ID of the application in the foreground"""
    frontmost_app = AppKit.NSWorkspace.sharedWorkspace().frontmostApplication()
    pid = frontmost_app.process_identifier()
    return pid


def get_running_apps() -> list['RunningApplication']:
    """Get a list of the running applications"""
    AppHelper.callLater(1, AppHelper.stopEventLoop)
    AppHelper.runConsoleEventLoop()
    # Get a list of running applications
    ws = AppKit.NSWorkspace.sharedWorkspace()
    apps = ws.runningApplications()
    app_list = []
    for app in apps:
        app_list.append(RunningApplication(app))
    return app_list


def launch_app_by_bundle_id(bundle_id: str):
    # NSWorkspaceLaunchAllowingClassicStartup does nothing on any
    # modern system that doesn't have the classic environment installed.
    # Encountered a bug when passing 0 for no options on 10.6 PyObjC.
    ws = AppKit.NSWorkspace.sharedWorkspace()

    r = ws.launchAppWithBundleIdentifier_options_additionalEventParamDescriptor_launchIdentifier_(  # noqa: B950
        bundle_id,
        AppKit.NSWorkspaceLaunchAllowingClassicStartup,
        AppKit.NSAppleEventDescriptor.nullDescriptor(),
        None,
    )
    # On 10.6, this returns a tuple - first element bool result, second is
    # a number. Let's use the bool result.
    if not r[0]:
        raise RuntimeError("Error launching specified application. %s" % str(r))


def launch_app_by_bundle_path(bundle_path: str, arguments=None):
    if arguments is None:
        arguments = []

    bundleUrl = AppKit.NSURL.fileURLWithPath_(bundle_path)
    workspace = AppKit.NSWorkspace.sharedWorkspace()
    configuration = {AppKit.NSWorkspaceLaunchConfigurationArguments: arguments}

    return workspace.launchApplicationAtURL_options_configuration_error_(
        bundleUrl, AppKit.NSWorkspaceLaunchAllowingClassicStartup, configuration, None
    )


def terminate_app_by_bundle_id(bundle_id: str):
    apps = running_apps_with_bundle_id(bundle_id)

    if not apps:
        return False

    return apps[0].terminate()


def terminate_app_by_pid(pid: int):
    apps = get_running_apps()

    for app in apps:
        if pid == app.process_identifier():
            return app.terminate()
    return False


def running_apps_with_bundle_id(bundle_id: str) -> list['RunningApplication']:
    """
    Returns an array of NSRunningApplications, or an empty array if
    no applications match the bundle identifier.
    """
    ra = AppKit.NSRunningApplication
    apps = ra.runningApplicationsWithBundleIdentifier_(bundle_id)
    app_list = []
    for app in apps:
        app_list.append(RunningApplication(app))
    return app_list

