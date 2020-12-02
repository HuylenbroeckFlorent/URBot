#include <AutoItConstants.au3>
#include <Array.au3>
#include <Date.au3>

;timer
Global $timer = [@HOUR, @MIN]
Global $total = 0
Global $overall_total = 0

;window-related variables
Global $UR1_pid = 0
Global $UR2_pid = 0

Global $UR1_handle = 0 ;spinning
Global $UR2_handle = 0 ;wheeling

Global $UR1_win_pos = [0,0,0,0]
Global $UR2_win_pos = [0,0,0,0]

;detection-related variables
Global $RECONNECT_CLIENT_DETECTOR_pos=[630,420], $RECONNECT_CLIENT_DETECTOR_color=0x009EFF, $RECONNECT_CLIENT_button_pos=$RECONNECT_CLIENT_DETECTOR_pos
Global $NO_RECONNECT_CLIENT_DETECTOR_pos=[325,420], $NO_RECONNECT_CLIENT_DETECTOR_color=0xFF2300, $NO_RECONNECT_CLIENT_button_pos=$NO_RECONNECT_CLIENT_DETECTOR_pos
GLobal $SKIP_INTRO_pos=[12,36]
Global $YOUR_MISSIONS_DETECTOR_pos=[340,450], $YOUR_MISSIONS_DETECTOR_color=0xFFA000, $YOUR_MISSIONS_button_pos=$YOUR_MISSIONS_DETECTOR_pos
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
Global $NEW_CHARACTER_OBTAINED_DETECTOR_pos=[465,440], $NEW_CHARACTER_OBTAINED_DETECTOR_color = 0xFFA000, $NEW_CHARACTER_OBTAINED_button_pos=$NEW_CHARACTER_OBTAINED_DETECTOR_pos
Global $ROLLS_LEFT_DETECTOR_pos=[170,615], $ROLLS_LEFT_DETECTOR_color=0xF5AD00
Global $MODE_SELECTION_DETECTOR_pos=[30,55], $MODE_SELECTION_DETECTOR_color=0xFFFFFF
Global $MODE_SELECTION_RANKED_DETECTOR_pos=[640,60], $MODE_SELECTION_RANKED_DETECTOR_color=0xD87000, $MODE_SELECTION_RANKED_button_pos=$MODE_SELECTION_RANKED_DETECTOR_pos
Global $MODE_SELECTION_RANKED_TYPE1_DETECTOR_pos=[585,230], $MODE_SELECTION_RANKED_TYPE1_DETECTOR_color=0xD97000, $MODE_SELECTION_RANKED_TYPE1_button_pos=$MODE_SELECTION_RANKED_TYPE1_DETECTOR_pos
Global $MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos=[640,230], $MODE_SELECTION_RANKED_TYPE2_DETECTOR_color=0xD97000, $MODE_SELECTION_RANKED_TYPE2_button_pos=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos
Global $MODE_SELECTION_RANKED_SURVIVOR_DETECTOR_pos=[600,440], $MODE_SELECTION_RANKED_SURVIVOR_DETECTOR_color=0xD97000, $MODE_SELECTION_RANKED_SURVIVOR_button_pos=$MODE_SELECTION_RANKED_SURVIVOR_DETECTOR_pos
Global $MODE_SELECTION_PVP_DETECTOR_pos=[515,60], $MODE_SELECTION_PVP_DETECTOR_color=0xD87000, $MODE_SELECTION_PVP_button_pos=$MODE_SELECTION_PVP_DETECTOR_pos
Global $MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_pos=[616,226], $MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_color=0xD87000, $MODE_SELECTION_PVP_FREEFIGHT_button_pos=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_pos
Global $FIGHT_DETECTOR_pos=[355,605], $FIGHT_DETECTOR_color=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_color, $FIGHT_button_pos=$FIGHT_DETECTOR_pos
Global $SEARCHING_FIGHT_DETECTOR_pos=[780,70], $SEARCHING_FIGHT_DETECTOR_color=0xBE2633, $SEARCHING_FIGHT_button_pos=$SEARCHING_FIGHT_DETECTOR_pos
Global $ACTIVE_FIGHT_DETECTOR_pos=[544,620], $ACTIVE_FIGHT_DETECTOR_color=0xB00000
Global $MY_TURN_DETECTOR_pos=[791,594], $MY_TURN_DETECTOR_color=0xE42C08
Global $CARD1_pos=[200,460], $CARD2_pos=[340,460], $CARD3_pos=[490,460], $CARD4_pos=[630,460]
Global $ENNEMY_LEFT_DETECTOR_pos=[320,420], $ENNEMY_LEFT_DETECTOR_color=0xFFA000, $ENNEMY_LEFT_button_pos=$ENNEMY_LEFT_DETECTOR_pos
Global $FIGHT_EXPIRED_BUG_DETECTOR_pos=[124,332], $FIGHT_EXPIRED_BUG_DETECTOR_color=0x000000
Global $PLAYABLE_CARD_DETECTOR_pos=[100,485], $PLAYABLE_CARD_DETECTOR_color=$ENNEMY_LEFT_DETECTOR_color
Global $CARD_ADD_PILLZ_pos=[770,325]
Global $PLAY_CARD_pos=[510,420]
Global $END_FIGHT_DETECTOR_pos=[320,605], $END_FIGHT_DETECTOR_color=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_color, $END_FIGHT_button_pos=$END_FIGHT_DETECTOR_pos

;game-related variables
Global $CHOSEN_MODE_pos=$MODE_SELECTION_PVP_DETECTOR_pos
Global $CHOSEN_MODE_color=$MODE_SELECTION_PVP_DETECTOR_color
Global $CHOSEN_ROOM_pos=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_pos
Global $CHOSEN_ROOM_color=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_color
Global $PILLZ = [4,4,4,4];[5,1,6,5]
Global $PILLZ_OFFSET = 1
Global $CARD_ORDER = [1,4,2,3];[3,2,4,1]

;resettable variables
Global $intro1_skipped = 0
Global $intro2_skipped = 0
Global $wheel_opened = 0
Global $mode_selection = 0
Global $mode_selected = 0
Global $in_fight = 0
Global $round = 0
Global $pillz_used = 0
Global $try_to_spin = 1
Global $searching_fight_timer = 0
Global $random_bug_fight_not_expiring = 0
Global $random_bug_fight_not_launching = 0
Global $ennemy_left = 0
Global $to_winkill = 0
Global $to_immediatly_winkill = 0

;counters
Global $winkill_total = 0

;functions
Func URPixelSearch($pos, $color, $window, $shade=5)
	If $window=1 Then
		WinActive($UR1_handle)
		Return IsArray(PixelSearch($UR1_win_pos[0]+$pos[0]-2, $UR1_win_pos[1]+$pos[1]-2, $UR1_win_pos[0]+$pos[0]+2, $UR1_win_pos[1]+$pos[1]+2, $color, $shade))
	ElseIf $window=2 Then
		WinActive($UR2_handle)
		Return IsArray(PixelSearch($UR2_win_pos[0]+$pos[0]-2, $UR2_win_pos[1]+$pos[1]-2, $UR2_win_pos[0]+$pos[0]+2, $UR2_win_pos[1]+$pos[1]+2, $color, $shade))
	EndIf
EndFunc

Func URClick($pos, $window, $n=1)
	If $n<1 Then
		Return
	EndIf
	If $window=1 Then
		WinActive($UR1_handle)
		For $i = 0 To $n-1
			MouseClick($MOUSE_CLICK_PRIMARY, $UR1_win_pos[0]+$pos[0], $UR1_win_pos[1]+$pos[1])
			Sleep(25)
		Next
	ElseIf $window=2 Then
		WinActive($UR2_handle)
		For $i = 0 To $n-1
			MouseClick($MOUSE_CLICK_PRIMARY, $UR2_win_pos[0]+$pos[0], $UR2_win_pos[1]+$pos[1])
			Sleep(25)
		Next
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

Func RollWheel()
	If $wheel_opened And Not URPixelSearch($ROLL_WHEEL_DARKENED_DETECTOR_pos, $ROLL_WHEEL_DARKENED_DETECTOR_color, 1) Then
		If URPixelSearch($ROLL_WHEEL_GREYED_DETECTOR_pos, $ROLL_WHEEL_GREYED_DETECTOR_color, 1) Then
			URClick($WHEEL_WON_CARD_FLIP_pos, 1)
			Sleep(300)
			URClick($WHEEL_WON_CARD_FLIP_pos, 1)
			Sleep(200)
		EndIf
		If URPixelSearch($ROLL_WHEEL_DETECTOR_pos, $ROLL_WHEEL_DETECTOR_color, 1) And $try_to_spin Then
			URClick($ROLL_WHEEL_button_pos, 1)
		EndIf
	EndIf
EndFunc

Func _GetHwndFromPID($PID) ;https://www.autoitscript.com/wiki/FAQ#How_can_I_get_a_window_handle_when_all_I_have_is_a_PID.3F
	$hWnd = 0
	$winlist = WinList()
	Do
		For $i = 1 To $winlist[0][0]
			If $winlist[$i][0] <> "" Then
				$iPID2 = WinGetProcess($winlist[$i][1])
				If $iPID2 = $PID Then
					$hWnd = $winlist[$i][1]
					ExitLoop
				EndIf
			EndIf
		Next
	Until $hWnd <> 0
	Return $hWnd
EndFunc

Func OpenClient($n=0)
	If $n=0 Or $n=1 Then
		If Not WinExists($UR1_handle) Then
			$UR1_pid = Run("C:\Program Files (x86)\Urban Rivals\Urban Rivals.exe")
			Sleep(3000)
			$UR1_handle = _GetHwndFromPID($UR1_pid)
			$UR1_win_pos = WinGetPos($UR1_handle)
			WinMove($UR1_handle, "", (@DesktopWidth-2*$UR1_win_pos[2])/3,  (@DesktopHeight-$UR1_win_pos[3])/2)
			$UR1_win_pos = WinGetPos($UR1_handle)
			$intro1_skipped = 0
			$wheel_opened = 0
			$try_to_spin = 1
		EndIf
	EndIf
	If $n=0 Or $n=2 Then
		If Not WinExists($UR2_handle) Then
			$UR2_pid = Run("C:\Program Files (x86)\Urban Rivals\Urban Rivals.exe")
			Sleep(3000)
			$UR2_handle = _GetHwndFromPID($UR2_pid)
			$UR2_win_pos = WinGetPos($UR2_handle)
			WinMove($UR2_handle, "", ((@DesktopWidth-2*$UR2_win_pos[2])/3)*2+$UR2_win_pos[2], (@DesktopHeight-$UR2_win_pos[3])/2)
			$UR2_win_pos = WinGetPos($UR2_handle)
			$intro2_skipped = 0
			$mode_selection = 0
			$mode_selected = 0
		EndIf
	EndIf
EndFunc

Func URWinKill($h)
	WinKill($h)
	$winkill_total = $winkill_total + 1
	$to_winkill = 0
	$to_immediatly_winkill = 0
	$total = 0
	$random_bug_fight_not_expiring = 0
	$random_bug_fight_not_launching = 0
	Sleep(1000)
EndFunc

Func TimerUpdate()
	Local $timer2 = [@HOUR, @MIN]
	If $timer[0] = $timer2[0] Then
		$total = $total + ($timer2[1]-$timer[1])
		$overall_total = $overall_total + ($timer2[1]-$timer[1])
	Else
		$total = $total + ($timer[1]+$timer2[1]-60)
		$overall_total = $overall_total + ($timer[1]+$timer2[1]-60)
	EndIf
	$timer = $timer2
EndFunc


;loop controller
HotKeySet("{F1}", "StartStop")
HotKeySet("{F2}", "Quit")
HotKeySet("{F3}", "ToggleSpin")
HotKeySet("{F4}", "ToggleFight")

Global $run = 0
Func StartStop()
	$run = Not $run
EndFunc

Global $quit = 0
Func Quit()
	$quit = 1
EndFunc

Global $do_spins = 1
Func ToggleSpin()
	$do_spins = Not $do_spins
EndFunc

Global $do_fights = 1
Func ToggleFight()
	$do_fights = Not $do_fights
EndFunc

;main
MsgBox(0,"Controls","F1 - start/stop (default : stopped)"&@CRLF&"F2 - quit"&@CRLF&"F3 - toggle spinning (default : ON)"&@CRLF&"F4 - toggle fighting (default : ON)", 5)
$timer[0] = @HOUR
$timer[1] = @MIN
While 1

	;in case F2 was pressed
	If $quit Then
		ExitLoop

	;in case F1 was pressed
	ElseIf $run Then

		;clock gestion
		TimerUpdate()
		If $total >= 60 Then
			$to_winkill = 1
		EndIf
		If $total >= 65 Then
			$to_immediatly_winkill = 1
		EndIf

		;CLIENT 1 : SPINNING
		If $do_spins Then

			;open client
			OpenClient(1)

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

			;closes "your missions" panel that randomly pops at launch
			If URPixelSearch($YOUR_MISSIONS_DETECTOR_pos, $YOUR_MISSIONS_DETECTOR_color, 1) Then
				URClick($YOUR_MISSIONS_button_pos, 1)
				Sleep(500)
				URWinKill($UR1_handle)
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
				EndIf
			EndIf

			;if new character unlocked
			If URPixelSearch($NEW_CHARACTER_OBTAINED_DETECTOR_pos, $NEW_CHARACTER_OBTAINED_DETECTOR_color, 1) Then
				URClick($NEW_CHARACTER_OBTAINED_button_pos, 1)
				Sleep(500)
			EndIf

			RollWheel()

			;no more spins
			If URPixelSearch($ENNEMY_LEFT_DETECTOR_pos, $ENNEMY_LEFT_DETECTOR_color, 1) Then
				URClick($ENNEMY_LEFT_button_pos, 1)
				$try_to_spin = 0
				Sleep(250)
			EndIf
		EndIf

		;CLIENT 2 : FIGHTING
		If $do_fights Then

			;open client
			OpenClient(2)

			;reset
			If $to_immediatly_winkill Then
				URWinKill($UR2_handle)
			EndIf

			;ensure window 2 is for fighting
			If URPixelSearch($RECONNECT_CLIENT_DETECTOR_pos, $RECONNECT_CLIENT_DETECTOR_color, 2) Then
				URClick($RECONNECT_CLIENT_button_pos, 2)
				Sleep(500)
				ContinueLoop
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

			;closes "your missions" panel that randomly pops at launch
			If URPixelSearch($YOUR_MISSIONS_DETECTOR_pos, $YOUR_MISSIONS_DETECTOR_color, 2) Then
				URClick($YOUR_MISSIONS_button_pos, 2)
				$intro2_skipped = 1
				$mode_selection = 0
				Sleep(500)
			EndIf

			;opens 'mode selection' menu from 'main' menu
			If $intro2_skipped And Not $mode_selection Then
				If URPixelSearch($MODE_SELECTION_DETECTOR_pos, $MODE_SELECTION_DETECTOR_color, 2) Then
					$mode_selection = 1
				ElseIf URPixelSearch($MAIN_MENU_DETECTOR_pos, $MAIN_MENU_DETECTOR_color, 2) Then
					URClick($MAIN_MENU_play_button_pos, 2)
				EndIf
			EndIf

			;opens selected mode menu in 'mode selection' menu
			If $mode_selection And Not $mode_selected Then
				If URPixelSearch($CHOSEN_MODE_pos, $CHOSEN_MODE_color, 2) Then
					URClick($CHOSEN_MODE_pos, 2)
					IF URPixelSearch($CHOSEN_ROOM_pos, $CHOSEN_ROOM_color, 2) Then
						URClick($CHOSEN_ROOM_pos, 2)
						$mode_selected=1
						Sleep(100)
					EndIf
				Else
					URClick($CHOSEN_MODE_pos, 2)
				EndIf
			EndIf

			;(re-)launches a fight
			If URPixelSearch($FIGHT_DETECTOR_pos, $FIGHT_DETECTOR_color, 2) Then
				If $to_winkill Then
					URWinKill($UR2_handle)
					ContinueLoop
				EndIf
				If URPixelSearch($SEARCHING_FIGHT_DETECTOR_pos, $SEARCHING_FIGHT_DETECTOR_color, 2) Then
					$random_bug_fight_not_launching = 0
				Else
					If $random_bug_fight_not_launching >= 10 Then
						$random_bug_fight_not_launching = 0
						URWinKill($UR2_handle)
					Else
						$try_to_spin = 1
						$init = 1
						$intro1_skipped = 1
						$intro2_skipped = 1
						$mode_selection = 1
						$mode_selected = 1
						ResetFight() ;REMOVED condtition that fight button is detected at this step too
						URClick($FIGHT_button_pos, 2)
						$searching_fight_timer = 0
						$random_bug_fight_not_launching = $random_bug_fight_not_launching + 1
						Sleep(500) ;
					EndIf
				EndIf
			EndIf

			;timeout timer for fight searching
			If URPixelSearch($SEARCHING_FIGHT_DETECTOR_pos, $SEARCHING_FIGHT_DETECTOR_color, 2) Then
				$random_bug_fight_not_launching = 0
				$searching_fight_timer = $searching_fight_timer + 1
				Sleep(250)
				If $searching_fight_timer > 75 Then
					URClick($SEARCHING_FIGHT_button_pos, 2)
					Sleep(250)
					URClick($SEARCHING_FIGHT_button_pos, 2)
					Sleep(250)
				EndIf
			EndIf

			;initializes a fight
			If Not $in_fight And URPixelSearch($ACTIVE_FIGHT_DETECTOR_pos, $ACTIVE_FIGHT_DETECTOR_color, 2, 20) Then
				$in_fight = 1
				$pillz_used = 0
				$round = 0
				$init = 1
				$intro1_skipped = 1
				$intro2_skipped = 1
				$mode_selection = 1
				$mode_selected = 1
				$random_bug_fight_not_launching = 0
				$searching_fight_timer = 0
			EndIf

			;ennemy left // already in matchmaking
			If URPixelSearch($ENNEMY_LEFT_DETECTOR_pos, $ENNEMY_LEFT_DETECTOR_color, 2) Then
				If $to_winkill Then
					URWinKill($UR2_handle)
					ContinueLoop
				EndIf
				If $ennemy_left < 5 And URPixelSearch($ENNEMY_LEFT_DETECTOR_pos, $ENNEMY_LEFT_DETECTOR_color, 2) Then
					$ennemy_left = $ennemy_left + 1
					URClick($ENNEMY_LEFT_button_pos, 2)
					Sleep(1000)
				Else
					URWinKill($UR2_handle)
				EndIf
			Else
				$ennemy_left = 0
			EndIf

			;in fight
			If $in_fight Then

				;resets the detector for fight not launching
				$random_bug_fight_not_launching = 0

 				;detects fights that randomly timeout without ending
				If URPixelSearch($FIGHT_EXPIRED_BUG_DETECTOR_pos, $FIGHT_EXPIRED_BUG_DETECTOR_color, 2) And Not $random_bug_fight_not_expiring Then
					$random_bug_fight_not_expiring = 1
					Sleep(5000)
				ElseIf URPixelSearch($FIGHT_EXPIRED_BUG_DETECTOR_pos, $FIGHT_EXPIRED_BUG_DETECTOR_color, 2) And $random_bug_fight_not_expiring Then
					$random_bug_fight_not_expiring = 0
					URWinKill($UR2_handle)
				Else
					$random_bug_fight_not_expiring = 0
				EndIf

				;player turn
				If URPixelSearch($MY_TURN_DETECTOR_pos, $MY_TURN_DETECTOR_color, 2, 20) Then
					Local $p = Pillz($round)
					$pillz_used = $pillz_used + $p
					Local $timeout = 0
					While URPixelSearch($MY_TURN_DETECTOR_pos, $MY_TURN_DETECTOR_color, 2, 20)
						If $timeout>=6 Then
							URWinKill($UR2_handle)
						EndIf
						URClick(Card($round), 2)
						Sleep(750)
						If URPixelSearch($PLAYABLE_CARD_DETECTOR_pos, $PLAYABLE_CARD_DETECTOR_color, 2) Then
							URClick($CARD_ADD_PILLZ_pos, 2, $p)
							URCLICK($PLAY_CARD_pos, 2)
							If $do_spins Then
								RollWheel()
							EndIf
							Sleep(3250)
						EndIf
						$timeout=$timeout+1
					WEnd
					$round = Mod($round+1, 4)
				EndIf
			EndIf
		EndIf
	EndIf
WEnd
MsgBox(0,"v.2.3.1","Total winkill : "&$winkill_total&"."&@CRLF&"Time until next reset : "&60-$total&"min."&@CRLF&"Total time : "&int($overall_total/60)&"h"&Mod($overall_total, 60)&"min.")
