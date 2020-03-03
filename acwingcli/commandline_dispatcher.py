import acwingcli.commandline_writer as cmdwriter
from acwingcli.decorators import *

@force_debug_output
def debuginfo():
    cmdwriter.client_debug(config.package_data_file)
