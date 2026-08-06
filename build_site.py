#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""片仔癀健康·沛呼吸 TVC 创意案网站构建器：解析 source/ 下的方案 md，生成 index.html。
用法：python3 build_site.py
"""
import re
import html
import pathlib

ROOT = pathlib.Path(__file__).parent
MD = ROOT / "source" / "片仔癀沛呼吸_30秒TVC方案与Seedance提示词.md"
OUT = ROOT / "index.html"

text = MD.read_text(encoding="utf-8")

# ---------------- 解析八个版本 ----------------
META = {
    "A": {"name": "新国风", "slogan": "草本清润，呼吸自在", "place": "品牌官号 / 视频号",
          "tags": ["东方美学", "电影质感", "暖橙金"]},
    "B": {"name": "清新现代", "slogan": "随时随地，一颗清爽", "place": "抖音信息流 / 千川",
          "tags": ["高亮明快", "白橙撞色", "快切卡点"]},
    "C": {"name": "洗脑鬼畜", "slogan": "片仔癀沛呼吸，润喉就可以", "place": "抖音 / B站鬼畜区",
          "tags": ["132BPM", "三连重复", "魔性 meme"]},
    "D": {"name": "喉咙火焰山", "slogan": "一颗灭火，一口清润", "place": "信息流跑量",
          "tags": ["西游国民梗", "国漫喜剧", "火焰红"]},
    "E": {"name": "九草本武林团", "slogan": "九种草本，一颗清润", "place": "社交传播 / 详情页切片",
          "tags": ["武侠角色 IP", "卖点拟人", "国漫"]},
    "F": {"name": "古画崩剧本", "slogan": "片仔癀沛呼吸，清润古今", "place": "社交传播赌爆款",
          "tags": ["工笔重彩", "古画 meme", "反差 rap"]},
    "G": {"name": "一口气吐青龙", "slogan": "一口气，清润自在", "place": "品牌官号置顶",
          "tags": ["史诗水墨", "青龙图腾", "航拍"]},
    "H": {"name": "见过世面的从容", "slogan": "见过世面的从容", "place": "视频号 / 朋友圈 / 私域",
          "tags": ["高端电影感", "ASMR", "赠礼线"]},
}


def parse_table(block):
    rows = []
    for line in block.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue
        rows.append(cells)
    if rows and rows[0][0] in ("时间", "素材", "维度"):
        rows = rows[1:]
    return rows


versions = []
ver_re = re.compile(r'^##\s*[^版]*版本\s*([A-H])\s*·\s*(.+)$', re.M)
matches = list(ver_re.finditer(text))
for i, m in enumerate(matches):
    key = m.group(1)
    start = m.end()
    nxt = re.search(r'^## ', text[start:], re.M)
    body = text[start:start + nxt.start() if nxt else len(text)]

    sub = m.group(2).strip()
    sub = re.sub(r'^（|）$', '', sub)

    mainline = ""
    mm = re.search(r'创意主线：(.+)', body)
    if mm:
        mainline = mm.group(1).strip()

    chars = ""
    cm = re.search(r'\*\*角色设定\*\*：(.+)', body)
    if cm:
        chars = cm.group(1).strip()

    agree = []
    if "**关键约定**" in body:
        seg = body.split("**关键约定**", 1)[1]
        seg = seg.split("###", 1)[0]
        agree = [l[2:].strip() for l in seg.splitlines() if l.strip().startswith("- ")]

    board = []
    bm = re.search(r'### 分镜脚本\s*\n((?:\|.+\n?)+)', body)
    if bm:
        board = parse_table(bm.group(1))

    prompts = []
    for pm in re.finditer(r'### Seedance 提示词 ([A-H][12])（第 [12] 条，15 秒，9:16）\s*\n```\n(.*?)```', body, re.S):
        prompts.append((pm.group(1), pm.group(2).strip()))

    extra_tables = []
    for tm in re.finditer(r'### (后期大字卡点表（剪映叠加）)\s*\n((?:\|.+\n?)+)', body):
        extra_tables.append((tm.group(1), parse_table(tm.group(2))))

    extra_fences = []
    for fm in re.finditer(r'### (可选：洗脑神曲提示词（音乐生成，铺底全片）)\s*\n```\n(.*?)```', body, re.S):
        extra_fences.append((fm.group(1), fm.group(2).strip()))

    notes = []
    for nm in re.finditer(r'\*\*(拼接点|后期文字|后期与投放)\*\*：(.+)', body):
        notes.append((nm.group(1), nm.group(2).strip()))

    versions.append(dict(key=key, sub=sub, mainline=mainline, chars=chars, agree=agree,
                         board=board, prompts=prompts, extra_tables=extra_tables,
                         extra_fences=extra_fences, notes=notes, **META[key]))

assert len(versions) == 8, f"解析到 {len(versions)} 个版本，应为 8"

# ---------------- 渲染 ----------------
def esc(s):
    return html.escape(s, quote=False)


def timeline_html(rows):
    out = ['<div class="timeline">']
    for r in rows:
        t = r[0] if len(r) > 0 else ""
        shot = r[1] if len(r) > 1 else ""
        pic = r[2] if len(r) > 2 else ""
        snd = r[3] if len(r) > 3 else ""
        out.append(f'''<div class="tl-row">
<div class="tl-time">{esc(t)}</div>
<div class="tl-body"><span class="tl-shot">{esc(shot)}</span><p>{esc(pic)}</p>
<p class="tl-snd">♪ {esc(snd)}</p></div>
</div>''')
    out.append('</div>')
    return "\n".join(out)


def prompts_html(items):
    out = []
    for pid, ptext in items:
        out.append(f'''<div class="prompt-card">
<div class="prompt-head"><span class="prompt-id">提示词 {pid}</span>
<span class="prompt-spec">第 {pid[-1]} 条 · 15s · 9:16</span>
<button class="copy-btn" data-target="p-{pid}">复制</button></div>
<pre id="p-{pid}">{esc(ptext)}</pre>
</div>''')
    return "\n".join(out)


ver_sections = []
for v in versions:
    k = v["key"].lower()
    chips = "".join(f'<span class="chip">{esc(t)}</span>' for t in v["tags"])
    parts = [f'''<section class="ver" id="v-{k}" data-v="{k}">
<div class="ver-head">
<div class="ver-letter">{v["key"]}</div>
<div class="ver-title"><h3>{esc(v["name"])}<span class="ver-sub">{esc(v["sub"])}</span></h3>
<div class="chips">{chips}<span class="chip chip-place">投放 · {esc(v["place"])}</span></div></div>
<div class="ver-slogan">「{esc(v["slogan"])}」</div>
</div>
<p class="mainline"><b>创意主线</b> {esc(v["mainline"])}</p>''']
    if v["chars"]:
        parts.append(f'<p class="chars"><b>角色设定</b> {esc(v["chars"])}</p>')
    if v["agree"]:
        parts.append('<ul class="agree">' + "".join(f"<li>{esc(a)}</li>" for a in v["agree"]) + "</ul>")
    parts.append(timeline_html(v["board"]))
    parts.append('<div class="prompts">' + prompts_html(v["prompts"]) + "</div>")
    for tname, trows in v["extra_tables"]:
        rows = "".join(
            f'<div class="xt-row"><span>{esc(r[0])}</span><b>{esc(r[1])}</b><i>{esc(r[2]) if len(r) > 2 else ""}</i></div>'
            for r in trows)
        parts.append(f'<div class="xtable"><h4>{esc(tname)}</h4>{rows}</div>')
    for fname, ftext in v["extra_fences"]:
        parts.append(f'''<div class="prompt-card music">
<div class="prompt-head"><span class="prompt-id">♪ {esc(fname)}</span>
<button class="copy-btn" data-target="p-{k}-music">复制</button></div>
<pre id="p-{k}-music">{esc(ftext)}</pre></div>''')
    if v["notes"]:
        parts.append('<div class="notes">' + "".join(
            f'<p><b>{esc(n[0])}</b>{esc(n[1])}</p>' for n in v["notes"]) + "</div>")
    parts.append("</section>")
    ver_sections.append("\n".join(parts))

ver_nav = "".join(
    f'<a class="vnav" href="#v-{v["key"].lower()}" data-v="{v["key"].lower()}">{v["key"]}<i>{esc(v["name"])}</i></a>'
    for v in versions)

HERBS = ["金线莲", "化橘红", "陈皮", "枇杷叶", "甘草", "罗汉果", "金银花", "超微绿茶粉", "天然薄荷脑"]
herb_chips = "".join(f'<span class="herb">{h}</span>' for h in HERBS)

HTML = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>沛呼吸 · 30秒TVC八版创意案</title>
<style>
:root {{
  --bg: #16110c; --bg2: #1e1710; --card: #241b12; --line: #3a2d1e;
  --ink: #f1e8d8; --ink-dim: #b3a48c; --gold: #e0a449; --seal: #b5382a;
  --serif: "Noto Serif SC","Songti SC","STSong","SimSun",serif;
  --sans: "PingFang SC","Noto Sans SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ background:var(--bg); color:var(--ink); font-family:var(--sans); line-height:1.75; font-size:15px; }}
::selection {{ background:var(--gold); color:#241b12; }}

/* ---------- 顶部导航 ---------- */
nav {{ position:fixed; top:0; left:0; right:0; z-index:50; display:flex; align-items:center; gap:14px;
  padding:10px 22px; background:rgba(22,17,12,.86); backdrop-filter:blur(12px);
  border-bottom:1px solid var(--line); }}
.brand {{ font-family:var(--serif); font-weight:700; color:var(--gold); letter-spacing:2px; white-space:nowrap; }}
.nav-links {{ display:flex; gap:4px; overflow-x:auto; scrollbar-width:none; margin-left:auto; }}
.nav-links::-webkit-scrollbar {{ display:none; }}
.nav-links a {{ color:var(--ink-dim); text-decoration:none; font-size:13px; padding:6px 10px; border-radius:999px; white-space:nowrap; transition:.25s; }}
.nav-links a:hover, .nav-links a.on {{ color:var(--gold); background:rgba(224,164,73,.12); }}

/* ---------- Hero ---------- */
header {{ min-height:92vh; display:flex; flex-direction:column; justify-content:center; align-items:center;
  text-align:center; position:relative; overflow:hidden; padding:110px 20px 60px;
  background:
    radial-gradient(900px 500px at 15% 0%, rgba(224,164,73,.16), transparent 60%),
    radial-gradient(700px 480px at 90% 90%, rgba(63,160,140,.10), transparent 60%),
    var(--bg); }}
header::before {{ content:""; position:absolute; inset:0; opacity:.5;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64'%3E%3Cpath d='M32 10h22v22H22V22h10v8h12V20H32z' fill='none' stroke='%23e0a449' stroke-opacity='.10' stroke-width='2'/%3E%3C/svg%3E"); }}
.spark {{ position:absolute; width:5px; height:5px; border-radius:50%; background:var(--gold); opacity:.5;
  animation:float 9s ease-in-out infinite; }}
@keyframes float {{ 0%,100% {{ transform:translateY(0); opacity:.15; }} 50% {{ transform:translateY(-46px); opacity:.6; }} }}
.hero-seal {{ writing-mode:vertical-rl; background:var(--seal); color:#fff; font-family:var(--serif);
  padding:14px 8px; border-radius:6px; letter-spacing:6px; font-size:18px; position:relative;
  box-shadow:0 6px 24px rgba(181,56,42,.4); margin-bottom:26px; }}
.hero-brand {{ color:var(--ink-dim); letter-spacing:6px; font-size:14px; margin-bottom:14px; position:relative; }}
h1 {{ font-family:var(--serif); font-size:clamp(34px,7vw,64px); font-weight:900; letter-spacing:4px; position:relative; }}
h1 em {{ font-style:normal; color:var(--gold); }}
.hero-sub {{ margin-top:18px; color:var(--ink-dim); font-size:clamp(14px,2.4vw,17px); letter-spacing:2px; position:relative; }}
.hero-chips {{ display:flex; gap:10px; flex-wrap:wrap; justify-content:center; margin-top:34px; position:relative; }}
.hero-chips span {{ border:1px solid var(--line); padding:7px 16px; border-radius:999px; font-size:13px;
  color:var(--ink-dim); background:rgba(36,27,18,.6); }}
.hero-chips b {{ color:var(--gold); font-weight:600; }}
.scroll-hint {{ position:absolute; bottom:26px; color:var(--ink-dim); font-size:12px; letter-spacing:3px; animation:hint 2s infinite; }}
@keyframes hint {{ 0%,100% {{ transform:translateY(0); }} 50% {{ transform:translateY(8px); }} }}

/* ---------- 通用区块 ---------- */
section.block {{ max-width:1080px; margin:0 auto; padding:80px 22px 10px; scroll-margin-top:70px; }}
.kicker {{ color:var(--gold); letter-spacing:6px; font-size:13px; margin-bottom:10px; }}
h2 {{ font-family:var(--serif); font-size:clamp(24px,4.4vw,36px); letter-spacing:3px; margin-bottom:14px; }}
.lead {{ color:var(--ink-dim); max-width:760px; margin-bottom:34px; }}

/* 产品洞察 */
.sp-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:14px; margin-bottom:26px; }}
.sp-card {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:20px; transition:.3s; }}
.sp-card:hover {{ transform:translateY(-4px); border-color:var(--gold); }}
.sp-card h4 {{ font-family:var(--serif); color:var(--gold); margin-bottom:8px; letter-spacing:2px; }}
.sp-card p {{ font-size:13.5px; color:var(--ink-dim); }}
.herbs {{ display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 26px; }}
.herb {{ font-family:var(--serif); border:1px solid rgba(224,164,73,.4); color:var(--gold);
  padding:6px 16px; border-radius:999px; font-size:14px; letter-spacing:2px; background:rgba(224,164,73,.07); }}
.callout {{ border-left:3px solid var(--seal); background:rgba(181,56,42,.08); border-radius:0 12px 12px 0;
  padding:14px 18px; font-size:13.5px; color:var(--ink-dim); }}
.callout b {{ color:#e8836f; }}

/* 方法论 */
.mth-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:14px; }}
.mth {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:18px 20px; display:flex; gap:16px; }}
.mth i {{ font-family:var(--serif); font-style:normal; font-size:30px; color:var(--gold); opacity:.85; line-height:1; }}
.mth h4 {{ font-family:var(--serif); letter-spacing:2px; margin-bottom:4px; }}
.mth p {{ font-size:13px; color:var(--ink-dim); }}

/* 版本导航条 */
.vbar {{ position:sticky; top:53px; z-index:40; display:flex; gap:8px; overflow-x:auto; padding:12px 22px;
  background:rgba(22,17,12,.9); backdrop-filter:blur(12px); border-block:1px solid var(--line); scrollbar-width:none; }}
.vbar::-webkit-scrollbar {{ display:none; }}
.vnav {{ flex:0 0 auto; display:flex; align-items:center; gap:8px; text-decoration:none; color:var(--ink-dim);
  border:1px solid var(--line); border-radius:999px; padding:6px 14px 6px 8px; font-size:13px; transition:.25s; }}
.vnav b {{ font-family:var(--serif); width:26px; height:26px; display:grid; place-items:center; border-radius:50%;
  background:rgba(224,164,73,.12); color:var(--gold); }}
.vnav:hover {{ border-color:var(--gold); color:var(--ink); }}

/* 版本区块主题 */
.ver {{ max-width:1080px; margin:56px auto; padding:34px 26px; border:1px solid var(--line); border-radius:22px;
  background:linear-gradient(160deg, color-mix(in srgb, var(--acc) 7%, var(--bg2)), var(--bg2)); position:relative; overflow:hidden;
  scroll-margin-top:128px; }}
.ver::before {{ content:attr(data-v); position:absolute; right:-10px; top:-46px; font-family:var(--serif);
  font-size:200px; font-weight:900; color:var(--acc); opacity:.07; text-transform:uppercase; }}
.ver[data-v="a"] {{ --acc:#e0a449; --acc2:#3fa08c; }}
.ver[data-v="b"] {{ --acc:#ff7a2f; --acc2:#ffd9b8; }}
.ver[data-v="c"] {{ --acc:#ffd23f; --acc2:#35d07f; }}
.ver[data-v="d"] {{ --acc:#ff5a36; --acc2:#ffb199; }}
.ver[data-v="e"] {{ --acc:#c08a3e; --acc2:#7fae6a; }}
.ver[data-v="f"] {{ --acc:#d8b26a; --acc2:#c03a2b; }}
.ver[data-v="g"] {{ --acc:#3fa08c; --acc2:#e0a449; }}
.ver[data-v="h"] {{ --acc:#c9a06a; --acc2:#8c7a5e; }}
.ver-head {{ display:flex; align-items:center; gap:18px; flex-wrap:wrap; }}
.ver-letter {{ font-family:var(--serif); font-size:44px; font-weight:900; color:var(--acc);
  width:74px; height:74px; border:2px solid var(--acc); border-radius:18px; display:grid; place-items:center;
  box-shadow:0 0 0 6px color-mix(in srgb, var(--acc) 12%, transparent); }}
.ver-title h3 {{ font-family:var(--serif); font-size:clamp(20px,3.6vw,28px); letter-spacing:3px; }}
.ver-sub {{ display:block; color:var(--ink-dim); font-size:13px; letter-spacing:2px; font-weight:400; margin-top:2px; }}
.ver-slogan {{ margin-left:auto; font-family:var(--serif); color:var(--acc); font-size:15px; letter-spacing:2px; }}
.chips {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:8px; }}
.chip {{ font-size:12px; color:var(--ink-dim); border:1px solid var(--line); padding:3px 12px; border-radius:999px; }}
.chip-place {{ color:var(--acc); border-color:color-mix(in srgb, var(--acc) 45%, transparent); }}
.mainline, .chars {{ margin:20px 0 6px; color:var(--ink); }}
.mainline b, .chars b {{ color:var(--acc); font-family:var(--serif); letter-spacing:2px; margin-right:8px; }}
.agree {{ margin:12px 0 4px 18px; color:var(--ink-dim); font-size:13.5px; }}

/* 时间线 */
.timeline {{ margin:26px 0 8px; border-left:2px solid color-mix(in srgb, var(--acc) 45%, transparent); padding-left:0; }}
.tl-row {{ display:flex; gap:16px; padding:10px 0 10px 22px; position:relative; }}
.tl-row::before {{ content:""; position:absolute; left:-6px; top:20px; width:10px; height:10px; border-radius:50%;
  background:var(--acc); box-shadow:0 0 10px var(--acc); }}
.tl-time {{ flex:0 0 64px; font-family:var(--serif); color:var(--acc); font-weight:700; }}
.tl-shot {{ display:inline-block; font-size:12px; color:var(--acc2); border:1px solid color-mix(in srgb, var(--acc2) 40%, transparent);
  border-radius:6px; padding:1px 8px; margin-bottom:4px; }}
.tl-body p {{ font-size:13.5px; color:var(--ink); }}
.tl-snd {{ color:var(--ink-dim) !important; font-size:12.5px !important; }}

/* 提示词卡片 */
.prompts {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:16px; margin-top:22px; }}
.prompt-card {{ background:#120d08; border:1px solid var(--line); border-radius:16px; overflow:hidden; }}
.prompt-head {{ display:flex; align-items:center; gap:10px; padding:10px 14px; border-bottom:1px solid var(--line);
  background:color-mix(in srgb, var(--acc) 8%, transparent); }}
.prompt-id {{ font-family:var(--serif); color:var(--acc); letter-spacing:2px; font-weight:700; }}
.prompt-spec {{ font-size:12px; color:var(--ink-dim); }}
.copy-btn {{ margin-left:auto; cursor:pointer; border:1px solid var(--acc); background:transparent; color:var(--acc);
  border-radius:999px; padding:4px 16px; font-size:12px; transition:.2s; }}
.copy-btn:hover {{ background:var(--acc); color:#16110c; }}
.prompt-card pre {{ padding:16px; font-size:12.5px; line-height:1.8; color:#d9cdb6; overflow-x:auto;
  font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace; white-space:pre-wrap; }}
.xtable {{ margin-top:18px; background:#120d08; border:1px solid var(--line); border-radius:16px; padding:16px; }}
.xtable h4 {{ font-family:var(--serif); color:var(--acc); letter-spacing:2px; margin-bottom:10px; }}
.xt-row {{ display:flex; gap:12px; flex-wrap:wrap; padding:6px 0; border-bottom:1px dashed var(--line); font-size:13px; }}
.xt-row span {{ flex:0 0 90px; color:var(--acc); font-family:var(--serif); }}
.xt-row b {{ color:var(--ink); }}
.xt-row i {{ color:var(--ink-dim); font-style:normal; }}
.notes {{ margin-top:18px; display:grid; gap:8px; }}
.notes p {{ font-size:13px; color:var(--ink-dim); background:rgba(0,0,0,.25); border-radius:10px; padding:10px 14px; }}
.notes b {{ color:var(--acc); margin-right:8px; }}

/* 试映室 */
.cinema {{ display:grid; grid-template-columns:1.4fr 1fr; gap:18px; }}
@media (max-width:820px) {{ .cinema {{ grid-template-columns:1fr; }} .cinema video {{ width:100%; height:auto; }} }}
.cinema video {{ display:block; height:min(76vh, 880px); aspect-ratio:9/16; width:auto; max-width:100%;
  justify-self:center; border-radius:18px; border:1px solid var(--line); background:#000; }}
.frames {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
.frames img {{ width:100%; border-radius:12px; border:1px solid var(--line); }}
.frames figcaption {{ font-size:12px; color:var(--ink-dim); margin-top:4px; }}
.cine-note {{ margin-top:16px; }}

/* 素材 & 投放 */
.assets {{ display:flex; gap:18px; flex-wrap:wrap; }}
.asset {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:14px; width:250px; }}
.asset img {{ width:100%; border-radius:10px; }}
.asset p {{ font-size:12.5px; color:var(--ink-dim); margin-top:10px; }}
.asset b {{ color:var(--gold); }}
.frames img, .asset img {{ cursor:zoom-in; transition:.25s; }}
.frames img:hover, .asset img:hover {{ transform:scale(1.03); border-color:var(--gold); }}
.lightbox {{ position:fixed; inset:0; z-index:100; display:none; place-items:center;
  background:rgba(10,7,4,.92); backdrop-filter:blur(8px); cursor:zoom-out; }}
.lightbox.on {{ display:grid; }}
.lightbox img {{ max-width:92vw; max-height:92vh; border-radius:12px; box-shadow:0 20px 80px rgba(0,0,0,.65); }}
.lightbox figcaption {{ position:absolute; bottom:22px; color:var(--ink-dim); font-size:13px; letter-spacing:2px; }}
.place-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }}
.place {{ background:var(--card); border:1px solid var(--line); border-radius:16px; padding:16px 20px; }}
.place b {{ color:var(--gold); font-family:var(--serif); letter-spacing:2px; display:block; margin-bottom:4px; }}
.place p {{ font-size:13px; color:var(--ink-dim); }}

footer {{ margin-top:90px; padding:40px 20px 50px; border-top:1px solid var(--line); text-align:center;
  color:var(--ink-dim); font-size:12.5px; letter-spacing:2px; }}
footer .seal-mini {{ display:inline-block; background:var(--seal); color:#fff; border-radius:4px; padding:2px 8px;
  font-family:var(--serif); margin-right:8px; }}

.reveal {{ opacity:0; transform:translateY(26px); transition:.7s ease; }}
.reveal.in {{ opacity:1; transform:none; }}
</style>
</head>
<body>

<nav>
<span class="brand">沛呼吸 × TVC</span>
<div class="nav-links">
<a href="#insight">产品洞察</a><a href="#method">创作方法</a><a href="#vers">八版创意</a>
<a href="#cinema">试映室</a><a href="#assets">参考素材</a><a href="#place">投放矩阵</a>
</div>
</nav>

<header>
<span class="spark" style="left:12%;top:24%"></span>
<span class="spark" style="left:80%;top:18%;animation-delay:1.2s"></span>
<span class="spark" style="left:68%;top:64%;animation-delay:2.4s"></span>
<span class="spark" style="left:22%;top:70%;animation-delay:3.1s"></span>
<span class="spark" style="left:46%;top:36%;animation-delay:4s"></span>
<div class="hero-seal">沛呼吸</div>
<div class="hero-brand">片仔癀健康 · PIEN TZE HUANG HEALTH</div>
<h1>草本清润含片糖<br><em>30 秒 TVC · 八版创意案</em></h1>
<p class="hero-sub">从新国风到洗脑鬼畜，从古画 meme 到高端电影感 —— 一支润喉糖的八种银幕人生</p>
<div class="hero-chips">
<span>画幅 <b>9:16</b> 竖屏</span><span>单条 <b>≤15s</b> 拆分</span><span><b>16</b> 条 Seedance 提示词</span>
<span>模型 <b>Seedance 2.0</b></span><span>样片 <b>已验证</b></span>
</div>
<div class="scroll-hint">向下探索 ↓</div>
</header>

<section class="block reveal" id="insight">
<div class="kicker">壹 · INSIGHT</div>
<h2>产品洞察</h2>
<p class="lead">片仔癀健康·沛呼吸 草本清润含片糖（精装 20g/盒 · 20 片）。中华老字号背书，九种草本协同，主打清凉、顺畅、甘润三重体验。</p>
<div class="sp-grid">
<div class="sp-card"><h4>核心卖点</h4><p>9 种甄选草本提取物——可视化为本草微距、原料实景、金色药液汇聚。</p></div>
<div class="sp-card"><h4>体验卖点</h4><p>清凉润喉 · 顺畅 · 甘润——可视化为蓝绿清凉气流、深呼吸、热浪退散。</p></div>
<div class="sp-card"><h4>信任卖点</h4><p>老字号背书 + 配料干净（D-阿洛酮糖代糖、低糖）+ 第三方权威检测。</p></div>
<div class="sp-card"><h4>场景卖点</h4><p>随时随地来一颗——用嗓人群、烟民、空调房，口袋里的从容。</p></div>
</div>
<div class="herbs">{herb_chips}</div>
<div class="callout"><b>合规口径</b> 本品为普通食品（压片糖果），全片文案只用「清凉、舒缓、甘润、清润」等体验性表达，不宣称化痰、止咳、治疗等功效；烟民画面仅作生活背景，不暗示功效。</div>
</section>

<section class="block reveal" id="method">
<div class="kicker">贰 · METHOD</div>
<h2>TVC 创作方法</h2>
<p class="lead">调研结论沉淀为六条执行纪律，也是本方案八版共用的底层结构。</p>
<div class="mth-grid">
<div class="mth"><i>壹</i><div><h4>五段式结构</h4><p>开场气氛 → 主角亮相 → 卖点展示 → 记忆点 → 品牌落版，每镜只解决一个目标。</p></div></div>
<div class="mth"><i>贰</i><div><h4>黄金三秒</h4><p>开场 3 秒内给出视觉钩子；30 秒拆 6–8 镜，单镜 2–5 秒。</p></div></div>
<div class="mth"><i>叁</i><div><h4>卖点可视化</h4><p>卖点用画面演出来——原料微距、清凉气流，不靠抽象文案堆砌。</p></div></div>
<div class="mth"><i>肆</i><div><h4>运镜连贯</h4><p>缓推 / 环绕 / 跟拍 / 快切交替，镜头间用匹配元素衔接，禁止无逻辑跳切。</p></div></div>
<div class="mth"><i>伍</i><div><h4>落版干净</h4><p>收尾定格产品 + 留白；Logo、Slogan、字幕全部后期叠加，AI 画面不生成文字。</p></div></div>
<div class="mth"><i>陆</i><div><h4>分条生成</h4><p>禁止一条 prompt 出全片——每版拆 2 条 15 秒生成后剪辑拼接，与平台限制天然契合。</p></div></div>
</div>
</section>

<div class="vbar" id="vers">{ver_nav}</div>

{chr(10).join(ver_sections)}

<section class="block reveal" id="cinema">
<div class="kicker">肆 · SCREENING</div>
<h2>试映室</h2>
<p class="lead">版本 A 第 1 条样片（Seedance 2.0 实测，15s · 720×1280 · 含音频）。逐帧核验：草本微距开场、夜景背影剪影、包装高还原、糖体涟漪收束，四个节奏点全部命中。</p>
<div class="cinema">
<video controls preload="metadata" poster="assets/poster.jpg" src="assets/sample-a1.mp4"></video>
<div>
<div class="frames">
<figure><img src="assets/frame_1.jpg" alt=""><figcaption>0s · 草本微距开场</figcaption></figure>
<figure><img src="assets/frame_2.jpg" alt=""><figcaption>4s · 夜景背影剪影</figcaption></figure>
<figure><img src="assets/frame_3.jpg" alt=""><figcaption>10s · 包装高还原亮相</figcaption></figure>
<figure><img src="assets/frame_4.jpg" alt=""><figcaption>14s · 糖体涟漪收束</figcaption></figure>
</div>
<p class="cine-note callout"><b>验证结论</b> 参考图策略生效：包装「沛呼吸 / 片仔癀健康 / 草本清润含片糖」清晰可读，仅个别小字轻微乱码，后期可修。提示词方案可行，八版共用同一套参考图与约定。</p>
</div>
</div>
</section>

<section class="block reveal" id="assets">
<div class="kicker">伍 · ASSETS</div>
<h2>参考素材</h2>
<p class="lead">上传即梦时作为 @图片1 / @图片2，保证产品外观还原。已裁去营销文字，只留包装与糖体。</p>
<div class="assets">
<div class="asset"><img src="assets/ref_package.jpg" alt="包装参考"><p><b>@图片1</b> 产品包装（盒+小袋）外观唯一依据。</p></div>
<div class="asset"><img src="assets/ref_tablet.jpg" alt="糖体参考"><p><b>@图片2</b> 糖体外观唯一依据。</p></div>
</div>
</section>

<section class="block reveal" id="place">
<div class="kicker">陆 · MEDIA</div>
<h2>投放矩阵</h2>
<p class="lead">八版不是八选一，而是一支内容舰队的八种弹药，按场域分配。</p>
<div class="place-grid">
<div class="place"><b>信息流跑量</b><p>C 洗脑鬼畜 / D 火焰山 —— 前 3 秒梗即钩子，完播与点击优先。</p></div>
<div class="place"><b>高端赠礼与私域</b><p>H 从容版 —— 视频号、朋友圈、商业播客、茶室私域。</p></div>
<div class="place"><b>品牌官号置顶</b><p>G 青龙 / A 新国风 —— 质感立品牌。</p></div>
<div class="place"><b>社交传播赌爆款</b><p>F 古画 / E 武林团 —— meme 与角色 IP 带二次创作空间。</p></div>
<div class="place"><b>详情页 / 直播间切片</b><p>B 清新现代 + E 角色登场单镜切片。</p></div>
</div>
</section>

<footer>
<span class="seal-mini">沛</span>片仔癀健康 · 沛呼吸 —— 30 秒 TVC 八版创意案 · 2026-08-06 · 内部提案
</footer>

<div class="lightbox" id="lightbox"><img alt=""><figcaption id="lb-cap"></figcaption></div>

<script>
// 灯箱放大
const lb = document.getElementById('lightbox'), lbImg = lb.querySelector('img'), lbCap = document.getElementById('lb-cap');
const lbClose = () => {{ lb.classList.remove('on'); document.body.style.overflow = ''; }};
document.querySelectorAll('.frames img, .asset img').forEach(im => im.addEventListener('click', () => {{
  lbImg.src = im.src; lbImg.alt = im.alt || '';
  const cap = im.closest('figure')?.querySelector('figcaption')?.textContent || im.closest('.asset')?.querySelector('p')?.textContent || '';
  lbCap.textContent = cap;
  lb.classList.add('on'); document.body.style.overflow = 'hidden';
}}));
lb.addEventListener('click', lbClose);
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') lbClose(); }});
// 复制按钮
document.querySelectorAll('.copy-btn').forEach(btn => {{
  btn.addEventListener('click', () => {{
    const pre = document.getElementById(btn.dataset.target);
    const txt = pre.innerText;
    const done = () => {{ btn.textContent = '已复制 ✓'; setTimeout(() => btn.textContent = '复制', 1600); }};
    if (navigator.clipboard) {{ navigator.clipboard.writeText(txt).then(done); }}
    else {{
      const ta = document.createElement('textarea'); ta.value = txt; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); ta.remove(); done();
    }}
  }});
}});
// 滚动显现
const io = new IntersectionObserver(es => es.forEach(e => {{ if (e.isIntersecting) {{ e.target.classList.add('in'); io.unobserve(e.target); }} }}), {{ threshold: .08 }});
document.querySelectorAll('.reveal, .ver').forEach(el => {{ el.classList.add('reveal'); io.observe(el); }});
// 导航高亮
const secs = [...document.querySelectorAll('section[id], .ver[id]')];
const links = [...document.querySelectorAll('.nav-links a')];
const io2 = new IntersectionObserver(es => es.forEach(e => {{
  if (e.isIntersecting) {{
    links.forEach(a => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
  }}
}}), {{ rootMargin: '-40% 0px -55% 0px' }});
secs.forEach(s => io2.observe(s));
</script>
</body>
</html>'''

OUT.write_text(HTML, encoding="utf-8")
print(f"OK -> {OUT} ({OUT.stat().st_size/1024:.0f} KB), versions: {[v['key'] for v in versions]}")
