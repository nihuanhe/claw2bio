# [Verbatim from the CRE 67-isolate reproduction pack sec 4.11. Changes vs the reproduction pack: header comment (ASCII English) + output CSV renamed to table9_sequencing_quality.csv. Inputs are the pseudonymized frozen CSVs.]
# -*- coding: utf-8 -*-
"""
Build the new Table 9_sequencing_quality (manuscript Supplemental Table S7;
response to reviewer Comment 1.5).

For every isolate in the analysis set (n = 67, after excluding the two
A. baumannii assemblies D2207137004 / D2207137062), list:
  - the isolate identifier used in the manuscript and in the GSA deposit
    (Assembly ID, D2207137xxx), plus the internal Patient_ID;
  - WGS-based species, sequence type, and carbapenemase gene;
  - assembly metrics: contig count, N50, total length, GC content,
    raw read pairs, raw bases, Q30 fraction, and estimated sequencing depth
    (raw bases / assembled genome size).

Single source of truth: clinical_data_CRE_67_patients.csv
"""
import csv, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = 'clinical_data_CRE_67_patients.csv'
EXCLUDE = {'D2207137004', 'D2207137062'}  # the two A. baumannii assemblies
OUT = 'table9_sequencing_quality.csv'

with open(SRC, encoding='utf-8-sig') as f:
    rows = [r for r in csv.DictReader(f) if r['Assembly'] and r['Assembly'] not in EXCLUDE]

out_rows = []
for r in rows:
    reads_m = float(r['samReadNum'])     # raw reads, in millions
    bases_gb = float(r['samBaseNum'])    # raw bases, in Gb
    total_len = float(r['Totallength'])  # assembled genome size (bp)
    depth = bases_gb * 1e9 / total_len if total_len else 0
    out_rows.append({
        'Isolate_ID': r['Assembly'],
        'Patient_ID': r['Patient_ID'],
        'Species': r['species.1'],
        'ST': 'ST' + r['ST'] if r['ST'].strip() not in ('-', '') else 'untypeable',
        'Carbapenemase': r['Bla_Carb_acquired'].strip().rstrip('^*'),
        'Contigs': r['contigs'],
        'N50_kb': f"{float(r['N50'])/1000:.1f}",
        'Total_length_Mb': f"{total_len/1e6:.2f}",
        'GC_pct': r['samGC'],
        'Raw_reads_M': f"{reads_m:.2f}",
        'Raw_bases_Gb': f"{bases_gb:.2f}",
        'Q30_pct': r['samQ30Total'],
        'Depth_x': f"{depth:.0f}",
    })

out_rows.sort(key=lambda x: int(x['Patient_ID']))
with open(OUT, 'w', newline='', encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)

n = len(out_rows)
depths = sorted(float(r['Depth_x']) for r in out_rows)
n50s = sorted(float(r['N50_kb']) for r in out_rows)
print(f"Saved: {OUT} (n = {n})")
print(f"Depth: {depths[0]:.0f}-{depths[-1]:.0f}x, median {depths[n//2]:.0f}x")
print(f"N50: {n50s[0]}-{n50s[-1]} kb, median {n50s[n//2]} kb")
print("First 3 rows:")
for r in out_rows[:3]:
    print(" ", r)
