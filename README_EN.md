# Audio-Batch-Merger

**Audio-Batch-Merger** is a high-performance GUI utility designed for the automated batch processing of audio and video files. It serves as a comprehensive wrapper for the **FFmpeg** engine, ensuring lossless concatenation and high-quality upscaling for datasets.

Designed with a minimal "Tool Window" interface, it simplifies bulk audio editing workflows by offering native Drag-and-Drop support and automatic format normalization.

## Quick Start (For Users)

No Python installation or configuration is required. The executable comes bundled with the necessary FFmpeg engine.

1.  **Download**: Navigate to the [Releases](https://github.com/robinhood0107/drag_and_marge_audio/releases) page and download the latest `Audio-Batch-Merger.exe`.
2.  **Run**: Launch the executable. (Note: Since this is an unsigned application, Windows SmartScreen may appear. Click 'More info' -> 'Run anyway'.)
3.  **Usage**:
    * Set the **Batch Size** (Default: 20).
    * **Drag & Drop** files into the gray area, or **Click** the area to select files via Explorer.
    * Confirm the "Merge Preview" popup details.
    * Click **Start**.
4.  **Result**: Merged files will be saved in a new folder named `Merged_{SampleRate}Hz` located in the same directory as your source files.

## Key Features

- **Standalone Execution**: Runs instantly as a single `.exe` file with zero external dependencies.
- **Dynamic Sample Rate Analysis**: Automatically scans input metadata using `ffprobe`. Upscales the entire batch to match the highest detected sample rate (up to 24-bit PCM) to prevent quality loss.
- **Batch Segmentation**: Automatically segments large datasets into user-defined chunk sizes.
- **Lossless Concatenation**: Utilizes the FFmpeg `concat demuxer` protocol to merge streams without re-encoding.
- **Format Support**: Supports MP3, MP4, M4A, WAV, FLAC, AAC, OGG, WMA.

---

## Developer Guide (Build from Source)

If you wish to modify the source code or build the executable yourself, follow these steps.

### Prerequisites
- Python 3.8+
- FFmpeg & FFprobe binaries (Must be placed in the project root)

### Installation & Build

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/robinhood0107/drag_and_marge_audio.git](https://github.com/robinhood0107/drag_and_marge_audio.git)
    cd Audio-Batch-Merger
    ```

2.  **Install Dependencies**
    ```bash
    pip install tkinterdnd2 natsort pyinstaller
    ```

3.  **Build Executable**
    Ensure `ffmpeg.exe` and `ffprobe.exe` are in the project root directory, then run:
    ```bash
    pyinstaller --noconsole --onefile --collect-all tkinterdnd2 --add-binary "ffmpeg.exe;." --add-binary "ffprobe.exe;." drag_merge_simple.py
    ```

## License
MIT License