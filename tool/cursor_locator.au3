#include <AutoItConstants.au3>

Global $upper_left_corner_pos[4] = [0,0,0,0]

If Not WinExists("Urban Rivals") Then
	Run("C:\Program Files (x86)\Urban Rivals\Urban Rivals.exe")
	WinWait("Urban Rivals")
EndIf

$upper_left_corner_pos = WinGetPos ("Urban Rivals")

WinActivate("Urban Rivals")


$MousePos = MouseGetPos()
msgbox(0,"Debug","Cursor located at " & $MousePos[0]-$upper_left_corner_pos[0] & "," & $MousePos[1]-$upper_left_corner_pos[1])