# Different scales, executed for 10s per instance
/root/JSA/run_imx8.sh /root/JSA/power_experiment/demos_configurations/scale-1x/imx8a/all/ /root/JSA/power_experiment/measurements/scale-1x/imx8a/all/ imx8 60 Fan
/root/JSA/run_imx8.sh /root/JSA/power_experiment/demos_configurations/scale-1x/imx8a/cpu/ /root/JSA/power_experiment/measurements/scale-1x/imx8a/cpu/ imx8 60 Fan

# /root/JSA/run_imx8.sh /root/JSA/power_experiment/demos_configurations/scale-3x/imx8a/all/ /root/JSA/power_experiment/measurements/scale-3x/imx8a/all/ imx8 30 Fan
# /root/JSA/run_imx8.sh /root/JSA/power_experiment/demos_configurations/scale-3x/imx8a/cpu/ /root/JSA/power_experiment/measurements/scale-3x/imx8a/cpu/ imx8 30 Fan

# 30s per instance (should mitigate the warm-up effect, e.g., tinyrenderer)
# /root/JSA/run_imx8.sh /root/JSA/power_experiment/demos_configurations/scale-1x/imx8a/all/ /root/JSA/power_experiment/measurements/scale-1x/imx8a/all-30/ imx8 30 Fan
# /root/JSA/run_imx8.sh /root/JSA/power_experiment/demos_configurations/scale-1x/imx8a/cpu/ /root/JSA/power_experiment/measurements/scale-1x/imx8a/cpu-30/ imx8 30 Fan