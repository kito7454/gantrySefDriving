import helpers.spcPyroClient as spc
import time

index = 47

spcRemote = spc.getRemoteSPC()
spcRemote.query(f"setvar batchNum {str(index)}\n")
spcRemote.query(f"compile\n")
spcRemote.switchImageNum(index, "thz")
time.sleep(20)
spcRemote.query(f"run\n")