import os
cmd = "wmic path Win32_VideoController get CurrentHorizontalResolution,CurrentVerticalResolution"
output = os.popen(cmd).read()
print(output)