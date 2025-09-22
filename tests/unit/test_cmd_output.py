"""tests/unit/test_cmd_output.py: Unit-Test bugtool.cmd_output()"""


def test_cmd_output(bugtool):
    """Test all code lines in bugtool.cmd_output(cap, args, label, filter)"""

    # Arguments for the positive test:
    cap = bugtool.CAP_XENSERVER_CONFIG

    # Assert that mismatching cap causes no output in bugtool.data:
    bugtool.entries = [bugtool.CAP_DISK_INFO, cap, bugtool.CAP_PAM]
    bugtool.cmd_output(cap=bugtool.CAP_XENSERVER_LOGS, args=[])
    assert bugtool.data == {}

    # Assert that non existing command results in no bugtool.data:
    bugtool.cmd_output(cap=cap, args=["/nonexisting-command", "arg1", "arg2"])
    assert bugtool.data == {}

    # Assert matching cap and args produces expected_data
    args = ["ls", "-l", __file__]
    for command in [args, " ".join(args), "/nonexisting-command arg"]:
        for label in [None, "cmd_output_label"]:
            # cmd_output() does not call the filter function, just stores it
            def mock():
                return ""

            mock()  # Cover the dummy filter function
            bugtool.data = {}  # Reset bugtool.data for the next test
            bugtool.cmd_output(cap=cap, args=command, label=label, filter=mock)

            if command == "/nonexisting-command arg":
                # Non-existing command produces no output
                assert bugtool.data == {}
            else:
                # Existing command produces expected output

                # Determine the expected label
                if label:
                    expected_label = label
                elif isinstance(command, str):
                    expected_label = command
                else:
                    expected_label = " ".join(command)

                expected_data = {
                    expected_label: {
                        "filter": mock,
                        "cap": bugtool.CAP_XENSERVER_CONFIG,
                        "cmd_args": command,
                    }
                }
                assert bugtool.data == expected_data
