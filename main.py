from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import NumericProperty, StringProperty
from pathlib import Path
from datetime import datetime
import random, json

SYMBOLS=["🎃","🧙","🧛","🧪","👹","💀","🦇","🌙","🔥"]
VALUES={"🎃":5,"🧙":8,"🧛":10,"🧪":12,"👹":15,"💀":20,"🦇":30,"🌙":40,"🔥":60}

class Game(BoxLayout):
    credits=NumericProperty(0); bet=NumericProperty(1); lines=NumericProperty(3)
    prize=NumericProperty(0); message=StringProperty("BOA SORTE! 👻")
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(8), spacing=dp(6), **kwargs)
        self.spinning=False; self.auto=False
        self.reels=[[random.choice(SYMBOLS) for _ in range(3)] for _ in range(5)]
        self.history=[]
        self.file=Path(App.get_running_app().user_data_dir)/"cardiftx_v5.json"
        self.load(); self.build_ui(); self.refresh()
    def build_ui(self):
        self.add_widget(Label(text="[b]🎃 HALLOWEEN SLOT V5[/b]",markup=True,font_size=dp(25),size_hint_y=None,height=dp(50)))
        info=BoxLayout(size_hint_y=None,height=dp(48)); self.lc=Label(); self.lb=Label(); self.lp=Label()
        for w in (self.lc,self.lb,self.lp): info.add_widget(w)
        self.add_widget(info)
        self.grid=GridLayout(cols=5,rows=3,spacing=dp(4)); self.cells=[]
        for r in range(3):
            for c in range(5):
                x=Label(text=self.reels[c][r],font_size=dp(38)); self.cells.append(x); self.grid.add_widget(x)
        self.add_widget(self.grid)
        self.msg=Label(font_size=dp(18),size_hint_y=None,height=dp(42)); self.add_widget(self.msg)
        controls=GridLayout(cols=4,rows=3,spacing=dp(5),size_hint_y=None,height=dp(165))
        buttons=[("− APOSTA",self.bet_down),("+ APOSTA",self.bet_up),("LINHAS",self.lines_up),("🎰 JOGAR",self.spin),("AUTO",self.toggle_auto),("🏆 PRÉMIOS",self.paytable),("📜 HISTÓRICO",self.history_popup),("💾 GUARDAR",self.save),("ZERAR",self.reset),("⛶ ECRÃ",self.fullscreen),("SAIR",App.get_running_app().stop),("INFO",self.info)]
        for text,fn in buttons:
            b=Button(text=text,font_size=dp(13)); b.bind(on_release=lambda _,f=fn:f()); controls.add_widget(b)
        self.add_widget(controls)
        self.add_widget(Label(text="CARDIFTX V5 • Android • créditos virtuais • sem USB",font_size=dp(10),size_hint_y=None,height=dp(24)))
    def refresh(self):
        self.lc.text=f"CRÉDITOS\n{self.credits}"; self.lb.text=f"APOSTA {self.bet}\nLINHAS {self.lines}"; self.lp.text=f"PRÉMIO\n{self.prize}"; self.msg.text=self.message
        for i,x in enumerate(self.cells): x.text=self.reels[i%5][i//5]
    def bet_down(self):
        if not self.spinning:self.bet=max(1,self.bet-1);self.refresh()
    def bet_up(self):
        if not self.spinning:self.bet=min(10,self.bet+1);self.refresh()
    def lines_up(self):
        if not self.spinning:self.lines=self.lines%3+1;self.refresh()
    def toggle_auto(self):
        self.auto=not self.auto; self.message="AUTO ATIVO 👻" if self.auto else "AUTO DESATIVADO"; self.refresh()
        if self.auto and not self.spinning:self.spin()
    def spin(self):
        if self.spinning:return
        cost=self.bet*self.lines
        if self.credits<cost:self.auto=False;self.message="CRÉDITOS INSUFICIENTES";self.refresh();return
        self.credits-=cost;self.spinning=True;self.message="A GIRAR... 🎃";self.refresh();self.anim_count=0;self.anim_event=Clock.schedule_interval(self.animate,0.06)
    def animate(self,dt):
        self.anim_count+=1
        for c in range(5):
            for r in range(3): self.reels[c][r]=random.choice(SYMBOLS)
        self.refresh()
        if self.anim_count>=22:
            self.anim_event.cancel();self.spinning=False;self.calculate()
            if self.auto:Clock.schedule_once(lambda _:self.spin(),0.9)
    def calculate(self):
        total=0
        for r in range(self.lines):
            row=[self.reels[c][r] for c in range(5)];count=1
            while count<5 and row[count]==row[0]:count+=1
            if count>=3:total+=VALUES[row[0]]*self.bet*(count-2)
        self.prize=total;self.credits+=total
        self.message=f"🔥 JACKPOT {total}! 🔥" if total>=100 else (f"GANHOU {total}! 🎃" if total else "TENTE NOVAMENTE 👻")
        self.history.append({"hora":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"aposta":self.bet*self.lines,"premio":total});self.history=self.history[-100:];self.save();self.refresh()
    def paytable(self):
        text="\n".join(f"{s}  3+ = {VALUES[s]}" for s in SYMBOLS);Popup(title="🏆 PRÉMIOS",content=Label(text=text,font_size=dp(16)),size_hint=(.8,.8)).open()
    def history_popup(self):
        text="\n".join(f"{x['hora']} | {x['aposta']} | {x['premio']}" for x in reversed(self.history[-50:])) or "Sem jogadas.";Popup(title="📜 HISTÓRICO",content=Label(text=text,font_size=dp(11)),size_hint=(.95,.85)).open()
    def reset(self): self.credits=0;self.prize=0;self.message="CRÉDITOS ZERADOS";self.save();self.refresh()
    def fullscreen(self): Window.fullscreen=not Window.fullscreen
    def info(self): Popup(title="CARDIFTX V5",content=Label(text="Protótipo Android offline.\nSem USB e sem pagamentos reais."),size_hint=(.8,.4)).open()
    def save(self,*_):
        try:
            self.file.parent.mkdir(parents=True,exist_ok=True);self.file.write_text(json.dumps({"credits":self.credits,"bet":self.bet,"lines":self.lines,"history":self.history},ensure_ascii=False),encoding="utf-8")
        except: pass
    def load(self):
        try:
            d=json.loads(self.file.read_text(encoding="utf-8"));self.credits=int(d.get("credits",0));self.bet=int(d.get("bet",1));self.lines=int(d.get("lines",3));self.history=d.get("history",[])[-100:]
        except: pass
class CardiftxApp(App):
    title="CARDIFTX Halloween V5"
    def build(self): return Game()
CardiftxApp().run()
