电控第一次作业
作者：冯远钦
学号：32501056106

实验平台：STM32F103C6 最小系统板，Ozone 3.26 + DAPLink。
构建配置：使用《纳新环境配置》附录的 CMake 模板，Debug 构建。

实验内容
1. GPIO：PC13 输出低电平，点亮板载 LED。
2. 定时器：TIM2 每 1 ms 触发中断，tick 持续递增。
3. 看门狗：停止喂狗后约 2 s 复位，tick 周期性归零。
当前源码为看门狗实验阶段，主循环为空，业务代码位于 Tasks。

主要文件
first-task.ioc：CubeMX 配置。
CMakeLists.txt、cmake：构建配置。
Core、Drivers：初始化代码与驱动库。
Tasks：业务代码。
firmware、debug：各阶段固件、烧录脚本及调试工程。
evidence：实验照片与原始截图。
report：实验报告及其源文件。
