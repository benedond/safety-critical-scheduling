import json
import click

# Define some constains used for the schedule creation:
MS_PER_CM = 225  # 1cm in the figure = MS_PER_CM milliseconds
Y_SCALE = 0.3  # height of a single core ~ 1cm * Y_SCALE
TASK_MARGIN_TOP_BOTTOM = 0.15
TASK_MARGIN_LEFT_RIGHT = 0
DRAW_TASK_NAMES = False
DRAW_TASK_IN_COLORS = True
DRAW_TASK_LEGEND = True
EXPORT_ONLY_TIKZ = True
MAJOR_FRAME_SYMBOL = "h" # symbol to describe the major frame length
WINDOW_SYMBOL = "w"

TASK_COLORS = {
        "a2time-4K": "TaskClrFill0",
        "a2time-4M": "TaskClrFill1",
        "aifirf-4K": "TaskClrFill2",
        "aifirf-4M": "TaskClrFill3",
        "bitmnp-4K": "TaskClrFill4",
        "bitmnp-4M": "TaskClrFill5",
        "canrdr-4K": "TaskClrFill6",
        "canrdr-4M": "TaskClrFill7",
        "idctrn-4K": "TaskClrFill8",
        "idctrn-4M": "TaskClrFill9",
        "iirflt-4K": "TaskClrFill10",
        "iirflt-4M": "TaskClrFill11",
        "matrix-4K": "TaskClrFill12",
        "matrix-4M": "TaskClrFill13",
        "membench-1K-RO-R": "TaskClrFill14",
        "membench-1K-RO-S": "TaskClrFill15",
        "membench-1K-RW-R": "TaskClrFill16",
        "membench-1K-RW-S": "TaskClrFill17",
        "membench-1M-RO-R": "TaskClrFill18",
        "membench-1M-RO-S": "TaskClrFill19",
        "membench-1M-RW-R": "TaskClrFill20",
        "membench-1M-RW-S": "TaskClrFill21",
        "membench-4M-RO-R": "TaskClrFill22",
        "membench-4M-RO-S": "TaskClrFill23",
        "membench-4M-RW-R": "TaskClrFill24",
        "membench-4M-RW-S": "TaskClrFill25",
        "pntrch-4K": "TaskClrFill26",
        "pntrch-4M": "TaskClrFill27",
        "puwmod-4K": "TaskClrFill28",
        "puwmod-4M": "TaskClrFill29",
        "rspeed-4K": "TaskClrFill30",
        "rspeed-4M": "TaskClrFill31",
        "tblook-4K": "TaskClrFill32",
        "tblook-4M": "TaskClrFill33",
        "tinyrenderer-boggie": "TaskClrFill34",
        "tinyrenderer-diablo": "TaskClrFill35",
        "ttsprk-4K": "TaskClrFill36",
        "ttsprk-4M": "TaskClrFill37"
}

#TASK_COLORS = {"dijkstra": "ClrFill1",
#               "fft": "ClrFill2",
#               "prime": "ClrFill3",
#               "sha": "ClrFill4",
#               "susan": "ClrFill5",
#               "test3": "ClrFill6",
#               "tinyrenderer": "ClrFill7",
#               "membench_rw_r_1M": "ClrFill8",
#               "membench_rw_r_4M": "ClrFill9",
#               }

def ms_to_cm(ms):
    """Convers milliseconds to centimeters"""
    return ms / MS_PER_CM

def get_core_offset(proc_unit, cluster):
    return proc_unit if cluster == "A53" else 4 + proc_unit  # Offset A72 by 4

@click.command()
@click.option('--inp', default="", help='Number of greetings.')
@click.option('--out', default="", help='Number of greetings.')
def run(inp, out):
    data = None
    if inp:
        data = json.load(open(inp))
    else:
        data = json.loads(input())

    result = []  # Array of strings to be joined in the end    
    if not EXPORT_ONLY_TIKZ:
        result.append(r'\documentclass{standalone}')
        result.append(r'\usepackage{tikz,pgfplots}')
        result.append(r'\usetikzlibrary{decorations.pathreplacing}')    
        result.append(r'\usepackage{siunitx}')
        # Define some colors
        result.append(r"\definecolor{ClrFill1}{HTML}{e6ebf9}")
        result.append(r"\definecolor{ClrFill2}{HTML}{b897c7}")
        result.append(r"\definecolor{ClrFill3}{HTML}{824c9a}")
        result.append(r"\definecolor{ClrFill4}{HTML}{4e79c3}")
        result.append(r"\definecolor{ClrFill5}{HTML}{57a3ab}")
        result.append(r"\definecolor{ClrFill6}{HTML}{7eb975}")
        result.append(r"\definecolor{ClrFill7}{HTML}{d0b541}")
        result.append(r"\definecolor{ClrFill8}{HTML}{e67f32}")
        result.append(r"\definecolor{ClrFill9}{HTML}{ce2123}")
        result.append(r"\definecolor{ClrFill10}{HTML}{531914}")
        result.append(r"\definecolor{TaskClrFill0}{HTML}{696969}")
        result.append(r"\definecolor{TaskClrFill1}{HTML}{556b2f}")
        result.append(r"\definecolor{TaskClrFill2}{HTML}{a0522d}")
        result.append(r"\definecolor{TaskClrFill3}{HTML}{7f0000}")
        result.append(r"\definecolor{TaskClrFill4}{HTML}{191970}")
        result.append(r"\definecolor{TaskClrFill5}{HTML}{808000}")
        result.append(r"\definecolor{TaskClrFill6}{HTML}{008000}")
        result.append(r"\definecolor{TaskClrFill7}{HTML}{3cb371}")
        result.append(r"\definecolor{TaskClrFill8}{HTML}{008080}")
        result.append(r"\definecolor{TaskClrFill9}{HTML}{4682b4}")
        result.append(r"\definecolor{TaskClrFill10}{HTML}{9acd32}")
        result.append(r"\definecolor{TaskClrFill11}{HTML}{00008b}")
        result.append(r"\definecolor{TaskClrFill12}{HTML}{32cd32}")
        result.append(r"\definecolor{TaskClrFill13}{HTML}{daa520}")
        result.append(r"\definecolor{TaskClrFill14}{HTML}{7f007f}")
        result.append(r"\definecolor{TaskClrFill15}{HTML}{b03060}")
        result.append(r"\definecolor{TaskClrFill16}{HTML}{d2b48c}")
        result.append(r"\definecolor{TaskClrFill17}{HTML}{ff0000}")
        result.append(r"\definecolor{TaskClrFill18}{HTML}{00ced1}")
        result.append(r"\definecolor{TaskClrFill19}{HTML}{ff8c00}")
        result.append(r"\definecolor{TaskClrFill20}{HTML}{6a5acd}")
        result.append(r"\definecolor{TaskClrFill21}{HTML}{0000cd}")
        result.append(r"\definecolor{TaskClrFill22}{HTML}{7cfc00}")
        result.append(r"\definecolor{TaskClrFill23}{HTML}{9400d3}")
        result.append(r"\definecolor{TaskClrFill24}{HTML}{ba55d3}")
        result.append(r"\definecolor{TaskClrFill25}{HTML}{00fa9a}")
        result.append(r"\definecolor{TaskClrFill26}{HTML}{dc143c}")
        result.append(r"\definecolor{TaskClrFill27}{HTML}{00bfff}")
        result.append(r"\definecolor{TaskClrFill28}{HTML}{f08080}")
        result.append(r"\definecolor{TaskClrFill29}{HTML}{ff7f50}")
        result.append(r"\definecolor{TaskClrFill30}{HTML}{ff00ff}")
        result.append(r"\definecolor{TaskClrFill31}{HTML}{1e90ff}")
        result.append(r"\definecolor{TaskClrFill32}{HTML}{f0e68c}")
        result.append(r"\definecolor{TaskClrFill33}{HTML}{ffff54}")
        result.append(r"\definecolor{TaskClrFill34}{HTML}{dda0dd}")
        result.append(r"\definecolor{TaskClrFill35}{HTML}{add8e6}")
        result.append(r"\definecolor{TaskClrFill36}{HTML}{ff1493}")
        result.append(r"\definecolor{TaskClrFill37}{HTML}{7fffd4}")
        result.append(r'\begin{document}')
    result.append('\\begin{{tikzpicture}}'.format(Y_SCALE))    
    result.extend(draw_image(data))  # Draw the figure in TikZ
    result.append(r'\end{tikzpicture}')
    
    if not EXPORT_ONLY_TIKZ:        
        result.append(r'\end{document}')
    
    result_string = '\n'.join(result)
    
    if out:
        with open(out, "w") as text_file:
            text_file.write(result_string)
    else:
        print(result_string)



def draw_image(data):
    fig = []
    MF = data["environment"]["majorFrameLength"]  

    fig.append('\\begin{{scope}}[yscale={:f}]'.format(Y_SCALE))
    # Draw the helping lines
    fig.append("\\draw[thick] (0,0) rectangle ({:f},6);".format(ms_to_cm(MF)))    
    # - horizontal lines - help between cores
    fig.append("\\foreach \\y in {{1,2,...,5}} {{\\draw[dotted] (0,\\y) -- ({:f},\\y);}}".format(ms_to_cm(MF)))
    # - A53/A72 desc
    fig.append(r"\draw [decorate,decoration={brace,amplitude=3pt},xshift=-4pt,yshift=0pt] (0,4.1) -- (0,5.9) node [black,midway,xshift=-0.5cm]  {\scriptsize A72};")
    fig.append(r"\draw [decorate,decoration={brace,amplitude=3pt},xshift=-4pt,yshift=0pt] (0,0.1) -- (0,3.9) node [black,midway,xshift=-0.5cm]  {\scriptsize A53};")

    # MF symbol
    # fig.append("\\node[anchor=north] at ({:f},0) {{\\scriptsize ${:s}$}};".format(ms_to_cm(MF), MAJOR_FRAME_SYMBOL))
    
    fig.append("")
    # Draw the tasks    
    cur_start = 0
    for window in data["solution"]["windows"]:        
        for task in window["tasks"]:
            cur_end = cur_start + task["length"]
            core_offset = get_core_offset(task["processingUnit"], task["processor"])
            task_class = task["task"][task["task"].find("_")+1:]
            task_len = task["length"]
            
            # Draw the task rectangle
            if DRAW_TASK_IN_COLORS:
                clr = "fill=" + TASK_COLORS[task_class]
            else:
                clr = ""
            fig.append("\\draw[{:s}] ({:f},{:f}) rectangle ({:f},{:f});".format(
                clr,
                ms_to_cm(cur_start + TASK_MARGIN_LEFT_RIGHT),
                core_offset+TASK_MARGIN_TOP_BOTTOM,
                ms_to_cm(cur_end - TASK_MARGIN_LEFT_RIGHT),
                core_offset+1-TASK_MARGIN_TOP_BOTTOM
            ))

            # Draw task name
            if DRAW_TASK_NAMES:
                fig.append("\\node[anchor=west] at ({:f},{:f}) {{\\tiny {:s}}};".format(
                    ms_to_cm(cur_start + TASK_MARGIN_LEFT_RIGHT),
                    core_offset + 0.5,
                    task["task"].replace("_", "\_")
                ))

        cur_start += window["length"]
    
    fig.append("")
    # Draw the windows
    cur_len = 0
    for window in data["solution"]["windows"]:
        cur_len += window["length"]
        fig.append("\\draw[dashed, red] ({0},0) rectangle ({0},6);".format(ms_to_cm(cur_len)))
        fig.append("\\node[anchor=north,font=\\tiny][red] at ({:f},0) {{ \\rotatebox{{90}}{{ {:.0f} }} }};".format(ms_to_cm(cur_len), cur_len))        

    fig.append(r'\end{scope}')

    # Draw legend
    if DRAW_TASK_LEGEND:
        fig.append(r"\begin{scope}[yshift=-0.75cm]")
        fig.append(r"\begin{axis}[%")
        fig.append("width={:f}cm,".format(ms_to_cm(MF)))
        fig.append(r"height=1cm,")
        fig.append(r"xmin=0,")
        fig.append(r"xmax=10,")
        fig.append(r"ymin=0,")
        fig.append(r"ymax=10,")
        fig.append(r"legend columns=5,")
        fig.append(r"scale only axis,")
        fig.append(r"hide axis,")
        fig.append(r"legend style={legend cell align=left, at={(0.5,0.0)},anchor=north, font=\footnotesize},")
        fig.append(r"]")

        task_set = set([t["task"].split("_")[1] for w in data["solution"]["windows"] for t in w["tasks"]])
        for t in TASK_COLORS.keys():
            if t in task_set:
                fig.append("\\addlegendimage{{ {:s},mark=square*, only marks}}".format(TASK_COLORS[t]))
                fig.append("\\addlegendentry{{ {:s} }};".format(t))
        
        fig.append(r"\end{axis}")
        fig.append(r"\end{scope}")

    return fig

if __name__=="__main__":
    run()
