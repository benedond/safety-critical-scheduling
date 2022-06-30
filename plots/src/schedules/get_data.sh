
METHODS="ILP-SM-I BB-LR BB-SM HEUR ILP-IDLE-MIN ILP-IDLE-MAX QP-LR-UB"
INSTANCE=1

for m in $METHODS; do
    python ../../../tools/src/visualizer_latex/main.py --inp ../../../experiments/04_solvers_thermal_evaluation/solutions/imx8a/all/IN_$INSTANCE-$m.json --out $INSTANCE-$m.tex
done

