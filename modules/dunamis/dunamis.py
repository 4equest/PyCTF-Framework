import ptrace.debugger
import signal
import ctypes
import sys
import os
import psutil
import time
import logging
from capstone import *

# logging.getLogger().setLevel(logging.DEBUG)

# ptrace constants
PTRACE_TRACEME = 0
PTRACE_SINGLESTEP = 9
PTRACE_GETREGS = 12
PTRACE_PEEKDATA = 2
libc = ctypes.CDLL('libc.so.6')
n_ptrace = libc.ptrace

def get_asm(process: ptrace.debugger.PtraceProcess, addr) -> CsInsn:
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    return next(md.disasm(process.readBytes(addr, 16), addr), None)
    
def dunamis_main(pid):
    debugger = ptrace.debugger.PtraceDebugger()
    process_pid = psutil.Process(pid)
    print("Attach the running process %s" % pid)
    process = debugger.addProcess(pid, True)
    writable_maps = []
    
    process_path = process_pid.exe()

    for map in process.readMappings():
        print("MAPS: %s" % map)
        if map.pathname == process_path and "x" in map.permissions:
            print(f"creating breakpoint at {hex(map.start)}")
            process.createBreakpoint(map.start) #本当はmainにbreakpoint打ちたいけどmainが見つけられなかったりプログラムが壊れたりするのでおそらく_initの部分に打ち込む
        if "w" in map.permissions or "r" in map.permissions:
            writable_maps.append([map.start, map.end]) #実は後から増えるのでここで取得した分だけだとだめ...
            
    
    process.cont()
    process.waitSignals(signal.SIGTRAP)
    print("IP : %#x" % process.getInstrPointer())
    print("SP : %#x" % process.getStackPointer())
    print("BP : %#x" % process.getFramePointer())
    
    while True:
        stack_addr = process.getStackPointer()
        base_addr = process.getFramePointer()
        next_asm = get_asm(process, process.getInstrPointer())
        # print(next_asm)
        
        if next_asm is not None:
            reads, writes = next_asm.regs_access()
            # readするレジスタは今のところ使ってない
            for read in reads:
                if next_asm.reg_name(read) != "rflags":
                    # print(f'read = {next_asm.reg_name(read)}')
                    pass
            
        process.singleStep()
        try:
            process.waitSignals(signal.SIGTRAP)
        except ptrace.debugger.ProcessSignal as e:
            process.dumpMaps()
            if e.name == "SIGWINCH":
                pass
            else:
                print(e)
                exit(1)
                
        if next_asm is None or len(writes) == 0:
            continue
        
        regs = process.getregs()
        for write in writes:
            register_name = next_asm.reg_name(write)
            if register_name != "rflags":
                # print(f'write = {register_name}')
                if register_name.startswith("e"):
                    register_name = "r" + register_name[1:]
                if register_name.startswith("x") or register_name.startswith("y"):
                    # print("FPU registers not supported")
                    continue
                if register_name.endswith("d") or register_name.endswith("w") or register_name.endswith("b"):
                    register_name = register_name[:-1]
                if register_name == "al" or register_name == "ah":
                    register_name = "rax"
                if register_name == "bl" or register_name == "bh":
                    register_name = "rbx"
                if register_name == "cl" or register_name == "ch":
                    register_name = "rcx"
                if register_name == "dl" or register_name == "dh":
                    register_name = "rdx"
                if register_name == "sil" or register_name == "si" :
                    register_name = "rsi"
                if register_name == "dil" or register_name == "di" :
                    register_name = "rdi"
                if register_name == "spl" or register_name == "sp" :
                    register_name = "rsp"
                if register_name == "bpl" or register_name == "bp" :
                    register_name = "rbp"

                register_value = getattr(regs, register_name)

                # ポインタを追い求めてその値を取得する
                while True:
                    # readWordとかするときにメモリ範囲外だと例外が発生するので無理やりtryでやる 絶対もっといい方法ある
                    try:
                        mem_string = process.readCString(register_value, 256)[0]
                        if (sys.argv[1] + "{").encode() in mem_string and b'}' in mem_string:
                            print(mem_string)
                            print("flag found!")
                            sys.exit(0) # これexceptに捕まえられたりなかったりする よくわからん 嗚呼
                            
                        if register_value % 8 == 0:
                            pointer_value = process.readWord(register_value)
                            
                            # print(f"-> {hex(pointer_value)} {mem_string}")
                            
                            # ループ対策　今までのポインタ一覧をリスト化してそれを比較したほうがいい
                            if register_value == pointer_value:
                                break
                            register_value = pointer_value
                        else:
                            # print(f"->  {mem_string}")
                            break
                    except Exception as e:
                        # print(e)
                        break
    process.detach()
    debugger.quit()

def main():
    
    if len(sys.argv) < 3:
        print("Usage: %s <flag pattern> <elf> <elf options>" % sys.argv[0])
        sys.exit(1)
    
    pid = os.fork()
    if pid == 0:  # child process
        n_ptrace(PTRACE_TRACEME, 0, None, None)
        os.execv(sys.argv[2], sys.argv[2:])  # execute the ELF file
    else:  # parent process
        dunamis_main(pid)
        print("end")
if __name__ == "__main__":
    main()