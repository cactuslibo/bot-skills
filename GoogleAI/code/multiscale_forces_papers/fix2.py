import re
L=open("list.md").read().split("\n")
def row(id_,f):
  for i,l in enumerate(L):
    c=l.split(" | ")
    if len(c)>10 and c[1]==id_:
      L[i]=f(c) if True else l; return
  raise SystemExit(id_)
def S(id_,**kw):
  idx=dict(title=2,auth=3,year=4,venue=5,doi=6,point=10,cr=12)
  def f(c):
    for k,v in kw.items(): c[idx[k]]=v
    return " | ".join(c)
  row(id_,f)
S("Den12",year="2014",venue="Electrostatics of Soft and Disordered Matter (Pan Stanford/CRC, 2014), pp.221–240；预印本 arXiv:1212.1758",doi="10.1201/b15597-18",point="带电胶体从PB到有效势（DOI已更正：原-19为Dobnikar章）",cr="OK(R2核验)")
S("Cah13",title="Free Energy of a Nonuniform System. I. Interfacial Free Energy",year="1958",venue="J. Chem. Phys. 28, 258–267",doi="10.1063/1.1744102",point="非均匀体系自由能（Cahn-Hilliard）；III 篇另见 10.1063/1.1730447 (J. Chem. Phys. 31, 688, 1959)；ID沿用Cah13",cr="OK(R2核验)")
S("Sch22",year="2022 (CR:2023)",venue="ACS Polymers Au 3, 28–58",doi="10.1021/acspolymersau.2c00049",point="高分子多尺度挑战（DOI已更正）",cr="OK(R2核验)")
S("Lik13",venue="Proc. Int. School Phys. “Enrico Fermi” Course 184 (IOS/SIF, 2013) pp.1–60（GoogleAI 建议 DOI 10.3254/978-1-61499-278-3-1 为 mEDRA 注册、Crossref 404，未采纳）",cr="未核实(Crossref无)")
S("Bra03",title="Statistical mechanics of inhomogeneous model colloid–polymer mixtures",auth="J. M. Brader, R. Evans, M. Schmidt",venue="Mol. Phys. 101, 3349–3384",doi="10.1080/0026897032000174263",cr="OK(R2核验)")
S("Bou23",venue="SIAM J. Appl. Math. 83, 2354–2389",doi="10.1137/23M1553315",cr="OK(R2核验)")
S("Sol15",title="Pressure and Phase Equilibria in Interacting Active Brownian Spheres",auth="A. P. Solon, J. Stenhammar, R. Wittkowski, M. Kardar, Y. Kafri, M. E. Cates, J. Tailleur",venue="Phys. Rev. Lett. 114, 198301",doi="10.1103/PhysRevLett.114.198301",point="活性布朗球压强与相平衡（原题为 Bertin 的 Physics Viewpoint 标题，已更正）",cr="OK(R2核验)")
S("Mcn19c",venue="PhD thesis, Harvard University (2019)；DASH URN-3:HUL.InstRepos:42013165",point="光操控测量生物图案（学位论文，无DOI，真实存在）")
S("Tur52",venue="Phil. Trans. R. Soc. Lond. B 237, 37–72")
S("Den07",venue="Nanostructured Soft Matter (Springer, NanoScience and Technology, 2007) pp.395–433")
S("Mul05",venue="Adv. Polym. Sci. 185 (2005) pp.1–58（DOI 为卷/章级，Crossref 返回该题名）")
S("Edw65",venue="Proc. Phys. Soc. 85, 613–624")
S("Fre05",venue="Oxford University Press（专著, 2005）")
new=[("Mor65","Transport, Collective Motion, and Brownian Motion","H. Mori","1965","Prog. Theor. Phys. 33, 423","10.1143/PTP.33.423","跨尺度动力学","Mori投影算符/GLE","A1","投影算符推导广义朗之万方程（记忆核）","no"),
("Zwa60","Ensemble Method in the Theory of Irreversibility","R. Zwanzig","1960","J. Chem. Phys. 33, 1338","10.1063/1.1731409","跨尺度动力学","Zwanzig投影算符","A1","系综投影法推导不可逆主方程","no"),
("Zwa61","Memory Effects in Irreversible Thermodynamics","R. Zwanzig","1961","Phys. Rev. 124, 983","10.1103/PhysRev.124.983","跨尺度动力学","Mori-Zwanzig记忆效应","A1","粗粒变量不可逆热力学中的记忆效应","no"),
("Eva79","The nature of the liquid-vapour interface and other topics in the statistical mechanics of non-uniform, classical fluids","R. Evans","1979","Adv. Phys. 28, 143","10.1080/00018737900101365","介观/液体","经典DFT","A1","经典密度泛函理论奠基综述","no"),
("Mar99","Dynamic density functional theory of fluids","U. M. B. Marconi, P. Tarazona","1999","J. Chem. Phys. 110, 8032","10.1063/1.478705","跨尺度动力学","DDFT","A1","由朗之万动力学推导DDFT","yes"),
("Asa54","On Interaction between Two Bodies Immersed in a Solution of Macromolecules","S. Asakura, F. Oosawa","1954","J. Chem. Phys. 22, 1255","10.1063/1.1740347","熵/排空力","AO排空势","A1","大分子溶液中两物体排空吸引（AO模型）","no"),
("Asa58","Interaction between particles suspended in solutions of macromolecules","S. Asakura, F. Oosawa","1958","J. Polym. Sci. 33, 183","10.1002/pol.1958.1203312618","熵/排空力","AO排空势","A1","AO排空相互作用完整推导","no"),
("Der41","Theory of the stability of strongly charged lyophobic sols and of the adhesion of strongly charged particles in solutions of electrolytes","B. Derjaguin, L. Landau","1941 (CR:1993重印)","Prog. Surf. Sci. 43, 30（1941 Acta Physicochim. URSS 重印）","10.1016/0079-6816(93)90013-L","静电/胶体","DLVO","A1","DLVO理论：双电层斥力+范德华引力","no"),
("Ver47","Theory of the Stability of Lyophobic Colloids.","E. J. W. Verwey","1947","J. Phys. Colloid Chem. 51, 631","10.1021/j150453a001","静电/胶体","DLVO","A1","疏液胶体稳定性理论（DLVO之V）","no"),
("Dzy61","The general theory of van der Waals forces","I. E. Dzyaloshinskii, E. M. Lifshitz, L. P. Pitaevskii","1961","Adv. Phys. 10, 165","10.1080/00018736100101281","范德华/Casimir","Lifshitz理论","A1","介质中范德华力的普适场论（DLP）","no"),
("Wei79","Phenomenological Lagrangians","S. Weinberg","1979","Physica A 96, 327","10.1016/0378-4371(79)90223-1","微观/核力","EFT","A1","有效场论唯象拉氏量原理","no"),
("Wil71","Renormalization Group and Critical Phenomena. I. Renormalization Group and the Kadanoff Scaling Picture","K. G. Wilson","1971","Phys. Rev. B 4, 3174","10.1103/PhysRevB.4.3174","跨尺度总框架","重整化群","A1","重整化群与Kadanoff标度图像","no"),
("Wil74","The renormalization group and the ε expansion","K. G. Wilson, J. Kogut","1974","Phys. Rep. 12, 75","10.1016/0370-1573(74)90023-4","跨尺度总框架","重整化群/ε展开","A1","RG与ε展开系统综述","no"),
("Bra09","Germline P Granules Are Liquid Droplets That Localize by Controlled Dissolution/Condensation","C. P. Brangwynne, ..., A. A. Hyman","2009","Science 324, 1729","10.1126/science.1172046","凝聚体","实验+相分离","B1","P颗粒为液滴，受控溶解/凝聚定位","no"),
("Hym14","Liquid-Liquid Phase Separation in Biology","A. A. Hyman, C. A. Weber, F. Jülicher","2014","Annu. Rev. Cell Dev. Biol. 30, 39","10.1146/annurev-cellbio-100913-013325","凝聚体","LLPS理论综述","A2","生物液-液相分离物理综述","no"),
("Vic95","Novel Type of Phase Transition in a System of Self-Driven Particles","T. Vicsek, ..., O. Shochet","1995","Phys. Rev. Lett. 75, 1226","10.1103/PhysRevLett.75.1226","活性物质","Vicsek模型","A1","自驱动粒子集体运动相变（Vicsek模型）","yes"),
("Hoh77","Theory of dynamic critical phenomena","P. C. Hohenberg, B. I. Halperin","1977","Rev. Mod. Phys. 49, 435","10.1103/RevModPhys.49.435","跨尺度动力学","动力学临界/模型A-B","A1","动力学临界现象（Model A/B…）","no"),
("She08","The relative entropy is fundamental to multiscale and inverse thermodynamic problems","M. S. Shell","2008","J. Chem. Phys. 129, 144108","10.1063/1.2992060","分子→CG","相对熵粗粒化","A1","相对熵作为多尺度/逆问题基本量","no")]
last=max(i for i,l in enumerate(L) if re.match(r"\| \d+ \| ",l))
rows=[f"| {161+j} | "+" | ".join(n)+" | OK(R2核验) | R4-GAI |" for j,n in enumerate(new)]
L[last+1:last+1]=rows
open("list.md","w").write("\n".join(L))
