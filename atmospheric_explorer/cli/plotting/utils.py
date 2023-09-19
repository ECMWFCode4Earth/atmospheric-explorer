"""\
Utils for the CLI.
"""


def comma_separated_list(ctx, param, value: str) -> list:
    # pylint: disable=unused-argument
    """Convert a comma separated string into an actual list"""
    return value.strip().split(",") if len(value) > 1 else []
