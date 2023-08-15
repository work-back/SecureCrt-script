
import re

def logToCrt(log):
    crt.Screen.Send("\n\r####[{}]####\n\r".format(log))
    crt.Screen.WaitForString("#")
    
def FixInBoot():
    crt.Screen.Send("\n")
    ret = crt.Screen.WaitForString("<< M7332 >>#", 1)
    if ret == True:
        logToCrt("Fix in Boot")
        crt.Screen.Send("reset\n")
        crt.Sleep(25 * 1000)

def WaitForInConsole():
    while True:
        crt.Screen.Send("\n")
        ret = crt.Screen.WaitForString("console:", 1)
        if ret == True:
            logToCrt("Got In console")
            break
        else:
            logToCrt("Not Got In console")
            FixInBoot()

def SwitchToRoot():
    crt.Screen.Send("whoami\n")
    ret = crt.Screen.WaitForString("root:", 1)
    if ret != True:
        crt.Screen.Send("su\n")
        crt.Screen.Send("\n")

def WaitForWlan0Running():
    while True:
        crt.Screen.Clear()
        crt.Screen.Send("ifconfig wlan0\n")
        ret = crt.Screen.WaitForString("RUNNING", 1)
        if ret == True:
            logToCrt("Got wlan0 UP")
            break
        else:
            logToCrt("Not Got wlan0 UP")

def WaitForWlan0Ip():
    while True:
        crt.Screen.Clear()
        crt.Screen.Send("ifconfig wlan0\n")
        ret = crt.Screen.WaitForString("192.168.66.", 1)
        if ret == True:
            logToCrt("Got wlan0 IP")
            break
        else:
            logToCrt("Not Got wlan0 IP")

def DumpUptime(max_uptime):
    crt.Screen.Clear()
    logToCrt("Show UP Time")
    crt.Screen.Send("UPTIME=$(cat /proc/uptime); echo __T_S__=[${UPTIME}]__T_E_$?__\n")
    crt.Sleep(1)
    res_strs = crt.Screen.ReadString("__T_E_0__", 10)
    res_lists = res_strs.split("\n")
    if len(res_lists) < 1:
        return False
    res_line = res_lists[-1]    # ==> __T_S__=[5842.55 11349.92]__T_E_0__
    # crt.Dialog.MessageBox(res_line);
    tt = re.split('\[|\]', res_line)
    if len(tt) != 3:
        return False
    # crt.Dialog.MessageBox(len(tt).__str__() + ":" + tt[1]);
    times = tt[1]               # ==> 5842.55 11349.92
    time_l = times.split(" ")
    if len(time_l) != 2:
        return False
    # crt.Dialog.MessageBox(time_l[0]); # ==> 5842.55
    logToCrt("uptime ==> " + time_l[0]);
    # crt.Dialog.MessageBox(int(time_l[0]))
    if float(time_l[0]) > max_uptime:
        return False
    
    return True
    
            
def CleanAllLogd():
    logToCrt("Clean All logcat")
    crt.Screen.Send("rm /data/misc/logd/logcat.* -rf && echo "" > /data/misc/logd/logcat\n")

def RebootSystem():
    crt.Screen.Send("reboot\n")
    crt.Screen.Send("\n")


max_wait_time = 45

def RunRebootLoop():
    reboot_cnt = 1

    while True:
        WaitForInConsole()
        SwitchToRoot()
        WaitForWlan0Running()
        WaitForWlan0Ip()
        if not DumpUptime(max_wait_time):
            logToCrt("Timeout %d" % max_wait_time)
            result = crt.Dialog.MessageBox("超时，是否继续?", "Error", ICON_QUESTION | BUTTON_YESNO | DEFBUTTON2)
            if result == IDNO:
                logToCrt("Stop Reboot Loop");
                break
            logToCrt("Continue Reboot Loop");
        
        crt.Sleep(10 * 1000)
        CleanAllLogd();
        
        logToCrt("====>%d<====" % reboot_cnt)
        reboot_cnt = reboot_cnt + 1
        crt.Sleep(1 * 1000)
        RebootSystem()
        
        crt.Sleep(30 * 1000)


RunRebootLoop()
