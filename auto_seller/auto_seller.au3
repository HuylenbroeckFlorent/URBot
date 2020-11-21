#include <AutoItConstants.au3>
#include <Array.au3>
#include <Math.au3>

Global $PRICES_FILE_handle = 0
Global $PRICES[48]

Global $SELL_CARD_DETECTOR_pos=[472,897], $SELL_CARD_DETECTOR_color=0xFEDB00, $SELL_CARD_button_pos=$SELL_CARD_DETECTOR_pos
Global $ENTER_PRIZE_pos=[730,250]
Global $SELL_DETECTOR_pos=[1147,462], $SELL_DETECTOR_color=0xFF8400, $SEL_button_pos=$SELL_DETECTOR_pos

Func UpdatePrices()
	RunWait("C:\Users\Florent\AppData\Local\Programs\Python\Python39\python.exe D:\Documents\URBot\auto_seller/auto_seller.py")
	Sleep(5000)
	$PRICES_FILE_handle = FileOpen("D:\Documents\URBot\prices.txt")
	For $i = 0 To 47
		$PRICES[$i]=FileReadLine($PRICES_FILE_handle, $i+1)
	Next
EndFunc

HotKeySet("{F1}", "StartStop")
HotKeySet("{F2}", "Quit")
Global $run = 0
Func StartStop()
	$run = Not $run
EndFunc

Global $quit = 0
Func Quit()
	$quit = 1
EndFunc

ShellExecute("https://www.urban-rivals.com/collection/index.php?view=collection&page=0&sortby=date&orderby=desc&group=evolve&nb_per_page=48")
While 1

	;in case F2 was pressed
	If $quit Then
		ExitLoop
	;in case F1 was pressed
	ElseIf $run Then
		UpdatePrices()
		For $i = 0 To 47
			If $run Then
				If IsArray(PixelSearch( $SELL_CARD_DETECTOR_pos[0]-2, $SELL_CARD_DETECTOR_pos[1]-2, $SELL_CARD_DETECTOR_pos[0]+2, $SELL_CARD_DETECTOR_pos[1]+2, $SELL_CARD_DETECTOR_color, 5)) Then
					MouseClick($MOUSE_CLICK_PRIMARY, $SELL_CARD_button_pos[0], $SELL_CARD_button_pos[1])
					Sleep(200)
					MouseClick($MOUSE_CLICK_PRIMARY, $ENTER_PRIZE_pos[0], $ENTER_PRIZE_pos[1])
					Sleep(200)
					Send($PRICES[$i])
					Sleep(200)
					If IsArray(PixelSearch( $SELL_DETECTOR_pos[0]-2, $SELL_DETECTOR_pos[1]-2, $SELL_DETECTOR_pos[0]+2, $SELL_DETECTOR_pos[1]+2, $SELL_DETECTOR_color, 5)) Then
						MouseClick($MOUSE_CLICK_PRIMARY, $SEL_button_pos[0], $SEL_button_pos[1])
						Sleep(650)
					EndIf
				Else
					$i=_Max(0, $i+1)
				EndIf
			EndIf
		Next
	EndIf
WEnd