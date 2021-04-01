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
TASK_COLORS = {"dijkstra": "ClrFill1",
               "fft": "ClrFill2",
               "prime": "ClrFill3",
               "sha": "ClrFill4",
               "susan": "ClrFill5",
               "test3": "ClrFill6",
               "tinyrenderer": "ClrFill7",
               "membench_rw_r_1M": "ClrFill8",
               "membench_rw_r_4M": "ClrFill9",
               }

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