.PHONY: all metrics figures slides clean clean-generated

all: slides

metrics:
	./scripts/recompute_metrics.py \
		--random results_random.csv \
		--qr results_qr.csv \
		--contrived results_contrived.csv \
		--head2head results_head_to_head.csv \
		--out-csv slides/generated/metrics_summary.csv \
		--out-tex slides/generated/metrics_callouts.tex

figures:
	./scripts/prepare_figures.py --source-dir . --out-dir slides/figures

slides: metrics figures
	latexmk -pdf -interaction=nonstopmode -cd slides/main.tex

clean:
	latexmk -C -cd slides/main.tex || true
	rm -f slides/main.pdf

clean-generated:
	rm -f slides/generated/metrics_summary.csv slides/generated/metrics_callouts.tex
	rm -f slides/figures/*_crop_left.png slides/figures/*_crop_right.png slides/figures/*_focus.png
