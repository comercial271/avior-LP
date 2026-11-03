// Gera as miniaturas (1280x720) das aulas: node youtube/miniaturas/gerar.js
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const os = require('os');
const FONTS = 'file://' + path.resolve(__dirname, '../../carrosseis/_render/fonts');

const AULAS = [
  { n: '01', l1: 'Como empresários', l2: 'tracionam com <b>IA</b>', sub: 'Casos reais de quem já está usando' },
  { n: '02', l1: 'IA que quebra', l2: '<b>objeções</b>', sub: 'Assistentes de IA para vender mais' },
  { n: '03', l1: 'Qual <b>IA</b> usar?', l2: '', sub: 'Modelos de IA e pesquisa de mercado' },
  { n: '04', l1: 'CRM e dashboard', l2: 'com <b>IA</b>', sub: 'Padrões de objeção na prática' },
  { n: '05', l1: 'Tecnologia', l2: 'e <b>negócios</b>', sub: 'Encontro da comunidade AVIOR' },
];

const html = (a, seed) => `<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:P;font-weight:300;src:url(${FONTS}/Poppins-Light.ttf)}
@font-face{font-family:P;font-weight:500;src:url(${FONTS}/Poppins-Medium.ttf)}
@font-face{font-family:P;font-weight:700;src:url(${FONTS}/Poppins-Bold.ttf)}
*{margin:0;box-sizing:border-box}
body{width:1280px;height:720px;overflow:hidden;font-family:P;color:#F5F1E8;position:relative;
 background:radial-gradient(45% 70% at 80% 50%,rgba(214,188,142,.32),rgba(0,0,0,0) 70%),radial-gradient(70% 90% at 50% 50%,#14110c,#050505 85%)}
canvas{position:absolute;left:740px;top:100px;width:600px;height:491px}
.t{position:absolute;left:70px;top:0;bottom:0;width:760px;display:flex;flex-direction:column;justify-content:center}
.pill{align-self:flex-start;display:flex;gap:12px;align-items:center;padding:10px 22px;border-radius:100px;background:linear-gradient(95deg,#E9D3A6,#A88E5C);color:#0b0a08;font-weight:700;font-size:26px;letter-spacing:.08em}
h1{margin-top:26px;font-weight:700;font-size:74px;line-height:1.04;white-space:nowrap;letter-spacing:-.02em;text-shadow:0 6px 30px rgba(0,0,0,.8)}
h1 b{background:linear-gradient(95deg,#FFF1CC,#EBCF96 60%,#D6B57A);-webkit-background-clip:text;color:transparent;text-shadow:none}
p{margin-top:24px;font-weight:500;font-size:30px;color:#C9C2B2}
.brand{position:absolute;left:72px;bottom:44px;font-weight:300;font-size:24px;letter-spacing:.42em;color:#C2B89D}
.bar{position:absolute;left:0;right:0;bottom:0;height:8px;background:linear-gradient(90deg,#D6BC8E,#8C7A4E)}
</style></head><body><canvas id="b" width="1100" height="900"></canvas>
<div class="t"><div class="pill">AULA ${a.n}</div><h1>${a.l1}${a.l2 ? '<br>' + a.l2 : ''}</h1><p>${a.sub}</p></div>
<div class="brand">AVIOR</div><div class="bar"></div>
<script>(function(){const c=document.getElementById('b'),x=c.getContext('2d');let s=${seed};const r=()=>(s=(s*16807)%2147483647)/2147483647;
const L=[[430,380,270,210],[640,330,230,200],[300,470,170,140],[560,520,250,120],[780,430,150,150],[760,600,120,80],[590,650,40,90]];
const ins=(px,py,m=1)=>L.some(([a,b,rx,ry])=>((px-a)/(rx*m))**2+((py-b)/(ry*m))**2<=1);
const P=[];let t=0;while(P.length<520&&t<2e5){t++;const px=120+r()*820,py=140+r()*640;if(!ins(px,py))continue;const e=!ins(px,py,.9);if(!e&&r()<.35)continue;P.push([px,py,e]);}
x.lineWidth=1.6;for(let i=0;i<P.length;i++)for(let j=i+1;j<P.length;j++){const d=Math.hypot(P[i][0]-P[j][0],P[i][1]-P[j][1]);if(d<62){x.strokeStyle='rgba(214,188,142,'+(.55*(1-d/62))+')';x.beginPath();x.moveTo(P[i][0],P[i][1]);x.lineTo(P[j][0],P[j][1]);x.stroke();}}
P.forEach(([px,py,e])=>{const big=r()<.05;if(big){const g=x.createRadialGradient(px,py,0,px,py,30);g.addColorStop(0,'rgba(241,221,178,.6)');g.addColorStop(1,'rgba(241,221,178,0)');x.fillStyle=g;x.beginPath();x.arc(px,py,30,0,7);x.fill();}
x.fillStyle=big?'#F6E7C4':(e?'#E2CA98':'rgba(214,188,142,.85)');x.beginPath();x.arc(px,py,big?6:(e?3:2.2),0,7);x.fill();});})();</script></body></html>`;

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  for (const [i, a] of AULAS.entries()) {
    const tmp = path.join(os.tmpdir(), `miniatura-${a.n}.html`);
    fs.writeFileSync(tmp, html(a, 7 + i * 13));
    await p.goto('file://' + tmp);
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: path.join(__dirname, `miniatura-aula-${a.n}.png`) });
  }
  await b.close();
})();
