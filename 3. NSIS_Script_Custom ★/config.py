# --- config.py ---
# 이 파일은 "값"만 담습니다. 동작(로직)은 patch_state.py / builder.py / main.py 에 있습니다.

# ==========================================
# [설정] 빌드 버전 관리 (여기서만 수정하세요!)
APP_VERSION = "v26.09.02.02"
# ==========================================

# 생성되는 패치 파일 확장자
file_extension = "exe"
DEFAULT_SETOUTPATH = r"C:\markany\Document Safer"


# ---------------- NSIS ----------------
MAKENSIS_PATH = r"C:\Program Files (x86)\NSIS\makensis.exe"
NSIS_ICON = r"${NSISDIR}\Contrib\Graphics\Icons\modern-install-colorful.ico"
NSI_ENCODING = "ansi"  # NSIS 스크립트 파일 저장 인코딩 (Windows 시스템 기본 코드페이지)

# 서비스 재기동 목록
TARGET_PROCESSES = {"dsh_service64.exe", "imgsf50svc.exe", "mawssvc.exe"}
_process_list_str = ", ".join(sorted(TARGET_PROCESSES))

# ---------------- 창 크기 / 위치 ----------------
WINDOW_WIDTH = 540
WINDOW_MARGIN_RIGHT = 80    # 화면 오른쪽 끝에서 띄우는 여백
WINDOW_MARGIN_TOP = 50      # 화면 위쪽에서 띄우는 여백
WINDOW_HEIGHT_MARGIN = 150  # 화면 높이에서 이 값만큼 뺀 높이로 창을 만듭니다
NOTICE_WRAPLENGTH = 500     # 공지 문구 자동 줄바꿈 폭(px). WINDOW_WIDTH보다 넉넉히 작게 잡습니다.

# ---------------- 색상 ----------------
COLOR_ADD_BTN = "#d1e7dd"
COLOR_CLEAR_BTN = "#f8d7da"
COLOR_BUILD_BTN = "#e1f5fe"
COLOR_DELETE_BTN = "#ff9e9e"
COLOR_FILE_PATH = "#0052cc"     # 패치 대상 확인 - 파일 경로 라인
COLOR_LABEL_TEXT = "black"      # 패치 대상 확인 - 모듈명/설치경로 라인
COLOR_NOTICE_TEXT = "#2C3E50"
COLOR_REBOOT_CHECK = "#d32f2f"
COLOR_HINT_TEXT = "gray"
COLOR_LOG_BG = "#f4f4f4"

# ---------------- 안내 문구 ----------------
NOTICE_TEXT = f"""1. 설치 경로(SetOutPath)를 입력하세요.
2. [파일 선택] 시, 모듈명으로 자동 인식되어 패치 대상에 추가됩니다.
3. 여러 모듈을 추가한 뒤, [패치 파일 생성] 버튼을 눌러 완성하세요.
4. Service Auto Install List : {_process_list_str}"""

SETOUTPATH_HINT = "ex) C:\markany\Document Safer, $WINDIR\System32"
