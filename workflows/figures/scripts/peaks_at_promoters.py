import os
import pandas
import pybedtools
import gffutils
from gffutils import pybedtools_integration

outdir = os.path.dirname(snakemake.output[0])
if not os.path.exists(outdir):
    os.makedirs(outdir)

# Based on the gffutils database, get each transcript's TSS, plus or minus 1 kb
db = gffutils.FeatureDB(snakemake.input.db)
tsses = (
    pybedtools_integration.tsses(db, as_bed6=True)
    .slop(l=1000, r=1000, s=True, genome='dm6')
    .saveas(os.path.join(outdir, 'tsses-slop.bed'))
)

df = []
for pk in snakemake.input.peaks:

    # Since each of the peaks files have the form '../run-name/peaks.bed', we
    # extract "run-name" from the path to use as the label
    label = os.path.basename(os.path.dirname(pk))

    p = pybedtools.BedTool(pk)

    # save the peaks found within a TSS to a separate file
    peaks_near_tsses = p.intersect(tsses).saveas(os.path.join(outdir, label + '.bed'))

    # Keep track of how many there were; this will be exported in the summary
    df.append(dict(label=label, npks=len(peaks_near_tsses)))

pandas.DataFrame(df)[['label', 'npks']].to_csv(snakemake.output[0], sep='\t', index=False)