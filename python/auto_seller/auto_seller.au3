#include <AutoItConstants.au3>
#include <Array.au3>
#include <Math.au3>

Global $timer = [@MIN, @SEC]
Global $total = 0

Global $PRICES_FILE_handle = 0
Global $PRICES[48]

Global $SELL_CARD_DETECTOR_pos=[493,895], $SELL_CARD_DETECTOR_color=0xFEDB00, $SELL_CARD_button_pos=$SELL_CARD_DETECTOR_pos
Global $SELL_CARD2_DETECTOR_pos=[472,832], $SELL_CARD2_DETECTOR_color=0xFEDB00, $SELL_CARD2_button_pos=$SELL_CARD2_DETECTOR_pos
Global $ENTER_PRIZE_pos=[757,250]
Global $SELL_DETECTOR_pos=[1184,462], $SELL_DETECTOR_color=0xFF8400, $SELL_button_pos=$SELL_DETECTOR_pos
Global $SOLD_DETECTOR_pos=[1853,157], $SOLD_DETECTOR_color=0xCFE9D3, $SOLD_button_pos=$SOLD_DETECTOR_pos
Global $ERROR_DETECTOR_pos=[1853,157], $ERROR_DETECTOR_color=0xF3D2D3, $ERROR_button_pos=$SOLD_DETECTOR_pos

Global $SORTBY_CLAN="clan", $SORTBY_NAME="name", $SORTBY_DATE="date", $SORTBY_LEVEL="level", $SORTBY_LEVELMAX="levelmax", $SORTBY_RARITY="rarity"
Global $ORDERBY_ASC="asc", $ORDERBY_DESC="desc"
Global $GROUP_ALL="all", $GROUP_DOUBLE="double", $GROUP_EVOLVE="evolve", $GROUP_MAXED="maxed", $GROUP_NODECK="nodeck", $GROUP_BEST="best"
Global $NB_PER_PAGE_12="12", $NB_PER_PAGE_24="24",$NB_PER_PAGE_48="48"

Global $SORTBY=$SORTBY_RARITY
Global $ORDERBY=$ORDERBY_DESC
Global $GROUP=$GROUP_EVOLVE
GLOBAL $NB_PER_PAGE=6

Global $COMMAND_LINE = "C:\Users\Florent\AppData\Local\Programs\Python\Python39\python.exe urbot_scraping.py prices "&$SORTBY&" "&$ORDERBY&" "&$GROUP&" "&$NB_PER_PAGE  ;&" >> D:\Documents\URBot\outputs.txt"
Global $URL = "https://www.urban-rivals.com/collection/index.php?view=collection&page=0&sortby="&$SORTBY&"&orderby="&$ORDERBY&"&group="&$GROUP&"&nb_per_page="&$NB_PER_PAGE

Global $TOTAL_PRICE = 0
Global $TOTAL_CARD = 0

Func UpdatePrices()
	RunWait($COMMAND_LINE, "D:\Documents\URBot\python/", @SW_HIDE)
	$PRICES_FILE_handle = FileOpen("D:\Documents\URBot\prices.txt")
	For $i = 0 To Number($NB_PER_PAGE)-1
		$PRICES[$i]=FileReadLine($PRICES_FILE_handle, $i+1)
	Next
	FileClose($PRICES_FILE_handle)
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

Func TimerUpdate()
	Local $timer2 = [@MIN, @SEC]
	If $timer[0] = $timer2[0] Then
		$total = $total + ($timer2[1]-$timer[1])
	Else
		$total = $total + ($timer[1]+$timer2[1]-60)
	EndIf
	$timer = $timer2
EndFunc



ShellExecute($URL)
While 1

	;in case F2 was pressed
	If $quit Then
		ExitLoop
	;in case F1 was pressed
	ElseIf $run Then
		TimerUpdate()
		UpdatePrices()

		;exit condition
		Local $max_rare_index = _ArraySearch($PRICES, 0, 0, Number($NB_PER_PAGE)-1)
		If $max_rare_index = 0 Then
			ExitLoop
		EndIf
		For $i = 0 To Number($NB_PER_PAGE)-1
			If $run Then

				If IsArray(PixelSearch($SELL_CARD_DETECTOR_pos[0]-2, $SELL_CARD_DETECTOR_pos[1]-2, $SELL_CARD_DETECTOR_pos[0]+2, $SELL_CARD_DETECTOR_pos[1]+2, $SELL_CARD_DETECTOR_color, 5)) Then
					MouseClick($MOUSE_CLICK_PRIMARY, $SELL_CARD_button_pos[0], $SELL_CARD_button_pos[1],1,5)
					While Not IsArray(PixelSearch($SELL_DETECTOR_pos[0]-2, $SELL_DETECTOR_pos[1]-2, $SELL_DETECTOR_pos[0]+2, $SELL_DETECTOR_pos[1]+2, $SELL_DETECTOR_color, 5))
						MouseClick($MOUSE_CLICK_PRIMARY, $SELL_CARD_button_pos[0], $SELL_CARD_button_pos[1],1,5)
					Wend
					MouseClick($MOUSE_CLICK_PRIMARY, $ENTER_PRIZE_pos[0], $ENTER_PRIZE_pos[1], 1, 2)
					Send($PRICES[$i])
					$TOTAL_CARD = $TOTAL_CARD + 1
					$TOTAL_PRICE = $TOTAL_PRICE + $PRICES[$i]
					MouseClick($MOUSE_CLICK_PRIMARY, $SELL_button_pos[0], $SELL_button_pos[1], 1, 2)
					While Not IsArray(PixelSearch($SOLD_DETECTOR_pos[0]-2,$SOLD_DETECTOR_pos[1]-2,$SOLD_DETECTOR_pos[0]+2,$SOLD_DETECTOR_pos[1]+2,$SOLD_DETECTOR_color ,5)) And Not IsArray(PixelSearch($ERROR_DETECTOR_pos[0]-2,$ERROR_DETECTOR_pos[1]-2,$ERROR_DETECTOR_pos[0]+2,$ERROR_DETECTOR_pos[1]+2,$ERROR_DETECTOR_color,5))
						Sleep(1)
					Wend
					If IsArray(PixelSearch($SOLD_DETECTOR_pos[0]-2,$SOLD_DETECTOR_pos[1]-2,$SOLD_DETECTOR_pos[0]+2,$SOLD_DETECTOR_pos[1]+2,$SOLD_DETECTOR_color ,5)) Then
						MouseClick($MOUSE_CLICK_PRIMARY, $SOLD_button_pos[0], $SOLD_button_pos[1], 1, 2)
					ElseIf IsArray(PixelSearch($ERROR_DETECTOR_pos[0]-2,$ERROR_DETECTOR_pos[1]-2,$ERROR_DETECTOR_pos[0]+2,$ERROR_DETECTOR_pos[1]+2,$ERROR_DETECTOR_color,5)) Then
						$i = Number($NB_PER_PAGE)
					EndIf
					Sleep(200)
				Else
					$i=_Max(0, $i-1)
				EndIf
			EndIf
			If $quit Or $i = $max_rare_index-1 Then
				$quit = 1
				ExitLoop
			EndIf
		Next
	EndIf
WEnd
FileDelete("D:\Documents\URBot\prices.txt")
MsgBox(0,"Summary","Ran for "&int($total/60)&"min"&Mod($total,60)&"s."&@CRLF&"Put "&$TOTAL_CARD&" characters for sale for a total of "&$TOTAL_PRICE&" clintz.")