#include <AutoItConstants.au3>

;locates the cursor
$MousePos = MouseGetPos()
msgbox(0,"Debug","Cursor located at " & $MousePos[0]& "," & $MousePos[1])