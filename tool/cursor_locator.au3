#include <AutoItConstants.au3>

;locates the cursor relative to the Urban Rivals client's upper left corner.
Global $upper_left_corner_pos[4] = [0,0,0,0]

$upper_left_corner_pos = WinGetPos ("[TITLE:Urban Rivals; CLASS:UnityWndClass; INSTANCE:1]")
WinActivate("[TITLE:Urban Rivals; CLASS:UnityWndClass; INSTANCE:1]")

$MousePos = MouseGetPos()
msgbox(0,"Debug","Cursor located at " & $MousePos[0]-$upper_left_corner_pos[0] & "," & $MousePos[1]-$upper_left_corner_pos[1])