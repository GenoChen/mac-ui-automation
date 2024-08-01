# mac-ui-automation: Automated Testing on macOS
[![license](https://img.shields.io/github/license/daveenguyen/atomacos.svg?style=flat-square)](https://github.com/daveenguyen/atomacos/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/atomacos.svg?style=flat-square)](https://pypi.org/project/atomacos/)
[![Build Status](https://img.shields.io/travis/daveenguyen/atomacos/master.svg?style=flat-square)](https://travis-ci.org/daveenguyen/atomacos)
[![codecov](https://img.shields.io/codecov/c/github/daveenguyen/atomacos/master.svg?style=flat-square)](https://codecov.io/gh/daveenguyen/atomacos/)
[![style](https://img.shields.io/badge/code%20style-black-black.svg?style=flat-square)](https://github.com/ambv/black)

This library is a fork of [atomacos].
It was created to provide a release with python 3 support because
there has not been a release [since 2013](https://github.com/pyatom/pyatom/releases)

Atomacos is a library to enable GUI testing of macOS applications via the Apple Accessibility API.
Atomacos has direct access to the API via [pyobjc]. It's fast and easy to use to write tests.


# Getting started
Requirements
- macOS
- [pyobjc]
- Systemwide Accesibility enabled

On travis, it's only on 10.11 because we are able to enable accessibility API.

If you experience issues, please open a ticket in the [issue tracker][issues].

## Enabling Systemwide Accessibility
Check the checkbox:
```
System Preferences > Universal Access > Enable access for assistive devices
System Preferences > Security & Privacy > Privacy > Accessibility
```

Failure to enable this will result in `AXErrorAPIDisabled` exceptions during some module usage.


## Installing

For release
```bash
$ pip install atomacos
```

For pre-release
```bash
$ pip install --pre atomacos
```


# Usage Examples
Once installed, you should be able to use it to launch an application:

```python
>>> import atomacos
>>> atomacos.launchAppByBundleId('com.apple.Automator')
```

This should launch Automator.


Next, get a reference to the UI Element for the application itself:

```python
>>> automator = atomacos.getAppRefByBundleId('com.apple.Automator')
>>> automator
<atomacos.AXClasses.NativeUIElement AXApplication Automator>
```


Now, we can find objects in the accessibility hierarchy:

```python
>>> window = automator.windows()[0]
>>> window.AXTitle
u'Untitled'
>>> sheet = window.sheets()[0]
```

Note that we retrieved an accessibility attribute from the Window object - `AXTitle`.
Atomacos supports reading and writing of most attributes.
Xcode's included `Accessibility Inspector` can provide a quick way to find these attributes.


There is a shortcut for getting the sheet object which
bypasses accessing it through the Window object.
Atomacos can search all objects in the hierarchy:

```python
>>> sheet = automator.sheetsR()[0]
```


There are search methods for most types of accessibility objects.
Each search method, such as `windows`,
has a corresponding recursive search function, such as `windowsR`.

The recursive search finds items that aren't just direct children, but children of children.
These search methods can be given terms to identify specific elements.
Note that `*` and `?` can be used as wildcard match characters in all search methods:

```python
>>> close = sheet.buttons('Close')[0]
```


There are methods to search for UI Elements that match any number of criteria.
The criteria are accessibility attributes:

```python
>>> close = sheet.findFirst(AXRole='AXButton', AXTitle='Close')
```

`findFirst` and `findFirstR` return the first item found to match the criteria or `None`.
`findAll` and `findAllR` return a list of all items that match the criteria or an empty list(`[]`).


Objects are fairly versatile.
You can get a list of supported attributes and actions on an object:

```python
>>> close.getAttributes()
[u'AXRole', u'AXRoleDescription', u'AXHelp', u'AXEnabled', u'AXFocused',
u'AXParent', u'AXWindow', u'AXTopLevelUIElement', u'AXPosition', u'AXSize',
u'AXTitle']
>>> close.AXTitle
u'Close'
>>> close.getActions()
[u'Press']
```


Performing an action is as natural as:

```python
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
- Thanks [ATOMac] and [PyObjC]


[source]:  https://github.com/daveenguyen/atomacos
[release]: https://github.com/daveenguyen/atomacos/releases
[commits]: https://github.com/daveenguyen/atomacos/commits
[license]: https://github.com/daveenguyen/atomacos/blob/master/LICENSE
[issues]:  https://github.com/daveenguyen/atomacos/issues
[pypi]:    https://pypi.org/project/atomacos/
[travis]:  https://travis-ci.org/daveenguyen/atomacos
[codecov]: https://codecov.io/gh/daveenguyen/atomacos/
[black]:   https://github.com/ambv/black
[atomac]:  https://github.com/pyatom/pyatom
[pyobjc]:  https://bitbucket.org/ronaldoussoren/pyobjc
