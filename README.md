# mac-ui-automation: Automated Testing on macOS
[![license](https://img.shields.io/github/license/daveenguyen/atomacos.svg?style=flat-square)](https://github.com/daveenguyen/atomacos/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/macuiauto.svg?style=flat-square)](https://pypi.org/project/atomacos/)
[![style](https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square)](https://github.com/ambv/black)

This library is a fork of [atomacos].
It was created to provide a release with type hints support because
there has not been a release [since 2024](https://github.com/pyatom/pyatom/releases)

macuiauto is a library to enable GUI testing of macOS applications via the Apple Accessibility API.
macuiauto has direct access to the API via [pyobjc]. It's fast and easy to use to write tests.

# Why macuiauto is needed
In the beginning, I was a fan of atomac, then I found out that it didn't support python3, so I discovered atomacos, thanks to atomacos for adding support for python3.
But when I used Atomacos, I found some inconveniences.
1. The method names of atomacos use camel case naming. If I remember correctly, python should recommend using lowercase and underscores to name methods and variables.
2. atomacos does not support type hints, so I often need to check whether my function name is written correctly. This is critical to development efficiency and development experience.

Based on the above two points, I modified some implementations of atomacos to solve the above two problems



# Getting started
Requirements
- macOS
- [pyobjc]
- Systemwide Accesibility enabled


If you experience issues, please open a ticket in the [issue tracker][issues].

## Enabling Accessibility
Check the checkbox:
```
System Settings > Privacy & Security > Accessibility > [The app that execute the python script]
```

Failure to enable this will result in `AXErrorAPIDisabled` exceptions during some module usage.


## Installing

For release
```bash
$ pip install macuiauto
```

For pre-release
```bash
$ pip install --pre macuiauto
```


# Usage Examples
Once installed, you should be able to use it to launch an application:

```python
>>> import macuiauto
>>> macuiauto.launch_app_by_bundle_id('com.apple.Automator')
```

This should launch Automator.


Next, get a reference to the UI Element for the application itself:

```python
>>> automator = macuiauto.get_app_ref_by_bundle_id('com.apple.Automator')
>>> automator
<macuiauto.AXClasses.NativeUIElement AXApplication Automator>
```


Now, we can find objects in the accessibility hierarchy:

```python
>>> window = macuiauto.windows()[0]
>>> window.title
u'Untitled'
>>> sheet = window.sheets()[0]
```

Note that we retrieved an accessibility attribute from the Window object - `AXTitle`.
macuiauto supports reading and writing of most attributes.
Xcode's included `Accessibility Inspector` can provide a quick way to find these attributes.


There is a shortcut for getting the sheet object which
bypasses accessing it through the Window object.
macuiauto can search all objects in the hierarchy:

```python
>>> sheet = automator.sheets_r()[0]
```


There are search methods for most types of accessibility objects.
Each search method, such as `windows`,
has a corresponding recursive search function, such as `windows_r`.

The recursive search finds items that aren't just direct children, but children of children.
These search methods can be given terms to identify specific elements.
Note that `*` and `?` can be used as wildcard match characters in all search methods:

```python
>>> close = sheet.buttons('Close')[0]
```


There are methods to search for UI Elements that match any number of criteria.
The criteria are accessibility attributes:

```python
>>> close = sheet.find_first(AXRole='AXButton', AXTitle='Close')
```

`find_first` and `find_first_r` return the first item found to match the criteria or `None`.
`find_all` and `find_all_r` return a list of all items that match the criteria or an empty list(`[]`).


Objects are fairly versatile.
You can get a list of supported attributes and actions on an object:

```python
>>> close.get_attributes()
[u'AXRole', u'AXRoleDescription', u'AXHelp', u'AXEnabled', u'AXFocused',
u'AXParent', u'AXWindow', u'AXTopLevelUIElement', u'AXPosition', u'AXSize',
u'AXTitle']
>>> close.title
u'Close'
>>> close.AXTitle
u'Close'
>>> close.get_actions()
[u'Press']
```


Performing an action is as natural as:

```python
>>> close.press()
>>> close.Press()
```

Any action can be triggered this way.



# Links
- [License]
- [Issues]
- [Source] Code
- Changes
    - [Commits] page has all changes to the project.
    - [Release] page will also outline changes
- Thanks [atomacos] [ATOMac] and [PyObjC]


[source]:  https://github.com/GenoChen/macuiauto
[release]: https://github.com/GenoChen/macuiauto/releases
[commits]: https://github.com/GenoChen/macuiauto/commits
[license]: https://github.com/GenoChen/macuiauto/blob/master/LICENSE
[issues]:  https://github.com/GenoChen/macuiauto/issues
[pypi]:    https://pypi.org/project/macuiauto/
[black]:   https://github.com/ambv/black
[atomac]:  https://github.com/pyatom/pyatom
[pyobjc]:  https://bitbucket.org/ronaldoussoren/pyobjc
