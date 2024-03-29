#include <AutoItConstants.au3>
#include <Array.au3>
#include <Date.au3>
#include <File.au3>

#RequireAdmin

;debug
Global $debug = 1
Global $1=0,$2=0,$3=0,$4=0,$5=0,$6=0,$7=0

;timer
Global $timer = [@HOUR, @MIN]
Global $total = 0
Global $overall_total = 0
Global $start = [@YEAR, @MON, @MDAY, @HOUR, @MIN, @SEC]
Global $end = [@YEAR, @MON, @MDAY, @HOUR, @MIN, @SEC]

;stats
Global $STATS_FILE_handle = 0
Global $STATS_COMMAND_LINE = "C:\Users\Florent\AppData\Local\Programs\Python\Python39\python.exe urbot_scraping.py stats"
Global $STATS_names = ["Views   ","Points  ","Fights  ","Wins    ","Loses   ","Draws   "]
Global $stats_start[6]
Global $stats_end[6]
Global $OUTPUT_FILE_path = @ScriptDir&"\saves\"
Global $OUTPUT_FILE_handle = 0
Global $OUTPUT_FILE_text = "=== STATS ==="&@CRLF

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
Global $TICKET_WHEEL_DETECTOR_pos=[320,60], $TICKET_WHEEL_DETECTOR_color=0x7F7F7F, $TICKET_WHEEL_BUTTON_pos=[320,60]
Global $ROLL_WHEEL_DETECTOR_pos=[310,596], $ROLL_WHEEL_DETECTOR_color=0xFFC200, $ROLL_WHEEL_button_pos=$ROLL_WHEEL_DETECTOR_pos
Global $ROLL_WHEEL_GREYED_DETECTOR_pos=$ROLL_WHEEL_DETECTOR_pos, $ROLL_WHEEL_GREYED_DETECTOR_color=0xCC9B00
Global $ROLL_WHEEL_DARKENED_DETECTOR_pos=[335,595], $ROLL_WHEEL_DARKENED_DETECTOR_color=0x280436
Global $WHEEL_WON_CARD_FLIP_pos=[410,325]
Global $NEW_CHARACTER_OBTAINED_DETECTOR_pos=[465,440], $NEW_CHARACTER_OBTAINED_DETECTOR_color = 0xFFA000, $NEW_CHARACTER_OBTAINED_button_pos=$NEW_CHARACTER_OBTAINED_DETECTOR_pos
Global $ROLLS_LEFT_DETECTOR_pos=[170,615], $ROLLS_LEFT_DETECTOR_color=0xF5AD00
Global $MODE_SELECTION_DETECTOR_pos=[30,55], $MODE_SELECTION_DETECTOR_color=0xFFFFFF
Global $MODE_SELECTION_RANKED_DETECTOR_pos=[640,60], $MODE_SELECTION_RANKED_DETECTOR_color=0xD87000, $MODE_SELECTION_RANKED_button_pos=$MODE_SELECTION_RANKED_DETECTOR_pos
Global $MODE_SELECTION_RANKED_TYPE1_DETECTOR_pos=[585,230], $MODE_SELECTION_RANKED_TYPE1_DETECTOR_color=0xD97000, $MODE_SELECTION_RANKED_TYPE1_button_pos=$MODE_SELECTION_RANKED_TYPE1_DETECTOR_pos
Global $MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos=[640,230], $MODE_SELECTION_RANKED_TYPE2_DETECTOR_color=0xD97000, $MODE_SELECTION_RANKED_TYPE2_button_pos=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos
Global $MODE_SELECTION_RANKED_TYPE3_DETECTOR_pos=[600,440], $MODE_SELECTION_RANKED_TYPE3_DETECTOR_color=0xD97000, $MODE_SELECTION_RANKED_TYPE3_button_pos=$MODE_SELECTION_RANKED_TYPE3_DETECTOR_pos
Global $MODE_SELECTION_PVP_DETECTOR_pos=[515,60], $MODE_SELECTION_PVP_DETECTOR_color=0xD87000, $MODE_SELECTION_PVP_button_pos=$MODE_SELECTION_PVP_DETECTOR_pos
Global $MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_pos=[530,280], $MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_color=0xD87000, $MODE_SELECTION_PVP_FREEFIGHT_button_pos=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_pos
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

;strategy-related variables
Global $STRATEGY_FILE_path=@ScriptDir&"\strategies\"
Global $CHOSEN_STRATEGY_FILE_name="chosen_strategy"
Global $CHOSEN_STRATEGY_FILE_handle=0
Global $CHOSEN_STRATEGY="default_strategy"
Global $STRATEGY_FILE_ext=".txt"
Global $STRATEGY_FILE_handle=0
Global $CHOSEN_MODE_pos=$MODE_SELECTION_PVP_DETECTOR_pos
Global $CHOSEN_MODE_color=$MODE_SELECTION_PVP_DETECTOR_color
Global $CHOSEN_ROOM_pos=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_pos
Global $CHOSEN_ROOM_color=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_color
Global $CARD_ORDER[0][4]
Global $PILLZ[0][4]
Global $PILLZ_OFFSET[0]
Global $STRATEGY_COUNT=0
Global $STRATEGY_INDEX=0

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
Global $reset_time = 30
Global $hard_reset_time = 68
Global $last_spin = @MIN

;speedhack
Global $SPEEDHACK_FILE_handle=0
Global $SPEEDHACK_FILE_path="\cheat_engine\speedhack.cetrainer"
Global $SPEEDHACK_KILL_FILE_path="\cheat_engine\kill_cheatengine.bat"

;counters
Global $winkill_total = 0

;loop controller
HotKeySet("{F1}", "StartStop")
HotKeySet("{F2}", "Quit")
HotKeySet("{F3}", "ToggleSpin")
HotKeySet("{F4}", "ToggleFight")
HotKeySet("{F5}", "SpinTickets")

Global $run = 0 ;runs the main loop
Func StartStop()
	$run = Not $run
EndFunc

Global $quit = 0 ;toggles quitting the bot
Func Quit()
	If Not $quit Then
		MsgBox(0,"Terminating","Terminating. Please wait.",1)
	EndIf
	$quit = 1
EndFunc

Global $do_spins = 1 ;toggles spinning
Func ToggleSpin()
	$do_spins = Not $do_spins
EndFunc

Global $do_fights = 1 ;toggles fighting
Func ToggleFight()
	$do_fights = Not $do_fights
EndFunc

Global $spin_tickets = 0
Func SpinTickets()
	$spin_tickets = Not $spin_tickets
EndFunc

;functions
Func URPixelSearch($pos, $color, $window, $shade=5) ;pixelsearch relative to a UR client.
	If $window=1 Then
		WinActive($UR1_handle)
		Return IsArray(PixelSearch($UR1_win_pos[0]+$pos[0]-2, $UR1_win_pos[1]+$pos[1]-2, $UR1_win_pos[0]+$pos[0]+2, $UR1_win_pos[1]+$pos[1]+2, $color, $shade))
	ElseIf $window=2 Then
		WinActive($UR2_handle)
		Return IsArray(PixelSearch($UR2_win_pos[0]+$pos[0]-2, $UR2_win_pos[1]+$pos[1]-2, $UR2_win_pos[0]+$pos[0]+2, $UR2_win_pos[1]+$pos[1]+2, $color, $shade))
	EndIf
EndFunc

Func URClick($pos, $window, $n=1) ;sends a click to a UR client.
	If $n<1 Then
		Return
	EndIf
	If $window=1 Then
		WinActive($UR1_handle)
		For $i = 0 To $n-1
			MouseClick($MOUSE_CLICK_PRIMARY, $UR1_win_pos[0]+$pos[0], $UR1_win_pos[1]+$pos[1], 1, 4)
			Sleep(25)
		Next
	ElseIf $window=2 Then
		WinActive($UR2_handle)
		For $i = 0 To $n-1
			MouseClick($MOUSE_CLICK_PRIMARY, $UR2_win_pos[0]+$pos[0], $UR2_win_pos[1]+$pos[1], 1, 4)
			Sleep(25)
		Next
	EndIf
EndFunc

Func Card($n) ;returns the position of the card to play at round $n.
	If $CARD_ORDER[$STRATEGY_INDEX][$n]=1 Then
		Return $CARD1_pos
	ElseIf $CARD_ORDER[$STRATEGY_INDEX][$n]=2 Then
		Return $CARD2_pos
	ElseIf $CARD_ORDER[$STRATEGY_INDEX][$n]=3 Then
		Return $CARD3_pos
	ElseIf $CARD_ORDER[$STRATEGY_INDEX][$n]=4 Then
		Return $CARD4_pos
	EndIf
EndFunc

Func Pillz($n) ;returns the number of pillz to play on card at round $n.
	If $n<3 Then
		Return Random($PILLZ[$STRATEGY_INDEX][$n]-$PILLZ_OFFSET[$STRATEGY_INDEX], $PILLZ[$STRATEGY_INDEX][$n]+$PILLZ_OFFSET[$STRATEGY_INDEX], 1)
	Else
		Return 20-$pillz_used
	EndIf
EndFunc

Func RollWheel() ;performs a spin, if it is possible.
	If $wheel_opened And Not URPixelSearch($ROLL_WHEEL_DARKENED_DETECTOR_pos, $ROLL_WHEEL_DARKENED_DETECTOR_color, 1) Then
		If URPixelSearch($ROLL_WHEEL_GREYED_DETECTOR_pos, $ROLL_WHEEL_GREYED_DETECTOR_color, 1) Then
			URClick($WHEEL_WON_CARD_FLIP_pos, 1)
			Sleep(300)
			URClick($WHEEL_WON_CARD_FLIP_pos, 1)
			Sleep(200)
		EndIf
		If $spin_tickets Then
			If URPixelSearch($TICKET_WHEEL_DETECTOR_pos, $TICKET_WHEEL_DETECTOR_color, 1) Then
				URClick($TICKET_WHEEL_BUTTON_pos, 1)
				Sleep(500)
			EndIf
		EndIf
		If URPixelSearch($ROLL_WHEEL_DETECTOR_pos, $ROLL_WHEEL_DETECTOR_color, 1, 20) And $try_to_spin Then
			URClick($ROLL_WHEEL_button_pos, 1)
		EndIf
	EndIf
EndFunc

Func _GetHwndFromPID($PID) ;returns the handle of a window given it's PID ;https://www.autoitscript.com/wiki/FAQ#How_can_I_get_a_window_handle_when_all_I_have_is_a_PID.3F
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

Func OpenClient($n=0) ;opens one or both UR clients.
	If $n=0 Or $n=1 Then
		If Not WinExists($UR1_handle) Then
			ShellExecute(@ScriptDir&$SPEEDHACK_KILL_FILE_path)
			$UR1_pid = Run("C:\Program Files (x86)\Urban Rivals\Urban Rivals.exe")
			Sleep(3000)
			$UR1_handle = _GetHwndFromPID($UR1_pid)
			$UR1_win_pos = WinGetPos($UR1_handle)
			WinMove($UR1_handle, "", (@DesktopWidth-2*$UR1_win_pos[2])/3,  (@DesktopHeight-$UR1_win_pos[3])/2)
			$UR1_win_pos = WinGetPos($UR1_handle)
			$intro1_skipped = 0
			$wheel_opened = 0
			$try_to_spin = 1
			$SPEEDHACK_FILE_handle = FileOpen(@ScriptDir&$SPEEDHACK_FILE_path, 2)
			FileWrite($SPEEDHACK_FILE_handle, '<?xml version="1.0" encoding="utf-8"?><CheatTable CheatEngineTableVersion="34"><CheatEntries/><UserdefinedSymbols/><LuaScript>openProcess('&$UR1_pid&')'&@CRLF&'speedhack_setSpeed(1.70)</LuaScript></CheatTable>')
			FileClose($SPEEDHACK_FILE_handle)
			ShellExecute(@ScriptDir&$SPEEDHACK_FILE_path)
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

Func URWinKill($h) ;kills a UR client.
	WinKill($h)
	$winkill_total = $winkill_total + 1
	$to_winkill = 0
	$to_immediatly_winkill = 0
	$total = 0
	$random_bug_fight_not_expiring = 0
	$random_bug_fight_not_launching = 0
	$ennemy_left = 0
	Sleep(1000)
EndFunc

Func LoadStrategy() ;loads a strategy file located under ./strategie

	;reads chosen_strategy_filename strategy filename in chosen_strategy.txt
	$CHOSEN_STRATEGY_FILE_handle = FileOpen($STRATEGY_FILE_path&$CHOSEN_STRATEGY_FILE_name&$STRATEGY_FILE_ext)
	$CHOSEN_STRATEGY=FileReadLine($CHOSEN_STRATEGY_FILE_handle, 1)
	FileClose($CHOSEN_STRATEGY_FILE_handle)

	;extract chosen strategy from chosen_strategy_filename.txt
	$STRATEGY_FILE_handle = FileOpen($STRATEGY_FILE_path&$CHOSEN_STRATEGY&$STRATEGY_FILE_ext)
	$STRATEGY_COUNT = _FileCountLines($STRATEGY_FILE_handle)-1
	ReDim $CARD_ORDER[$STRATEGY_COUNT][4]
	ReDim $PILLZ[$STRATEGY_COUNT][4]
	ReDim $PILLZ_OFFSET[$STRATEGY_COUNT]

	Local $tmp_type = FileReadLine($STRATEGY_FILE_handle, 1)

	For $i=2 To _FileCountLines($STRATEGY_FILE_handle)+1
		Local $tmp_strategy_split = StringSplit(FileReadLine($STRATEGY_FILE_handle, $i), ' ', 2)
		Local $tmp_card_order = StringSplit($tmp_strategy_split[0], '', 2)
		Local $tmp_pillz_order = StringSplit($tmp_strategy_split[1], '', 2)
		For $j=0 To 3
			$CARD_ORDER[$i-2][$j]=$tmp_card_order[$j]
			$PILLZ[$i-2][$j]=$tmp_pillz_order[$j]
		Next
		$PILLZ_OFFSET[$i-2]=$tmp_strategy_split[2]
	Next
	FileClose($STRATEGY_FILE_handle)

	;parse for what room to play in
	$tmp_type_split = StringSplit($tmp_type, '', 2)
	Switch $tmp_type_split[0]
		Case 'f'
			$CHOSEN_MODE_pos=$MODE_SELECTION_PVP_DETECTOR_pos
			$CHOSEN_MODE_color=$MODE_SELECTION_PVP_DETECTOR_color
			$CHOSEN_ROOM_pos=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_pos
			$CHOSEN_ROOM_color=$MODE_SELECTION_PVP_FREEFIGHT_DETECTOR_color
		Case 't'
			Switch $tmp_type_split[1]
				Case '1'
					$CHOSEN_MODE_pos=$MODE_SELECTION_RANKED_DETECTOR_pos
					$CHOSEN_MODE_color=$MODE_SELECTION_RANKED_DETECTOR_color
					$CHOSEN_ROOM_pos=$MODE_SELECTION_RANKED_TYPE1_DETECTOR_pos
					$CHOSEN_ROOM_color=$MODE_SELECTION_RANKED_TYPE1_DETECTOR_color
				Case '2'
					$CHOSEN_MODE_pos=$MODE_SELECTION_RANKED_DETECTOR_pos
					$CHOSEN_MODE_color=$MODE_SELECTION_RANKED_DETECTOR_color
					$CHOSEN_ROOM_pos=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_pos
					$CHOSEN_ROOM_color=$MODE_SELECTION_RANKED_TYPE2_DETECTOR_color
				Case '3'
					$CHOSEN_MODE_pos=$MODE_SELECTION_RANKED_DETECTOR_pos
					$CHOSEN_MODE_color=$MODE_SELECTION_RANKED_DETECTOR_color
					$CHOSEN_ROOM_pos=$MODE_SELECTION_RANKED_TYPE3_DETECTOR_pos
					$CHOSEN_ROOM_color=$MODE_SELECTION_RANKED_TYPE3_DETECTOR_color
			EndSwitch
		Case Else
			MsgBox(0,"Error","Error loading strategy : invalid room.")
	EndSwitch
EndFunc

Func TimerUpdate() ;updates the timer and associated variables.
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

Func Stats() ;retrieve the stats of current user.
	Local $ret[6]
	RunWait($STATS_COMMAND_LINE, @ScriptDir&"\python", @SW_HIDE)
	Local $STATS_FILE_path = @ScriptDir&"\python\data\player_page_data.txt"
	$STATS_FILE_handle = FileOpen($STATS_FILE_path)
	For $i = 0 To Number(UBound($ret))-1
		$ret[$i] = FileReadLine($STATS_FILE_handle, $i+1)
	Next
	FileDelete($STATS_FILE_path)
	Return $ret
EndFunc

; === main ===
MsgBox(0,"Controls","F1 - start/stop (default : stopped)"&@CRLF&"F2 - quit"&@CRLF&"F3 - toggle spinning (default : ON)"&@CRLF&"F4 - toggle fighting (default : ON)"&@CRLF&"F5 - Spin tickets (default :OFF)", 5)
$timer[0] = @HOUR
$timer[1] = @MIN
LoadStrategy()
$stats_start = Stats()
While 1

	;avoids too many loops
	Sleep(200)

	;in case F2 was pressed
	If $quit Then
		ExitLoop

	;in case F1 was pressed
	ElseIf $run Then

		;clock gestion
		TimerUpdate()
		If $total >= $reset_time Then
			$to_winkill = 1
		EndIf
		If $total >= $hard_reset_time Then
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
				If $debug Then
					$1=$1+1
				Endif
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
						EndIf
					If URPixelSearch($WHEEL_DETECTOR2_pos, $WHEEL_DETECTOR2_color, 1) Then
						URClick($WHEEL_button2_pos, 1)
						Sleep(500)
					EndIf
				EndIf
			EndIf

			;if new character unlocked
			If URPixelSearch($NEW_CHARACTER_OBTAINED_DETECTOR_pos, $NEW_CHARACTER_OBTAINED_DETECTOR_color, 1) Then
				URClick($NEW_CHARACTER_OBTAINED_button_pos, 1)
				Sleep(500)
			EndIf

			;if fighting client is not opened, try to spin once every minutes
			If Not $do_fights And Not $try_to_spin And $last_spin <> @MIN Then
				$try_to_spin = 1
				$last_spin = @MIN
			EndIf

			RollWheel()

			;no more spins
			If URPixelSearch($ENNEMY_LEFT_DETECTOR_pos, $ENNEMY_LEFT_DETECTOR_color, 1) And Not $spin_tickets Then
				URClick($ENNEMY_LEFT_button_pos, 1)
				$try_to_spin = 0
				Sleep(250)
			EndIf

			;if client is connected and fighting, reset
			If URPixelSearch($FIGHT_DETECTOR_pos, $FIGHT_DETECTOR_color, 1) Then
				$to_winkill = 1
			EndIf
		EndIf

		;CLIENT 2 : FIGHTING
		If $do_fights Then

			;open client
			OpenClient(2)

			;reset
			If $to_immediatly_winkill Then
				If $debug Then
					$2=$2+1
				EndIf
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
					URClick($CHOSEN_ROOM_pos, 2)
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
					If $debug Then
						$3=$3+2
					EndIf
					URWinKill($UR1_handle)
					URWinKill($UR2_handle)
					ContinueLoop
				EndIf
				If URPixelSearch($SEARCHING_FIGHT_DETECTOR_pos, $SEARCHING_FIGHT_DETECTOR_color, 2) Then
					$random_bug_fight_not_launching = 0
				Else
					If $random_bug_fight_not_launching >= 10 Then
						$random_bug_fight_not_launching = 0
						If $debug Then
							$4=$4+1
						EndIf
						URWinKill($UR2_handle)
					Else
						$try_to_spin = 1
						$init = 1
						$intro1_skipped = 1
						$intro2_skipped = 1
						$mode_selection = 1
						$mode_selected = 1
						$in_fight = 0
						$round = 0
						$pillz_used = 0
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
				$STRATEGY_INDEX=Random(0,$STRATEGY_COUNT-1,1)
			EndIf

			;ennemy left // already in matchmaking
			If $ennemy_left < 90 Then
				If URPixelSearch($ENNEMY_LEFT_DETECTOR_pos, $ENNEMY_LEFT_DETECTOR_color, 2) Then
					$ennemy_left = $ennemy_left + 1
					URClick($ENNEMY_LEFT_button_pos, 2)
					Sleep(1000)
				Else
					$ennemy_left = 0
				EndIf
				Else
				If $debug Then
					$5=$5+1
				EndIf
				URWinKill($UR2_handle)
			EndIf

			;in fight
			If $in_fight Then

				;resets the detector for fight not launching
				$random_bug_fight_not_launching = 0

 				;detects fights that randomly timeout without ending
				If URPixelSearch($FIGHT_EXPIRED_BUG_DETECTOR_pos, $FIGHT_EXPIRED_BUG_DETECTOR_color, 2) Then
					If $random_bug_fight_not_expiring > 20 Then
						$random_bug_fight_not_expiring = 0
						If $debug Then
							$6=$6+1
						EndIf
						URWinKill($UR2_handle)
					Else
						$random_bug_fight_not_expiring = $random_bug_fight_not_expiring + 1
						Sleep(1500)
					EndIf
				Else
					$random_bug_fight_not_expiring = 0
				EndIf

				;player turn
				If URPixelSearch($MY_TURN_DETECTOR_pos, $MY_TURN_DETECTOR_color, 2, 20) Then
					Local $p = Pillz($round)
					$pillz_used = $pillz_used + $p
					Local $timeout = 0
					Local $delay_generator = Random(0, 5, 1)
					If $delay_generator = 0 Then
						Local $human_delay = Random(0, 5000, 1)
						Sleep($human_delay)
					EndIf
					While URPixelSearch($MY_TURN_DETECTOR_pos, $MY_TURN_DETECTOR_color, 2, 20)
						If $timeout>=6 Then
							If $debug Then
								$7=$7+1
							EndIf
							URWinKill($UR2_handle)
						EndIf
						URClick(Card($round), 2)
						Sleep(750)
						If URPixelSearch($PLAYABLE_CARD_DETECTOR_pos, $PLAYABLE_CARD_DETECTOR_color, 2) Then
							URClick($CARD_ADD_PILLZ_pos, 2, $p)
							URCLICK($PLAY_CARD_pos, 2)
							If $do_spins Then
								RollWheel()
							MouseMove(@DesktopWidth/2, @DesktopHeight/2, 4)
							EndIf
							Sleep(3250)
						EndIf
						$timeout=$timeout+1
					WEnd
					MouseMove(@DesktopWidth/2, @DesktopHeight/2, 4)
					$round = Mod($round+1, 4)
					If $spin_tickets Then
						RollWheel()
					EndIf
				EndIf
			EndIf
		EndIf
	EndIf
WEnd
ShellExecute(@ScriptDir&$SPEEDHACK_KILL_FILE_path)
$stats_end = Stats()
$end[0] = @YEAR
$end[1] = @MON
$end[2] = @MDAY
$end[3] = @HOUR
$end[4] = @MIN
$end[5] = @SEC
$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Start    "&$start[0]&"/"&$start[1]&"/"&$start[2]&" "&$start[3]&":"&$start[4]&":"&$start[5]&@CRLF
$OUTPUT_FILE_text = $OUTPUT_FILE_text&"End      "&$end[0]&"/"&$end[1]&"/"&$end[2]&" "&$end[3]&":"&$end[4]&":"&$end[5]&@CRLF
$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Duration            "
If int($overall_total/60) < 10 Then
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&" "
EndIf
$OUTPUT_FILE_text = $OUTPUT_FILE_text&int($overall_total/60)&":"
If Mod($overall_total, 60) < 10 Then
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"0"
EndIf
$OUTPUT_FILE_text = $OUTPUT_FILE_text&Mod($overall_total, 60)&":00"&@CRLF
For $i = 0 To Number(UBound($STATS_names))-1
	Local $tmp = $stats_end[$i] - $stats_start[$i]
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&$STATS_names[$i]&" "&$tmp&@CRLF
Next
If $stats_end[2]-$stats_start[2] = 0 Then
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"WR       N/A"&@CRLF
Else
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"WR       "&Round((($stats_end[3]-$stats_start[3])/($stats_end[2]-$stats_start[2]))*100,1)&"%"&@CRLF
EndIf
If $debug Then
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"=== DEBUG ==="&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Time until next reset (min)                           "&$reset_time-$total&"min."&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkills $timer > "&$reset_time&"                                  "&$3&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkills $timer > "&$hard_reset_time&"                                  "&$2&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkills from fight not launching                     "&$4&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkills from ennemy left/already in matchmaking      "&$5&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkills from fight not expiring                      "&$6&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkills from unable to play card                     "&$7&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkills from your missions panel on wheeling client  "&$1&@CRLF
	$OUTPUT_FILE_text = $OUTPUT_FILE_text&"Winkill total                                         "&$winkill_total&@CRLF
EndIf
$OUTPUT_FILE_text = $OUTPUT_FILE_text&"============="


$OUTPUT_FILE_path = $OUTPUT_FILE_path&"stats_"&@YEAR&"-"&@MON&"-"&@MDAY&"_"&@HOUR&"h"&@MIN&".txt"
$OUTPUT_FILE_handle = FileOpen($OUTPUT_FILE_path, 1)
FileWrite($OUTPUT_FILE_handle, $OUTPUT_FILE_text)
FileClose($OUTPUT_FILE_handle)

MsgBox(0,"Terminated","Bot terminated.",1)