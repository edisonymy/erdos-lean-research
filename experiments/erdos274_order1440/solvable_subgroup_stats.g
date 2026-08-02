out := OutputTextFile("/work/solvable_subgroup_stats.tsv", false);
SetPrintFormattingStatus(out, false);
seen := 0;
for id in [1..NumberSmallGroups(1440)] do
  G := SmallGroup(1440, id);
  if IsSolvableGroup(G) and not IsSupersolvableGroup(G) then
    cc := ConjugacyClassesSubgroups(G);
    inds := Set(List(cc, c -> Index(G, Representative(c))));
    totalSubs := Sum(cc, Size);
    totalCosets := Sum(cc, c -> Size(c) * Index(G, Representative(c)));
    PrintTo(out, id, "\t", Length(cc), "\t", totalSubs, "\t", totalCosets, "\t");
    for x in inds do PrintTo(out, x, ","); od;
    PrintTo(out, "\n");
    seen := seen + 1;
    if seen mod 25 = 0 then Print("PROGRESS ", seen, " id=", id, "\n"); fi;
  fi;
od;
CloseStream(out);
Print("FINAL ", seen, "\n");
QUIT;
