# -*- coding: utf-8 -*-
"""
One-time patch for bcgTree 1.2.1 (bioconda) running with newer Gblocks:
classic Gblocks writes "<gene>.aln-gb", patched builds write
"<gene>.aln-gb.fa" directly. bcgTree.pm (run_muscle_and_gblocks) reads the
bare name and dies with "Fasta::Parser::new: ... No such file or directory".

Fix: read whichever file exists, and write the cleaned output via a temp
file so the input is never clobbered.

Run inside WSL Ubuntu:  python3 patch_bcgtree_gblocks.py

[改自 CRE 67-isolate 实战复现包 §8.3.2，仅改动：PM 由"手改第 15 行"
 改为 环境变量 PM 优先 → 自动探测 ~/miniconda3|anaconda3/envs/*/lib/；
 补丁体（old/new 两段 Perl 替换）逐字未动]
"""
import glob, os, sys

PM = os.environ.get("PM", "").strip()
if not PM:
    hits = (glob.glob(os.path.expanduser("~/miniconda3/envs/*/lib/bcgTree.pm")) +
            glob.glob(os.path.expanduser("~/anaconda3/envs/*/lib/bcgTree.pm")))
    if len(hits) != 1:
        sys.exit(f"ERROR: expected exactly 1 bcgTree.pm, found {hits}. "
                 "Re-run with PM=/path/to/envs/<env>/lib/bcgTree.pm")
    PM = hits[0]
print(f"patching: {PM}")

src = open(PM, encoding='utf-8').read()

old = '''		my $seqIn = Fasta::Parser->new(file => "$out/$gene.aln-gb", mode => "<");
		my $seqOut = Fasta::Parser->new(file => "$out/$gene.aln-gb.fa", mode => ">");'''

new = '''		# patched 2026-09-05 (CRE 67-isolate study): accept both Gblocks output
		# namings (bare ".aln-gb" from classic Gblocks, ".aln-gb.fa" from
		# patched builds); write the cleaned file via a temp name.
		my $gb_in = (-f "$out/$gene.aln-gb") ? "$out/$gene.aln-gb" : "$out/$gene.aln-gb.fa";
		my $seqIn = Fasta::Parser->new(file => $gb_in, mode => "<");
		my $seqOut = Fasta::Parser->new(file => "$out/$gene.aln-gb.fa.tmp", mode => ">");'''

if new in src:
    sys.exit('already patched — nothing to do')   # idempotent guard (added)
assert src.count(old) == 1, 'pattern not found or not unique'
src = src.replace(old, new)

old2 = '''			$seqOut->append_seq($seq);
		}
	}
	$L->info("Finished muscle and Gblocks.");'''

new2 = '''			$seqOut->append_seq($seq);
		}
		rename("$out/$gene.aln-gb.fa.tmp", "$out/$gene.aln-gb.fa");   # patched 2026-09-05
	}
	$L->info("Finished muscle and Gblocks.");'''

assert src.count(old2) == 1, 'second pattern not found or not unique'
src = src.replace(old2, new2)

open(PM, 'w', encoding='utf-8', newline='\n').write(src)
print('bcgTree.pm patched OK')
