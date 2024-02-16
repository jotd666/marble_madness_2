; Jim Power slave
	INCDIR	Include:
	INCLUDE	whdload.i
	INCLUDE	whdmacros.i
;CHIP_ONLY
	IFD	CHIP_ONLY
CHIPMEMSIZE = $200000
EXPMEMSIZE = 0
	ELSE
CHIPMEMSIZE = $200000
EXPMEMSIZE = $200000
	ENDC
	
_base	SLAVE_HEADER					; ws_security + ws_id
	dc.w	17					; ws_version (was 10)
	dc.w	WHDLF_NoError|WHDLF_ReqAGA|WHDLF_Req68020
	dc.l	CHIPMEMSIZE					; ws_basememsize
	dc.l	0					; ws_execinstall
	dc.w	start-_base		; ws_gameloader
	dc.w	_data-_base					; ws_currentdir
	dc.w	0					; ws_dontcache
_keydebug
	dc.b	$0					; ws_keydebug
_keyexit
	dc.b	$59					; ws_keyexit
_expmem
	dc.l	EXPMEMSIZE					; ws_expmem
	dc.w	_name-_base				; ws_name
	dc.w	_copy-_base				; ws_copy
	dc.w	_info-_base				; ws_info
    dc.w    0     ; kickstart name
    dc.l    $0         ; kicksize
    dc.w    $0         ; kickcrc
    dc.w    _config-_base
;---
_config
;	dc.b    "C1:X:invincibility:0;"    
;	dc.b    "C1:X:infinite lives:1;"    
;	dc.b    "C1:X:reveal sol tower:2;"    
;	dc.b    "C1:X:reveal bonus flag:3;"    
;	dc.b    "C2:L:skill level:normal,easy,hard,hardest;"
;	dc.b    "C3:X:flag awards bonus life:0;"    
;	dc.b    "C3:X:no in-game music:1;"    
;	dc.b    "C3:X:play Super Xevious:2;"
;	dc.b    "C4:L:lives:3,1,2,5;"
;	dc.b	"C5:L:start area:1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16;"
	dc.b	0

	IFD BARFLY
	DOSCMD	"WDate  >T:date"
	ENDC

DECL_VERSION:MACRO
	dc.b	"1.1"
	IFD BARFLY
		dc.b	" "
		INCBIN	"T:date"
	ENDC
	IFD	DATETIME
		dc.b	" "
		incbin	datetime
	ENDC
	ENDM
_data   dc.b    "data",0
_name	dc.b	'Marble Madness 2',0
_copy	dc.b	'1991 Atari Games',0
_info
    dc.b	"Amiga port by JOTD",0
	dc.b	0
_kickname   dc.b    0
;--- version id

    dc.b	0
    even

start:
	LEA	_resload(PC),A1
	MOVE.L	A0,(A1)
	move.l	a0,a2

	move.l	_expmem(pc),d0
	lea		_gameram(pc),a0
	move.l	d0,(a0)
	add.l	#$4000,d0
	lea		_gameram_2(pc),a0
	add.l	#$8000,d0
	move.l	d0,(a0)
	
	;enable cache
	;move.l	#WCPUF_All,d1
	;jsr	(resload_SetCPU,a2)

	lea		exe(pc),a0
	move.l	_progbase(pc),a1
	add.w	#$100,a1		; skip vectors
	move.l	#$7FF00,d0
	move.l	#$100,d1
	jsr		(resload_LoadFileOffset,a2)
	
	; relocate RAM
	lea		ram_relocs(pc),a0
	move.l	_progbase(pc),a1
.reloc:
	move.l	(a0)+,d0
	bmi.b	.out
	move.l	(a1,d0.l),d1
	sub.l	#$7f8000,d1
	add.l	_gameram(pc),d1
	move.l	d1,(a1,d0.l)
	bra.b	.reloc
.out
	lea		pl_main(pc),a0
	jsr		(resload_Patch,a2)
	
	; install VBL
	move.l	_progbase(pc),a1
	add.l	#$077f4,a1
	move.l	a1,$6C.W
	
	move.w	#$C020,_custom+intena
	move.w	#$2700,SR

	move.l	_expmem(pc),a7
	add.l	#EXPMEMSIZE,a7
	
	move.l	_progbase(pc),a1
	add.w	#$9cc,a1
	blitz
	jmp		(a1)
	
	

install_palette:
	rts
	

set_palette_part:
	rts


read_port_600021_d2:
	moveq	#0,d2
	rts
	
and_port_600021_d1:
	moveq	#0,d1
	rts
read_port_600020_d1:
	moveq	#0,d1
	rts
read_port_600021_d1:
	moveq	#0,d1
	rts

vblank_end:
	MOVEM.L	(A7)+,D0/A0-A1		;0783c: 4cdf0301
	move.w	#$20,_custom+intreq
	RTE				;07840: 4e73

get_second_ram_block:
	move.l	_gameram_2(pc),a0
	rts
	
clear_video_ram:
	rts
	
ram_relocs:
	include	"ram_relocs.s"
	dc.l	-1
pl_main:
	include	"patchlist.s"
	
;  success,error = resload_LoadFileOffset(size, offset, name, address)
;          D0     D1                        D0     D1     A0      A1
;         BOOL   ULONG                          ULONG  ULONG  CPTR    APTR	

    rts

_gameram:
	dc.l	0
_gameram_2:
	dc.l	0
	
_resload:
	dc.l	0
_progbase:
    dc.l    0
exe:
	dc.b	"prog",0
	