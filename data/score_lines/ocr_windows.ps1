# Windows 内置 OCR 引擎 — 中文识别
param([string]$ImagePath)

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Runtime.WindowsRuntime

$asTaskGeneric = ([System.Runtime.WindowsRuntimeSystemExtensions].GetMethods() | ? { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]

function Await($winrtTask, $resultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($resultType)
    $netTask = $asTask.Invoke($null, @($winrtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}

[Windows.Globalization.Language,Windows.Globalization,ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine,Windows.Media.Ocr,ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder,Windows.Graphics.Imaging,ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.RandomAccessStreamReference,Windows.Storage.Streams,ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.FileRandomAccessStream,Windows.Storage.Streams,ContentType=WindowsRuntime] | Out-Null

# Try Chinese, fallback to English
$lang = [Windows.Globalization.Language]::new("zh-Hans-CN")
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lang)
if (-not $engine) {
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
}

$file = Get-Item $ImagePath
$stream = [Windows.Storage.Streams.FileRandomAccessStream]::OpenAsync($file.FullName, [Windows.Storage.FileAccessMode]::Read)
$opStream = Await $stream ([Windows.Storage.Streams.IRandomAccessStream])

$decoder = [Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($opStream)
$opDecoder = Await $decoder ([Windows.Graphics.Imaging.BitmapDecoder])

$bitmap = [Windows.Graphics.Imaging.SoftwareBitmap]::Convert($opDecoder.GetSoftwareBitmapAsync().GetAwaiter().GetResult(), [Windows.Graphics.Imaging.BitmapPixelFormat]::Bgra8, [Windows.Graphics.Imaging.BitmapAlphaMode]::Straight)

$ocrResult = Await $engine.RecognizeAsync($bitmap) ([Windows.Media.Ocr.OcrResult])

foreach ($line in $ocrResult.Lines) {
    Write-Host $line.Text
}
