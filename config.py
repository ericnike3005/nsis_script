# --- config.py ---
# 이 파일은 "값"만 담습니다. 동작(로직)은 patch_state.py / builder.py / main.py 에 있습니다.

# ==========================================
# [설정] 빌드 버전 관리
APP_VERSION = "v26.09.14.01"
# ==========================================

file_extension = "exe"
DEFAULT_SETOUTPATH = r"C:\markany\Document Safer"

MODULE_PATH_CSV = "module_paths.csv"  # exe/py와 같은 폴더에 위치
CSV_ENCODING = "utf-8-sig"

#LAST_DIR_FILE = "last_dir.txt"
# ---------------- NSIS ----------------
MAKENSIS_PATH = r"C:\Program Files (x86)\NSIS\makensis.exe"
NSIS_ICON = r"${NSISDIR}\Contrib\Graphics\Icons\modern-install-colorful.ico"
NSI_ENCODING = "ansi"  # NSIS 스크립트 파일 저장 인코딩 (Windows 시스템 기본 코드페이지)

# 서비스 재기동 목록
TARGET_PROCESSES = {"DSH_Service64.exe", "IMGSF50svc.exe", "mawssvc.exe", "PolicyServerService.exe"}
_process_list_str = ", ".join(sorted(TARGET_PROCESSES))

REG_TARGET_DLLS = {"AcapIconMgr.dll","AcapIconMgr64.dll","MAShlMgr.dll","MAShlMgr64.dll"}
_dll_list_str = ", ".join(sorted(REG_TARGET_DLLS))

# ---------------- 창 크기 / 위치 ----------------
WINDOW_WIDTH = 540
WINDOW_MARGIN_RIGHT = 80    
WINDOW_MARGIN_TOP = 50      
WINDOW_HEIGHT = 850
NOTICE_WRAPLENGTH = 450     # 공지 문구 자동 줄바꿈 폭(px). WINDOW_WIDTH보다 넉넉히

# ---------------- 색상 ----------------
COLOR_ADD_BTN = "#d1e7dd"
COLOR_CLEAR_BTN = "#f8d7da"
COLOR_BUILD_BTN = "#e1f5fe"
COLOR_SELECT_BTN = "#ff9e9e"
COLOR_FILE_PATH = "#0052cc"     # 패치 대상 확인 - 파일 경로 라인
COLOR_LABEL_TEXT = "black"      # 패치 대상 확인 - 모듈명/설치경로 라인
COLOR_NOTICE_TEXT = "#2C3E50"
COLOR_REBOOT_CHECK = "#d32f2f"
COLOR_HINT_TEXT = "gray"
COLOR_LOG_BG = "#f4f4f4"

# ---------------- 안내 문구 ----------------
NOTICE_TEXT = f"""1. [① 폴더 선택] 후, 모듈 선택 (module_paths.csv 기반 자동 인식)
2. "패치 대상 확인" 후 "② 패치 파일 생성" 클릭.
3. 서비스 재설치 목록 : {_process_list_str}
4. DLL 등록 목록 : {_dll_list_str}"""

SETOUTPATH_HINT = r"ex) C:\markany\Document Safer, $WINDIR\System32"
