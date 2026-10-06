"""Build the first-task report from observed firmware and original evidence."""
from pathlib import Path
from html import escape
from PIL import Image as PILImage
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, Image, Preformatted, PageBreak, NextPageTemplate,
)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STEM = '冯远钦_32501056106_电控第1次作业实验报告'
pdfmetrics.registerFont(TTFont('Song', r'C:\Windows\Fonts\simsun.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('Hei', r'C:\Windows\Fonts\simhei.ttf'))
pdfmetrics.registerFont(TTFont('Code', r'C:\Windows\Fonts\consola.ttf'))

PAGES = [
    {'title': '电控第一次作业实验报告', 'items': [
        ('meta', '姓名 冯远钦    学号 32501056106    日期 2026年10月6日'),
        ('p', '本实验在同一个 STM32CubeMX 工程中完成 GPIO 点灯、1 ms 定时器中断和独立看门狗复位。实测 PC13 板载灯点亮；喂狗时 tick 持续增长；停止喂狗后 tick 反复增长并归零。照片和调试截图集中放在附录。'),
        ('h', '一 实验环境与工程结构'),
        ('table', [
            ['项目', '配置'],
            ['开发板', 'STM32F103C6 最小系统板，32 KB Flash，10 KB RAM'],
            ['时钟', 'HSI 8 MHz；AHB、APB1 和 APB2 分频均为 1'],
            ['代码生成与构建', 'STM32CubeMX，CMake，Ninja，Arm GCC；Debug 构建'],
            ['调试', 'Ozone 3.26；DAPLink；USB；SWD；100 kHz'],
            ['外设', 'PC13 GPIO；TIM2 更新中断；IWDG 独立看门狗'],
        ]),
        ('p', '业务代码位于 Tasks/src/tasks.c，接口位于 Tasks/inc/tasks.h。根目录 CMakeLists.txt 使用《纳新环境配置》附录发放模板，只将项目名改为 first-task，user_folders 保持 "Tasks"。main.c 仅在 USER CODE 区域包含 tasks.h 并调用 Tasks_Init()；while (1) 保持为空。'),
        ('p', '三个实验使用同一份工程。定时器阶段与看门狗阶段分别编译、下载和截图；切换阶段时仅改变回调中的 HAL_IWDG_Refresh 调用，IWDG 配置始终保留。'),
        ('h', '二 GPIO 点灯'),
        ('p', 'PC13 配置为 GPIO_Output，GPIO mode 为 Output Push Pull，GPIO Pull-up/Pull-down 为 No pull-up and no pull-down，Maximum output speed 为 Low。Tasks_Init() 中写入低电平，点亮板载 PC13 灯。程序不在主循环中翻转引脚。'),
        ('code', 'HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);'),
        ('p', '实测结果：板载 PC13 指示灯点亮，照片见附录图1。'),
    ]},
    {'title': '三 定时器中断与持续计数', 'items': [
        ('p', 'TIM2 位于 APB1 总线。系统使用 HSI 8 MHz，AHB 与 APB1 分频均为 1，因此 PCLK1 = 8 MHz，TIM2 定时器时钟也为 8 MHz。本配置的 APB1 分频为 1，无需把 PCLK1 乘以 2。'),
        ('p', '设置 Prescaler（PSC）= 7，Counter Period（ARR）= 999，Counter Mode = Up，Clock Source = Internal Clock，并启用 TIM2 global interrupt。计数器时钟与更新周期计算如下。'),
        ('formula', '计数器时钟 = 8 000 000 / (7 + 1) = 1 000 000 Hz'),
        ('formula', '更新周期 = (7 + 1) * (999 + 1) / 8 000 000 = 0.001 s'),
        ('p', '因此，每 1 ms 产生一次更新中断，每秒约触发 1000 次。Tasks_Init() 启动中断模式定时器，全工程只在 Tasks 中实现一份更新回调。定时器阶段的业务代码如下。'),
        ('code', '''extern TIM_HandleTypeDef htim2;
extern IWDG_HandleTypeDef hiwdg;
volatile uint32_t tick = 0U;

void Tasks_Init(void)
{
    HAL_GPIO_WritePin(GPIOC, GPIO_PIN_13, GPIO_PIN_RESET);
    if (HAL_TIM_Base_Start_IT(&htim2) != HAL_OK)
    {
        Error_Handler();
    }
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM2)
    {
        ++tick;
        (void)HAL_IWDG_Refresh(&hiwdg);
    }
}'''),
        ('p', 'tick 定义为全局 volatile uint32_t。TIM2_IRQHandler() 调用 HAL_TIM_IRQHandler(&htim2)，由 HAL 分派到更新回调；计数不依赖 HAL_Delay 或主循环。每次中断同时喂狗，因此程序可持续运行。'),
        ('p', '实测结果：附录图2显示tick持续上升。10 s处约256 500，20 s处约266 500，增长速度约为(266 500 - 256 500) / (20 - 10) = 1000次/s，符合1 ms更新周期。截图中CPU保持运行。对应固件归档为firmware/first-task-timer-course.elf，调试加载build/first-task-timer.elf。'),
    ]},
    {'title': '四 独立看门狗与周期复位', 'items': [
        ('p', '保持 IWDG 启用，并保持原参数：IWDG counter clock prescaler = 64，IWDG down-counter reload value = 1249。F103 的 LSI 按约40 kHz计算，标称超时如下。'),
        ('formula', '超时 = (Reload + 1) * 分频 / LSI'),
        ('formula', '     = (1249 + 1) * 64 / 40 000 = 2 s'),
        ('p', '看门狗阶段仅注释同一更新回调中的喂狗调用；TIM2 仍每1 ms更新一次，tick仍每次自增1。当前提交的 Tasks/src/tasks.c 为这一阶段。'),
        ('code', '''void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
    if (htim->Instance == TIM2)
    {
        ++tick;
        // (void)HAL_IWDG_Refresh(&hiwdg);
    }
}'''),
        ('p', '使用发放CMake模板重新构建后，已重新下载当前build/first-task.elf。OpenOCD输出Verified OK，Programming exit code为0。随后使用Ozone 3.26加载该ELF，实测tick仍周期性增长并归零，与附录图3的实验现象一致。当前实测固件归档为firmware/first-task-watchdog-course.elf。'),
        ('p', '实测结果：tick反复从接近0增长到约1900～2000后归零，形成锯齿曲线，见附录图3。没有喂狗时，IWDG超时触发芯片复位，启动代码重新初始化全局变量，tick回到0。LSI频率存在偏差，因此实际超时与计数峰值不必恰好为2 s和2000。'),
        ('p', 'Ozone采用 Attach to Running Program 保持CPU运行。Timeline设置为 Clear Never，保留各次复位前的曲线。观察时状态为 CPU running 和 Connected @ 100 kHz，程序未停在断点。'),
        ('h', '五 构建与复现'),
        ('code', 'cmake --preset Debug\ncmake --build --preset Debug'),
        ('p', '在first-task根目录执行以上命令。Debug配置目录为build/Debug，按发放模板ELF输出为build/first-task.elf，HEX和BIN位于build/Debug。恢复定时器阶段时，取消HAL_IWDG_Refresh那一行的注释，再编译并下载。'),
        ('p', '烧录脚本为 debug/flash-daplink-watchdog.cmd。切换到Ozone前关闭OpenOCD，重新插拔DAPLink USB，保持开发板Micro-USB供电。Ozone通过 File > Open 打开 debug/first-task-ozone-326-watchdog.jdebug，随后选择 Debug > Start Debug Session > Attach to Running Program。'),
        ('p', '在 View > Watched Data 中添加 tick，右键选择 Graph，再打开 View > Timeline。实验说明与参数依据为《电控第一次作业》；实际参数以本工程源码和CubeMX配置为准。'),
    ]},
    {'title': '附录 GPIO 点灯照片', 'items': [
        ('p', '图1 PC13低电平点亮板载指示灯。'),
        ('image', ('gpio-pc13-led-on.jpg', 500)),
        ('caption', '板上标注 PC13 的绿色指示灯点亮。此照片记录GPIO实验现象。'),
    ]},
    {'title': '附录 定时器持续计数', 'landscape': True, 'items': [
        ('p', '图2 定时器阶段的tick Timeline。'),
        ('image', ('timer-course-tick-timeline.png', 390)),
        ('caption', '完整时间轴和纵轴显示tick持续增长，10 s处约256 500，20 s处约266 500，即约1000次/s。程序保持运行；此阶段在TIM2回调中调用HAL_IWDG_Refresh。'),
    ]},
    {'title': '附录 看门狗复位曲线', 'items': [
        ('p', '图3 看门狗阶段的tick Timeline。'),
        ('image', ('watchdog-tick-timeline.png', 560)),
        ('caption', 'tick反复上升到约1900～2000后归零。Clear Never保留多个复位周期，横轴为秒。此阶段回调中已注释喂狗调用。'),
    ]},
]

styles = {
    'title': ParagraphStyle('title', fontName='Hei', fontSize=19, leading=27, spaceAfter=14),
    'h': ParagraphStyle('h', fontName='Hei', fontSize=13, leading=20, spaceBefore=9, spaceAfter=7),
    'p': ParagraphStyle('p', fontName='Song', fontSize=10.5, leading=17, spaceAfter=8, wordWrap='CJK'),
    'meta': ParagraphStyle('meta', fontName='Song', fontSize=10.5, leading=17, spaceAfter=12),
    'caption': ParagraphStyle('caption', fontName='Song', fontSize=10, leading=16, spaceBefore=8, spaceAfter=6, wordWrap='CJK'),
    'formula': ParagraphStyle('formula', fontName='Song', fontSize=11, leading=19, leftIndent=12, spaceAfter=5),
    'cell': ParagraphStyle('cell', fontName='Song', fontSize=10, leading=15, wordWrap='CJK'),
    'code': ParagraphStyle('code', fontName='Code', fontSize=8.5, leading=11.2, spaceBefore=3, spaceAfter=9),
}

def footer(c, doc):
    width, height = c._pagesize
    c.saveState()
    c.setFillColor(colors.black)
    c.setFont('Song', 8.5)
    c.drawString(40, 23, '电控第一次作业  冯远钦')
    c.drawRightString(width-40, 23, f'{doc.page} / {len(PAGES)}')
    c.restoreState()

def make_pdf():
    output = HERE / f'{STEM}.pdf'
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=42, rightMargin=42,
                          topMargin=38, bottomMargin=40, title='电控第一次作业实验报告',
                          author='冯远钦', subject='STM32F103C6 GPIO TIM2 IWDG实验')
    templates = []
    for name, size in [('portrait', A4), ('landscape', landscape(A4))]:
        frame = Frame(42, 40, size[0]-84, size[1]-78, leftPadding=0, rightPadding=0,
                      topPadding=0, bottomPadding=0)
        templates.append(PageTemplate(id=name, frames=[frame], onPage=footer, pagesize=size))
    doc.addPageTemplates(templates)
    story=[]
    for page_index, page in enumerate(PAGES):
        if page_index:
            story.extend([NextPageTemplate('landscape' if page.get('landscape') else 'portrait'), PageBreak()])
        story.append(Paragraph(escape(page['title']), styles['title']))
        page_width = (landscape(A4) if page.get('landscape') else A4)[0]-84
        for kind, value in page['items']:
            if kind == 'code':
                story.append(Preformatted(value, styles['code']))
            elif kind == 'table':
                rows=[[Paragraph(escape(cell), styles['cell']) for cell in row] for row in value]
                table=Table(rows, colWidths=[118, page_width-118], hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0),(-1,0),colors.HexColor('#EEEEEE')),
                    ('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#D9D9D9')),
                    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                    ('LEFTPADDING',(0,0),(-1,-1),8), ('RIGHTPADDING',(0,0),(-1,-1),8),
                    ('TOPPADDING',(0,0),(-1,-1),7), ('BOTTOMPADDING',(0,0),(-1,-1),7),
                ]))
                story.extend([table, Spacer(1, 10)])
            elif kind == 'image':
                name, max_h = value
                path=ROOT / 'evidence' / name
                with PILImage.open(path) as im:
                    w,h=im.size
                scale=min(page_width/w, max_h/h)
                story.append(Image(str(path), width=w*scale, height=h*scale, hAlign='CENTER'))
            else:
                story.append(Paragraph(escape(value), styles[kind]))
    doc.build(story)
    print(output)

def make_html():
    css='''@page { size: A4; margin: 15mm; }
body { font-family: SimSun, serif; color: #000; max-width: 180mm; margin: auto; line-height: 1.65; }
h1,h2 { font-family: SimHei, sans-serif; font-weight: normal; color: #000; }
h1 { font-size: 21pt; } h2 { font-size: 15pt; }
section { break-after: page; padding: 7mm 0; } section:last-child { break-after: auto; }
p { font-size: 11pt; } table { border-collapse: collapse; width: 100%; }
td { border: 1px solid #d9d9d9; padding: 7px 10px; font-size: 10.5pt; } tr:first-child { background: #eee; }
pre { font-family: Consolas, monospace; font-size: 9pt; line-height: 1.35; white-space: pre-wrap; }
figure { margin: 12px 0; text-align: center; } img { max-width: 100%; max-height: 185mm; object-fit: contain; }
.caption { font-size: 10pt; } .formula { margin-left: 12px; }
'''
    parts=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>电控第一次作业实验报告</title><style>'+css+'</style><body>']
    for page in PAGES:
        parts.append('<section><h1>'+escape(page['title'])+'</h1>')
        for kind,value in page['items']:
            if kind=='table':
                parts.append('<table>'+''.join('<tr>'+''.join('<td>'+escape(x)+'</td>' for x in row)+'</tr>' for row in value)+'</table>')
            elif kind=='code':
                parts.append('<pre>'+escape(value)+'</pre>')
            elif kind=='h':
                parts.append('<h2>'+escape(value)+'</h2>')
            elif kind=='image':
                parts.append('<figure><img src="../evidence/'+escape(value[0])+'" alt="实验原始照片或Ozone截图"></figure>')
            else:
                parts.append('<p class="'+kind+'">'+escape(value)+'</p>')
        parts.append('</section>')
    parts.append('</body></html>')
    output=HERE / f'{STEM}.html'
    output.write_text('\n'.join(parts), encoding='utf-8')
    print(output)

if __name__ == '__main__':
    make_pdf()
    make_html()
