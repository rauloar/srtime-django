
from zk import const

print("--- ZK Constants ---")
print(f"EF_ATTLOG: {const.EF_ATTLOG}")
print(f"EF_FINGER: {const.EF_FINGER}")
print(f"EF_FACE: {const.EF_FACE}")

# Status / Machine Status
# Usually 0=CheckIn, 1=CheckOut, 2=BreakOut, 3=BreakIn, 4=OT-In, 5=OT-Out
# Let's see if constants exist for these
try:
    print(f"MACHINE_STATUS_OP_CHECKIN: {const.MACHINE_STATUS_OP_CHECKIN}")
except: pass

# Verification Modes
# Usually 0=Password, 1=Finger, 2=Card, 15=Face (varies by device)
# Need to find where these are defined or rely on raw values.
