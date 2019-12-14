#include <AutoItConstants.au3>
#include <Array.au3>

HotKeySet("{F1}", "StartStop")
HotKeySet("{F2}", "Quit")

;res
Global $BASE_RES = [800, 600]
Global $CUSTOM_RES = [800, 600]
;client position and dimensions
Global $dim[4] = [0,0,0,0]
Global $UR = "Urban Rivals"

;main menu
Global $MAIN_MENU_DETECTOR_pos = [78, 610], $MAIN_MENU_DETECTOR_color = 0xF9F9F9
Global $MAIN_MENU_play_button_pos = [210,260]

;mode selection
Global $MODE_MENU_DETECTOR_pos = [52,44], $MODE_MENU_DETECTOR_color = 0xFFFFFF

;mode selection : solo
Global $MODE_MENU_solo_button_pos = [460,60]
Global $MODE_MENU_SOLO_DETECTOR_pos = $MODE_MENU_solo_button_pos, $MODE_MENU_SOLO_DETECTOR_color = 0xD97000
Global $MODE_MENU_SOLO_dojo_enter_pos = [580,280]
Global $MODE_MENU_SOLO_arcade_enter_pos = [580,380]

;mode selection : pvp
Global $MODE_MENU_pvp_button_pos = [590,60]
Global $MODE_MENU_PVP_DETECTOR_pos = $MODE_MENU_pvp_button_pos, $MODE_MENU_PVP_DETECTOR_color = 0xD97000
Global $MODE_MENU_PVP_freefight_enter_pos = [580,230]
Global $MODE_MENU_PVP_training_normal_pos = [550,330]
Global $MODE_MENU_PVP_training_nopillz_pos = [630,330]
Global $MODE_MENU_PVP_event_enter_pos = [570,440]

;mode selection : ranked
Global $MODE_MENU_ranked_button_pos = [730,60]
Global $MODE_MENU_RANKED_DETECTOR_pos = $MODE_MENU_ranked_button_pos, $MODE_MENU_RANKED_DETECTOR_color = 0xD97000
Global $MODE_MENU_RANKED_tourney_type1_pos = [550,230]
Global $MODE_MENU_RANKED_tourney_type2_pos = [630,230]
Global $MODE_MENU_RANKED_efc_enter_pos = [570,330]
Global $MODE_MENU_RANKED_survivor_enter_pos = [570,440]

;menu in-room
Global $ROOM_MENU_DETECTOR_pos = [470, 605], $ROOM_MENU_DETECTOR_color = 0xD97000
Global $ROOM_MENU_SEARCHING_FIGHT_DETECTOR_pos = [786,73], $ROOM_MENU_SEARCHING_FIGHT_DETECTOR_color = 0xBE2633
Global $ROOM_MENU_fight_button_pos = [410,600]

;in-fight
Global $FIGHT_DETECTOR_pos = [544,621], $FIGHT_DETECTOR_color = 0xAF0000
Global $FIGHT_TURN_DETECTOR_pos = [790,593], $FIGHT_TURN_DETECTOR_color = 0xE42D08
Global $FIGHT_TIMEOUT_DETECTOR_pos = [465, 420], $FIGHT_TIMEOUT_DETECTOR_color = 0xFFA000
Global $FIGHT_PLAYABLE_CARD_DETECTOR_pos = [769,326], $FIGHT_PLAYABLE_CARD_DETECTOR_color = 0xFFA000
Global $FIGHT_UNPLAYABLE_CARD_CLICKAWAY_pos = [360,100]
Global $FIGHT_CARD1_pos = [190,450]
Global $FIGHT_CARD2_pos = [340,450]
Global $FIGHT_CARD3_pos = [490,450]
Global $FIGHT_CARD4_pos = [640,450]
Global $FIGHT_ADD_PILLZ_pos = [768,326]
Global $FIGHT_FIGHT_pos = [483,417]

;choices
Global $CHOSEN_MODE = $MODE_MENU_ranked_button_pos
Global $CHOSEN_ROOM = $MODE_MENU_RANKED_tourney_type1_pos
Global $CHOSEN_CARD_ORDER = [$FIGHT_CARD2_pos,$FIGHT_CARD1_pos,$FIGHT_CARD3_pos,$FIGHT_CARD4_pos]
Global $CHOSEN_PILLZ = [4,1,3,4]
Global $CHOSEN_PILLZ_OFFSET = 1

;loop controller
Global $run = 0
Func StartStop()
	$run = Not $run
EndFunc

Global $quit = 0
Func Quit()
	$quit = 1
EndFunc

;game controller
Global $in_fight = 0
Global $round = 0

;functions
Func AdjustToRes($pos)
	Local $adpos = [0,0]
	$adpos[0] = $pos[0]/$BASE_RES[0]*$CUSTOM_RES[0]
	$adpos[1] = $pos[1]/$BASE_RES[1]*$CUSTOM_RES[1]
	Return $adpos
EndFunc

Func URPixelSearch($pos, $color)
	Local $adpos = AdjustToRes($pos)
	Return IsArray(PixelSearch($dim[0]+$adpos[0]-2, $dim[1]+$adpos[1]-2, $dim[0]+$adpos[0]+2, $dim[1]+$adpos[1]+2, $color, 10))
EndFunc

Func URClick($pos, $n=1)
	Local $adpos = AdjustToRes($pos)
	Return MouseClick($MOUSE_CLICK_PRIMARY, $dim[0]+$adpos[0], $dim[1]+$adpos[1], $n)
EndFunc

Func ResetFight()
	$in_fight = 0
	$round = 0
EndFunc

Func Pillz()
	If $round=3 Then
		Return $CHOSEN_PILLZ[3] + 3*$CHOSEN_PILLZ_OFFSET
	Else
		Return Random($CHOSEN_PILLZ[$round]-$CHOSEN_PILLZ_OFFSET, $CHOSEN_PILLZ[$round]+$CHOSEN_PILLZ_OFFSET, 1)
	EndIf
EndFunc

;main
While 1
	If $quit Then
		ExitLoop
	ElseIf $run Then

		;init
		If Not WinExists($UR) Then
			Run("C:\Program Files (x86)\Urban Rivals\Urban Rivals.exe")
			WinWait($UR)
			Sleep(5000)
			MouseClick($MOUSE_CLICK_PRIMARY, WinGetPos($UR)[0]+WinGetPos($UR)[2]/2, WinGetPos($UR)[1]+WinGetPos($UR)[3]/2, 2)
		EndIf

		WinActivate($UR)
		WinWaitActive($UR)
		$dim = WinGetPos ($UR)
		MouseMove($dim[0]+10, $dim[1]+5)

		;main menu
		If URPixelSearch($MAIN_MENU_DETECTOR_pos, $MAIN_MENU_DETECTOR_color) Then
			URClick($MAIN_MENU_play_button_pos)
			ResetFight()
			ContinueLoop
		EndIf

		;mode select menu
		If URPixelSearch($MODE_MENU_DETECTOR_pos, $MODE_MENU_DETECTOR_color) Then
			URClick($CHOSEN_MODE)
			ResetFight()
			URClick($CHOSEN_ROOM,2)
			ContinueLoop
		EndIf

		;in-room menu
		If Not URPixelSearch($ROOM_MENU_SEARCHING_FIGHT_DETECTOR_pos, $ROOM_MENU_SEARCHING_FIGHT_DETECTOR_color) Then
			If URPixelSearch($ROOM_MENU_DETECTOR_pos, $ROOM_MENU_DETECTOR_color) Then
				URClick($ROOM_MENU_fight_button_pos)
				ResetFight()
				ContinueLoop
			EndIf
		Else
			Sleep(100)
			ContinueLoop
		EndIf

		;in-fight
		If URPixelSearch($FIGHT_TIMEOUT_DETECTOR_pos, $FIGHT_TIMEOUT_DETECTOR_color) Then ;timeout
			URClick($FIGHT_TIMEOUT_DETECTOR_pos)
			ResetFight()
			ContinueLoop
		ElseIf URPixelSearch($FIGHT_DETECTOR_pos, $FIGHT_DETECTOR_color) Then
			$in_fight = 1
			If URPixelSearch($FIGHT_TURN_DETECTOR_pos, $FIGHT_TURN_DETECTOR_color) Then
				URClick($CHOSEN_CARD_ORDER[$round])
				Sleep(750)
				If URPixelSearch($FIGHT_ADD_PILLZ_pos, $FIGHT_PLAYABLE_CARD_DETECTOR_color) Then
					URClick($FIGHT_ADD_PILLZ_pos, Pillz())
					URClick($FIGHT_FIGHT_pos)
					$round = Mod($round+1, 4)
					Sleep(4000)
					ContinueLoop
				Else
					URClick($FIGHT_UNPLAYABLE_CARD_CLICKAWAY_pos, 2)
					$round = Mod($round+1, 4)
					ContinueLoop
				EndIf
			EndIf
		EndIf
	EndIf
WEnd
msgbox(0,"Debug","Program killed, cya.")


