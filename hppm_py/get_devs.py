import ctypes.wintypes
import ctypes as C

_dsound_dll = C.windll.LoadLibrary("dsound.dll")
_DirectSoundEnumerateW = _dsound_dll.DirectSoundEnumerateW
_DirectSoundCaptureEnumerateW = _dsound_dll.DirectSoundCaptureEnumerateW

_LPDSENUMCALLBACK = C.WINFUNCTYPE(C.wintypes.BOOL,
                                  C.wintypes.LPVOID,
                                  C.wintypes.LPCWSTR,
                                  C.wintypes.LPCWSTR,
                                  C.wintypes.LPCVOID)

_ole32_dll = C.oledll.ole32
_StringFromGUID2 = _ole32_dll.StringFromGUID2


def get_devices():
    
    devices = []
    
    def cb_enum(lpGUID, lpszDesc, lpszDrvName, _unused):
        dev = ""
        if lpGUID is not None:
            buf = C.create_unicode_buffer(200)
            if _StringFromGUID2(lpGUID, C.byref(buf), 200):
                dev = buf.value
        
        devices.append((dev, lpszDesc))
        return True
    
    _DirectSoundEnumerateW(_LPDSENUMCALLBACK(cb_enum), None)
    
    return devices

def get_caps():
    
    devices = []
    
    def cb_enum(lpGUID, lpszDesc, lpszDrvName, _unused):
        dev = ""
        if lpGUID is not None:
            buf = C.create_unicode_buffer(200)
            if _StringFromGUID2(lpGUID, C.byref(buf), 200):
                dev = buf.value
        
        devices.append((dev, lpszDesc))
        return True
    
    _DirectSoundCaptureEnumerateW(_LPDSENUMCALLBACK(cb_enum), None)
    
    return devices

if __name__ == '__main__':
    print 'playback devices'
    for devid, desc in get_devices():
        print '%38s: %s' % (devid, desc)
    print 'capture devices'
    for devid, desc in get_caps():
        print '%38s: %s' % (devid, desc)



