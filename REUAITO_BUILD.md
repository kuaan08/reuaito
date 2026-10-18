# Reuaito

Complete source imported from Player124413/rexauto, commit
dac49b331f2632f0b050f469e35747721300b8b2.

This fork retains the original MIT license, NOTICE, upstream
credits and the independent supporting components. It does not
include commercial Xbox 360 game files, keys or assets.

## Windows EXE

GitHub Actions > Build Reuaito Windows EXE produces the
Reuaito-Windows-x64 artifact containing reuaito.exe.

The executable bundles the Python desktop application and its
WebView frontend. It does NOT bundle the separate native ReXGlue
SDK or Visual Studio C++/LLVM build tools. Configure these
through the application's Setup screen. Successful packaging
is not proof that any commercial Xbox 360 game can run.

Original project: https://github.com/Player124413/rexauto

## Windows recompilation: RC=9009 and missing CMake

If the live pipeline stops at **Recompile** (sometimes around 57%) and
`_build.log` contains:

```text
'cmake' is not recognized as an internal or external command
RC=9009
```

this indicates a **host build tool cannot be executed**, not that a
PowerPC function or game asset was rejected. A separate
`'Fastboot++\\'` command error may indicate that a Windows PATH
entry or the Visual Studio environment script is malformed.

The fork now detects both **CMake** and **Ninja**, shows them in **Setup**,
and resolves absolute executable paths *before* running `vcvars64.bat`.
It passes the verified Ninja path to the CMake preset and aborts
immediately if Visual Studio initialization or CMake configuration fails.

Use **Setup → CMake** and **Setup → Ninja** to install them, or run:

```powershell
winget install --id Kitware.CMake --exact
winget install --id Ninja-build.Ninja --exact
```

Restart the application after installation, then reopen **Setup** and
confirm both are found. If you have unusual tool locations, use the
`CMAKE` and `NINJA` environment variables with full executable paths.
For example, `CMAKE=C:\\Program Files\\CMake\\bin\\cmake.exe`.

The existing title's `default.xex`, files and progress should be
left intact. The pipeline can reuse generated objects if its
configuration remains compatible. A successful native compilation
still does not guarantee the title will boot or render correctly.

