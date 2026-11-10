# Build a shim with zig. Usage: build-shim2.ps1 <shim-dir>
param([Parameter(Mandatory=$true)][string]$ShimDir)
$ErrorActionPreference = "Stop"
$Root = "E:\dsh\ios-sweet-port"
$Zig = "$Root\zig-windows-x86_64-0.13.0\zig.exe"
$Shim = $ShimDir
$Out = "$Shim\out"

$env:ZIG_LOCAL_CACHE_DIR = "$Root\zig-cache"
$env:ZIG_GLOBAL_CACHE_DIR = "$Root\zig-cache"

New-Item -ItemType Directory -Force -Path $Out | Out-Null

$srcs = @("start.S", "shim.c", "console.c", "mmu.c", "fdt.c", "loader.c", "ufs.c", "stubs.c")
foreach ($f in $srcs) {
    $base = [System.IO.Path]::GetFileNameWithoutExtension($f)
    $src = "$Shim\$f"
    $o = "$Out\$base.o"
    $args = @("-target","aarch64-freestanding-none","-mcpu=cortex_a76","-ffreestanding","-nostdlib","-fno-pic","-mgeneral-regs-only","-mstrict-align","-fno-stack-protector","-Wall","-Wextra","-c",$src,"-o",$o)
    & $Zig cc @args 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) { throw "compile failed: $f" }
}
Write-Host "compiled all objects"

$objs = @("start","shim","console","mmu","fdt","loader","ufs","stubs") | ForEach-Object { "$Out\$_.o" }
$ldargs = @("-target","aarch64-freestanding-none","-mcpu=cortex_a76","-nostdlib","-fno-pic","-Wl,--build-id=none","-Wl,-T,$Shim\shim.ld") + $objs + @("-o","$Out\shim.elf")
& $Zig cc @ldargs 2>&1 | ForEach-Object { Write-Host $_ }
if ($LASTEXITCODE -ne 0) { throw "link failed" }

python "$Root\elf2bin.py" "$Out\shim.elf" "$Out\Image"
if ($LASTEXITCODE -ne 0) { throw "elf2bin failed" }

Write-Host "=== BUILD OK: $Shim ==="
Get-Item "$Out\Image" | ForEach-Object { "{0}  {1} bytes" -f $_.Name, $_.Length }
