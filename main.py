# --- main.py ---
# 디자인 config.py 
# 패치 대상 관리 patch_state.py
# NSIS 빌드는 builder.py

import tkinter as tk
from tkinter import filedialog

import config
import patch_state
import builder
import os
import traceback

csv_path = os.path.join(builder.get_base_dir(), config.MODULE_PATH_CSV)
loaded_ok, loaded_result = patch_state.load_path_map(csv_path, config.CSV_ENCODING)

# 로그 띄워주는 함수 (화면 UI)
def log_message(message, tag=None):
    text_log.config(state=tk.NORMAL)
    if tag:
        text_log.insert(tk.END, message + "\n", tag)
    else:
        text_log.insert(tk.END, message + "\n")
    text_log.see(tk.END)
    text_log.config(state=tk.DISABLED)

# ---------------- file_target ---------------- #
def browse_and_add_target():
    out_path = setoutpath_var.get().strip()

    selected_dir = filedialog.askdirectory(title="폴더를 선택하세요")
    if not selected_dir:
        return

    selected = []
    for root, dirs, files in os.walk(selected_dir):
        for fname in files:
            selected.append(os.path.join(root, fname))
            
    if not selected:
        log_message(f"  → [알림] 선택한 폴더에 파일이 없습니다: {selected_dir}")
        return

    ok, result = patch_state.add_target(out_path, selected)
    if not ok:
        log_message(f"  → [알림] {result}")
        return

    render_patch_targets()
    log_message(f"  → [추가됨] '{result['label']}' ({len(result['files'])}개 파일)")
    #for fe in result["files"]:
    #    log_message(f"      - {os.path.basename(fe['path'])} → {fe['out_path']} ({fe['source']})")
    setoutpath_var.set("")

def clear_patch_targets():
    patch_state.clear_targets()
    render_patch_targets()
    log_message("  → [초기화] 패치 대상 목록을 모두 비웠습니다.")

def render_patch_targets():
    targets = patch_state.get_targets()
    info_text_left.config(state=tk.NORMAL)
    info_text_left.delete("1.0", tk.END)

    if not targets:
        info_text_left.insert(tk.END, " 아직 추가된 패치 대상이 없습니다.\n", "missing")
    else:
        for idx, t in enumerate(targets, start=1):
            info_text_left.insert(tk.END, f" [{idx}] 선택폴더명: {t['label']}\n", "missing")
            for fe in t["files"]:
                fname = os.path.basename(fe["path"])
                info_text_left.insert(tk.END, f"     {fname} → {fe['out_path']} ({fe['source']})\n", "ready")
            info_text_left.insert(tk.END, "\n")

    info_text_left.config(state=tk.DISABLED)
    info_label_title.config(text=f"▶ 패치 대상: {len(targets)}개 그룹")

def execute_build():
    install_mode = Show_Mode.get()
    is_reboot = Reboot_Check.get()

    targets = patch_state.get_targets()
    if not targets:
        log_message("  → [알림] 먼저 파일 선택으로 패치할 대상을 추가해 주세요.")
        return

    try:
        builder.Custom_Multi_Build(targets, Show_Mode, log_message, is_reboot)
    except Exception:
        log_message("  → [내부 오류] 예상치 못한 오류가 발생했습니다:")
        for line in traceback.format_exc().splitlines():
            log_message(f"      {line}")


# ---------------- UI 구성 부분 ---------------- #
app = tk.Tk()
app.title(f"DRM Patch Autogenerator_{config.APP_VERSION}")

try:
    icon_path = os.path.join(builder.get_base_dir(), "icon.ico")
    app.iconbitmap(icon_path)
except Exception:
    pass

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

app_w = config.WINDOW_WIDTH
app_h = config.WINDOW_HEIGHT

pos_x = screen_width - app_w - config.WINDOW_MARGIN_RIGHT
pos_y = config.WINDOW_MARGIN_TOP

app.geometry(f"{app_w}x{app_h}+{pos_x}+{pos_y}")

main_canvas = tk.Canvas(app, highlightthickness=0)
main_scrollbar = tk.Scrollbar(app, orient="vertical", command=main_canvas.yview)
scroll_frame = tk.Frame(main_canvas)

scroll_frame.bind(
    "<Configure>",
    lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
)
main_canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=app_w)
main_canvas.configure(yscrollcommand=main_scrollbar.set)

main_canvas.pack(side="left", fill="both", expand=True)
main_scrollbar.pack(side="right", fill="y")

def _on_mousewheel(event):
    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

frame_notice = tk.LabelFrame(scroll_frame, text="공지사항 및 사용 방법", padx=10, pady=5)
frame_notice.pack(pady=(15, 5), fill="x", padx=20)
tk.Label(frame_notice, text=config.NOTICE_TEXT, justify="left", fg=config.COLOR_NOTICE_TEXT,
         wraplength=config.NOTICE_WRAPLENGTH).pack(anchor="w", padx=5, pady=5)

Show_Mode = tk.StringVar(value="silent")
Reboot_Check = tk.BooleanVar(value=False)  # 체크박스 (기본값 : 체크 안함)

frame_mode = tk.LabelFrame(scroll_frame, text="설치 모드 선택", padx=10, pady=5)
frame_mode.pack(pady=5, fill="x", padx=20)

tk.Radiobutton(frame_mode, text="Silent (백그라운드)", variable=Show_Mode, value="silent").pack(side="left", padx=10)
tk.Radiobutton(frame_mode, text="Show (설치 화면)", variable=Show_Mode, value="show").pack(side="left", padx=10)
tk.Checkbutton(frame_mode, text="재부팅 여부", variable=Reboot_Check, fg=config.COLOR_REBOOT_CHECK).pack(side="right", padx=10)

# ==================== 패치 대상 설정 (직접 입력) ==================== #
#setoutpath_var = tk.StringVar(value=config.DEFAULT_SETOUTPATH)
setoutpath_var = tk.StringVar(value="")

frame_custom = tk.LabelFrame(scroll_frame, text="패치 대상 설정 (직접 입력 가능)", padx=10, pady=10)
frame_custom.pack(pady=5, fill="x", padx=20)

row_outpath = tk.Frame(frame_custom)
row_outpath.pack(fill="x", pady=2)
tk.Label(row_outpath, text="설치 경로", width=10, anchor="w").pack(side="left")
tk.Entry(row_outpath, textvariable=setoutpath_var).pack(side="left", fill="x", expand=True)
tk.Label(frame_custom, text=config.SETOUTPATH_HINT, fg=config.COLOR_HINT_TEXT, anchor="w", font=("", 8)).pack(anchor="w", padx=(85, 0))

row_action = tk.Frame(frame_custom)
row_action.pack(fill="x", pady=(10, 0))
tk.Button(row_action, text="① 폴더 선택", command=browse_and_add_target,
          bg=config.COLOR_SELECT_BTN, font=("", 9, "bold")).pack(side="left", fill="x", expand=True, ipady=3)
tk.Button(row_action, text="목록 초기화", command=clear_patch_targets ).pack(side="left", padx=(5, 0), ipady=3)

# ==================== 패치 대상 확인 및 실행 구역 ==================== #
frame_info = tk.LabelFrame(scroll_frame, text="패치 대상 확인", padx=10, pady=5)
frame_info.pack(pady=5, fill="both", expand=False, padx=20)

info_label_title = tk.Label(frame_info, text="▶ 패치 대상: 0개 그룹", justify="left", fg="black", font=("", 9, "bold"))
info_label_title.pack(anchor="w", pady=(5, 0))

info_text_left = tk.Text(frame_info, height=20, bg=app.cget("bg"), bd=0, highlightthickness=0, font=("", 9))
info_text_left.pack(anchor="w", fill="x", pady=(0, 5))
info_text_left.tag_config("ready", foreground=config.COLOR_FILE_PATH)
info_text_left.tag_config("missing", foreground=config.COLOR_LABEL_TEXT)
info_text_left.config(state=tk.DISABLED)

# 최종 빌드 실행 버튼
frame_action_btns = tk.Frame(frame_info)
frame_action_btns.pack(fill="x", pady=5)

frame_action_btns.columnconfigure(0, weight=5)
frame_action_btns.columnconfigure(1, weight=1)

btn_build = tk.Button(frame_action_btns, text=" ② 패치 파일 생성", bg=config.COLOR_SELECT_BTN, font=("", 10, "bold"), height=1, command=execute_build)
btn_build.grid(row=0, column=0, sticky="ew", padx=(0, 5), ipady=3)

btn_delete = tk.Button(frame_action_btns, text="🗑️패치 파일 삭제", font=("", 10, "bold"), height=1, command=lambda: builder.delete_exes(log_message))
btn_delete.grid(row=0, column=1, sticky="ew", ipady=3)

# 초기 렌더링 (빈 상태 표시)
render_patch_targets()

# ========================================================================= #

frame_log = tk.LabelFrame(scroll_frame, text="실행 로그", padx=5, pady=5)
frame_log.pack(fill="both", expand=True, padx=20, pady=5)

scrollbar = tk.Scrollbar(frame_log)
scrollbar.pack(side="right", fill="y")

text_log = tk.Text(frame_log, height=8, yscrollcommand=scrollbar.set, state=tk.DISABLED, bg=config.COLOR_LOG_BG)
text_log.pack(side="left", fill="both", expand=True)
scrollbar.config(command=text_log.yview)

text_log.tag_config("blue_text", foreground="blue")

tk.Label(scroll_frame).pack(side="bottom", anchor="e", padx=10, pady=2)

if loaded_ok:
    log_message(f"  → [CSV] module_paths.csv 로드 완료 ({loaded_result}개 모듈 경로 등록됨)")
else:
    log_message(f"  → [CSV 알림] {loaded_result}")

app.mainloop()
