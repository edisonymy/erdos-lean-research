gids := [655,659,2641,2642,267,657,265,255,2666,2667,74,654,1881,4109,1624,4108,2549,2522,1625,1629,1628,2547,2524,256,2542];

for gid in gids do
  G := SmallGroup(1440,gid);
  elts := Elements(G);
  classes := ConjugacyClassesSubgroups(G);
  filename := Concatenation("/work/cosets", String(gid), ".tsv");
  out := OutputTextFile(filename, false);
  SetPrintFormattingStatus(out, false);
  subgroupId := 0;
  candidateId := 0;
  classId := 0;
  for c in classes do
    classId := classId + 1;
    H0 := Representative(c);
    idx := Index(G,H0);
    if idx > 2 then
      firstInClass := true;
      for H in AsList(c) do
        subgroupId := subgroupId + 1;
        isRepresentative := 0;
        if firstInClass then
          isRepresentative := 1;
          firstInClass := false;
        fi;
        for C in RightCosets(G,H) do
          candidateId := candidateId + 1;
          ids := List(Elements(C), x -> Position(elts,x));
          Sort(ids);
          line := JoinStringsWithSeparator(List(ids,String), ",");
          PrintTo(out, candidateId, "\t", idx, "\t", subgroupId, "\t",
                  classId, "\t", isRepresentative, "\t", line, "\n");
        od;
      od;
    fi;
  od;
  CloseStream(out);
  Print(gid, " subgroups=", subgroupId, " candidates=", candidateId, "\n");
od;
QUIT;
