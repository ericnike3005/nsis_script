# --- builder.py ---
import os
import sys
import subprocess
from datetime import datetime

import config


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


# 삭제 버튼 기능
def delete_exes(log_message):
    base_dir = get_base_dir()

    files = os.listdir(base_dir)
    deleted_count = 0

    for file in files:
        # 파일 이름이 'DRM_'로 시작하고 '_Patch_'를 포함하며 '.exe'로 끝나는 것만 적용
        if file.startswith("DRM_") and "_Patch_" in file and file.endswith(".exe"):
            full_path = os.path.join(base_dir, file)
            try:
                os.remove(full_path)
                deleted_count += 1
            except Exception as e:
                # 혹시 지우다가 에러가 나면 로그에 남깁니다.
                log_message(f"  → [삭제 실패] {file}: {e}")

    # 최종 결과를 로그 창에 띄워줍니다.
    if deleted_count > 0:
        log_message("-" * 40)
        log_message(f"  → [완료] 총 {deleted_count}개의 생성된 exe 파일을 삭제했습니다.")
        log_message("-" * 40)
    else:
        log_message("  → [알림] 삭제할 생성된 exe 파일이 없습니다.")


# ---------------- 커스텀 다중 대상 빌드 (SetOutPath 직접 입력) ---------------- #
def Custom_Multi_Build(targets, Show_Mode, log_message, is_reboot):
 
    install_mode = Show_Mode.get()
    base_dir = get_base_dir()

    if not targets:
        log_message("  → [오류] 추가된 패치 대상이 없습니다.")
        return

    name_part = targets[0]["label"] if len(targets) == 1 else "MultiTarget"

    section_blocks = ""
    service_restart_blocks = ""
    restarted_servcies = set()
    all_files_display = []

    for t in targets:
        for fe in t["files"]:
            f = fe["path"]
            out_path = fe["out_path"]
            fname = os.path.basename(f)
            all_files_display.append(f"[{t['label']}] {fname}")

            section_blocks += f'\n        SetOutPath "{out_path}"\n'
            section_blocks += (
                f'\n      DetailPrint "[{t["label"]}] {fname} 백업 및 교체 중..."\n'
                f'        Delete "{out_path}\\{fname}_old"\n'
                f'        Rename "{out_path}\\{fname}" "{out_path}\\{fname}_old"\n'
                f'        Delete /REBOOTOK "{out_path}\\{fname}_old"\n'
                f'        File "{f}"\n'
            )

            if fname.lower() in config.TARGET_PROCESSES:
                exe_full_path = f"{out_path}\\{fname}"
                section_blocks += (
                    f'\n        nsExec::Exec \'"{exe_full_path}" -stop\'\n'
                    f'        nsExec::Exec \'"{exe_full_path}" -remove\'\n'

                )
                if exe_full_path not in restarted_servcies:
                    restarted_servcies.add(exe_full_path)
                    service_restart_blocks += (
                        f'\n      DetailPrint "[{t["label"]}] {fname} [서비스 재기동] {fname}"\n'
                        f'        nsExec::Exec \'"{exe_full_path}" -install\'\n'
                        f'        Sleep 3000\n'
                        f'        nsExec::Exec \'"{exe_full_path}" -start\'\n'
                    )

                elif fname.lower() in config.REG_TARGET_DLLS:
                    dll_full_path = f"{out_path}\\{fname}"
                    section_blocks += (
                        f'\n      DetailPrint "[{t["label"]}] {fname} 레지스트리 재등록 중..."\n'
                        f'        nsExec::Exec \'taskkill /f /im explorer.exe\'\n'
                        f'        UnRegDLL "{dll_full_path}"\n'
                        f'        Sleep 2000\n'
                        f'        RegDLL "{dll_full_path}"\n'
                        f'        Exec "explorer.exe"\n'
                    )

    silent_directive = "SilentInstall silent" if install_mode == "silent" else ""
    msg_box = "" if install_mode == "silent" else f'MessageBox MB_OK "{name_part} 패치가 완료되었습니다!"'
    current_time = datetime.now().strftime("%y%m%d_%H%M%S")
    final_exe_name = f"DRM_Patch({install_mode})_{current_time}.{config.file_extension}"

    if is_reboot:
        reboot_command = """
        MessageBox MB_YESNO|MB_ICONQUESTION "패치가 완료되었습니다. 지금 바로 재부팅하시겠습니까?$\\n$\\n재부팅을 하지 않는 경우 오류가 발생할 수 있습니다." IDNO +2
        Reboot
        """
    else:
        reboot_command = ""

    nsi_content = f"""
    !define APPNAME "{name_part}_Patch"

    Name "MarkAny DRM Patch"
    Icon "{config.NSIS_ICON}"

    OutFile "{base_dir}\\{final_exe_name}"

    {silent_directive}
    ShowInstDetails show
    AutoCloseWindow true

    Section "PatchSection" SEC01
        {section_blocks}

        {service_restart_blocks}

        {msg_box}
        {reboot_command}
    SectionEnd
    """

    temp_nsi_path = os.path.join(base_dir, "temp_build.nsi")

    try:
        with open(temp_nsi_path, "w", encoding=config.NSI_ENCODING) as f:
            f.write(nsi_content)

        result = subprocess.run([config.MAKENSIS_PATH, temp_nsi_path], capture_output=True, text=True)

        if result.returncode == 0:
            file_list = ", ".join(all_files_display)
            log_message(f"  → [성공] {final_exe_name} 생성 완료!")
            log_message(f"  → [포함된 파일] {file_list}", "blue_text")
        else:
            log_message(f"  → [오류] 컴파일 실패:\n{result.stderr}")

    except FileNotFoundError:
        log_message("  → [실행 오류] makensis.exe를 찾을 수 없습니다. (NSIS 설치 확인)")
    except Exception as e:
        log_message(f"  → [알 수 없는 오류] {e}")

    finally:
        if os.path.exists(temp_nsi_path):
            os.remove(temp_nsi_path)
        log_message("-" * 40)
