import flet as ft
import json
import os
import base64
import shutil
import sys

def main(page: ft.Page):
    # exe 빌드 시에도 작동하는 경로 계산 (최대한 단순하게)
    if getattr(sys, 'frozen', False):
        # PyInstaller로 빌드된 경우: exe 파일이 있는 디렉토리
        base_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 일반 실행 시: 스크립트 파일이 있는 디렉토리
        base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # data 폴더는 항상 exe/스크립트와 같은 위치에 생성 (절대 경로 사용)
    data_dir = os.path.abspath(os.path.join(base_dir, "data"))
    
    # img 폴더 찾기 (같은 위치 먼저, 없으면 상위 디렉토리)
    img_dir = os.path.abspath(os.path.join(base_dir, "img"))
    if not os.path.exists(img_dir):
        img_dir = os.path.abspath(os.path.join(os.path.dirname(base_dir), "img"))
    
    # 페이지 설정
    page.title = "Dashboard"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window.width = 500
    
    # assets 디렉토리 설정 (이미지 로드용)
    page.assets_dir = img_dir
    
    # data 디렉토리 생성 (없으면)
    os.makedirs(data_dir, exist_ok=True)
    
    # JSON 파일 경로 (절대 경로로 변환)
    공지사항_path = os.path.abspath(os.path.join(data_dir, "공지사항.json"))
    알림창_path = os.path.abspath(os.path.join(data_dir, "알림창.json"))
    프로필_path = os.path.abspath(os.path.join(data_dir, "프로필.json"))
    미니맵_path = os.path.abspath(os.path.join(data_dir, "미니맵.json"))
    메뉴_path = os.path.abspath(os.path.join(data_dir, "메뉴.json"))
    프리셋_path = os.path.abspath(os.path.join(data_dir, "프리셋.json"))
    url_path = os.path.abspath(os.path.join(data_dir, "url.json"))
    
    # 초기 JSON 파일 생성 함수
    def init_json_file(file_path, default_data):
        """JSON 파일이 없으면 기본값으로 생성"""
        if not os.path.exists(file_path):
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=2)
    
    # 필요한 JSON 파일들 초기화
    init_json_file(공지사항_path, {"내용": ""})
    init_json_file(알림창_path, {"내용": ""})
    init_json_file(프로필_path, {})
    init_json_file(미니맵_path, {})
    init_json_file(메뉴_path, [])
    init_json_file(프리셋_path, {"current": ""})
    init_json_file(url_path, {"채팅창url": ""})
    
    # JSON 파일 읽기 함수
    def load_json(file_path):
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"내용": ""}
        return {"내용": ""}
    
    # JSON 파일 저장 함수
    def save_json(file_path, content):
        file_path = os.path.abspath(file_path)  # 절대 경로로 변환
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        data = {"내용": content}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 공지사항 저장 핸들러
    def on_공지사항_change(e):
        save_json(공지사항_path, e.control.value)
    
    # 알림창 저장 핸들러
    def on_알림창_change(e):
        save_json(알림창_path, e.control.value)
    
    # 기존 데이터 로드
    공지사항_data = load_json(공지사항_path)
    알림창_data = load_json(알림창_path)
    
    # 파일 선택기 (전역)
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    minimap_file_picker = ft.FilePicker()
    page.overlay.append(minimap_file_picker)
    
    # 메뉴 아이콘용 파일 선택기 (전역)
    menu_icon_file_picker = ft.FilePicker()
    page.overlay.append(menu_icon_file_picker)
    
    # 현재 선택된 탭 인덱스
    selected_index = 0
    
    # 현재 화면 상태 ("home", "settings", "add_minimap")
    current_screen = "home"
    
    # 스크롤 위치 저장용
    settings_scroll_position = 0.0
    
    # 항상 최상단 설정 (변수에 저장)
    항상_최상단 = False
    
    # 메인 콘텐츠 컨테이너 (동적으로 변경됨)
    main_content_container = ft.Container(expand=True)
    
    # 홈 페이지 콘텐츠
    def get_home_content():
        # 프로필 데이터 로드
        profile_data = load_profile()
        has_profile_data = bool(profile_data and len(profile_data) > 0)
        
        # 피로도 슬라이더 관련 변수 초기화
        피로도_섹션 = None
        
        if has_profile_data:
            # 첫 번째 프로필 데이터 사용
            first_profile_key = list(profile_data.keys())[0]
            profile = profile_data.get(first_profile_key, {})
            
            # 최대 피로도 숫자 입력
            최대_피로도_값 = profile.get("최대_피로도", "100")
            try:
                최대_피로도_숫자 = int(최대_피로도_값) if 최대_피로도_값 else 100
            except:
                최대_피로도_숫자 = 100
            
            # 피로도 슬라이더
            피로도_값 = profile.get("피로도", "0")
            try:
                피로도_숫자 = int(피로도_값) if 피로도_값 else 0
            except:
                피로도_숫자 = 0
            
            빠른_피로도_표시 = ft.Text(
                value=f"피로도: {피로도_숫자}/{최대_피로도_숫자}",
                size=14,
            )
            
            빠른_피로도_slider = ft.Slider(
                min=0,
                max=max(최대_피로도_숫자, 1),
                value=min(피로도_숫자, 최대_피로도_숫자),
                divisions=min(최대_피로도_숫자, 100),
                label="{value}",
            )
            
            # 자동 저장 함수
            def auto_save_quick_settings():
                # 프로필 데이터 다시 로드
                profile_data_new = load_profile()
                if not profile_data_new or len(profile_data_new) == 0:
                    return
                
                first_profile_key_new = list(profile_data_new.keys())[0]
                profile_new = profile_data_new.get(first_profile_key_new, {})
                
                # 최대 피로도는 프로필에서 가져오기
                최대_피로도_값_new = profile_new.get("최대_피로도", "100")
                try:
                    최대_피로도_숫자_new = int(최대_피로도_값_new) if 최대_피로도_값_new else 100
                except:
                    최대_피로도_숫자_new = 100
                
                # 프로필 데이터 업데이트
                profile_data_new[first_profile_key_new]["피로도"] = str(int(빠른_피로도_slider.value))
                
                # 저장
                save_profile(profile_data_new)
            
            # 피로도 슬라이더 변경 핸들러
            def on_빠른_피로도_change(e):
                # 프로필 데이터 다시 로드
                profile_data_new = load_profile()
                if not profile_data_new or len(profile_data_new) == 0:
                    return
                
                first_profile_key_new = list(profile_data_new.keys())[0]
                profile_new = profile_data_new.get(first_profile_key_new, {})
                
                최대_피로도_값_new = profile_new.get("최대_피로도", "100")
                try:
                    최대값 = int(최대_피로도_값_new) if 최대_피로도_값_new else 100
                except:
                    최대값 = 100
                
                빠른_피로도_표시.value = f"피로도: {int(e.control.value)}/{최대값}"
                빠른_피로도_표시.update()
                auto_save_quick_settings()
            
            빠른_피로도_slider.on_change = on_빠른_피로도_change
            
            피로도_섹션 = ft.Column(
                [
                    빠른_피로도_표시,
                    빠른_피로도_slider,
                ],
                spacing=10,
            )
        
        # 프리셋 데이터 로드
        preset_data = load_preset()
        current_preset = preset_data.get("current", "")
        preset_keys = [k for k in preset_data.keys() if k != "current"]
        
        # 프리셋 라디오 버튼 그룹 (선택만 가능, 수정 버튼 없음)
        home_preset_radio_group = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Radio(
                                value=preset_key,
                            ),
                            ft.Text(preset_key, size=12),
                        ],
                        spacing=10,
                        expand=True,
                    )
                    for preset_key in preset_keys
                ] if preset_keys else [ft.Text("프리셋이 없습니다.", color=ft.Colors.GREY_600)],
                spacing=5,
            ),
            value=current_preset if current_preset else None,
        )
        
        # 프리셋 선택 변경 핸들러
        def on_home_preset_selection_change(e):
            selected_preset = e.control.value
            if selected_preset:
                # 프리셋 로드
                load_preset_combination(selected_preset)
                # 현재 프리셋 저장
                preset_data = load_preset()
                preset_data["current"] = selected_preset
                save_preset(preset_data)
                # 성공 메시지
                page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"프리셋 '{selected_preset}'이(가) 선택되었습니다."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
        
        home_preset_radio_group.on_change = on_home_preset_selection_change
        
        # 항상 최상단 스위치
        항상_최상단_스위치 = ft.Switch(
            value=항상_최상단,
            label="항상 최상단에 표시",
        )
        
        # 항상 최상단 스위치 변경 핸들러
        def on_항상_최상단_change(e):
            nonlocal 항상_최상단
            항상_최상단 = e.control.value
            page.window.always_on_top = 항상_최상단
            page.update()
        
        항상_최상단_스위치.on_change = on_항상_최상단_change
        
        # 홈 화면 콘텐츠 구성
        home_content_items = [
            항상_최상단_스위치,
            # 프리셋 선택 섹션
            ft.Text(
                value="프리셋 선택",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            home_preset_radio_group,
        ]
        
        # 피로도 섹션이 있으면 프리셋 선택 하단에 추가
        if 피로도_섹션:
            home_content_items.append(피로도_섹션)
        
        # 나머지 섹션 추가
        home_content_items.extend([
            # 공지사항 섹션
            ft.Text(
                value="공지사항",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            공지사항_field,
            # 알림창 섹션
            ft.Text(
                value="알림창",
                size=18,
                weight=ft.FontWeight.BOLD,
            ),
            알림창_field,
        ])
        
        return ft.Container(
            content=ft.Column(
                home_content_items,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
    
    # 프로필 JSON 파일 읽기 함수
    def load_profile():
        if os.path.exists(프로필_path):
            try:
                with open(프로필_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    # 프로필 저장 함수
    def save_profile(profile_data):
        file_path = os.path.abspath(프로필_path)  # 절대 경로로 변환
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, ensure_ascii=False, indent=2)
    
    # 프로필 확인 함수
    def has_profile():
        profile_data = load_profile()
        # 프로필이 딕셔너리이고 키가 있으면 프로필이 있는 것
        if isinstance(profile_data, dict):
            return len(profile_data) > 0
        return False
    
    # 미니맵 JSON 파일 읽기 함수
    def load_minimap():
        if os.path.exists(미니맵_path):
            try:
                with open(미니맵_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    # 미니맵 저장 함수
    def save_minimap(minimap_data):
        file_path = os.path.abspath(미니맵_path)  # 절대 경로로 변환
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(minimap_data, f, ensure_ascii=False, indent=2)
    
    # 메뉴 JSON 파일 읽기 함수
    def load_menu():
        if os.path.exists(메뉴_path):
            try:
                with open(메뉴_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 리스트 형태로 반환 (순서 유지)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and "항목들" in data:
                        return data["항목들"]
                    return []
            except:
                return []
        return []
    
    # 메뉴 저장 함수
    def save_menu(menu_items):
        file_path = os.path.abspath(메뉴_path)  # 절대 경로로 변환
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # 리스트 형태로 저장 (순서 유지)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(menu_items, f, ensure_ascii=False, indent=2)
    
    # 프리셋 JSON 파일 읽기 함수
    def load_preset():
        if os.path.exists(프리셋_path):
            try:
                with open(프리셋_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"current": ""}
        return {"current": ""}
    
    # 프리셋 저장 함수
    def save_preset(preset_data):
        file_path = os.path.abspath(프리셋_path)  # 절대 경로로 변환
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(preset_data, f, ensure_ascii=False, indent=2)
    
    # URL JSON 파일 읽기 함수
    def load_url():
        if os.path.exists(url_path):
            try:
                with open(url_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"채팅창url": ""}
        return {"채팅창url": ""}
    
    # URL 저장 함수
    def save_url(url_data):
        file_path = os.path.abspath(url_path)  # 절대 경로로 변환
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(url_data, f, ensure_ascii=False, indent=2)
    
    # 설정 페이지 콘텐츠
    def get_settings_content():
        # 기존 프로필 데이터 로드
        profile_data = load_profile()
        has_profile_data = bool(profile_data and len(profile_data) > 0)
        
        # 프로필 표시 영역
        if has_profile_data:
            # 프로필이 있는 경우: 첫 번째 프로필 데이터 사용
            first_profile_key = list(profile_data.keys())[0]
            profile = profile_data.get(first_profile_key, {})
            
            # 프로필 이미지 표시
            profile_image_widget = None
            profile_image_path = profile.get("이미지", "")
            if profile_image_path:
                # 상대 경로인 경우 img 폴더 확인
                if not os.path.isabs(profile_image_path):
                    img_path = os.path.join(img_dir, profile_image_path)
                else:
                    img_path = profile_image_path
                
                if os.path.exists(img_path):
                    try:
                        # Base64 인코딩
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            # MIME 타입 결정
                            if img_path.lower().endswith('.svg'):
                                mime_type = "image/svg+xml"
                            elif img_path.lower().endswith('.png'):
                                mime_type = "image/png"
                            elif img_path.lower().endswith(('.jpg', '.jpeg')):
                                mime_type = "image/jpeg"
                            else:
                                mime_type = "image/png"
                            profile_image_widget = ft.Image(
                                src_base64=img_data,
                                width=64,
                                height=64,
                                fit=ft.ImageFit.CONTAIN,
                            )
                    except:
                        profile_image_widget = ft.Icon(ft.Icons.PERSON, size=64, color=ft.Colors.GREY_400)
            
            if not profile_image_widget:
                profile_image_widget = ft.Icon(ft.Icons.PERSON, size=64, color=ft.Colors.GREY_400)
            
            # 프로필 이름 (닉네임)
            profile_name = profile.get("이름", "이름 없음")
            
            # 프로필 표시 컨테이너
            profile_display = ft.Container(
                content=ft.Row(
                    [
                        ft.Container(
                            content=profile_image_widget,
                            width=64,
                            height=64,
                            border_radius=32,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        ),
                        ft.Text(
                            value=profile_name,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Container(expand=True),  # 공간 채우기
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=20,
                            tooltip="수정",
                            on_click=lambda e: show_edit_profile_screen(),
                        ),
                    ],
                    spacing=15,
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
            )
        else:
            # 프로필이 없는 경우: 프로필 추가 버튼 표시
            profile_display = ft.ElevatedButton(
                "프로필 추가",
                icon=ft.Icons.ADD,
                on_click=lambda e: show_add_profile_screen(),
            )
        
        # 프리셋 데이터 로드
        preset_data = load_preset()
        current_preset = preset_data.get("current", "")
        preset_keys = [k for k in preset_data.keys() if k != "current"]
        
        # 프리셋 라디오 버튼 그룹
        preset_radio_group = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Radio(
                                value=preset_key,
                            ),
                            ft.Text(preset_key, size=12),
                            ft.Container(expand=True),  # 공간 채우기
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="수정",
                                on_click=lambda e, k=preset_key: show_edit_preset_screen(k),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=20,
                                tooltip="삭제",
                                icon_color=ft.Colors.RED,
                                on_click=lambda e, k=preset_key: delete_preset(k),
                            ),
                        ],
                        spacing=10,
                        expand=True,
                    )
                    for preset_key in preset_keys
                ] if preset_keys else [],
                spacing=5,
            ),
            value=current_preset if current_preset else None,
        )
        
        # 프리셋 선택 변경 핸들러
        def on_preset_selection_change(e):
            selected_preset = e.control.value
            if selected_preset:
                # 프리셋 로드
                load_preset_combination(selected_preset)
                # 현재 프리셋 저장
                preset_data = load_preset()
                preset_data["current"] = selected_preset
                save_preset(preset_data)
                # UI 업데이트
                refresh_settings_screen()
        
        preset_radio_group.on_change = on_preset_selection_change
        
        # 프리셋 삭제 함수
        def delete_preset(preset_key):
            preset_data = load_preset()
            if preset_key in preset_data:
                del preset_data[preset_key]
                # 현재 프리셋이 삭제된 경우 초기화
                if preset_data.get("current") == preset_key:
                    preset_data["current"] = ""
                save_preset(preset_data)
                refresh_settings_screen()
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("프리셋이 삭제되었습니다."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
        
        # 스크롤 가능한 컬럼 생성 (스크롤 위치 유지를 위해 ListView 사용)
        settings_list_view = ft.ListView(
            [
                ft.Text(
                    value="프로필 설정",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                profile_display,
                # 프리셋 설정
                ft.Text(
                    value="프리셋 설정",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                # 프리셋 선택 라디오 버튼
                ft.Text(
                    value="프리셋 선택:",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                ),
                preset_radio_group,
                # 프리셋 추가 버튼
                ft.ElevatedButton(
                    "새 프리셋 추가",
                    icon=ft.Icons.ADD,
                    on_click=lambda e: show_add_preset_screen(),
                ),
                # 채팅 URL 설정
                ft.Text(
                    value="채팅 URL 설정",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                # 채팅 URL 입력 필드
                ft.TextField(
                    label="채팅창 URL",
                    hint_text="채팅창 URL을 입력하세요",
                    value=load_url().get("채팅창url", ""),
                    expand=True,
                    on_change=lambda e: save_url({"채팅창url": e.control.value}),
                ),
            ],
            spacing=15,
            padding=20,
            expand=True,
        )
        
        content_widget = ft.Container(
            content=settings_list_view,
            expand=True,
        )
        return content_widget
    
    # 메뉴 리스트 생성 함수 (위/아래 화살표 버튼으로 순서 변경)
    def get_menu_list():
        menu_items = load_menu()
        
        if not menu_items:
            return ft.Container(
                content=ft.Text("메뉴 항목이 없습니다.", color=ft.Colors.GREY_600),
                padding=10,
            )
        
        # 체크박스 상태 변경 핸들러
        def on_menu_checkbox_change(idx, checkbox):
            # 메뉴 데이터 다시 로드
            menu_items_new = load_menu()
            
            # 해당 인덱스의 메뉴 객체 가져오기
            if idx < len(menu_items_new):
                menu_item = menu_items_new[idx]
                
                # 문자열 형태인 경우 딕셔너리로 변환
                if isinstance(menu_item, str):
                    menu_item = {"텍스트": menu_item, "아이콘": "", "서브_텍스트": "", "사용": False}
                    menu_items_new[idx] = menu_item
                
                # 체크 상태를 메뉴 객체에 저장
                menu_item["사용"] = checkbox.value
                
                # 저장
                save_menu(menu_items_new)
                
                # 스크롤 위치 유지하며 업데이트
                refresh_settings_screen()
        
        # 위로 이동 핸들러
        def move_up(idx):
            if idx > 0:
                menu_items_new = load_menu()
                menu_items_new[idx], menu_items_new[idx - 1] = menu_items_new[idx - 1], menu_items_new[idx]
                save_menu(menu_items_new)
                # 스크롤 위치 유지하며 업데이트
                refresh_settings_screen()
        
        # 아래로 이동 핸들러
        def move_down(idx):
            menu_items_new = load_menu()
            if idx < len(menu_items_new) - 1:
                menu_items_new[idx], menu_items_new[idx + 1] = menu_items_new[idx + 1], menu_items_new[idx]
                save_menu(menu_items_new)
                # 스크롤 위치 유지하며 업데이트
                refresh_settings_screen()
        
        menu_list_items = []
        for idx, item in enumerate(menu_items):
            # 기존 문자열 형태 호환
            if isinstance(item, str):
                item_icon = ""
                item_text = item
                item_subtext = ""
            else:
                item_icon = item.get("아이콘", "")
                item_text = item.get("텍스트", "")
                item_subtext = item.get("서브_텍스트", "")
            
            # 텍스트를 표시
            display_text = item_text
            
            # 체크박스 상태 확인 (메뉴 객체의 "사용" 필드 확인)
            if isinstance(item, dict):
                is_checked = item.get("사용", False)
            else:
                is_checked = False
            
            # 체크박스 생성
            menu_checkbox = ft.Checkbox(
                value=is_checked,
                on_change=lambda e, i=idx, cb=None: on_menu_checkbox_change(i, e.control),
            )
            
            # 아이콘 표시 (이미지 경로가 있으면 표시)
            icon_widget = None
            if item_icon:
                # 이미지 파일 경로 (전체 경로 또는 상대 경로)
                img_path = item_icon
                # 상대 경로인 경우 img 폴더 확인
                if not os.path.isabs(img_path):
                    img_path = os.path.join(img_dir, item_icon)
                
                if os.path.exists(img_path):
                    try:
                        # Base64 인코딩
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            mime_type = "image/png" if img_path.lower().endswith('.png') else "image/jpeg"
                            icon_widget = ft.Image(
                                src_base64=img_data,
                                width=24,
                                height=24,
                                fit=ft.ImageFit.CONTAIN,
                            )
                    except:
                        icon_widget = None
            
            # 텍스트 영역
            text_column = ft.Column(
                [
                    ft.Text(display_text, size=14, weight=ft.FontWeight.BOLD) if display_text else ft.Text("", size=14),
                    ft.Text(item_subtext, size=12, color=ft.Colors.GREY_600) if item_subtext else ft.Text("", size=12),
                ],
                spacing=2,
                expand=True,
            )
            
            # 메뉴 항목 컨테이너
            menu_item_container = ft.Container(
                content=ft.Row(
                    [
                        menu_checkbox,  # 체크박스 추가
                        icon_widget if icon_widget else ft.Container(width=24, height=24),
                        text_column,
                        ft.Container(expand=True),  # 공간 채우기
                        # 위로 이동 버튼 (첫 번째 항목이 아니면 표시)
                        ft.IconButton(
                            icon=ft.Icons.ARROW_UPWARD,
                            icon_size=18,
                            tooltip="위로 이동",
                            on_click=lambda e, i=idx: move_up(i),
                            disabled=(idx == 0),
                        ) if idx > 0 else ft.Container(width=40, height=40),
                        # 아래로 이동 버튼 (마지막 항목이 아니면 표시)
                        ft.IconButton(
                            icon=ft.Icons.ARROW_DOWNWARD,
                            icon_size=18,
                            tooltip="아래로 이동",
                            on_click=lambda e, i=idx: move_down(i),
                            disabled=(idx == len(menu_items) - 1),
                        ) if idx < len(menu_items) - 1 else ft.Container(width=40, height=40),
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=20,
                            tooltip="수정",
                            on_click=lambda e, i=idx: show_edit_menu_screen(i),
                        ),
                    ],
                    spacing=5,
                    expand=True,
                ),
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
                border_radius=5,
                bgcolor=ft.Colors.WHITE,
            )
            
            menu_list_items.append(menu_item_container)
        
        return ft.Column(
            menu_list_items,
            spacing=5,
            expand=False,
        )
    
    # 미니맵 추가 화면
    def get_add_minimap_content(return_screen=None, preset_key=None):
        # 입력 필드들
        new_minimap_이름_field = ft.TextField(
            label="미니맵 이름",
            value="",
            expand=True,
        )
        
        new_minimap_지역_이름_field = ft.TextField(
            label="미니맵 지역 이름",
            value="",
            expand=True,
        )
        
        new_minimap_위험도_field = ft.TextField(
            label="위험도",
            value="",
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        new_minimap_탐사진척도_field = ft.TextField(
            label="탐사진척도",
            value="",
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        # img 디렉토리의 이미지 파일 목록 가져오기 (이미 위에서 정의됨)
        image_files = []
        if os.path.exists(img_dir):
            for file in os.listdir(img_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                    image_files.append(file)
        
        # 파일명 순서대로 정렬
        image_files.sort()
        
        # 이미지 위젯 생성 함수
        def create_minimap_image_widget(img_file):
            img_path = os.path.join(img_dir, img_file)
            if os.path.exists(img_path):
                try:
                    # Base64 인코딩
                    with open(img_path, 'rb') as img_file_handle:
                        img_data = base64.b64encode(img_file_handle.read()).decode('utf-8')
                        # MIME 타입 결정
                        if img_file.lower().endswith('.svg'):
                            mime_type = "image/svg+xml"
                        elif img_file.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif img_file.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        else:
                            mime_type = "image/png"
                        return ft.Image(
                            src_base64=img_data,
                            width=32,
                            height=32,
                            fit=ft.ImageFit.CONTAIN,
                        )
                except:
                    return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
        
        # 이미지 선택 핸들러
        def select_minimap_image(img_file):
            minimap_image_radio_group.value = img_file
            minimap_image_radio_group.update()
        
        # RadioGroup 생성
        minimap_image_radio_group = ft.RadioGroup(
            content=ft.ListView(
                [
                    ft.ListTile(
                        leading=ft.Radio(
                            value=img_file,
                        ),
                        title=ft.Row(
                            [
                                create_minimap_image_widget(img_file),
                                ft.Text(img_file, size=12),
                            ],
                            spacing=10,
                        ),
                        on_click=lambda e, f=img_file: select_minimap_image(f),
                    )
                    for img_file in image_files
                ] if image_files else [ft.ListTile(title=ft.Text("이미지가 없습니다.", color=ft.Colors.GREY_600))],
                height=150,
                spacing=2,
            ),
            value=None,
        )
        
        # 이미지 선택 컨테이너
        minimap_image_selection_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        value="이미지 선택",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=minimap_image_radio_group,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=8,
            ),
        )
        
        # 뒤로 가기 핸들러
        def go_back(e):
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                show_settings_screen()
        
        # 저장 핸들러
        def save_new_minimap(e):
            new_name = new_minimap_이름_field.value.strip()
            if not new_name:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("미니맵 이름을 입력하세요."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 기존 미니맵 데이터 로드
            minimap_data = load_minimap()
            if new_name in minimap_data:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("이미 존재하는 미니맵 이름입니다."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 선택된 이미지 경로 (파일명만 저장)
            selected_image = minimap_image_radio_group.value if minimap_image_radio_group.value else ""
            
            # 새 미니맵 생성 (미니맵 이름을 키로 사용)
            minimap_data[new_name] = {
                "이미지": selected_image,
                "미니맵_이름": new_name,
                "미니맵_지역_이름": new_minimap_지역_이름_field.value,
                "위험도": new_minimap_위험도_field.value,
                "탐사진척도": new_minimap_탐사진척도_field.value,
            }
            
            # 저장
            save_minimap(minimap_data)
            
            # 프리셋 화면으로 돌아가기
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("미니맵이 추가되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="새 미니맵 추가",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드들
                    minimap_image_selection_container,
                    new_minimap_이름_field,
                    new_minimap_지역_이름_field,
                    new_minimap_위험도_field,
                    new_minimap_탐사진척도_field,
                    # 저장 버튼
                    ft.ElevatedButton(
                        "저장",
                        icon=ft.Icons.SAVE,
                        on_click=save_new_minimap,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    # 미니맵 수정 화면
    def get_edit_minimap_content(minimap_key, return_screen=None, preset_key=None):
        # 미니맵 데이터 로드
        minimap_data = load_minimap()
        current_minimap = minimap_data.get(minimap_key, {})
        
        # 입력 필드들 (기존 데이터로 초기화)
        edit_minimap_이름_field = ft.TextField(
            label="미니맵 이름",
            value=current_minimap.get("미니맵_이름", minimap_key),  # 기존 키를 기본값으로 사용
            expand=True,
        )
        
        edit_minimap_지역_이름_field = ft.TextField(
            label="미니맵 지역 이름",
            value=current_minimap.get("미니맵_지역_이름", ""),
            expand=True,
        )
        
        edit_minimap_위험도_field = ft.TextField(
            label="위험도",
            value=current_minimap.get("위험도", ""),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        edit_minimap_탐사진척도_field = ft.TextField(
            label="탐사진척도",
            value=current_minimap.get("탐사진척도", ""),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        # img 디렉토리의 이미지 파일 목록 가져오기 (이미 위에서 정의됨)
        image_files = []
        if os.path.exists(img_dir):
            for file in os.listdir(img_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                    image_files.append(file)
        
        # 파일명 순서대로 정렬
        image_files.sort()
        
        # 현재 선택된 이미지 파일명 추출
        menu_icon = current_minimap.get("이미지", "")
        current_image_file = None
        if menu_icon:
            if os.path.isabs(menu_icon):
                current_image_file = os.path.basename(menu_icon)
            else:
                current_image_file = os.path.basename(menu_icon)
            # img 폴더에 있는 파일인지 확인
            if current_image_file not in image_files:
                current_image_file = None
        
        # 이미지 위젯 생성 함수
        def create_edit_minimap_image_widget(img_file):
            img_path = os.path.join(img_dir, img_file)
            if os.path.exists(img_path):
                try:
                    # Base64 인코딩
                    with open(img_path, 'rb') as img_file_handle:
                        img_data = base64.b64encode(img_file_handle.read()).decode('utf-8')
                        # MIME 타입 결정
                        if img_file.lower().endswith('.svg'):
                            mime_type = "image/svg+xml"
                        elif img_file.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif img_file.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        else:
                            mime_type = "image/png"
                        return ft.Image(
                            src_base64=img_data,
                            width=32,
                            height=32,
                            fit=ft.ImageFit.CONTAIN,
                        )
                except:
                    return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
        
        # 이미지 선택 핸들러
        def select_edit_minimap_image(img_file):
            edit_minimap_image_radio_group.value = img_file
            edit_minimap_image_radio_group.update()
        
        # 이미지 선택 라디오 버튼 그룹
        edit_minimap_image_radio_group = ft.RadioGroup(
            content=ft.ListView(
                [
                    ft.ListTile(
                        leading=ft.Radio(
                            value=img_file,
                        ),
                        title=ft.Row(
                            [
                                create_edit_minimap_image_widget(img_file),
                                ft.Text(img_file, size=12),
                            ],
                            spacing=10,
                        ),
                        on_click=lambda e, f=img_file: select_edit_minimap_image(f),
                    )
                    for img_file in image_files
                ] if image_files else [ft.ListTile(title=ft.Text("이미지가 없습니다.", color=ft.Colors.GREY_600))],
                height=150,
                spacing=2,
            ),
            value=current_image_file,
        )
        
        # 이미지 선택 컨테이너
        edit_minimap_image_selection_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        value="이미지 선택",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=edit_minimap_image_radio_group,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=8,
            ),
        )
        
        # 뒤로 가기 핸들러
        def go_back(e):
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                show_settings_screen()
        
        # 저장 핸들러
        def save_edited_minimap(e):
            new_name = edit_minimap_이름_field.value.strip()
            if not new_name:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("미니맵 이름을 입력하세요."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 기존 미니맵 데이터 로드
            minimap_data = load_minimap()
            
            # 기존 미니맵의 "선택됨" 필드 가져오기
            existing_minimap = minimap_data.get(minimap_key, {})
            existing_선택됨 = existing_minimap.get("선택됨", False)
            
            # 선택된 이미지 경로 (파일명만 저장)
            selected_image = edit_minimap_image_radio_group.value if edit_minimap_image_radio_group.value else ""
            
            # 미니맵 데이터 준비 ("선택됨" 필드 유지)
            updated_minimap = {
                "이미지": selected_image,
                "미니맵_이름": new_name,
                "미니맵_지역_이름": edit_minimap_지역_이름_field.value,
                "위험도": edit_minimap_위험도_field.value,
                "탐사진척도": edit_minimap_탐사진척도_field.value,
            }
            
            # "선택됨" 필드 유지
            if existing_선택됨:
                updated_minimap["선택됨"] = True
            
            # 키가 변경된 경우
            if new_name != minimap_key:
                # 기존 키가 이미 존재하는지 확인
                if new_name in minimap_data:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("이미 존재하는 미니맵 이름입니다."),
                        action="OK",
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                # 기존 키 삭제하고 새 키로 추가
                if minimap_key in minimap_data:
                    del minimap_data[minimap_key]
                minimap_data[new_name] = updated_minimap
            else:
                # 키가 변경되지 않은 경우 기존 키 업데이트
                minimap_data[minimap_key] = updated_minimap
            
            # 저장
            save_minimap(minimap_data)
            
            # 프리셋 화면으로 돌아가기
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("미니맵이 수정되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        # 삭제 핸들러
        def delete_minimap(e):
            # 기존 미니맵 데이터 로드
            minimap_data = load_minimap()
            
            # 미니맵 삭제
            if minimap_key in minimap_data:
                del minimap_data[minimap_key]
            
            # 저장
            save_minimap(minimap_data)
            
            # 프리셋 화면으로 돌아가기
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("미니맵이 삭제되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="미니맵 수정",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드들
                    edit_minimap_image_selection_container,
                    edit_minimap_이름_field,
                    edit_minimap_지역_이름_field,
                    edit_minimap_위험도_field,
                    edit_minimap_탐사진척도_field,
                    # 버튼들
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "저장",
                                icon=ft.Icons.SAVE,
                                on_click=save_edited_minimap,
                                expand=True,  # 나머지 너비 모두 차지
                            ),
                            ft.ElevatedButton(
                                "삭제",
                                icon=ft.Icons.DELETE,
                                on_click=delete_minimap,
                                color=ft.Colors.RED,
                                # expand 없음 - 내부 크기만큼만 차지
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    # 메뉴 추가 화면
    def get_add_menu_content(return_screen=None, preset_key=None):
        # 입력 필드들
        new_menu_text_field = ft.TextField(
            label="텍스트",
            hint_text="메뉴 텍스트를 입력하세요",
            expand=True,
            autofocus=True,
        )
        
        new_menu_subtext_field = ft.TextField(
            label="서브 텍스트",
            hint_text="서브 텍스트를 입력하세요 (선택사항)",
            expand=True,
        )
        
        # img 디렉토리의 이미지 파일 목록 가져오기 (이미 위에서 정의됨)
        image_files = []
        if os.path.exists(img_dir):
            for file in os.listdir(img_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                    image_files.append(file)
        
        # 파일명 순서대로 정렬
        image_files.sort()
        
        # 이미지 위젯 생성 함수
        def create_image_widget(img_file):
            img_path = os.path.join(img_dir, img_file)
            if os.path.exists(img_path):
                try:
                    # Base64 인코딩
                    with open(img_path, 'rb') as img_file_handle:
                        img_data = base64.b64encode(img_file_handle.read()).decode('utf-8')
                        # MIME 타입 결정
                        if img_file.lower().endswith('.svg'):
                            mime_type = "image/svg+xml"
                        elif img_file.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif img_file.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        else:
                            mime_type = "image/png"
                        return ft.Image(
                            src_base64=img_data,
                            width=32,
                            height=32,
                            fit=ft.ImageFit.CONTAIN,
                        )
                except:
                    return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
        
        # RadioGroup 생성
        image_radio_group = ft.RadioGroup(
            content=ft.ListView(
                [
                    ft.ListTile(
                        leading=ft.Radio(
                            value=img_file,
                        ),
                        title=ft.Row(
                            [
                                create_image_widget(img_file),
                                ft.Text(img_file, size=12),
                            ],
                            spacing=10,
                        ),
                        on_click=lambda e, f=img_file: select_image(f),
                    )
                    for img_file in image_files
                ] if image_files else [ft.ListTile(title=ft.Text("이미지가 없습니다.", color=ft.Colors.GREY_600))],
                height=150,
                spacing=2,
            ),
            value=None,
        )
        
        # 이미지 선택 핸들러
        def select_image(img_file):
            image_radio_group.value = img_file
            image_radio_group.update()
        
        # 이미지 선택 컨테이너
        image_selection_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        value="아이콘 선택",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=image_radio_group,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=8,
            ),
        )
        
        # 뒤로 가기 핸들러
        def go_back(e):
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                refresh_settings_screen()
        
        # 저장 핸들러
        def save_new_menu(e):
            menu_text = new_menu_text_field.value.strip()
            if not menu_text:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("텍스트를 입력하세요."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 기존 메뉴 데이터 로드
            menu_items = load_menu()
            
            # 선택된 이미지 경로
            image_path = image_radio_group.value if image_radio_group.value else ""
            
            # 새 메뉴 추가 (텍스트를 키로 사용)
            new_menu = {
                "아이콘": image_path,
                "텍스트": menu_text,
                "서브_텍스트": new_menu_subtext_field.value.strip(),
                "사용": False,  # 기본값은 체크 안됨
            }
            menu_items.append(new_menu)
            
            # 저장
            save_menu(menu_items)
            
            # 프리셋 화면으로 돌아가기
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                refresh_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("메뉴가 추가되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="새 메뉴 추가",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드들
                    image_selection_container,
                    new_menu_text_field,
                    new_menu_subtext_field,
                    # 저장 버튼
                    ft.ElevatedButton(
                        "저장",
                        icon=ft.Icons.SAVE,
                        on_click=save_new_menu,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    # 메뉴 수정 화면
    def get_edit_menu_content(menu_index, return_screen=None, preset_key=None):
        # 메뉴 데이터 로드
        menu_items = load_menu()
        if menu_index >= len(menu_items):
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                show_settings_screen()
            return ft.Container()
        
        current_menu = menu_items[menu_index]
        # 기존 문자열 형태 호환
        if isinstance(current_menu, str):
            menu_icon = ""
            menu_text = current_menu
            menu_subtext = ""
        else:
            menu_icon = current_menu.get("아이콘", "")
            menu_text = current_menu.get("텍스트", "")
            menu_subtext = current_menu.get("서브_텍스트", "")
        
        # img 디렉토리의 이미지 파일 목록 가져오기 (이미 위에서 정의됨)
        image_files = []
        if os.path.exists(img_dir):
            for file in os.listdir(img_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                    image_files.append(file)
        
        # 파일명 순서대로 정렬
        image_files.sort()
        
        # 현재 선택된 이미지 파일명 추출 (경로에서)
        current_image_file = None
        if menu_icon:
            if os.path.isabs(menu_icon):
                # 절대 경로인 경우
                current_image_file = os.path.basename(menu_icon)
            else:
                # 상대 경로인 경우
                current_image_file = os.path.basename(menu_icon)
            # img 폴더에 있는 파일인지 확인
            if current_image_file not in image_files:
                current_image_file = None
        
        # 입력 필드들 (기존 데이터로 초기화)
        edit_menu_text_field = ft.TextField(
            label="텍스트",
            hint_text="메뉴 텍스트를 입력하세요",
            value=menu_text,
            expand=True,
            autofocus=True,
        )
        
        edit_menu_subtext_field = ft.TextField(
            label="서브 텍스트",
            hint_text="서브 텍스트를 입력하세요 (선택사항)",
            value=menu_subtext,
            expand=True,
        )
        
        # 이미지 위젯 생성 함수
        def create_edit_image_widget(img_file):
            img_path = os.path.join(img_dir, img_file)
            if os.path.exists(img_path):
                try:
                    # Base64 인코딩
                    with open(img_path, 'rb') as img_file_handle:
                        img_data = base64.b64encode(img_file_handle.read()).decode('utf-8')
                        # MIME 타입 결정
                        if img_file.lower().endswith('.svg'):
                            mime_type = "image/svg+xml"
                        elif img_file.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif img_file.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        else:
                            mime_type = "image/png"
                        return ft.Image(
                            src_base64=img_data,
                            width=32,
                            height=32,
                            fit=ft.ImageFit.CONTAIN,
                        )
                except:
                    return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
        
        # 이미지 선택 핸들러
        def select_edit_image(img_file):
            edit_image_radio_group.value = img_file
            edit_image_radio_group.update()
        
        # 이미지 선택 라디오 버튼 그룹 (스크롤 뷰 안에)
        edit_image_radio_group = ft.RadioGroup(
            content=ft.ListView(
                [
                    ft.ListTile(
                        leading=ft.Radio(
                            value=img_file,
                        ),
                        title=ft.Row(
                            [
                                create_edit_image_widget(img_file),
                                ft.Text(img_file, size=12),
                            ],
                            spacing=10,
                        ),
                        on_click=lambda e, f=img_file: select_edit_image(f),
                    )
                    for img_file in image_files
                ] if image_files else [ft.ListTile(title=ft.Text("이미지가 없습니다.", color=ft.Colors.GREY_600))],
                height=150,
                spacing=2,
            ),
            value=current_image_file,
        )
        
        # 이미지 선택 컨테이너
        edit_image_selection_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        value="아이콘 선택",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=edit_image_radio_group,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=8,
            ),
        )
        
        # 뒤로 가기 핸들러
        def go_back(e):
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                refresh_settings_screen()
        
        # 저장 핸들러
        def save_edited_menu(e):
            menu_text_value = edit_menu_text_field.value.strip()
            if not menu_text_value:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("텍스트를 입력하세요."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 기존 메뉴 데이터 로드
            menu_items = load_menu()
            
            # 기존 메뉴의 "사용" 필드 가져오기
            existing_menu = menu_items[menu_index] if menu_index < len(menu_items) else {}
            existing_사용 = existing_menu.get("사용", False) if isinstance(existing_menu, dict) else False
            
            # 선택된 이미지 경로 (파일명만 저장)
            selected_image = edit_image_radio_group.value
            image_path = selected_image if selected_image else ""
            
            # 메뉴 업데이트 (텍스트를 키로 사용, "사용" 필드 유지)
            menu_items[menu_index] = {
                "아이콘": image_path,
                "텍스트": menu_text_value,
                "서브_텍스트": edit_menu_subtext_field.value.strip(),
                "사용": existing_사용,  # 기존 체크 상태 유지
            }
            
            # 저장
            save_menu(menu_items)
            
            # 프리셋 화면으로 돌아가기
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                refresh_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("메뉴가 수정되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        # 삭제 핸들러
        def delete_menu(e):
            # 기존 메뉴 데이터 로드
            menu_items = load_menu()
            
            # 메뉴 삭제
            menu_items.pop(menu_index)
            
            # 저장
            save_menu(menu_items)
            
            # 프리셋 화면으로 돌아가기
            if return_screen == "add_preset":
                show_add_preset_screen()
            elif return_screen == "edit_preset" and preset_key:
                show_edit_preset_screen(preset_key)
            else:
                refresh_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("메뉴가 삭제되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="메뉴 수정",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드
                    edit_image_selection_container,
                    edit_menu_text_field,
                    edit_menu_subtext_field,
                    # 버튼들
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "저장",
                                icon=ft.Icons.SAVE,
                                on_click=save_edited_menu,
                                expand=True,  # 나머지 너비 모두 차지
                            ),
                            ft.ElevatedButton(
                                "삭제",
                                icon=ft.Icons.DELETE,
                                on_click=delete_menu,
                                color=ft.Colors.RED,
                                # expand 없음 - 내부 크기만큼만 차지
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    # 프로필 추가 화면
    def get_add_profile_content():
        # img 디렉토리의 이미지 파일 목록 가져오기 (이미 위에서 정의됨)
        image_files = []
        if os.path.exists(img_dir):
            for file in os.listdir(img_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                    image_files.append(file)
        
        # 파일명 순서대로 정렬
        image_files.sort()
        
        # 입력 필드들
        new_profile_이름_field = ft.TextField(
            label="이름",
            expand=True,
            autofocus=True,
        )
        
        new_profile_user_id_field = ft.TextField(
            label="User ID",
            expand=True,
        )
        
        new_profile_레벨_field = ft.TextField(
            label="레벨",
            expand=True,
        )
        
        new_profile_최대_피로도_field = ft.TextField(
            label="최대 피로도",
            value="100",
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        # 피로도 슬라이더
        new_profile_피로도_표시 = ft.Text(
            value="피로도: 0/100",
            size=14,
        )
        
        new_profile_피로도_slider = ft.Slider(
            min=0,
            max=100,
            value=0,
            divisions=100,
            label="{value}",
        )
        
        # 이미지 위젯 생성 함수
        def create_profile_image_widget(img_file):
            img_path = os.path.join(img_dir, img_file)
            if os.path.exists(img_path):
                try:
                    # Base64 인코딩
                    with open(img_path, 'rb') as img_file_handle:
                        img_data = base64.b64encode(img_file_handle.read()).decode('utf-8')
                        # MIME 타입 결정
                        if img_file.lower().endswith('.svg'):
                            mime_type = "image/svg+xml"
                        elif img_file.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif img_file.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        else:
                            mime_type = "image/png"
                        return ft.Image(
                            src_base64=img_data,
                            width=32,
                            height=32,
                            fit=ft.ImageFit.CONTAIN,
                        )
                except:
                    return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
        
        # 이미지 선택 핸들러
        def select_profile_image(img_file):
            profile_image_radio_group.value = img_file
            profile_image_radio_group.update()
        
        # 이미지 선택 라디오 버튼 그룹
        profile_image_radio_group = ft.RadioGroup(
            content=ft.ListView(
                [
                    ft.ListTile(
                        leading=ft.Radio(
                            value=img_file,
                        ),
                        title=ft.Row(
                            [
                                create_profile_image_widget(img_file),
                                ft.Text(img_file, size=12),
                            ],
                            spacing=10,
                        ),
                        on_click=lambda e, f=img_file: select_profile_image(f),
                    )
                    for img_file in image_files
                ] if image_files else [ft.ListTile(title=ft.Text("이미지가 없습니다.", color=ft.Colors.GREY_600))],
                height=150,
                spacing=2,
            ),
            value=None,
        )
        
        # 이미지 선택 컨테이너
        profile_image_selection_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        value="이미지 선택",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=profile_image_radio_group,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=8,
            ),
        )
        
        # 최대 피로도 변경 핸들러
        def on_최대_피로도_change(e):
            try:
                최대값 = int(e.control.value) if e.control.value else 100
            except:
                최대값 = 100
            
            # 슬라이더 최대값 업데이트
            new_profile_피로도_slider.max = max(최대값, 1)
            new_profile_피로도_slider.divisions = min(최대값, 100)
            # 현재 값이 새로운 최대값을 초과하면 최대값으로 조정
            if new_profile_피로도_slider.value > 최대값:
                new_profile_피로도_slider.value = 최대값
            
            new_profile_피로도_표시.value = f"피로도: {int(new_profile_피로도_slider.value)}/{최대값}"
            new_profile_피로도_표시.update()
            new_profile_피로도_slider.update()
        
        new_profile_최대_피로도_field.on_change = on_최대_피로도_change
        
        # 피로도 슬라이더 변경 핸들러
        def on_피로도_change(e):
            try:
                최대값 = int(new_profile_최대_피로도_field.value) if new_profile_최대_피로도_field.value else 100
            except:
                최대값 = 100
            new_profile_피로도_표시.value = f"피로도: {int(e.control.value)}/{최대값}"
            new_profile_피로도_표시.update()
        
        new_profile_피로도_slider.on_change = on_피로도_change
        
        # 뒤로 가기 핸들러
        def go_back(e):
            show_settings_screen()
        
        # 저장 핸들러
        def save_new_profile(e):
            이름 = new_profile_이름_field.value.strip()
            if not 이름:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("이름을 입력하세요."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 프로필 데이터 구성
            try:
                최대_피로도_값 = int(new_profile_최대_피로도_field.value) if new_profile_최대_피로도_field.value else 100
            except:
                최대_피로도_값 = 100
            
            selected_image = profile_image_radio_group.value if profile_image_radio_group.value else ""
            
            new_profile = {
                "이미지": selected_image,
                "이름": 이름,
                "User_ID": new_profile_user_id_field.value,
                "피로도": str(int(new_profile_피로도_slider.value)),
                "최대_피로도": str(최대_피로도_값),
                "레벨": new_profile_레벨_field.value,
            }
            
            # 프로필 저장 (이름을 키로 사용)
            save_data = {이름: new_profile}
            save_profile(save_data)
            
            # 설정 화면으로 돌아가기
            show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("프로필이 추가되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="프로필 추가",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드들
                    profile_image_selection_container,
                    new_profile_이름_field,
                    new_profile_user_id_field,
                    new_profile_레벨_field,
                    new_profile_최대_피로도_field,
                    new_profile_피로도_표시,
                    new_profile_피로도_slider,
                    # 저장 버튼
                    ft.ElevatedButton(
                        "저장",
                        icon=ft.Icons.SAVE,
                        on_click=save_new_profile,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    # 프로필 수정 화면
    def get_edit_profile_content():
        # 프로필 데이터 로드
        profile_data = load_profile()
        if not profile_data or len(profile_data) == 0:
            show_settings_screen()
            return ft.Container()
        
        # 첫 번째 프로필 데이터 사용
        first_profile_key = list(profile_data.keys())[0]
        profile = profile_data.get(first_profile_key, {})
        
        # img 디렉토리의 이미지 파일 목록 가져오기 (이미 위에서 정의됨)
        image_files = []
        if os.path.exists(img_dir):
            for file in os.listdir(img_dir):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg')):
                    image_files.append(file)
        
        # 파일명 순서대로 정렬
        image_files.sort()
        
        # 현재 선택된 이미지 파일명 추출
        current_image_file = None
        profile_image_path = profile.get("이미지", "")
        if profile_image_path:
            current_image_file = os.path.basename(profile_image_path)
            # img 폴더에 있는 파일인지 확인
            if current_image_file not in image_files:
                current_image_file = None
        
        # 입력 필드들 (기존 데이터로 초기화)
        edit_profile_이름_field = ft.TextField(
            label="이름",
            value=profile.get("이름", ""),
            expand=True,
            autofocus=True,
        )
        
        edit_profile_user_id_field = ft.TextField(
            label="User ID",
            value=profile.get("User_ID", ""),
            expand=True,
        )
        
        edit_profile_레벨_field = ft.TextField(
            label="레벨",
            value=profile.get("레벨", ""),
            expand=True,
        )
        
        # 최대 피로도 숫자 입력
        최대_피로도_값 = profile.get("최대_피로도", "100")
        try:
            최대_피로도_숫자 = int(최대_피로도_값) if 최대_피로도_값 else 100
        except:
            최대_피로도_숫자 = 100
        
        edit_profile_최대_피로도_field = ft.TextField(
            label="최대 피로도",
            value=str(최대_피로도_숫자),
            expand=True,
            input_filter=ft.NumbersOnlyInputFilter(),
        )
        
        # 피로도 슬라이더
        피로도_값 = profile.get("피로도", "0")
        try:
            피로도_숫자 = int(피로도_값) if 피로도_값 else 0
        except:
            피로도_숫자 = 0
        
        edit_profile_피로도_표시 = ft.Text(
            value=f"피로도: {피로도_숫자}/{최대_피로도_숫자}",
            size=14,
        )
        
        edit_profile_피로도_slider = ft.Slider(
            min=0,
            max=max(최대_피로도_숫자, 1),
            value=min(피로도_숫자, 최대_피로도_숫자),
            divisions=min(최대_피로도_숫자, 100),
            label="{value}",
        )
        
        # 이미지 위젯 생성 함수
        def create_profile_image_widget(img_file):
            img_path = os.path.join(img_dir, img_file)
            if os.path.exists(img_path):
                try:
                    # Base64 인코딩
                    with open(img_path, 'rb') as img_file_handle:
                        img_data = base64.b64encode(img_file_handle.read()).decode('utf-8')
                        # MIME 타입 결정
                        if img_file.lower().endswith('.svg'):
                            mime_type = "image/svg+xml"
                        elif img_file.lower().endswith('.png'):
                            mime_type = "image/png"
                        elif img_file.lower().endswith(('.jpg', '.jpeg')):
                            mime_type = "image/jpeg"
                        else:
                            mime_type = "image/png"
                        return ft.Image(
                            src_base64=img_data,
                            width=32,
                            height=32,
                            fit=ft.ImageFit.CONTAIN,
                        )
                except:
                    return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=32, color=ft.Colors.GREY_400)
        
        # 이미지 선택 핸들러
        def select_profile_image(img_file):
            profile_image_radio_group.value = img_file
            profile_image_radio_group.update()
        
        # 이미지 선택 라디오 버튼 그룹
        profile_image_radio_group = ft.RadioGroup(
            content=ft.ListView(
                [
                    ft.ListTile(
                        leading=ft.Radio(
                            value=img_file,
                        ),
                        title=ft.Row(
                            [
                                create_profile_image_widget(img_file),
                                ft.Text(img_file, size=12),
                            ],
                            spacing=10,
                        ),
                        on_click=lambda e, f=img_file: select_profile_image(f),
                    )
                    for img_file in image_files
                ] if image_files else [ft.ListTile(title=ft.Text("이미지가 없습니다.", color=ft.Colors.GREY_600))],
                height=150,
                spacing=2,
            ),
            value=current_image_file,
        )
        
        # 이미지 선택 컨테이너
        profile_image_selection_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        value="이미지 선택",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(
                        content=profile_image_radio_group,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        border_radius=5,
                        padding=10,
                    ),
                ],
                spacing=8,
            ),
        )
        
        # 최대 피로도 변경 핸들러
        def on_최대_피로도_change(e):
            try:
                최대값 = int(e.control.value) if e.control.value else 100
            except:
                최대값 = 100
            
            # 슬라이더 최대값 업데이트
            edit_profile_피로도_slider.max = max(최대값, 1)
            edit_profile_피로도_slider.divisions = min(최대값, 100)
            # 현재 값이 새로운 최대값을 초과하면 최대값으로 조정
            if edit_profile_피로도_slider.value > 최대값:
                edit_profile_피로도_slider.value = 최대값
            
            edit_profile_피로도_표시.value = f"피로도: {int(edit_profile_피로도_slider.value)}/{최대값}"
            edit_profile_피로도_표시.update()
            edit_profile_피로도_slider.update()
        
        edit_profile_최대_피로도_field.on_change = on_최대_피로도_change
        
        # 피로도 슬라이더 변경 핸들러
        def on_피로도_change(e):
            try:
                최대값 = int(edit_profile_최대_피로도_field.value) if edit_profile_최대_피로도_field.value else 100
            except:
                최대값 = 100
            edit_profile_피로도_표시.value = f"피로도: {int(e.control.value)}/{최대값}"
            edit_profile_피로도_표시.update()
        
        edit_profile_피로도_slider.on_change = on_피로도_change
        
        # 뒤로 가기 핸들러
        def go_back(e):
            show_settings_screen()
        
        # 저장 핸들러
        def save_edited_profile(e):
            # 프로필 데이터 구성
            try:
                최대_피로도_값 = int(edit_profile_최대_피로도_field.value) if edit_profile_최대_피로도_field.value else 100
            except:
                최대_피로도_값 = 100
            
            selected_image = profile_image_radio_group.value if profile_image_radio_group.value else ""
            
            new_profile = {
                "이미지": selected_image,
                "이름": edit_profile_이름_field.value,
                "User_ID": edit_profile_user_id_field.value,
                "피로도": str(int(edit_profile_피로도_slider.value)),
                "최대_피로도": str(최대_피로도_값),
                "레벨": edit_profile_레벨_field.value,
            }
            
            # 프로필 저장 (기존 키 유지)
            save_data = {first_profile_key: new_profile}
            save_profile(save_data)
            
            # 설정 화면으로 돌아가기
            show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("프로필이 수정되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        # 삭제 핸들러
        def delete_profile(e):
            # 프로필 데이터 삭제
            save_profile({})
            
            # 설정 화면으로 돌아가기
            show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("프로필이 삭제되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="프로필 수정",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드들
                    profile_image_selection_container,
                    edit_profile_이름_field,
                    edit_profile_user_id_field,
                    edit_profile_레벨_field,
                    edit_profile_최대_피로도_field,
                    edit_profile_피로도_표시,
                    edit_profile_피로도_slider,
                    # 버튼들
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "저장",
                                icon=ft.Icons.SAVE,
                                on_click=save_edited_profile,
                                expand=True,
                            ),
                            ft.ElevatedButton(
                                "삭제",
                                icon=ft.Icons.DELETE,
                                on_click=delete_profile,
                                color=ft.Colors.RED,
                            ),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    # 화면 전환 함수들
    def show_home_screen():
        nonlocal current_screen
        current_screen = "home"
        main_content_container.content = get_home_content()
        nav_bar.visible = True
        page.update()
    
    def show_settings_screen():
        nonlocal current_screen
        current_screen = "settings"
        main_content_container.content = get_settings_content()
        nav_bar.visible = True
        page.update()
    
    # 설정 화면 새로고침 (스크롤 위치 유지)
    def refresh_settings_screen():
        # 현재 컨텐츠가 설정 화면인지 확인
        if current_screen == "settings":
            # 컨텐츠만 업데이트 (ListView가 스크롤 위치를 유지)
            main_content_container.content = get_settings_content()
            page.update()
        else:
            show_settings_screen()
    
    # 프리셋 추가 화면
    def get_add_preset_content():
        # 프리셋 이름 입력 필드
        new_preset_name_field = ft.TextField(
            label="프리셋 이름",
            hint_text="프리셋 이름을 입력하세요",
            expand=True,
            autofocus=True,
        )
        
        # 미니맵 데이터 로드
        minimap_data = load_minimap()
        minimap_keys = list(minimap_data.keys()) if minimap_data else []
        
        # 미니맵 이미지 위젯 생성 함수
        def create_preset_minimap_image_widget(key):
            minimap_item = minimap_data.get(key, {})
            image_path = minimap_item.get("이미지", "")
            if image_path:
                if not os.path.isabs(image_path):
                    img_path = os.path.join(img_dir, image_path)
                else:
                    img_path = image_path
                
                if os.path.exists(img_path):
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            if img_path.lower().endswith('.svg'):
                                mime_type = "image/svg+xml"
                            elif img_path.lower().endswith('.png'):
                                mime_type = "image/png"
                            elif img_path.lower().endswith(('.jpg', '.jpeg')):
                                mime_type = "image/jpeg"
                            else:
                                mime_type = "image/png"
                            return ft.Image(
                                src_base64=img_data,
                                width=24,
                                height=24,
                                fit=ft.ImageFit.CONTAIN,
                            )
                    except:
                        return ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
        
        # 미니맵 라디오 버튼 그룹
        preset_minimap_radio_group = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Radio(
                                value=key,
                            ),
                            create_preset_minimap_image_widget(key),
                            ft.Text(key, size=12),
                            ft.Container(expand=True),  # 공간 채우기
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="수정",
                                on_click=lambda e, k=key: show_edit_minimap_from_preset(k, "add_preset"),
                            ),
                        ],
                        spacing=10,
                        expand=True,
                    )
                    for key in minimap_keys
                ] if minimap_keys else [ft.Text("미니맵이 없습니다.", color=ft.Colors.GREY_600)],
                spacing=5,
            ),
            value=None,
        )
        
        # 메뉴 데이터 로드
        menu_items = load_menu()
        
        # 메뉴 체크박스 리스트
        menu_checkboxes = []
        for idx, menu_item in enumerate(menu_items):
            if isinstance(menu_item, dict):
                menu_text = menu_item.get("텍스트", f"메뉴 {idx}")
                menu_icon = menu_item.get("아이콘", "")
                
                # 메뉴 아이콘 위젯 생성
                menu_icon_widget = None
                if menu_icon:
                    img_path = os.path.join(img_dir, menu_icon)
                    if os.path.exists(img_path):
                        try:
                            with open(img_path, 'rb') as img_file:
                                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                                if img_path.lower().endswith('.svg'):
                                    mime_type = "image/svg+xml"
                                elif img_path.lower().endswith('.png'):
                                    mime_type = "image/png"
                                elif img_path.lower().endswith(('.jpg', '.jpeg')):
                                    mime_type = "image/jpeg"
                                else:
                                    mime_type = "image/png"
                                menu_icon_widget = ft.Image(
                                    src_base64=img_data,
                                    width=24,
                                    height=24,
                                    fit=ft.ImageFit.CONTAIN,
                                )
                        except:
                            menu_icon_widget = ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
                
                if not menu_icon_widget:
                    menu_icon_widget = ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
                
                checkbox = ft.Checkbox(value=False)
                menu_checkboxes.append({
                    "index": idx,
                    "checkbox": checkbox,
                    "widget": ft.Row(
                        [
                            checkbox,
                            menu_icon_widget,
                            ft.Text(menu_text, size=12),
                            ft.Container(expand=True),  # 공간 채우기
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="수정",
                                on_click=lambda e, i=idx: show_edit_menu_from_preset(i, "add_preset"),
                            ),
                        ],
                        spacing=10,
                    ),
                })
        
        # 뒤로 가기 핸들러
        def go_back(e):
            show_settings_screen()
        
        # 저장 핸들러
        def save_new_preset(e):
            preset_name = new_preset_name_field.value.strip()
            if not preset_name:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("프리셋 이름을 입력하세요."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 기존 프리셋 데이터 로드
            preset_data = load_preset()
            if preset_name in preset_data:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("이미 존재하는 프리셋 이름입니다."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 선택된 미니맵
            selected_minimap = preset_minimap_radio_group.value if preset_minimap_radio_group.value else ""
            
            # 선택된 메뉴 인덱스
            selected_menu_indices = []
            for menu_checkbox_item in menu_checkboxes:
                if menu_checkbox_item["checkbox"].value:
                    selected_menu_indices.append(menu_checkbox_item["index"])
            
            # 프리셋 데이터 저장
            preset_data[preset_name] = {
                "미니맵": selected_minimap,
                "메뉴": selected_menu_indices,
            }
            
            # 현재 프리셋으로 설정
            preset_data["current"] = preset_name
            
            # 저장
            save_preset(preset_data)
            
            # 설정 화면으로 돌아가기
            show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("프리셋이 추가되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="새 프리셋 추가",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드들
                    new_preset_name_field,
                    ft.Text(
                        value="미니맵 선택:",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    preset_minimap_radio_group,
                    ft.ElevatedButton(
                        "새 미니맵 추가",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: show_add_minimap_from_preset("add_preset"),
                    ),
                    ft.Text(
                        value="메뉴 선택:",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Column(
                        [item["widget"] for item in menu_checkboxes] if menu_checkboxes else [ft.Text("메뉴가 없습니다.", color=ft.Colors.GREY_600)],
                        spacing=5,
                    ),
                    ft.ElevatedButton(
                        "새 메뉴 추가",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: show_add_menu_from_preset("add_preset"),
                    ),
                    # 저장 버튼
                    ft.ElevatedButton(
                        "저장",
                        icon=ft.Icons.SAVE,
                        on_click=save_new_preset,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    # 프리셋 수정 화면
    def get_edit_preset_content(preset_key):
        # 프리셋 데이터 로드
        preset_data = load_preset()
        if preset_key not in preset_data:
            show_settings_screen()
            return ft.Container()
        
        preset_info = preset_data[preset_key]
        
        # 프리셋 이름 입력 필드
        edit_preset_name_field = ft.TextField(
            label="프리셋 이름",
            value=preset_key,
            expand=True,
            autofocus=True,
        )
        
        # 미니맵 데이터 로드
        minimap_data = load_minimap()
        minimap_keys = list(minimap_data.keys()) if minimap_data else []
        
        # 선택된 미니맵
        selected_minimap = preset_info.get("미니맵", "")
        
        # 미니맵 이미지 위젯 생성 함수
        def create_edit_preset_minimap_image_widget(key):
            minimap_item = minimap_data.get(key, {})
            image_path = minimap_item.get("이미지", "")
            if image_path:
                if not os.path.isabs(image_path):
                    img_path = os.path.join(img_dir, image_path)
                else:
                    img_path = image_path
                
                if os.path.exists(img_path):
                    try:
                        with open(img_path, 'rb') as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            if img_path.lower().endswith('.svg'):
                                mime_type = "image/svg+xml"
                            elif img_path.lower().endswith('.png'):
                                mime_type = "image/png"
                            elif img_path.lower().endswith(('.jpg', '.jpeg')):
                                mime_type = "image/jpeg"
                            else:
                                mime_type = "image/png"
                            return ft.Image(
                                src_base64=img_data,
                                width=24,
                                height=24,
                                fit=ft.ImageFit.CONTAIN,
                            )
                    except:
                        return ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
            return ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
        
        # 미니맵 라디오 버튼 그룹
        edit_preset_minimap_radio_group = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Radio(
                                value=key,
                            ),
                            create_edit_preset_minimap_image_widget(key),
                            ft.Text(key, size=12),
                            ft.Container(expand=True),  # 공간 채우기
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="수정",
                                on_click=lambda e, k=key: show_edit_minimap_from_preset(k, "edit_preset", preset_key),
                            ),
                        ],
                        spacing=10,
                        expand=True,
                    )
                    for key in minimap_keys
                ] if minimap_keys else [ft.Text("미니맵이 없습니다.", color=ft.Colors.GREY_600)],
                spacing=5,
            ),
            value=selected_minimap if selected_minimap else None,
        )
        
        # 메뉴 데이터 로드
        menu_items = load_menu()
        selected_menu_indices = preset_info.get("메뉴", [])
        
        # 메뉴 체크박스 리스트
        menu_checkboxes = []
        for idx, menu_item in enumerate(menu_items):
            if isinstance(menu_item, dict):
                menu_text = menu_item.get("텍스트", f"메뉴 {idx}")
                menu_icon = menu_item.get("아이콘", "")
                
                # 메뉴 아이콘 위젯 생성
                menu_icon_widget = None
                if menu_icon:
                    img_path = os.path.join(img_dir, menu_icon)
                    if os.path.exists(img_path):
                        try:
                            with open(img_path, 'rb') as img_file:
                                img_data = base64.b64encode(img_file.read()).decode('utf-8')
                                if img_path.lower().endswith('.svg'):
                                    mime_type = "image/svg+xml"
                                elif img_path.lower().endswith('.png'):
                                    mime_type = "image/png"
                                elif img_path.lower().endswith(('.jpg', '.jpeg')):
                                    mime_type = "image/jpeg"
                                else:
                                    mime_type = "image/png"
                                menu_icon_widget = ft.Image(
                                    src_base64=img_data,
                                    width=24,
                                    height=24,
                                    fit=ft.ImageFit.CONTAIN,
                                )
                        except:
                            menu_icon_widget = ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
                
                if not menu_icon_widget:
                    menu_icon_widget = ft.Icon(ft.Icons.IMAGE, size=24, color=ft.Colors.GREY_400)
                
                checkbox = ft.Checkbox(value=idx in selected_menu_indices)
                menu_checkboxes.append({
                    "index": idx,
                    "checkbox": checkbox,
                    "widget": ft.Row(
                        [
                            checkbox,
                            menu_icon_widget,
                            ft.Text(menu_text, size=12),
                            ft.Container(expand=True),  # 공간 채우기
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=20,
                                tooltip="수정",
                                on_click=lambda e, i=idx: show_edit_menu_from_preset(i, "edit_preset", preset_key),
                            ),
                        ],
                        spacing=10,
                    ),
                })
        
        # 뒤로 가기 핸들러
        def go_back(e):
            show_settings_screen()
        
        # 저장 핸들러
        def save_edited_preset(e):
            new_preset_name = edit_preset_name_field.value.strip()
            if not new_preset_name:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("프리셋 이름을 입력하세요."),
                    action="OK",
                )
                page.snack_bar.open = True
                page.update()
                return
            
            # 기존 프리셋 데이터 로드
            preset_data = load_preset()
            
            # 키가 변경된 경우
            if new_preset_name != preset_key:
                # 기존 키가 이미 존재하는지 확인
                if new_preset_name in preset_data:
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text("이미 존재하는 프리셋 이름입니다."),
                        action="OK",
                    )
                    page.snack_bar.open = True
                    page.update()
                    return
                
                # 기존 키 삭제하고 새 키로 추가
                if preset_key in preset_data:
                    del preset_data[preset_key]
                
                # 현재 프리셋 업데이트
                if preset_data.get("current") == preset_key:
                    preset_data["current"] = new_preset_name
            
            # 선택된 미니맵
            selected_minimap = edit_preset_minimap_radio_group.value if edit_preset_minimap_radio_group.value else ""
            
            # 선택된 메뉴 인덱스
            selected_menu_indices = []
            for menu_checkbox_item in menu_checkboxes:
                if menu_checkbox_item["checkbox"].value:
                    selected_menu_indices.append(menu_checkbox_item["index"])
            
            # 프리셋 데이터 저장
            preset_data[new_preset_name] = {
                "미니맵": selected_minimap,
                "메뉴": selected_menu_indices,
            }
            
            # 저장
            save_preset(preset_data)
            
            # 설정 화면으로 돌아가기
            show_settings_screen()
            
            # 성공 메시지
            page.snack_bar = ft.SnackBar(
                content=ft.Text("프리셋이 수정되었습니다."),
                action="OK",
            )
            page.snack_bar.open = True
            page.update()
        
        content_widget = ft.Container(
            content=ft.Column(
                [
                    # 상단 헤더 (뒤로 가기 버튼)
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.ARROW_BACK,
                                on_click=go_back,
                                tooltip="뒤로 가기",
                            ),
                            ft.Text(
                                value="프리셋 수정",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        spacing=10,
                    ),
                    # 입력 필드들
                    edit_preset_name_field,
                    ft.Text(
                        value="미니맵 선택:",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    edit_preset_minimap_radio_group,
                    ft.ElevatedButton(
                        "새 미니맵 추가",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: show_add_minimap_from_preset("edit_preset", preset_key),
                    ),
                    ft.Text(
                        value="메뉴 선택:",
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Column(
                        [item["widget"] for item in menu_checkboxes] if menu_checkboxes else [ft.Text("메뉴가 없습니다.", color=ft.Colors.GREY_600)],
                        spacing=5,
                    ),
                    ft.ElevatedButton(
                        "새 메뉴 추가",
                        icon=ft.Icons.ADD,
                        on_click=lambda e: show_add_menu_from_preset("edit_preset", preset_key),
                    ),
                    # 저장 버튼
                    ft.ElevatedButton(
                        "저장",
                        icon=ft.Icons.SAVE,
                        on_click=save_edited_preset,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=20,
            expand=True,
        )
        return content_widget
    
    def show_add_minimap_screen():
        nonlocal current_screen
        current_screen = "add_minimap"
        main_content_container.content = get_add_minimap_content()
        nav_bar.visible = False
        page.update()
    
    def show_edit_minimap_screen(minimap_key):
        nonlocal current_screen
        current_screen = "edit_minimap"
        main_content_container.content = get_edit_minimap_content(minimap_key)
        nav_bar.visible = False
        page.update()
    
    def show_add_menu_screen():
        nonlocal current_screen
        current_screen = "add_menu"
        main_content_container.content = get_add_menu_content()
        nav_bar.visible = False
        page.update()
    
    def show_edit_menu_screen(menu_index):
        nonlocal current_screen
        current_screen = "edit_menu"
        main_content_container.content = get_edit_menu_content(menu_index)
        nav_bar.visible = False
        page.update()
    
    # 프리셋에서 미니맵 추가
    def show_add_minimap_from_preset(return_screen, preset_key=None):
        nonlocal current_screen
        current_screen = f"add_minimap_from_{return_screen}"
        if preset_key:
            main_content_container.content = get_add_minimap_content(return_screen, preset_key)
        else:
            main_content_container.content = get_add_minimap_content(return_screen)
        nav_bar.visible = False
        page.update()
    
    # 프리셋에서 미니맵 수정
    def show_edit_minimap_from_preset(minimap_key, return_screen, preset_key=None):
        nonlocal current_screen
        current_screen = f"edit_minimap_from_{return_screen}"
        if preset_key:
            main_content_container.content = get_edit_minimap_content(minimap_key, return_screen, preset_key)
        else:
            main_content_container.content = get_edit_minimap_content(minimap_key, return_screen)
        nav_bar.visible = False
        page.update()
    
    # 프리셋에서 메뉴 추가
    def show_add_menu_from_preset(return_screen, preset_key=None):
        nonlocal current_screen
        current_screen = f"add_menu_from_{return_screen}"
        if preset_key:
            main_content_container.content = get_add_menu_content(return_screen, preset_key)
        else:
            main_content_container.content = get_add_menu_content(return_screen)
        nav_bar.visible = False
        page.update()
    
    # 프리셋에서 메뉴 수정
    def show_edit_menu_from_preset(menu_index, return_screen, preset_key=None):
        nonlocal current_screen
        current_screen = f"edit_menu_from_{return_screen}"
        if preset_key:
            main_content_container.content = get_edit_menu_content(menu_index, return_screen, preset_key)
        else:
            main_content_container.content = get_edit_menu_content(menu_index, return_screen)
        nav_bar.visible = False
        page.update()
    
    def show_edit_profile_screen():
        nonlocal current_screen
        current_screen = "edit_profile"
        main_content_container.content = get_edit_profile_content()
        nav_bar.visible = False
        page.update()
    
    def show_add_profile_screen():
        nonlocal current_screen
        current_screen = "add_profile"
        main_content_container.content = get_add_profile_content()
        nav_bar.visible = False
        page.update()
    
    def show_add_preset_screen():
        nonlocal current_screen
        current_screen = "add_preset"
        main_content_container.content = get_add_preset_content()
        nav_bar.visible = False
        page.update()
    
    def show_edit_preset_screen(preset_key):
        nonlocal current_screen
        current_screen = "edit_preset"
        main_content_container.content = get_edit_preset_content(preset_key)
        nav_bar.visible = False
        page.update()
    
    # 프리셋 조합 로드 함수
    def load_preset_combination(preset_key):
        preset_data = load_preset()
        if preset_key not in preset_data:
            return
        
        preset_info = preset_data[preset_key]
        
        # 미니맵 선택
        selected_minimap = preset_info.get("미니맵", "")
        if selected_minimap:
            minimap_data = load_minimap()
            # 모든 미니맵의 "선택됨" 필드 제거
            for key in minimap_data.keys():
                if "선택됨" in minimap_data[key]:
                    del minimap_data[key]["선택됨"]
            # 선택된 미니맵에 "선택됨" 표시 추가
            if selected_minimap in minimap_data:
                minimap_data[selected_minimap]["선택됨"] = True
                save_minimap(minimap_data)
        
        # 메뉴 선택
        selected_menu_indices = preset_info.get("메뉴", [])
        if selected_menu_indices:
            menu_items = load_menu()
            # 모든 메뉴의 "사용" 필드 제거
            for menu_item in menu_items:
                if isinstance(menu_item, dict):
                    menu_item["사용"] = False
            # 선택된 메뉴에 "사용" 표시 추가
            for idx in selected_menu_indices:
                if 0 <= idx < len(menu_items):
                    if isinstance(menu_items[idx], dict):
                        menu_items[idx]["사용"] = True
            save_menu(menu_items)
    
    # 네비게이션 바 변경 핸들러
    def on_nav_change(e):
        nonlocal selected_index
        selected_index = e.control.selected_index
        
        # 탭에 따라 콘텐츠 변경
        if selected_index == 0:  # 홈
            show_home_screen()
        elif selected_index == 1:  # 설정
            show_settings_screen()
    
    # 네비게이션 바 생성
    nav_bar = ft.NavigationBar(
        selected_index=selected_index,
        on_change=on_nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.HOME,
                label="홈",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS,
                label="설정",
            ),
        ],
    )
    
    # 텍스트 필드 생성
    공지사항_field = ft.TextField(
        multiline=True,
        min_lines=3,
        max_lines=3,
        expand=True,
        value=공지사항_data.get("내용", ""),
        on_change=on_공지사항_change,
    )
    
    알림창_field = ft.TextField(
        multiline=True,
        min_lines=3,
        max_lines=3,
        expand=True,
        value=알림창_data.get("내용", ""),
        on_change=on_알림창_change,
    )
    
    # 초기 콘텐츠 설정 (홈 페이지)
    main_content_container.content = get_home_content()
    
    # 페이지 레이아웃 구성
    page.add(
        ft.Row(
            [
                main_content_container,
            ],
            expand=True,
        ),
        nav_bar,  # 네비게이션 바는 항상 하단에 고정
    )

ft.app(main)
