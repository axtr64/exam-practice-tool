#!/usr/bin/env python3
"""
==========================================================================
  Exam Practice Tool — Deployment Script
==========================================================================
  USAGE:
    1. Place this file (main.py) and exam_data.js in the same folder.
    2. Run:  python main.py
    3. Your default browser will open automatically.

  To change exams, replace exam_data.js with another data file of the
  same structure (e.g., rename exam_data_python.js to exam_data.js).

  Tested on Windows 10/11, Ubuntu 22+, macOS 14+.
==========================================================================
"""

import http.server
import socketserver
import webbrowser
import threading
import os
import sys
import signal
import time

# ──────────────────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────────────────
DEFAULT_PORT = 8080
MAX_PORT_ATTEMPTS = 20

# ──────────────────────────────────────────────────────────
#  Embedded HTML / CSS / JS  (minified index.html)
# ──────────────────────────────────────────────────────────
HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Exam Practice Tool</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Crimson+Pro:ital,wght@0,300;0,400;0,500;0,600;1,400&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
html{font-size:16px;scroll-behavior:smooth}
body{font-family:'Crimson Pro',serif;font-weight:400;line-height:1.6;color:var(--text-primary);background:var(--bg-base);min-height:100vh;overflow-x:hidden;transition:background .3s,color .3s}
:root{--font-display:'Bebas Neue',cursive;--font-body:'Crimson Pro',serif;--font-mono:'DM Mono',monospace;--radius:6px;--radius-lg:12px;--radius-xl:20px;--transition:0.3s cubic-bezier(.4,0,.2,1);--header-h:56px;--sidebar-w:260px;--proctor-h:0px}
[data-theme="dark"]{--bg-base:#0a0c10;--bg-surface:#11141a;--bg-elevated:#191d26;--bg-hover:#21262f;--accent:#d4a843;--accent-glow:rgba(212,168,67,.15);--accent-hover:#e6bc5a;--text-primary:#e8e4dc;--text-secondary:#8a857d;--text-muted:#55524d;--success:#3ddc84;--success-bg:rgba(61,220,132,.1);--danger:#ff6b6b;--danger-bg:rgba(255,107,107,.1);--warning:#ffa726;--warning-bg:rgba(255,167,38,.12);--border:#1f2330;--shadow:0 4px 24px rgba(0,0,0,.4)}
[data-theme="light"]{--bg-base:#f0ece3;--bg-surface:#ffffff;--bg-elevated:#f8f5ef;--bg-hover:#eae5db;--accent:#a67c00;--accent-glow:rgba(166,124,0,.1);--accent-hover:#8a6800;--text-primary:#1a1715;--text-secondary:#6b6560;--text-muted:#9a958d;--success:#2e7d32;--success-bg:rgba(46,125,50,.08);--danger:#c62828;--danger-bg:rgba(198,40,40,.08);--warning:#e65100;--warning-bg:rgba(230,81,0,.08);--border:#d5d0c8;--shadow:0 4px 24px rgba(0,0,0,.08)}
h1,h2,h3,h4{font-family:var(--font-display);font-weight:400;letter-spacing:.04em;line-height:1.1}
h1{font-size:2.5rem}h2{font-size:2rem}h3{font-size:1.5rem}h4{font-size:1.25rem}
p{font-size:1.05rem}
a{color:var(--accent);text-decoration:none}
::-webkit-scrollbar{width:6px}
::-webkit-scrollbar-track{background:var(--bg-base)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
::-webkit-scrollbar-thumb:hover{background:var(--text-muted)}
.app-header{position:fixed;top:0;left:0;right:0;height:var(--header-h);background:var(--bg-surface);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 24px;z-index:100;transition:background var(--transition)}
.header-left{display:flex;align-items:center;gap:12px}
.header-logo{width:32px;height:32px;display:flex;align-items:center;justify-content:center;color:var(--accent)}
.header-logo svg{width:26px;height:26px}
.header-title{font-family:var(--font-display);font-size:1.3rem;letter-spacing:.08em;color:var(--accent)}
.header-right{display:flex;align-items:center;gap:12px}
.theme-toggle{background:none;border:1px solid var(--border);border-radius:50%;width:36px;height:36px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--text-secondary);transition:all var(--transition)}
.theme-toggle:hover{border-color:var(--accent);color:var(--accent)}
.mode-badge{font-family:var(--font-mono);font-size:.7rem;font-weight:500;text-transform:uppercase;letter-spacing:.1em;padding:4px 10px;border-radius:4px;display:none}
.mode-badge.practice{background:var(--success-bg);color:var(--success);border:1px solid var(--success)}
.mode-badge.strict{background:var(--danger-bg);color:var(--danger);border:1px solid var(--danger)}
.page{display:none;padding-top:calc(var(--header-h) + var(--proctor-h));min-height:100vh}
.page.active{display:block;animation:fadeIn .25s ease}
.page.strict-offset{--proctor-h:38px}
.landing-content{max-width:820px;margin:0 auto;padding:56px 24px 40px;text-align:center}
.landing-icon{width:80px;height:80px;margin:0 auto 24px;display:flex;align-items:center;justify-content:center;background:var(--accent-glow);border-radius:var(--radius-xl);border:1px solid rgba(212,168,67,.3)}
.landing-icon svg{width:40px;height:40px;color:var(--accent)}
.landing-title{font-size:3rem;color:var(--text-primary);margin-bottom:6px}
.landing-subtitle{font-size:1.15rem;color:var(--text-secondary);font-style:italic;margin-bottom:10px}
.landing-description{font-size:1rem;color:var(--text-muted);max-width:620px;margin:0 auto 8px;line-height:1.7}
.question-count{font-family:var(--font-mono);font-size:.75rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-bottom:44px}
.mode-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:36px}
.mode-card{background:var(--bg-surface);border:2px solid var(--border);border-radius:var(--radius-lg);padding:30px 24px;cursor:pointer;transition:all var(--transition);text-align:left;position:relative;overflow:hidden}
.mode-card::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:transparent;transition:background var(--transition)}
.mode-card:hover{border-color:var(--text-muted);background:var(--bg-elevated)}
.mode-card.selected{border-color:var(--accent);background:var(--accent-glow)}
.mode-card.selected::before{background:var(--accent)}
.mode-card-icon{width:44px;height:44px;margin-bottom:14px;display:flex;align-items:center;justify-content:center;border-radius:var(--radius)}
.mode-card-icon svg{width:26px;height:26px}
.mode-card h3{font-size:1.45rem;margin-bottom:6px;color:var(--text-primary)}
.mode-card p{font-size:.95rem;color:var(--text-secondary);margin-bottom:14px;line-height:1.5}
.mode-card ul{list-style:none;padding:0}
.mode-card ul li{font-family:var(--font-mono);font-size:.75rem;color:var(--text-muted);padding:3px 0 3px 16px;position:relative}
.mode-card ul li::before{content:'';position:absolute;left:0;top:50%;width:5px;height:5px;border-radius:50%;background:var(--text-muted);transform:translateY(-50%);transition:background var(--transition)}
.mode-card.selected ul li::before{background:var(--accent)}
.btn-start{font-family:var(--font-display);font-size:1.35rem;letter-spacing:.1em;padding:14px 48px;background:var(--accent);color:#0a0a0a;border:none;border-radius:var(--radius);cursor:pointer;transition:all var(--transition);text-transform:uppercase}
.btn-start:hover:not(:disabled){background:var(--accent-hover);letter-spacing:.14em}
.btn-start:disabled{opacity:.35;cursor:not-allowed}
.btn{font-family:var(--font-display);font-size:1rem;letter-spacing:.08em;padding:10px 24px;border:none;border-radius:var(--radius);cursor:pointer;transition:all var(--transition);text-transform:uppercase}
.btn-primary{background:var(--accent);color:#0a0a0a}
.btn-primary:hover:not(:disabled){background:var(--accent-hover)}
.btn-secondary{background:var(--bg-elevated);color:var(--text-secondary);border:1px solid var(--border)}
.btn-secondary:hover{border-color:var(--accent);color:var(--accent)}
.btn-danger{background:var(--danger);color:#fff}
.btn-danger:hover{filter:brightness(1.1)}
.btn:disabled{opacity:.4;cursor:not-allowed}
.previous-stats{margin-top:40px;padding-top:24px;border-top:1px solid var(--border);display:none}
.previous-stats.has-data{display:block}
.previous-stats h4{font-size:1rem;color:var(--text-muted);margin-bottom:14px;letter-spacing:.06em}
.stats-row{display:flex;justify-content:center;gap:36px}
.stats-row .stat{text-align:center}
.stats-row .stat-val{font-family:var(--font-mono);font-size:1.5rem;font-weight:500;color:var(--accent);display:block}
.stats-row .stat-lbl{font-family:var(--font-mono);font-size:.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em}
.exam-layout{display:grid;grid-template-columns:var(--sidebar-w) 1fr;min-height:calc(100vh - var(--header-h) - var(--proctor-h))}
.stats-sidebar{background:var(--bg-surface);border-right:1px solid var(--border);padding:24px 20px;position:sticky;top:calc(var(--header-h) + var(--proctor-h));height:calc(100vh - var(--header-h) - var(--proctor-h));overflow-y:auto;transition:background var(--transition)}
.stats-sidebar h3{font-size:1.05rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:22px;padding-bottom:12px;border-bottom:1px solid var(--border)}
.stat-item{display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid var(--border)}
.stat-label{font-family:var(--font-mono);font-size:.72rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em}
.stat-value{font-family:var(--font-mono);font-size:.95rem;font-weight:500;color:var(--text-primary)}
.stat-value.time-warning{color:var(--warning);animation:pulse 1s infinite}
.stat-value.time-critical{color:var(--danger);animation:pulse .5s infinite}
.progress-section{margin-top:22px}
.progress-label{font-family:var(--font-mono);font-size:.68rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px}
.progress-segments{display:flex;gap:3px;margin-bottom:8px}
.progress-segment{flex:1;height:10px;background:var(--bg-elevated);border-radius:2px;transition:background .4s ease}
.progress-segment.correct{background:var(--success)}
.progress-segment.wrong{background:var(--danger)}
.progress-segment.current{background:var(--accent);animation:pulse 1.5s infinite}
.progress-segment.answered-default{background:var(--text-muted);opacity:.55}
.progress-text{font-family:var(--font-mono);font-size:.78rem;color:var(--text-secondary);text-align:right}
.question-area{padding:32px 40px;max-width:820px}
.question-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid var(--border)}
.question-counter{font-family:var(--font-mono);font-size:.78rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em}
.question-type-badge{font-family:var(--font-mono);font-size:.68rem;color:var(--accent);background:var(--accent-glow);padding:3px 10px;border-radius:4px;border:1px solid rgba(212,168,67,.3);text-transform:uppercase;letter-spacing:.05em}
.question-text{font-size:1.2rem;line-height:1.75;color:var(--text-primary);margin-bottom:28px}
.options-list{display:flex;flex-direction:column;gap:10px;margin-bottom:24px}
.option-item{display:flex;align-items:center;gap:14px;padding:14px 18px;background:var(--bg-surface);border:2px solid var(--border);border-radius:var(--radius);cursor:pointer;transition:all var(--transition);user-select:none}
.option-item:hover:not(.disabled){border-color:var(--text-muted);background:var(--bg-elevated)}
.option-item.selected{border-color:var(--accent);background:var(--accent-glow)}
.option-item.correct{border-color:var(--success);background:var(--success-bg)}
.option-item.wrong{border-color:var(--danger);background:var(--danger-bg)}
.option-item.disabled{cursor:default;opacity:.75}
.option-item input[type="radio"]{display:none}
.option-marker{width:32px;height:32px;display:flex;align-items:center;justify-content:center;border:2px solid var(--border);border-radius:50%;font-family:var(--font-mono);font-size:.78rem;font-weight:500;color:var(--text-muted);flex-shrink:0;transition:all var(--transition)}
.option-item.selected .option-marker{border-color:var(--accent);background:var(--accent);color:#0a0a0a}
.option-item.correct .option-marker{border-color:var(--success);background:var(--success);color:#0a0a0a}
.option-item.wrong .option-marker{border-color:var(--danger);background:var(--danger);color:#fff}
.option-text{font-size:1rem;line-height:1.5;color:var(--text-primary)}
.exact-answer{margin-bottom:24px}
.exact-answer label{display:block;font-family:var(--font-mono);font-size:.78rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px}
.exact-input{width:100%;max-width:420px;padding:12px 16px;font-family:var(--font-mono);font-size:1rem;color:var(--text-primary);background:var(--bg-surface);border:2px solid var(--border);border-radius:var(--radius);outline:none;transition:all var(--transition)}
.exact-input:focus{border-color:var(--accent);background:var(--bg-elevated)}
.exact-input.correct{border-color:var(--success);background:var(--success-bg)}
.exact-input.wrong{border-color:var(--danger);background:var(--danger-bg)}
.exact-input:disabled{opacity:.7;cursor:not-allowed}
.feedback{padding:14px 18px;border-radius:var(--radius);font-family:var(--font-mono);font-size:.82rem;font-weight:500;margin-bottom:16px;display:none;border:1px solid transparent}
.feedback.show{display:block;animation:fadeUp .3s ease}
.feedback.correct{background:var(--success-bg);color:var(--success);border-color:var(--success)}
.feedback.wrong{background:var(--danger-bg);color:var(--danger);border-color:var(--danger)}
.feedback.recorded{background:var(--accent-glow);color:var(--accent);border-color:var(--accent)}
.explanation{padding:18px 20px;background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:24px;display:none}
.explanation.show{display:block;animation:fadeUp .3s ease}
.explanation-label{font-family:var(--font-mono);font-size:.68rem;color:var(--accent);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px}
.explanation-text{font-size:.95rem;color:var(--text-secondary);line-height:1.65}
.question-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:8px}
.results-content{max-width:820px;margin:0 auto;padding:40px 24px;text-align:center}
.score-display{margin-bottom:32px}
.score-number{font-family:var(--font-display);font-size:6rem;line-height:1;color:var(--accent);animation:scoreReveal .8s ease-out}
.score-label{font-family:var(--font-mono);font-size:.9rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.08em;margin-top:8px}
.pass-fail{font-family:var(--font-display);font-size:1.8rem;letter-spacing:.1em;margin-bottom:28px}
.pass-fail.pass{color:var(--success)}.pass-fail.fail{color:var(--danger)}
.results-stats{display:flex;justify-content:center;gap:36px;margin-bottom:36px;padding:20px;background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-lg);flex-wrap:wrap}
.results-stats .stat{text-align:center;min-width:70px}
.results-stats .stat-val{font-family:var(--font-mono);font-size:1.3rem;font-weight:500;color:var(--text-primary);display:block}
.results-stats .stat-lbl{font-family:var(--font-mono);font-size:.68rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.05em}
.review-section{text-align:left;margin-top:40px}
.review-section h3{font-size:1.2rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em;margin-bottom:18px;padding-bottom:12px;border-bottom:1px solid var(--border)}
.review-item{background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:10px;overflow:hidden;transition:border-color var(--transition)}
.review-item:hover{border-color:var(--text-muted)}
.review-header{display:flex;align-items:center;padding:14px 18px;cursor:pointer;transition:background var(--transition);gap:12px}
.review-header:hover{background:var(--bg-elevated)}
.review-q-num{font-family:var(--font-mono);font-size:.75rem;color:var(--text-muted);flex-shrink:0;width:32px}
.review-q-text{flex:1;font-size:.92rem;color:var(--text-primary);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.review-status{font-family:var(--font-mono);font-size:.68rem;font-weight:500;text-transform:uppercase;letter-spacing:.05em;padding:3px 8px;border-radius:4px;flex-shrink:0}
.review-status.correct{background:var(--success-bg);color:var(--success)}
.review-status.wrong{background:var(--danger-bg);color:var(--danger)}
.review-detail{padding:4px 18px 18px;display:none;border-top:1px solid var(--border)}
.review-detail.show{display:block;animation:fadeUp .25s ease}
.review-detail p{margin-top:10px;font-size:.9rem;color:var(--text-secondary);line-height:1.6}
.review-detail .correct-answer{color:var(--success);font-weight:600}
.review-detail .user-answer{color:var(--danger);font-weight:600}
.strict-init-overlay{position:fixed;inset:0;background:rgba(0,0,0,.88);display:none;align-items:center;justify-content:center;z-index:1000;backdrop-filter:blur(6px)}
.strict-init-overlay.show{display:flex}
.strict-init-modal{background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius-lg);padding:36px 40px;max-width:480px;width:92%;text-align:center;animation:modalPop .3s ease}
.strict-init-icon{width:60px;height:60px;margin:0 auto 18px;display:flex;align-items:center;justify-content:center;background:var(--accent-glow);border-radius:50%;border:1px solid rgba(212,168,67,.3)}
.strict-init-icon svg{width:30px;height:30px;color:var(--accent)}
.strict-init-modal h3{font-size:1.6rem;letter-spacing:.06em;color:var(--text-primary);margin-bottom:6px}
.strict-init-modal>p{font-size:.95rem;color:var(--text-secondary);margin-bottom:24px;line-height:1.5}
.perm-check-row{display:flex;align-items:center;gap:14px;padding:14px 18px;background:var(--bg-elevated);border:1px solid var(--border);border-radius:var(--radius);margin-bottom:10px;transition:border-color var(--transition)}
.perm-check-row.granted{border-color:rgba(61,220,132,.3)}
.perm-check-row.denied{border-color:rgba(255,107,107,.3)}
.perm-check-icon{width:36px;height:36px;display:flex;align-items:center;justify-content:center;border-radius:50%;background:var(--bg-surface);border:1px solid var(--border);flex-shrink:0;transition:all var(--transition)}
.perm-check-icon svg{width:18px;height:18px;color:var(--text-muted);transition:color var(--transition)}
.perm-check-row.granted .perm-check-icon{background:var(--success-bg);border-color:var(--success)}
.perm-check-row.granted .perm-check-icon svg{color:var(--success)}
.perm-check-row.denied .perm-check-icon{background:var(--danger-bg);border-color:var(--danger)}
.perm-check-row.denied .perm-check-icon svg{color:var(--danger)}
.perm-check-label{flex:1;text-align:left}
.perm-check-label strong{display:block;font-family:var(--font-mono);font-size:.78rem;font-weight:500;color:var(--text-primary);letter-spacing:.02em}
.perm-check-label span{font-family:var(--font-mono);font-size:.7rem;color:var(--text-muted);letter-spacing:.02em}
.perm-check-status{font-family:var(--font-mono);font-size:.72rem;font-weight:500;text-transform:uppercase;letter-spacing:.05em;flex-shrink:0}
.perm-check-status.pending{color:var(--text-muted)}
.perm-check-status.checking{color:var(--accent)}
.perm-check-status.granted{color:var(--success)}
.perm-check-status.denied{color:var(--danger)}
.perm-spinner{display:inline-block;width:14px;height:14px;border:2px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .6s linear infinite;vertical-align:middle;margin-right:6px}
.perm-audio-meter{margin-top:8px;display:none}
.perm-audio-meter.show{display:block}
.perm-audio-track{width:100%;height:6px;background:var(--bg-surface);border-radius:3px;overflow:hidden;border:1px solid var(--border)}
.perm-audio-fill{height:100%;width:0%;background:var(--success);border-radius:3px;transition:width .1s}
.perm-message{margin-top:18px;padding:12px 16px;border-radius:var(--radius);font-family:var(--font-mono);font-size:.78rem;font-weight:500;display:none;border:1px solid transparent}
.perm-message.show{display:block;animation:fadeUp .3s ease}
.perm-message.error{background:var(--danger-bg);color:var(--danger);border-color:var(--danger)}
.perm-message.success{background:var(--success-bg);color:var(--success);border-color:var(--success)}
.perm-buttons{margin-top:20px;display:flex;gap:10px;justify-content:center}
.perm-buttons .btn{min-width:120px}
.fs-required-overlay{position:fixed;inset:0;background:rgba(0,0,0,.92);display:none;align-items:center;justify-content:center;z-index:1000;backdrop-filter:blur(8px)}
.fs-required-overlay.show{display:flex}
.fs-required-modal{background:var(--bg-surface);border:2px solid var(--warning);border-radius:var(--radius-lg);padding:40px;max-width:460px;width:90%;text-align:center;animation:modalPop .3s ease}
.fs-required-modal .modal-icon{width:60px;height:60px;margin:0 auto 18px;display:flex;align-items:center;justify-content:center;background:var(--warning-bg);border-radius:50%;border:1px solid rgba(255,167,38,.3)}
.fs-required-modal .modal-icon svg{width:30px;height:30px;color:var(--warning)}
.fs-required-modal h3{font-size:1.4rem;color:var(--warning);margin-bottom:10px;letter-spacing:.06em}
.fs-required-modal p{color:var(--text-secondary);margin-bottom:24px;font-size:1rem;line-height:1.6}
.camera-container{position:fixed;bottom:20px;right:20px;width:200px;border-radius:var(--radius-lg);overflow:hidden;border:2px solid var(--accent);box-shadow:var(--shadow);z-index:200;display:none;background:#000}
.camera-container video{width:100%;display:block;transform:scaleX(-1)}
.camera-label{position:absolute;top:8px;left:8px;display:flex;align-items:center;gap:6px;font-family:var(--font-mono);font-size:.65rem;font-weight:500;color:#fff;background:rgba(0,0,0,.55);padding:2px 8px;border-radius:4px}
.live-dot{width:6px;height:6px;border-radius:50%;background:#ff3b3b;animation:livePulse 1s infinite}
.proctor-bar{position:fixed;top:var(--header-h);left:0;right:0;height:36px;background:rgba(220,50,50,.07);border-bottom:1px solid rgba(220,50,50,.25);display:none;align-items:center;justify-content:center;gap:20px;z-index:150;font-family:var(--font-mono);font-size:.68rem;font-weight:500;color:var(--danger);text-transform:uppercase;letter-spacing:.1em}
.proctor-bar .proctor-dot{width:8px;height:8px;border-radius:50%;background:var(--danger);animation:livePulse 1.5s infinite}
.proctor-bar.active{display:flex}
.time-expired-overlay{position:fixed;inset:0;background:rgba(0,0,0,.88);display:none;align-items:center;justify-content:center;z-index:1000;backdrop-filter:blur(6px)}
.time-expired-overlay.show{display:flex}
.time-expired-modal{background:var(--bg-surface);border:2px solid var(--danger);border-radius:var(--radius-lg);padding:40px;max-width:480px;width:90%;text-align:center;animation:modalPop .3s ease}
.time-expired-modal .modal-icon{width:60px;height:60px;margin:0 auto 18px;display:flex;align-items:center;justify-content:center;background:var(--danger-bg);border-radius:50%}
.time-expired-modal .modal-icon svg{width:30px;height:30px;color:var(--danger)}
.time-expired-modal h3{font-size:1.5rem;color:var(--danger);margin-bottom:10px;letter-spacing:.06em}
.time-expired-modal p{color:var(--text-secondary);margin-bottom:24px;font-size:1rem;line-height:1.6}
.security-overlay{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:1000}
.security-overlay.show{display:flex}
.security-modal{background:var(--bg-surface);border:2px solid var(--danger);border-radius:var(--radius-lg);padding:40px;max-width:480px;width:90%;text-align:center;animation:modalPop .3s ease}
.modal-icon{width:60px;height:60px;margin:0 auto 18px;display:flex;align-items:center;justify-content:center;background:var(--danger-bg);border-radius:50%}
.modal-icon svg{width:30px;height:30px;color:var(--danger)}
.security-modal h3{font-size:1.5rem;color:var(--danger);margin-bottom:10px;letter-spacing:.06em}
.security-modal p{color:var(--text-secondary);margin-bottom:24px;font-size:1rem;line-height:1.6}
.security-log{position:fixed;bottom:20px;left:20px;width:300px;background:var(--bg-surface);border:1px solid var(--border);border-radius:var(--radius);z-index:200;display:none;font-family:var(--font-mono);font-size:.68rem;box-shadow:var(--shadow)}
.security-log.active{display:block}
.log-header{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid var(--border);cursor:pointer;user-select:none}
.log-header span{color:var(--text-muted);text-transform:uppercase;letter-spacing:.1em;font-weight:500}
.log-header button{background:none;border:none;color:var(--text-muted);cursor:pointer;font-family:var(--font-mono);font-size:.65rem;text-transform:uppercase;letter-spacing:.05em}
.log-entries{max-height:180px;overflow-y:auto;padding:6px 8px}
.log-entry{padding:4px 6px;color:var(--text-secondary);border-bottom:1px solid var(--border);line-height:1.4}
.log-entry:last-child{border-bottom:none}
.log-entry.violation{color:var(--danger)}
.log-time{color:var(--text-muted);margin-right:8px}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes scoreReveal{from{opacity:0;transform:scale(.6)}to{opacity:1;transform:scale(1)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}
@keyframes livePulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes modalPop{from{transform:scale(.92);opacity:0}to{transform:scale(1);opacity:1}}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:960px){.exam-layout{grid-template-columns:1fr}.stats-sidebar{position:relative;top:0;height:auto;border-right:none;border-bottom:1px solid var(--border);display:flex;flex-wrap:wrap;gap:12px;padding:16px}.stats-sidebar h3{width:100%;margin-bottom:6px;padding-bottom:8px;font-size:.9rem}.stat-item{flex:1;min-width:110px;border-bottom:none;padding:6px 0}.progress-section{width:100%;margin-top:6px}.question-area{padding:24px 20px}.mode-grid{grid-template-columns:1fr}.landing-title{font-size:2.2rem}.camera-container{width:140px;bottom:10px;right:10px}.security-log{width:calc(100% - 20px);left:10px;bottom:10px}}
@media(max-width:520px){.landing-title{font-size:1.8rem}.landing-content{padding:36px 16px 30px}.score-number{font-size:4rem}.results-stats{flex-direction:column;gap:14px}.question-actions{flex-direction:column}.question-actions .btn{width:100%;text-align:center}.review-header{flex-wrap:wrap}.review-q-text{width:100%;order:3;margin-top:6px}.strict-init-modal{padding:28px 20px}}
</style>
</head>
<body>
<header class="app-header">
  <div class="header-left">
    <div class="header-logo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="14" y2="11"/></svg></div>
    <span class="header-title" id="header-title">Exam Practice Tool</span>
  </div>
  <div class="header-right">
    <span class="mode-badge" id="mode-badge"></span>
    <button class="theme-toggle" id="theme-toggle" aria-label="Toggle theme">
      <svg class="icon-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
      <svg class="icon-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display:none"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
    </button>
  </div>
</header>
<section class="page active" id="landing-page">
  <div class="landing-content">
    <div class="landing-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/><line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="14" y2="11"/></svg></div>
    <h2 class="landing-title" id="landing-title">Loading...</h2>
    <p class="landing-subtitle" id="landing-subtitle"></p>
    <p class="landing-description" id="landing-description"></p>
    <p class="question-count" id="question-count"></p>
    <div class="mode-grid">
      <div class="mode-card" data-mode="practice" id="mode-practice">
        <div class="mode-card-icon" style="color:var(--success)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg></div>
        <h3>Practice Mode</h3><p>Get immediate feedback and learn from explanations after each question.</p>
        <ul><li>Instant green / red validation</li><li>Detailed explanations on demand</li><li>No time limit</li></ul>
      </div>
      <div class="mode-card" data-mode="strict" id="mode-strict">
        <div class="mode-card-icon" style="color:var(--danger)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg></div>
        <h3>Strict Mode</h3><p>Simulate a proctored exam environment with camera, microphone, and focus monitoring.</p>
        <ul><li>Camera and mic required to start</li><li>Fullscreen enforced throughout</li><li>Noise detection active</li><li>1 hour time limit enforced</li><li>Tab switching and Alt+Tab prohibited</li><li>New tabs and windows blocked</li></ul>
      </div>
    </div>
    <button class="btn-start" id="start-btn" disabled>Select a Mode to Begin</button>
    <div class="previous-stats" id="previous-stats"><h4>Previous Performance</h4><div class="stats-row" id="prev-stats-row"></div></div>
  </div>
</section>
<section class="page" id="exam-page">
  <div class="exam-layout">
    <aside class="stats-sidebar" id="stats-sidebar">
      <h3>Live Statistics</h3>
      <div class="stat-item"><span class="stat-label">Score</span><span class="stat-value" id="stat-score">0 / 0</span></div>
      <div class="stat-item"><span class="stat-label">Accuracy</span><span class="stat-value" id="stat-accuracy">--</span></div>
      <div class="stat-item"><span class="stat-label">Remaining</span><span class="stat-value" id="stat-remaining">--</span></div>
      <div class="stat-item"><span class="stat-label">Elapsed</span><span class="stat-value" id="stat-time">00:00</span></div>
      <div class="stat-item" id="time-limit-row" style="display:none"><span class="stat-label">Time Limit</span><span class="stat-value" id="stat-time-limit">01:00:00</span></div>
      <div class="stat-item" id="violations-stat" style="display:none"><span class="stat-label">Violations</span><span class="stat-value" id="stat-violations" style="color:var(--danger)">0</span></div>
      <div class="progress-section"><div class="progress-label">Progress</div><div class="progress-segments" id="progress-segments"></div><div class="progress-text" id="progress-text">0%</div></div>
    </aside>
    <main class="question-area" id="question-area">
      <div class="question-header"><span class="question-counter" id="question-counter">Question 1 of 5</span><span class="question-type-badge" id="question-type-badge">Multiple Choice</span></div>
      <div class="question-text" id="question-text"></div>
      <div id="answer-area"></div>
      <div class="feedback" id="feedback"></div>
      <div class="explanation" id="explanation"><div class="explanation-label">Explanation</div><div class="explanation-text" id="explanation-text"></div></div>
      <div class="question-actions" id="question-actions">
        <button class="btn btn-primary" id="submit-btn">Submit Answer</button>
        <button class="btn btn-secondary" id="explanation-btn" style="display:none">Show Explanation</button>
        <button class="btn btn-primary" id="next-btn" style="display:none">Next Question</button>
        <button class="btn btn-danger" id="finish-btn" style="display:none">Submit Exam</button>
      </div>
    </main>
  </div>
</section>
<section class="page" id="results-page"><div class="results-content" id="results-content"></div></section>
<div class="strict-init-overlay" id="strict-init-overlay">
  <div class="strict-init-modal">
    <div class="strict-init-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4"/></svg></div>
    <h3>Environment Check</h3><p>Camera and microphone access are required to enter Strict Mode. Fullscreen will activate automatically once all checks pass.</p>
    <div class="perm-check-row" id="perm-camera-row"><div class="perm-check-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg></div><div class="perm-check-label"><strong>Camera Access</strong><span>Required for visual monitoring</span></div><span class="perm-check-status pending" id="perm-camera-status">Waiting</span></div>
    <div class="perm-check-row" id="perm-mic-row"><div class="perm-check-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg></div><div class="perm-check-label"><strong>Microphone Access</strong><span>Required for noise monitoring</span></div><span class="perm-check-status pending" id="perm-mic-status">Waiting</span></div>
    <div class="perm-audio-meter" id="perm-audio-meter"><div class="perm-audio-track"><div class="perm-audio-fill" id="perm-audio-fill"></div></div></div>
    <div class="perm-message" id="perm-message"></div>
    <div class="perm-buttons" id="perm-buttons"><button class="btn btn-primary" id="perm-check-btn">Check Permissions</button></div>
  </div>
</div>
<div class="fs-required-overlay" id="fs-required-overlay">
  <div class="fs-required-modal">
    <div class="modal-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="8 3 3 3 3 8"/><line x1="3" y1="3" x2="10" y2="10"/><polyline points="16 3 21 3 21 8"/><line x1="21" y1="3" x2="14" y2="10"/><polyline points="8 21 3 21 3 16"/><line x1="3" y1="21" x2="10" y2="14"/><polyline points="16 21 21 21 21 16"/><line x1="21" y1="21" x2="14" y2="14"/></svg></div>
    <h3>Fullscreen Required</h3><p>You have exited fullscreen mode. This has been logged as a violation. You must re-enter fullscreen to continue the exam.</p>
    <button class="btn btn-primary" id="fs-reenter-btn">Re-enter Fullscreen</button>
  </div>
</div>
<div class="camera-container" id="camera-container"><video id="camera-feed" autoplay muted playsinline></video><div class="camera-label"><span class="live-dot"></span> LIVE</div></div>
<div class="proctor-bar" id="proctor-bar"><span class="proctor-dot"></span><span>Monitoring Active</span><span style="opacity:.4">|</span><span>Violations: <span id="proctor-violations">0</span></span></div>
<div class="time-expired-overlay" id="time-expired-overlay"><div class="time-expired-modal"><div class="modal-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg></div><h3>Time Expired</h3><p>The 1-hour time limit has been reached. Your exam is being submitted automatically.</p><button class="btn btn-primary" id="time-expired-btn">View Results</button></div></div>
<div class="security-overlay" id="security-overlay"><div class="security-modal"><div class="modal-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg></div><h3>Security Alert</h3><p id="security-message">Tab switching or window blur detected. This violation has been logged.</p><button class="btn btn-primary" id="dismiss-btn">I Understand</button></div></div>
<div class="security-log" id="security-log"><div class="log-header" id="log-header"><span>Security Log</span><button id="log-toggle-btn">Toggle</button></div><div class="log-entries" id="log-entries"></div></div>
<script src="exam_data.js"></script>
<script>
(function(){
'use strict';
var STRICT_TIME_LIMIT=3600,TIME_WARN_THRESHOLD=300,TIME_CRIT_THRESHOLD=60;
var state={mode:null,questions:[],currentIndex:0,answers:[],correctCount:0,answered:false,selectedOption:null,userInput:'',startTime:null,timerInterval:null,finished:false,cameraStream:null,audioStream:null,audioContext:null,analyserNode:null,audioAnimFrame:null,permAudioFrame:null,violations:[],violationCooldown:false,strictActive:false,logCollapsed:false,permissionsGranted:false,timeExpired:false,focusCheckInterval:null};
var $=function(id){return document.getElementById(id)};var dom={};
function cacheDom(){dom.html=document.documentElement;dom.headerTitle=$('header-title');dom.modeBadge=$('mode-badge');dom.themeToggle=$('theme-toggle');dom.iconSun=dom.themeToggle.querySelector('.icon-sun');dom.iconMoon=dom.themeToggle.querySelector('.icon-moon');dom.landingPage=$('landing-page');dom.examPage=$('exam-page');dom.resultsPage=$('results-page');dom.landingTitle=$('landing-title');dom.landingSubtitle=$('landing-subtitle');dom.landingDescription=$('landing-description');dom.questionCount=$('question-count');dom.modePractice=$('mode-practice');dom.modeStrict=$('mode-strict');dom.startBtn=$('start-btn');dom.previousStats=$('previous-stats');dom.prevStatsRow=$('prev-stats-row');dom.statScore=$('stat-score');dom.statAccuracy=$('stat-accuracy');dom.statRemaining=$('stat-remaining');dom.statTime=$('stat-time');dom.statTimeLimit=$('stat-time-limit');dom.timeLimitRow=$('time-limit-row');dom.statViolations=$('stat-violations');dom.violationsStat=$('violations-stat');dom.progressSegments=$('progress-segments');dom.progressText=$('progress-text');dom.questionCounter=$('question-counter');dom.questionTypeBadge=$('question-type-badge');dom.questionText=$('question-text');dom.answerArea=$('answer-area');dom.feedback=$('feedback');dom.explanation=$('explanation');dom.explanationText=$('explanation-text');dom.submitBtn=$('submit-btn');dom.explanationBtn=$('explanation-btn');dom.nextBtn=$('next-btn');dom.finishBtn=$('finish-btn');dom.resultsContent=$('results-content');dom.strictInitOverlay=$('strict-init-overlay');dom.permCameraRow=$('perm-camera-row');dom.permCameraStatus=$('perm-camera-status');dom.permMicRow=$('perm-mic-row');dom.permMicStatus=$('perm-mic-status');dom.permAudioMeter=$('perm-audio-meter');dom.permAudioFill=$('perm-audio-fill');dom.permMessage=$('perm-message');dom.permButtons=$('perm-buttons');dom.permCheckBtn=$('perm-check-btn');dom.cameraContainer=$('camera-container');dom.cameraFeed=$('camera-feed');dom.proctorBar=$('proctor-bar');dom.proctorViolations=$('proctor-violations');dom.securityOverlay=$('security-overlay');dom.securityMessage=$('security-message');dom.dismissBtn=$('dismiss-btn');dom.securityLog=$('security-log');dom.logHeader=$('log-header');dom.logEntries=$('log-entries');dom.logToggleBtn=$('log-toggle-btn');dom.timeExpiredOverlay=$('time-expired-overlay');dom.timeExpiredBtn=$('time-expired-btn');dom.fsRequiredOverlay=$('fs-required-overlay');dom.fsReenterBtn=$('fs-reenter-btn')}
function init(){cacheDom();loadTheme();setupLanding();bindEvents();loadPreviousStats()}
function loadTheme(){var t=localStorage.getItem('exam_theme')||'dark';dom.html.setAttribute('data-theme',t);updateThemeIcon(t)}
function updateThemeIcon(t){dom.iconSun.style.display=t==='dark'?'block':'none';dom.iconMoon.style.display=t==='light'?'block':'none'}
function toggleTheme(){var c=dom.html.getAttribute('data-theme');var n=c==='dark'?'light':'dark';dom.html.setAttribute('data-theme',n);localStorage.setItem('exam_theme',n);updateThemeIcon(n)}
function setupLanding(){if(typeof examConfig==='undefined'){dom.landingTitle.textContent='Error: exam_data.js Not Found';dom.landingSubtitle.textContent='Place exam_data.js in the same directory and reload.';return}dom.headerTitle.textContent=examConfig.title||'Exam Practice Tool';document.title=(examConfig.title||'Exam')+' \u2014 Exam Practice Tool';dom.landingTitle.textContent=examConfig.title||'Exam Practice Tool';dom.landingSubtitle.textContent=examConfig.subtitle||'';dom.landingDescription.textContent=examConfig.description||'';if(typeof examQuestions!=='undefined'){dom.questionCount.textContent=examQuestions.length+' questions available'}}
function loadPreviousStats(){if(typeof examConfig==='undefined')return;var s=getStats();if(s&&s.attempts>0){dom.previousStats.classList.add('has-data');dom.prevStatsRow.innerHTML='<div class="stat"><span class="stat-val">'+s.bestScore+'%</span><span class="stat-lbl">Best</span></div><div class="stat"><span class="stat-val">'+s.lastScore+'%</span><span class="stat-lbl">Last</span></div><div class="stat"><span class="stat-val">'+s.attempts+'</span><span class="stat-lbl">Attempts</span></div>'}else{dom.previousStats.classList.remove('has-data')}}
function bindEvents(){dom.themeToggle.addEventListener('click',toggleTheme);dom.modePractice.addEventListener('click',function(){selectMode('practice')});dom.modeStrict.addEventListener('click',function(){selectMode('strict')});dom.startBtn.addEventListener('click',startExam);dom.submitBtn.addEventListener('click',submitAnswer);dom.explanationBtn.addEventListener('click',showExplanation);dom.nextBtn.addEventListener('click',nextQuestion);dom.finishBtn.addEventListener('click',finishExam);dom.dismissBtn.addEventListener('click',dismissWarning);dom.logToggleBtn.addEventListener('click',toggleLog);dom.permCheckBtn.addEventListener('click',runPermissionCheck);dom.timeExpiredBtn.addEventListener('click',function(){handleTimeExpired()});dom.fsReenterBtn.addEventListener('click',requestReenterFullscreen);document.addEventListener('keydown',handleKey,true);window.addEventListener('beforeunload',function(e){if(state.mode&&state.startTime&&!state.finished){e.preventDefault();e.returnValue=''}});document.addEventListener('contextmenu',function(e){if(state.strictActive&&state.mode==='strict'){e.preventDefault();e.stopPropagation();logViolation('contextmenu','Right-click blocked');return false}});document.addEventListener('mousedown',function(e){if(state.strictActive&&state.mode==='strict'&&e.button===1){e.preventDefault();e.stopPropagation();logViolation('click','Middle-click blocked');return false}},true);document.addEventListener('dragstart',function(e){if(state.strictActive&&state.mode==='strict'){e.preventDefault();return false}})}
function handleKey(e){if(!state.mode||state.finished)return;if(dom.securityOverlay.classList.contains('show')){e.preventDefault();e.stopPropagation();return}if(dom.strictInitOverlay.classList.contains('show')){e.preventDefault();e.stopPropagation();return}if(dom.timeExpiredOverlay.classList.contains('show')){e.preventDefault();e.stopPropagation();return}if(dom.fsRequiredOverlay.classList.contains('show')){e.preventDefault();e.stopPropagation();return}if(state.strictActive&&state.mode==='strict'){if(e.altKey){e.preventDefault();e.stopPropagation();logViolation('keyboard','Alt key combination blocked (Alt+'+e.key+')');return false}if(e.metaKey){e.preventDefault();e.stopPropagation();logViolation('keyboard','Meta/OS key combination blocked');return false}if(e.ctrlKey){var k=e.key.toLowerCase();if(e.shiftKey&&k!=='a'&&k!=='c'&&k!=='v'&&k!=='x'&&k!=='z'){e.preventDefault();e.stopPropagation();logViolation('keyboard','Blocked Ctrl+Shift+'+k);return false}var navKeys=['t','n','w','l','h','j','o','r','u','p','d','e','i','g','b','k'];if(navKeys.indexOf(k)!==-1){e.preventDefault();e.stopPropagation();logViolation('keyboard','Blocked Ctrl+'+k+' shortcut');return false}}if(e.key.indexOf('F')===0&&e.key.length<=3){var fNum=parseInt(e.key.substring(1));if(fNum>=1&&fNum<=12){e.preventDefault();e.stopPropagation();if(e.key==='F11')logViolation('keyboard','Fullscreen toggle blocked (F11)');else if(e.key==='F12')logViolation('keyboard','Developer tools blocked (F12)');return false}}if(e.key==='Escape'){e.preventDefault();e.stopPropagation();logViolation('keyboard','Escape key blocked');if(!isFullscreen())requestFullscreen();return false}if(e.key==='PrintScreen'){e.preventDefault();e.stopPropagation();logViolation('keyboard','PrintScreen blocked');return false}}if(!state.answered&&state.mode==='practice'){var q=state.questions[state.currentIndex];if(q&&q.type==='multiple-choice'&&e.key>='1'&&e.key<='9'){var idx=parseInt(e.key)-1;var opts=dom.answerArea.querySelectorAll('.option-item');if(idx<opts.length)opts[idx].click()}}if(e.key==='Enter'){if(!state.answered&&dom.submitBtn.style.display!=='none'&&!dom.submitBtn.disabled)submitAnswer();else if(dom.nextBtn.style.display!=='none')nextQuestion();else if(dom.finishBtn.style.display!=='none')finishExam()}}
function selectMode(m){state.mode=m;dom.modePractice.classList.toggle('selected',m==='practice');dom.modeStrict.classList.toggle('selected',m==='strict');dom.startBtn.disabled=false;dom.startBtn.textContent='Start '+(m==='practice'?'Practice':'Strict')+' Exam'}
function startExam(){if(!state.mode||typeof examQuestions==='undefined'||!examQuestions.length)return;var qs=examQuestions.slice();if(examConfig.shuffleQuestions)qs=shuffle(qs);if(examConfig.shuffleOptions){qs=qs.map(function(q){if(q.type==='multiple-choice'&&q.options){return Object.assign({},q,{options:shuffle(q.options.slice())})}return q})}state.questions=qs;if(state.mode==='strict'){state.permissionsGranted=false;showPermInitOverlay()}else{launchExamUI()}}
function showPermInitOverlay(){dom.permCameraRow.className='perm-check-row';dom.permCameraStatus.className='perm-check-status pending';dom.permCameraStatus.textContent='Waiting';dom.permMicRow.className='perm-check-row';dom.permMicStatus.className='perm-check-status pending';dom.permMicStatus.textContent='Waiting';dom.permAudioMeter.classList.remove('show');dom.permMessage.className='perm-message';dom.permMessage.style.display='none';dom.permButtons.innerHTML='<button class="btn btn-primary" id="perm-check-btn">Check Permissions</button>';dom.permCheckBtn=$('perm-check-btn');dom.permCheckBtn.addEventListener('click',runPermissionCheck);dom.permCheckBtn.disabled=false;dom.strictInitOverlay.classList.add('show')}
function closePermInitOverlay(){dom.strictInitOverlay.classList.remove('show');if(state.permAudioFrame){cancelAnimationFrame(state.permAudioFrame);state.permAudioFrame=null}}
async function runPermissionCheck(){dom.permCheckBtn.disabled=true;dom.permCheckBtn.textContent='Checking...';dom.permMessage.className='perm-message';dom.permMessage.style.display='none';var camOk=false;var micOk=false;if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){showPermError('Your browser does not support camera/microphone access.');return}dom.permCameraStatus.className='perm-check-status checking';dom.permCameraStatus.innerHTML='<span class="perm-spinner"></span>Requesting';try{var camStream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:320},height:{ideal:240},facingMode:'user'}});state.cameraStream=camStream;camOk=true;dom.permCameraRow.className='perm-check-row granted';dom.permCameraStatus.className='perm-check-status granted';dom.permCameraStatus.textContent='Granted'}catch(e){dom.permCameraRow.className='perm-check-row denied';dom.permCameraStatus.className='perm-check-status denied';dom.permCameraStatus.textContent='Denied'}dom.permMicStatus.className='perm-check-status checking';dom.permMicStatus.innerHTML='<span class="perm-spinner"></span>Requesting';try{var micStream=await navigator.mediaDevices.getUserMedia({audio:true});state.audioStream=micStream;micOk=true;dom.permMicRow.className='perm-check-row granted';dom.permMicStatus.className='perm-check-status granted';dom.permMicStatus.textContent='Granted';dom.permAudioMeter.classList.add('show');startPermAudioMeter(micStream)}catch(e){dom.permMicRow.className='perm-check-row denied';dom.permMicStatus.className='perm-check-status denied';dom.permMicStatus.textContent='Denied'}if(camOk&&micOk){state.permissionsGranted=true;dom.permMessage.className='perm-message show success';dom.permMessage.textContent='All checks passed. Fullscreen will activate when you begin.';dom.permButtons.innerHTML='<button class="btn btn-danger" id="perm-cancel-btn">Cancel</button><button class="btn btn-primary" id="perm-begin-btn">Begin Exam</button>';$('perm-begin-btn').addEventListener('click',function(){beginStrictExamWithFullscreen()});$('perm-cancel-btn').addEventListener('click',function(){cleanupPermStreams();closePermInitOverlay()})}else{var reasons=[];if(!camOk)reasons.push('camera');if(!micOk)reasons.push('microphone');showPermError('Access denied for: '+reasons.join(', ')+'. Both are required.')}}
function showPermError(msg){dom.permMessage.className='perm-message show error';dom.permMessage.textContent=msg;dom.permButtons.innerHTML='<button class="btn btn-secondary" id="perm-cancel-btn">Cancel</button><button class="btn btn-primary" id="perm-retry-btn">Retry</button>';$('perm-retry-btn').addEventListener('click',function(){cleanupPermStreams();runPermissionCheck()});$('perm-cancel-btn').addEventListener('click',function(){cleanupPermStreams();closePermInitOverlay()})}
function cleanupPermStreams(){if(state.audioStream){state.audioStream.getTracks().forEach(function(t){t.stop()});state.audioStream=null}if(state.cameraStream){state.cameraStream.getTracks().forEach(function(t){t.stop()});state.cameraStream=null}if(state.permAudioFrame){cancelAnimationFrame(state.permAudioFrame);state.permAudioFrame=null}}
function startPermAudioMeter(stream){try{var ctx=new(window.AudioContext||window.webkitAudioContext)();var src=ctx.createMediaStreamSource(stream);var analyser=ctx.createAnalyser();analyser.fftSize=256;src.connect(analyser);var data=new Uint8Array(analyser.frequencyBinCount);(function tick(){if(!state.audioStream){ctx.close().catch(function(){});return}analyser.getByteFrequencyData(data);var avg=0;for(var i=0;i<data.length;i++)avg+=data[i];avg=avg/data.length/255;dom.permAudioFill.style.width=Math.min(avg*300,100)+'%';state.permAudioFrame=requestAnimationFrame(tick)})()}catch(e){}}
function isFullscreen(){return !!(document.fullscreenElement||document.webkitFullscreenElement||document.mozFullScreenElement||document.msFullscreenElement)}
async function requestFullscreen(){try{var el=document.documentElement;if(el.requestFullscreen)await el.requestFullscreen();else if(el.webkitRequestFullscreen)await el.webkitRequestFullscreen();else if(el.mozRequestFullScreen)await el.mozRequestFullScreen();else if(el.msRequestFullscreen)await el.msRequestFullscreen();return true}catch(e){return false}}
async function beginStrictExamWithFullscreen(){closePermInitOverlay();var fsOk=await requestFullscreen();if(!fsOk){dom.permMessage.className='perm-message show error';dom.permMessage.textContent='Fullscreen was blocked by your browser. Please allow fullscreen and try again.';dom.strictInitOverlay.classList.add('show');dom.permButtons.innerHTML='<button class="btn btn-secondary" id="perm-cancel-btn">Cancel</button><button class="btn btn-primary" id="perm-retry-fs-btn">Retry Fullscreen</button>';$('perm-retry-fs-btn').addEventListener('click',function(){beginStrictExamWithFullscreen()});$('perm-cancel-btn').addEventListener('click',function(){cleanupPermStreams();closePermInitOverlay()});return}launchStrictExam()}
function requestReenterFullscreen(){requestFullscreen().then(function(ok){if(ok){dom.fsRequiredOverlay.classList.remove('show');addLog('Fullscreen re-entered')}})}
function initFullscreenMonitor(){var handler=function(){if(!state.strictActive||state.mode!=='strict'||state.finished)return;if(!isFullscreen()){dom.fsRequiredOverlay.classList.add('show');logViolation('fullscreen','Exited fullscreen mode')}else{dom.fsRequiredOverlay.classList.remove('show')}};document.addEventListener('fullscreenchange',handler);document.addEventListener('webkitfullscreenchange',handler);document.addEventListener('mozfullscreenchange',handler);document.addEventListener('MSFullscreenChange',handler)}
function exitFullscreenIfNeeded(){if(isFullscreen()){try{if(document.exitFullscreen)document.exitFullscreen();else if(document.webkitExitFullscreen)document.webkitExitFullscreen();else if(document.mozCancelFullScreen)document.mozCancelFullScreen();else if(document.msExitFullscreen)document.msExitFullscreen()}catch(e){}}}
function launchExamUI(){state.currentIndex=0;state.answers=[];state.correctCount=0;state.answered=false;state.selectedOption=null;state.userInput='';state.startTime=Date.now();state.finished=false;state.violations=[];state.strictActive=false;state.violationCooldown=false;state.timeExpired=false;showPage('exam');dom.modeBadge.textContent=state.mode==='practice'?'Practice':'Strict';dom.modeBadge.className='mode-badge '+state.mode;dom.modeBadge.style.display='inline-block';dom.violationsStat.style.display=state.mode==='strict'?'flex':'none';if(state.mode==='strict'){dom.timeLimitRow.style.display='flex';dom.statTimeLimit.textContent=fmtTimeHMS(STRICT_TIME_LIMIT);dom.examPage.classList.add('strict-offset');dom.proctorBar.classList.add('active');dom.securityLog.classList.add('active')}else{dom.timeLimitRow.style.display='none';dom.examPage.classList.remove('strict-offset')}renderProgressBar();startTimer();renderQuestion()}
async function launchStrictExam(){state.strictActive=true;if(state.cameraStream){dom.cameraFeed.srcObject=state.cameraStream;dom.cameraContainer.style.display='block'}else{try{var camStream=await navigator.mediaDevices.getUserMedia({video:{width:{ideal:320},height:{ideal:240},facingMode:'user'}});state.cameraStream=camStream;dom.cameraFeed.srcObject=camStream;dom.cameraContainer.style.display='block'}catch(e){}}launchExamUI();initFullscreenMonitor();initFocusMonitor();startFocusCheck();if(state.audioStream){try{state.audioContext=new(window.AudioContext||window.webkitAudioContext)();var src=state.audioContext.createMediaStreamSource(state.audioStream);state.analyserNode=state.audioContext.createAnalyser();state.analyserNode.fftSize=256;src.connect(state.analyserNode);addLog('Audio monitoring initialized');monitorAudio()}catch(e){addLog('Audio monitoring setup failed')}}addLog('Fullscreen enforced');addLog('Focus monitoring active');addLog('Alt+Tab / OS switching blocked');addLog('New tabs and windows blocked');addLog('Right-click disabled');addLog('Keyboard shortcuts restricted');addLog('1-hour time limit enforced');addLog('Exam started in Strict Mode');if(state.cameraStream){state.cameraStream.getVideoTracks().forEach(function(track){track.addEventListener('ended',function(){if(state.strictActive&&!state.finished)logViolation('camera','Camera was disconnected or permission revoked')})})}if(state.audioStream){state.audioStream.getAudioTracks().forEach(function(track){track.addEventListener('ended',function(){if(state.strictActive&&!state.finished)logViolation('microphone','Microphone was disconnected or permission revoked')})})}}
function startTimer(){stopTimer();state.timerInterval=setInterval(function(){var el=Math.floor((Date.now()-state.startTime)/1000);if(state.mode==='strict'){var remaining=STRICT_TIME_LIMIT-el;dom.statTime.textContent=fmtTimeHMS(el);dom.statTimeLimit.textContent=fmtTimeHMS(Math.max(remaining,0));dom.statTime.className='stat-value';dom.statTimeLimit.className='stat-value';if(remaining<=TIME_CRIT_THRESHOLD){dom.statTime.classList.add('time-critical');dom.statTimeLimit.classList.add('time-critical')}else if(remaining<=TIME_WARN_THRESHOLD){dom.statTime.classList.add('time-warning');dom.statTimeLimit.classList.add('time-warning')}if(remaining<=0&&!state.finished&&!state.timeExpired){state.timeExpired=true;stopTimer();addLog('TIME EXPIRED: 1-hour limit reached');showTimeExpiredOverlay()}}else{dom.statTime.textContent=fmtTime(el)}},1000)}
function stopTimer(){if(state.timerInterval){clearInterval(state.timerInterval);state.timerInterval=null}}
function showTimeExpiredOverlay(){dom.timeExpiredOverlay.classList.add('show')}
function handleTimeExpired(){dom.timeExpiredOverlay.classList.remove('show');autoSubmitExam()}
function autoSubmitExam(){while(state.answers.length<state.questions.length){var idx=state.answers.length;var q=state.questions[idx];state.answers.push({questionId:q.id,userAnswer:'(No answer \u2014 time expired)',isCorrect:false,question:q.question,correctAnswer:q.correctAnswer,explanation:q.explanation,type:q.type})}stopTimer();state.finished=true;state.strictActive=false;var total=state.questions.length;var pct=Math.round((state.correctCount/total)*100);var elapsed=Math.floor((Date.now()-state.startTime)/1000);saveStats(pct);if(state.mode==='strict')cleanupStrictMode();showResults(pct,elapsed,true)}
function renderQuestion(){var q=state.questions[state.currentIndex];var total=state.questions.length;state.answered=false;state.selectedOption=null;state.userInput='';dom.questionCounter.textContent='Question '+(state.currentIndex+1)+' of '+total;dom.questionTypeBadge.textContent=q.type==='multiple-choice'?'Multiple Choice':'Exact Word';dom.questionText.textContent=q.question;if(q.type==='multiple-choice')renderMC(q);else renderExact(q);dom.feedback.className='feedback';dom.feedback.style.display='none';dom.explanation.className='explanation';dom.explanation.style.display='none';dom.submitBtn.style.display='inline-block';dom.submitBtn.disabled=true;dom.explanationBtn.style.display='none';dom.nextBtn.style.display='none';dom.nextBtn.textContent='Next Question';dom.finishBtn.style.display='none';updateStats();updateProgressBar();if(q.type==='exact-word'){setTimeout(function(){var inp=dom.answerArea.querySelector('#exact-input');if(inp)inp.focus()},80)}}
function renderMC(q){var letters='ABCDEFGH';var html='<div class="options-list">';q.options.forEach(function(o,i){html+='<div class="option-item" data-value="'+esc(o)+'" tabindex="0"><input type="radio" name="answer" value="'+esc(o)+'"><span class="option-marker">'+letters[i]+'</span><span class="option-text">'+esc(o)+'</span></div>'});html+='</div>';dom.answerArea.innerHTML=html;dom.answerArea.querySelectorAll('.option-item').forEach(function(item){item.addEventListener('click',function(){if(state.answered)return;dom.answerArea.querySelectorAll('.option-item').forEach(function(o){o.classList.remove('selected')});item.classList.add('selected');state.selectedOption=item.getAttribute('data-value');dom.submitBtn.disabled=false})})}
function renderExact(q){dom.answerArea.innerHTML='<div class="exact-answer"><label for="exact-input">Type your answer below:</label><input type="text" class="exact-input" id="exact-input" placeholder="Enter your answer..." autocomplete="off" spellcheck="false"></div>';var inp=dom.answerArea.querySelector('#exact-input');inp.addEventListener('input',function(){state.userInput=inp.value;dom.submitBtn.disabled=inp.value.trim()===''});inp.addEventListener('keydown',function(e){if(e.key==='Enter'&&inp.value.trim()!==''&&!state.answered)submitAnswer()})}
function submitAnswer(){if(state.answered)return;var q=state.questions[state.currentIndex];var userAns,correct;if(q.type==='multiple-choice'){if(!state.selectedOption)return;userAns=state.selectedOption;correct=userAns===q.correctAnswer}else{userAns=state.userInput.trim();if(!userAns)return;correct=q.caseSensitive?userAns===q.correctAnswer:userAns.toLowerCase()===q.correctAnswer.toLowerCase()}state.answered=true;if(correct)state.correctCount++;state.answers.push({questionId:q.id,userAnswer:userAns,isCorrect:correct,question:q.question,correctAnswer:q.correctAnswer,explanation:q.explanation,type:q.type});if(state.mode==='practice')showFeedbackPractice(correct,q,userAns);else showFeedbackStrict(q);dom.submitBtn.style.display='none';if(state.mode==='practice'){dom.explanationBtn.style.display='inline-block';if(state.currentIndex<state.questions.length-1)dom.nextBtn.style.display='inline-block';else{dom.finishBtn.style.display='inline-block';dom.finishBtn.textContent='View Results'}}else{if(state.currentIndex<state.questions.length-1)dom.nextBtn.style.display='inline-block';else{dom.finishBtn.style.display='inline-block';dom.finishBtn.textContent='Submit Exam'}}updateStats();updateProgressBar()}
function showFeedbackPractice(correct,q,userAns){dom.feedback.style.display='block';dom.feedback.className='feedback show '+(correct?'correct':'wrong');if(correct)dom.feedback.textContent='Correct';else dom.feedback.innerHTML='Incorrect. The correct answer is: <strong>'+esc(q.correctAnswer)+'</strong>';if(q.type==='multiple-choice'){dom.answerArea.querySelectorAll('.option-item').forEach(function(item){item.classList.add('disabled');if(item.getAttribute('data-value')===q.correctAnswer)item.classList.add('correct');else if(item.getAttribute('data-value')===userAns&&!correct)item.classList.add('wrong')})}else{var inp=dom.answerArea.querySelector('.exact-input');if(inp){inp.disabled=true;inp.classList.add(correct?'correct':'wrong')}}}
function showFeedbackStrict(q){dom.feedback.style.display='block';dom.feedback.className='feedback show recorded';dom.feedback.textContent='Answer recorded';if(q.type==='multiple-choice')dom.answerArea.querySelectorAll('.option-item').forEach(function(item){item.classList.add('disabled')});else{var inp=dom.answerArea.querySelector('.exact-input');if(inp)inp.disabled=true}}
function showExplanation(){var q=state.questions[state.currentIndex];dom.explanation.style.display='block';dom.explanation.className='explanation show';dom.explanationText.textContent=q.explanation;dom.explanationBtn.style.display='none'}
function nextQuestion(){if(state.currentIndex<state.questions.length-1){state.currentIndex++;renderQuestion();window.scrollTo({top:0,behavior:'smooth'})}}
function finishExam(){var unanswered=state.questions.length-state.answers.length;if(unanswered>0){if(!confirm('You have '+unanswered+' unanswered question'+(unanswered>1?'s':'')+'. Submit anyway?'))return}stopTimer();state.finished=true;state.strictActive=false;var total=state.questions.length;var pct=Math.round((state.correctCount/total)*100);var elapsed=Math.floor((Date.now()-state.startTime)/1000);saveStats(pct);if(state.mode==='strict')cleanupStrictMode();showResults(pct,elapsed,false)}
function showResults(pct,elapsed,wasTimeExpired){showPage('results');dom.modeBadge.style.display='none';dom.examPage.classList.remove('strict-offset');var total=state.questions.length;var pass=examConfig.passingScore||70;var ok=pct>=pass;var h='';if(wasTimeExpired)h+='<div style="background:var(--danger-bg);border:1px solid var(--danger);color:var(--danger);padding:14px 20px;border-radius:var(--radius);margin-bottom:24px;font-family:var(--font-mono);font-size:.82rem;font-weight:500">Time expired. Unanswered questions were marked incorrect.</div>';h+='<div class="score-display"><div class="score-number">'+pct+'%</div><div class="score-label">'+state.correctCount+' of '+total+' correct</div></div><div class="pass-fail '+(ok?'pass':'fail')+'">'+(ok?'PASSED':'FAILED')+'</div><div class="results-stats"><div class="stat"><span class="stat-val">'+state.correctCount+'</span><span class="stat-lbl">Correct</span></div><div class="stat"><span class="stat-val">'+(total-state.correctCount)+'</span><span class="stat-lbl">Incorrect</span></div><div class="stat"><span class="stat-val">'+fmtTimeHMS(elapsed)+'</span><span class="stat-lbl">Time</span></div><div class="stat"><span class="stat-val">'+pass+'%</span><span class="stat-lbl">Passing</span></div>';if(state.mode==='strict')h+='<div class="stat"><span class="stat-val" style="color:var(--danger)">'+state.violations.length+'</span><span class="stat-lbl">Violations</span></div>';h+='</div><div class="review-section"><h3>Question Review</h3>';state.answers.forEach(function(a,i){h+='<div class="review-item"><div class="review-header" onclick="App.toggleReview('+i+')"><span class="review-q-num">Q'+(i+1)+'</span><span class="review-q-text">'+esc(a.question)+'</span><span class="review-status '+(a.isCorrect?'correct':'wrong')+'">'+(a.isCorrect?'Correct':'Wrong')+'</span></div><div class="review-detail" id="review-'+i+'"><p><strong>Your Answer:</strong> <span class="'+(a.isCorrect?'correct-answer':'user-answer')+'">'+esc(a.userAnswer)+'</span></p>';if(!a.isCorrect)h+='<p><strong>Correct Answer:</strong> <span class="correct-answer">'+esc(a.correctAnswer)+'</span></p>';h+='<p>'+esc(a.explanation)+'</p></div></div>'});h+='</div><div class="question-actions" style="justify-content:center;margin-top:36px"><button class="btn btn-primary" onclick="App.restart()">Take Again</button><button class="btn btn-secondary" onclick="App.goHome()">Back to Home</button></div>';dom.resultsContent.innerHTML=h}
function updateStats(){var total=state.questions.length;var answered=state.answers.length;dom.statScore.textContent=state.correctCount+' / '+answered;dom.statAccuracy.textContent=answered>0?Math.round((state.correctCount/answered)*100)+'%':'--';dom.statRemaining.textContent=total-answered;if(state.mode==='strict'){dom.statViolations.textContent=state.violations.length;dom.proctorViolations.textContent=state.violations.length}}
function renderProgressBar(){var total=state.questions.length;dom.progressSegments.innerHTML='';for(var i=0;i<total;i++){var s=document.createElement('div');s.className='progress-segment';s.id='seg-'+i;dom.progressSegments.appendChild(s)}dom.progressText.textContent='0%'}
function updateProgressBar(){var total=state.questions.length;state.answers.forEach(function(a,i){var seg=document.getElementById('seg-'+i);if(!seg)return;if(state.mode==='strict')seg.className='progress-segment answered-default';else seg.className='progress-segment '+(a.isCorrect?'correct':'wrong')});var cur=document.getElementById('seg-'+state.currentIndex);if(cur&&!state.answered)cur.className='progress-segment current';dom.progressText.textContent=Math.round((state.answers.length/total)*100)+'%'}
function statsKey(){return'exam_stats_'+((examConfig&&examConfig.title)||'default').replace(/\s+/g,'_')}
function getStats(){try{var d=localStorage.getItem(statsKey());return d?JSON.parse(d):null}catch(e){return null}}
function saveStats(pct){var s=getStats()||{attempts:0,bestScore:0,lastScore:0};s.attempts++;s.lastScore=pct;s.bestScore=Math.max(s.bestScore,pct);s.lastDate=new Date().toISOString();localStorage.setItem(statsKey(),JSON.stringify(s))}
function monitorAudio(){if(!state.analyserNode)return;if(!state.strictActive)return;if(state.mode!=='strict')return;var data=new Uint8Array(state.analyserNode.frequencyBinCount);var noiseStart=null;(function check(){if(!state.strictActive||state.mode!=='strict')return;state.analyserNode.getByteFrequencyData(data);var avg=0;for(var i=0;i<data.length;i++)avg+=data[i];avg=avg/data.length/255;if(avg>0.12){if(!noiseStart)noiseStart=Date.now();if(Date.now()-noiseStart>1500){if(!state.violationCooldown){logViolation('noise','Sustained sound detected above threshold');state.violationCooldown=true;setTimeout(function(){state.violationCooldown=false},5000)}noiseStart=Date.now()}}else{noiseStart=null}state.audioAnimFrame=requestAnimationFrame(check)})()}
function startFocusCheck(){if(state.focusCheckInterval)clearInterval(state.focusCheckInterval);state.focusCheckInterval=setInterval(function(){if(!state.strictActive||state.mode!=='strict'||state.finished)return;if(!document.hasFocus()&&!dom.fsRequiredOverlay.classList.contains('show')&&!dom.securityOverlay.classList.contains('show')){logViolation('focus','Periodic check: document lost focus (possible Alt+Tab or OS switch)');dom.securityMessage.textContent='Focus lost detected. Possible Alt+Tab or application switch. This violation has been logged.';dom.securityOverlay.classList.add('show')}},500)}
function stopFocusCheck(){if(state.focusCheckInterval){clearInterval(state.focusCheckInterval);state.focusCheckInterval=null}}
function initFocusMonitor(){document.addEventListener('visibilitychange',function(){if(document.hidden&&state.strictActive&&state.mode==='strict'&&!state.finished){logViolation('focus','Document hidden (visibility change)');dom.securityMessage.textContent='Tab or window lost focus. This violation has been logged.';dom.securityOverlay.classList.add('show')}});window.addEventListener('blur',function(){if(state.strictActive&&state.mode==='strict'&&!state.finished){logViolation('focus','Window lost focus (blur) - possible Alt+Tab or new tab/window');dom.securityMessage.textContent='Window lost focus. Alt+Tab and application switching are prohibited. This violation has been logged.';dom.securityOverlay.classList.add('show')}})}
function dismissWarning(){dom.securityOverlay.classList.remove('show');if(state.strictActive&&!state.finished&&isFullscreen()){addLog('Warning dismissed, exam continues')}}
function logViolation(type,detail){state.violations.push({type:type,detail:detail,time:new Date().toISOString()});addLog('VIOLATION ['+type.toUpperCase()+']: '+detail,true);updateStats()}
function addLog(text,isV){var t=new Date().toLocaleTimeString();var d=document.createElement('div');d.className='log-entry'+(isV?' violation':'');d.innerHTML='<span class="log-time">'+t+'</span>'+esc(text);dom.logEntries.prepend(d)}
function toggleLog(){state.logCollapsed=!state.logCollapsed;dom.logEntries.style.display=state.logCollapsed?'none':'block'}
function cleanupStrictMode(){state.strictActive=false;stopFocusCheck();if(state.cameraStream){state.cameraStream.getTracks().forEach(function(t){t.stop()});state.cameraStream=null}if(state.audioStream){state.audioStream.getTracks().forEach(function(t){t.stop()});state.audioStream=null}if(state.audioAnimFrame){cancelAnimationFrame(state.audioAnimFrame);state.audioAnimFrame=null}if(state.permAudioFrame){cancelAnimationFrame(state.permAudioFrame);state.permAudioFrame=null}if(state.audioContext){state.audioContext.close().catch(function(){});state.audioContext=null;state.analyserNode=null}dom.cameraContainer.style.display='none';dom.proctorBar.classList.remove('active');dom.securityLog.classList.remove('active');dom.timeExpiredOverlay.classList.remove('show');dom.fsRequiredOverlay.classList.remove('show');exitFullscreenIfNeeded()}
function showPage(p){dom.landingPage.classList.remove('active');dom.examPage.classList.remove('active');dom.resultsPage.classList.remove('active');if(p==='landing')dom.landingPage.classList.add('active');else if(p==='exam')dom.examPage.classList.add('active');else dom.resultsPage.classList.add('active')}
window.App={toggleReview:function(i){var el=document.getElementById('review-'+i);if(el)el.classList.toggle('show')},restart:function(){startExam()},goHome:function(){stopTimer();cleanupStrictMode();cleanupPermStreams();state.mode=null;state.finished=false;state.permissionsGranted=false;state.timeExpired=false;dom.modePractice.classList.remove('selected');dom.modeStrict.classList.remove('selected');dom.startBtn.disabled=true;dom.startBtn.textContent='Select a Mode to Begin';dom.modeBadge.style.display='none';dom.examPage.classList.remove('strict-offset');dom.logEntries.innerHTML='';dom.statTime.className='stat-value';loadPreviousStats();showPage('landing')}}
function shuffle(a){var b=a.slice();for(var i=b.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1));var tmp=b[i];b[i]=b[j];b[j]=tmp}return b}
function fmtTime(sec){var m=Math.floor(sec/60);var s=sec%60;return(m<10?'0':'')+m+': '+(s<10?'0':'')+s}
function fmtTimeHMS(sec){sec=Math.max(0,sec);var h=Math.floor(sec/3600);var m=Math.floor((sec%3600)/60);var s=sec%60;return(h<10?'0':'')+h+':'+(m<10?'0':'')+m+':'+(s<10?'0':'')+s}
function esc(str){var m={'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'};return String(str).replace(/[&<>"']/g,function(c){return m[c]})}
document.addEventListener('DOMContentLoaded',init);
})();
</script>
</body>
</html>"""

# ──────────────────────────────────────────────────────────
#  MIME types
# ──────────────────────────────────────────────────────────
MIME_TYPES = {
    '.html': 'text/html; charset=utf-8',
    '.css':  'text/css; charset=utf-8',
    '.js':   'application/javascript; charset=utf-8',
    '.json': 'application/json; charset=utf-8',
    '.png':  'image/png',
    '.jpg':  'image/jpeg',
    '.svg':  'image/svg+xml',
    '.ico':  'image/x-icon',
}

# ──────────────────────────────────────────────────────────
#  HTTP Request Handler
# ──────────────────────────────────────────────────────────
class ExamHandler(http.server.BaseHTTPRequestHandler):
    """Serves the embedded HTML for / and serves exam_data.js
       (and any other static files) from the script's directory."""

    # Suppress default stderr logging — we print our own banner
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        path = self.path.split('?')[0]   # strip query string

        # ── Root → serve embedded HTML ────────────────────
        if path in ('/', '/index.html'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(HTML_CONTENT.encode('utf-8'))))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
            return

        # ── favicon (prevent 404 noise) ──────────────────
        if path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return

        # ── Static files from the script directory ───────
        safe_path = os.path.normpath(path.lstrip('/'))
        file_path = os.path.join(DIRECTORY, safe_path)

        # Security: prevent directory traversal
        if not os.path.abspath(file_path).startswith(os.path.abspath(DIRECTORY)):
            self.send_error(403, 'Forbidden')
            return

        if os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1].lower()
            content_type = MIME_TYPES.get(ext, 'application/octet-stream')
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except Exception:
                self.send_error(500, 'Internal Server Error')
        else:
            self.send_error(404, 'Not Found')


# ──────────────────────────────────────────────────────────
#  Utility: find a free port
# ──────────────────────────────────────────────────────────
def find_port(start, attempts):
    for offset in range(attempts):
        port = start + offset
        try:
            with socketserver.TCPServer(('', port), None) as test:
                return port
        except OSError:
            continue
    return None


# ──────────────────────────────────────────────────────────
#  Banner
# ──────────────────────────────────────────────────────────
BANNER = r"""
  ╔══════════════════════════════════════════════════════════╗
  ║                                                          ║
  ║   ┌──────────────────────────────────────────────────┐   ║
  ║   │                EXAM PRACTICE TOOL                │   ║
  ║   └──────────────────────────────────────────────────┘   ║
  ║                                                          ║
  ║                      Server Started                      ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║    Author     : axtr64                                   ║
  ║    Disclaimer : For exam preparation only.               ║
  ║                 Clean, local, no background installs.    ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║    URL        : http://localhost:{port}                    ║
  ║    Directory  : {dir}        ║
  ║    exam_data  : {data_status}                                    ║
  ║                                                          ║
  ╠══════════════════════════════════════════════════════════╣
  ║                                                          ║
  ║    Press Ctrl+C to stop the server.                      ║
  ║                                                          ║
  ╚══════════════════════════════════════════════════════════╝
"""



# ──────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────
def main():
    global DIRECTORY
    DIRECTORY = os.path.dirname(os.path.abspath(__file__))

    # Check exam_data.js exists
    data_file = os.path.join(DIRECTORY, 'exam_data.js')
    if os.path.isfile(data_file):
        data_status = 'Found'
    else:
        data_status = 'NOT FOUND \u2014 place exam_data.js in: ' + DIRECTORY

    # Find an available port
    port = find_port(DEFAULT_PORT, MAX_PORT_ATTEMPTS)
    if port is None:
        print(f'[ERROR] Could not find an open port '
              f'(tried {DEFAULT_PORT}\u2013{DEFAULT_PORT + MAX_PORT_ATTEMPTS - 1}).')
        sys.exit(1)

    # Create server (allow address reuse to avoid "Address already in use")
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(('', port), ExamHandler)

    # Graceful shutdown on Ctrl+C / SIGTERM
    def shutdown_handler(*_):
        print('\n[INFO] Shutting down server...')
        threading.Thread(target=server.shutdown).start()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Print banner
    print(BANNER.format(port=str(port), dir=DIRECTORY, data_status=data_status))

    # Open browser after a short delay
    def open_browser():
        time.sleep(0.6)
        webbrowser.open(f'http://localhost:{port}')

    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Serve forever
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        print('[INFO] Server stopped.')


if __name__ == '__main__':
    main()
