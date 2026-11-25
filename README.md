<h1>Wajeeha Phonon Transcribe</h1>

<p>A lightweight Windows GUI for offline speech-to-text transcription using Fermion Research's <strong>Phonon-2</strong>.</p>
<img width="614" height="608" alt="image" src="https://github.com/user-attachments/assets/a8a6cc6c-596a-40f9-be72-9eaa9b6dad29" />

<p>Wajeeha Phonon Transcribe is a simple desktop application that converts speech from audio files or microphone recordings into text. It provides an easy-to-use graphical interface, handles long recordings automatically, and saves the resulting transcript to a <code>.txt</code> file. The model runs locally — no internet needed after the initial setup.</p>

<h2>Features</h2>
<ul>
  <li><strong>Audio File Transcription:</strong> Browse and select <code>.wav</code>, <code>.flac</code>, <code>.ogg</code>, or <code>.aiff</code> files.</li>
  <li><strong>Microphone Recording:</strong> Record audio directly from your microphone.</li>
  <li><strong>Long Audio Support:</strong> Phonon-2 splits long files at pauses automatically — no length limit in the app.</li>
  <li><strong>Text Export:</strong> Save the generated transcript to a <code>.txt</code> file of your choice.</li>
  <li><strong>Offline Support:</strong> Model weights are stored locally next to the executable; transcription runs without an internet connection.</li>
  <li><strong>Simple GUI:</strong> Clean and intuitive Windows desktop interface.</li>
  <li><strong>Background Processing:</strong> Model setup and transcription run in background threads to keep the interface responsive.</li>
  <li><strong>Portable:</strong> The built folder can be copied to any Windows PC and run as-is.</li>
</ul>

<h2>How It Works</h2>
<p>Wajeeha Phonon Transcribe uses <strong>Fermion Research's Phonon-2</strong> as its speech-to-text engine.</p>
<p>The application follows this workflow:</p>
<ol>
  <li>Select an audio file or record audio using your microphone.</li>
  <li>Choose where to save the transcript.</li>
  <li>Click <strong>Run transcription</strong>.</li>
  <li>The application loads the audio and runs Phonon-2 in-process.</li>
  <li>Phonon-2 splits long recordings at natural pauses and transcribes each segment.</li>
  <li>The combined text is saved as a UTF-8 <code>.txt</code> file.</li>
</ol>
<p>On first launch, the app downloads the Phonon-2 weights (~164 MB) into a <code>models</code> folder next to the executable, so subsequent runs are fully offline.</p>

<h2>Requirements</h2>

<h3>System Requirements</h3>
<ul>
  <li>Windows 10 or Windows 11 (64-bit).</li>
  <li>Microphone (optional, only required for recording).</li>
  <li>Internet connection for the initial model download, unless the <code>models</code> folder is already present.</li>
  <li>Sufficient disk space for the application, the model (~164 MB), and the PyTorch dependencies.</li>
</ul>

<h3>Python Requirements</h3>
<p>If running from source, you need:</p>
<ul>
  <li>Python 3.10 or later (64-bit).</li>
  <li><code>pip</code> (Python package manager).</li>
</ul>
<p>The Python dependencies are listed in <code>requirements.txt</code>.</p>

<h2>Project Structure</h2>
<p>The project is organized as follows:</p>
<pre><code>Wajeeha-Phonon-Transcribe/
│
├── app.py                   # Main application and GUI
├── collect_args.py          # Prints PyInstaller --collect-all flags for fermion-research
├── requirements.txt         # Python dependencies
├── build.bat                # Windows build script
├── README.md                # Project documentation
│
├── models/                  # Phonon-2 weights (populated on first run)
│   └── hf/                  # Hugging Face cache used by the engine
│
├── WT.ico                   # Application icon
└── WT.png                   # Application icon (PNG fallback)
</code></pre>
<blockquote>
  <p><strong>Note:</strong> The <code>models</code> directory is created automatically on first run or during the build process. It contains the Phonon-2 weights and is required for offline operation.</p>
</blockquote>

<h2>Installation</h2>

<h3>Option 1: Run from Source</h3>
<ol>
  <li>Clone or download this repository.</li>
  <li>Open Command Prompt or PowerShell in the project directory.</li>
  <li>(Optional but recommended) Create a virtual environment:
    <pre><code>python -m venv venv</code></pre>
  </li>
  <li>Activate the virtual environment:
    <pre><code>venv\Scripts\activate</code></pre>
  </li>
  <li>Install the required dependencies:
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  <li>Run the application:
    <pre><code>python app.py</code></pre>
  </li>
</ol>
<p>On the first run, the application checks whether the Phonon-2 weights are present in <code>models/</code> next to the script.</p>
<ul>
  <li>If they are missing, it downloads them (~164 MB). An internet connection is required for this initial setup.</li>
  <li>Once downloaded, the weights are stored locally and transcription works offline.</li>
</ul>

<h3>Option 2: Build the Windows Executable</h3>
<p>The project includes a <code>build.bat</code> script to automate the Windows executable build process.</p>
<p>To build the application:</p>
<ol>
  <li>Make sure Python 3.10+ (64-bit) is installed and available in <code>PATH</code>.</li>
  <li>Open the project directory.</li>
  <li>Double-click <code>build.bat</code>, or execute it from Command Prompt:
    <pre><code>build.bat</code></pre>
  </li>
</ol>
<p>The build script automates the preparation of dependencies and packaging of the application into a Windows executable.</p>
<p>The application uses a PyInstaller-compatible frozen execution structure, allowing it to locate resources relative to the executable rather than relying on the current working directory.</p>
<p><strong>Build script responsibilities:</strong></p>
<ul>
  <li>Create a virtual environment and install the required Python dependencies.</li>
  <li>Discover the correct PyInstaller <code>--collect-all</code> flags for the <code>fermion-research</code> package via <code>collect_args.py</code>.</li>
  <li>Package the Python application into a Windows executable with <code>--onedir</code> (bundling PyTorch and the Phonon engine).</li>
  <li>Bundle icons (<code>WT.ico</code>, <code>WT.png</code>) and required native/data files.</li>
  <li>Download the Phonon-2 weights into the packaged folder via <code>python app.py --prepare dist\PhononTranscribe</code>.</li>
  <li>Copy the result into <code>PhononTranscribe_Package\</code> for distribution.</li>
</ul>
<p>The output is a self-contained folder: <code>PhononTranscribe_Package\</code> containing <code>PhononTranscribe.exe</code>, <code>_internal\</code> (libraries), and <code>models\</code> (Phonon-2 weights). Copy the whole folder to any Windows PC and run the executable — keep the folder together.</p>

<h2>Model Setup</h2>
<p>Wajeeha Phonon Transcribe requires one important component:</p>
<table>
  <thead>
    <tr><th>Component</th><th>Location</th><th>Purpose</th></tr>
  </thead>
  <tbody>
    <tr><td>Phonon-2 Weights</td><td><code>models/</code></td><td>Contains the speech recognition model weights (~164 MB) and the Hugging Face cache used by the engine.</td></tr>
  </tbody>
</table>

<h3>Automatic Setup</h3>
<p>On startup, the application checks for the model weights next to the executable (or script, when running from source).</p>
<ul>
  <li>If the weights are present, the application configures the engine and enables offline mode.</li>
  <li>If they are missing, it launches a background download that:
    <ol>
      <li>Sets <code>FERMION_CACHE_DIR</code> and <code>HF_HOME</code> to point inside <code>models/</code>.</li>
      <li>Triggers Phonon-2 to download its weights into that folder.</li>
      <li>Verifies the download and switches to offline mode for future runs.</li>
    </ol>
  </li>
</ul>
<p>The initial download is approximately <strong>164 MB</strong> and requires an internet connection.</p>

<h3>Offline Mode</h3>
<p>Once the model weights are present in the <code>models/</code> folder, transcription runs without an internet connection.</p>
<p>The application sets the following environment variables:</p>
<ul>
  <li><code>FERMION_CACHE_DIR</code>: Points to the local <code>models/</code> folder.</li>
  <li><code>HF_HOME</code>: Points to <code>models/hf</code> so Hugging Face downloads stay inside the portable folder.</li>
  <li><code>HF_HUB_OFFLINE=1</code>: Enables offline Hugging Face Hub operation when local weights are present.</li>
</ul>

<h2>Using the Application</h2>

<h3>1. Select an Audio File</h3>
<p>Click <strong>Browse</strong> next to the <strong>Audio file</strong> field and select a supported file.</p>
<p>The application supports:</p>
<ul>
  <li><code>.wav</code></li>
  <li><code>.flac</code></li>
  <li><code>.ogg</code></li>
  <li><code>.aiff</code> / <code>.aif</code></li>
</ul>
<p>Audio is internally converted to 16 kHz mono before being passed to Phonon-2.</p>
<blockquote>
  <p><strong>Note:</strong> <code>.mp3</code> and <code>.m4a</code> are not supported directly — convert them to <code>.wav</code> first.</p>
</blockquote>

<h3>2. Record Audio</h3>
<p>Alternatively, click <strong>● Record</strong> to capture audio from your microphone.</p>
<p>When finished, click <strong>■ Stop</strong>.</p>
<p>The recording is automatically saved in:</p>
<pre><code>Documents/
└── WajeehaTranscribe/
    └── recording_YYYYMMDD_HHMMSS.wav
</code></pre>
<p>The recorded audio is automatically selected as the input file.</p>

<h3>3. Choose the Output Location</h3>
<p>Click <strong>Browse</strong> next to <strong>Save transcript to</strong> and select the destination for the transcript.</p>
<p>The output is saved as a <code>.txt</code> file.</p>
<p>If no output path is specified automatically, select one before starting transcription.</p>

<h3>4. Run Transcription</h3>
<p>Click <strong>Run transcription</strong>.</p>
<p>The status panel displays the current operation, including:</p>
<ul>
  <li>Model setup progress (on first run)</li>
  <li>Engine loading (the first transcription can take 10–40 s)</li>
  <li>Transcription progress</li>
  <li>Completion status and a short preview</li>
  <li>Errors, if any</li>
</ul>
<p>When transcription finishes, the generated text is saved to the selected location.</p>

<h2>Audio Processing Details</h2>
<p>Phonon-2 handles long audio natively by splitting it at natural pauses, so the app does not impose a chunking limit.</p>
<table>
  <thead>
    <tr><th>Property</th><th>Value</th></tr>
  </thead>
  <tbody>
    <tr><td>Sample Rate</td><td>16,000 Hz</td></tr>
    <tr><td>Channels</td><td>Mono</td></tr>
    <tr><td>Internal Format</td><td>16-bit PCM WAV (for recordings)</td></tr>
    <tr><td>Long Audio Handling</td><td>Splits at pauses internally (no app-level limit)</td></tr>
  </tbody>
</table>

<h2>Dependencies</h2>
<p>The project uses the following Python libraries and components:</p>
<table>
  <thead>
    <tr><th>Dependency</th><th>Purpose</th></tr>
  </thead>
  <tbody>
    <tr><td><code>tkinter</code></td><td>Desktop graphical user interface</td></tr>
    <tr><td><code>fermion-research</code></td><td>Phonon-2 speech-to-text engine</td></tr>
    <tr><td><code>torch</code></td><td>Deep learning runtime used by Phonon-2</td></tr>
    <tr><td><code>safetensors</code></td><td>Model weight loading</td></tr>
    <tr><td><code>soundfile</code></td><td>Reading/writing audio files</td></tr>
    <tr><td><code>scipy</code></td><td>Signal processing used by the engine</td></tr>
    <tr><td><code>zstandard</code></td><td>Compression support</td></tr>
    <tr><td><code>sounddevice</code></td><td>Microphone recording</td></tr>
    <tr><td><code>numpy</code></td><td>Audio data processing</td></tr>
    <tr><td><code>pyinstaller</code></td><td>Packaging the application into a Windows executable</td></tr>
  </tbody>
</table>
<p>The exact dependency versions are maintained in <code>requirements.txt</code>.</p>
<p>Install them using:</p>
<pre><code>pip install -r requirements.txt</code></pre>
<p>Some dependencies (notably <code>torch</code>) are large; the first install and build may take a few minutes.</p>

<h2>Troubleshooting</h2>

<h3>Model Weights Not Found</h3>
<p><strong>Problem:</strong> The app reports that Phonon-2 weights are missing, or transcription fails on first run.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Check that the <code>models</code> folder exists next to the executable (or script) and contains the downloaded files.</li>
  <li>Ensure the app has permission to write to its directory.</li>
  <li>Connect to the internet and restart the app if the initial download is required.</li>
  <li>Delete a partial <code>models</code> folder and restart if a previous download was interrupted.</li>
</ul>

<h3>First Transcription Is Slow</h3>
<p><strong>Problem:</strong> The first transcription takes a long time.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>This is expected: the engine loads PyTorch and Phonon-2 into memory (10–40 s) on first use.</li>
  <li>Subsequent transcriptions in the same session are much faster.</li>
</ul>

<h3>Microphone Error</h3>
<p><strong>Problem:</strong> Recording cannot start.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Make sure a microphone is connected.</li>
  <li>Check Windows microphone privacy settings.</li>
  <li>Ensure the microphone is not exclusively occupied by another application.</li>
  <li>Verify that <code>sounddevice</code> is installed correctly.</li>
</ul>

<h3>Unsupported Audio Format</h3>
<p><strong>Problem:</strong> The application cannot open the selected file.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Use <code>.wav</code>, <code>.flac</code>, <code>.ogg</code>, or <code>.aiff</code>.</li>
  <li>Convert <code>.mp3</code> and <code>.m4a</code> to <code>.wav</code> first.</li>
</ul>

<h3>Transcription Fails</h3>
<p><strong>Problem:</strong> The transcription process fails or produces unexpected results.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Prefer clear recordings with minimal background noise.</li>
  <li>Ensure the model weights are present in <code>models/</code>.</li>
  <li>Check the status panel for the reported error.</li>
  <li>If the failure persists, rebuild with <code>build.bat</code> and check the console output during packaging.</li>
</ul>

<h3>No Speech Detected</h3>
<p><strong>Problem:</strong> The output file is empty or contains no recognized speech.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Ensure the recording contains audible speech.</li>
  <li>Check the microphone input level.</li>
  <li>Reduce background noise.</li>
  <li>Try recording again in a quieter environment.</li>
</ul>

<h3>Build Fails on PyInstaller</h3>
<p><strong>Problem:</strong> <code>build.bat</code> fails while collecting the <code>fermion-research</code> package or PyTorch.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Confirm Python 3.10+ (64-bit) is on <code>PATH</code>.</li>
  <li>Delete the <code>venv</code> folder and re-run <code>build.bat</code> for a clean install.</li>
  <li>Check that <code>collect_args.py</code> prints a non-empty <code>COLLECT</code> value; if not, verify the <code>fermion-research</code> package installed correctly.</li>
  <li>Make sure there is enough disk space for PyTorch and the packaged output.</li>
</ul>

<h2>Privacy</h2>
<p>Wajeeha Phonon Transcribe is designed to support local transcription.</p>
<p>After the model weights have been downloaded and stored locally, audio processing takes place entirely on your machine.</p>
<p>Microphone recordings are saved locally in the user's Documents folder, and transcripts are saved to the location selected by the user.</p>
<p>The only network activity is the one-time model download on first run (or when <code>models/</code> is missing).</p>

<h2>Limitations</h2>
<ul>
  <li>Input formats: <code>.wav</code>, <code>.flac</code>, <code>.ogg</code>, <code>.aiff</code>. Convert <code>.mp3</code>/<code>.m4a</code> to <code>.wav</code> first.</li>
  <li>Audio is internally converted to 16 kHz mono.</li>
  <li>Transcription is currently optimized for English.</li>
  <li>The first transcription in a session is slow while the engine loads.</li>
  <li>Transcription quality depends on recording clarity, background noise, and speech quality.</li>
  <li>Initial model setup requires internet access unless the <code>models</code> folder is already present.</li>
</ul>

<h2>License</h2>
<p>MIT</p>
<hr>
<p><strong>Wajeeha Phonon Transcribe</strong> — Simple, local, and convenient speech-to-text transcription for Windows.</p>
