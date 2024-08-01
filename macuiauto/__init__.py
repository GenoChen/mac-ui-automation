"""Automated Testing on macOS"""
# flake8: noqa: F401
__version__ = "3.2.0"

from macuiauto import _a11y, errors
from macuiauto.AXClasses import NativeUIElement
from pynput import keyboard

Key = keyboard.Key
Error = errors.AXError
ErrorAPIDisabled = errors.AXErrorAPIDisabled
ErrorInvalidUIElement = errors.AXErrorInvalidUIElement
ErrorCannotComplete = errors.AXErrorCannotComplete
ErrorUnsupported = errors.AXErrorUnsupported
ErrorNotImplemented = errors.AXErrorNotImplemented

#
# get_app_ref_by_localized_name = NativeUIElement.getAppRefByLocalizedName
# terminate_app_by_bundle_id = NativeUIElement.terminateAppByBundleId
# launch_app_by_bundle_path = NativeUIElement.launchAppByBundlePath
# set_system_wide_timeout = NativeUIElement.setSystemWideTimeout
# get_app_ref_by_bundle_id = NativeUIElement.getAppRefByBundleId
# launch_app_by_bundle_id = NativeUIElement.launchAppByBundleId
# get_frontmost_app = NativeUIElement.getFrontmostApp
get_app_ref_by_pid = NativeUIElement.get_app_ref_by_pid
get_app_ref_by_bundle_id = NativeUIElement.get_app_ref_by_bundle_id
get_running_apps = _a11y.get_running_apps
launch_app_by_bundle_id = _a11y.launch_app_by_bundle_id
launch_app_by_bundle_path = _a11y.launch_app_by_bundle_path
terminate_app_by_bundle_id = _a11y.terminate_app_by_bundle_id
terminate_app_by_pid = _a11y.terminate_app_by_pid
running_apps_with_bundle_id = _a11y.running_apps_with_bundle_id


