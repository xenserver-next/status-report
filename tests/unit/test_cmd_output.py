"""tests/unit/test_cmd_output.py: Unit-Test bugtool.cmd_output()"""


def test_cmd_output_mismatching_cap(bugtool_fixture):
    """Assert that mismatching cap causes no extension of bugtool.data:"""

    # Prepare that mismatching cap causes no output in bugtool.data:
    bugtool_fixture.entries = [bugtool_fixture.CAP_PAM]

    # Act
    bugtool_fixture.cmd_output(bugtool_fixture.CAP_XENSERVER_LOGS, ["/bin/sh"])

    # Assert that the command is not added to data
    assert bugtool_fixture.data == {}


def check_cmd_output_data(bugtool, command, label=None, filter_func=None):
    """Assert that cmd_output() stores the expected command in bugtool.data"""

    # Prepare
    bugtool.entries = [bugtool.CAP_PAM]
    bugtool.data = {}

    # Act
    bugtool.cmd_output(bugtool.entries[0], command, label, filter=filter_func)

    # Assert
    assert bugtool.data == {
        label
        or command: {
            "filter": filter_func,
            "cap": bugtool.entries[0],
            "cmd_args": command,
        }
    }


def test_cmd_output_commands_and_labels(bugtool_fixture):
    """Test cmd_output() behavior with commands, labels, and filters."""

    def mock_filter(input_string):
        """Mock filter function replacing 'arg' with 'cookie' in the input string."""
        return input_string.replace("arg", "cookie")

    # Test various combinations of command, label, and filter:
    check_cmd_output_data(bugtool_fixture, "/missing-cmd arg")
    check_cmd_output_data(bugtool_fixture, "/missing-cmd arg", "label")
    check_cmd_output_data(bugtool_fixture, "pwd --version", filter_func=mock_filter)
    check_cmd_output_data(bugtool_fixture, "pwd --version", "label", mock_filter)

    # Additionally, verify that the given filter function can be used as expected:
    assert bugtool_fixture.data["label"]["filter"]("arg") == "cookie"


def test_cmd_output_multiple_commands(bugtool_fixture):
    """Assert that multiple entries and commands extend bugtool.data."""

    # Prepare
    #
    cap1 = bugtool_fixture.CAP_OEM
    cap2 = bugtool_fixture.CAP_PAM
    bugtool_fixture.entries = [cap1, cap2]

    # Act
    #
    cmd1 = ["/usr/bin/pwd", "--version"]
    cmd2 = ["/missing-cmd", "arg1", "arg2"]
    bugtool_fixture.cmd_output(cap1, cmd1)
    bugtool_fixture.cmd_output(cap2, cmd2)

    # Assert
    #
    assert bugtool_fixture.data == {
        # At the moment, we also add commands which are missing on the system to data
        "missing-cmd arg1 arg2": {
            "cap": cap2,
            "cmd_args": cmd2,
            "filter": None,
        },
        # Uses command as string without path as key when no label is set
        "pwd --version": {
            "cap": cap1,
            "cmd_args": cmd1,
            "filter": None,
        },
    }
