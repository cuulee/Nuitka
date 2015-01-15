#!/usr/bin/env python
#     Copyright 2015, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Python tests originally created or extracted from other peoples work. The
#     parts were too small to be protected.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import os, sys

# Find common code relative in file system. Not using packages for test stuff.
sys.path.insert(
    0,
    os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            ".."
        )
    )
)
from test_common import (
    my_print,
    setup,
    convertUsing2to3,
    compareWithCPython
)

python_version = setup()

search_mode = len( sys.argv ) > 1 and sys.argv[1] == "search"

start_at = sys.argv[2] if len( sys.argv ) > 2 else None

if start_at:
    active = False
else:
    active = True

extra_options = os.environ.get("NUITKA_EXTRA_OPTIONS","")

for filename in sorted(os.listdir( "." )):
    if not os.path.isdir(filename) or filename.endswith(".build"):
        continue

    path = os.path.relpath( filename )

    if not active and start_at in ( filename, path ):
        active = True

    expected_errors = [
        "module_exits", "main_raises", "main_raises2",
        "package_contains_main"
    ]

    # Allowed after Python3, packages need no more "__init__.py"

    if python_version < "3.3":
        expected_errors.append( "package_missing_init" )

    if filename not in expected_errors:
        extra_flags = [ "expect_success" ]
    else:
        extra_flags = [ "expect_failure" ]

    if filename in ( "package_missing_init", "dash_import", "reimport_main" ):
        extra_flags.append( "ignore_stderr" )

    extra_flags.append( "remove_output" )

    # Cannot include the files with syntax errors, these would then become
    # ImportError, but that's not the test. In all other cases, use two
    # step execution, which will not add the program original source to
    # PYTHONPATH.
    if filename != "syntax_errors":
        extra_flags.append("two_step_execution")
    else:
        extra_flags.append("binary_python_path")

    if filename == "plugin_import":
        os.environ[ "NUITKA_EXTRA_OPTIONS" ] = extra_options + \
          " --recurse-all --recurse-directory=%s/some_package" % (
              os.path.abspath( filename )
          )
    else:
        os.environ[ "NUITKA_EXTRA_OPTIONS" ] = extra_options + " --recurse-all"

    if active:
        my_print( "Consider output of recursively compiled program:", path )

        for filename_main in os.listdir( filename ):
            if filename_main.endswith( "Main.py" ):
                break

            if filename_main.endswith( "Main" ):
                break
        else:
            sys.exit(
                """\
Error, no file ends with 'Main.py' or 'Main' in %s, incomplete test case.""" % (
                    filename
                )
            )

        compareWithCPython(
            path        = os.path.join( filename, filename_main ),
            extra_flags = extra_flags,
            search_mode = search_mode,
            needs_2to3  = False
        )
    else:
        my_print( "Skipping", filename )
