#include <AutoItConstants.au3>
#include <Array.au3>

;window-related variables
Global $UR1 = "[TITLE:Urban Rivals; CLASS:UnityWndClass; INSTANCE:1]" ;Wheel
Global $UR2 = "[TITLE:Urban Rivals; CLASS:UnityWndClass; INSTANCE:2]" ;Fights

Global $UR_pid1 = 0
Global $UR_pid2 = 0

Global $UR_win1_pos = [0,0,0,0]
Global $UR_win2_pos = [0,0,0,0]

;detection-related variables
Global $RECONNECT_CLIENT_DETECTOR_pos=[630,420], $RECONNECT_CLIENT_DETECTOR_color=0x009EFF, $RECONNECT_CLIENT_button_pos=$RECONNECT_CLIENT_DETECTOR_pos
Global $NO_RECONNECT_CLIENT_DETECTOR_pos=[325,420], $NO_RECONNECT_CLIENT_DETECTOR_color=0xFF2300, $NO_RECONNECT_CLIENT_button_pos=$NO_RECONNECT_CLIENT_DETECTOR_pos
GLobal $SKIP_INTRO_pos=[12,36]
Global $MAIN_MENU_DETECTOR_pos=[345,100], $MAIN_MENU_DETECTOR_color=0xF90049
Global $MAIN_MENU_play_button_pos=[210,290]
Global $WHEEL_DETECTOR_pos=[790,315], $WHEEL_DETECTOR_color=0x850000
Global $WHEEL_button1_pos=[770,70]
Global $WHEEL_DETECTOR2_pos=[267,325], $WHEEL_DETECTOR2_color=0xCF781B
Global $WHEEL_button2_pos=$WHEEL_DETECTOR2_pos
Global $ROLL_WHEEL_DETECTOR_pos=[310,595], $ROLL_WHEEL_DETECTOR_color=0xFFC200, $ROLL_WHEEL_button_pos=$ROLL_WHEEL_DETECTOR_pos
Global $ROLL_WHEEL_GREYED_DETECTOR_pos=$ROLL_WHEEL_DETECTOR_pos, $ROLL_WHEEL_GREYED_DETECTOR_color=0xCC9B00
Global $ROLL_WHEEL_DARKENED_DETECTOR_pos=[335,595], $ROLL_WHEEL_DARKENED_DETECTOR_color=0x280436
Global $WHEEL_WON_CARD_FLIP_pos=[410,325]
;Global $NO_MORE_SPINS_pos=[360,425], $NO_MORE_SPINS_color=0xFFA000
Global $MODE_SELECTION_DETECTOR_pos=[30,55], $MODE_SELECTION_DETECTOR_color=0xFFFFFF
Global $MODE_SELECTION_RANKED_DETECTOR_pos=[640,60], $MODE_SELECTION_RANKED_DETECTOR_color=0xD87000, $MODE_SELECTION_RANKED_button_pos=$MODE_SELECTION_RANKED_DETECTOR_pos
Global $MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos=[640,230], $MODE_SELECTION_RANKED_TYPE2_DETECTOR_color=0xD97000, $MODE_SELECTION_RANKED_TYPE2_button_pos=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos
Global $FIGHT_DETECTOR_pos=[355,605], $FIGHT_DETECTOR_color=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_color, $FIGHT_button_pos=$FIGHT_DETECTOR_pos
Global $SEARCHING_FIGHT_DETECTOR_pos=[780,70], $SEARCHING_FIGHT_DETECTOR_color=0xBE2633
Global $ACTIVE_FIGHT_DETECTOR_pos=[544,620], $ACTIVE_FIGHT_DETECTOR_color=0xB00000
Global $MY_TURN_DETECTOR_pos=[791,594], $MY_TURN_DETECTOR_color=0xE42C08
Global $CARD1_pos=[200,460], $CARD2_pos=[340,460], $CARD3_pos=[490,460], $CARD4_pos=[630,460]
Global $ENNEMY_LEFT_DETECTOR_pos=[360,420], $ENNEMY_LEFT_DETECTOR_color=0xFFA000, $ENNEMY_LEFT_button_pos=$ENNEMY_LEFT_DETECTOR_pos
Global $PLAYABLE_CARD_DETECTOR_pos=[100,485], $PLAYABLE_CARD_DETECTOR_color=$ENNEMY_LEFT_DETECTOR_color
Global $CARD_ADD_PILLZ_pos=[770,325]
Global $PLAY_CARD_pos=[510,420]
Global $END_FIGHT_DETECTOR_pos=[320,605], $END_FIGHT_DETECTOR_color=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_color, $END_FIGHT_button_pos=$END_FIGHT_DETECTOR_pos

;game-related variables
Global $PILLZ = [5,1,8,0]
Global $PILLZ_OFFSET = 1
Global $CARD_ORDER = [2,3,4,1]

;resettable variables
Global $init = 0
Global $intro1_skipped = 0
Global $intro2_skipped = 0
Global $wheel_opened = 0
Global $mode_selection = 0
Global $mode_selected = 0
Global $in_fight = 0
Global $round = 0
Global $pillz_used = 0

;functions
Func OpenClient($name)
	Local $pid = 0
	If Not WinExists($name) Then
		$pid = Run("C:\Program Files (x86)\Urban Rivals\Urban Rivals.exe")
		WinWait($name)
	EndIf
	Return $pid
EndFunc

Func URPixelSearch($pos, $color, $window, $shade=5)
	If $window=1 Then
		WinActive($UR1)
		Return IsArray(PixelSearch($UR_win1_pos[0]+$pos[0]-2, $UR_win1_pos[1]+$pos[1]-2, $UR_win1_pos[0]+$pos[0]+2, $UR_win1_pos[1]+$pos[1]+2, $color, $shade))
	ElseIf $window=2 Then
		WinActive($UR2)
		Return IsArray(PixelSearch($UR_win2_pos[0]+$pos[0]-2, $UR_win2_pos[1]+$pos[1]-2, $UR_win2_pos[0]+$pos[0]+2, $UR_win2_pos[1]+$pos[1]+2, $color, $shade))
	EndIf
EndFunc

Func URClick($pos, $window, $n=1)
	If $n<1 Then
		Return
	EndIf
	If $window=1 Then
		WinActive($UR1)
		Return MouseClick($MOUSE_CLICK_PRIMARY, $UR_win1_pos[0]+$pos[0], $UR_win1_pos[1]+$pos[1], $n)
	ElseIf $window=2 Then
		WinActive($UR2)
		Return MouseClick($MOUSE_CLICK_PRIMARY, $UR_win2_pos[0]+$pos[0], $UR_win2_pos[1]+$pos[1], $n)
	EndIf
EndFunc

Func ResetWindow($window)
	If $window=1 Then
		WinActive($UR1)
		WinKill($UR1)
		$init=0
		$intro1_skipped=0
		$wheel_opened=0
	ElseIf $window=2 Then
		WinActive($UR2)
		WinKill($UR2)
		$init=0
		$intro2_skipped=0
		$mode_selection=0
		$mode_selected=0
	EndIf
EndFunc

Func Card($n)
	If $CARD_ORDER[$n]=1 Then
		Return $CARD1_pos
	ElseIf $CARD_ORDER[$n]=2 Then
		Return $CARD2_pos
	ElseIf $CARD_ORDER[$n]=3 Then
		Return $CARD3_pos
	ElseIf $CARD_ORDER[$n]=4 Then
		Return $CARD4_pos
	EndIf
EndFunc

Func Pillz($n)
	If $n<3 Then
		Return Random($PILLZ[$n]-$PILLZ_OFFSET, $PILLZ[$n]+$PILLZ_OFFSET, 1)
	Else
		Return 14-$pillz_used
	EndIf
EndFunc

Func ResetFight()
	$in_fight=0
	$round=0
	$pillz_used=0
EndFunc


;loop controller
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

;main
While 1
	If $quit Then
		;ResetWindow($UR1)
		;ResetWindow($UR2)
		ExitLoop
	ElseIf $run Then

		;init if not already done
		If Not $init Then
			$UR_pid1 = OpenClient($UR1)
			$UR_pid2 = OpenClient($UR2)

			Sleep(1000)

			$UR_win1_pos = WinGetPos($UR1,"")
			$UR_win2_pos = WinGetPos($UR2,"")

			WinMove($UR1, "", (@DesktopWidth-2*$UR_win1_pos[2])/3,  (@DesktopHeight-$UR_win1_pos[3])/2)
			WinMove($UR2, "", ((@DesktopWidth-2*$UR_win2_pos[2])/3)*2+$UR_win1_pos[2], (@DesktopHeight-$UR_win1_pos[3])/2)

			$UR_win1_pos = WinGetPos($UR1,"")
			$UR_win2_pos = WinGetPos($UR2,"")

			$init=1
		EndIf

		;ensure window 2 is for fighting
		If URPixelSearch($RECONNECT_CLIENT_DETECTOR_pos, $RECONNECT_CLIENT_DETECTOR_color, 2) Then
			URClick($RECONNECT_CLIENT_button_pos, 2)
			Sleep(500)
			ContinueLoop
		EndIf

		;ensure window 1 is offline for wheeling
		If URPixelSearch($NO_RECONNECT_CLIENT_DETECTOR_pos, $NO_RECONNECT_CLIENT_DETECTOR_color, 1) Then
			URClick($NO_RECONNECT_CLIENT_button_pos, 1)
			Sleep(500)
			ContinueLoop
		EndIf

		;skips intro on window1
		If Not $intro1_skipped Then
			If Not URPixelSearch($MAIN_MENU_DETECTOR_pos, $MAIN_MENU_DETECTOR_color, 1) Then
				URClick($SKIP_INTRO_pos, 1, 2)
				Sleep(100)
			Else
				$intro1_skipped=1
			EndIf
		EndIf

		;skips intro on window2
		If Not $intro2_skipped Then
			If Not URPixelSearch($MAIN_MENU_DETECTOR_pos, $MAIN_MENU_DETECTOR_color, 2) Then
				URClick($SKIP_INTRO_pos, 2, 2)
				Sleep(100)
			Else
				$intro2_skipped=1
			EndIf
		EndIf

		;open wheel menu on win1
		If $intro1_skipped And Not $wheel_opened Then
			If URPixelSearch($WHEEL_DETECTOR_pos, $WHEEL_DETECTOR_color, 1) Then
				$wheel_opened=1
			Else
				If URPixelSearch($MAIN_MENU_DETECTOR_pos, $MAIN_MENU_DETECTOR_color, 1) Then
					URClick($WHEEL_button1_pos, 1)
					Sleep(500)
					If URPixelSearch($WHEEL_DETECTOR2_pos, $WHEEL_DETECTOR2_color, 1) Then
						URClick($WHEEL_button2_pos, 1)
					EndIf
				EndIf
				ContinueLoop
			EndIf
		EndIf

		;rolls wheel
		If $wheel_opened And Not URPixelSearch($ROLL_WHEEL_DARKENED_DETECTOR_pos, $ROLL_WHEEL_DARKENED_DETECTOR_color, 1) Then
			If URPixelSearch($ROLL_WHEEL_GREYED_DETECTOR_pos, $ROLL_WHEEL_GREYED_DETECTOR_color, 1) Then
				URClick($WHEEL_WON_CARD_FLIP_pos, 1)
				Sleep(500)
				URClick($WHEEL_WON_CARD_FLIP_pos, 1)
				Sleep(200)
			EndIf
			If URPixelSearch($ROLL_WHEEL_DETECTOR_pos, $ROLL_WHEEL_DETECTOR_color, 1) Then
				URClick($ROLL_WHEEL_button_pos, 1)
			EndIf
		EndIf

		;no more spins
		If URPixelSearch($ENNEMY_LEFT_DETECTOR_pos, $ENNEMY_LEFT_DETECTOR_color, 1) Then
			URClick($ENNEMY_LEFT_button_pos, 1)
			Sleep(500)
		EndIf

		;opens 'mode selection' menu from 'main' menu
		If $intro2_skipped And Not $mode_selection Then
			If URPixelSearch($MODE_SELECTION_DETECTOR_pos, $MODE_SELECTION_DETECTOR_color, 2) Then
				$mode_selection = 1
			ElseIf URPixelSearch($MAIN_MENU_DETECTOR_pos, $MAIN_MENU_DETECTOR_color, 2) Then
				URClick($MAIN_MENU_play_button_pos, 2)
			EndIf
			ContinueLoop
		EndIf

		;opens selected mode menu in 'mode selection' menu
		If $mode_selection And Not $mode_selected Then
			If URPixelSearch($MODE_SELECTION_RANKED_DETECTOR_pos, $MODE_SELECTION_RANKED_DETECTOR_color, 2) Then
				IF URPixelSearch($MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos, $MODE_SELECTION_RANKED_TYPE2_DETECTOR_color, 2) Then
					URClick($MODE_SELECTION_RANKED_TYPE2_button_pos, 2)
					$mode_selected = 1
				EndIf
			Else
				URClick($MODE_SELECTION_RANKED_button_pos, 2)
			EndIf
			ContinueLoop
		EndIf

		;launches a fight
		If $mode_selected And Not URPixelSearch($SEARCHING_FIGHT_DETECTOR_pos, $SEARCHING_FIGHT_DETECTOR_color, 2) Then
			If URPixelSearch($FIGHT_DETECTOR_pos, $FIGHT_DETECTOR_color, 2) Then
				URClick($FIGHT_button_pos, 2)
				Sleep(500)
			EndIf
		EndIf

		;initializes a fight
		If Not $in_fight And URPixelSearch($ACTIVE_FIGHT_DETECTOR_pos, $ACTIVE_FIGHT_DETECTOR_color, 2, 20) Then
			$in_fight=1
			$pillz_used=0
			$round=0
			$init = 1
			$intro1_skipped = 1
			$intro2_skipped = 1
			$mode_selection = 1
			$mode_selected = 1
		EndIf

		;ennemy left // already in matchmaking
		If URPixelSearch($ENNEMY_LEFT_DETECTOR_pos, $ENNEMY_LEFT_DETECTOR_color, 2) Then
			URClick($ENNEMY_LEFT_button_pos, 2)
			Sleep(500)
		EndIf

		;in fight
		If $in_fight Then

			;player turn
			If URPixelSearch($MY_TURN_DETECTOR_pos, $MY_TURN_DETECTOR_color, 2, 20) Then
				URClick(Card($round), 2)
				Sleep(1000)
				If URPixelSearch($PLAYABLE_CARD_DETECTOR_pos, $PLAYABLE_CARD_DETECTOR_color, 2) Then
					Local $p = Pillz($round)
					$pillz_used = $pillz_used + $p
					URClick($CARD_ADD_PILLZ_pos, 2, $p)
					URCLICK($PLAY_CARD_pos, 2)
					$round = Mod($round+1, 4)
					Sleep(3500)
				EndIf
			EndIf
		EndIf

		;fight done
		IF URPixelSearch($END_FIGHT_DETECTOR_pos, $END_FIGHT_DETECTOR_color, 2) And Not URPixelSearch($SEARCHING_FIGHT_DETECTOR_pos, $SEARCHING_FIGHT_DETECTOR_color, 2) Then
			URClick($END_FIGHT_button_pos, 2)
			$init = 1
			$intro1_skipped = 1
			$intro2_skipped = 1
			$mode_selection = 1
			$mode_selected = 1
			ResetFight()
			Sleep(1000)
		EndIf
	EndIf
WEnd