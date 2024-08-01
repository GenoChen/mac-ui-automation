import time
from collections import deque
from macuiauto import AXCallbacks
from macuiauto import errors
from macuiauto import _a11y
from macuiauto._converter import *
from macuiauto._mixin import KeyboardMouseMixin, WaitForMixin
import warnings
from typing import Optional, List, Any, Callable, Dict

class NativeUIElement(
    KeyboardMouseMixin, WaitForMixin, _a11y.AXUIElement
):
    """NativeUIElement class - expose the accessibility API in the simplest,
    most natural way possible.
    """

    def __init__(self, ref=None):
        self._last_method: Optional[Callable[..., Optional[Any]]] = None
        self._last_kwargs: Optional[Dict[str, Any]] = None
        self._last_result: Optional[Any] = None
        super(NativeUIElement, self).__init__(ref=ref)
        self.eventList = deque()

    def __getattr__(self, name):
        """Handle attribute requests in several ways:

        1. If it starts with AX, it is probably an a11y attribute. Pass
           it to the handler in _a11y which will determine that for sure.
        2. See if the attribute is an action which can be invoked on the
           UIElement. If so, return a function that will invoke the attribute.
        """
        print(name)
        if name not in ['find_first_r', 'find_first']:
            self._last_method = None
            self._last_kwargs = None
            self._last_result = None

        if "AX" + name in self._ax_actions:
            action = super(NativeUIElement, self).__getattr__("AX" + name)

            def perform_specified_action():
                # activate the app before performing the specified action
                self._activate()
                return action()

            return perform_specified_action
        else:
            return super(NativeUIElement, self).__getattr__(name)

    @property
    def title(self) -> str:
        return self.__getattr__('AXTitle')

    @title.setter
    def title(self, new_value):
        self.__setattr__('AXTitle', new_value)

    @property
    def frame(self) -> CGRect:
        return self.__getattr__('AXFrame')

    @property
    def position(self) -> CGPoint:
        return self.__getattr__('AXPosition')

    @property
    def role(self) -> str:
        return self.__getattr__('AXRole')

    @property
    def parent(self) -> Optional['NativeUIElement']:
        return self.__getattr__('AXParent')

    @property
    def size(self) -> CGSize:
        return self.__getattr__('AXSize')

    @property
    def children(self) -> list['NativeUIElement']:
        return self.__getattr__('AXChildren')

    @property
    def enabled(self) -> bool:
        return self.__getattr__('AXEnabled')

    @property
    def description(self) -> str:
        return self.__getattr__('AXDescription')

    @property
    def label(self) -> str:
        warnings.warn(
            f"Please use description instead",
            DeprecationWarning,
            stacklevel=2
        )
        return self.__getattr__('AXDescription')


    @property
    def focused(self) -> bool:
        return self.__getattr__('AXFocused')

    @property
    def value(self) -> str:
        return self.__getattr__('AXValue')

    @value.setter
    def value(self, new_value):
        self.__setattr__('AXValue', new_value)

    @property
    def role_description(self) -> str:
        return self.__getattr__('AXRoleDescription')

    @property
    def window(self) -> Optional['NativeUIElement']:
        return self.__getattr__('AXWindow')

    def press(self):
        if "Press" in self._ax_actions:
            return super(NativeUIElement, self).perform_ax_action("Press")

    def show_menu(self):
        if "ShowMenu" in self._ax_actions:
            return super(NativeUIElement, self).perform_ax_action("ShowMenu")

    @classmethod
    def get_app_ref_by_pid(cls, pid) -> Optional['NativeUIElement']:
        """Get the top level element for the application specified by pid."""
        return cls._from_pid(pid)

    @classmethod
    def get_app_ref_by_bundle_id(cls, bundle_id: str) -> Optional['NativeUIElement']:
        """
        Get the top level element for the application with the specified
        bundle ID, such as com.vmware.fusion.
        """
        return cls._from_bundle_id(bundle_id)

    @classmethod
    def get_app_ref_by_localized_name(cls, name: str) -> Optional['NativeUIElement']:

        """Get the top level element for the application with the specified
        localized name, such as VMware Fusion.

        Wildcards are also allowed.
        """
        # Refresh the runningApplications list
        return cls._from_localized_name(name)

    @classmethod
    def get_frontmost_app(cls) -> Optional['NativeUIElement']:
        """Get the current frontmost application.

        Raise a ValueError exception if no GUI applications are found.
        """
        # Refresh the runningApplications list
        return cls._frontmost()

    @classmethod
    def get_any_app_with_window(cls) -> Optional['NativeUIElement']:
        """Get a random app that has windows.

        Raise a ValueError exception if no GUI applications are found.
        """
        # Refresh the runningApplications list
        return cls._with_window()

    @classmethod
    def get_system_object(cls) -> Optional['NativeUIElement']:
        """Get the top level system accessibility object."""
        return cls._systemwide()

    @classmethod
    def set_system_wide_timeout(cls, timeout=0.0):
        """Set the system-wide accessibility timeout.

        Args:
            timeout: non-negative float. 0 will reset to the system default.

        Returns:
            None

        """
        return cls.set_systemwide_timeout(timeout)

    @staticmethod
    def launch_app_by_bundle_id(bundle_id: str):
        """Launch the application with the specified bundle ID"""
        # NSWorkspaceLaunchAllowingClassicStartup does nothing on any
        # modern system that doesn't have the classic environment installed.
        # Encountered a bug when passing 0 for no options on 10.6 PyObjC.
        _a11y.launch_app_by_bundle_id(bundle_id)

    @staticmethod
    def launch_app_by_bundle_path(bundle_path: str, arguments=None):
        """Launch app with a given bundle path.

        Return True if succeed.
        """
        return _a11y.launch_app_by_bundle_path(bundle_path, arguments)

    @staticmethod
    def terminate_app_by_bundle_id(bundle_id: str):
        """Terminate app with a given bundle ID.
        Requires 10.6.

        Return True if succeed.
        """
        return _a11y.terminate_app_by_bundle_id(bundle_id)

    @classmethod
    def set_systemwide_timeout(cls, timeout=0.0):
        """Set the system-wide accessibility timeout.

        Args:
            timeout: A value of 0 will reset the timeout to the system default.
        """
        return cls.systemwide().setTimeout(timeout)

    def set_timeout(self, timeout=0.0):
        """Set the accessibiltiy API timeout on the given reference.

        Args:
            timeout: A value of 0 will reset the timeout to the systemwide value
        """
        self._set_timeout(timeout)

    def get_attributes(self) -> list[str]:
        """Get a list of the attributes available on the element."""
        return self._ax_attributes

    def get_actions(self) -> list[str]:
        """Return a list of the actions available on the element."""
        actions = self._ax_actions
        # strip leading AX from actions - help distinguish them from attributes
        return [action[2:] for action in actions]

    def set_string(self, attribute, string):
        """Set the specified attribute to the specified string."""
        return self.__setattr__(attribute, str(string))

    def get_element_at_position(self, coord: tuple) -> Optional['NativeUIElement']:
        """Return the AXUIElement at the given coordinates.

        If self is behind other windows, this function will return self.
        """
        return self._get_element_at_position(coord)

    def activate(self):
        """Activate the application (bringing menus and windows forward)"""
        return self._activate()

    def get_application(self) -> Optional['NativeUIElement']:
        """Get the base application UIElement.

        If the UIElement is a child of the application, it will try
        to get the AXParent until it reaches the top application level
        element.
        """
        app = self
        while "AXParent" in app._ax_attributes:
            app = app.AXParent
        return app

    def menu_item(self, *args) -> Optional['NativeUIElement']:
        """Return the specified menu item.

        Example - refer to items by name:

        app.menuItem('File', 'New').Press()
        app.menuItem('Edit', 'Insert', 'Line Break').Press()

        Refer to items by index:

        app.menuitem(1, 0).Press()

        Refer to items by mix-n-match:

        app.menuitem(1, 'About TextEdit').Press()
        """
        menuitem = self.get_application().AXMenuBar
        return self._menu_item(menuitem, *args)

    def pop_up_item(self, *args) -> Optional['NativeUIElement']:
        """Return the specified item in a pop up menu."""
        self.Press()
        time.sleep(0.5)
        return self._menu_item(self, *args)

    def get_bundle_id(self) -> str:
        """Return the bundle ID of the application."""
        return self.bundle_id

    def get_localized_name(self) -> str:
        """Return the localized name of the application."""
        return self.get_application().AXTitle

    '''
    Search 
    '''
    def _generate_children(self, target=None, recursive=False) -> List['NativeUIElement']:
        """Generator which yields all AXChildren of the object."""
        if target is None:
            target = self

        try:
            children = target.children
        except (AttributeError, errors.AXError):
            return

        for child in children:
            yield child
            if recursive:
                for c in self._generate_children(child, recursive):
                    yield c

    def _find_all(self, recursive=False, **kwargs) -> List['NativeUIElement']:
        """Return a list of all children that match the specified criteria."""
        return filter(
            AXCallbacks.match_filter(**kwargs),
            self._generate_children(recursive=recursive),
        )

    def _find_first(self, recursive=False, **kwargs) -> Optional['NativeUIElement']:
        """Return the first object that matches the criteria."""
        for item in self._find_all(recursive=recursive, **kwargs):
            return item

    def find_first(self, **kwargs) -> Optional['NativeUIElement']:
        """Return the first object that matches the criteria."""
        return self._find_first(**kwargs)

    def find_first_r(self, **kwargs) -> Optional['NativeUIElement']:
        """Search recursively for the first object that matches the
        criteria.
        """
        self._last_method = self._find_first
        self._last_kwargs = kwargs
        self._last_result = self._find_first(recursive=True, **kwargs)
        return self._last_result

    def find_all(self, **kwargs) -> List['NativeUIElement']:
        """Return a list of all children that match the specified criteria."""
        return list(self._find_all(**kwargs))

    def find_all_r(self, **kwargs) -> List['NativeUIElement']:
        """Return a list of all children (recursively) that match
        the specified criteria.
        """
        return list(self._find_all(recursive=True, **kwargs))

    def _convenience_match(self, role, attr, match) -> List['NativeUIElement']:
        """Method used by role based convenience functions to find a match"""
        kwargs = {}
        # If the user supplied some text to search for,
        # supply that in the kwargs
        if match:
            kwargs[attr] = match
        return self.find_all(AXRole=role, **kwargs)

    def _convenience_match_r(self, role, attr, match) -> List['NativeUIElement']:
        """Method used by role based convenience functions to find a match"""
        kwargs = {}
        # If the user supplied some text to search for,
        # supply that in the kwargs
        if match:
            kwargs[attr] = match
        return self.find_all_r(AXRole=role, **kwargs)

    def text_areas(self, match=None) -> List['NativeUIElement']:
        """Return a list of text areas with an optional match parameter."""
        return self._convenience_match("AXTextArea", "AXTitle", match)

    def text_areas_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of text areas with an optional match parameter."""
        return self._convenience_match_r("AXTextArea", "AXTitle", match)

    def text_fields(self, match=None) -> List['NativeUIElement']:
        """Return a list of textfields with an optional match parameter."""
        return self._convenience_match("AXTextField", "AXRoleDescription", match)

    def text_fields_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of textfields with an optional match parameter."""
        return self._convenience_match_r("AXTextField", "AXRoleDescription", match)

    def buttons(self, match=None) -> List['NativeUIElement']:
        """Return a list of buttons with an optional match parameter."""
        return self._convenience_match("AXButton", "AXTitle", match)

    def buttons_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of buttons with an optional match parameter."""
        return self._convenience_match_r("AXButton", "AXTitle", match)

    def windows(self, match=None) -> list['NativeUIElement']:
        """Return a list of windows with an optional match parameter."""
        return self._convenience_match("AXWindow", "AXTitle", match)

    def windows_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of windows with an optional match parameter."""
        return self._convenience_match_r("AXWindow", "AXTitle", match)

    def sheets(self, match=None) -> List['NativeUIElement']:
        """Return a list of sheets with an optional match parameter."""
        return self._convenience_match("AXSheet", "AXDescription", match)

    def sheets_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of sheets with an optional match parameter."""
        return self._convenience_match_r("AXSheet", "AXDescription", match)

    def static_texts(self, match=None) -> List['NativeUIElement']:
        """Return a list of statictexts with an optional match parameter."""
        return self._convenience_match("AXStaticText", "AXValue", match)

    def static_texts_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of statictexts with an optional match parameter"""
        return self._convenience_match_r("AXStaticText", "AXValue", match)

    def generic_elements(self, match=None) -> List['NativeUIElement']:
        """Return a list of genericelements with an optional match parameter."""
        return self._convenience_match("AXGenericElement", "AXValue", match)

    def generic_elements_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of genericelements with an optional match parameter."""
        return self._convenience_match_r("AXGenericElement", "AXValue", match)

    def groups(self, match=None) -> List['NativeUIElement']:
        """Return a list of groups with an optional match parameter."""
        return self._convenience_match("AXGroup", "AXRoleDescription", match)

    def groups_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of groups with an optional match parameter."""
        return self._convenience_match_r("AXGroup", "AXRoleDescription", match)

    def radio_buttons(self, match=None) -> List['NativeUIElement']:
        """Return a list of radio buttons with an optional match parameter."""
        return self._convenience_match("AXRadioButton", "AXTitle", match)

    def radio_buttons_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of radio buttons with an optional match parameter."""
        return self._convenience_match_r("AXRadioButton", "AXTitle", match)

    def pop_up_buttons(self, match=None) -> List['NativeUIElement']:
        """Return a list of popup menus with an optional match parameter."""
        return self._convenience_match("AXPopUpButton", "AXTitle", match)

    def pop_up_buttons_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of popup menus with an optional match parameter."""
        return self._convenience_match_r("AXPopUpButton", "AXTitle", match)

    def rows(self, match=None) -> List['NativeUIElement']:
        """Return a list of rows with an optional match parameter."""
        return self._convenience_match("AXRow", "AXTitle", match)

    def rows_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of rows with an optional match parameter."""
        return self._convenience_match_r("AXRow", "AXTitle", match)

    def sliders(self, match=None) -> List['NativeUIElement']:
        """Return a list of sliders with an optional match parameter."""
        return self._convenience_match("AXSlider", "AXValue", match)

    def sliders_r(self, match=None) -> List['NativeUIElement']:
        """Return a list of sliders with an optional match parameter."""
        return self._convenience_match_r("AXSlider", "AXValue", match)

    def _menu_item(self, menuitem, *args) -> Optional['NativeUIElement']:
        """Return the specified menu item.

        Example - refer to items by name:

        app._menuItem(app.AXMenuBar, 'File', 'New').Press()
        app._menuItem(app.AXMenuBar, 'Edit', 'Insert', 'Line Break').Press()

        Refer to items by index:

        app._menuitem(app.AXMenuBar, 1, 0).Press()

        Refer to items by mix-n-match:

        app._menuitem(app.AXMenuBar, 1, 'About TextEdit').Press()
        """
        self._activate()
        for item in args:
            # If the item has an AXMenu as a child, navigate into it.
            # This seems like a silly abstraction added by apple's a11y api.
            if menuitem.AXChildren[0].AXRole == "AXMenu":
                menuitem = menuitem.AXChildren[0]
            # Find AXMenuBarItems and AXMenuItems using a handy wildcard
            try:
                menuitem = menuitem.AXChildren[int(item)]
            except ValueError:
                menuitem = menuitem.findFirst(AXRole="AXMenu*Item", AXTitle=item)
        return menuitem

    def wait(self, timeout: int = 30, poll_interval: float = 0.1) -> Optional[Any]:
        """Wait for the last called method to return a non-None result.

        Args:
            timeout (int): Maximum time to wait in seconds.
            poll_interval (float): Time interval between method calls in seconds.

        Returns:
            Optional[Any]: The result of the method call if found within the timeout, otherwise None.
        """
        if self._last_method is None:
            raise ValueError("No method has been called to wait for.")

        start_time = time.time()
        while (time.time() - start_time) < timeout:
            self._last_result = self._last_method(**self._last_kwargs)
            if self._last_result is not None:
                return self._last_result
            time.sleep(poll_interval)
        return None

    def all_values(self):
        print(self.get_attributes())
        for key in self._ax_attributes:
            print(key, self.__getattr__(key))
