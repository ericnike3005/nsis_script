# --- patch_state.py ---
# 패치 대상 목록을 관리하는 순수 로직입니다. tkinter 등 UI에 전혀 의존하지 않습니다.
import os
import csv

_targets = []   # [{"label": 폴더명, "files": [{"path":..., "out_path":..., "source":...}, ...]}, ...]
_path_map = {}  # {파일명(소문자): out_path}


def load_path_map(csv_path, encoding="utf-8-sig"):
    global _path_map
    if not os.path.exists(csv_path):
        _path_map = {}
        return False, f"CSV 파일을 찾을 수 없습니다: {csv_path}"

    tried_encodings = [encoding, "cp949", "utf-8"]
    mapping = {}
    last_error = None

    for enc in tried_encodings:
        try:
            mapping = {}
            with open(csv_path, newline="", encoding=enc) as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < 2:
                        continue
                    out_path = row[0].strip()   # 1열: 경로
                    file_name = row[1].strip()  # 2열: 파일명
                    if not out_path or not file_name:
                        continue
                    mapping[file_name.lower()] = out_path
            last_error = None
            break
        except UnicodeDecodeError as e:
            last_error = e
            continue
        except Exception as e:
            return False, f"CSV 읽기 오류: {e}"

    if last_error is not None:
        return False, f"CSV 읽기 오류: 인코딩을 확인해 주세요 — {last_error}"

    _path_map = mapping
    return True, len(_path_map)


def get_path_for_file(filename):
    return _path_map.get(filename.lower())


def add_target(out_path, selected_files):
    if not selected_files:
        return False, "선택된 파일이 없습니다."

    files = [os.path.normpath(f) for f in selected_files]

    # 모듈명(label)은 사용자가 입력하지 않고, 선택된 파일들의 공통 상위 폴더 이름을 자동 인식합니다.
    if len(files) == 1:
        common_dir = os.path.dirname(files[0])
    else:
        try:
            common_dir = os.path.commonpath(files)
        except ValueError:
            common_dir = os.path.dirname(files[0])
    label = os.path.basename(os.path.normpath(common_dir)) or common_dir

    manual_out_path = (out_path or "").strip()

    file_entries = []
    missing = []
    for f in files:
        fname = os.path.basename(f)
        mapped = get_path_for_file(fname)
        if mapped:
            file_entries.append({"path": f, "out_path": mapped, "source": "CSV"})
        elif manual_out_path:
            file_entries.append({"path": f, "out_path": manual_out_path, "source": "수동입력"})
        else:
            missing.append(fname)

    if missing:
        return False, f"다음 파일은 CSV에 경로가 없습니다: {', '.join(missing)} (직접 입력하거나 module_paths.csv에 추가해 주세요.)"

    target = {"label": label, "files": file_entries}
    _targets.append(target)
    return True, target


def clear_targets():
    _targets.clear()


def get_targets():
    return _targets