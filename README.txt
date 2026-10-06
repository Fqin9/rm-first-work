电控第一次作业
作者：冯远钦
学号：32501056106
日期：2026年10月6日

开发板：STM32F103C6 最小系统板
调试：Ozone 3.26 + DAPLink，SWD，100 kHz

工程目录
first-task.ioc：STM32CubeMX 配置
Core、Drivers、cmake：CubeMX 生成代码与构建支持
Tasks/inc/tasks.h：业务代码接口
Tasks/src/tasks.c：GPIO 初始化与 TIM2 中断回调
firmware：定时器阶段与看门狗阶段已编译固件
debug：烧录脚本与 Ozone 调试工程
evidence：实验原始照片和截图
report：实验报告 PDF、可编辑 HTML、生成脚本及提交说明

构建
在工程根目录执行：
cmake --preset Debug
cmake --build --preset Debug
需要已安装并加入 PATH 的 CMake、Ninja 和 arm-none-eabi-gcc。
根目录 CMakeLists.txt 使用《纳新环境配置》附录发放模板，只将项目名改为 first-task。
user_folders 保持 Tasks。原模板与替换前文件备份在 cmake 目录中。
Debug 配置目录为 build/Debug，ELF 为 build/first-task.elf。
模板同时生成 build/Debug/first-task.hex 和 build/Debug/first-task.bin。

当前阶段
当前 Tasks/src/tasks.c 中 HAL_IWDG_Refresh 已注释，为看门狗实验。
恢复定时器实验时取消该行注释，重新编译并下载。
TIM2：8 MHz，PSC=7，ARR=999，周期1 ms。
IWDG：分频64，Reload=1249，LSI按40 kHz计算约2 s。
主循环保持为空；PC13低电平点亮板载灯。

调试
烧录前关闭 Ozone 与其他 OpenOCD；运行 debug/flash-daplink-watchdog.cmd。
该脚本下载当前 build/first-task.elf，请确保当前源码为所需的实验阶段。
下载完成后关闭脚本窗口，重新插拔 DAPLink USB，保持开发板供电。
Ozone 3.26 打开 debug/first-task-ozone-326-watchdog.jdebug。
使用 Debug > Start Debug Session > Attach to Running Program。
在 Watched Data 添加 tick，右键 Graph，打开 Timeline。
看门狗实验选择 Clear Never，保持 CPU running 观察周期性归零。

模板替换后的新 ELF 已重新下载并通过校验，Ozone 3.26 实测看门狗周期复位正常。
本次运行截图见 evidence/watchdog-course-ozone-running.png；烧录校验见 evidence/watchdog-course-flash-verified.png。
报告附录仅包含点灯照片、定时器曲线和看门狗曲线三张图片；本次完整运行窗口截图作为备查记录保留。

构建输出 build、报告排版检查图 report/qa 和调试日志由 .gitignore 排除。
提交时保留 Tasks、CubeMX 配置、构建配置、报告与实验截图。
报告见 report 目录；邮件提交要求见 report/使用说明.txt。

图2补拍
运行debug/flash-daplink-timer.cmd，校验成功后重新插拔DAPLink USB。
Ozone 3.26打开debug/first-task-ozone-326-timer.jdebug并Attach to Running Program。
该工程加载build/first-task-timer.elf，用于观察喂狗时tick持续增长。
源码和默认build/first-task.elf已恢复看门狗阶段；补拍后可用flash-daplink-watchdog.cmd恢复板上固件。
