rmdir .\badspinda2 /s /q

robocopy .\badspinda .\badspinda2 /s /e

powershell.exe -Command "Get-ChildItem .\badspinda2\*.png | Rename-Item -NewName {$_.Name -replace '_0x.+?$', '.png'}"

ffmpeg.exe -y -framerate 30 -i ".\badspinda2\frame%%04d.png" -vf scale="iw*10:ih*10" -c:v libx264 -sws_flags neighbor out.mp4

ffmpeg.exe -y -i .\out.mp4 -i .\badapple_crop.mp4 -filter_complex "[1:v]scale=128:-1[v2];[0:v][v2]overlay=main_w-overlay_w-5:5" -c:v libx264 -c:a copy out2.mp4