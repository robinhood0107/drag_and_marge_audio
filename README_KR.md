# Audio-Batch-Merger

**Audio-Batch-Merger**는 FFmpeg 엔진 기반의 고성능 오디오 일괄 처리 자동화 도구입니다. 복잡한 설치 과정 없이 클릭 한 번으로 대량의 오디오/비디오 데이터를 무손실로 병합하고 업스케일링할 수 있습니다.

이 프로그램은 직관적인 Drag-and-Drop 인터페이스를 제공하며, 데이터셋 전처리 및 대량 음성 편집 워크플로우를 획기적으로 단축시킵니다.

## 빠른 시작 (사용자용)

Python이나 FFmpeg를 별도로 설치할 필요가 없습니다. 모든 엔진이 실행 파일 하나에 내장되어 있습니다.

1.  **다운로드**: 상단 [Releases](https://github.com/robinhood0107/drag_and_marge_audio/releases) 탭에서 최신 `Audio-Batch-Merger.exe` 파일을 다운로드합니다.
2.  **실행**: 다운로드한 파일을 실행합니다. (서명되지 않은 앱 경고창이 뜰 경우 '추가 정보' -> '실행'을 클릭하세요.)
3.  **사용법**:
    * **Batch Size** (묶을 개수)를 설정합니다 (기본값: 20).
    * 회색 영역에 파일을 **드래그**하거나, 영역을 **클릭**하여 파일을 선택합니다.
    * "병합 미리보기(Merge Preview)" 팝업에서 정보를 확인하고 **시작**을 누릅니다.
4.  **결과 확인**: 원본 파일이 있는 위치에 `Merged_{SampleRate}Hz` 폴더가 생성되며 결과물이 저장됩니다.

## 주요 기능

- **Standalone 배포**: 별도의 환경 설정 없이 즉시 실행 가능한 단일 `.exe` 포맷입니다.
- **동적 샘플 레이트 분석**: 입력된 파일 중 가장 높은 음질(Sample Rate)을 자동으로 감지하고, 전체 배치를 해당 품질(최대 24-bit PCM)로 업스케일링하여 품질 저하를 막습니다.
- **배치 세그먼테이션**: 수백, 수천 개의 파일을 지정된 개수 단위로 자동 분할하여 병합합니다.
- **무손실 병합**: FFmpeg의 `concat demuxer` 프로토콜을 사용하여, 불필요한 재인코딩 없이 스트림을 복사합니다.
- **지원 포맷**: MP3, MP4, M4A, WAV, FLAC, AAC, OGG, WMA

---

## 개발자 가이드 (소스 빌드)

소스 코드를 수정하거나 직접 빌드하려면 아래 절차를 따르십시오.

### 요구 사항
- Python 3.8 이상
- FFmpeg & FFprobe 바이너리 (프로젝트 루트에 위치해야 함)

### 설치 및 빌드

1.  **레포지토리 클론**
    ```bash
    git clone [https://github.com/robinhood0107/drag_and_marge_audio.git](https://github.com/robinhood0107/drag_and_marge_audio.git)
    cd Audio-Batch-Merger
    ```

2.  **의존성 패키지 설치**
    ```bash
    pip install tkinterdnd2 natsort pyinstaller
    ```

3.  **실행 파일 빌드**
    프로젝트 폴더에 `ffmpeg.exe`와 `ffprobe.exe`가 있는지 확인한 후, 아래 명령어를 실행합니다:
    ```bash
    pyinstaller --noconsole --onefile --collect-all tkinterdnd2 --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." drag_merge_simple.py
    ```

## 라이선스
MIT License