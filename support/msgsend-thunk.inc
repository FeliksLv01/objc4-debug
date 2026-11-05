// Local macOS 27 compatibility entry point, tail-calling upstream objc_msgSend.
.text
.p2align 2
.globl _objc_msgSend_thunk
_objc_msgSend_thunk:
    b _objc_msgSend
