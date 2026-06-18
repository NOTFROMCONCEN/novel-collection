#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用小说网页阅读器生成器 v2
- 保留完整嵌套目录层次
- 智能章节排序（数字前缀、中文序号、卷+章多级排序）
- 清理目录/文件名中的下划线
用法: python generate_website.py <小说目录名>
"""

import os
import sys
import json
import re
import shutil
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(SCRIPT_DIR, '2019血疫纪元', '2019血疫纪元', 'website')

# ─── 辅助函数 ───────────────────────────────────────────

def clean_name(raw):
    s = raw.strip()
    s = s.replace('_', ' ')
    s = re.sub(r'\s+', ' ', s)
    return s


def cn_to_int(s):
    cn_map = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10}
    s = s.strip()
    if not s: return 0
    if s == '十': return 10
    if s.startswith('十'): return 10 + cn_map.get(s[1:], 0)
    if s.endswith('十'): return cn_map.get(s[:-1], 0) * 10
    if '十' in s:
        parts = s.split('十', 1)
        return cn_map.get(parts[0], 0) * 10 + cn_map.get(parts[1], 0)
    return cn_map.get(s, 0)


def extract_sort_key(filename):
    name = os.path.splitext(filename)[0]
    vol = 0
    ch = 0

    m = re.search(r'第([一二三四五六七八九十百]+)卷', name)
    if m: vol = cn_to_int(m.group(1))

    m2 = re.search(r'[Pp]art\s*(\d+)', name)
    if m2: vol = int(m2.group(1))

    m3 = re.search(r'第([一二三四五六七八九十百]+)[章节幕部]', name)
    if m3:
        ch = cn_to_int(m3.group(1))
    else:
        m4 = re.search(r'第(\d+)[章节幕部]', name)
        if m4:
            ch = int(m4.group(1))
        else:
            m5 = re.match(r'^(\d+)[\-_]', name)
            if m5:
                ch = int(m5.group(1))
            else:
                m6 = re.search(r'[Ww]ordview\.(\d+)', name)
                if m6:
                    ch = int(m6.group(1))
                else:
                    m7 = re.search(r'[\-_](\d+)$', name)
                    if m7:
                        ch = int(m7.group(1))

    suffix = re.sub(r'第[一二三四五六七八九十百\d]+[章节卷幕部]', '', name)
    suffix = re.sub(r'[Pp]art\s*\d+', '', suffix)
    suffix = re.sub(r'^\d+[\-_]', '', suffix)
    suffix = suffix.strip(' -_')

    if vol > 0 or ch > 0:
        return (0, vol, ch, suffix)
    return (1, 0, 0, name)


def sort_items(items):
    files, dirs = [], []
    for item in items:
        (dirs if item['type'] == 'dir' else files).append(item)
    dirs.sort(key=lambda x: extract_sort_key(x['name'] + '.md'))
    files.sort(key=lambda x: extract_sort_key(x['name']))
    return dirs + files


# ─── 目录树扫描 ──────────────────────────────────────────

def build_tree(root_dir):
    items = []
    try:
        entries = sorted(os.listdir(root_dir))
    except OSError:
        return items
    for entry in entries:
        if entry.startswith('.') or entry == '.git':
            continue
        fp = os.path.join(root_dir, entry)
        if os.path.isdir(fp):
            children = build_tree(fp)
            if children:
                items.append({'type': 'dir', 'name': entry, 'path': fp, 'children': sort_items(children)})
        elif entry.endswith('.md'):
            items.append({'type': 'file', 'name': entry, 'path': fp})
    return items


def flatten_tree(tree, parent_id='', parent_section=''):
    all_items = []
    nav_children = []
    for node in tree:
        if node['type'] == 'file':
            title = clean_name(os.path.splitext(node['name'])[0])
            raw_id = (parent_id + '/' + title) if parent_id else title
            safe_id = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff/_-]', '', raw_id.replace(' ', '_'))
            safe_id = safe_id.replace('/', '_')
            item = {'id': safe_id, 'title': title, 'file': node['path'], 'section_path': parent_section or '正文'}
            all_items.append(item)
            nav_children.append({'type': 'item', 'id': safe_id, 'title': title})
        elif node['type'] == 'dir':
            dn = clean_name(node['name'])
            child_items, child_nav = flatten_tree(
                node['children'],
                parent_id=(parent_id + '/' + dn) if parent_id else dn,
                parent_section=(parent_section + ' / ' + dn) if parent_section else dn,
            )
            all_items.extend(child_items)
            if child_nav:
                nav_children.append({'type': 'section', 'title': dn, 'children': child_nav})
    return all_items, nav_children


def read_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"  [WARN] 读取失败 {filepath}: {e}")
        return ''


# ─── 主逻辑 ──────────────────────────────────────────────

def generate(novel_name):
    novel_dir = os.path.join(SCRIPT_DIR, novel_name)
    if not os.path.isdir(novel_dir):
        print(f"错误: 目录不存在: {novel_dir}")
        return False

    content_dir = novel_dir
    ignore_dirs = {'website', '.git', '.obsidian', '.codebuddy', '__pycache__'}
    subdirs = [d for d in os.listdir(novel_dir)
               if os.path.isdir(os.path.join(novel_dir, d))
               and not d.startswith('.')
               and d not in ignore_dirs]
    if len(subdirs) == 1 and subdirs[0] == novel_name:
        content_dir = os.path.join(novel_dir, novel_name)

    website_dir = os.path.join(novel_dir, 'website')
    os.makedirs(website_dir, exist_ok=True)

    print(f"处理: {novel_name}")
    print(f"  内容目录: {content_dir}")

    tree = build_tree(content_dir)
    tree = sort_items(tree)

    all_items, nav_tree = flatten_tree(tree)
    total_files = len(all_items)
    total_words = 0

    for item in all_items:
        content = read_content(item['file'])
        item['content'] = content
        total_words += len(content)

    # 打印树结构
    def print_tree(nodes, indent=0):
        for n in nodes:
            if n['type'] == 'section':
                print('  ' * indent + '[' + n['title'] + ']')
                print_tree(n['children'], indent + 1)
            else:
                print('  ' * indent + '  - ' + n['title'])
    print_tree(nav_tree)
    print(f"  共 {total_files} 章, {total_words} 字\n")

    # 生成 content.js
    content_js_path = os.path.join(website_dir, 'content.js')
    js = []
    js.append('// Auto-generated by generate_website.py v2')
    js.append('// Novel: ' + novel_name)
    js.append('// Updated: ' + datetime.now().strftime('%Y-%m-%d %H:%M'))
    js.append('// Chapters: ' + str(total_files))
    js.append('')
    js.append('const NOVEL_NAME = ' + json.dumps(novel_name, ensure_ascii=False) + ';')
    js.append('const TOTAL_FILES = ' + str(total_files) + ';')
    js.append('const TOTAL_WORDS = ' + str(total_words) + ';')
    js.append('')
    js.append('const NAV_TREE = ' + json.dumps(nav_tree, ensure_ascii=False, indent=2) + ';')
    js.append('')
    js.append('const CONTENT_DATA = {')
    for item in all_items:
        js.append('  ' + json.dumps(item['id'], ensure_ascii=False) + ': {')
        js.append('    id: ' + json.dumps(item['id'], ensure_ascii=False) + ',')
        js.append('    title: ' + json.dumps(item['title'], ensure_ascii=False) + ',')
        js.append('    section: ' + json.dumps(item['section_path'], ensure_ascii=False) + ',')
        js.append('    content: ' + json.dumps(item['content'], ensure_ascii=False))
        js.append('  },')
    js.append('};')

    with open(content_js_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(js))
    size_kb = os.path.getsize(content_js_path) / 1024
    print(f"  content.js ({size_kb:.1f} KB)")

    # 复制静态文件
    for fname in ['common.css', 'utils.js']:
        src = os.path.join(TEMPLATE_DIR, fname)
        dst = os.path.join(website_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # 生成 index.html
    index_path = os.path.join(website_dir, 'index.html')
    html = INDEX_HTML_TEMPLATE.replace('{{NOVEL_NAME}}', novel_name)
    html = html.replace('{{TOTAL_FILES}}', str(total_files))
    html = html.replace('{{TOTAL_WORDS}}', str(total_words))
    html = html.replace('{{WORD_WAN}}', str(total_words // 10000))
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  index.html")

    print(f"完成: {website_dir}/index.html")
    return True


# ─── HTML 模板 ───────────────────────────────────────────

INDEX_HTML_TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{NOVEL_NAME}}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;700&family=Noto+Sans+SC:wght@300;400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="common.css">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{font-size:16px;scroll-behavior:smooth}
body{font-family:'Noto Sans SC',sans-serif;background:var(--bg-base);color:var(--text-primary);min-height:100vh;overflow-x:hidden;transition:background 0.35s ease,color 0.35s ease}
::selection{background:var(--selection-bg);color:var(--text-primary)}

.loading-screen{position:fixed;inset:0;z-index:9999;background:var(--bg-base);display:flex;flex-direction:column;align-items:center;justify-content:center;transition:opacity 0.8s ease,visibility 0.8s ease}
.loading-screen.hidden{opacity:0;visibility:hidden;pointer-events:none}
.loading-logo{font-family:'Noto Serif SC',serif;font-size:2rem;color:var(--text-primary);letter-spacing:0.15em;margin-bottom:2rem;animation:pulse 2s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
.loading-bar{width:200px;height:2px;background:var(--border);border-radius:2px;overflow:hidden}
.loading-bar::after{content:'';display:block;width:40%;height:100%;background:linear-gradient(90deg,transparent,var(--accent),transparent);animation:loading 1.5s ease-in-out infinite}
@keyframes loading{0%{transform:translateX(-100%)}100%{transform:translateX(350%)}}

#app{display:none;min-height:100vh}
#app.active{display:flex}

.sidebar{position:fixed;left:0;top:0;bottom:0;width:300px;background:var(--bg-surface);border-right:1px solid var(--border);overflow-y:auto;z-index:100;display:flex;flex-direction:column;transition:transform 0.3s ease,background 0.35s ease}
.sidebar-header{padding:1.5rem;border-bottom:1px solid var(--border);flex-shrink:0}
.sidebar-logo{font-family:'Noto Serif SC',serif;font-size:1.2rem;color:var(--text-primary);letter-spacing:0.1em;cursor:pointer}
.sidebar-stats{font-size:0.7rem;color:var(--text-dim);margin-top:0.5rem;letter-spacing:0.05em}
.nav-scroll{flex:1;overflow-y:auto;padding:0.3rem 0}

.nav-folder-header{display:flex;align-items:center;gap:0.4rem;padding:0.55rem 1rem;font-size:0.73rem;color:var(--text-secondary);cursor:pointer;letter-spacing:0.12em;transition:color 0.3s;user-select:none;font-weight:600}
.nav-folder-header:hover{color:var(--text-primary)}
.nav-folder-header .arrow{font-size:0.55rem;transition:transform 0.3s;color:var(--accent-dim);flex-shrink:0}
.nav-folder.open>.nav-folder-header .arrow{transform:rotate(90deg)}
.nav-folder-body{max-height:0;overflow:hidden;transition:max-height 0.35s ease}
.nav-folder.open>.nav-folder-body{max-height:4000px}
.nav-folder-body .nav-folder-header{padding-left:1.8rem}
.nav-folder-body .nav-item{padding-left:2.6rem}
.nav-folder-body .nav-folder-body .nav-folder-header{padding-left:2.6rem}
.nav-folder-body .nav-folder-body .nav-item{padding-left:3.4rem}
.nav-folder-body .nav-folder-body .nav-folder-body .nav-folder-header{padding-left:3.4rem}
.nav-folder-body .nav-folder-body .nav-folder-body .nav-item{padding-left:4.2rem}

.nav-item{display:flex;align-items:center;gap:0.5rem;padding:0.45rem 1rem 0.45rem 1.8rem;font-size:0.8rem;color:var(--text-secondary);cursor:pointer;transition:all 0.25s;border-left:2px solid transparent;line-height:1.5}
.nav-item:hover{color:var(--text-primary);background:rgba(91,170,126,0.05);border-left-color:var(--accent-dim)}
.nav-item.active{color:var(--text-primary);background:rgba(91,170,126,0.08);border-left-color:var(--accent)}
.nav-item .ch-num{font-size:0.6rem;color:var(--accent-dim);min-width:1.4em;text-align:right;flex-shrink:0;opacity:0.7}

.main{flex:1;margin-left:300px;min-height:100vh;position:relative}
.content-area{max-width:780px;margin:0 auto;padding:3rem 2.5rem 6rem}

.welcome{max-width:600px;margin:8vh auto 0;text-align:center;padding:2rem}
.welcome h1{font-family:'Noto Serif SC',serif;font-size:clamp(2rem,6vw,3.5rem);color:var(--text-primary);letter-spacing:0.15em;margin-bottom:1rem}
.welcome .divider{width:60px;height:1px;background:linear-gradient(90deg,transparent,var(--accent-dim),transparent);margin:1.5rem auto}
.welcome p{font-size:0.9rem;color:var(--text-dim);line-height:1.8}
.welcome .stats{display:flex;justify-content:center;gap:2.5rem;margin-top:2rem;flex-wrap:wrap}
.welcome .stat{text-align:center}
.welcome .stat-num{font-family:'Noto Serif SC',serif;font-size:1.8rem;color:var(--accent-dim)}
.welcome .stat-label{font-size:0.7rem;color:var(--text-dim);letter-spacing:0.1em;margin-top:0.3rem}

.article-meta{margin-bottom:2.5rem;padding-bottom:1.5rem;border-bottom:1px solid var(--border)}
.article-meta h1{font-family:'Noto Serif SC',serif;font-size:clamp(1.5rem,4vw,2.2rem);font-weight:700;color:var(--text-primary);line-height:1.4;margin-bottom:0.5rem}
.article-body{font-family:'Noto Serif SC',serif;font-size:1.05rem;line-height:1.95;color:var(--text-body)}
.article-body p{margin-bottom:1.2em}
.article-body h2{font-family:'Noto Serif SC',serif;font-size:1.35rem;font-weight:700;color:var(--text-primary);margin:2.5rem 0 1rem;padding-bottom:0.5rem;border-bottom:1px solid var(--border)}
.article-body h3{font-family:'Noto Serif SC',serif;font-size:1.15rem;font-weight:700;color:var(--text-primary);margin:2rem 0 0.8rem}
.article-body h4{font-family:'Noto Serif SC',serif;font-size:1.02rem;font-weight:700;color:var(--text-secondary);margin:1.5rem 0 0.6rem}
.article-body blockquote{margin:1.5rem 0;padding:1rem 1.5rem;border-left:3px solid var(--blockquote-border);background:var(--blockquote-bg);font-style:italic;color:var(--text-secondary)}
.article-body strong{color:var(--text-primary);font-weight:700}
.article-body em{color:var(--text-secondary);font-style:italic}
.article-body pre{margin:1.5rem 0;padding:1.2rem;background:rgba(0,0,0,0.35);border:1px solid var(--border);border-radius:4px;overflow-x:auto;font-family:'Courier New',monospace;font-size:0.85rem;line-height:1.6;color:var(--text-secondary)}
.article-body code{font-family:'Courier New',monospace;font-size:0.88em;background:rgba(255,255,255,0.04);padding:0.1em 0.3em;border-radius:2px}
.article-body ul,.article-body ol{margin:1rem 0 1.2rem 1.5rem}
.article-body li{margin-bottom:0.4em}
.article-body hr{border:none;margin:2.5rem auto;width:40%;height:1px;background:linear-gradient(90deg,transparent,rgba(91,170,126,0.25),transparent)}
.article-body .meta-block{margin:1.5rem 0;padding:1rem 1.2rem;background:rgba(0,0,0,0.25);border:1px solid var(--border);border-radius:4px;font-size:0.88rem;line-height:1.8}
.article-body .scene-break{text-align:center;margin:2rem 0;color:rgba(91,170,126,0.35);letter-spacing:1em;font-size:0.9rem}
.breadcrumb{font-size:0.75rem;color:var(--text-dim);margin-bottom:2rem;letter-spacing:0.1em}
.breadcrumb span{cursor:pointer}
.breadcrumb span:hover{color:var(--text-secondary)}
.breadcrumb .sep{margin:0 0.5em;color:var(--accent-dim)}
.reading-time{font-size:0.72rem;color:var(--text-dim);margin-top:0.3rem;opacity:0.7}

.reading-progress{position:fixed;top:0;left:300px;right:0;height:2px;z-index:50;background:transparent}
.reading-progress .bar{height:100%;width:0%;background:linear-gradient(90deg,rgba(91,170,126,0.6),rgba(91,170,126,0.25));transition:width 0.1s}
.scroll-top{position:fixed;bottom:2rem;right:2rem;width:40px;height:40px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:50%;color:var(--text-dim);font-size:1.1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;opacity:0;visibility:hidden;transition:all 0.3s ease;z-index:50}
.scroll-top.visible{opacity:1;visibility:visible}
.scroll-top:hover{border-color:var(--accent);color:var(--text-primary);transform:translateY(-2px);box-shadow:0 4px 12px rgba(0,0,0,0.2)}

.chapter-nav{display:flex;justify-content:space-between;align-items:center;margin-top:3rem;padding-top:1.5rem;border-top:1px solid var(--border)}
.chapter-nav button{padding:0.55rem 1rem;font-size:0.78rem;color:var(--accent-dim);cursor:pointer;background:none;border:1px solid var(--border);border-radius:4px;transition:all 0.3s;font-family:'Noto Sans SC',sans-serif;letter-spacing:0.05em;max-width:42%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.chapter-nav button:hover:not(:disabled){color:var(--text-primary);border-color:var(--accent-dim);background:rgba(91,170,126,0.05)}
.chapter-nav button:disabled{opacity:0.3;cursor:default}
.chapter-nav .pos{font-size:0.75rem;color:var(--text-dim)}

.mobile-toggle{display:none;position:fixed;top:1rem;left:1rem;z-index:200;width:40px;height:40px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:4px;cursor:pointer;align-items:center;justify-content:center;color:var(--text-secondary);font-size:1.2rem}
.sidebar-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:99}
@media(max-width:768px){.mobile-toggle{display:flex}.sidebar{transform:translateX(-100%);width:280px}.sidebar.open{transform:translateX(0)}.sidebar-overlay.open{display:block}.main{margin-left:0}.content-area{padding:4rem 1.5rem 4rem}.reading-progress{left:0}}
.fade-in{animation:fadeIn 0.4s ease forwards}
@keyframes fadeIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>

<div class="loading-screen" id="loading">
  <div class="loading-logo">{{NOVEL_NAME}}</div>
  <div class="loading-bar"></div>
</div>

<div id="app">
  <button class="theme-toggle" onclick="cycleTheme()" title="切换主题">☀</button>
  <button class="mobile-toggle" onclick="toggleSidebar()">☰</button>
  <div class="sidebar-overlay" onclick="toggleSidebar()"></div>
  <div class="reading-progress"><div class="bar" id="progress-bar"></div></div>

  <nav class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <div class="sidebar-logo" onclick="showWelcome()">{{NOVEL_NAME}}</div>
      <div class="sidebar-stats">{{TOTAL_FILES}} 章 · {{WORD_WAN}} 万字</div>
    </div>
    <div class="nav-scroll" id="nav-container"></div>
  </nav>

  <main class="main" id="main-content">
    <div class="content-area" id="content-area"></div>
  </main>

  <button class="scroll-top" id="scroll-top" onclick="window.scrollTo({top:0})">↑</button>
</div>

<script src="content.js"></script>
<script src="utils.js"></script>
<script>
var _chapterIndex = [];

function buildNavigation() {
  _chapterIndex = [];
  var nav = document.getElementById('nav-container');
  nav.innerHTML = '';

  function buildNode(nodes, parentEl, depth) {
    nodes.forEach(function(node) {
      if (node.type === 'section') {
        var folder = document.createElement('div');
        folder.className = 'nav-folder' + (depth === 0 ? ' open' : '');
        var header = document.createElement('div');
        header.className = 'nav-folder-header';
        header.innerHTML = '<span class="arrow">▶</span> ' + node.title;
        header.onclick = function() { folder.classList.toggle('open'); };
        folder.appendChild(header);
        var body = document.createElement('div');
        body.className = 'nav-folder-body';
        buildNode(node.children, body, depth + 1);
        folder.appendChild(body);
        parentEl.appendChild(folder);
      } else if (node.type === 'item') {
        _chapterIndex.push(node.id);
        var el = document.createElement('div');
        el.className = 'nav-item';
        el.dataset.id = node.id;
        el.innerHTML = '<span class="ch-num">' + _chapterIndex.length + '</span>' + node.title;
        el.onclick = function() {
          openContent(node.id);
          document.getElementById('sidebar').classList.remove('open');
          document.querySelector('.sidebar-overlay').classList.remove('open');
        };
        parentEl.appendChild(el);
      }
    });
  }

  buildNode(NAV_TREE, nav, 0);
}

function showWelcome() {
  document.querySelectorAll('.nav-item').forEach(function(el) { el.classList.remove('active'); });
  document.getElementById('content-area').innerHTML =
    '<div class="welcome fade-in">' +
    '<h1>{{NOVEL_NAME}}</h1>' +
    '<div class="divider"></div>' +
    '<p>从左侧导航选择章节开始阅读</p>' +
    '<div class="stats">' +
    '<div class="stat"><div class="stat-num">{{TOTAL_FILES}}</div><div class="stat-label">章节</div></div>' +
    '<div class="stat"><div class="stat-num">{{WORD_WAN}}万</div><div class="stat-label">总字数</div></div>' +
    '</div></div>';
}

function openContent(id) {
  var data = CONTENT_DATA[id];
  if (!data) return;

  document.querySelectorAll('.nav-item').forEach(function(el) {
    el.classList.toggle('active', el.dataset.id === id);
  });

  var curIdx = _chapterIndex.indexOf(id);
  var prevId = curIdx > 0 ? _chapterIndex[curIdx - 1] : null;
  var nextId = curIdx < _chapterIndex.length - 1 ? _chapterIndex[curIdx + 1] : null;

  var activeEl = document.querySelector('.nav-item[data-id="' + id + '"]');
  if (activeEl) {
    var parent = activeEl.parentElement;
    while (parent) {
      if (parent.classList.contains('nav-folder-body')) {
        parent.parentElement.classList.add('open');
      }
      parent = parent.parentElement;
    }
  }

  var html = renderMarkdown(data.content);
  var sectionPath = data.section.replace(/ \/ /g, ' <span class="sep">/</span> ');

  document.getElementById('content-area').innerHTML =
    '<div class="fade-in">' +
    '<div class="breadcrumb"><span onclick="showWelcome()">首页</span><span class="sep">/</span>' + sectionPath + '</div>' +
    '<div class="article-meta"><h1>' + data.title + '</h1>' +
    '<div class="reading-time">约 ' + Math.ceil(data.content.length / 500) + ' 分钟阅读 · ' + data.content.length + ' 字</div></div>' +
    '<div class="article-body">' + html + '</div>' +
    '<div class="chapter-nav">' +
    (prevId
      ? '<button onclick="openContent(\'' + prevId + '\')">← ' + CONTENT_DATA[prevId].title + '</button>'
      : '<button disabled>← 已是第一章</button>') +
    '<span class="pos">' + (curIdx + 1) + ' / ' + _chapterIndex.length + '</span>' +
    (nextId
      ? '<button onclick="openContent(\'' + nextId + '\')">' + CONTENT_DATA[nextId].title + ' →</button>'
      : '<button disabled>已是最后一章 →</button>') +
    '</div></div>';

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.querySelector('.sidebar-overlay').classList.toggle('open');
}

var _scrollTicking = false;
window.addEventListener('scroll', function() {
  if (!_scrollTicking) {
    requestAnimationFrame(function() {
      var bar = document.getElementById('progress-bar');
      if (bar) {
        var st = window.scrollY;
        var dh = document.documentElement.scrollHeight - window.innerHeight;
        bar.style.width = (dh > 0 ? (st / dh) * 100 : 0) + '%';
        var stb = document.getElementById('scroll-top');
        if (stb) stb.classList.toggle('visible', st > 400);
      }
      _scrollTicking = false;
    });
    _scrollTicking = true;
  }
});

window.addEventListener('load', function() {
  setTimeout(function() {
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('app').classList.add('active');
  }, 800);
});

(function() {
  var t = localStorage.getItem('theme') || 'warm';
  document.documentElement.setAttribute('data-theme', t);
  var icons = { warm: '☀', light: '○', dark: '●' };
  var btn = document.querySelector('.theme-toggle');
  if (btn) btn.textContent = icons[t];
  window.cycleTheme = function() {
    var s = ['warm', 'light', 'dark'];
    var cur = document.documentElement.getAttribute('data-theme');
    var i = (s.indexOf(cur) + 1) % s.length;
    document.documentElement.setAttribute('data-theme', s[i]);
    localStorage.setItem('theme', s[i]);
    if (btn) btn.textContent = icons[s[i]];
  };
})();

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    var sb = document.getElementById('sidebar');
    if (sb && sb.classList.contains('open')) toggleSidebar();
  }
});

document.addEventListener('DOMContentLoaded', function() {
  buildNavigation();
  showWelcome();
});
</script>
</body>
</html>'''

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python generate_website.py <小说目录名>")
        print("示例: python generate_website.py 夏夜")
        sys.exit(1)
    generate(sys.argv[1])
