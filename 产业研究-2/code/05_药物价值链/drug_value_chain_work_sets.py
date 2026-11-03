# stage -> list of (key, branch, grade)  grade like 'A2', 'B3', 'C2', 'X' (excluded after screening)
S={}
S['init_lookup']="Won18:2:A1 Dim16:3:A1 Wou20:3:A1 Pra17:3:A2 Ser24:3:A2 Ser16b:3:A2 Jay24b:4:A2 Hay14b:2:A1 Pau10:3:A2 Nuy21:5:A2 Jay22:4:B2 Sch21c:3:B1 Dow19:2:A2 Bro21:1:A2 Sca12:3:B2 Dim03:3:A1 Mul16:2:B2"
S['init_ds']="Mul25:3:A2 Zho25f:2:A2 Sch25:2:A3 Ren21b:3:B2 Oka25:1:A2 Dim10:2:A2 Dim07:3:A2 Moo20c:3:A2 Moo18b:3:A2 Yam21b:2:A2 Lo20:2:A2 Dim20b:1:A2 Pam20:2:A2 Gou18:3:A2 Els24:2:A2 Hen23:3:B2 Ada06:3:A2 Wou24c:1:A2 Mor11:3:B2 Ada10:3:A2 Pam11:2:A2 War15c:2:A2 Mes12b:3:A3 Fer24b:3:B2 Bre19c:1:A2 Pro13:2:A2 Sim21c:3:B2 Dim01:2:A2 Jay19:3:A2 Dim04:3:A2 Cum21:3:A2 Dim91:3:A2 Kan26b:2:A2 Dhe20:2:A2 Sch25b:2:A2 Abr06:1:A2 Hed26:1:A2 Tak18:2:B2"
S['init_sem']="Fer26b:4:B2 Haq26:4:A2 Haq26b:4:A3 Ret24:4:B3 Mun21:4:B3 Ver20c:4:B2 Joy25:5:B2 Soo21:5:A2 Sch18f:5:B2 Kak20:5:A3 Fel21c:5:A2 Con21:5:B3 Qat24:5:A2 Yan20e:5:A2 Dus17:5:A2 Mat23c:5:A2 Vil22:5:B2 Vil19:5:B2 How08:5:A2 Pia02:5:B2 Bal17:5:B3 Ber16d:5:A3 Coc04:5:B2 Sch25c:5:C2 Lou21:4:A2 Wu25j:4:A2"
S['r1']="Jen23:3:A2 Wou22:3:A2 Fra19:3:B2 Dim13:2:A2 Lig11:3:B2 Chi15:3:B2 Dim12b:3:B2 Dan03:2:A2 Dim95d:2:A2 Bac17:2:B3 Bar13b:1:B3 Cle20:5:A3 Ben20b:4:B2 Ali23b:4:B2 Wal24b:4:A2 Fre26b:4:A2 Fre25:4:A2 Kha26:4:B2 Dha25b:4:B2 Has23c:4:B2 Ben26:4:B2 Zha25ap:4:B2 Wil24:4:B2 Led20:5:A2 Ber15b:5:A2 Hig06:5:A2 Sch16e:5:B2 Gra12d:5:A2 Dia22:5:A2 Dia24:5:A2 Gra23b:5:B3 Nor26:5:B2 Ful23:5:B2 Gue05:5:B3 Avo15:3:C2"
S['r2']="Mah22b:2:A2 Par25f:2:A2 Has22b:2:A2 Yam26:2:A2 Sch26:2:B2 Ver09:3:B2 Dim07b:3:A2 Str94:2:A2 Bie92:2:A2 Her24:1:B2 Wil24b:1:B2 Woo21c:5:A2 Kri18b:2:B2 Rin17:5:B2 Sca16:2:B2 Low12:5:B2 Mas12:5:B2 Shi14:5:B2 Dan07:5:A2 Cec14:5:B2 Heg20:2:B3 Wou24:3:C2 Fra03:3:C2"
S['r3']="Bar18b:1:B3 Kan24d:5:A2 Han15:1:A2 Sam11:5:A2 Sch23d:3:B2 Lig12:3:B2 Shi14d:3:B2"
S['r4']="Cle23:5:A2 Nay19:5:A2 Fow24:5:A2 Sim21d:5:B2 Baz25:4:A2 Kan25e:5:A2 Lo22:5:B2 Gra12e:5:A2 Sch21e:3:A2 Too12:5:A2 Lae21b:3:B2 Smi19:5:B2 Coc96:5:A2"
S['r5']="Sch22c:5:A2 Zho23f:5:A2 Fow26:5:A2 Ste11:5:A2 Cha16c:5:A2 Gia11:3:B2 Bar12:3:B2 Ang23:5:B2 Nay21:5:A2 Con20c:5:B2"
P={k:[tuple(x.split(':')) for x in v.split()] for k,v in S.items()}
