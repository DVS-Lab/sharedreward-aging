# Run Record: sub144-restored-contrasts-L1-L2

- Timestamp: 20260915-091946
- Branch: main
- Commit: e7b77eb
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260915-091946_sub144-restored-contrasts-L1-L2.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: corrected sub-144 activation and provisional VS PPI, including subject-level outputs.

## Command

```bash
/ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/recover_sub144_analysis.py --run-models 
```

## Log

```text
RUN START: 20260915-091946
PROJECT_ROOT: /ZPOOL/data/projects/sharedreward-aging
GIT: main e7b77eb
HOST: CLA19787.tu.temple.edu
USER: tug87422
PWD: /ZPOOL/data/projects/sharedreward-aging
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python code/recover_sub144_analysis.py --run-models 

COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/build_event_qc_manifest.py --output /ZPOOL/data/projects/sharedreward-aging/logs/runlists/fulltrial-event-qc-ready.tsv --missing-output /ZPOOL/data/projects/sharedreward-aging/logs/runlists/fulltrial-event-qc-missing.tsv
Ready event-QC units: 765
Incomplete event-QC units: 2
Ready manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/fulltrial-event-qc-ready.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/fulltrial-event-qc-missing.tsv
INCOMPLETE rf1 sub-11450 ses-01 run-2: missing_source_events
INCOMPLETE rf1 sub-12037 ses-01 run-2: missing_source_events
SOURCE GAPS RECORDED: missing event sources remain excluded from the ready manifest.
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/run_event_qc_batch.py --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/fulltrial-event-qc-ready.tsv --overwrite --jobs 4 --log-dir /ZPOOL/data/projects/sharedreward-aging/logs/events-sub144-recovery
Event-QC plan: 765 unit(s), jobs=4, overwrite=true
Per-unit logs: /ZPOOL/data/projects/sharedreward-aging/logs/events-sub144-recovery
COMPLETED: ds003745_sub-104_ses-none_run-01
COMPLETED: ds003745_sub-105_ses-none_run-02
COMPLETED: ds003745_sub-104_ses-none_run-02
COMPLETED: ds003745_sub-105_ses-none_run-01
COMPLETED: ds003745_sub-106_ses-none_run-01
COMPLETED: ds003745_sub-106_ses-none_run-02
COMPLETED: ds003745_sub-107_ses-none_run-01
COMPLETED: ds003745_sub-107_ses-none_run-02
COMPLETED: ds003745_sub-108_ses-none_run-01
COMPLETED: ds003745_sub-108_ses-none_run-02
COMPLETED: ds003745_sub-109_ses-none_run-01
COMPLETED: ds003745_sub-109_ses-none_run-02
COMPLETED: ds003745_sub-110_ses-none_run-01
COMPLETED: ds003745_sub-111_ses-none_run-01
COMPLETED: ds003745_sub-110_ses-none_run-02
COMPLETED: ds003745_sub-111_ses-none_run-02
COMPLETED: ds003745_sub-112_ses-none_run-01
COMPLETED: ds003745_sub-113_ses-none_run-01
COMPLETED: ds003745_sub-112_ses-none_run-02
COMPLETED: ds003745_sub-113_ses-none_run-02
COMPLETED: ds003745_sub-115_ses-none_run-02
COMPLETED: ds003745_sub-115_ses-none_run-01
COMPLETED: ds003745_sub-116_ses-none_run-01
COMPLETED: ds003745_sub-116_ses-none_run-02
COMPLETED: ds003745_sub-118_ses-none_run-01
COMPLETED: ds003745_sub-117_ses-none_run-02
COMPLETED: ds003745_sub-117_ses-none_run-01
COMPLETED: ds003745_sub-118_ses-none_run-02
COMPLETED: ds003745_sub-120_ses-none_run-01
COMPLETED: ds003745_sub-121_ses-none_run-01
COMPLETED: ds003745_sub-120_ses-none_run-02
COMPLETED: ds003745_sub-121_ses-none_run-02
COMPLETED: ds003745_sub-122_ses-none_run-01
COMPLETED: ds003745_sub-122_ses-none_run-02
COMPLETED: ds003745_sub-124_ses-none_run-02
COMPLETED: ds003745_sub-124_ses-none_run-01
COMPLETED: ds003745_sub-125_ses-none_run-01
COMPLETED: ds003745_sub-125_ses-none_run-02
COMPLETED: ds003745_sub-126_ses-none_run-01
COMPLETED: ds003745_sub-126_ses-none_run-02
COMPLETED: ds003745_sub-127_ses-none_run-01
COMPLETED: ds003745_sub-127_ses-none_run-02
COMPLETED: ds003745_sub-128_ses-none_run-01
COMPLETED: ds003745_sub-128_ses-none_run-02
COMPLETED: ds003745_sub-129_ses-none_run-01
COMPLETED: ds003745_sub-130_ses-none_run-01
COMPLETED: ds003745_sub-129_ses-none_run-02
COMPLETED: ds003745_sub-130_ses-none_run-02
COMPLETED: ds003745_sub-131_ses-none_run-01
COMPLETED: ds003745_sub-131_ses-none_run-02
COMPLETED: ds003745_sub-132_ses-none_run-01
COMPLETED: ds003745_sub-133_ses-none_run-01
COMPLETED: ds003745_sub-132_ses-none_run-02
COMPLETED: ds003745_sub-134_ses-none_run-01
COMPLETED: ds003745_sub-133_ses-none_run-02
COMPLETED: ds003745_sub-134_ses-none_run-02
COMPLETED: ds003745_sub-135_ses-none_run-01
COMPLETED: ds003745_sub-136_ses-none_run-01
COMPLETED: ds003745_sub-135_ses-none_run-02
COMPLETED: ds003745_sub-136_ses-none_run-02
COMPLETED: ds003745_sub-137_ses-none_run-01
COMPLETED: ds003745_sub-137_ses-none_run-02
COMPLETED: ds003745_sub-138_ses-none_run-01
COMPLETED: ds003745_sub-140_ses-none_run-01
COMPLETED: ds003745_sub-140_ses-none_run-02
COMPLETED: ds003745_sub-138_ses-none_run-02
COMPLETED: ds003745_sub-141_ses-none_run-01
COMPLETED: ds003745_sub-141_ses-none_run-02
COMPLETED: ds003745_sub-142_ses-none_run-01
COMPLETED: ds003745_sub-142_ses-none_run-02
COMPLETED: ds003745_sub-143_ses-none_run-01
COMPLETED: ds003745_sub-144_ses-none_run-01
COMPLETED: ds003745_sub-143_ses-none_run-02
COMPLETED: ds003745_sub-145_ses-none_run-01
COMPLETED: ds003745_sub-144_ses-none_run-02
COMPLETED: ds003745_sub-147_ses-none_run-01
COMPLETED: ds003745_sub-145_ses-none_run-02
COMPLETED: ds003745_sub-147_ses-none_run-02
COMPLETED: ds003745_sub-149_ses-none_run-01
COMPLETED: ds003745_sub-149_ses-none_run-02
COMPLETED: ds003745_sub-150_ses-none_run-01
COMPLETED: ds003745_sub-150_ses-none_run-02
COMPLETED: ds003745_sub-151_ses-none_run-01
COMPLETED: ds003745_sub-151_ses-none_run-02
COMPLETED: ds003745_sub-152_ses-none_run-02
COMPLETED: ds003745_sub-152_ses-none_run-01
COMPLETED: ds003745_sub-153_ses-none_run-02
COMPLETED: ds003745_sub-154_ses-none_run-01
COMPLETED: ds003745_sub-153_ses-none_run-01
COMPLETED: ds003745_sub-154_ses-none_run-02
COMPLETED: ds003745_sub-155_ses-none_run-01
COMPLETED: ds003745_sub-155_ses-none_run-02
COMPLETED: ds003745_sub-156_ses-none_run-01
COMPLETED: ds003745_sub-157_ses-none_run-01
COMPLETED: ds003745_sub-156_ses-none_run-02
COMPLETED: ds003745_sub-157_ses-none_run-02
COMPLETED: ds003745_sub-158_ses-none_run-02
COMPLETED: ds003745_sub-158_ses-none_run-01
COMPLETED: ds003745_sub-159_ses-none_run-02
COMPLETED: ds003745_sub-159_ses-none_run-01
COMPLETED: rf1_sub-10317_ses-01_run-1
COMPLETED: rf1_sub-10369_ses-01_run-1
COMPLETED: rf1_sub-10317_ses-01_run-2
COMPLETED: rf1_sub-10369_ses-01_run-2
COMPLETED: rf1_sub-10402_ses-01_run-2
COMPLETED: rf1_sub-10402_ses-01_run-1
COMPLETED: rf1_sub-10418_ses-01_run-1
COMPLETED: rf1_sub-10462_ses-01_run-1
COMPLETED: rf1_sub-10418_ses-01_run-2
COMPLETED: rf1_sub-10478_ses-01_run-1
COMPLETED: rf1_sub-10486_ses-01_run-1
COMPLETED: rf1_sub-10529_ses-01_run-1
COMPLETED: rf1_sub-10478_ses-01_run-2
COMPLETED: rf1_sub-10486_ses-01_run-2
COMPLETED: rf1_sub-10529_ses-01_run-2
COMPLETED: rf1_sub-10541_ses-01_run-1
COMPLETED: rf1_sub-10541_ses-01_run-2
COMPLETED: rf1_sub-10559_ses-01_run-1
COMPLETED: rf1_sub-10559_ses-01_run-2
COMPLETED: rf1_sub-10572_ses-01_run-1
COMPLETED: rf1_sub-10572_ses-01_run-2
COMPLETED: rf1_sub-10581_ses-01_run-1
COMPLETED: rf1_sub-10581_ses-01_run-2
COMPLETED: rf1_sub-10584_ses-01_run-1
COMPLETED: rf1_sub-10585_ses-01_run-1
COMPLETED: rf1_sub-10585_ses-01_run-2
COMPLETED: rf1_sub-10589_ses-01_run-1
COMPLETED: rf1_sub-10589_ses-01_run-2
COMPLETED: rf1_sub-10590_ses-01_run-1
COMPLETED: rf1_sub-10590_ses-01_run-2
COMPLETED: rf1_sub-10596_ses-01_run-2
COMPLETED: rf1_sub-10596_ses-01_run-1
COMPLETED: rf1_sub-10603_ses-01_run-1
COMPLETED: rf1_sub-10606_ses-01_run-1
COMPLETED: rf1_sub-10608_ses-01_run-1
COMPLETED: rf1_sub-10606_ses-01_run-2
COMPLETED: rf1_sub-10608_ses-01_run-2
COMPLETED: rf1_sub-10617_ses-01_run-1
COMPLETED: rf1_sub-10636_ses-01_run-1
COMPLETED: rf1_sub-10636_ses-01_run-2
COMPLETED: rf1_sub-10638_ses-01_run-1
COMPLETED: rf1_sub-10638_ses-01_run-2
COMPLETED: rf1_sub-10640_ses-01_run-1
COMPLETED: rf1_sub-10640_ses-01_run-2
COMPLETED: rf1_sub-10641_ses-01_run-1
COMPLETED: rf1_sub-10642_ses-01_run-1
COMPLETED: rf1_sub-10642_ses-01_run-2
COMPLETED: rf1_sub-10644_ses-01_run-2
COMPLETED: rf1_sub-10644_ses-01_run-1
COMPLETED: rf1_sub-10647_ses-01_run-1
COMPLETED: rf1_sub-10649_ses-01_run-1
COMPLETED: rf1_sub-10647_ses-01_run-2
COMPLETED: rf1_sub-10649_ses-01_run-2
COMPLETED: rf1_sub-10652_ses-01_run-1
COMPLETED: rf1_sub-10652_ses-01_run-2
COMPLETED: rf1_sub-10656_ses-01_run-1
COMPLETED: rf1_sub-10656_ses-01_run-2
COMPLETED: rf1_sub-10657_ses-01_run-1
COMPLETED: rf1_sub-10661_ses-01_run-1
COMPLETED: rf1_sub-10657_ses-01_run-2
COMPLETED: rf1_sub-10661_ses-01_run-2
COMPLETED: rf1_sub-10663_ses-01_run-1
COMPLETED: rf1_sub-10663_ses-01_run-2
COMPLETED: rf1_sub-10668_ses-01_run-1
COMPLETED: rf1_sub-10673_ses-01_run-2
COMPLETED: rf1_sub-10673_ses-01_run-1
COMPLETED: rf1_sub-10674_ses-01_run-1
COMPLETED: rf1_sub-10674_ses-01_run-2
COMPLETED: rf1_sub-10677_ses-01_run-1
COMPLETED: rf1_sub-10677_ses-01_run-2
COMPLETED: rf1_sub-10685_ses-01_run-1
COMPLETED: rf1_sub-10685_ses-01_run-2
COMPLETED: rf1_sub-10690_ses-01_run-2
COMPLETED: rf1_sub-10690_ses-01_run-1
COMPLETED: rf1_sub-10691_ses-01_run-2
COMPLETED: rf1_sub-10691_ses-01_run-1
COMPLETED: rf1_sub-10700_ses-01_run-1
COMPLETED: rf1_sub-10700_ses-01_run-2
COMPLETED: rf1_sub-10701_ses-01_run-1
COMPLETED: rf1_sub-10701_ses-01_run-2
COMPLETED: rf1_sub-10713_ses-01_run-1
COMPLETED: rf1_sub-10713_ses-01_run-2
COMPLETED: rf1_sub-10716_ses-01_run-1
COMPLETED: rf1_sub-10716_ses-01_run-2
COMPLETED: rf1_sub-10718_ses-01_run-2
COMPLETED: rf1_sub-10718_ses-01_run-1
COMPLETED: rf1_sub-10723_ses-01_run-1
COMPLETED: rf1_sub-10720_ses-01_run-1
COMPLETED: rf1_sub-10720_ses-01_run-2
COMPLETED: rf1_sub-10723_ses-01_run-2
COMPLETED: rf1_sub-10741_ses-01_run-1
COMPLETED: rf1_sub-10741_ses-01_run-2
COMPLETED: rf1_sub-10748_ses-01_run-1
COMPLETED: rf1_sub-10748_ses-01_run-2
COMPLETED: rf1_sub-10767_ses-01_run-1
COMPLETED: rf1_sub-10767_ses-01_run-2
COMPLETED: rf1_sub-10770_ses-01_run-1
COMPLETED: rf1_sub-10770_ses-01_run-2
COMPLETED: rf1_sub-10777_ses-01_run-1
COMPLETED: rf1_sub-10777_ses-01_run-2
COMPLETED: rf1_sub-10781_ses-01_run-1
COMPLETED: rf1_sub-10781_ses-01_run-2
COMPLETED: rf1_sub-10783_ses-01_run-1
COMPLETED: rf1_sub-10783_ses-01_run-2
COMPLETED: rf1_sub-10785_ses-01_run-1
COMPLETED: rf1_sub-10785_ses-01_run-2
COMPLETED: rf1_sub-10794_ses-01_run-1
COMPLETED: rf1_sub-10794_ses-01_run-2
COMPLETED: rf1_sub-10800_ses-01_run-1
COMPLETED: rf1_sub-10800_ses-01_run-2
COMPLETED: rf1_sub-10801_ses-01_run-2
COMPLETED: rf1_sub-10801_ses-01_run-1
COMPLETED: rf1_sub-10802_ses-01_run-1
COMPLETED: rf1_sub-10802_ses-01_run-2
COMPLETED: rf1_sub-10804_ses-01_run-1
COMPLETED: rf1_sub-10803_ses-01_run-1
COMPLETED: rf1_sub-10804_ses-01_run-2
COMPLETED: rf1_sub-10806_ses-01_run-1
COMPLETED: rf1_sub-10806_ses-01_run-2
COMPLETED: rf1_sub-10807_ses-01_run-2
COMPLETED: rf1_sub-10807_ses-01_run-1
COMPLETED: rf1_sub-10809_ses-01_run-1
COMPLETED: rf1_sub-10809_ses-01_run-2
COMPLETED: rf1_sub-10810_ses-01_run-1
COMPLETED: rf1_sub-10810_ses-01_run-2
COMPLETED: rf1_sub-10812_ses-01_run-1
COMPLETED: rf1_sub-10812_ses-01_run-2
COMPLETED: rf1_sub-10817_ses-01_run-2
COMPLETED: rf1_sub-10817_ses-01_run-1
COMPLETED: rf1_sub-10827_ses-01_run-1
COMPLETED: rf1_sub-10831_ses-01_run-2
COMPLETED: rf1_sub-10831_ses-01_run-1
COMPLETED: rf1_sub-10827_ses-01_run-2
COMPLETED: rf1_sub-10834_ses-01_run-1
COMPLETED: rf1_sub-10834_ses-01_run-2
COMPLETED: rf1_sub-10838_ses-01_run-2
COMPLETED: rf1_sub-10838_ses-01_run-1
COMPLETED: rf1_sub-10843_ses-01_run-2
COMPLETED: rf1_sub-10843_ses-01_run-1
COMPLETED: rf1_sub-10850_ses-01_run-1
COMPLETED: rf1_sub-10850_ses-01_run-2
COMPLETED: rf1_sub-10854_ses-01_run-2
COMPLETED: rf1_sub-10854_ses-01_run-1
COMPLETED: rf1_sub-10857_ses-01_run-1
COMPLETED: rf1_sub-10857_ses-01_run-2
COMPLETED: rf1_sub-10858_ses-01_run-1
COMPLETED: rf1_sub-10860_ses-01_run-2
COMPLETED: rf1_sub-10858_ses-01_run-2
COMPLETED: rf1_sub-10860_ses-01_run-1
COMPLETED: rf1_sub-10862_ses-01_run-1
COMPLETED: rf1_sub-10863_ses-01_run-1
COMPLETED: rf1_sub-10862_ses-01_run-2
COMPLETED: rf1_sub-10863_ses-01_run-2
COMPLETED: rf1_sub-10866_ses-01_run-1
COMPLETED: rf1_sub-10866_ses-01_run-2
COMPLETED: rf1_sub-10875_ses-01_run-1
COMPLETED: rf1_sub-10875_ses-01_run-2
COMPLETED: rf1_sub-10886_ses-01_run-1
COMPLETED: rf1_sub-10881_ses-01_run-1
COMPLETED: rf1_sub-10887_ses-01_run-2
COMPLETED: rf1_sub-10887_ses-01_run-1
COMPLETED: rf1_sub-10896_ses-01_run-1
COMPLETED: rf1_sub-10897_ses-01_run-1
COMPLETED: rf1_sub-10896_ses-01_run-2
COMPLETED: rf1_sub-10898_ses-01_run-1
COMPLETED: rf1_sub-10898_ses-01_run-2
COMPLETED: rf1_sub-10908_ses-01_run-1
COMPLETED: rf1_sub-10908_ses-01_run-2
COMPLETED: rf1_sub-10913_ses-01_run-1
COMPLETED: rf1_sub-10913_ses-01_run-2
COMPLETED: rf1_sub-10918_ses-01_run-2
COMPLETED: rf1_sub-10918_ses-01_run-1
COMPLETED: rf1_sub-10919_ses-01_run-1
COMPLETED: rf1_sub-10919_ses-01_run-2
COMPLETED: rf1_sub-10924_ses-01_run-1
COMPLETED: rf1_sub-10924_ses-01_run-2
COMPLETED: rf1_sub-10926_ses-01_run-1
COMPLETED: rf1_sub-10926_ses-01_run-2
COMPLETED: rf1_sub-10928_ses-01_run-1
COMPLETED: rf1_sub-10928_ses-01_run-2
COMPLETED: rf1_sub-10929_ses-01_run-1
COMPLETED: rf1_sub-10929_ses-01_run-2
COMPLETED: rf1_sub-10930_ses-01_run-1
COMPLETED: rf1_sub-10930_ses-01_run-2
COMPLETED: rf1_sub-10938_ses-01_run-1
COMPLETED: rf1_sub-10938_ses-01_run-2
COMPLETED: rf1_sub-10940_ses-01_run-1
COMPLETED: rf1_sub-10940_ses-01_run-2
COMPLETED: rf1_sub-10950_ses-01_run-1
COMPLETED: rf1_sub-10950_ses-01_run-2
COMPLETED: rf1_sub-10951_ses-01_run-1
COMPLETED: rf1_sub-10951_ses-01_run-2
COMPLETED: rf1_sub-10952_ses-01_run-2
COMPLETED: rf1_sub-10952_ses-01_run-1
COMPLETED: rf1_sub-10953_ses-01_run-1
COMPLETED: rf1_sub-10953_ses-01_run-2
COMPLETED: rf1_sub-10954_ses-01_run-1
COMPLETED: rf1_sub-10954_ses-01_run-2
COMPLETED: rf1_sub-10956_ses-01_run-1
COMPLETED: rf1_sub-10958_ses-01_run-1
COMPLETED: rf1_sub-10956_ses-01_run-2
COMPLETED: rf1_sub-10961_ses-01_run-1
COMPLETED: rf1_sub-10958_ses-01_run-2
COMPLETED: rf1_sub-10961_ses-01_run-2
COMPLETED: rf1_sub-10964_ses-01_run-1
COMPLETED: rf1_sub-10964_ses-01_run-2
COMPLETED: rf1_sub-10966_ses-01_run-1
COMPLETED: rf1_sub-10966_ses-01_run-2
COMPLETED: rf1_sub-10969_ses-01_run-1
COMPLETED: rf1_sub-10969_ses-01_run-2
COMPLETED: rf1_sub-10974_ses-01_run-1
COMPLETED: rf1_sub-10974_ses-01_run-2
COMPLETED: rf1_sub-10977_ses-01_run-1
COMPLETED: rf1_sub-10979_ses-01_run-1
COMPLETED: rf1_sub-10977_ses-01_run-2
COMPLETED: rf1_sub-10979_ses-01_run-2
COMPLETED: rf1_sub-10983_ses-01_run-2
COMPLETED: rf1_sub-10983_ses-01_run-1
COMPLETED: rf1_sub-10984_ses-01_run-1
COMPLETED: rf1_sub-10984_ses-01_run-2
COMPLETED: rf1_sub-10998_ses-01_run-1
COMPLETED: rf1_sub-10998_ses-01_run-2
COMPLETED: rf1_sub-11005_ses-01_run-1
COMPLETED: rf1_sub-11005_ses-01_run-2
COMPLETED: rf1_sub-11007_ses-01_run-1
COMPLETED: rf1_sub-11007_ses-01_run-2
COMPLETED: rf1_sub-11012_ses-01_run-1
COMPLETED: rf1_sub-11012_ses-01_run-2
COMPLETED: rf1_sub-11016_ses-01_run-1
COMPLETED: rf1_sub-11016_ses-01_run-2
COMPLETED: rf1_sub-11021_ses-01_run-1
COMPLETED: rf1_sub-11021_ses-01_run-2
COMPLETED: rf1_sub-11030_ses-01_run-1
COMPLETED: rf1_sub-11030_ses-01_run-2
COMPLETED: rf1_sub-11031_ses-01_run-1
COMPLETED: rf1_sub-11031_ses-01_run-2
COMPLETED: rf1_sub-11036_ses-01_run-1
COMPLETED: rf1_sub-11036_ses-01_run-2
COMPLETED: rf1_sub-11039_ses-01_run-1
COMPLETED: rf1_sub-11039_ses-01_run-2
COMPLETED: rf1_sub-11042_ses-01_run-1
COMPLETED: rf1_sub-11053_ses-01_run-1
COMPLETED: rf1_sub-11042_ses-01_run-2
COMPLETED: rf1_sub-11053_ses-01_run-2
COMPLETED: rf1_sub-11058_ses-01_run-1
COMPLETED: rf1_sub-11058_ses-01_run-2
COMPLETED: rf1_sub-11060_ses-01_run-1
COMPLETED: rf1_sub-11060_ses-01_run-2
COMPLETED: rf1_sub-11063_ses-01_run-1
COMPLETED: rf1_sub-11063_ses-01_run-2
COMPLETED: rf1_sub-11064_ses-01_run-1
COMPLETED: rf1_sub-11064_ses-01_run-2
COMPLETED: rf1_sub-11065_ses-01_run-1
COMPLETED: rf1_sub-11066_ses-01_run-1
COMPLETED: rf1_sub-11065_ses-01_run-2
COMPLETED: rf1_sub-11066_ses-01_run-2
COMPLETED: rf1_sub-11068_ses-01_run-1
COMPLETED: rf1_sub-11068_ses-01_run-2
COMPLETED: rf1_sub-11071_ses-01_run-2
COMPLETED: rf1_sub-11071_ses-01_run-1
COMPLETED: rf1_sub-11072_ses-01_run-1
COMPLETED: rf1_sub-11074_ses-01_run-1
COMPLETED: rf1_sub-11074_ses-01_run-2
COMPLETED: rf1_sub-11072_ses-01_run-2
COMPLETED: rf1_sub-11075_ses-01_run-1
COMPLETED: rf1_sub-11075_ses-01_run-2
COMPLETED: rf1_sub-11076_ses-01_run-1
COMPLETED: rf1_sub-11078_ses-01_run-2
COMPLETED: rf1_sub-11078_ses-01_run-1
COMPLETED: rf1_sub-11083_ses-01_run-1
COMPLETED: rf1_sub-11083_ses-01_run-2
COMPLETED: rf1_sub-11084_ses-01_run-2
COMPLETED: rf1_sub-11084_ses-01_run-1
COMPLETED: rf1_sub-11085_ses-01_run-1
COMPLETED: rf1_sub-11090_ses-01_run-1
COMPLETED: rf1_sub-11085_ses-01_run-2
COMPLETED: rf1_sub-11090_ses-01_run-2
COMPLETED: rf1_sub-11110_ses-01_run-1
COMPLETED: rf1_sub-11110_ses-01_run-2
COMPLETED: rf1_sub-11113_ses-01_run-1
COMPLETED: rf1_sub-11113_ses-01_run-2
COMPLETED: rf1_sub-11116_ses-01_run-2
COMPLETED: rf1_sub-11116_ses-01_run-1
COMPLETED: rf1_sub-11120_ses-01_run-1
COMPLETED: rf1_sub-11120_ses-01_run-2
COMPLETED: rf1_sub-11125_ses-01_run-2
COMPLETED: rf1_sub-11126_ses-01_run-1
COMPLETED: rf1_sub-11125_ses-01_run-1
COMPLETED: rf1_sub-11128_ses-01_run-1
COMPLETED: rf1_sub-11128_ses-01_run-2
COMPLETED: rf1_sub-11134_ses-01_run-1
COMPLETED: rf1_sub-11134_ses-01_run-2
COMPLETED: rf1_sub-11139_ses-01_run-1
COMPLETED: rf1_sub-11139_ses-01_run-2
COMPLETED: rf1_sub-11145_ses-01_run-1
COMPLETED: rf1_sub-11145_ses-01_run-2
COMPLETED: rf1_sub-11164_ses-01_run-1
COMPLETED: rf1_sub-11167_ses-01_run-1
COMPLETED: rf1_sub-11167_ses-01_run-2
COMPLETED: rf1_sub-11168_ses-01_run-1
COMPLETED: rf1_sub-11168_ses-01_run-2
COMPLETED: rf1_sub-11171_ses-01_run-1
COMPLETED: rf1_sub-11171_ses-01_run-2
COMPLETED: rf1_sub-11177_ses-01_run-1
COMPLETED: rf1_sub-11192_ses-01_run-1
COMPLETED: rf1_sub-11177_ses-01_run-2
COMPLETED: rf1_sub-11192_ses-01_run-2
COMPLETED: rf1_sub-11193_ses-01_run-2
COMPLETED: rf1_sub-11193_ses-01_run-1
COMPLETED: rf1_sub-11201_ses-01_run-1
COMPLETED: rf1_sub-11203_ses-01_run-1
COMPLETED: rf1_sub-11203_ses-01_run-2
COMPLETED: rf1_sub-11209_ses-01_run-1
COMPLETED: rf1_sub-11209_ses-01_run-2
COMPLETED: rf1_sub-11227_ses-01_run-2
COMPLETED: rf1_sub-11227_ses-01_run-1
COMPLETED: rf1_sub-11238_ses-01_run-2
COMPLETED: rf1_sub-11238_ses-01_run-1
COMPLETED: rf1_sub-11241_ses-01_run-2
COMPLETED: rf1_sub-11241_ses-01_run-1
COMPLETED: rf1_sub-11246_ses-01_run-1
COMPLETED: rf1_sub-11246_ses-01_run-2
COMPLETED: rf1_sub-11276_ses-01_run-2
COMPLETED: rf1_sub-11286_ses-01_run-1
COMPLETED: rf1_sub-11276_ses-01_run-1
COMPLETED: rf1_sub-11301_ses-01_run-1
COMPLETED: rf1_sub-11311_ses-01_run-2
COMPLETED: rf1_sub-11311_ses-01_run-1
COMPLETED: rf1_sub-11301_ses-01_run-2
COMPLETED: rf1_sub-11312_ses-01_run-1
COMPLETED: rf1_sub-11312_ses-01_run-2
COMPLETED: rf1_sub-11316_ses-01_run-2
COMPLETED: rf1_sub-11316_ses-01_run-1
COMPLETED: rf1_sub-11318_ses-01_run-1
COMPLETED: rf1_sub-11318_ses-01_run-2
COMPLETED: rf1_sub-11321_ses-01_run-2
COMPLETED: rf1_sub-11321_ses-01_run-1
COMPLETED: rf1_sub-11325_ses-01_run-1
COMPLETED: rf1_sub-11325_ses-01_run-2
COMPLETED: rf1_sub-11326_ses-01_run-2
COMPLETED: rf1_sub-11326_ses-01_run-1
COMPLETED: rf1_sub-11329_ses-01_run-1
COMPLETED: rf1_sub-11329_ses-01_run-2
COMPLETED: rf1_sub-11330_ses-01_run-1
COMPLETED: rf1_sub-11330_ses-01_run-2
COMPLETED: rf1_sub-11337_ses-01_run-1
COMPLETED: rf1_sub-11338_ses-01_run-2
COMPLETED: rf1_sub-11337_ses-01_run-2
COMPLETED: rf1_sub-11338_ses-01_run-1
COMPLETED: rf1_sub-11340_ses-01_run-1
COMPLETED: rf1_sub-11343_ses-01_run-1
COMPLETED: rf1_sub-11340_ses-01_run-2
COMPLETED: rf1_sub-11343_ses-01_run-2
COMPLETED: rf1_sub-11345_ses-01_run-1
COMPLETED: rf1_sub-11348_ses-01_run-1
COMPLETED: rf1_sub-11345_ses-01_run-2
COMPLETED: rf1_sub-11348_ses-01_run-2
COMPLETED: rf1_sub-11364_ses-01_run-1
COMPLETED: rf1_sub-11358_ses-01_run-1
COMPLETED: rf1_sub-11358_ses-01_run-2
COMPLETED: rf1_sub-11364_ses-01_run-2
COMPLETED: rf1_sub-11367_ses-01_run-1
COMPLETED: rf1_sub-11374_ses-01_run-1
COMPLETED: rf1_sub-11367_ses-01_run-2
COMPLETED: rf1_sub-11374_ses-01_run-2
COMPLETED: rf1_sub-11377_ses-01_run-1
COMPLETED: rf1_sub-11376_ses-01_run-1
COMPLETED: rf1_sub-11376_ses-01_run-2
COMPLETED: rf1_sub-11377_ses-01_run-2
COMPLETED: rf1_sub-11387_ses-01_run-2
COMPLETED: rf1_sub-11387_ses-01_run-1
COMPLETED: rf1_sub-11410_ses-01_run-1
COMPLETED: rf1_sub-11410_ses-01_run-2
COMPLETED: rf1_sub-11416_ses-01_run-1
COMPLETED: rf1_sub-11426_ses-01_run-1
COMPLETED: rf1_sub-11430_ses-01_run-1
COMPLETED: rf1_sub-11432_ses-01_run-1
COMPLETED: rf1_sub-11432_ses-01_run-2
COMPLETED: rf1_sub-11433_ses-01_run-1
COMPLETED: rf1_sub-11433_ses-01_run-2
COMPLETED: rf1_sub-11435_ses-01_run-2
COMPLETED: rf1_sub-11435_ses-01_run-1
COMPLETED: rf1_sub-11439_ses-01_run-1
COMPLETED: rf1_sub-11440_ses-01_run-1
COMPLETED: rf1_sub-11440_ses-01_run-2
COMPLETED: rf1_sub-11443_ses-01_run-1
COMPLETED: rf1_sub-11450_ses-01_run-1
COMPLETED: rf1_sub-11451_ses-01_run-1
COMPLETED: rf1_sub-11461_ses-01_run-1
COMPLETED: rf1_sub-11451_ses-01_run-2
COMPLETED: rf1_sub-11462_ses-01_run-1
COMPLETED: rf1_sub-11461_ses-01_run-2
COMPLETED: rf1_sub-11472_ses-01_run-2
COMPLETED: rf1_sub-11472_ses-01_run-1
COMPLETED: rf1_sub-11492_ses-01_run-1
COMPLETED: rf1_sub-11492_ses-01_run-2
COMPLETED: rf1_sub-11493_ses-01_run-1
COMPLETED: rf1_sub-11493_ses-01_run-2
COMPLETED: rf1_sub-11498_ses-01_run-1
COMPLETED: rf1_sub-11517_ses-01_run-1
COMPLETED: rf1_sub-11517_ses-01_run-2
COMPLETED: rf1_sub-11518_ses-01_run-1
COMPLETED: rf1_sub-11518_ses-01_run-2
COMPLETED: rf1_sub-11523_ses-01_run-1
COMPLETED: rf1_sub-11523_ses-01_run-2
COMPLETED: rf1_sub-11526_ses-01_run-2
COMPLETED: rf1_sub-11526_ses-01_run-1
COMPLETED: rf1_sub-11527_ses-01_run-1
COMPLETED: rf1_sub-11527_ses-01_run-2
COMPLETED: rf1_sub-11529_ses-01_run-1
COMPLETED: rf1_sub-11530_ses-01_run-1
COMPLETED: rf1_sub-11529_ses-01_run-2
COMPLETED: rf1_sub-11530_ses-01_run-2
COMPLETED: rf1_sub-11532_ses-01_run-1
COMPLETED: rf1_sub-11533_ses-01_run-1
COMPLETED: rf1_sub-11532_ses-01_run-2
COMPLETED: rf1_sub-11533_ses-01_run-2
COMPLETED: rf1_sub-11534_ses-01_run-1
COMPLETED: rf1_sub-11535_ses-01_run-1
COMPLETED: rf1_sub-11534_ses-01_run-2
COMPLETED: rf1_sub-11535_ses-01_run-2
COMPLETED: rf1_sub-11536_ses-01_run-1
COMPLETED: rf1_sub-11536_ses-01_run-2
COMPLETED: rf1_sub-11539_ses-01_run-1
COMPLETED: rf1_sub-11539_ses-01_run-2
COMPLETED: rf1_sub-11540_ses-01_run-1
COMPLETED: rf1_sub-11540_ses-01_run-2
COMPLETED: rf1_sub-11542_ses-01_run-2
COMPLETED: rf1_sub-11542_ses-01_run-1
COMPLETED: rf1_sub-11545_ses-01_run-2
COMPLETED: rf1_sub-11545_ses-01_run-1
COMPLETED: rf1_sub-11551_ses-01_run-1
COMPLETED: rf1_sub-11559_ses-01_run-1
COMPLETED: rf1_sub-11551_ses-01_run-2
COMPLETED: rf1_sub-11560_ses-01_run-1
COMPLETED: rf1_sub-11559_ses-01_run-2
COMPLETED: rf1_sub-11560_ses-01_run-2
COMPLETED: rf1_sub-11563_ses-01_run-2
COMPLETED: rf1_sub-11570_ses-01_run-2
COMPLETED: rf1_sub-11563_ses-01_run-1
COMPLETED: rf1_sub-11570_ses-01_run-1
COMPLETED: rf1_sub-11572_ses-01_run-1
COMPLETED: rf1_sub-11572_ses-01_run-2
COMPLETED: rf1_sub-11579_ses-01_run-1
COMPLETED: rf1_sub-11579_ses-01_run-2
COMPLETED: rf1_sub-11587_ses-01_run-1
COMPLETED: rf1_sub-11586_ses-01_run-1
COMPLETED: rf1_sub-11588_ses-01_run-2
COMPLETED: rf1_sub-11587_ses-01_run-2
COMPLETED: rf1_sub-11591_ses-01_run-1
COMPLETED: rf1_sub-11588_ses-01_run-1
COMPLETED: rf1_sub-11591_ses-01_run-2
COMPLETED: rf1_sub-11597_ses-01_run-2
COMPLETED: rf1_sub-11598_ses-01_run-1
COMPLETED: rf1_sub-11597_ses-01_run-1
COMPLETED: rf1_sub-11598_ses-01_run-2
COMPLETED: rf1_sub-11599_ses-01_run-1
COMPLETED: rf1_sub-11599_ses-01_run-2
COMPLETED: rf1_sub-11600_ses-01_run-1
COMPLETED: rf1_sub-11600_ses-01_run-2
COMPLETED: rf1_sub-11606_ses-01_run-1
COMPLETED: rf1_sub-11614_ses-01_run-1
COMPLETED: rf1_sub-11606_ses-01_run-2
COMPLETED: rf1_sub-11614_ses-01_run-2
COMPLETED: rf1_sub-11622_ses-01_run-1
COMPLETED: rf1_sub-11622_ses-01_run-2
COMPLETED: rf1_sub-11623_ses-01_run-1
COMPLETED: rf1_sub-11625_ses-01_run-1
COMPLETED: rf1_sub-11625_ses-01_run-2
COMPLETED: rf1_sub-11626_ses-01_run-1
COMPLETED: rf1_sub-11626_ses-01_run-2
COMPLETED: rf1_sub-11628_ses-01_run-1
COMPLETED: rf1_sub-11628_ses-01_run-2
COMPLETED: rf1_sub-11631_ses-01_run-1
COMPLETED: rf1_sub-11631_ses-01_run-2
COMPLETED: rf1_sub-11651_ses-01_run-1
COMPLETED: rf1_sub-11651_ses-01_run-2
COMPLETED: rf1_sub-11660_ses-01_run-2
COMPLETED: rf1_sub-11670_ses-01_run-1
COMPLETED: rf1_sub-11660_ses-01_run-1
COMPLETED: rf1_sub-11670_ses-01_run-2
COMPLETED: rf1_sub-11674_ses-01_run-1
COMPLETED: rf1_sub-11679_ses-01_run-2
COMPLETED: rf1_sub-11679_ses-01_run-1
COMPLETED: rf1_sub-11681_ses-01_run-1
COMPLETED: rf1_sub-11681_ses-01_run-2
COMPLETED: rf1_sub-11692_ses-01_run-2
COMPLETED: rf1_sub-11692_ses-01_run-1
COMPLETED: rf1_sub-11694_ses-01_run-1
COMPLETED: rf1_sub-11701_ses-01_run-1
COMPLETED: rf1_sub-11701_ses-01_run-2
COMPLETED: rf1_sub-11703_ses-01_run-2
COMPLETED: rf1_sub-11703_ses-01_run-1
COMPLETED: rf1_sub-11705_ses-01_run-1
COMPLETED: rf1_sub-11705_ses-01_run-2
COMPLETED: rf1_sub-11709_ses-01_run-1
COMPLETED: rf1_sub-11709_ses-01_run-2
COMPLETED: rf1_sub-11710_ses-01_run-2
COMPLETED: rf1_sub-11710_ses-01_run-1
COMPLETED: rf1_sub-11714_ses-01_run-1
COMPLETED: rf1_sub-11714_ses-01_run-2
COMPLETED: rf1_sub-11719_ses-01_run-1
COMPLETED: rf1_sub-11720_ses-01_run-2
COMPLETED: rf1_sub-11720_ses-01_run-1
COMPLETED: rf1_sub-11722_ses-01_run-1
COMPLETED: rf1_sub-11722_ses-01_run-2
COMPLETED: rf1_sub-11723_ses-01_run-1
COMPLETED: rf1_sub-11723_ses-01_run-2
COMPLETED: rf1_sub-11736_ses-01_run-1
COMPLETED: rf1_sub-11736_ses-01_run-2
COMPLETED: rf1_sub-11744_ses-01_run-1
COMPLETED: rf1_sub-11744_ses-01_run-2
COMPLETED: rf1_sub-11746_ses-01_run-1
COMPLETED: rf1_sub-11746_ses-01_run-2
COMPLETED: rf1_sub-11748_ses-01_run-2
COMPLETED: rf1_sub-11748_ses-01_run-1
COMPLETED: rf1_sub-11756_ses-01_run-1
COMPLETED: rf1_sub-11756_ses-01_run-2
COMPLETED: rf1_sub-11764_ses-01_run-1
COMPLETED: rf1_sub-11764_ses-01_run-2
COMPLETED: rf1_sub-11772_ses-01_run-1
COMPLETED: rf1_sub-11773_ses-01_run-1
COMPLETED: rf1_sub-11773_ses-01_run-2
COMPLETED: rf1_sub-11774_ses-01_run-2
COMPLETED: rf1_sub-11774_ses-01_run-1
COMPLETED: rf1_sub-11784_ses-01_run-2
COMPLETED: rf1_sub-11784_ses-01_run-1
COMPLETED: rf1_sub-11787_ses-01_run-1
COMPLETED: rf1_sub-11787_ses-01_run-2
COMPLETED: rf1_sub-11788_ses-01_run-1
COMPLETED: rf1_sub-11788_ses-01_run-2
COMPLETED: rf1_sub-11789_ses-01_run-1
COMPLETED: rf1_sub-11789_ses-01_run-2
COMPLETED: rf1_sub-11790_ses-01_run-2
COMPLETED: rf1_sub-11790_ses-01_run-1
COMPLETED: rf1_sub-11793_ses-01_run-1
COMPLETED: rf1_sub-11795_ses-01_run-1
COMPLETED: rf1_sub-11793_ses-01_run-2
COMPLETED: rf1_sub-11795_ses-01_run-2
COMPLETED: rf1_sub-11815_ses-01_run-1
COMPLETED: rf1_sub-11815_ses-01_run-2
COMPLETED: rf1_sub-11822_ses-01_run-1
COMPLETED: rf1_sub-11822_ses-01_run-2
COMPLETED: rf1_sub-11823_ses-01_run-1
COMPLETED: rf1_sub-11823_ses-01_run-2
COMPLETED: rf1_sub-11824_ses-01_run-1
COMPLETED: rf1_sub-11828_ses-01_run-1
COMPLETED: rf1_sub-11824_ses-01_run-2
COMPLETED: rf1_sub-11829_ses-01_run-1
COMPLETED: rf1_sub-11828_ses-01_run-2
COMPLETED: rf1_sub-11829_ses-01_run-2
COMPLETED: rf1_sub-11840_ses-01_run-2
COMPLETED: rf1_sub-11840_ses-01_run-1
COMPLETED: rf1_sub-11847_ses-01_run-1
COMPLETED: rf1_sub-11847_ses-01_run-2
COMPLETED: rf1_sub-11853_ses-01_run-1
COMPLETED: rf1_sub-11853_ses-01_run-2
COMPLETED: rf1_sub-11854_ses-01_run-1
COMPLETED: rf1_sub-11861_ses-01_run-2
COMPLETED: rf1_sub-11854_ses-01_run-2
COMPLETED: rf1_sub-11861_ses-01_run-1
COMPLETED: rf1_sub-11866_ses-01_run-1
COMPLETED: rf1_sub-11866_ses-01_run-2
COMPLETED: rf1_sub-11867_ses-01_run-2
COMPLETED: rf1_sub-11867_ses-01_run-1
COMPLETED: rf1_sub-11870_ses-01_run-1
COMPLETED: rf1_sub-11872_ses-01_run-1
COMPLETED: rf1_sub-11870_ses-01_run-2
COMPLETED: rf1_sub-11872_ses-01_run-2
COMPLETED: rf1_sub-11876_ses-01_run-1
COMPLETED: rf1_sub-11877_ses-01_run-1
COMPLETED: rf1_sub-11876_ses-01_run-2
COMPLETED: rf1_sub-11877_ses-01_run-2
COMPLETED: rf1_sub-11881_ses-01_run-1
COMPLETED: rf1_sub-11881_ses-01_run-2
COMPLETED: rf1_sub-11885_ses-01_run-1
COMPLETED: rf1_sub-11885_ses-01_run-2
COMPLETED: rf1_sub-11891_ses-01_run-1
COMPLETED: rf1_sub-11897_ses-01_run-2
COMPLETED: rf1_sub-11897_ses-01_run-1
COMPLETED: rf1_sub-11891_ses-01_run-2
COMPLETED: rf1_sub-11900_ses-01_run-1
COMPLETED: rf1_sub-11900_ses-01_run-2
COMPLETED: rf1_sub-11902_ses-01_run-2
COMPLETED: rf1_sub-11909_ses-01_run-1
COMPLETED: rf1_sub-11902_ses-01_run-1
COMPLETED: rf1_sub-11909_ses-01_run-2
COMPLETED: rf1_sub-11913_ses-01_run-2
COMPLETED: rf1_sub-11913_ses-01_run-1
COMPLETED: rf1_sub-11914_ses-01_run-1
COMPLETED: rf1_sub-11914_ses-01_run-2
COMPLETED: rf1_sub-11920_ses-01_run-1
COMPLETED: rf1_sub-11920_ses-01_run-2
COMPLETED: rf1_sub-11922_ses-01_run-1
COMPLETED: rf1_sub-11923_ses-01_run-1
COMPLETED: rf1_sub-11922_ses-01_run-2
COMPLETED: rf1_sub-11923_ses-01_run-2
COMPLETED: rf1_sub-11924_ses-01_run-1
COMPLETED: rf1_sub-11924_ses-01_run-2
COMPLETED: rf1_sub-11926_ses-01_run-2
COMPLETED: rf1_sub-11926_ses-01_run-1
COMPLETED: rf1_sub-11928_ses-01_run-1
COMPLETED: rf1_sub-11929_ses-01_run-2
COMPLETED: rf1_sub-11928_ses-01_run-2
COMPLETED: rf1_sub-11929_ses-01_run-1
COMPLETED: rf1_sub-11931_ses-01_run-1
COMPLETED: rf1_sub-11935_ses-01_run-1
COMPLETED: rf1_sub-11935_ses-01_run-2
COMPLETED: rf1_sub-11931_ses-01_run-2
COMPLETED: rf1_sub-11939_ses-01_run-1
COMPLETED: rf1_sub-11943_ses-01_run-1
COMPLETED: rf1_sub-11943_ses-01_run-2
COMPLETED: rf1_sub-11939_ses-01_run-2
COMPLETED: rf1_sub-11949_ses-01_run-1
COMPLETED: rf1_sub-11949_ses-01_run-2
COMPLETED: rf1_sub-11960_ses-01_run-1
COMPLETED: rf1_sub-11960_ses-01_run-2
COMPLETED: rf1_sub-11969_ses-01_run-1
COMPLETED: rf1_sub-11974_ses-01_run-2
COMPLETED: rf1_sub-11969_ses-01_run-2
COMPLETED: rf1_sub-11974_ses-01_run-1
COMPLETED: rf1_sub-11976_ses-01_run-1
COMPLETED: rf1_sub-11982_ses-01_run-2
COMPLETED: rf1_sub-11976_ses-01_run-2
COMPLETED: rf1_sub-11982_ses-01_run-1
COMPLETED: rf1_sub-11984_ses-01_run-1
COMPLETED: rf1_sub-12008_ses-01_run-1
COMPLETED: rf1_sub-11984_ses-01_run-2
COMPLETED: rf1_sub-12008_ses-01_run-2
COMPLETED: rf1_sub-12011_ses-01_run-1
COMPLETED: rf1_sub-12013_ses-01_run-2
COMPLETED: rf1_sub-12011_ses-01_run-2
COMPLETED: rf1_sub-12013_ses-01_run-1
COMPLETED: rf1_sub-12018_ses-01_run-1
COMPLETED: rf1_sub-12020_ses-01_run-1
COMPLETED: rf1_sub-12020_ses-01_run-2
COMPLETED: rf1_sub-12018_ses-01_run-2
COMPLETED: rf1_sub-12021_ses-01_run-1
COMPLETED: rf1_sub-12021_ses-01_run-2
COMPLETED: rf1_sub-12031_ses-01_run-1
COMPLETED: rf1_sub-12031_ses-01_run-2
COMPLETED: rf1_sub-12032_ses-01_run-1
COMPLETED: rf1_sub-12032_ses-01_run-2
COMPLETED: rf1_sub-12033_ses-01_run-1
COMPLETED: rf1_sub-12033_ses-01_run-2
COMPLETED: rf1_sub-12036_ses-01_run-1
COMPLETED: rf1_sub-12037_ses-01_run-1
COMPLETED: rf1_sub-12038_ses-01_run-1
COMPLETED: rf1_sub-12036_ses-01_run-2
COMPLETED: rf1_sub-12038_ses-01_run-2
COMPLETED: rf1_sub-12041_ses-01_run-1
COMPLETED: rf1_sub-12039_ses-01_run-2
COMPLETED: rf1_sub-12039_ses-01_run-1
COMPLETED: rf1_sub-12047_ses-01_run-1
COMPLETED: rf1_sub-12047_ses-01_run-2
COMPLETED: rf1_sub-12049_ses-01_run-2
COMPLETED: rf1_sub-12049_ses-01_run-1
COMPLETED: rf1_sub-12051_ses-01_run-1
COMPLETED: rf1_sub-12051_ses-01_run-2
COMPLETED: rf1_sub-12054_ses-01_run-2
COMPLETED: rf1_sub-12054_ses-01_run-1
COMPLETED: rf1_sub-12055_ses-01_run-1
COMPLETED: rf1_sub-12055_ses-01_run-2
COMPLETED: rf1_sub-12057_ses-01_run-1
COMPLETED: rf1_sub-12057_ses-01_run-2
Units scheduled: 765
Units newly completed: 765
Units verified existing: 0
Units failed: 0
CHECK PASSED: every harmonized event derivative is complete and valid.
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/audit_event_qc.py --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/fulltrial-event-qc-ready.tsv --output /ZPOOL/data/projects/sharedreward-aging/logs/records/fulltrial-event-qc-run-level.tsv --subject-output /ZPOOL/data/projects/sharedreward-aging/logs/records/fulltrial-event-qc-subject-level.tsv --missing-output /ZPOOL/data/projects/sharedreward-aging/logs/records/fulltrial-event-qc-missing.tsv --fail-on-incomplete
Event-QC units checked: 765
Complete event-QC units: 765
Incomplete event-QC units: 0
Runs excluded for >25% missed trials: 19
Runs with one or more zero-count modeled conditions: 27
Subjects with zero usable runs: 4
  ds003745: n=100; missed=532/7200 (7.389%)
  rf1: n=665; missed=783/35861 (2.183%)
Run-level audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/fulltrial-event-qc-run-level.tsv
Subject-level audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/fulltrial-event-qc-subject-level.tsv
Missing report: /ZPOOL/data/projects/sharedreward-aging/logs/records/fulltrial-event-qc-missing.tsv
CHECK PASSED: every run has valid harmonized full-trial event QC.
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/build_fsl_confounds_manifest.py --output /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ds003745-fsl-confounds.tsv --output-root /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/confounds_fmriprep
ds003745 FSL nuisance units: 100
Manifest: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ds003745-fsl-confounds.tsv
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/run_fsl_confounds_batch.py --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ds003745-fsl-confounds.tsv --jobs 8 --log-dir /ZPOOL/data/projects/sharedreward-aging/logs/ds003745-fsl-confounds
VERIFIED EXISTING: ds003745_sub-112_run-02
VERIFIED EXISTING: ds003745_sub-104_run-02
VERIFIED EXISTING: ds003745_sub-111_run-01
VERIFIED EXISTING: ds003745_sub-108_run-02
VERIFIED EXISTING: ds003745_sub-106_run-02
VERIFIED EXISTING: ds003745_sub-108_run-01
VERIFIED EXISTING: ds003745_sub-115_run-02
VERIFIED EXISTING: ds003745_sub-110_run-01
VERIFIED EXISTING: ds003745_sub-110_run-02
VERIFIED EXISTING: ds003745_sub-115_run-01
VERIFIED EXISTING: ds003745_sub-118_run-01
VERIFIED EXISTING: ds003745_sub-112_run-01
VERIFIED EXISTING: ds003745_sub-106_run-01
VERIFIED EXISTING: ds003745_sub-109_run-02
VERIFIED EXISTING: ds003745_sub-105_run-02
VERIFIED EXISTING: ds003745_sub-104_run-01
VERIFIED EXISTING: ds003745_sub-113_run-02
VERIFIED EXISTING: ds003745_sub-117_run-02
VERIFIED EXISTING: ds003745_sub-116_run-02
VERIFIED EXISTING: ds003745_sub-107_run-02
VERIFIED EXISTING: ds003745_sub-105_run-01
VERIFIED EXISTING: ds003745_sub-111_run-02
VERIFIED EXISTING: ds003745_sub-117_run-01
VERIFIED EXISTING: ds003745_sub-113_run-01
VERIFIED EXISTING: ds003745_sub-109_run-01
VERIFIED EXISTING: ds003745_sub-107_run-01
VERIFIED EXISTING: ds003745_sub-116_run-01
VERIFIED EXISTING: ds003745_sub-118_run-02
VERIFIED EXISTING: ds003745_sub-120_run-02
VERIFIED EXISTING: ds003745_sub-120_run-01
VERIFIED EXISTING: ds003745_sub-121_run-02
VERIFIED EXISTING: ds003745_sub-122_run-01
VERIFIED EXISTING: ds003745_sub-122_run-02
VERIFIED EXISTING: ds003745_sub-124_run-01
VERIFIED EXISTING: ds003745_sub-124_run-02
VERIFIED EXISTING: ds003745_sub-125_run-01
VERIFIED EXISTING: ds003745_sub-125_run-02
VERIFIED EXISTING: ds003745_sub-126_run-01
VERIFIED EXISTING: ds003745_sub-126_run-02
VERIFIED EXISTING: ds003745_sub-127_run-01
VERIFIED EXISTING: ds003745_sub-127_run-02
VERIFIED EXISTING: ds003745_sub-128_run-01
VERIFIED EXISTING: ds003745_sub-128_run-02
VERIFIED EXISTING: ds003745_sub-129_run-01
VERIFIED EXISTING: ds003745_sub-129_run-02
VERIFIED EXISTING: ds003745_sub-130_run-01
VERIFIED EXISTING: ds003745_sub-130_run-02
VERIFIED EXISTING: ds003745_sub-131_run-01
VERIFIED EXISTING: ds003745_sub-131_run-02
VERIFIED EXISTING: ds003745_sub-132_run-01
VERIFIED EXISTING: ds003745_sub-121_run-01
VERIFIED EXISTING: ds003745_sub-132_run-02
VERIFIED EXISTING: ds003745_sub-133_run-02
VERIFIED EXISTING: ds003745_sub-134_run-01
VERIFIED EXISTING: ds003745_sub-134_run-02
VERIFIED EXISTING: ds003745_sub-135_run-01
VERIFIED EXISTING: ds003745_sub-135_run-02
VERIFIED EXISTING: ds003745_sub-136_run-01
VERIFIED EXISTING: ds003745_sub-136_run-02
VERIFIED EXISTING: ds003745_sub-137_run-01
VERIFIED EXISTING: ds003745_sub-137_run-02
VERIFIED EXISTING: ds003745_sub-138_run-01
VERIFIED EXISTING: ds003745_sub-138_run-02
VERIFIED EXISTING: ds003745_sub-140_run-01
VERIFIED EXISTING: ds003745_sub-140_run-02
VERIFIED EXISTING: ds003745_sub-141_run-01
VERIFIED EXISTING: ds003745_sub-141_run-02
VERIFIED EXISTING: ds003745_sub-142_run-01
VERIFIED EXISTING: ds003745_sub-142_run-02
VERIFIED EXISTING: ds003745_sub-143_run-01
VERIFIED EXISTING: ds003745_sub-143_run-02
VERIFIED EXISTING: ds003745_sub-144_run-01
VERIFIED EXISTING: ds003745_sub-144_run-02
VERIFIED EXISTING: ds003745_sub-133_run-01
VERIFIED EXISTING: ds003745_sub-145_run-01
VERIFIED EXISTING: ds003745_sub-147_run-01
VERIFIED EXISTING: ds003745_sub-147_run-02
VERIFIED EXISTING: ds003745_sub-149_run-01
VERIFIED EXISTING: ds003745_sub-149_run-02
VERIFIED EXISTING: ds003745_sub-150_run-01
VERIFIED EXISTING: ds003745_sub-150_run-02
VERIFIED EXISTING: ds003745_sub-151_run-01
VERIFIED EXISTING: ds003745_sub-151_run-02
VERIFIED EXISTING: ds003745_sub-152_run-01
VERIFIED EXISTING: ds003745_sub-152_run-02
VERIFIED EXISTING: ds003745_sub-153_run-01
VERIFIED EXISTING: ds003745_sub-153_run-02
VERIFIED EXISTING: ds003745_sub-154_run-01
VERIFIED EXISTING: ds003745_sub-154_run-02
VERIFIED EXISTING: ds003745_sub-155_run-01
VERIFIED EXISTING: ds003745_sub-155_run-02
VERIFIED EXISTING: ds003745_sub-156_run-01
VERIFIED EXISTING: ds003745_sub-156_run-02
VERIFIED EXISTING: ds003745_sub-157_run-01
VERIFIED EXISTING: ds003745_sub-157_run-02
VERIFIED EXISTING: ds003745_sub-158_run-01
VERIFIED EXISTING: ds003745_sub-158_run-02
VERIFIED EXISTING: ds003745_sub-159_run-01
VERIFIED EXISTING: ds003745_sub-159_run-02
VERIFIED EXISTING: ds003745_sub-145_run-02
Units scheduled: 100
Units newly completed: 0
Units verified existing: 100
Units failed: 0
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/audit_fsl_confounds.py --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/ds003745-fsl-confounds.tsv --output /ZPOOL/data/projects/sharedreward-aging/logs/records/ds003745-fsl-confounds-audit.tsv --fail-on-incomplete
FSL nuisance units checked: 100
Complete units: 100
Incomplete units: 0
Audit: /ZPOOL/data/projects/sharedreward-aging/logs/records/ds003745-fsl-confounds-audit.tsv
CHECK PASSED: every ds003745 FSL nuisance matrix is numeric and volume-aligned.
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/build_analysis_cohort.py --ds-confounds-root /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/confounds_fmriprep
Imaging-ready runs considered: 767
Task-ready L1 runs: 744
Task-excluded runs: 23
Model-review holds: 0
Task-ready L2 subject-sessions: 393
Ratings-qualified L1 runs: 655
Ratings-qualified L2 subject-sessions: 346
Wrote: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-task-ready.tsv
Wrote: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-ratings-ready.tsv
Wrote: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-model-review-hold.tsv
Wrote: /ZPOOL/data/projects/sharedreward-aging/logs/records/analysis-run-dispositions.tsv
Wrote: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L2-task-ready.tsv
Wrote: /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L2-ratings-ready.tsv
Wrote: /ZPOOL/data/projects/sharedreward-aging/logs/records/analysis-subject-dispositions.tsv
Selected l1: 2 row(s): /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-sub144-recovered.tsv
Selected l2: 1 row(s): /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L2-sub144-recovered.tsv
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/generate_l1_evs.py --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-sub144-recovered.tsv --output-root /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/EVfiles --overwrite
L1 EV units: 2
Newly generated: 2
Verified existing: 0
EV root: /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/EVfiles
ARCHIVED (recoverable): /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-act_run-1_sm-6.feat -> /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/replaced-models/sub144-20260915-131949-404913/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-act_run-1_sm-6.feat
ARCHIVED (recoverable): /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-act_run-2_sm-6.feat -> /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/replaced-models/sub144-20260915-131949-404913/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-act_run-2_sm-6.feat
ARCHIVED (recoverable): /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-ppi_seed-vs_run-1_sm-6.feat -> /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/replaced-models/sub144-20260915-131949-404913/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-ppi_seed-vs_run-1_sm-6.feat
ARCHIVED (recoverable): /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-ppi_seed-vs_run-2_sm-6.feat -> /ZPOOL/data/projects/sharedreward-aging/derivatives/fsl/replaced-models/sub144-20260915-131949-404913/ds003745/sub-144/L1_task-sharedreward_model-fulltrial_type-ppi_seed-vs_run-2_sm-6.feat
COMMAND: bash /ZPOOL/data/projects/sharedreward-aging/code/run_L1stats.sh --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-sub144-recovered.tsv --ppi-seed vs --parallel-types --jobs 2 --log-dir /ZPOOL/data/projects/sharedreward-aging/logs/L1-sub144-20260915-131949-404913
Paired L1 plan: 2 unit(s), jobs=2, activation + PPI seed-vs
Concurrent analysis types: up to 4 L1 FEAT jobs (2 paired workers).
Per-unit logs: /ZPOOL/data/projects/sharedreward-aging/logs/L1-sub144-20260915-131949-404913
START: ds003745 sub-144 ses-none run-1 (log: /ZPOOL/data/projects/sharedreward-aging/logs/L1-sub144-20260915-131949-404913/ds003745_sub-144_ses-none_task-sharedreward_run-1.log)
START: ds003745 sub-144 ses-none run-2 (log: /ZPOOL/data/projects/sharedreward-aging/logs/L1-sub144-20260915-131949-404913/ds003745_sub-144_ses-none_task-sharedreward_run-2.log)
DONE: ds003745 sub-144 ses-none run-1
DONE: ds003745 sub-144 ses-none run-2
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/audit_outputs.py --level l1 --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-sub144-recovered.tsv --type act --output /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-L1-act-completeness.tsv
Manifest units checked: 2
Fully complete units: 2
Incomplete units: 0
Completeness report: /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-L1-act-completeness.tsv
CHECK PASSED: all 2 l1 act unit(s) are complete.
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/audit_outputs.py --level l1 --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L1-sub144-recovered.tsv --type ppi_seed-vs --output /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-L1-ppi_seed-vs-completeness.tsv
Manifest units checked: 2
Fully complete units: 2
Incomplete units: 0
Completeness report: /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-L1-ppi_seed-vs-completeness.tsv
CHECK PASSED: all 2 l1 ppi_seed-vs unit(s) are complete.
COMMAND: bash /ZPOOL/data/projects/sharedreward-aging/code/run_L2stats.sh --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L2-sub144-recovered.tsv --ppi-seed vs --parallel-types --jobs 1 --log-dir /ZPOOL/data/projects/sharedreward-aging/logs/L2-sub144-20260915-131949-404913
Paired L2 plan: 1 fixed-effects unit(s), 0 one-run passthrough(s), jobs=1, activation + PPI seed-vs
Concurrent analysis types: up to 2 L2 FEAT jobs (1 paired workers).
Per-unit logs: /ZPOOL/data/projects/sharedreward-aging/logs/L2-sub144-20260915-131949-404913
START: ds003745 sub-144 ses-none (log: /ZPOOL/data/projects/sharedreward-aging/logs/L2-sub144-20260915-131949-404913/ds003745_sub-144_ses-none_task-sharedreward.log)
DONE: ds003745 sub-144 ses-none
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/audit_outputs.py --level subject --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L2-sub144-recovered.tsv --type act --output /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-subject-act-completeness.tsv
Manifest units checked: 1
Fully complete units: 1
Incomplete units: 0
Completeness report: /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-subject-act-completeness.tsv
CHECK PASSED: all 1 subject act unit(s) are complete.
COMMAND: /ZPOOL/data/tools/anaconda/tug87422/envs/sharedreward-phase0/bin/python /ZPOOL/data/projects/sharedreward-aging/code/audit_outputs.py --level subject --manifest /ZPOOL/data/projects/sharedreward-aging/logs/runlists/L2-sub144-recovered.tsv --type ppi_seed-vs --output /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-subject-ppi_seed-vs-completeness.tsv
Manifest units checked: 1
Fully complete units: 1
Incomplete units: 0
Completeness report: /ZPOOL/data/projects/sharedreward-aging/logs/records/sub144-subject-ppi_seed-vs-completeness.tsv
CHECK PASSED: all 1 subject ppi_seed-vs unit(s) are complete.
CHECK PASSED: corrected sub-144 activation and provisional VS PPI, including subject-level outputs.

COMMAND EXIT: 0
```
