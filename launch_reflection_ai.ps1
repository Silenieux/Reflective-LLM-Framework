# launch_reflection_ai.ps1
# Launches the LLaMA server and allows querying symbolic reflection via RAG

# --- Configuration ---
$llamaDir = "C:\users\scrambles\llama.cpp\build\bin\release"
$modelPath = "C:\users\scrambles\llama.cpp\models\MythoMax-L2-13B.Q4_K_M.gguf"
$pythonScript = "D:/LLM_Memory/symbolic_rag_prototype.py"
$ragOutputPath = "D:/LLM_Memory/rag_output.txt"

# --- Validate paths ---
if (!(Test-Path $llamaDir) -or !(Test-Path $modelPath) -or !(Test-Path $pythonScript)) {
    Write-Host "[!] One or more required paths not found:"
    if (!(Test-Path $llamaDir)) { Write-Host "  ✗ LLaMA dir: $llamaDir" }
    if (!(Test-Path $modelPath)) { Write-Host "  ✗ Model: $modelPath" }
    if (!(Test-Path $pythonScript)) { Write-Host "  ✗ Python Script: $pythonScript" }
    Start-Sleep -Seconds 10
    exit
}

# --- Ask for reflection query ---
$ragQuery = Read-Host "Enter symbolic query for reflection"
$ragResult = python $pythonScript $ragQuery

# --- Write result to disk ---
$ragResult | Out-File -FilePath $ragOutputPath -Encoding UTF8

# --- Display the result ---
Write-Host "`n[Injected Context]:"
Get-Content $ragOutputPath

# --- Launch LLaMA Server ---
try {
    Set-Location $llamaDir
    .\llama-server.exe --model "$modelPath" -c 4096 --port 8080 |
        Tee-Object -FilePath "D:/LLM_Memory/logs/llama_session_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').txt"
}
catch {
    Write-Host "`n[!] An error occurred: $($_.Exception.Message)"
}
finally {
    Write-Host "`n[~] Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
